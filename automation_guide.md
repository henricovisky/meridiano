# Guia de Automação: Meridiano no Ubuntu (1GB RAM)

Este guia descreve como automatizar a atualização do código, o processamento de dados e o reinício da interface web no seu servidor.

## 1. O Script de Automação (`run_update.sh`)

O arquivo `run_update.sh` foi criado na raiz do seu projeto. Ele realiza as seguintes ações:
1. Navega até a pasta do projeto.
2. Executa `git pull` para baixar as últimas melhorias.
3. Roda o pipeline `start_meridiano.py --all` (que já gerencia o ambiente virtual e dependências).
4. Possui espaços reservados para reiniciar o servidor web.

### Ajuste os caminhos
Abra o arquivo `run_update.sh` e altere a variável `PROJECT_DIR` para o caminho absoluto onde o projeto está no seu servidor (ex: `/home/ubuntu/meridiano`).

## 2. Permissão de Execução
No terminal do seu servidor, dê permissão para o script rodar:
```bash
chmod +x run_update.sh
```

## 3. Configurando o Gatilho (Cron)

Para rodar o script automaticamente (por exemplo, todos os dias às 04:00 da manhã):

1. Abra o editor de cron:
   ```bash
   crontab -e
   ```
2. Adicione a seguinte linha ao final do arquivo:
   ```cron
   0 4 * * * /home/usuario/meridiano/run_update.sh
   ```
   *Substitua `/home/usuario/meridiano` pelo caminho real.*

## 4. Gerenciando a Interface Web (1GB RAM)

Em servidores com pouca memória, é fundamental que o servidor web seja resiliente. Recomendamos usar **Systemd**.

### Exemplo de arquivo de serviço (`/etc/systemd/system/meridiano.service`)
Crie este arquivo para que o Flask rode em segundo plano e reinicie se o servidor for reiniciado:

```ini
[Unit]
Description=Servidor Web Meridiano
After=network.target

[Service]
User=seu_usuario
WorkingDirectory=/home/usuario/meridiano
ExecStart=/home/usuario/meridiano/.venv/bin/python -m meridiano.app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Comandos úteis:**
* `sudo systemctl enable meridiano` (inicia com o boot)
* `sudo systemctl start meridiano` (inicia agora)
* `sudo systemctl restart meridiano` (atualiza após o git pull no script bash)

> [!TIP]
> Se o pipeline de IA (`start_meridiano.py`) consumir muita memória e travar o servidor, considere limitar o número de artigos processados usando o argumento `--limit 5` no script bash.
