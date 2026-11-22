"""Acesso público ao catálogo SNIRH e às séries convencionais ANA."""
import calendar
from datetime import date
from json import load
from math import asin, cos, radians, sin, sqrt
from urllib.parse import urlencode
from xml.etree import ElementTree

import pandas as pd

from fontes_https import open_official

CATALOG = 'https://portal1.snirh.gov.br/server/rest/services/dados_abertos'
REGIONS = ('https://portal1.snirh.gov.br/arcgis/rest/services/SNIRH2016/'
           'Limites_hidrograficos_mapabase/MapServer/4/query')
HISTORY = 'https://telemetriaws1.ana.gov.br/ServiceANA.asmx/HidroSerieHistorica'
HIDROWEB = 'https://www.snirh.gov.br/hidroweb/serieshistoricas'
# Camada de estações com medição de descarga para vazão, e camada pluviométrica para chuva.
VARIABLES = {
    'Vazão': ('Estacao_Fluviometrica_com_Medicao_de_Descarga', 3, 'Vazao', 'm³/s'),
    'Chuva': ('Estacao_Pluviometrica', 2, 'Chuva', 'mm'),
}
FIELDS = ('CODIGO', 'NOME', 'LATITUDE', 'LONGITUDE', 'BACIANOME', 'SUBBACIANOME', 'ESTADONOME', 'OPERANDO')
MAX_STATIONS = 200


def endpoint(url, params):
    return f'{url}?{urlencode(params)}'


def features(url, **params):
    with open_official(endpoint(url, {'f': 'json', **params}), timeout=20) as response:
        payload = load(response)
    if 'features' not in payload:
        raise ValueError('O catálogo SNIRH não devolveu uma lista de resultados.')
    return [item['attributes'] for item in payload['features']], bool(payload.get('exceededTransferLimit'))


def hydrographic_regions(latitude, longitude):
    rows, _ = features(REGIONS, geometry=f'{longitude},{latitude}', geometryType='esriGeometryPoint',
                       inSR=4326, spatialRel='esriSpatialRelIntersects', outFields='RHI_NM',
                       returnGeometry='false')
    return sorted({row['RHI_NM'] for row in rows if row.get('RHI_NM')})


def station_distance(latitude, longitude, station_lat, station_lon):
    lat_difference = radians(station_lat - latitude)
    lon_difference = radians(station_lon - longitude)
    haversine = sin(lat_difference / 2) ** 2 + cos(radians(latitude)) * cos(radians(station_lat)) * sin(lon_difference / 2) ** 2
    return 6371.0088 * 2 * asin(sqrt(min(1., haversine)))


def search_stations(variable, term='', location=None):
    layer, _, _, _ = VARIABLES[variable]
    term = term.strip()
    if term.isascii() and term.isdecimal():
        where = f'CODIGO = {int(term[:9])}' if len(term) <= 9 else '1=0'
    elif term:
        if not all(char.isalnum() or char in " '-." for char in term):
            raise ValueError('Use letras, números, espaços, hífen, ponto ou apóstrofo na busca.')
        escaped = term.upper().replace("'", "''")
        where = f"UPPER(NOME) LIKE '%{escaped}%'"
    else:
        where = '1=1'
    if location is not None:
        lat, lon, radius = location
        lat_delta = radius / 110
        lon_delta = radius / (110 * cos(radians(abs(lat) + lat_delta)))
        where += (f' AND LATITUDE BETWEEN {lat - lat_delta:.6f} AND {lat + lat_delta:.6f}'
                  f' AND LONGITUDE BETWEEN {lon - lon_delta:.6f} AND {lon + lon_delta:.6f}')
    rows, truncated = features(
        f'{CATALOG}/{layer}/FeatureServer/0/query', where=where, outFields=','.join(FIELDS),
        returnGeometry='false', resultRecordCount=MAX_STATIONS, orderByFields='CODIGO',)
    frame = pd.DataFrame(rows, columns=FIELDS)
    frame['CODIGO'] = frame.CODIGO.map(lambda value: str(int(value)).zfill(8))
    frame[['LATITUDE', 'LONGITUDE']] = frame[['LATITUDE', 'LONGITUDE']].apply(pd.to_numeric, errors='coerce')
    if location is not None:
        frame = frame.dropna(subset=['LATITUDE', 'LONGITUDE']).copy()
        frame['distancia_km'] = [
            station_distance(lat, lon, row.LATITUDE, row.LONGITUDE) for row in frame.itertuples()
        ]
        frame = frame.loc[frame.distancia_km.le(radius)].sort_values('distancia_km')
    return frame, truncated or len(rows) == MAX_STATIONS


def series_url(code, variable, start, end, level):
    _, kind, _, _ = VARIABLES[variable]
    if start > end or (end - start).days > 3660:
        raise ValueError('Selecione um intervalo válido de até dez anos por consulta.')
    if level not in (1, 2) or not code.isascii() or not code.isdecimal():
        raise ValueError('Selecione um código de estação e um nível de consistência válidos.')
    return endpoint(HISTORY, dict(codEstacao=code, dataInicio=start.strftime('%d/%m/%Y'),
                                  dataFim=end.strftime('%d/%m/%Y'), tipoDados=kind, nivelConsistencia=level))


def parse_series(xml, code, variable, start, end, level):
    _, _, prefix, unit = VARIABLES[variable]
    root = ElementTree.fromstring(xml)
    if root.tag.rsplit('}', 1)[-1] not in ('DataTable', 'DataSet'):
        raise ValueError('O serviço ANA devolveu um documento inesperado.')
    rows = []
    for node in root.iter():
        tag = node.tag.rsplit('}', 1)[-1]
        if tag == 'Error' and node.text and 'sem dados para esta estação' not in node.text.casefold():
            raise ValueError('O serviço ANA informou erro na consulta.')
        if tag != 'SerieHistorica':
            continue
        row = {child.tag.rsplit('}', 1)[-1]: child.text for child in node}
        # O serviço pode retornar os dois níveis mesmo quando foi solicitado apenas um.
        if row.get('NivelConsistencia') != str(level) or row.get('EstacaoCodigo', '').zfill(8) != code.zfill(8):
            continue
        month = pd.to_datetime(row.get('DataHora'), errors='coerce')
        if month is None or pd.isna(month):
            raise ValueError('O serviço ANA devolveu um registro mensal com data inválida.')
        for day in range(1, calendar.monthrange(month.year, month.month)[1] + 1):
            day_date = date(month.year, month.month, day)
            if not start <= day_date <= end:
                continue
            field = f'{prefix}{day:02}'
            raw = row.get(field) or ''
            rows.append((day_date, raw.replace(',', '.'), row.get(field + 'Status'), row.get('DataIns')))
    frame = pd.DataFrame(rows, columns=['data', 'valor', 'status_ana', 'registro_ana'])
    frame['valor'] = pd.to_numeric(frame.valor, errors='coerce')
    frame['registro_ana'] = pd.to_datetime(frame.registro_ana, errors='coerce')
    frame = frame.drop_duplicates()
    # Para revisões no mesmo nível, usa o registro com a data de inserção mais recente.
    frame = frame.sort_values('registro_ana', na_position='first')
    chosen = frame.drop_duplicates('data', keep='last')
    tied = frame.merge(chosen[['data', 'registro_ana']], on=['data', 'registro_ana'])
    if tied.data.duplicated().any():
        raise ValueError('Há versões de uma data sem ordem de revisão identificável. Confira a série no HidroWeb.')
    values = chosen.dropna(subset=['valor']).sort_values('data')
    return values.assign(codigo=code, variavel=variable, unidade=unit, nivel_consistencia=level)


def read_series(code, variable, start, end, level):
    with open_official(series_url(code, variable, start, end, level), timeout=30) as response:
        return parse_series(response.read(), code, variable, start, end, level)
