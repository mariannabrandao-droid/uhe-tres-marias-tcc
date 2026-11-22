"""Painel Streamlit e percurso de defesa do TCC."""
from base64 import b64encode

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import hidroclima as hydro
from figuras_tcc import oni_series
from pirapora import daily_series as pirapora_daily
from postos_defesa import FLOW_POSTS, RAIN_POSTS, describe
from informes_ana import INDEX as ANA_BOLETINS, fetch_bulletins, saved_bulletins
import operacao_ons as ons
from defluencia_diurna import THRESHOLD, analyze, hourly_intervals
from hidroclima import DATA, FLOW, ISSUE, LABELS, ROOT, SAR, unit
from analise_defesa import CLIMATE, associations, climate_series, low_runs
from mapas import climate_map, network_map
from preparar_dados import preparar_dados
from evidencia_jusante import STATION, compare, load_station_csv

def configure_page(title):
    preparar_dados()
    st.set_page_config(page_title=title, page_icon='🌊', layout='wide', initial_sidebar_state='auto')
    st.markdown("""<style>

    :root{--navy:#09233e;--navy2:#113957;--teal:#0b9a9c;--bg:#f3f7fb;--muted:#71839a;--line:#e1eaf2}
    html,body,[class*=css],.stApp{font-family:'DM Sans',sans-serif!important}
    .stApp,[data-testid=stAppViewContainer]{background:var(--bg)}
    [data-testid=stHeader]{background:transparent;height:2.4rem}
    [data-testid=stSidebar]{background:linear-gradient(180deg,#0a2744 0%,#102f4d 65%,#0b253f 100%)!important;border-right:1px solid #24415c}
    [data-testid=stSidebar] *{color:#e8f3fa!important}
    [data-testid=stSidebar] .stRadio label{padding:7px 10px;border-radius:10px;margin:1px 0;font-size:0.88rem}
    [data-testid=stSidebar] .stRadio label:has(input:checked){background:#1b506c!important;border-left:3px solid #4bd0c7}
    [data-testid=stSidebar] [data-testid=stAlert]{background:#183e58!important;border:1px solid #2c6077!important}
    [data-testid=stSidebar] hr{border-color:#35516a}
    .block-container{max-width:1500px!important;padding:1.4rem 2.6rem 5rem!important}
    h1,h2,h3,h4{font-family:'Manrope',sans-serif!important;color:#132d48!important;letter-spacing:-.03em}
    h1{font-size:1.8rem!important;font-weight:800!important;margin-bottom:1rem!important}
    h2{font-size:1.24rem!important}h3{font-size:1.03rem!important}
    .hero{display:flex;align-items:center;gap:25px;background:#fff;border:1px solid #dbe8f3;border-left:5px solid #1161a8;border-radius:18px;padding:29px 34px;color:#fff;margin-bottom:19px;box-shadow:0 12px 35px #102f4b12;position:relative;overflow:hidden}
    .hero:after{content:'';position:absolute;right:-35px;top:-90px;width:330px;height:260px;border-radius:50%;border:45px solid #ffffff0c}
    .hero h1{color:#123450!important;font-size:1.9rem!important;margin:0 0 5px!important}
    .hero p{color:#395a74;margin:0;font-size:.92rem}.hero .eyebrow{font-size:.73rem;font-weight:800;letter-spacing:.14em;color:#61d3cc;margin-bottom:10px}
    div[data-testid=stMetric]{background:#fff;border:1px solid var(--line);border-radius:14px;padding:17px 20px;box-shadow:0 5px 15px #15334d08;min-height:114px;border-top:3px solid #18a3a8}
    [data-testid=stMetricLabel]{font-size:.84rem!important;color:#60758b!important}
    [data-testid=stMetricValue]{font-size:1.75rem!important;font-weight:800!important;color:#102e49!important}
    [data-testid=stVerticalBlockBorderWrapper]{border-radius:16px!important;border-color:var(--line)!important}
    .stPlotlyChart{background:white;border-radius:16px;border:1px solid var(--line);padding:9px 12px;box-shadow:0 5px 20px #16374b09;overflow:hidden}
    [data-testid=stDataFrame]{background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden}
    [data-testid=stAlert]{border-radius:12px!important}
    .stButton>button,.stDownloadButton>button{background:#0d6e81;color:white;border:none;border-radius:10px;font-weight:700;padding:9px 18px}
    .stButton>button:hover,.stDownloadButton>button:hover{background:#0a4c66;color:white}
    [data-testid=stSelectbox], [data-testid=stMultiSelect], [data-testid=stSlider]{border-radius:10px}
    .smallhead{font-size:.72rem;font-weight:800;letter-spacing:.13em;color:#0b9298;margin-bottom:4px}
    .sectionintro{color:#6b7d90;font-size:.92rem;margin-top:-.65rem;margin-bottom:1.2rem}
    .pill{display:inline-block;background:#e1f4f4;border:1px solid #b8e4e4;color:#176d76;border-radius:20px;font-size:.74rem;padding:4px 11px;margin:0 5px 7px 0;font-weight:700}
    .footerline{margin-top:25px;padding-top:16px;border-top:1px solid #d9e5ed;color:#788a9a;font-size:.78rem}
    .stApp [data-testid='stSidebar'] [role='radiogroup'] label{transition:background .2s ease}.stApp [data-testid='stSidebar'] [role='radiogroup'] label:hover{background:#19445d!important}.stApp [data-testid='stHorizontalBlock']{align-items:stretch}.stApp [data-testid='stMetric']{height:100%}.stApp [data-testid='stDataFrame']{font-size:.86rem}.stApp .stTabs [data-baseweb='tab']{font-weight:700}.insight{background:#eff8fb;border-left:4px solid #0d9eaa;padding:13px 17px;border-radius:10px;color:#21465b;margin:12px 0}.warningbox{background:#fff6e8;border-left:4px solid #e59a31;padding:13px 17px;border-radius:10px;color:#70542b;margin:12px 0}@media(max-width:850px){.block-container{padding:1rem .8rem 3rem!important}.hero{padding:21px}.hero h1{font-size:1.45rem!important}}
    </style>""",unsafe_allow_html=True)
    logo = b64encode((ROOT / 'assets' / 'logo_uff.png').read_bytes()).decode('ascii')
    st.markdown(f'<div class="hero"><img src="data:image/png;base64,{logo}" width="72" alt="Universidade Federal Fluminense">'
                '<div><h1>UHE Três Marias</h1><p>Painel hidroclimático do Rio São Francisco</p></div></div>',
                unsafe_allow_html=True)



MONTHS = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
PAGES = (
    '00 · Capa e roteiro',
    '01 · Usina, operação e vazão mínima',
    '02 · Histórico, ZCAS e bloqueios',
    '03 · Operação diária da usina',
    '04 · Defluência diária e horária',
    '05 · Síntese e rastreabilidade',
    '06 · Conclusão',
)
SCIENCE_TOPICS = ('Postos e estações', 'Vazões e sazonalidade', 'Clima e associações', 'Previsão mensal')



ONS_SALA = ('https://www.gov.br/ana/pt-br/assuntos/monitoramento-e-eventos-criticos/'
            'eventos-criticos/apresentacoes-das-reunioes/apresentacao-ons-sala-do-rio-sao-francisco-06_05_2025.pdf')
ANA_REGRA = 'https://www.gov.br/ana/pt-br/legislacao/resolucoes/resolucoes-regulatorias/2017/2081'
MPF_ACAO = ('https://www.mpf.mp.br/o-mpf/unidades/pr-mg/noticias/'
            'mpf-ajuiza-acao-para-garantir-vazao-minima-do-rio-sao-francisco-em-tres-marias-mg')

def graph(fig,key,height=355):
 fig.update_layout(template='plotly_white',height=fig.layout.height or height,margin=dict(l=18,r=18,t=55,b=65),
  paper_bgcolor='#ffffff',plot_bgcolor='#ffffff',font=dict(family='DM Sans, Arial',color='#425d73',size=12),
  title_font=dict(family='Manrope, Arial',size=15,color='#15334d'),
  legend=dict(orientation='h',y=-.28,x=0,font=dict(size=11)),
  hovermode=fig.layout.hovermode or 'x unified',colorway=['#087eae','#12a9a0','#f3a54b','#8c70c9','#df7185'],
  xaxis=dict(showgrid=False,zeroline=False,automargin=True),yaxis=dict(gridcolor='#edf2f6',zeroline=False,automargin=True))
 st.plotly_chart(fig,width="stretch",key=key,config={'displaylogo':False,'responsive':True})


@st.cache_data
def load_history():
    return hydro.read_series(), hydro.complete_sar()


def number(value, places=1):
    if pd.isna(value):
        return '—'
    return f'{value:,.{places}f}'.translate(str.maketrans(',.', '.,'))


def month(date):
    return date.strftime('%m/%Y') if pd.notna(date) else '—'


def table(frame):
    st.dataframe(frame, width='stretch', hide_index=True)


def figure(fig, key, caption):
    graph(fig, key)
    st.caption(caption)


def time_series(frame, keys, title, key):
    chart = go.Figure()
    for name in keys:
        chart.add_scatter(x=frame.index, y=frame[name], name=LABELS[name], mode='lines',
                          connectgaps=False)
    chart.update_layout(title=title, yaxis_title=unit(keys[0]), xaxis_title='Mês')
    coverage = ' · '.join(f'{LABELS[name]}: {month(frame[name].first_valid_index())} a {month(frame[name].last_valid_index())}' for name in keys)
    figure(chart, key, coverage + '. Valores mensais completos na escala indicada. Interrupções representam ausências. '
           'Código · hidroclima.read_series → app.time_series.')


def seasonality(frame, key, chart_key):
    data = frame[key].dropna().rename('Valor').to_frame()
    data['Mês'] = [MONTHS[i - 1] for i in data.index.month]
    data['Amostra'] = data.groupby('Mês')['Valor'].transform('size')
    chart = px.box(data, hover_data=['Amostra'], x='Mês', y='Valor', category_orders={'Mês': MONTHS}, points='outliers',
                   labels={'Valor': unit(key)}, title=f'Sazonalidade · {LABELS[key]}')
    counts = data.groupby(data.index.month).size()
    chart.update_xaxes(tickvals=[MONTHS[i-1] for i in counts.index],
                       ticktext=[f'{MONTHS[i-1]}<br>n={n}' for i, n in counts.items()])
    source = ' · SAR' if key in SAR else ''
    figure(chart, chart_key, f'Período: {month(data.index.min())} a {month(data.index.max())}{source}. '
           'Cada caixa reúne o mesmo mês em anos diferentes. A linha interna é a mediana.')


def select_page(page):
    st.session_state['defense_page'] = page


def setup():
    st.sidebar.markdown('### Navegação')
    selected = st.sidebar.radio('Páginas', PAGES, key='defense_page')
    st.sidebar.caption(f'Base hidroclimática de referência · {ISSUE:%d/%m/%Y}')
    return selected


def defense_navigation(page):
    index = PAGES.index(page)
    if index == 0:
        return
    previous, following = st.columns(2)
    previous.button(f'Voltar · {PAGES[index - 1][5:]}', key='previous_page',
                    on_click=select_page, args=(PAGES[index - 1],))
    if index == 2:
        current_topic = SCIENCE_TOPICS.index(st.session_state['science_topic'])
        if current_topic < len(SCIENCE_TOPICS) - 1:
            next_topic = SCIENCE_TOPICS[current_topic + 1]
            following.button(f'Avançar · {next_topic}', key='next_topic',
                             on_click=open_science_topic, args=(next_topic,))
            return
    if index + 1 < len(PAGES):
        following.button(f'Avançar · {PAGES[index + 1][5:]}', key='next_page',
                         on_click=select_page, args=(PAGES[index + 1],))


def diagnosis_for_month(key, limit, hourly=None, daily=None):
    period = pd.Period(key, freq='M')
    hourly = ons.read('horario') if hourly is None else hourly
    daily = ons.read('diario') if daily is None else daily
    start, end = period.start_time, period.end_time.normalize()
    hour_month = ons.slice_days(hourly, start, end)
    return analyze(hour_month, ons.slice_days(daily, start, end), limit, start, end)


def downstream_evidence(hourly, days, limit, day, daily):
    st.subheader('Verificação no ponto de controle 41020002')
    st.write('Este campo responde a uma pergunta: o episódio sinalizado na saída da usina também aparece na estação '
             'de controle? Se você obtiver um CSV horário validado, o painel alinha os horários e mostra a cobertura. '
             'Sem esse arquivo, a lista do ONS serve para solicitar os registros dos dias sinalizados. '
             'A mesma hora do relógio é uma primeira triagem. A água pode levar tempo para percorrer o trecho.')
    st.caption('A série histórica do posto incluída no projeto termina em outubro de 2006. '
               f'Para o recorte de {month(days.index.min())}, carregue médias horárias da estação de uma fonte identificada.')
    source = st.text_input('Fonte da série e condição de validação', key='downstream_source',
                           placeholder='Órgão, referência da exportação e status de consistência')
    file = st.file_uploader('Importar CSV horário da estação 41020002', type='csv', key='downstream_csv')
    st.download_button('Baixar modelo de CSV', 'estacao,inicio_intervalo,vazao_m3s\n',
                       file_name='modelo_41020002.csv', mime='text/csv')
    st.caption('CSV UTF-8 separado por vírgulas. Use ponto decimal. Informe a média de cada hora '
               'pelo início do intervalo (AAAA-MM-DD HH:MM), em horário de Brasília (UTC−03). '
               'Converta previamente os registros referenciados pelo fim da hora.')
    downstream = None
    if file is not None:
        if not source.strip():
            st.warning('Identifique a fonte e a condição de validação para incluir a série na comparação.')
        else:
            try:
                downstream = load_station_csv(file)
            except (ValueError, pd.errors.ParserError) as error:
                st.error(f'CSV da estação: {error}')
    paired, summary = compare(hourly, days, limit, downstream)
    flagged = summary.loc[summary.diverge]
    complete = int(flagged.intervalos_jusante.eq(12).sum())
    st.write(f'**{len(flagged)} datas sinalizadas pelo ONS · {complete} com cobertura horária completa '
             f'na estação {STATION}.**')
    st.caption('O pareamento usa a mesma hora do relógio e serve à triagem. Uma análise de propagação '
               'exige estimar o tempo de viagem entre os pontos. A origem e a validação declaradas '
               'para arquivos importados devem ser verificadas com o órgão responsável.')
    if not flagged.empty:
        visible = flagged.reset_index()[['dia', 'media_diaria', 'minimo_diurno',
                                        'cobertura_jusante', 'minimo_disponivel_jusante',
                                        'intervalos_jusante_abaixo']]
        table(visible.rename(columns={
            'dia': 'Data', 'media_diaria': 'Média ONS (m³/s)', 'minimo_diurno': 'Mínimo diurno ONS (m³/s)',
            'cobertura_jusante': 'Cobertura 41020002', 'minimo_disponivel_jusante': 'Mínimo disponível 41020002 (m³/s)',
            'intervalos_jusante_abaixo': 'Registros disponíveis abaixo na estação'}))
    selected = paired.loc[paired.dia.eq(day)]
    if selected.vazao_41020002_m3s.notna().any():
        chart = go.Figure()
        for field, name in [('defluencia_ons_m3s', 'Defluência ONS'),
                            ('vazao_41020002_m3s', 'Estação 41020002')]:
            chart.add_scatter(x=selected.inicio.to_list(), y=selected[field].to_list(),
                              mode='lines+markers', name=name, connectgaps=False)
        chart.add_hline(y=limit, line_dash='dot')
        chart.update_layout(title=f'Confronto no dia {day:%d/%m/%Y}', yaxis_title='Vazão (m³/s)')
        figure(chart, 'downstream_comparison', f'Período: {day:%d/%m/%Y}. Fonte da estação informada pelo usuário: {source.strip()}')
    evidence = paired.loc[paired.dia.isin(flagged.index)].copy()
    evidence['media_diaria_ons_m3s'] = evidence.dia.map(summary.media_diaria)
    evidence['estacao_jusante'] = STATION
    evidence['fonte_jusante'] = source.strip() if downstream is not None else ''
    evidence['fim_intervalo'] = evidence.inicio + pd.Timedelta(hours=1)
    evidence['fuso_horario'] = 'UTC-03:00'
    st.download_button('Baixar evidências das datas sinalizadas (CSV)',
                       evidence.to_csv(index=False).encode('utf-8-sig'),
                       file_name='evidencias_ons_41020002.csv', mime='text/csv')
    context = daily.set_index('din_instante').loc[day]
    st.write(f'**Contexto operativo de {day:%d/%m/%Y} (ONS diário)**')
    table(context[['val_vazaoafluente', 'val_volumeutilcon', 'val_vazaoturbinada', 'val_vazaovertida']]
          .rename(index={'val_vazaoafluente': 'Afluência (m³/s)', 'val_volumeutilcon': 'Volume útil (%)',
                         'val_vazaoturbinada': 'Vazão turbinada (m³/s)', 'val_vazaovertida': 'Vazão vertida (m³/s)'})
          .to_frame().T.reset_index(drop=True))
    st.caption('Esses indicadores contextualizam a operação. A viabilidade de uma medida depende '
               'também das restrições operativas, regras aplicáveis e condições a jusante.')


@st.cache_data
def load_pirapora():
    return pirapora_daily()


def show_pirapora():
    st.markdown('**Pirapora Barreiro (41135000) · referência complementar a jusante.** '
                'A série diária contextualiza o rio em outro ponto. A janela disponível termina antes de outubro '
                'de 2026 e tem resolução diária.')
    data = load_pirapora()
    recent = data[data.dia.ge('2023-01-01')]
    chart = go.Figure()
    for level, label in ((1, 'Bruto'), (2, 'Consistido')):
        full = data[data.NivelConsistencia.eq(level)]
        subset = recent[recent.NivelConsistencia.eq(level)].set_index('dia').vazao_m3s.asfreq('D')
        chart.add_scatter(x=subset.index, y=subset, mode='lines', name=label, connectgaps=False)
        st.caption(f'{label} · último dia com valor: {full.dia.max():%d/%m/%Y}.')
    chart.update_layout(title='Vazão diária em Pirapora Barreiro desde 2023', yaxis_title='m³/s', xaxis_title='Dia')
    figure(chart, 'pirapora_daily', 'ANA/HidroWeb, estação 41135000. Exportação de 12/11/2026. '
           'Os níveis são exibidos separadamente. Lacunas interrompem as linhas.')
    st.download_button('Baixar CSV original de Pirapora', (ROOT / 'dados_ana/41135000_Vazoes.csv').read_bytes(),
                       '41135000_Vazoes.csv', 'text/csv')


def show_bulletins():
    st.subheader('Informes públicos de operação')
    st.write('Consulte a lista de boletins da ANA para verificar a data de referência e as condições dos reservatórios '
             'do São Francisco. Esta consulta é independente da atualização dos CSVs do ONS.')
    if st.button('Buscar boletins recentes da ANA'):
        with st.spinner('Consultando a página oficial da ANA…'):
            try:
                st.session_state['ana_bulletins'] = fetch_bulletins()
                st.session_state.pop('ana_bulletins_error', None)
            except (OSError, ValueError) as error:
                st.session_state['ana_bulletins_error'] = str(error)
    if 'ana_bulletins_error' in st.session_state:
        st.warning('A consulta ao portal da ANA falhou. Os links abaixo vêm da última lista disponível.')
        with st.expander('Detalhes da falha da ANA'):
            st.text(st.session_state['ana_bulletins_error'])
    live = 'ana_bulletins' in st.session_state
    records, checked = st.session_state['ana_bulletins'] if live else saved_bulletins()
    origin = 'Consulta nesta sessão' if live else 'Lista incluída no painel'
    checked_local = pd.Timestamp(checked).tz_convert('America/Sao_Paulo')
    st.caption(f'{origin} · {checked_local:%d/%m/%Y %H:%M} (Brasília) · Fonte: ANA.')
    for date, url in records:
        st.markdown(f'[Boletim de {date:%d/%m/%Y}]({url})')
    st.markdown(f'[Abrir o índice oficial de boletins diários]({ANA_BOLETINS})')



FIGURES = {
    1: ('Médias mensais em janelas históricas', 'Acervo Três Marias (156) · comparação descritiva das janelas da justificativa.'),
    2: ('Localização da bacia hidrográfica', 'Mapa reproduzido do TCC, com atribuição a Silva et al. (2015) no PDF.'),
    3: ('Sistema de reservatórios do São Francisco', 'Esquema reproduzido do TCC, com atribuição à ANA (2013) no PDF.'),
    4: ('Vazões médias anuais de 1931 a 2023', 'Acervo Três Marias (156) · média anual da série histórica.'),
    5: ('Precipitação e vazão anual normalizadas', 'Treistman et al. (2015) · reprodução do gráfico apresentado no TCC.'),
    6: ('Índice anual de ZCAS na região AB', 'Acervo da pesquisa · médias móveis de três e cinco anos.'),
    7: ('Sazonalidade média dos bloqueios atmosféricos', 'Acervo da pesquisa · sazonalidade de 1961 a 2023, seção 4.4.'),
    8: ('Dias de bloqueio por mês no recorte Total', 'Acervo da pesquisa · ver critérios na seção 5.6.'),
    9: ('Permanência da vazão natural mensal e posição de Q90 e Q95', 'SAR/ANA · meses completos e posição de excedência conforme seção 5.6.'),
    10: ('Barramento e estação Três Marias Jusante', 'ANA/SNIRH e cadastro HidroWeb · referência cartográfica do trecho.'),
    11: ('Defluência horária em 22 de outubro de 2026', 'ONS · SFTMAR. A janela diurna vai de 6 h a 18 h.'),
    12: ('Localização cadastral dos postos analisados', 'ANA/HidroWeb · seleção descrita na seção 5.4.2.'),
    13: ('Vazão natural mensal e meses abaixo de 150 m³/s', 'SAR/ANA · janeiro de 2020 a setembro de 2026, seção 6.1.'),
    14: ('Associação entre chuva em Andrequicé e vazão natural por defasagem', 'HidroWeb e SAR/ANA · anomalias mensais e número de pares, seção 6.2.'),
    15: ('Vazão natural de referência e estimativas M+1', 'SAR/ANA · auditoria retrospectiva de 21 meses-alvo, seção 6.3.'),
    16: ('Vazão natural de referência e estimativas M+2', 'SAR/ANA · auditoria retrospectiva de 21 meses-alvo, seção 6.3.'),
    17: ('Estimativas M+1 para outubro de 2026 e média do ONS', 'Estimativas com origem em setembro e média de 31 registros diários do ONS, seção 6.3.'),
    18: ('Afluência, defluência, vias de liberação e volume útil', 'ONS · SFTMAR, outubro de 2026, seção 6.4.'),
    19: ('Média diária e mínimo diurno em outubro de 2025 e de 2026', 'ONS · SFTMAR, dias elegíveis, patamar de 300 m³/s, seção 6.4.'),
}


def paper_figure(index):
    title, source = FIGURES[index]
    figure_number = index + 2 if index >= 13 else index
    st.markdown(f'**Figura {figure_number} do TCC · {title}**')
    with st.container(border=True):
        st.image(str(ROOT / 'assets' / 'figuras_pdf' / f'{index:02}.png'), width='stretch')
        st.caption(source)


def export(data, label, filename, index=False):
    st.download_button(label, data.to_csv(index=index).encode('utf-8-sig'), filename, 'text/csv')


@st.cache_data
def bundled_ons(kind):
    return ons.read(kind, directory=ROOT / 'dados_ons' / 'sem_atualizacoes')


def cover():
    st.title('Desenvolvimento de uma plataforma didática para análise hidroclimática da UHE Três Marias')
    st.write('**Marianna Brandão Ferreira** · Universidade Federal Fluminense · 2026')
    st.write('Orientador: Prof. Dr. Márcio Cataldi')
    st.subheader('O que a média diária revela sobre a água liberada pela usina?')
    st.write('Da localização da bacia e da seleção dos postos à comparação das vazões diária e horária. '
             'As figuras numeradas correspondem às legendas do PDF do TCC.')
    st.button('Iniciar apresentação', type='primary', on_click=select_page, args=(PAGES[1],))
    for label, summary in zip(PAGES[1:], (
        'Discussão do MPF, histórico da usina, Alto São Francisco e ponto de controle.',
        'Postos e cobertura, histórico de vazões, clima e previsão mensal.',
        'Entradas, liberações, armazenamento e estudo de caso do ONS.',
        'Comparação diária e horária e consulta exploratória a jusante.',
        'Fontes, arquivos e critérios de reprodução.',
        'Resultados por escala e contribuição para o debate.',
    )):
        left, right = st.columns([1, 1.5], vertical_alignment='center')
        left.button(label, on_click=select_page, args=(label,), width='stretch')
        right.write(summary)


def context():
    st.header('Contexto do estudo e discussão sobre vazão mínima')
    st.subheader('O pedido divulgado pelo Ministério Público Federal')
    st.write('Em fevereiro de 2026, o MPF divulgou pedido de 300 m³/s constantes entre 6 h e 18 h. '
             'O TCC usa esse patamar como cenário analítico para localizar intervalos de baixa liberação na usina.')
    st.write('A Resolução ANA nº 2.081/2017 descreve condições de operação do sistema e identifica '
             'a estação 41020002 como ponto de controle. O estudo distingue os registros da usina '
             'da vazão medida no rio a jusante.')
    st.markdown(f'[Comunicado do MPF]({MPF_ACAO}) · [Resolução ANA nº 2.081/2017]({ANA_REGRA})')
    st.subheader('Por que o reservatório foi construído')
    st.write('Implantada na década de 1960, a UHE Três Marias reuniu objetivos de geração de energia, '
             'controle de cheias e desenvolvimento regional. O TCC situa a construção da barragem '
             'no planejamento da região e nas transformações vividas pelas populações ribeirinhas.')
    st.caption('TCC · Introdução e seções 4.1 e 5.3.')
    st.subheader('A UHE Três Marias no Alto São Francisco')
    st.write('O reservatório participa da geração de energia, da regularização das vazões, do controle de cheias '
             'e do atendimento aos usos múltiplos da água. Sua posição a montante ajuda a situar as liberações '
             'no conjunto de reservatórios do São Francisco.')
    for index in (2, 3, 10):
        paper_figure(index)
        if index == 2:
            st.write('O mapa regional situa a usina em Minas Gerais e na bacia do São Francisco.')
        if index == 3:
            st.write('Em escala local, o mapa seguinte identifica o barramento e a estação de controle.')


def open_science_topic(topic):
    st.session_state['science_topic'] = topic


def science(frame, sar, defense=True):
    st.header('Dos postos ao histórico hidroclimático')
    structure = SCIENCE_TOPICS
    topic = st.radio('Etapas da página 02' if defense else 'Temas do histórico',
                     structure, horizontal=True, key='science_topic')
    if topic == structure[0]:
        st.write('As séries foram selecionadas pela posição, pela variável medida, pela cobertura e '
                 'pela sobreposição temporal. Barramento e Porto Mesquita contextualizam a chuva histórica. '
                 'Andrequicé permite a comparação com a vazão natural recente. Indaiá é referência de tributário '
                 'e Três Marias Jusante é o posto de controle histórico.')
        paper_figure(12)
        records = describe(frame, {**FLOW_POSTS, **RAIN_POSTS})
        table(records.assign(Início=records.Início.map(month), Fim=records.Fim.map(month)))
        st.caption('Cadastro de estações e séries mensais organizadas · HidroWeb/ANA, seção 5.4.2.')
        with st.expander('Explorar o mapa dos postos selecionados'):
            figure(network_map(records['Código ANA'].tolist()), 'station_map',
                   'Coordenadas cadastrais ANA/HidroWeb, seção 5.4.2.')
        with st.expander('Conferir séries mensais selecionadas'):
            groups = {'Vazões dos postos': list(FLOW_POSTS), 'Chuva nos postos': list(RAIN_POSTS)}
            selected = st.selectbox('Grupo', groups)
            keys = groups[selected]
            time_series(frame, keys, selected, 'station_series')
            export(frame[keys].dropna(how='all'), 'Baixar séries selecionadas', 'postos_mensais.csv', index=True)
    elif topic == structure[1]:
        for index in (1, 4, 9, 13):
            paper_figure(index)
            if index == 4:
                st.write('O acervo histórico descreve a variação ao longo de décadas. As análises de permanência '
                         'e sequências usam a vazão natural mensal da série SAR.')
        series = sar[FLOW[0]]
        limit = st.number_input('Patamar descritivo da vazão natural mensal (m³/s)', min_value=0., value=150.)
        runs = low_runs(series, limit)
        st.write(f'{series.lt(limit).sum()} de {series.count()} meses abaixo do patamar. '
                 'Meses ausentes ou iguais ao patamar interrompem a sequência.')
        st.markdown('**Tabela 1 do TCC · Sequências de baixa vazão**' if limit == 150
                    else '**Sequências no patamar selecionado**')
        if len(runs):
            table(runs.assign(Início=runs.Início.map(month), Fim=runs.Fim.map(month)).round(2))
        else:
            st.info('Nenhuma sequência abaixo desse patamar.')
        with st.expander('Explorar a curva de permanência e a sazonalidade'):
            curve = hydro.permanence(series)
            chart = go.Figure(go.Scatter(x=curve.excedencia, y=curve.vazao, mode='lines+markers', name='SAR'))
            for exceedance in (90, 95):
                quantile = hydro.reference_quantile(curve, exceedance)
                if pd.notna(quantile):
                    chart.add_vline(x=exceedance, line_dash='dot')
                    chart.add_scatter(x=[exceedance], y=[quantile], mode='markers',
                                      name=f'Q{exceedance} = {number(quantile, 2)} m³/s')
            chart.update_layout(title='Permanência da vazão natural mensal',
                                xaxis_title='Frequência de excedência (%)', yaxis_title='Vazão (m³/s)')
            figure(chart, 'sar_permanence', 'ANA/SAR, meses completos. Posição de Weibull e interpolação linear, seções 5.6 e 6.1.')
            export(curve, 'Baixar curva de permanência', 'permanencia_sar.csv')
            seasonality(sar, FLOW[0], 'sar_season')
            export(sar[[FLOW[0]]].dropna(), 'Baixar vazão natural mensal', 'sar_vazao_natural.csv', index=True)
    elif topic == structure[2]:
        st.write('ZCAS, bloqueios e ONI contextualizam as séries. A associação destacada no estudo '
                 'usa anomalias mensais da chuva de Andrequicé e da vazão natural do SAR.')
        for index in (5, 6, 7, 8, 14):
            paper_figure(index)
        st.write('A maior associação entre as defasagens testadas ocorreu a dois meses '
                 '(r = 0,566, com 76 pares). A leitura se aplica à janela e ao posto analisados.')
        with st.expander('Consultar as defasagens e o contexto climático'):
            st.caption('Sensibilidade por retirada de um ano hidrológico (novembro a outubro), classificado pelo mês da variável-resposta. A faixa mostra variação amostral e a correlação expressa associação, seção 5.6.')
            mode = st.radio('Séries para a correlação', ('Anomalias mensais', 'Valores originais'),
                            horizontal=True, key='correlation_mode')
            anomalies = mode == 'Anomalias mensais'
            result = associations(frame, ['chuva_andrequice_mm'], FLOW[0],
                                  anomalies=anomalies, lags=range(4))
            table(result.round(3))
            export(result, 'Baixar resultados por defasagem', 'andrequice_defasagens.csv')
            climate, _ = climate_series()
            targets = {'Chuva no Barramento': 'chuva_barramento_mm', 'Vazão natural SAR': FLOW[0]}
            target = targets[st.selectbox('Variável-resposta dos índices climáticos', targets)]
            lag = st.selectbox('Defasagem dos índices (meses)', range(4))
            climate_pairs = frame[[target]].join(climate, how='outer')
            climate_result = associations(climate_pairs, CLIMATE, target, anomalies=anomalies, lags=[lag])
            st.caption('Os recortes usam os mesmos meses válidos em cada comparação (ANA/HidroWeb, SAR e acervo climático, seções 5.6 e 6.2).')
            table(climate_result.round(3))
            export(climate_result, 'Baixar associações climáticas', 'associacoes_climaticas.csv')
            figure(climate_map('ZCAS'), 'climate_map',
                   'Recortes esquemáticos conforme Cataldi et al. (2025), seção 4.4.')
            oni = oni_series()
            chart = go.Figure(go.Scatter(x=oni.index, y=oni, mode='lines', name='ONI'))
            chart.update_layout(title='Índice Oceânico Niño', yaxis_title='Anomalia (°C)', xaxis_title='Mês central')
            figure(chart, 'oni', 'NOAA/CPC · cópia local. Informação de contexto climático.')
    else:
        st.caption('Experimento acadêmico desenvolvido pela autora, seção 5.7. As previsões oficiais do ONS têm fonte e protocolo próprios.')
        st.write('A climatologia apresentou o menor erro médio global em M+1 e M+2. '
                 'Nos quatro meses abaixo de 150 m³/s, a persistência teve o menor erro em M+1.')
        paper_figure(15)
        st.write('M+1 estima o primeiro mês após a origem. Em M+2, a estimativa tem dois meses de antecedência.')
        paper_figure(16)
        with st.expander('Método e limites da previsão'):
            st.write('A persistência repete a vazão na origem. A climatologia usa a média histórica do mês-alvo. '
                     'O Ridge usa vazões na origem e 1, 2, 3, 6 e 12 meses antes, além de seno e cosseno do mês-alvo. '
                     'O treino expansivo considera alvos anteriores à origem e padroniza os atributos a cada rodada.')
            st.write('São 21 meses-alvo por horizonte na auditoria e quatro casos abaixo de 150 m³/s. A checagem '
                     'de outubro de 2026 usa uma referência ONS separada do backtest SAR.')
        forecasts = ROOT / 'historico_desenvolvimento' / 'resultados_entrega'
        metrics = pd.read_csv(forecasts / 'metricas.csv').query("etapa == 'Auditoria' and horizonte in (1, 2)")
        metrics = metrics.pivot(index=['horizonte', 'recorte', 'n'], columns='modelo', values='MAE')
        metrics = metrics.reset_index().rename(columns={'horizonte': 'Horizonte', 'recorte': 'Recorte', 'n': 'Meses'})
        order = ('Todos', 'Seca (mai–out)', 'Baixa (<150 m³/s)')
        metrics['Recorte'] = pd.Categorical(metrics.Recorte, categories=order, ordered=True)
        metrics = metrics.sort_values(['Horizonte', 'Recorte']).reset_index(drop=True)
        metrics['Horizonte'] = metrics.Horizonte.map(lambda value: f'M+{value}')
        st.markdown('**Tabela 2 do TCC · Erro absoluto médio (m³/s)**')
        table(metrics[['Recorte', 'Horizonte', 'Meses', 'Persistência', 'Climatologia', 'Ridge']].round(2))
        export(metrics, 'Baixar erros da auditoria', 'auditoria_mensal.csv')
        paper_figure(17)
        st.write('Outubro de 2026 é uma checagem complementar com referência do ONS. '
                 'A persistência teve a menor diferença absoluta nesse mês, de 49,39 m³/s.')


def operations():
    st.header('Operação diária da usina')
    st.write('A afluência descreve o que chega ao reservatório. A defluência descreve o que é liberado. '
             'As vazões turbinada e vertida mostram como se deu a liberação.')
    paper_figure(18)
    st.write('Em outubro de 2026, a defluência média superou a afluência média e o volume útil '
             'passou de 77,10% a 69,74%. A evolução é compatível com o uso de parte da água armazenada.')
    daily = bundled_ons('diario')
    start, end = pd.Timestamp('2026-10-01'), pd.Timestamp('2026-10-31')
    records = ons.slice_days(daily, start, end).set_index(ons.STAMP)
    generation = ons.day_mean_generation(bundled_ons('geracao'))
    records = records.join(generation)
    with st.expander('Consultar registros diários e geração'):
        table(records.reset_index())
        st.caption('ONS · SFTMAR (hidráulica) e MGTMAR (geração). Geração média em MW para dias com 24 valores válidos.')
        export(records, 'Baixar operação diária de outubro de 2026', 'operacao_outubro_2026.csv', index=True)
    st.subheader('Estudo documental · previsão divulgada pelo ONS')
    reference = pd.date_range('2025-05-05', '2025-06-30')
    observed = daily.set_index(ons.STAMP).val_vazaonatural.reindex(reference)
    if observed.count() == len(reference):
        cols = st.columns(3)
        mean = observed.mean()
        cols[0].metric('Média prevista', '192 m³/s')
        cols[1].metric('Média nos 57 registros', f'{number(mean, 2)} m³/s')
        cols[2].metric('Registrada menos prevista', f'{number(mean - 192, 2)} m³/s')
    st.caption('Janela de 05/05 a 30/06/2025. Comparação entre médias conforme a seção 6.3.')
    st.link_button('Consultar publicação do ONS · slide 15', ONS_SALA + '#page=15')
    with st.expander('Consultar boletins e informes da ANA'):
        show_bulletins()
    with st.expander('Consultar arquivos públicos do ONS'):
        st.markdown(' · '.join(f'[{label}]({ons.SOURCES[key]})' for key, label in (
            ('diario', 'Hidráulica diária'), ('horario', 'Hidráulica horária'), ('geracao', 'Geração horária'),
        )))
        st.caption('A consulta às fontes é complementar. Os gráficos e as tabelas do percurso usam os recortes arquivados do TCC.')


def hourly_view(hourly, day, avg):
    records = hourly_intervals(hourly)
    records = records.loc[records.dia.eq(day)]
    starts = records.inicio.dt.hour
    daytime = starts.between(6, 17)
    below = daytime & records.val_vazaodefluente.lt(THRESHOLD)
    bars = go.Figure(go.Bar(x=starts, y=records.val_vazaodefluente,
                            marker_color=np.where(below, '#f19042', '#097ea9'), name='Defluência horária'))
    bars.add_vrect(x0=5.5, x1=17.5, fillcolor='#d9eef3', opacity=.4, line_width=0, layer='below')
    bars.add_hline(y=THRESHOLD, line_dash='dash', line_color='#b87524', annotation_text='300 m³/s')
    if pd.notna(avg):
        bars.add_hline(y=avg, line_color='#215776', annotation_text=f'Média diária: {number(avg, 0)} m³/s')
    bars.update_layout(title=f'Defluência de {day:%d/%m/%Y}', xaxis_title='Início do intervalo (hora de Brasília)',
                       yaxis_title='Vazão (m³/s)')
    figure(bars, 'selected_day', 'ONS · SFTMAR. Intervalos diurnos abaixo de 300 m³/s em laranja.')


def scenarios():
    st.header('Vazão liberada · da média diária ao intervalo horário')
    st.write('O diagnóstico sinaliza dias com média diária igual ou superior a 300 m³/s '
             'e ao menos uma hora abaixo desse valor entre 6 h e 18 h. '
             'Cada dia elegível tem média oficial e os 12 registros da janela.')
    st.caption('A contagem descreve diferenças entre escalas temporais. A avaliação de conformidade depende da regra aplicável e de evidências consistidas no ponto de controle, conforme as seções 5.8 e 6.5.')
    daily, hourly = bundled_ons('diario'), bundled_ons('horario')
    months = ('2025-10', '2026-10')
    readings = {key: diagnosis_for_month(key, THRESHOLD, hourly, daily) for key in months}
    st.markdown('**Tabela 3 do TCC · Comparação do diagnóstico**')
    indicators = {}
    for key, (_, summary) in readings.items():
        eligible = int(summary.elegivel.sum())
        flagged = int(summary.diverge.sum())
        indicators[month(pd.Period(key).start_time)] = [
            eligible, int(summary.horas_abaixo.gt(0).sum()), int(summary.horas_abaixo.sum()),
            flagged, round(100 * flagged / eligible, 1) if eligible else np.nan,
        ]
    indicators = pd.DataFrame(indicators, index=['Dias elegíveis', 'Dias com pelo menos uma hora abaixo',
        'Horas abaixo nos dias elegíveis', 'Dias com divergência entre escalas', 'Percentual sinalizado (%)'])
    table(indicators.rename_axis('Indicador').reset_index())
    paper_figure(19)
    paper_figure(11)
    st.write('Em 22/10/2026, a média diária foi de 450 m³/s. Houve cinco horas diurnas consecutivas '
             'abaixo de 300 m³/s, com mínimo de 164 m³/s entre 13 h e 14 h.')
    key = st.selectbox('Mês do diagnóstico', months, index=1, format_func=lambda x: month(pd.Period(x).start_time))
    intervals, summary = readings[key]
    days = summary.index[summary.elegivel]
    if days.empty:
        st.info('Nenhum dia com cobertura completa neste mês.')
        return
    example = pd.Timestamp('2026-10-22')
    default = example if key == '2026-10' and example in days else days[0]
    day = st.selectbox('Dia elegível para detalhar', list(days), index=days.get_loc(default),
                       format_func=lambda d: d.strftime('%d/%m/%Y'), key=f'day_{key}')
    hourly_view(hourly, day, summary.loc[day, 'media_diaria'])
    export(summary, 'Baixar diagnóstico diário', f'diagnostico_{key}.csv', index=True)
    with st.expander('Comparação exploratória com a estação 41020002'):
        downstream_evidence(intervals, summary, THRESHOLD, day, daily)


def synthesis():
    st.header('Fontes, cobertura e rastreabilidade')
    table(pd.DataFrame([
        ('ANA/HidroWeb', 'Cadastro, chuva e vazão observada', '5.4–5.5'),
        ('SAR/ANA', 'Vazão natural mensal, permanência e auditoria', '5.6–5.7, 6.1 e 6.3'),
        ('Acervo e NOAA/CPC', 'Séries históricas e contexto hidroclimático', '5.6 e 6.2'),
        ('ONS', 'Operação, geração e defluência diária e horária', '5.8 e 6.4'),
        ('ANA/HidroWeb', 'Estação 41020002 e referência de Pirapora Barreiro', '6.5'),
    ], columns=['Fonte', 'Uso no painel', 'Seções do TCC']))
    with st.expander('Inventário ANA e cobertura das séries'):
        for path in (DATA / '01_decisao_45_estacoes.csv', ROOT / 'docs' / 'inventario_series.csv'):
            records = pd.read_csv(path, sep=';', dtype={'codigo': str})
            table(records)
            st.download_button(f'Baixar {path.name}', path.read_bytes(), path.name, 'text/csv')
    with st.expander('Vazão diária em Pirapora Barreiro'):
        show_pirapora()
    path = ROOT / 'revisao' / 'CORRESPONDENCIA_TCC.md'
    st.download_button('Baixar correspondência com o TCC', path.read_bytes(), path.name, 'text/markdown')


def conclusion():
    st.header('Conclusão')
    st.write('A plataforma permite consultar a disponibilidade hídrica mensal, descrever a operação diária '
             'e localizar horários de menor liberação da usina com os dados do ONS.')
    st.markdown('**Quadro 4 do TCC · Síntese dos resultados**')
    table(pd.DataFrame([
        ('Histórico', 'Cinco meses consecutivos abaixo de 150 m³/s entre junho e outubro de 2024.'),
        ('Associações', 'Chuva de Andrequicé e vazão natural: r = 0,566 com defasagem de dois meses.'),
        ('Previsão mensal', 'Climatologia com menor erro global. Persistência com menor erro em M+1 nos quatro meses de baixa vazão.'),
        ('Operação diária', 'Em outubro de 2026 o volume útil diminuiu de 77,10% para 69,74%.'),
        ('Diagnóstico horário', 'Divergência entre escalas em 29 de 30 dias elegíveis em outubro de 2025 e 8 de 31 em outubro de 2026.'),
    ], columns=['Etapa', 'Resultado']))
    st.write('A contribuição da plataforma é reunir séries e métodos rastreáveis. O experimento de previsão tem 21 meses-alvo por horizonte e apenas quatro meses de baixa vazão. A avaliação a jusante requer série horária consistida e uma estimativa de tempo de viagem.')
    st.info('As datas e horas da descarga registrada na usina orientam o acompanhamento no trecho a jusante. '
            'A estação 41020002 identifica o ponto de controle discutido no TCC.')



def main():
    configure_page('Três Marias | Defesa do TCC')
    page = setup()
    if page == PAGES[0]:
        cover()
    elif page == PAGES[1]:
        context()
    elif page == PAGES[2]:
        frame, sar = load_history()
        science(frame, sar)
    elif page == PAGES[3]:
        operations()
    elif page == PAGES[4]:
        scenarios()
    elif page == PAGES[5]:
        synthesis()
    else:
        conclusion()
    defense_navigation(page)
    st.caption('Marianna Brandão Ferreira · Universidade Federal Fluminense')


if __name__ == '__main__':
    main()
