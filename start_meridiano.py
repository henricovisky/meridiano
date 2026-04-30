#!/usr/bin/env python3
"""
start_meridiano.py — Inicializador multiplataforma do Meridiano.

Comportamento:
  1. Detecta o SO (Windows / Linux / macOS).
  2. Verifica se o venv existe; cria se necessário.
  3. Instala dependências via 'uv sync' (preferencial) ou 'pip install -r requirements.txt'.
  4. Executa o pipeline do Meridiano dentro do venv.

Uso:
  python start_meridiano.py [--feed brasil] [--all] [--process-articles] ...
  python start_meridiano.py --help
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.resolve()
VENV_DIR = ROOT / ".venv"
PYPROJECT = ROOT / "pyproject.toml"
REQUIREMENTS = ROOT / "requirements.txt"

IS_WINDOWS = platform.system() == "Windows"

# Caminhos dos executáveis dentro do venv
if IS_WINDOWS:
    VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
    VENV_PIP = VENV_DIR / "Scripts" / "pip.exe"
    VENV_UV = VENV_DIR / "Scripts" / "uv.exe"
else:
    VENV_PYTHON = VENV_DIR / "bin" / "python"
    VENV_PIP = VENV_DIR / "bin" / "pip"
    VENV_UV = VENV_DIR / "bin" / "uv"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    """Executa um comando e encerra o script em caso de falha."""
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"\n[ERRO] Comando falhou com código {result.returncode}. Abortando.")
        sys.exit(result.returncode)
    return result


def _ensure_venv() -> None:
    """Cria o venv caso não exista."""
    if VENV_PYTHON.exists():
        print(f"[OK] venv encontrado em: {VENV_DIR}")
        return

    print(f"[INFO] venv não encontrado. Criando em: {VENV_DIR}")
    _run([sys.executable, "-m", "venv", str(VENV_DIR)])
    print("[OK] venv criado.")


def _install_deps() -> None:
    """Instala dependências usando uv (preferencial) ou pip."""
    # Tenta uv sync (requer uv instalado no PATH ou já no venv)
    uv_global = subprocess.run(
        ["uv", "--version"], capture_output=True, text=True
    ).returncode == 0

    if PYPROJECT.exists() and uv_global:
        print("[INFO] Instalando dependências com 'uv sync'…")
        _run(["uv", "sync", "--project", str(ROOT)])
        print("[OK] Dependências instaladas via uv.")
        return

    # Fallback: pip
    if REQUIREMENTS.exists():
        print("[INFO] Instalando dependências com pip…")
        _run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
        _run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(REQUIREMENTS), "--quiet"])
    elif PYPROJECT.exists():
        print("[INFO] Instalando pacote em modo editável com pip…")
        _run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
        _run([str(VENV_PYTHON), "-m", "pip", "install", "-e", str(ROOT), "--quiet"])
    else:
        print("[AVISO] Nenhum requirements.txt nem pyproject.toml encontrado. Pulando instalação.")
        return

    print("[OK] Dependências instaladas via pip.")


def _check_env() -> None:
    """Alerta se .env não existir."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        example = ROOT / ".env.example"
        if example.exists():
            print(
                f"\n[AVISO] Arquivo .env não encontrado.\n"
                f"        Copie o exemplo e configure suas chaves:\n"
                f"          cp {example} {env_file}\n"
            )
        else:
            print("\n[AVISO] Arquivo .env não encontrado. Crie-o com as variáveis necessárias.\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    # Parse apenas os argumentos de inicialização; o restante vai para run_briefing
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--skip-install", action="store_true", help="Pula a etapa de instalação de dependências.")
    pre_args, remaining_args = pre_parser.parse_known_args()

    print("=" * 60)
    print("  Meridiano — Inicializador Multiplataforma")
    print(f"  Sistema: {platform.system()} {platform.release()} | Python {sys.version.split()[0]}")
    print("=" * 60)

    # 1. Garante venv
    print("\n[1/3] Verificando ambiente virtual…")
    _ensure_venv()

    # 2. Instala dependências
    if not pre_args.skip_install:
        print("\n[2/3] Verificando dependências…")
        _install_deps()
    else:
        print("\n[2/3] Instalação pulada (--skip-install).")

    # 3. Verifica .env
    _check_env()

    # 4. Executa o Meridiano
    print("\n[3/3] Iniciando Meridiano…\n")
    cmd = [str(VENV_PYTHON), "-m", "meridiano.run_briefing"] + remaining_args
    # Se --help foi passado, repassa normalmente
    if not remaining_args:
        cmd.append("--all")

    try:
        proc = subprocess.run(cmd, cwd=str(ROOT / "src"))
        sys.exit(proc.returncode)
    except KeyboardInterrupt:
        print("\n\n[INFO] Interrompido pelo usuário.")
        sys.exit(0)


if __name__ == "__main__":
    main()
