"""Blocos de consulta da defesa, integrados às páginas existentes."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analise_defesa import BLOCKS, ZCAS
from series_historicas import ASSETS, MONTHS, NOAA, NOAA_DATA, OCT_MAR, blocking_seasonality, historical_flows, oni_series, zcas_annual
from hidroclima import ROOT
import operacao_ons as ons
from mapas import regional_map


def context_figures(figure):
    """Visões de contexto: localização, funcionamento conceitual e encadeamento de reservatórios."""
    st.markdown('### Da estrutura física às variáveis monitoradas')
    photo_path = ROOT / 'foto_vertedouro.png'
    supplied = photo_path.exists()
    source = 'https://www.cemig.com.br/wp-content/uploads/2026/02/uhe-tres-marias-862x350.jpg'
    if supplied:
        from base64 import b64encode
        source = 'data:image/png;base64,' + b64encode(photo_path.read_bytes()).decode('ascii')
    photo_col, reading_col = st.columns([2.3, 1], gap='medium')
    with reading_col:
        focus = st.radio('Explore a estrutura', ['Visão geral', 'Armazenamento', 'Turbinamento', 'Vertimento', 'Defluência'], key='physical_focus')
        descriptions = {
            'Visão geral': 'A entrada, o estoque e a saída são observados por indicadores diferentes.',
            'Armazenamento': 'O volume útil descreve o estoque de água no reservatório.',
            'Turbinamento': 'A água captada segue internamente até a casa de força. O percurso interno não é visível.',
            'Vertimento': 'A água liberada pelo vertedouro não passa pelas turbinas.',
            'Defluência': 'A saída da usina é analisada nas escalas diária e horária.',
        }
        st.info(descriptions[focus])
        st.image(str(ROOT / 'esquema_reservatorio.svg'), width='stretch')
    with photo_col:
        w, h = (800, 533) if supplied else (862, 350)
        photo = go.Figure()
        photo.add_layout_image(dict(source=source, x=0, y=h, sizex=w, sizey=h, xref='x', yref='y', sizing='stretch', layer='below'))
        labels = [('Armazenamento', 'Reservatório', 570, 155, -85, -48), ('Turbinamento', 'Casa de força', 530, 272, 85, -32), ('Vertimento', 'Vertedouro', 275, 255, -95, -40), ('Defluência', 'Rio a jusante', 610, 420, 70, -35), ('Armazenamento', 'Barramento', 710, 235, 10, -55)] if supplied else [('Armazenamento', 'Reservatório', 310, 95, 15, -52), ('Armazenamento', 'Barramento', 440, 158, 80, -42), ('Turbinamento', 'Tomada de água', 160, 158, -60, -42), ('Turbinamento', 'Casa de força', 205, 278, 100, -42), ('Defluência', 'Rio a jusante', 640, 287, 65, -45)]
        for category, label, x, y, ax, ay in labels:
            if focus == 'Visão geral' or category == focus:
                photo.add_annotation(x=x,y=h-y,text=label,ax=ax,ay=ay,showarrow=True,arrowhead=2,arrowwidth=2,arrowcolor='#0d1d96',bgcolor='#ffffff',bordercolor='#0d1d96',borderpad=5,font=dict(color='#0d1d96',size=12))
        photo.update_xaxes(range=[0,w],visible=False,fixedrange=True)
        photo.update_yaxes(range=[0,h],visible=False,fixedrange=True,scaleanchor='x')
        photo.update_layout(height=520,margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor='white',plot_bgcolor='white')
        st.plotly_chart(photo,width='stretch',key='physical_photo',config={'displayModeBar':False})
        st.caption('Fotografia fornecida para o TCC; data e autoria a confirmar.' if supplied else 'Fotografia institucional: Cemig. Nesta perspectiva o vertedouro não está identificado; consulte o esquema ao lado.')
        st.markdown('[Referência técnica das estruturas — Cemig, PAE, seção D](https://www.cemig.com.br/wp-content/uploads/2025/07/PAE_UHE_Tres_Marias_revF-Tachado.pdf)')
    st.markdown('### Onde a usina está e como a água percorre o sistema')
    left, right = st.columns([1.08, .92], gap='large')

    with left:
        regional = regional_map()
        regional.update_layout(
            title='Três Marias na Região Hidrográfica São Francisco',
            height=415,
        )
        regional.update_traces(hoverinfo='skip', hovertemplate=None)
        figure(
            regional, 'tcc_fig02',
            'Localização do empreendimento na Região Hidrográfica São Francisco. '
            'Base cartográfica ANA/SNIRH; o mapa serve à orientação espacial, não à análise de distância.'
        )

    with right:
        st.markdown('**Funcionamento físico do reservatório**')
        st.image(str(ROOT / 'esquema_reservatorio.svg'), width='stretch')
        st.caption('Esquema conceitual, sem escala. Afluência, armazenamento, turbinamento, vertimento e defluência são variáveis distintas.')

    st.markdown('### Três Marias no encadeamento dos principais aproveitamentos')
    nodes = [
        ('Três Marias', 0, 0, '396 MW · 19 bilhões m³ totais · 15 bilhões m³ úteis'),
        ('Sobradinho', 0, 1, '1.050 MW · 34 bilhões m³ totais · 28 bilhões m³ úteis'),
        ('Itaparica', 0, 2, '1.500 MW · 10 bilhões m³ totais · 3 bilhões m³ úteis'),
        ('Moxotó', 0, 3, '400 MW'),
        ('Paulo Afonso I–III', 0, 4, 'I: 180 MW · II: 445 MW · III: 800 MW'),
        ('Paulo Afonso IV', -.55, 4, '2.460 MW'),
        ('Xingó', 0, 5, '3.000 MW'),
    ]
    chart = go.Figure()
    for route in ((0, 1, 2, 3, 4, 6), (2, 5, 6)):
        chart.add_scatter(
            x=[nodes[i][1] for i in route], y=[nodes[i][2] for i in route],
            mode='lines', line={'color': '#3a8097', 'width': 3},
            hoverinfo='skip', showlegend=False,
        )
    names, x, y, values = zip(*nodes)
    chart.add_scatter(
        x=x, y=y, mode='markers', marker={'size': 15, 'color': '#087eae'},
        text=names, customdata=values, showlegend=False,
        hovertemplate='<b>%{text}</b><br>%{customdata}<extra></extra>',
    )
    for name, position, row, _ in nodes:
        chart.add_annotation(
            x=position, y=row, text=name, showarrow=False,
            xanchor='left', xshift=12, font=dict(size=12, color='#173b52'),
        )
    chart.update_layout(
        title='Principais aproveitamentos do São Francisco · montante → jusante',
        height=385, hovermode='closest',
        yaxis=dict(visible=False, range=[5.45, -.45], fixedrange=True),
        xaxis=dict(visible=False, range=[-.68, .78], fixedrange=True),
    )
    figure(
        chart, 'tcc_fig03',
        'Esquema de montante a jusante, sem escala. Passe sobre os pontos para ver as potências e os volumes '
        'indicados na referência histórica da ANA (2013). Os valores retratam essa referência.'
    )

def historical_figures(figure):
    with st.expander('Vazões históricas por ano e mês'):
        flows = historical_flows()
        monthly = flows.iloc[:, :12]
        chart = go.Figure()
        for size in (93, 50, 30, 10):
            sample = monthly.tail(size)
            chart.add_scatter(x=MONTHS, y=sample.mean(), mode='lines+markers',
                              name=f'{sample.index.min()}–{sample.index.max()}')
        chart.update_layout(title='Vazão média por mês e janela histórica',
                            yaxis_title='Vazão (m³/s)', xaxis_title='Mês do calendário')
        figure(chart, 'tcc_fig01', 'Fonte: planilha histórica Três Marias (156) do acervo do estudo. '
               'Cada curva é a média de um mesmo mês do calendário entre os anos indicados.')
        chart = go.Figure(go.Scatter(x=flows.index, y=flows.media_anual_m3s, mode='lines',
                                     hovertemplate='%{x}: %{y:.2f} m³/s<extra></extra>'))
        chart.update_layout(title='Vazão média anual em Três Marias', yaxis_title='Vazão (m³/s)', xaxis_title='Ano')
        chart.update_xaxes(tickmode='array', tickvals=[1931, *range(1940, 2020, 10), 2023], tickangle=0)
        figure(chart, 'tcc_fig04', 'Fonte: planilha histórica Três Marias (156) do acervo do estudo, coluna jan–dez. '
               'Média aritmética das 12 vazões mensais de cada ano, de 1931 a 2023. '
               'A planilha está incluída para rastreabilidade. A origem institucional da série ainda requer confirmação.')
        st.download_button('Baixar série histórica de vazão',
                           (ASSETS / 'vazao_1931_2023.csv').read_bytes(), 'vazao_1931_2023.csv', 'text/csv')


def climate_history(figure, frame):
    with st.expander('Histórico e sazonalidade dos índices climáticos'):
        region = st.selectbox('Região do índice de ZCAS', ZCAS, format_func=lambda key: key.split('_')[1])
        values = zcas_annual(frame[region])
        chart = go.Figure()
        for name in values:
            chart.add_scatter(x=values.index, y=values[name], name=name, mode='lines', connectgaps=False)
        chart.update_layout(title=f'Índice anual da ZCAS na região {region.split("_")[1]}',
                            xaxis_title='Ano', yaxis_title='Índice ZCAS (adimensional)')
        chart.update_xaxes(tickmode='array', tickvals=[1961, 1970, 1980, 1990, 2000, 2010, 2023], tickformat='d')
        figure(chart, 'tcc_fig06', 'Fonte: índice diário do acervo climático, 1961–2023. Médias anuais '
               'das 12 médias mensais, seguidas de médias móveis retrospectivas de 3 e 5 anos completos. '
               'O índice quantifica o sinal associado à atuação da ZCAS. A contagem de eventos exige um critério de detecção.')
        st.download_button('Baixar série anual da ZCAS', values.to_csv(index_label='ano').encode('utf-8-sig'),
                           'zcas_anual.csv', 'text/csv')
        region = st.selectbox('Região de bloqueio atmosférico', list(BLOCKS))
        seasonal = blocking_seasonality(frame[region])
        chart = go.Figure(go.Bar(x=MONTHS, y=seasonal['mean'], customdata=seasonal['count'],
                                 marker_color=['#087eae' if m in OCT_MAR else '#98afbe' for m in range(1,13)],
                                 hovertemplate='%{x}: %{y:.2f} dias · %{customdata} anos<extra></extra>'))
        chart.update_layout(title=f'Sazonalidade mensal dos bloqueios ({region})',
                            yaxis_title='Média de dias sinalizados por mês', xaxis_title='Mês')
        figure(chart, 'tcc_fig07', 'Fonte: campos diários de bloqueio do acervo climático, 1961–2023. '
               'A média usa meses completos. As barras azuis destacam outubro–março, '
               'janela usada para comparar bloqueios com ZCAS na aba Associações climáticas.')
        st.download_button('Baixar sazonalidade dos bloqueios', seasonal.to_csv(index_label='mes').encode('utf-8-sig'),
                           'sazonalidade_bloqueios.csv', 'text/csv')


def climate_references(figure):
    with st.expander('Precipitação e vazão normalizadas'):
        path = ASSETS / 'treistman_fig4_digitizada.csv'
        values = pd.read_csv(path)
        chart = go.Figure()
        for field, label in [('precipitacao_normalizada', 'Precipitação anual'),
                             ('vazao_normalizada', 'Vazão natural anual')]:
            chart.add_scatter(x=values.ano, y=values[field], name=label, mode='lines+markers',
                              marker={'size': 4}, hovertemplate='%{x}: ≈%{y:.2f}<extra>%{fullData.name}</extra>')
        chart.update_layout(title='Precipitação e vazão natural anuais normalizadas',
                            xaxis_title='Ano', yaxis_title='Valor normalizado (adimensional)')
        chart.update_xaxes(tickmode='array', tickvals=[1943, 1950, 1960, 1970, 1980, 1990, 2000, 2005])
        figure(chart, 'tcc_fig05', 'Treistman et al. (2015), figura 4, 1943–2005. Valores aproximados '
               'digitalizados das curvas publicadas. O artigo reporta r = 0,75 para as séries originais. '
               'Use o redesenho para acompanhar a variação, com os valores originais a consultar junto aos autores.')
        st.link_button('Abrir publicação de Treistman et al.',
                       'https://files.abrhidro.org.br/Eventos/Trabalhos/4/PAP019701.pdf')
        st.download_button('Baixar pontos digitalizados da Figura 5', path.read_bytes(), path.name, 'text/csv')
    with st.expander('Contexto oceânico · índice ONI da NOAA'):
        oni = oni_series()
        chart = go.Figure(go.Scatter(x=oni.index, y=oni, mode='lines', name='ONI', connectgaps=False))
        chart.add_hline(y=0, line_color='#98afbe')
        chart.update_layout(title='Índice Oceânico Niño (ONI)', yaxis_title='Anomalia (°C)', xaxis_title='Mês central')
        figure(chart, 'tcc_oni', 'Fonte: NOAA/CPC, cópia local da série histórica. O ONI representa uma média móvel '
               'trimestral na região Niño 3.4. Cada trimestre é posicionado no mês central.')
        st.write('A série contextualiza o ENSO. Uma associação com o clima regional depende do recorte, '
                 'da cobertura e do método. O Ridge reproduzido usa vazão e sazonalidade.')
        st.markdown(f'[Catálogo NOAA/CPC]({NOAA}) · [Arquivo original]({NOAA_DATA})')


def october_projection_verification(path, figure, table):
    st.subheader('Outubro de 2026 · estimativa M+1 e verificação')
    projection = pd.read_csv(path / 'projecoes.csv', parse_dates=['alvo', 'origem', 'emissao'])
    october = pd.Timestamp('2026-10-01')
    archived = projection.loc[projection.alvo.eq(october) & projection.horizonte.eq(1)]
    if archived.empty:
        st.info('Estimativas arquivadas de outubro indisponíveis.')
        return
    daily = ons.read('diario', directory=ons.SNAPSHOT)
    month = ons.slice_days(daily, october, october + pd.offsets.MonthEnd())
    expected = pd.date_range(october, october + pd.offsets.MonthEnd())
    actual = month.set_index(ons.STAMP).val_vazaonatural.sort_index()
    valid_days = actual[np.isfinite(actual)].index.intersection(expected)
    verified = actual.mean() if actual.index.equals(expected) and len(valid_days) == len(expected) else np.nan
    reference = archived.iloc[0]
    st.caption(f'Origem dos dados: {reference.origem:%m/%Y} (SAR). '
               f'Data de emissão arquivada: {reference.emissao:%d/%m/%Y}. '
               'Outubro já havia terminado nessa data. A estimativa é retrospectiva.')
    result = archived[['modelo', 'previsto']].rename(columns={
        'modelo': 'Método', 'previsto': 'Estimativa (m³/s)',
    }).copy()
    if pd.notna(verified):
        st.metric('Vazão natural média verificada pelo ONS', f'{verified:.2f}'.replace('.', ',') + ' m³/s')
        st.caption(f'Cobertura: {len(valid_days)}/{len(expected)} dias com vazão natural. '
                   'Média aritmética dos registros diários do reservatório SFTMAR.')
        result['Diferença: estimativa − ONS (m³/s)'] = result['Estimativa (m³/s)'] - verified
        result['Erro absoluto (m³/s)'] = result['Diferença: estimativa − ONS (m³/s)'].abs()
        chart = px.bar(result, x='Método', y='Estimativa (m³/s)', color_discrete_sequence=['#087eae'],
                       title='Outubro de 2026 · estimativas M+1 e média verificada')
        chart.add_hline(y=verified, line_dash='dash', line_color='#a63f2b',
                        annotation_text=f'ONS: {verified:.2f} m³/s'.replace('.', ','))
        figure(chart, 'october_projection_chart',
               'Acima da linha tracejada, o método superestimou a vazão. Abaixo, subestimou.')
        closest = result.loc[result['Erro absoluto (m³/s)'].idxmin(), 'Método']
        st.write(f'**{closest}** ficou mais perto da referência neste mês. Para escolher uma abordagem por '
                 'horizonte, compare também o desempenho nos 21 meses e no recorte de baixa vazão.')
    else:
        st.info(f'Média mensal não exibida. Cobertura: {len(valid_days)}/{len(expected)} dias válidos. '
                'A verificação exige exatamente um valor por dia.')
    table(result.round(2))
    st.markdown('O SAR é a fonte do treinamento e da auditoria histórica. O ONS fornece a referência '
                'externa para este mês. Esta diferença pontual fica fora do MAE dos 21 meses do backtest. '
                f'[Base hidráulica diária do ONS]({ons.SOURCES["diario"]}).')
