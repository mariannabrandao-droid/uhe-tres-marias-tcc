"""Valida a resposta ANA e o fluxo da consulta livre sem depender da rede."""
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from consulta_ana import FIELDS, parse_series, station_distance

XML = b'''<DataTable><SerieHistorica><EstacaoCodigo>1943001</EstacaoCodigo>
<NivelConsistencia>2</NivelConsistencia><DataHora>2000-02-01</DataHora>
<Chuva28>0</Chuva28><Chuva29>2,5</Chuva29><Chuva29Status>1</Chuva29Status>
<Chuva30>95</Chuva30></SerieHistorica><SerieHistorica><EstacaoCodigo>1943001</EstacaoCodigo>
<NivelConsistencia>1</NivelConsistencia><DataHora>2000-02-01</DataHora>
<Chuva29>99</Chuva29></SerieHistorica></DataTable>'''


def main():
    start, end = date(2000, 2, 27), date(2000, 3, 1)
    rain = parse_series(XML, '01943001', 'Chuva', start, end, 2)
    assert rain.valor.tolist() == [0., 2.5]
    assert rain.data.tolist() == [date(2000, 2, 28), date(2000, 2, 29)]
    assert rain.iloc[1].status_ana == '1'
    assert 110 < station_distance(0, 0, 0, 1) < 112
    stations = pd.DataFrame([['01943001', 'RIO PIRACICABA', -19.9228, -43.1778,
                              'ATLÂNTICO,TRECHO LESTE', 'RIO DOCE', 'MINAS GERAIS', 1]], columns=FIELDS)
    app = Path(__file__).with_name('app_publica.py')
    at = AppTest.from_file(str(app), default_timeout=45).run()
    at.sidebar.radio[0].set_value('Histórico hidroclimático').run()
    at.radio(key='public_history_source').set_value('Outra localização · ANA').run()
    at.selectbox[0].select('Chuva')
    at.number_input[0].set_value(-19.93)
    at.number_input[1].set_value(-43.17)
    with patch('explorar_ana.cached_stations', return_value=(stations, False)) as search, \
         patch('explorar_ana.cached_regions', return_value=['ATLÂNTICO SUDESTE']):
        at.button[0].click().run()
    search.assert_called_once_with('Chuva', '', (-19.93, -43.17, 50))
    assert not at.exception
    assert 'RIO DOCE' in at.dataframe[0].value['Sub-bacia'].tolist()
    at.date_input[0].set_value(start)
    at.date_input[1].set_value(end)
    with patch('explorar_ana.cached_series', return_value=rain) as series:
        next(button for button in at.button if button.label == 'Consultar série histórica').click().run()
    series.assert_called_once_with('01943001', 'Chuva', start, end, 2)
    assert not at.exception
    assert {'2/4', '50.0%'} <= {metric.value for metric in at.metric}
    assert at.dataframe[1].value.valor.isna().all()
    assert len(at.get('download_button')) == 3
    print('Busca por coordenadas, série, lacunas, chuva zero e downloads verificados.')


if __name__ == '__main__':
    main()
