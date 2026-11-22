# Parecer científico e visual

O protocolo reproduziu os resultados centrais do TCC nas entradas diárias e nos recortes operacionais arquivados. A previsão foi reexecutada a partir da matriz de modelagem e a variável-alvo foi confrontada com a agregação mensal do SAR. A página de defesa mantém a ordem do Quadro 3 e a consulta pública reutiliza as telas e os módulos científicos.

## Auditoria das séries e métricas

| Indicador | Reprodução |
| --- | --- |
| Vazão natural SAR | 81 meses completos (jan/2020 a set/2026). 16 meses estritamente abaixo de 150 m³/s (19,75%). Maior sequência de cinco meses (jun–out/2024). |
| Permanência SAR | Q90 de 100,87 m³/s e Q95 de 69,19 m³/s por posição de Weibull, ordenação decrescente e interpolação linear. |
| Andrequicé × SAR | Chuva diária admitida somada por mês completo e vazão natural diária promediada no SAR. Com anomalias por mês e vazão em t+2, Pearson r = 0,565654 e n = 76. |
| ZCAS C × Barramento | Agregação dos índices a partir dos dados diários. Pearson r = 0,67086 e n = 220, com anomalias mensais e defasagem zero na amostra comum dos recortes. |
| Outubro/2025 | 29 de 30 dias elegíveis divergentes. O dia sem cobertura completa fica fora do denominador. |
| Outubro/2026 | 8 de 31 dias elegíveis divergentes. 95 de 372 intervalos diurnos abaixo de 300 m³/s e dez dias com pelo menos uma hora abaixo. |
| 22/10/2026 | Média diária oficial de 450 m³/s, mínimo de 164 m³/s entre 13h e 14h e cinco horas consecutivas abaixo de 300 m³/s. |

Meses faltantes ou iguais ao limiar interrompem as sequências. As curvas se referem à vazão natural mensal do SAR. Afluência, defluência, vazões turbinada e vertida correspondem a grandezas operacionais próprias. Na comparação por hora, o carimbo ONS observado é o término do intervalo. A janela começa às 6h e encerra às 18h e exige média diária oficial e 12 intervalos distintos com vazão válida. Horas duplicadas e datas diárias duplicadas são rejeitadas.

### Agrupamento hidrológico das correlações

O código anterior rotulava os anos de novembro a outubro pela data do preditor, independentemente da defasagem. A revisão usa primeiro o mês-alvo (mês do preditor + defasagem), depois aplica o calendário novembro–outubro. Assim, um par outubro–novembro em t+1 pertence ao novo ano hidrológico. O teste confere as quatro defasagens e a passagem de outubro para novembro. O coeficiente integral, o número de pares e as faixas com defasagem zero permanecem iguais. No TCC, Sul H2 × SAR, defasagem zero, reproduziu r = −0,321 e faixa de −0,370 a −0,297. Como exemplo do efeito da correção em t+2, a faixa ZCAS C × Barramento passou de [−0,07749, 0,00856] a [−0,05787, 0,00118]. Trata-se de análise de sensibilidade amostral.

### Previsão mensal

| Modelo | MAE M+1 (m³/s) | MAE M+2 (m³/s) | NSE M+1 | NSE M+2 |
| --- | ---: | ---: | ---: | ---: |
| Climatologia | 200,35 | 200,35 | 0,645 | 0,645 |
| Ridge | 220,86 | 338,17 | 0,683 | 0,257 |
| Persistência | 247,76 | 405,55 | 0,461 | −0,453 |

A auditoria tem 21 meses-alvo por horizonte (jan/2025–set/2026), com 11 no período seco e quatro abaixo de 150 m³/s. A climatologia tem o menor MAE global nos dois horizontes. Ridge tem o maior NSE global em M+1, coerente com seu menor erro quadrático nesse recorte. Persistência tem o menor MAE no subgrupo de baixa vazão em M+1.

A persistência usa o valor da origem e a climatologia usa a média histórica do mês-alvo com dados até a origem. Os atributos Ridge usam as vazões na origem e nos meses −1, −2, −3, −6 e −12, com seno e cosseno do mês-alvo. O treino Ridge admite alvos estritamente anteriores à origem. O escalonador é ajustado dentro de cada pipeline de treino e α é escolhido entre 1, 10 e 100 com validação interna temporal e fallback 10. Os conjuntos de seleção e auditoria são separados no tempo, com uma janela de expurgo antes da primeira origem auditada. Essa checagem cobre a ordem temporal dos registros fornecidos. A disponibilidade de cada observação na data original, incluindo possíveis revisões posteriores do SAR, exigiria versões históricas das bases.

A checagem complementar de outubro de 2026 usa a média ONS de 31 registros de vazão natural (292,87 m³/s) e estimativas com origem em setembro. A evidência é pontual e usa fonte diferente da referência SAR do backtest. As projeções arquivadas incluem M+3 e faixas empíricas baseadas em 21 resíduos por horizonte/modelo. M+1 e M+2 são os horizontes discutidos no TCC. As faixas descrevem a distribuição histórica dos erros e carecem de validação de cobertura futura.

O diagnóstico de escala com 300 m³/s descreve a descarga na usina. Avaliar conformidade exige a regra, o ponto de controle e a resolução temporal aplicáveis. A comparação com a estação 41020002 usa horário de Brasília e horário coincidente para triagem. A propagação depende do tempo de viagem. A base horária consistida recente da estação permanece pendente.

## Parecer de visualização

| Visualização | Justificativa e leitura |
| --- | --- |
| Séries mensais e operacionais | Linhas preservam a sequência e as lacunas. Eixos e legendas identificam grandezas. Use detalhes por ponto e tabelas baixáveis para conferência. |
| Sazonalidade | Caixas por mês mostram dispersão e mediana. O tamanho amostral no eixo ajuda a interpretar meses com cobertura diferente. |
| Permanência | Uma curva ordenada mostra a relação entre vazão e excedência. Marcadores e traços identificam Q90 e Q95; a tabela exportável permite conferir a interpolação. |
| Associações | A figura de defasagens dá contexto e a tabela mantém r, n e faixa de retirada juntos. Controles comparam dados originais e anomalias. O mapa informa o recorte espacial. |
| Previsão | Séries alinhadas por mês-alvo mostram os desvios e a tabela de erros compara horizontes na mesma unidade. Os detalhes deixam visíveis os limites de cobertura. |
| Diagnóstico horário | As barras correspondem a intervalos de 1h. Faixa de fundo, linha tracejada e texto identificam a janela, o limiar e a média oficial. Tabela e CSV oferecem os valores numéricos. |
| Mapas e figuras da defesa | O mapa responde à localização. O gráfico responde à mudança temporal. Figuras estáticas dão referência para a fala e exploradores em expansores dão acesso a valores e explicações. |

A referência institucional e a hierarquia existentes continuam nas duas telas. A versão pública reduz o conteúdo de apresentação oral e mantém filtros junto à análise. Foram verificados os fluxos, a renderização e a largura de capa em navegador. Uma avaliação integral de conformidade WCAG, leitores de tela e diferentes dispositivos continua pendente. As figuras de referência permanecem rasterizadas, com legenda textual e alternativas em dados interativos quando disponíveis.

A seção 4.7 cita a integração espacial e temporal na Tethys Platform e no Tethys Dash, além de exemplos de aplicação hidrológica com Streamlit. A arquitetura cliente–servidor, o cache, os testes e a publicação seguem a documentação do Streamlit. As séries, interações e escalas seguem a documentação do Plotly. O uso conjunto de texto, padrões e cor segue o princípio de uso de cor da WCAG. [Nelson et al. (2019)](https://doi.org/10.3389/fenvs.2019.00148) · [Mahjarin et al. (2026)](https://doi.org/10.2166/hydro.2026.164) · [Yadav et al. (2024)](https://doi.org/10.1007/s40899-024-01137-9) · [Pulla et al. (2024)](https://doi.org/10.3390/w16070949) · [Arquitetura Streamlit](https://docs.streamlit.io/develop/concepts/architecture/architecture) · [Cache](https://docs.streamlit.io/develop/concepts/architecture/caching) · [App testing](https://docs.streamlit.io/develop/concepts/app-testing) · [Séries Plotly](https://plotly.com/python/time-series/) · [WCAG 2.2](https://www.w3.org/TR/WCAG22/). A referência de Mahjarin foi consultada no TCC e o site da editora restringiu o acesso nesta revisão.

## Ajustes no documento acadêmico

1. Explicitar na seção 5.6 que o ano hidrológico é atribuído pelo mês da variável-resposta quando existe defasagem. A faixa citada para Sul H2 e os resultados centrais preservam seus valores.
2. Se o TCC passar a descrever a revisão, atualizar o apêndice de código e indicar a segunda interface em 5.9. As capturas 13 e 14 podem ser mantidas como registro da edição anterior ou atualizadas com indicação da versão. A numeração exibida no painel segue o documento final; o manifesto das imagens registra a extração do PDF anterior.
3. Caso seja necessário afirmar equivalência com a versão publicada, obter a configuração e o commit direto no Streamlit Community Cloud. O endereço consultado solicitou autenticação. A branch principal do GitHub no início da revisão estava em `91e07b1`.
4. Se houver afirmação de verificação a jusante, condicioná-la a dados horários consistidos e à avaliação do tempo de viagem. Registrar a atribuição institucional da planilha histórica Três Marias (156), ainda pendente no acervo.
