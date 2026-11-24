# Painel hidroclimático da UHE Três Marias

Consulte disponibilidade hídrica mensal, associações chuva–vazão, previsões retrospectivas e registros de operação. O exemplo integra dados ANA, ONS e acervo climático para localizar episódios de baixa liberação e recuperar os registros usados na análise.

A consulta livre (`app_publica.py`) abre em **Configuração da área**, onde é possível pesquisar estações de chuva ou vazão da ANA, reunir séries e calcular correlações mensais com defasagem. Para telas menores, utilize `app_publica_responsiva.py` e consulte [Compatibilidade](Painel_Tres_Marias/COMPATIBILIDADE.md). [Como pesquisar estações e séries](docs/CONSULTA_ANA.md)

[Abrir painel publicado](https://uhe-tres-marias-tcc-otuk87syyzpg5dh82bdq6f.streamlit.app/)

## Começar

| Quero | Onde começar |
| --- | --- |
| Rodar a consulta livre no computador | [Instalação e execução](docs/EXECUTAR_E_PUBLICAR.md#executar-no-computador) |
| Publicar minha cópia no Streamlit | [Publicação com GitHub](docs/EXECUTAR_E_PUBLICAR.md#publicar-uma-cópia-no-streamlit-community-cloud) |
| Modificar uma tela, filtro ou base | [Manual de adaptação](docs/ADAPTAR.md) |
| Conferir os dados e a metodologia | [Fontes, métodos e testes](docs/METODOS.md) |

## Coleta convencional ANA

O script [`coletar_ana.py`](coletar_ana.py), descrito na metodologia, consulta o ServiceANA e preserva respostas XML, tabelas CSV e o registro de falhas. Requer Python 3.10 ou superior. Execute `python coletar_ana.py --help` para consultar as opções. A conversão dos registros mensais em série diária é uma etapa posterior.

## Estrutura

- [`Painel_Tres_Marias/app.py`](Painel_Tres_Marias/app.py) abre o percurso guiado no endereço publicado.
- [`Painel_Tres_Marias/app_publica.py`](Painel_Tres_Marias/app_publica.py) abre a consulta livre.
- [`Painel_Tres_Marias/painel.py`](Painel_Tres_Marias/painel.py) e [`visualizacoes.py`](Painel_Tres_Marias/visualizacoes.py) compõem as telas. As rotinas de cálculo e leitura ficam nos módulos ao lado.
- [`Painel_Tres_Marias/dados_painel.zip`](Painel_Tres_Marias/dados_painel.zip) contém o acervo de exemplo, os recursos das telas e os resultados reproduzíveis do experimento mensal.
- [`docs/`](docs/) reúne os manuais de execução, publicação, adaptação e métodos.

Desenvolvido por Marianna Brandão Ferreira, Universidade Federal Fluminense.
