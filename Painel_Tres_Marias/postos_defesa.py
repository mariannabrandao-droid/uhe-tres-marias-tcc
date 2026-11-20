"""Rastreabilidade das séries pontuais, com base no inventário do projeto."""
import pandas as pd
import plotly.express as px

from hidroclima import DATA, LABELS, coverage

FLOW_POSTS = {
    'vazao_jusante_m3s': ('41020002', 'Rio São Francisco, a jusante da barragem',
                        'Histórico do ponto de controle citado pela ANA. A série mensal inclui anos anteriores à operação.'),
    'vazao_indaia_m3s': ('40963000', 'Rio Indaiá, tributário a montante',
                        'Contextualiza a resposta de uma sub-bacia. Representa apenas parte da contribuição ao reservatório.'),
    'vazao_barramento_m3s': ('40990080', 'Área do barramento',
                            'Série auxiliar. A variável física ainda precisa de confirmação cadastral antes de tratá-la como entrada ou saída.'),
}
RAIN_POSTS = {
    'chuva_barramento_mm': ('01845009', 'Área do barramento',
                           'Referência histórica de chuva próxima à usina.'),
    'chuva_mesquita_mm': ('01944060', 'Porto Mesquita, a sudeste da usina',
                         'Comparação histórica contemporânea ao Barramento, em outro ponto.'),
    'chuva_andrequice_mm': ('01845032', 'Andrequicé, a sudeste da usina',
                           'Série de chuva recente com sobreposição à vazão natural do SAR.'),
}


def catalog():
    return pd.read_csv(DATA / '01_decisao_45_estacoes.csv', sep=';', dtype={'codigo': str})


def describe(frame, posts):
    locations = catalog().set_index('codigo')
    rows = []
    for name, (code, position, reason) in posts.items():
        row = locations.loc[code]
        dates = coverage(frame[name])
        rows.append({'Série': LABELS[name], 'Código ANA': code, 'Posição': position,
                     'Latitude (°)': row.latitude, 'Longitude (°)': row.longitude,
                     'Distância ao barramento (km)': row.distancia_barramento_km,
                     'Início': dates['inicio'], 'Fim': dates['fim'],
                     'Meses válidos': dates['n'], 'Por que entra': reason})
    return pd.DataFrame(rows)


def coverage_chart(frame, posts):
    pieces = []
    for name, (code, *_) in posts.items():
        months = frame.index[frame[name].notna()]
        groups = months.to_period('M').asi8 - range(len(months))
        for _, dates in pd.Series(months).groupby(groups):
            pieces.append({'Posto': code, 'Início': dates.iloc[0],
                           'Fim': dates.iloc[-1] + pd.offsets.MonthBegin()})
    fig = px.timeline(pieces, x_start='Início', x_end='Fim', y='Posto',
                      title='Meses completos disponíveis por estação')
    fig.update_yaxes(type='category', autorange='reversed')
    fig.update_traces(marker_color='#087eae', hoverinfo='skip', hovertemplate=None)
    fig.update_layout(height=245)
    return fig
