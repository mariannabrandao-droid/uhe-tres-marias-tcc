# Adaptar o painel

Faça uma cópia do repositório, rode o exemplo sem alterações e depois adapte uma tela por vez. Os arquivos desta página estão em `Painel_Tres_Marias/`.

| Bloco | Onde editar | Como conferir |
| --- | --- | --- |
| Entrada e navegação | `app.py` inicia o percurso guiado; `app_publica.py`, funções `main` e `glossary`, organiza o menu livre. `painel.py`, `PAGES` e `main`, organiza a sequência guiada. | Confira os rótulos, a tela inicial e as ações de avanço e retorno. |
| Cabeçalho e gráficos | `painel.py`, `configure_page` e `graph`, define identidade visual, layout, cores e configuração Plotly. | Confira legenda e eixos em uma janela estreita. Use unidades no eixo e traço ou marcador para distinguir séries importantes. |
| Contexto e postos | `painel.py`, `context` e primeiro tema de `science`; `postos_defesa.py` define os postos e `mapas.py` lê as camadas. | Atualize códigos, coordenadas, local da usina e ponto de controle em conjunto. Confira os limites das camadas e os códigos preservados como texto. |
| Vazão mensal e permanência | `science` apresenta o patamar, séries e sazonalidade. `hidroclima.py` define as variáveis, unidades e curva de permanência; `analise_defesa.py` calcula as sequências. | Compare o CSV, os meses completos e os pontos Q90/Q95. Teste um mês ausente e um exatamente igual ao patamar. |
| Associações climáticas | `science`, `analise_defesa.py` e `series_historicas.py` montam as séries, aplicam defasagens e calculam correlação. `visualizacoes.py` reúne as séries de contexto. | Confira a origem do mês t, o mês t+k, o número de pares e o ano hidrológico se a região tiver outro calendário. |
| Previsão mensal | `science` apresenta as estimativas por horizonte e o erro. `previsao_mensal/previsao.py` e suas dependências ficam dentro do ZIP e calculam os resultados retrospectivos. | Reexecute `auditar_previsao.py` para o exemplo. Para outra série, ajuste o alvo, a cobertura, o corte temporal e as referências simples. Gere novos CSVs antes de atualizar a interface. |
| Operação diária | `painel.py`, `operations`, escolhe janela e variáveis. `operacao_ons.py` define os identificadores hidráulicos e de geração, nomes de campos e leitura. | Compare o recorte com a fonte original, as unidades por eixo e a exigência de 24 horas válidas para média de geração. |
| Diagnóstico diário e horário | `painel.py`, `scenarios` e `hourly_view`; `defluencia_diurna.py` define `THRESHOLD`, converte o carimbo em início do intervalo e aplica a regra de elegibilidade. | Experimente outro patamar na tela e confira o gráfico, os indicadores e o CSV. Ao alterar o horário da janela no código, ajuste também o número de horas válidas exigido, os rótulos e o teste. |
| Consulta a jusante | `painel.py`, `downstream_evidence`, e `evidencia_jusante.py`. O modelo CSV usa `estacao,inicio_intervalo,vazao_m3s`. | Identifique a fonte, confirme a base horária e verifique o tempo de viagem antes de associar registros da usina e do rio. |
| Fontes e downloads | `synthesis`, `export` e `reproducibility` reúnem inventários, unidades e CSVs. `inventariar_series.py` recompõe o inventário da edição de referência. | Abra os arquivos exportados e confira formatos, unidades, cobertura e correspondência com a seleção. |

## Trocar as bases

1. Extraia o ZIP em uma pasta de trabalho e mantenha a estrutura interna. Localize as entradas em `ANA_Etapa02/entradas`, as séries mensais em `ANA_Etapa02/resultados` e os recortes ONS em `dados_ons/operacao`.
2. Preserve o esquema dos arquivos onde a origem e o significado das variáveis forem equivalentes. Se o novo produto usa outras colunas, unidades, códigos, fuso ou convenção de carimbo, adapte o leitor antes de calcular. Há séries ANA separadas por ponto e vírgula; os recortes ONS usam CSV separado por vírgulas.
3. Para reconstruir as tabelas de referência ANA, consulte as instruções da pasta `ANA_Etapa02` e reexecute as rotinas em uma cópia com as entradas esperadas. Atualize resultados, inventários e textos que mencionam datas ou achados do caso original.
4. Compacte as pastas internas diretamente na raiz do ZIP, sem incluir uma pasta-pai. Substitua `dados_painel.zip`, use um checkout limpo para verificar os caminhos e reinicie o Streamlit.
5. Rode os testes do exemplo antes das alterações. Na sua adaptação, atualize os testes de resultados com valores conferidos independentemente para a nova base.

As conclusões da versão guiada e a comparação com a previsão oficial de maio–junho de 2025 são específicas de Três Marias. Ajuste ou retire esses blocos ao adaptar o projeto a outra usina.
