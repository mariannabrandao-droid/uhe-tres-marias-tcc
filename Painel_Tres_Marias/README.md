# UHE Três Marias · Painel hidroclimático

Duas interfaces executáveis usam o acervo e o código científico do TCC de Marianna Brandão Ferreira (UFF). A defesa mantém sete páginas em sequência. A versão pública oferece navegação livre e glossário.

## Executar localmente

Use Python 3.12 e rode os comandos dentro de `Painel_Tres_Marias`.

```sh
python -m venv .venv
# Linux ou macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
# Em outro terminal com o mesmo ambiente ativado
python -m streamlit run app_publica.py --server.port 8502
```

O endereço padrão da defesa é http://localhost:8501. A versão pública abre em http://localhost:8502 com o comando acima. A primeira execução extrai `dados_painel.zip` dentro da pasta do aplicativo. O pacote reúne entradas, séries tratadas, figuras, cópias ONS e histórico de desenvolvimento.

## Reproduzir cálculos e testar

```sh
python -m pip install -r requirements-auditoria.txt
python -c "from preparar_dados import preparar_dados; preparar_dados()"
python testar_calculos_defesa.py
python testar_operacao.py
python auditar_previsao.py --saida ../previsao-reexecutada
python testar_interface_defesa.py
python testar_interface_publica.py
```

A auditoria usa o protocolo de `historico_desenvolvimento/previsao.py` extraído do acervo. O comando compara as séries de previsões, métricas e projeções com os CSVs de referência e grava cópias recalculadas em um diretório externo quando solicitado. O código de modelagem histórica permanece disponível para rastreabilidade.

## Fontes e atualização

- `ANA_Etapa02/entradas/` e `resultados/` guardam o SAR, as séries de estações ANA/HidroWeb, os índices climáticos e os produtos mensais admitidos. As rotinas históricas `selecionar_limpar.py` e `integrar_clima.py`, com os respectivos manifestos, documentam a seleção e a integração.
- `dados_ons/sem_atualizacoes/` guarda os recortes operacionais usados nas telas do TCC. `auditar_ons.py` compara o recorte de outubro de 2026 com os CSVs diário e horário originais do ONS. Informe os dois caminhos conforme `python auditar_ons.py --help`. As telas da edição acadêmica leem os recortes versionados.
- `assets/` guarda o logotipo, os mapas e as figuras de referência. O manifesto registra o PDF de origem das imagens.
- Para atualizar uma edição, trabalhe em outra branch, arquive a versão anterior e registre a fonte, a data de extração, a cobertura, as unidades e a impressão SHA-256 dos novos arquivos. Preserve o esquema das entradas, reexecute o tratamento, valide os resultados e atualize os textos e figuras que dependem dos recortes. Monte o ZIP a partir de cópias verificadas e reinicie as duas aplicações para recarregar os dados. A publicação de uma revisão dos resultados depende dessa conferência.

## Streamlit Community Cloud

No repositório atual, selecione a branch de revisão e `Painel_Tres_Marias/app.py` para a defesa e `Painel_Tres_Marias/app_publica.py` para um segundo aplicativo. Use Python 3.12. Mantenha `requirements.txt` e `dados_painel.zip` ao lado dos pontos de entrada. A configuração registrada na aplicação já existente exige acesso ao painel administrativo para verificar branch, commit e ponto de entrada.

[Instruções oficiais de publicação](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)

## Documentação

- [Parecer científico e visual](revisao/PARECER.md)
- [Matriz de correspondência com o TCC](revisao/CORRESPONDENCIA_TCC.md)
- [Inventário e roteiro de defesa](revisao/INVENTARIO_E_ROTEIRO.md)
- [Verificação e capturas](revisao/VALIDACAO.md)
