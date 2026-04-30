# meridiano/llm_manager.py
"""
Gerenciador de modelos LLM com controle de taxa (throttling) dinâmico e
exponential backoff para erros 429 (Too Many Requests).

Perfis suportados via variáveis de ambiente:
  LLM_CHAT_MODEL   -> nome do modelo de chat (ex: gemini/gemini-2.0-flash-lite)
  EMBEDDING_MODEL  -> nome do modelo de embedding (ex: gemini/text-embedding-004)

Os limites de RPM/RPD são lidos automaticamente a partir do MODEL_PROFILES
ou sobrescritos pelas variáveis LLM_RPM e LLM_RPD.
"""

import os
import time
import logging
from collections import deque
from threading import Lock
from typing import Optional

import litellm
from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

load_dotenv()
log = logging.getLogger(__name__)


class _RateLimitSignal(Exception):
    """Sinal interno: a chamada deve ser retentada (erro 429)."""

# ---------------------------------------------------------------------------
# Perfis de modelos conhecidos (RPM = requests/min, RPD = requests/day)
# ---------------------------------------------------------------------------
MODEL_PROFILES: dict[str, dict] = {
    # Perfil A – Flash Models (High Performance)
    "gemini/gemini-2.5-flash": {"rpm": 10, "rpd": 1500},
    "gemini/gemini-2.0-flash": {"rpm": 10, "rpd": 1500},
    "gemini/gemini-2.0-flash-lite": {"rpm": 10, "rpd": 1500},
    "gemini/gemini-1.5-flash": {"rpm": 10, "rpd": 1500},
    
    # Perfil B – Heavy / Research Models
    # Reduzido para 5 RPM para evitar estourar o limite de tokens (15k/min)
    "gemini/gemma-3-4b-it": {"rpm": 5, "rpd": 14_000},
    
    # Perfil C – Previews
    "gemini/gemini-2.5-flash-preview-04-17": {"rpm": 10, "rpd": 20},
    
    # Embeddings
    "gemini/gemini-embedding-001": {"rpm": 1_500, "rpd": 100_000},
    "gemini/gemini-embedding-exp-03-07": {"rpm": 5, "rpd": 100},
}

_DEFAULT_RPM = 10
_DEFAULT_RPD = 500


def _get_limits(model: str) -> tuple[int, int]:
    """Retorna (rpm, rpd) para o modelo dado, priorizando variáveis de ambiente."""
    rpm = int(os.getenv("LLM_RPM", 0)) or MODEL_PROFILES.get(model, {}).get("rpm", _DEFAULT_RPM)
    rpd = int(os.getenv("LLM_RPD", 0)) or MODEL_PROFILES.get(model, {}).get("rpd", _DEFAULT_RPD)
    return rpm, rpd


# ---------------------------------------------------------------------------
# Token-bucket simples (thread-safe) baseado em timestamps
# ---------------------------------------------------------------------------
class _RateLimiter:
    """Garante no máximo `rpm` chamadas por minuto e `rpd` por dia."""

    def __init__(self, rpm: int, rpd: int) -> None:
        self.rpm = rpm
        self.rpd = rpd
        self._minute_window: deque[float] = deque()
        self._day_window: deque[float] = deque()
        self._lock = Lock()

    def _purge(self, window: deque, max_age: float) -> None:
        now = time.monotonic()
        while window and now - window[0] > max_age:
            window.popleft()

    def wait(self) -> None:
        with self._lock:
            while True:
                now = time.monotonic()
                self._purge(self._minute_window, 60.0)
                self._purge(self._day_window, 86_400.0)

                if len(self._minute_window) < self.rpm and len(self._day_window) < self.rpd:
                    self._minute_window.append(now)
                    self._day_window.append(now)
                    return

                # Descobre quanto tempo esperar
                if len(self._minute_window) >= self.rpm:
                    sleep_for = 60.0 - (now - self._minute_window[0]) + 0.1
                else:
                    sleep_for = 86_400.0 - (now - self._day_window[0]) + 0.1

                log.info("Rate limit atingido — aguardando %.1f s", sleep_for)
                time.sleep(max(sleep_for, 0.1))


# Cache de limitadores (um por modelo)
_limiters: dict[str, _RateLimiter] = {}
_limiters_lock = Lock()


def _get_limiter(model: str) -> _RateLimiter:
    with _limiters_lock:
        if model not in _limiters:
            rpm, rpd = _get_limits(model)
            log.info("Criando rate limiter para '%s': %d RPM / %d RPD", model, rpm, rpd)
            _limiters[model] = _RateLimiter(rpm=rpm, rpd=rpd)
        return _limiters[model]


# ---------------------------------------------------------------------------
# Identificador de erro 429 compatível com litellm
# ---------------------------------------------------------------------------
def _is_rate_limit_error(exc: BaseException) -> bool:
    exc_type = type(exc).__name__
    if exc_type in ("RateLimitError", "APIStatusError", "APIError"):
        return True
    msg = str(exc).lower()
    return any(term in msg for term in ["429", "rate limit", "too many requests", "quota", "exhausted"])



# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def llm_completion(
    model: str,
    messages: list[dict],
    max_tokens: int = 2048,
    temperature: float = 0.7,
    **kwargs,
) -> Optional[str]:
    """
    Chama litellm.completion com throttling dinâmico e exponential backoff.
    Retorna o texto da resposta ou None em caso de falha persistente.
    """
    limiter = _get_limiter(model)

    @retry(
        retry=retry_if_exception_type(_RateLimitSignal),
        wait=wait_exponential(multiplier=2, min=5, max=120),
        stop=stop_after_attempt(6),
        before_sleep=before_sleep_log(log, logging.WARNING),
    )
    def _call() -> Optional[str]:
        limiter.wait()
        try:
            resp = litellm.completion(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
            return resp["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            if _is_rate_limit_error(exc):
                log.warning("429 recebido para modelo '%s', aplicando backoff…", model)
                raise _RateLimitSignal(str(exc)) from exc
            log.error("Erro na chamada LLM ('%s'): %s", model, exc)
            return None

    try:
        return _call()
    except _RateLimitSignal as exc:
        log.error("Falha permanente após retentativas ('%s'): %s", model, exc)
        return None


def llm_embedding(
    model: str,
    text: str,
    **kwargs,
) -> Optional[list[float]]:
    """
    Chama litellm.embedding com throttling dinâmico e exponential backoff.
    Retorna o vetor de embedding ou None em caso de falha persistente.
    """
    limiter = _get_limiter(model)

    @retry(
        retry=retry_if_exception_type(_RateLimitSignal),
        wait=wait_exponential(multiplier=2, min=5, max=120),
        stop=stop_after_attempt(6),
        before_sleep=before_sleep_log(log, logging.WARNING),
    )
    def _call() -> Optional[list[float]]:
        limiter.wait()
        try:
            resp = litellm.embedding(model=model, input=[text], **kwargs)
            data = resp.get("data") or []
            if data:
                return data[0]["embedding"]
            log.warning("Embedding vazio retornado para modelo '%s'.", model)
            return None
        except Exception as exc:
            if _is_rate_limit_error(exc):
                log.warning("429 recebido para embedding '%s', aplicando backoff…", model)
                raise _RateLimitSignal(str(exc)) from exc
            log.error("Erro na chamada de embedding ('%s'): %s", model, exc)
            return None

    try:
        return _call()
    except _RateLimitSignal as exc:
        log.error("Falha permanente no embedding após retentativas ('%s'): %s", model, exc)
        return None
