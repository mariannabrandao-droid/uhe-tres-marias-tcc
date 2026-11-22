# Painel hidroclimático da UHE Três Marias

Consulte disponibilidade hídrica mensal, associações chuva–vazão, previsões retrospectivas e registros de operação. O exemplo integra dados ANA, ONS e acervo climático para localizar episódios de baixa liberação e recuperar os registros usados na análise.

[Abrir painel publicado](https://uhe-tres-marias-tcc-otuk87syyzpg5dh82bdq6f.streamlit.app/)

## Começar

| Quero | Onde começar |
| --- | --- |
| Rodar a consulta livre no computador | [Instalação e execução](docs/EXECUTAR_E_PUBLICAR.md#executar-no-computador) |
| Publicar minha cópia no Streamlit | [Publicação com GitHub](docs/EXECUTAR_E_PUBLICAR.md#publicar-uma-cópia-no-streamlit-community-cloud) |
| Modificar uma tela, filtro ou base | [Manual de adaptação](docs/ADAPTAR.md) |
| Conferir os dados e a metodologia | [Fontes, métodos e testes](docs/METODOS.md) |

## Estrutura

- [`Painel_Tres_Marias/app.py`](Painel_Tres_Marias/app.py) abre o percurso guiado no endereço publicado.
- [`Painel_Tres_Marias/app_publica.py`](Painel_Tres_Marias/app_publica.py) abre a consulta livre.
- [`Painel_Tres_Marias/painel.py`](Painel_Tres_Marias/painel.py) e [`visualizacoes.py`](Painel_Tres_Marias/visualizacoes.py) compõem as telas. As rotinas de cálculo e leitura ficam nos módulos ao lado.
- [`Painel_Tres_Marias/dados_painel.zip`](Painel_Tres_Marias/dados_painel.zip) contém o acervo de exemplo, os recursos das telas e os resultados reproduzíveis do experimento mensal.
- [`docs/`](docs/) reúne os manuais de execução, publicação, adaptação e métodos.

Desenvolvido por Marianna Brandão Ferreira, Universidade Federal Fluminense.
