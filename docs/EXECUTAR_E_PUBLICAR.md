# Executar e publicar

## Executar no computador

1. No GitHub, escolha **Code → Download ZIP** e extraia todo o conteúdo. Se usa Git, clone `https://github.com/mariannabrandao-droid/uhe-tres-marias-tcc.git`.
2. Instale Python 3.12 ou use o ambiente Python compatível já disponível. Abra um terminal na pasta extraída e entre em `Painel_Tres_Marias`.
3. Crie o ambiente e instale as dependências. Em Windows, também é possível abrir `INICIAR_WINDOWS.bat` para usar a consulta livre.

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app_publica.py
```

**macOS ou Linux**

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app_publica.py
```

Abra **http://localhost:8501**. Para abrir o percurso guiado use `app.py` no último comando. Se as duas versões estiverem abertas ao mesmo tempo, acrescente `--server.port 8502` à segunda execução. Use `Ctrl+C` no terminal para encerrar.

O primeiro acesso extrai `dados_painel.zip` ao lado do código. Mantenha o ZIP, os módulos e `requirements.txt` na mesma pasta. A internet é necessária para instalar dependências e consultar fontes externas por demanda.

## Publicar uma cópia no Streamlit Community Cloud

1. Faça um **fork** no GitHub e envie suas mudanças à branch que pretende publicar. Preserve a estrutura do projeto.
2. Entre no Streamlit Community Cloud com sua conta e conecte o GitHub. Autorize o acesso ao fork quando solicitado.
3. Escolha **Create app** e selecione seu repositório, a branch (por exemplo, `main`) e o caminho `Painel_Tres_Marias/app_publica.py`. Para publicar o percurso guiado, use `Painel_Tres_Marias/app.py`.
4. Selecione Python 3.12 em **Advanced settings** para acompanhar o ambiente de reprodução. Escolha seu subdomínio e clique em **Deploy**.
5. Abra a URL gerada. Visite o histórico e o diagnóstico horário e baixe um CSV. Se houver falha, confira **Manage app → Logs**, o caminho do arquivo e a instalação do `requirements.txt`.
6. Para atualizar sua cópia, envie as mudanças à mesma branch e mantenha o ponto de entrada. Se o app precisar reiniciar, use **Manage app → Reboot app**.

O endereço original acompanha a branch `main` e `Painel_Tres_Marias/app.py`. Uma cópia de terceiros usa o subdomínio próprio escolhido ao publicar.

[Publicar um app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app) · [Reiniciar uma implantação](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/reboot-your-app)
