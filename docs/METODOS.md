# Fontes, métodos e testes

| Pergunta | Dados e regra | Visualização e interpretação |
| --- | --- | --- |
| Quando a disponibilidade foi menor? | ANA/SAR. Média mensal da vazão natural em meses completos, contagem estrita abaixo do patamar e sequência interrompida por lacunas ou igualdade. Permanência pela posição de Weibull e interpolação linear. | Série mensal mostra a duração dos episódios. A curva ordenada descreve a excedência na amostra. |
| Como chuva e vazão variam em relação uma à outra? | ANA/HidroWeb, SAR e séries climáticas. Pearson em pares válidos, opção de anomalias por mês e retirada por ano hidrológico do mês-resposta. | Barras por defasagem e tabela com r, n e sensibilidade. A retirada de anos mostra dependência da amostra. |
| O modelo acrescenta informação? | Vazão natural SAR. Persistência, climatologia e Ridge com treino expansivo. O alvo do treino antecede a origem. O escalonador é ajustado no treino e os modelos compartilham os mesmos 21 meses-alvo por horizonte. | Linhas por mês-alvo e MAE por recorte. Apenas quatro alvos em baixa vazão, portanto esse recorte tem evidência limitada. A checagem com ONS é retrospectiva e separada do backtest SAR. |
| Quando a média diária encobre liberações menores? | ONS/SFTMAR, média diária oficial e janela de 6h a 18h, carimbo no fim do intervalo. Um dia elegível exige média válida e 12 intervalos. O diagnóstico original usa 300 m³/s. | Média oficial, mínimo diurno e marcador de divergência. O detalhamento informa intensidade e duração. A avaliação regulatória exige o critério aplicável e evidência na estação 41020002, incluindo tempo de viagem. |

## Referências usadas no desenho do painel

- Mapas, séries e tabelas compõem um percurso que conecta local, período e análise. Esse princípio de integração está em [Nelson et al. (2019)](https://doi.org/10.3389/fenvs.2019.00148) e [Mahjarin et al. (2026)](https://doi.org/10.2166/hydro.2026.164).
- Os recortes climáticos têm contexto regional em [Cataldi et al. (2025)](https://doi.org/10.3390/atmos16060699).
- A comparação de previsão mensal tem como antecedente local o estudo de [Paiva, Montenegro e Cataldi (2020)](https://doi.org/10.1590/2318-0331.252020190067), que usa precipitação do CFS e modelos chuva–vazão. A configuração deste painel usa vazões antecedentes e calendário.
- Para consultar os dados, acesse [HidroWeb](https://www.snirh.gov.br/hidroweb/), [SAR](https://www.ana.gov.br/sar0/), [ONS](https://dados.ons.org.br/) e [NOAA/CPC](https://www.cpc.ncep.noaa.gov/data/indices/). A série histórica 1931–2023 está identificada como acervo do estudo e tem atribuição institucional pendente.
- A interação com eixos temporais, a arquitetura de aplicação e os testes seguem as documentações de [Plotly](https://plotly.com/python/time-series/) e [Streamlit](https://docs.streamlit.io/develop/concepts/app-testing).

## Reexecutar os testes

Dentro de `Painel_Tres_Marias`, com o ambiente local ativado:

```sh
python -m pip install -r requirements-auditoria.txt
python -c "from preparar_dados import preparar_dados; preparar_dados()"
python testar_calculos_defesa.py
python testar_operacao.py
python auditar_previsao.py --saida ../previsao-reexecutada
python testar_interface_defesa.py
python testar_interface_publica.py
```

`auditar_previsao.py` confere os resultados com o acervo entregue. `auditar_ons.py` aceita os caminhos locais dos CSVs originais do ONS para verificar o recorte de outubro de 2026. Os caminhos e fontes estão descritos no manual dentro de `dados_ons/` após a extração.
