"""Mapas cadastrais e camadas oficiais para consulta local."""
import json
from math import cos, radians

import plotly.graph_objects as go

from hidroclima import ROOT
from postos_defesa import catalog

BARRAMENTO = '01845009'
JUSANTE = '41020002'
POSTOS = {
    BARRAMENTO: ('Posto do Barramento', 'Chuva pontual no local de referência da usina', '#075985'),
    JUSANTE: ('Três Marias Jusante', 'Estação fluviométrica citada no art. 3º da Resolução ANA 2.081/2017', '#b45309'),
    '01845032': ('Andrequicé', 'Chuva pontual', '#047857'),
    '01944060': ('Porto Mesquita', 'Chuva pontual', '#047857'),
    '40963000': ('Porto Indaiá', 'Vazão do rio Indaiá', '#6d28d9'),
    '40990080': ('Barramento · vazão auxiliar', 'Variável física pendente de confirmação', '#6d28d9'),
}


def _paths(filename, geometry_type):
    path = ROOT / 'assets' / filename
    for feature in json.loads(path.read_text(encoding='utf-8'))['features']:
        shape = feature['geometry']
        if shape['type'] == geometry_type:
            yield shape['coordinates']
        elif shape['type'] == f'Multi{geometry_type}':
            yield from shape['coordinates']


def _markers(chart, codes):
    locations = catalog().set_index('codigo')
    for code in codes:
        label, role, color = POSTOS[code]
        row = locations.loc[code]
        chart.add_scatter(
            x=[row.longitude], y=[row.latitude], mode='markers+text', name=label,
            text=[label], textposition='bottom center' if code == '40990080' else 'top center',
            marker=dict(size=18 if code == '40990080' else 12, color=color,
                        symbol='circle-open' if code == '40990080' else 'circle',
                        line=dict(color=color if code == '40990080' else 'white', width=2)),
            hovertemplate=f'<b>{label}</b><br>{code} · {role}<br>'
                          '%{y:.4f}°, %{x:.4f}°<extra></extra>',
        )


def _layout(chart, title):
    chart.update_layout(title=title, height=470, dragmode='pan', hovermode='closest', showlegend=False,
                        xaxis_title='Longitude (°)', yaxis_title='Latitude (°)')
    chart.update_yaxes(scaleanchor='x', scaleratio=1 / cos(radians(18)), constrain='domain')
    return chart


def regional_map():
    chart = go.Figure()
    for polygon in _paths('regiao_sao_francisco.geojson', 'Polygon'):
        for index, ring in enumerate(polygon):
            x, y = zip(*ring)
            chart.add_scatter(x=x, y=y, mode='lines', fill='toself',
                              fillcolor='#cee9e6' if index == 0 else '#ffffff',
                              line=dict(color='#087f8c', width=1), hoverinfo='skip')
    _markers(chart, [BARRAMENTO])
    return _layout(chart, 'Três Marias na Região Hidrográfica São Francisco')


def local_map():
    chart = go.Figure()
    xs, ys = [], []
    for line in _paths('hidrografia_tramo.geojson', 'LineString'):
        x, y = zip(*line)
        xs.extend([*x, None])
        ys.extend([*y, None])
    chart.add_scatter(x=xs, y=ys, mode='lines', line=dict(color='#38a4c2', width=1.5),
                      hoverinfo='skip', name='Trechos da BHO')
    _markers(chart, [BARRAMENTO, JUSANTE])
    chart.update_xaxes(range=[-45.32, -45.18])
    chart.update_yaxes(range=[-18.27, -18.13])
    return _layout(chart, 'Barramento e estação de controle a jusante')


def network_map(codes=None, all_stations=False):
    chart = go.Figure()
    locations = catalog()
    if all_stations:
        locations = locations[~locations.codigo.isin(POSTOS)].dropna(subset=['longitude', 'latitude'])
        chart.add_scatter(x=locations.longitude, y=locations.latitude, mode='markers',
                          name='Outros postos cadastrados', marker=dict(color='#8394a3', size=7),
                          customdata=locations[['codigo', 'nome', 'uso']].to_numpy(),
                          hovertemplate='%{customdata[0]} · %{customdata[1]}<br>%{customdata[2]}<extra></extra>')
    codes = list(POSTOS) if codes is None else codes
    _markers(chart, codes)
    if not all_stations:
        # Margem explícita para rótulos, inclusive nos postos próximos ao barramento.
        local = locations[locations.codigo.isin(codes)]
        chart.update_xaxes(range=[local.longitude.min() - .22, local.longitude.max() + .22])
        chart.update_yaxes(range=[local.latitude.min() - .14, local.latitude.max() + .17])
    return _layout(chart, 'Inventário de estações ANA' if all_stations else 'Postos das séries apresentadas')


def climate_map(kind):
    """Recortes da tabela 2 de Cataldi et al. (2025), DOI 10.3390/atmos16060699."""
    chart = regional_map()
    if kind == 'ZCAS':
        boxes = [('AB', -44, -42, -21, -16), ('C', -44, -42, -23.5, -21),
                 ('DE', -44, -42, -28.5, -23.5)]
    else:
        boxes = [('Norte H1', -60, -50, -17.5, -10), ('Norte H2', -50, -40, -17.5, -10),
                 ('Sul H1', -60, -50, -25, -17.5), ('Sul H2', -50, -40, -25, -17.5)]
    for label, west, east, south, north in boxes:
        chart.add_shape(type='rect', x0=west, x1=east, y0=south, y1=north, layer='below',
                        line=dict(color='#335c9b', width=2), fillcolor='rgba(66,111,175,.12)')
        chart.add_annotation(x=(west + east) / 2, y=(south + north) / 2,
                             text=label, showarrow=False, font=dict(color='#1a436d', size=14))
    title = 'Faixas do índice de ZCAS' if kind == 'ZCAS' else 'Subáreas do índice de bloqueio'
    return _layout(chart, title)
