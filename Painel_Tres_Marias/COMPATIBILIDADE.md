# Consulta livre — alternativa responsiva

O arquivo app_publica_responsiva.py utiliza app_publica.py e os mesmos módulos, dados e dependências. Não altera cálculos, correlações ou a aplicação publicada. A entrada original permanece disponível.

## macOS (Intel e Apple Silicon) e Linux

Instale Python 3.12 de arquitetura nativa. No Terminal, dentro da pasta Painel_Tres_Marias:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app_publica_responsiva.py
```

## Windows (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app_publica_responsiva.py
```

Abra o endereço Local URL exibido no terminal. Use Safari, Chrome, Edge ou Firefox atualizados. Caso haja falha visual, teste zoom de 100%, janela anônima e outro navegador. Não desative a validação HTTPS.

## Validação recomendada

Testar larguras de 390, 768, 1024, 1280 e 1920 pixels, menu aberto e fechado, gráficos, tabelas, filtros, downloads e as cinco etapas da consulta. Comparar resultados e CSVs com a entrada original para as mesmas séries. Em caso de erro, registrar sistema, arquitetura, versão de Python, navegador, resolução, captura e mensagem do terminal.

As regras CSS são preventivas; não constituem certificação de compatibilidade universal nem validação em hardware macOS real.
