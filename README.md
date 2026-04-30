# Meridiano: Sistema Pessoal de Briefing de Inteligência

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](#)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

**Briefings de inteligência impulsionados por IA, adaptados aos seus interesses, construídos com tecnologia simples e implementável.**

O Meridiano elimina o ruído extraindo dados de fontes configuradas, analisando notícias com IA, agrupando eventos relacionados e entregando briefs diários concisos através de uma interface web leve.

Baseado no projeto original [meridian](https://github.com/iliane5/meridian).

---

## 🎯 Propósito

Inspirado no conceito de briefings diários presidenciais, o Meridiano fornece inteligência focada e personalizada para usuários individuais. Ele ajuda você a:
* **Manter-se informado** sobre os principais eventos globais ou tópicos específicos sem se afogar em ruído.
* **Entender o contexto** além das manchetes através da análise de IA (via LiteLLM com suporte a múltiplos provedores).
* **Acompanhar o desenvolvimento de histórias** por meio do agrupamento inteligente de artigos.
* **Manter o controle** com uma infraestrutura leve (Bare Metal) e feeds personalizáveis.

---

## 🏗️ Arquitetura Técnica

O Meridiano é otimizado para servidores modestos (ex: Ubuntu com 1GB RAM) utilizando uma abordagem nativa (Bare Metal), sem depender de contêineres ou orquestradores pesados.

* **Pipeline Backend**: `run_briefing.py` orquestra a extração, processamento, avaliação (rating) e geração do brief.
* **Banco de Dados**: `SQLModel` com SQLite/PostgreSQL, apresentando FTS5 para pesquisa rápida de texto completo.
* **Servidor Web**: Interface web em Flask servida via `gunicorn`, controlada por `systemd` para alta disponibilidade e resiliência.
* **Integração de IA**: Usa `LiteLLM` para sumarização, avaliação de relevância e síntese (suporta modelos robustos como `gemma-3-27b-it`, Deepseek, OpenAI, etc.).
* **Automação**: Tarefas agendadas via `cron` que executam o script `start_meridiano.sh`, garantindo código sempre atualizado e pipeline fluindo.

---

## 🚀 Configuração e Implantação (Ubuntu Server)

### Pré-requisitos
* Ubuntu Server (1GB RAM recomendado)
* Python 3.10+ e `venv`
* Git
* Chaves de API para provedores de LLM e Embedding (ex: Gemini, Together AI)
* (Opcional) Tailscale configurado para acesso seguro à rede (`http://jarvis:5000`)

### 1. Instalação Básica

Clone o repositório e configure o ambiente virtual:

```bash
cd /opt
sudo git clone <url-do-seu-repositorio> meridiano
sudo chown -R $USER:$USER meridiano
cd meridiano

python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install gunicorn
```

Configure suas chaves:
```bash
cp .env.example .env
nano .env # Adicione suas chaves, ex: GEMINI_API_KEY
```

Crie os perfis de feeds desejados na pasta `src/meridiano/feeds/`.

### 2. Serviço Web (systemd + gunicorn)

Crie um arquivo de serviço para manter a página web sempre ativa:

```bash
sudo nano /etc/systemd/system/meridiano-web.service
```

Exemplo de configuração (`meridiano-web.service`):
```ini
[Unit]
Description=Meridiano Web App
After=network.target

[Service]
User=seu_usuario
WorkingDirectory=/opt/meridiano
Environment="PATH=/opt/meridiano/.venv/bin"
ExecStart=/opt/meridiano/.venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 'meridiano.app:app'
Restart=always

[Install]
WantedBy=multi-user.target
```

Ative e inicie o serviço:
```bash
sudo systemctl daemon-reload
sudo systemctl enable meridiano-web.service
sudo systemctl start meridiano-web.service
```

### 3. Automação do Pipeline (cron)

A automação é controlada pelo script `start_meridiano.sh`, que atualiza o código, roda o pipeline e reinicia o serviço web.

Certifique-se de que o script tem permissão de execução:
```bash
chmod +x /opt/meridiano/start_meridiano.sh
```

Edite seu crontab (`crontab -e`) para rodar os briefings diariamente (exemplo: todo dia às 06:00 da manhã):
```cron
0 6 * * * /opt/meridiano/start_meridiano.sh >> /opt/meridiano/cron.log 2>&1
```

---

## 💻 Fluxo Operacional (CLI)

Além do cron, você pode executar o pipeline do Meridiano manualmente ativando o `.venv` e usando o CLI `run_briefing.py`:

```bash
source /opt/meridiano/.venv/bin/activate
export PYTHONPATH="/opt/meridiano/src"

# Executa todo o pipeline com o perfil padrão:
python3 src/meridiano/run_briefing.py --feed default --all
```

### Argumentos Principais
* `--feed <perfil>`: Especifique o perfil (ex: `default`, `tech`). O padrão é `default`.
* `--scrape-articles`: Executa apenas a extração via RSS.
* `--process-articles`: Executa apenas a etapa de resumo e geração de embeddings.
* `--rate-articles`: Executa a avaliação de impacto via IA.
* `--generate-brief`: Agrupa e sintetiza o brief final.
* `--all`: Executa todas as etapas sequencialmente.
* `-m`, `--model`: Substitui temporariamente o modelo de chat.

---

## 🤝 Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes de colaboração. Agradecemos pull requests!

### Créditos
* Conceito original: [iliane5/meridian](https://github.com/iliane5/meridian)
* Base robusta e atualizações: Diversos contribuidores da comunidade open-source.

## 📄 Licença
Licenciado sob a **GNU Affero General Public License v3.0 (AGPLv3)**.
