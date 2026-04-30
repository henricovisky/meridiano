# Meridiano: Sistema Pessoal de Briefing de Inteligência

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](#)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

**Briefings de inteligência impulsionados por IA, adaptados aos seus interesses, construídos com tecnologia simples e implementável.**

O Meridiano elimina o ruído extraindo dados de fontes configuradas, analisando notícias com IA, agrupando eventos relacionados e entregando briefs diários concisos através de uma interface web.

Baseado no projeto original [meridian](https://github.com/iliane5/meridian).

---

## 🎯 Propósito

Inspirado no conceito de briefings diários presidenciais, o Meridiano fornece inteligência focada e personalizada para usuários individuais. Ele ajuda você a:
* **Manter-se informado** sobre os principais eventos globais ou tópicos específicos sem se afogar em ruído.
* **Entender o contexto** além das manchetes através da análise de IA.
* **Acompanhar o desenvolvimento de histórias** por meio do agrupamento inteligente de artigos.
* **Manter o controle** através de perfis de feed personalizáveis e código de código aberto.

---

## 🏗️ Arquitetura Técnica

O Meridiano é construído como um pipeline ETL modular em Python com uma interface web.

* **Pipeline Backend**: `run_briefing.py` orquestra a extração, processamento, avaliação e geração do brief.
* **Banco de Dados**: `SQLModel` com SQLite/PostgreSQL, apresentando FTS5 para pesquisa rápida de texto completo.
* **Servidor Web**: Uma interface limpa baseada em Flask (`app.py`) para navegar pelos briefings e artigos.
* **Integração de IA**: Usa `LiteLLM` para sumarização, avaliação e síntese (suporta Deepseek, Gemini, Together AI, etc.). Usa `scikit-learn` e embeddings para agrupamento (clustering).
* **Ferramentas Principais**: `uv` para gerenciamento de dependências, `trafilatura` para extração de conteúdo e `feedparser` para manipulação de RSS.

### Como Funciona

1. **Configuração**: Carrega as configurações base (`config_base.py`) e os perfis de feed (`feeds/<profile>.py`).
2. **Extração (Scraping)**: Busca RSS e extrai o conteúdo dos artigos. Gatilhos FTS preenchem `articles_fts`.
3. **Processamento**: Gera resumos e embeddings para artigos não processados.
4. **Avaliação (Rating)**: Usa um LLM para avaliar o impacto (1-10) com base nos resumos.
5. **Geração do Brief**: Agrupa artigos recentes, analisa os grupos e sintetiza um brief final.
6. **Interface Web**: Navegue pelos briefs, pesquise, filtre e classifique artigos via uma interface Flask.

---

## 🚀 Começando

### Pré-requisitos
* Python 3.10+
* Gerenciador de pacotes `uv`
* Chaves de API para provedores de LLM e Embedding (ex: Gemini, Deepseek, Together AI)

### Instruções de Instalação

1. **Clone o repositório:**
   ```bash
   git clone <url-do-seu-repositorio> meridiano
   cd meridiano
   ```

2. **Configure o ambiente:**
   ```bash
   # Instale as dependências usando uv
   uv sync
   ```

3. **Configure as Variáveis de Ambiente:**
   Copie `.env.example` para `.env` e adicione suas chaves de API:
   ```dotenv
   # Exemplo usando Gemini
   GEMINI_API_KEY="sua_chave_de_api_aqui"
   ```

4. **Configure os Feeds:**
   Revise `src/meridiano/config_base.py` e crie perfis de feed em `src/meridiano/feeds/`.

5. **Inicialize o Banco de Dados:**
   O banco de dados é inicializado automaticamente na primeira execução. Para PostgreSQL, defina `DATABASE_URL` no `.env`.

---

## 💻 Fluxo Operacional (Uso da CLI)

O Meridiano é controlado pelo script de linha de comando `run_briefing.py`.

### Uso Básico
Execute todas as etapas para o perfil padrão:
```bash
uv run -m meridiano.run_briefing --feed default --all
```

### Argumentos da CLI
* `--feed <perfil>`: Especifique o perfil (ex: `default`, `tech`). O padrão é `default`.
* `--scrape-articles`: Execute apenas a etapa de extração.
* `--process-articles`: Execute apenas a etapa de sumarização/embedding.
* `--rate-articles`: Execute apenas a etapa de avaliação de impacto.
* `--generate-brief`: Execute apenas a etapa de geração do brief.
* `--all`: Execute todas as etapas sequencialmente.
* `-m`, `--model`: Substitua o modelo de chat (ex: `gemini/gemma-3-4b`).
* `-n`, `--limit`: Limite o número de artigos a processar.

### Executando o Servidor Web
Inicie a interface Flask para ver seus briefings:
```bash
uv run -m meridiano.app
```
Acesse a interface em `http://localhost:5000`.

---

## 🐳 Executando com Docker

O Meridiano fornece um `Dockerfile` e `compose.yml` para fácil implantação.

* `make build`: Constrói a imagem Docker.
* `make up`: Inicia a aplicação web e o banco de dados na porta 5000.
* `make run ARGS="--feed default --all"`: Executa o processo de briefing dentro do Docker.

---

## 🤝 Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes.

### Créditos
* Conceito original: [iliane5/meridian](https://github.com/iliane5/meridian)
* Suporte a PostgreSQL: [commonProgrammerr](https://github.com/commonProgrammerr)
* Migração `uv` & `litellm`: [Costiss](https://github.com/Costiss)
* Testes & correções: [marcostx](https://github.com/marcostx)
* Docker & pacote padrão: [garciadias](https://github.com/garciadias)

## 📄 Licença
Licenciado sob a **GNU Affero General Public License v3.0 (AGPLv3)**.
