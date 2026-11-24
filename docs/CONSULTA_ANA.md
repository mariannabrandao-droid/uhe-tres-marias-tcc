# Consultar estações e séries da ANA

1. Rode `Painel_Tres_Marias/app_publica.py` e abra **Configuração da área**.
2. Selecione **Vazão** ou **Chuva**. Em **Coordenadas e raio**, informe latitude e longitude em graus decimais e o raio em quilômetros. Em **Nome ou código**, use o nome cadastrado ou o código ANA.
3. Clique em **Buscar estações**. Consulte o mapa e a tabela com informações de bacia, sub-bacia e estado. O catálogo filtrado pode ser salvo em CSV.
4. Selecione uma estação, o período e o nível de consistência. Clique em **Consultar série histórica**. Confira a cobertura e baixe o CSV diário. Expanda **Resumo mensal e cobertura** para baixar os totais de chuva ou as médias de vazão dos meses completos. Cada série consultada fica guardada durante a sessão e pode ser aberta em **Histórico e disponibilidade** e comparada em **Correlações hidroclimáticas**.

Para experimentar em outra bacia, use latitude **−19,93**, longitude **−43,17** e raio **25 km**. Procure a estação de vazão **56610000** ou a de chuva **01943001**, ambas em Rio Piracicaba (MG), sub-bacia do Rio Doce. Use o período de **1 a 31 de janeiro de 2000**, nível **2 · Consistido**.

## Alcance dos resultados

- A região hidrográfica é a região oficial cujo polígono intercepta o ponto. A bacia e a sub-bacia da estação vêm do cadastro. A distância em linha reta serve para localizar estações próximas e pode atravessar divisores de água.
- A busca consulta as camadas de estações pluviométricas e fluviométricas com medição de descarga. Uma estação cadastrada pode ter lacunas ou nenhum dado no período solicitado. A consulta limita a lista a 200 registros e cada pedido de série a dez anos.
- A extração conserva o nível solicitado e os códigos de status da ANA. O serviço pode devolver registros brutos e consistidos na mesma resposta. Lacunas permanecem em branco e chuva igual a zero permanece zero. Os meses incompletos aparecem com cobertura e sem total ou média.
- A consulta usa as estações e séries convencionais disponíveis naquele momento nos serviços públicos. Em caso de indisponibilidade, o link para o HidroWeb permanece acessível.
- Os blocos de operação, previsão e diagnóstico horário referem-se ao estudo de Três Marias. Esta extensão usa o mesmo percurso de consulta de postos, séries, cobertura e exportação para outras regiões.

Fontes oficiais: [HidroWeb](https://www.snirh.gov.br/hidroweb/serieshistoricas) · [Camadas de dados abertos do SNIRH](https://portal1.snirh.gov.br/server/rest/services/dados_abertos) · [Regiões hidrográficas](https://portal1.snirh.gov.br/arcgis/rest/services/SNIRH2016/Limites_hidrograficos_mapabase/MapServer/4) · [Serviço ANA e descrição das operações](https://telemetriaws1.ana.gov.br/ServiceANA.asmx?WSDL).
