"""Bloco de consulta livre por localização e estação."""
from datetime import date
from urllib.error import URLError
from xml.etree.ElementTree import ParseError

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from consulta_ana import HIDROWEB, VARIABLES, hydrographic_regions, read_series, search_stations, series_url

DEFAULT_POINT = (-18.20, -45.26)
SOURCE_ERRORS = (URLError, OSError, ValueError, ParseError, RecursionError)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_stations(variable, term, location):
    return search_stations(variable, term, location)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_regions(latitude, longitude):
    return hydrographic_regions(latitude, longitude)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_series(code, variable, start, end, level):
    return read_series(code, variable, start, end, level)


def download(frame, label, filename):
    st.download_button(label, frame.to_csv(index=False).encode('utf-8-sig'), filename, 'text/csv', on_click='ignore')


def station_map(stations, location):
    points = stations.dropna(subset=['LATITUDE', 'LONGITUDE'])
    if points.empty and location is None:
        return
    if location is None:
        center = dict(lat=points.LATITUDE.mean(), lon=points.LONGITUDE.mean())
        zoom = 3 if len(points) > 1 else 9
    else:
        center = dict(lat=location[0], lon=location[1])
        zoom = 8 if location[2] <= 50 else 6
    chart = go.Figure()
    chart.add_scattermap(lat=points.LATITUDE, lon=points.LONGITUDE, mode='markers', name='Estações ANA',
                         marker={'size': 10, 'color': '#087eae'},
                         text=points.CODIGO + ' · ' + points.NOME.fillna(''),
                         hovertemplate='%{text}<extra></extra>')
    if location is not None:
        chart.add_scattermap(lat=[location[0]], lon=[location[1]], mode='markers', name='Ponto pesquisado',
                             marker={'size': 15, 'color': '#a44e16'}, hoverinfo='name')
    chart.update_layout(map={'style': 'open-street-map', 'center': center, 'zoom': zoom},
                        height=390, margin=dict(l=0, r=0, t=0, b=0), legend={'orientation': 'h'})
    st.plotly_chart(chart, width='stretch', config={'displaylogo': False})


def show_series(series, code, variable, start, end, level):
    calendar = pd.date_range(start, end, name='data')
    indexed = series.assign(data=pd.to_datetime(series.data)).set_index('data').valor.reindex(calendar)
    valid = indexed.notna().sum()
    count, coverage = st.columns(2)
    count.metric('Dias com valor', f'{valid}/{len(calendar)}')
    coverage.metric('Cobertura no período', f'{100 * valid / len(calendar):.1f}%')
    unit = VARIABLES[variable][3]
    chart = go.Figure()
    if variable == 'Chuva':
        chart.add_bar(x=indexed.index, y=indexed, name='Chuva diária')
    else:
        chart.add_scatter(x=indexed.index, y=indexed, mode='lines+markers', name='Vazão diária', connectgaps=False)
    chart.update_layout(template='plotly_white', title=f'{variable} diária · estação {code}',
                        xaxis_title='Data', yaxis_title=f'{variable} ({unit})', margin={'l': 35, 'r': 20, 't': 55, 'b': 35})
    st.plotly_chart(chart, width='stretch', config={'displaylogo': False})
    st.caption(f'ANA/HidroWeb · Nível {level}. Lacunas são dias sem valor. O CSV preserva o código de status da ANA.')
    download(series, 'Baixar série diária (CSV)', f'ana_{code}_nivel_{level}_diario.csv')
    st.link_button('Abrir XML original da ANA', series_url(code, variable, start, end, level))
    with st.container(border=True):
        st.subheader('Diagnóstico mensal e sazonal')
        grouped = indexed.resample('MS')
        monthly = grouped.sum(min_count=1) if variable == 'Chuva' else grouped.mean()
        counts = grouped.count()
        complete = counts.eq(counts.index.days_in_month)
        summary = pd.DataFrame({
            'mes': counts.index.strftime('%Y-%m'), 'dias_validos': counts.values,
            'dias_no_mes': counts.index.days_in_month, 'valor': monthly.where(complete).values,
            'unidade': 'mm/mês' if variable == 'Chuva' else unit,
        })
        st.caption('O total de chuva ou a média de vazão só é calculado para meses completos.')
        monthly_valid = monthly.where(complete)
        left, right = st.columns(2)
        with left:
            fig = go.Figure(go.Scatter(x=monthly_valid.index, y=monthly_valid, mode='lines+markers', connectgaps=False, line=dict(color='#0d1d96')))
            fig.update_layout(title='Série mensal completa', yaxis_title=summary.unidade.iloc[0])
            st.plotly_chart(fig, width='stretch')
        with right:
            fig = go.Figure()
            for m in range(1, 13):
                fig.add_box(y=monthly_valid[monthly_valid.index.month == m].dropna(), name=str(m), marker_color='#0d6aff')
            fig.update_layout(title='Distribuição sazonal mensal', showlegend=False, xaxis_title='Mês', yaxis_title=summary.unidade.iloc[0])
            st.plotly_chart(fig, width='stretch')
        if variable == 'Vazão' and valid:
            values = indexed.dropna().sort_values(ascending=False).to_numpy()
            p = 100 * (pd.RangeIndex(1, len(values)+1).to_numpy()) / (len(values)+1)
            fig = go.Figure(go.Scatter(x=p, y=values, line=dict(color='#0d1d96')))
            fig.update_layout(title='Curva de permanência diária', xaxis_title='Frequência de excedência (%)', yaxis_title=unit)
            st.plotly_chart(fig, width='stretch')
            st.caption('Posição de Weibull; apenas dias válidos no período selecionado. Não equivale à curva mensal do estudo de Três Marias.')
        st.dataframe(summary, hide_index=True)
        download(summary, 'Baixar resumo mensal (CSV)', f'ana_{code}_nivel_{level}_mensal.csv')


def explorer():
    st.subheader('Estações e séries da ANA')
    st.write('Use coordenadas para localizar estações próximas ou pesquise pelo nome ou código. '
             'Selecione uma estação para ver a série histórica e baixar os dados.')
    st.caption('O diagnóstico utiliza somente a estação, variável e período selecionados. Não extrapola os resultados de Três Marias.')
    mode = st.radio('Como localizar a estação?', ('Coordenadas e raio', 'Nome ou código'), horizontal=True)
    with st.form('ana_search'):
        variable = st.selectbox('Variável medida', tuple(VARIABLES))
        if mode == 'Coordenadas e raio':
            first, second, third = st.columns(3)
            latitude = first.number_input('Latitude', -35., 6., DEFAULT_POINT[0], format='%.5f')
            longitude = second.number_input('Longitude', -74., -28., DEFAULT_POINT[1], format='%.5f')
            radius = third.number_input('Raio (km)', 1, 200, 50)
            location, term = (latitude, longitude, radius), ''
        else:
            location, term = None, st.text_input('Nome ou código ANA', placeholder='Ex.: 41020002', max_chars=80)
        search = st.form_submit_button('Buscar estações', type='primary')
    if search:
        st.session_state.pop('ana_series_result', None)
        st.session_state.pop('ana_stations_result', None)
        if location is None and not term.strip():
            st.warning('Informe o nome ou código da estação.')
        else:
            with st.spinner('Consultando o catálogo público do SNIRH…'):
                try:
                    stations, truncated = cached_stations(variable, term, location)
                except SOURCE_ERRORS:
                    st.error('Não foi possível consultar as estações no SNIRH. Tente novamente ou abra o HidroWeb.')
                else:
                    regions = None
                    if location is not None:
                        try:
                            regions = cached_regions(*location[:2])
                        except SOURCE_ERRORS:
                            st.warning('A camada de regiões hidrográficas está indisponível nesta consulta.')
                    st.session_state['ana_stations_result'] = (mode, variable, location, stations, truncated, regions)
    result = st.session_state.get('ana_stations_result')
    if result is not None and result[0] == mode:
        _, variable, location, stations, truncated, regions = result
        if regions:
            st.write(f'**Região hidrográfica do ponto:** {", ".join(regions)}')
        elif regions == []:
            st.info('O ponto não interceptou uma região hidrográfica na camada consultada.')
        if location is not None:
            st.caption('A busca usa distância em linha reta. Confira a bacia e a sub-bacia de cada estação na tabela.')
        if truncated:
            st.warning('O catálogo limitou a resposta a 200 registros. Reduza o raio ou refine o nome para evitar omissões.')
        if stations.empty:
            st.info('Nenhuma estação encontrada para a variável e os filtros escolhidos.')
        else:
            station_results(variable, location, stations)
    st.link_button('Consultar catálogo e séries no HidroWeb', HIDROWEB)


def station_results(variable, location, stations):
    station_map(stations, location)
    labels = {'CODIGO': 'Código ANA', 'NOME': 'Estação', 'BACIANOME': 'Bacia',
              'SUBBACIANOME': 'Sub-bacia', 'ESTADONOME': 'Estado', 'distancia_km': 'Distância (km)'}
    display = stations[[key for key in labels if key in stations]].rename(columns=labels)
    st.dataframe(display, hide_index=True, column_config={'Distância (km)': st.column_config.NumberColumn(format='%.1f')})
    download(stations, 'Baixar catálogo da busca (CSV)', 'estacoes_ana.csv')
    unique = stations.drop_duplicates('CODIGO').set_index('CODIGO')
    code = st.selectbox('Estação para consultar a série', unique.index,
                        format_func=lambda code: f'{code} · {unique.loc[code, "NOME"]}')
    with st.form('ana_series'):
        first, second = st.columns(2)
        end_default = date.today().replace(month=1, day=1)
        start = first.date_input('Data inicial', end_default.replace(year=end_default.year - 1), min_value=date(1900, 1, 1))
        end = second.date_input('Data final', end_default, min_value=date(1900, 1, 1))
        level = st.selectbox('Nível de consistência', (2, 1), format_func=lambda value: '2 · Consistido' if value == 2 else '1 · Bruto')
        fetch = st.form_submit_button('Consultar série histórica')
    if fetch:
        st.session_state.pop('ana_series_result', None)
        if start > end or (end - start).days > 3660:
            st.warning('Selecione um intervalo válido de até dez anos por consulta.')
        else:
            with st.spinner('Consultando o serviço de séries históricas da ANA…'):
                try:
                    series = cached_series(code, variable, start, end, level)
                except SOURCE_ERRORS:
                    st.error('Não foi possível carregar a série da ANA. Tente um período menor ou consulte o HidroWeb.')
                else:
                    st.session_state['ana_series_result'] = (code, variable, start, end, level, series)
    result = st.session_state.get('ana_series_result')
    if result is not None and not result[5].empty:
        collection = st.session_state.setdefault('study_series', {})
        collection[(result[0], result[1], result[2], result[3], result[4])] = result
    if result is None or result[:2] != (code, variable):
        return
    _, _, start, end, level, series = result
    if series.empty:
        st.info(f'A ANA não retornou valores de nível {level} nesse intervalo. Confira o período e o nível disponíveis no HidroWeb.')
    else:
        st.caption(f'Série consultada de {start:%d/%m/%Y} a {end:%d/%m/%Y}.')
        show_series(series, code, variable, start, end, level)
