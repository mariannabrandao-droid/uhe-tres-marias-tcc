"""Figuras conceituais sem escala para a apresentação do TCC."""
import plotly.graph_objects as go


def _flow(title, nodes, arrows, height):
    fig = go.Figure()
    for start, end in arrows:
        fig.add_annotation(x=end[0], y=end[1], ax=start[0], ay=start[1],
                           xref='x', yref='y', axref='x', ayref='y',
                           text='', showarrow=True, arrowhead=3, arrowsize=1,
                           arrowwidth=2, arrowcolor='#42798b')
    for x, y, label in nodes:
        fig.add_annotation(x=x, y=y, text=label, showarrow=False, borderpad=7,
                           bgcolor='#e6f4f4', bordercolor='#9ccccc',
                           font=dict(color='#123450', size=12))
    fig.update_layout(title=title, height=height, hovermode=False,
                      xaxis=dict(visible=False, range=[0, 100], fixedrange=True),
                      yaxis=dict(visible=False, range=[0, 100], fixedrange=True))
    return fig


def water_routes():
    return _flow('Caminhos da água em uma hidrelétrica',
                 [(9, 50, 'Afluência'), (31, 50, 'Reservatório'),
                  (62, 75, 'Turbinas<br>com geração'), (62, 26, 'Vertedouro<br>sem geração'),
                  (90, 50, 'Rio a jusante')],
                 [((15, 50), (23, 50)), ((40, 54), (53, 71)), ((40, 46), (53, 30)),
                  ((72, 71), (81, 54)), ((72, 30), (81, 46))], 275)


def climate_flow():
    return _flow('Da circulação atmosférica à água que chega ao reservatório',
                 [(19, 73, 'ZCAS e bloqueios<br>indicadores mensais'),
                  (51, 73, 'Chuva no posto<br>em mm/mês'),
                  (82, 73, 'Vazão de referência<br>em m³/s'),
                  (51, 24, 'Solo e armazenamento<br>modulam a resposta')],
                 [((32, 73), (39, 73)), ((63, 73), (70, 73)), ((64, 30), (75, 62))], 285)
