"""Dashboard TCC Três Marias V2. Inicie com: python -m streamlit run app_tres_marias_v2.py"""
from pathlib import Path
import io
import numpy as np
import json
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'resultados_v2';PROF=OUT/'professor_recalculado'
st.set_page_config(page_title='Três Marias | Pesquisa acadêmica V2.2',layout='wide',initial_sidebar_state='collapsed')
st.markdown('''<style>
:root{--uff:#004f9f;--uff-dark:#00366c;--bg:#f5f7fa}
.stApp{background:#f7f9fc;color:#23334a}
.block-container{padding-top:1.25rem;max-width:1440px;padding-bottom:3rem}
[data-testid="stHeader"]{background:transparent}
h1,h2,h3{color:#123c68;letter-spacing:-.025em}
h1{font-size:2rem!important}h2{font-size:1.45rem!important}h3{font-size:1.18rem!important}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:12px;border-bottom:1px solid #dbe4ef;flex-wrap:wrap}
button[data-baseweb="tab"]{font-weight:600;color:#375b7f;padding:10px 12px}
button[data-baseweb="tab"][aria-selected="true"]{color:#004f9f;border-bottom:3px solid #004f9f}
[data-testid="stMetric"]{background:white;padding:18px;border:1px solid #e1e9f2;border-radius:10px;box-shadow:0 3px 12px #00366c0a}
[data-testid="stMetricValue"]{color:#004f9f;font-size:1.75rem}
[data-testid="stDataFrame"], [data-testid="stPlotlyChart"]{background:white;border-radius:10px;padding:6px}
[data-testid="stAlert"]{border-radius:9px}
.uff-banner{background:linear-gradient(110deg,#004f9f,#00366c);color:white;padding:24px 30px;border-radius:12px;margin:0 0 24px}
.uff-banner h1{color:white!important;margin:5px 0;font-size:1.9rem!important}
.uff-banner p{color:#e6f2ff;margin:0}
.uff-eyebrow{font-size:.78rem;letter-spacing:.12em;font-weight:700;color:#c8e6ff}
.uff-note{background:#edf4fc;border-left:4px solid #004f9f;padding:12px 16px;border-radius:5px;color:#244766;margin:12px 0}
.uff-footer{border-top:1px solid #d9e3ef;margin-top:32px;padding-top:16px;color:#59708b;font-size:.85rem}
</style>''',unsafe_allow_html=True)

st.markdown('''<div class="uff-banner"><div class="uff-eyebrow">PROJETO ACADÊMICO INDEPENDENTE · ENGENHARIA DE RECURSOS HÍDRICOS</div><h1>UHE Três Marias | Observatório hidrológico</h1><p>Histórico, disponibilidade hídrica, diagnóstico climático e previsão mensal M+1 · Versão 2.2</p></div>''',unsafe_allow_html=True)
st.caption('Projeto acadêmico independente, inspirado na identidade visual da UFF. Não é uma página oficial da universidade. Dados e previsões não devem orientar decisões operacionais.')
if not (OUT/'ana_mensal.csv').exists():st.error('Execute: python 02_preparar_ana.py');st.stop()
ana=pd.read_csv(OUT/'ana_mensal.csv',parse_dates=['data']).sort_values('data')
abas=st.tabs(['Panorama ANA','Histórico e operação','Vazões mínimas','Modelo M+1','Análises climáticas','Discussão do TCC','Metodologia e dados'])
with abas[0]:
 st.subheader('Situação recente da UHE Três Marias')
 ultimo=ana.iloc[-1];ultimo_completo=ana.loc[ana.mes_completo.astype(str).str.lower().eq('true')].iloc[-1]
 st.info(f'Último mês completo: {ultimo_completo.data:%m/%Y}. Mês parcial disponível: {ultimo.data:%m/%Y} ({int(ultimo.dias_registrados)} de {int(ultimo.dias_mes)} dias).')
 a,b,c,d=st.columns(4)
 a.metric('Vazão natural média',f'{ultimo_completo.vazao_natural_m3s:,.1f} m³/s')
 b.metric('Afluência média',f'{ultimo_completo.afluencia_m3s:,.1f} m³/s')
 c.metric('Defluência média',f'{ultimo_completo.defluencia_m3s:,.1f} m³/s')
 d.metric('Volume útil médio',f'{ultimo_completo.volume_util_pct:,.1f}%')
 st.caption('Indicadores referentes ao último mês completo, não ao último dia. Valores diários e mensais não são intercambiáveis.')
with abas[1]:
 st.subheader('Séries mensais ANA (2020–2026)')
 nomes={'vazao_natural_m3s':'Vazão natural (m³/s)','afluencia_m3s':'Afluência (m³/s)','defluencia_m3s':'Defluência (m³/s)','volume_util_pct':'Volume útil (%)','cota_m':'Cota (m)','vertida_m3s':'Vazão vertida (m³/s)','turbinada_m3s':'Vazão turbinada (m³/s)'}
 escolha=st.multiselect('Variáveis',list(nomes),default=['vazao_natural_m3s','afluencia_m3s','defluencia_m3s'],format_func=lambda x:nomes[x])
 so_completos=st.checkbox('Mostrar somente meses completos',value=True)
 rec=ana.loc[ana.mes_completo.astype(str).str.lower().eq('true')] if so_completos else ana
 if escolha:
  longo=rec[['data']+escolha].melt(id_vars='data',var_name='variavel',value_name='valor');longo['variavel']=longo['variavel'].map(nomes)
  st.plotly_chart(px.line(longo,x='data',y='valor',color='variavel',title='Evolução mensal'),use_container_width=True)
  st.caption('Para comparar variáveis com unidades diferentes, selecione uma variável por vez.')
 st.dataframe(rec.tail(18).sort_values('data',ascending=False),hide_index=True,use_container_width=True)

with abas[2]:
 st.subheader('Disponibilidade hídrica e regime de vazões mínimas')
 st.markdown('<div class="uff-note">Os indicadores abaixo caracterizam a série mensal ANA (2020–2026). <b>Q90 e Q95 mensais não representam, por si só, vazão ecológica, vazão mínima defluente autorizada ou limite operacional.</b></div>',unsafe_allow_html=True)
 base=ana.loc[ana['mes_completo'].astype(str).str.lower().eq('true')].copy()
 fonte=st.radio('Série utilizada na análise',['Vazão natural','Afluência','Defluência'],horizontal=True)
 col={'Vazão natural':'vazao_natural_m3s','Afluência':'afluencia_m3s','Defluência':'defluencia_m3s'}[fonte]
 serie=base[['data',col]].dropna().sort_values('data').copy()
 serie=serie.loc[serie[col]>=0]
 if len(serie)<12: st.warning('Dados mensais insuficientes para caracterizar a permanência.')
 else:
  v=serie[col].to_numpy(dtype=float)
  q90=float(pd.Series(v).quantile(.10));q95=float(pd.Series(v).quantile(.05))
  k1,k2,k3,k4=st.columns(4)
  k1.metric('Q90 mensal (excedência)',f'{q90:,.1f} m³/s')
  k2.metric('Q95 mensal (excedência)',f'{q95:,.1f} m³/s')
  k3.metric('Menor média mensal',f'{v.min():,.1f} m³/s')
  k4.metric('Meses válidos',f'{len(v)}')
  st.caption('Q90: vazão igualada ou superada em aproximadamente 90% dos meses da amostra; Q95: em aproximadamente 95%. Estimativas empíricas por quantis (10% e 5%) da série mensal, não de vazões diárias.')
  ordenado=sorted(v,reverse=True)
  permanencia=pd.DataFrame({'Permanência (%)':[100*i/(len(ordenado)+1) for i in range(1,len(ordenado)+1)],'Vazão (m³/s)':ordenado})
  graf=px.line(permanencia,x='Permanência (%)',y='Vazão (m³/s)',title=f'Curva de permanência mensal · {fonte}',template='plotly_white')
  graf.add_hline(y=q90,line_dash='dash',line_color='#007f9e',annotation_text='Q90')
  graf.add_hline(y=q95,line_dash='dot',line_color='#c47b18',annotation_text='Q95')
  graf.update_traces(line_color='#004f9f',line_width=3)
  st.plotly_chart(graf,use_container_width=True)
  zoom=permanencia.loc[permanencia['Permanência (%)']>=70].copy()
  gz=px.line(zoom,x='Permanência (%)',y='Vazão (m³/s)',title='Ampliação da cauda seca · permanência ≥ 70%',template='plotly_white')
  gz.add_hline(y=q90,line_dash='dash',line_color='#007f9e',annotation_text='Q90 mensal')
  gz.add_hline(y=q95,line_dash='dot',line_color='#c47b18',annotation_text='Q95 mensal')
  gz.update_traces(line_color='#004f9f',line_width=3)
  st.plotly_chart(gz,use_container_width=True)

  x,y=st.columns(2)
  with x:
   temp=serie.copy();temp['Mês']=temp.data.dt.month
   clim=temp.groupby('Mês')[col].agg(['mean','min','count']).reset_index()
   g=px.bar(clim,x='Mês',y='mean',title='Sazonalidade · média de cada mês',labels={'mean':'Vazão média (m³/s)'},template='plotly_white')
   g.update_traces(marker_color='#004f9f');st.plotly_chart(g,use_container_width=True)
  with y:
   serie2=serie.copy();serie2['Ano']=serie2.data.dt.year
   mins=serie2.loc[serie2.groupby('Ano')[col].idxmin()].sort_values('Ano')
   g=px.line(mins,x='Ano',y=col,markers=True,title='Menor média mensal em cada ano',labels={col:'Vazão (m³/s)'},template='plotly_white')
   g.update_traces(line_color='#007f9e',line_width=3);st.plotly_chart(g,use_container_width=True)
  st.markdown('#### Meses com menores vazões')
  tabela=serie.nsmallest(min(12,len(serie)),col).copy()
  tabela['Mês']=tabela.data.dt.strftime('%m/%Y')
  st.dataframe(tabela[['Mês',col]].rename(columns={col:'Vazão média mensal (m³/s)'}),hide_index=True,use_container_width=True)
  st.markdown('#### Investigação exploratória de um valor de referência')
  st.caption('Este campo serve apenas para contar ocorrências históricas; não declara conformidade regulatória nem permite decidir a defluência mínima.')
  ref=st.number_input('Valor de referência para análise exploratória (m³/s)',min_value=0.0,value=150.0,step=10.0)
  abaixo=int((serie[col]<ref).sum());frac=100*abaixo/len(serie)
  st.write(f'Na série **{fonte.lower()}**, **{abaixo} de {len(serie)} meses ({frac:.1f}%)** apresentaram média mensal inferior a **{ref:,.1f} m³/s**.')
  if fonte!='Defluência':st.info('Esta é uma série de disponibilidade/entrada, não a vazão liberada a jusante. Compará-la com um valor de referência não indica violação de limite de defluência.')
  else:st.info('Médias mensais não identificam descumprimentos em escala diária ou horária. É necessário verificar a regra aplicável e os dados operacionais na resolução temporal exigida.')
 st.markdown('#### Permanência diária — escala adequada à avaliação de eventos curtos')
 diario=pd.read_csv(OUT/'ana_diario.csv',parse_dates=['data'])
 diario=diario.loc[diario['data']<=ana.loc[ana['mes_completo'].astype(str).str.lower().eq('true'),'data'].max()+pd.offsets.MonthEnd(0)].copy()
 vd=pd.to_numeric(diario[col],errors='coerce').dropna()
 vd=vd.loc[vd>=0]
 if len(vd):
  d90=float(vd.quantile(.10));d95=float(vd.quantile(.05))
  u,v,w=st.columns(3)
  u.metric('Q90 diária (amostra ANA)',f'{d90:,.1f} m³/s')
  v.metric('Q95 diária (amostra ANA)',f'{d95:,.1f} m³/s')
  w.metric('Dias válidos',f'{len(vd):,}')
  st.caption('Q90/Q95 diárias calculadas sobre observações diárias de 2020 até o último mês completo; método empírico por quantis de 10% e 5%. Não equivalem à Q7,10 nem a limites autorizados.')
  if fonte=='Defluência':
   dias_abaixo=int((vd<ref).sum())
   st.write(f'Na defluência diária, {dias_abaixo} de {len(vd)} dias ({100*dias_abaixo/len(vd):.1f}%) tiveram valor inferior ao referencial exploratório de {ref:,.1f} m³/s; **não é uma avaliação de conformidade**.')
  else:st.caption('Para interpretar condições a jusante, selecione Defluência. A vazão natural não representa diretamente a descarga operada.')
 st.markdown('#### Questões que ainda precisam de validação técnica')
 st.write('Para discutir uma revisão de vazão mínima operativa: confirmar a regra vigente e seus condicionantes; examinar demandas e usos a jusante, requisitos ambientais, níveis e armazenamento do reservatório; distinguir afluência, vazão natural e defluência; e avaliar períodos secos com resolução temporal adequada.')

with abas[3]:
 st.subheader('Previsão experimental da vazão natural média do próximo mês')
 if not (OUT/'metricas.csv').exists():st.warning('Execute: python 03_modelagem_mensal_v2.py')
 else:
  met=pd.read_csv(OUT/'metricas.csv');st.dataframe(met,hide_index=True,use_container_width=True)
  pred=pd.read_csv(OUT/'previsoes_teste.csv',parse_dates=['data_prevista'])
  longo=pred.melt(id_vars='data_prevista',value_vars=['observado','Persistencia','Autorregressivo'],var_name='Série',value_name='Vazão natural (m³/s)')
  st.plotly_chart(px.line(longo,x='data_prevista',y='Vazão natural (m³/s)',color='Série',markers=True,title='Teste cronológico 2025–2026: observado × previsto'),use_container_width=True)
  info=json.loads((OUT/'ultima_previsao.json').read_text(encoding='utf-8'))
  st.metric(f"Previsão M+1 para {pd.Timestamp(info['mes_previsto']):%m/%Y}",f"{info['previsao_m3s']:,.2f} m³/s")
  st.warning(info['aviso'])
  st.markdown('#### Desempenho nos meses de baixa vazão')
  df=pred.copy();df['erro_m3s']=df['Autorregressivo']-df['observado'];df['erro_absoluto_m3s']=df['erro_m3s'].abs()
  limite=float(df['observado'].quantile(.25))
  baixos=df.loc[df['observado']<=limite].copy()
  m1,m2,m3=st.columns(3)
  m1.metric('Limite do quartil inferior',f'{limite:.1f} m³/s')
  m2.metric('MAE em meses secos',f'{baixos.erro_absoluto_m3s.mean():.1f} m³/s')
  m3.metric('Meses secos superestimados',f'{int((baixos.erro_m3s>0).sum())} de {len(baixos)}')
  baixos['Mês']=baixos.data_prevista.dt.strftime('%m/%Y')
  st.dataframe(baixos[['Mês','observado','Autorregressivo','erro_m3s','erro_absoluto_m3s']].rename(columns={'observado':'Observado (m³/s)','Autorregressivo':'Previsto (m³/s)','erro_m3s':'Viés pontual (m³/s)','erro_absoluto_m3s':'Erro absoluto (m³/s)'}).round(2),hide_index=True,use_container_width=True)
  st.caption('Meses secos definidos apenas como o quartil inferior das 21 observações do teste, não como evento hidrológico oficialmente classificado. Valores previstos acima do observado indicam superestimação.')
  st.download_button('Baixar previsões do teste (CSV)',pred.to_csv(index=False).encode('utf-8-sig'),file_name='previsoes_teste_v22.csv',mime='text/csv')
  st.markdown('**Interpretação:** o NSE avalia a qualidade no período de teste; valores maiores indicam melhor ajuste em relação à média observada. O MAE e RMSE são erros em m³/s. Persistência é a referência simples: usar a vazão do mês anterior como previsão.')
with abas[4]:
 st.subheader('Diagnóstico climático e estatístico · resultados rastreáveis')
 st.info('Os resultados deste painel foram produzidos em processamento anterior com a base histórica 1931–2023. Não equivalem à execução literal do notebook original do professor. O modelo M+1 é independente e utiliza exclusivamente ANA 2020–2026.')
 orig={'1974–1993 · precipitação, ZCAS, bloqueios e vazão':'A_quatro_familias_1974_1993','1961–2023 · ZCAS, bloqueios e vazão':'B_tres_familias_periodo_longo'}
 selecao=st.selectbox('Período e conjunto de variáveis',list(orig))
 pasta=OUT/'professor_arquivo_v2'/orig[selecao]
 if not pasta.exists():st.error('Arquivos de análises ausentes; confirme a pasta resultados_v2/professor_arquivo_v2.')
 else:
  arquivos=sorted(pasta.glob('*'))
  with st.expander('Cobertura, variáveis e ressalvas',expanded=True):
   st.write('O período indicado é o intervalo da análise; o número de meses efetivamente utilizado depende de dados completos em cada procedimento. Correlações não demonstram causalidade. PCA é diagnóstico exploratório, não modelo preditivo.')
   st.write('A PCA desses resultados anteriores inclui vazão. **A PCA original de seis variáveis climáticas, sem vazão, é apresentada separadamente abaixo quando disponível no conjunto de resultados do professor.** Não atribuir equivalência entre metodologias.')
  secoes=[('Estatística descritiva','01_estatisticas_descritivas.csv'),('Correlação de Pearson','02_correlacao.png'),('Distâncias e agrupamento','03_dendrograma.png'),('Componentes principais','04_pca_variancia.png'),('Séries históricas','05_serie_'),('Histogramas','06_histograma_'),('Decomposição sazonal','07_decomposicao_'),('Correlações com defasagem','08_correlacao_defasagens_COMPLEMENTAR.csv')]
  for titulo,padrao in secoes:
   st.markdown(f'#### {titulo}')
   selecionados=sorted(pasta.glob(padrao+'*.png')) if padrao.endswith('_') else [pasta/padrao]
   for arq in selecionados:
    if not arq.exists():continue
    if arq.suffix=='.png':
     with st.expander(arq.stem.replace('_',' ').capitalize(),expanded=padrao in ('02_correlacao.png','03_dendrograma.png','04_pca_variancia.png')):
      st.image(str(arq),use_container_width=True)
    elif arq.suffix=='.csv':
     tabela=pd.read_csv(arq)
     st.dataframe(tabela.round(4),hide_index=True,use_container_width=True)
     st.download_button('Baixar '+titulo+' (CSV)',arq.read_bytes(),file_name=arq.name,mime='text/csv',key='prof_'+orig[selecao]+arq.name)
   if padrao=='04_pca_variancia.png':
    pesos=pasta/'04_pca_pesos_variaveis.csv'
    if pesos.exists():
     with st.expander('Pesos das componentes principais'):
      st.dataframe(pd.read_csv(pesos).round(3),hide_index=True,use_container_width=True)
  st.markdown('#### Correlação com a vazão: leitura orientada')
  c=pasta/'02_correlacao_pearson.csv'
  if c.exists():
   cc=pd.read_csv(c,index_col=0)
   if 'vazao_m3s' in cc.columns:
    st.dataframe(cc[['vazao_m3s']].drop('vazao_m3s').sort_values('vazao_m3s',ascending=False).round(3),use_container_width=True)
    st.caption('Associações simultâneas entre variáveis; não são relações causais nem necessariamente previsões em M+1. Investigar defasagens e sazonalidade antes de inferências.')
 st.markdown('#### PCA do notebook original — referência metodológica')
 st.write('No notebook trabalhado anteriormente, a PCA considerou seis entradas climáticas P1–P6, excluindo Q (vazão), e explicou aproximadamente 71,65% na CP1, 13,74% na CP2 e 7,90% na CP3, com 218 meses coincidentes de 1975 a março de 1993. Estes valores são **resultados anteriormente registrados**, não recalculados nesta versão. A PCA do arquivo exibido acima usa outro conjunto de variáveis e não deve substituí-los.')
 st.markdown('#### Arquivo integral das análises')
 st.download_button('Baixar resultados estatísticos arquivados (ZIP)',(ROOT/'RESULTADOS_CODIGO_PROFESSOR.zip').read_bytes(),file_name='RESULTADOS_CODIGO_PROFESSOR.zip',mime='application/zip')

with abas[5]:
 st.subheader('Discussão hidrológica · o que os dados permitem afirmar')
 st.markdown('''**Pergunta central:** como o comportamento das vazões e o armazenamento do reservatório podem subsidiar a discussão sobre a vazão mínima operativa da UHE Três Marias?

A plataforma **não determina uma nova vazão mínima operativa**. Ela organiza evidências sobre disponibilidade hídrica (vazão natural e afluência), água efetivamente liberada (defluência), armazenamento (volume útil e cota), eventos de estiagem e capacidade de previsão mensal. A definição de uma regra operativa depende de condicionantes oficiais, usos a jusante e requisitos ambientais.''')
 completos=ana.loc[ana.mes_completo.astype(str).str.lower().eq('true')].copy()
 completos['diferenca_defluencia_afluencia']=completos.defluencia_m3s-completos.afluencia_m3s
 completos['variacao_volume_util_pp']=completos.volume_util_pct.diff()
 st.markdown('#### Entrada, saída e armazenamento')
 oper=px.line(completos,x='data',y=['afluencia_m3s','defluencia_m3s'],labels={'value':'Vazão média mensal (m³/s)','data':'Mês','variable':'Série'},title='Afluência e defluência mensais')
 st.plotly_chart(oper,use_container_width=True)
 st.plotly_chart(px.line(completos,x='data',y='volume_util_pct',title='Evolução do volume útil médio (%)',labels={'volume_util_pct':'Volume útil médio (%)','data':'Mês'}),use_container_width=True)
 ult=completos.iloc[-1]
 a,b,c=st.columns(3)
 a.metric('Afluência — último mês completo',f'{ult.afluencia_m3s:.1f} m³/s')
 b.metric('Defluência — último mês completo',f'{ult.defluencia_m3s:.1f} m³/s')
 c.metric('Defluência − afluência',f'{ult.diferenca_defluencia_afluencia:+.1f} m³/s')
 st.caption('Defluência superior à afluência é compatível com retirada de água armazenada, mas não prova isoladamente a variação do armazenamento: existem outros termos no balanço, incertezas e diferenças de definição. Volume útil aqui é média mensal, não volume no início/fim do mês.')
 st.markdown('#### Meses com maior diferença entre saída e entrada')
 view=completos.nlargest(12,'diferenca_defluencia_afluencia')[['data','afluencia_m3s','defluencia_m3s','diferenca_defluencia_afluencia','volume_util_pct']].copy()
 view['data']=view['data'].dt.strftime('%m/%Y')
 st.dataframe(view.round(2),hide_index=True,use_container_width=True)
 st.markdown('#### Evidências, limitações e necessidades de validação')
 st.markdown('''**Evidências disponíveis:** séries diárias e mensais da ANA (2020–2026); curvas de permanência e sazonalidade; valores mínimos e episódios críticos; previsão M+1 de vazão natural; diagnósticos climáticos históricos.

**O que ainda não está demonstrado:** valor de vazão mínima juridicamente vigente para cada condição de operação; atendimento aos usos múltiplos a jusante; necessidades ecológicas; simulação hidrodinâmica; comparação formal com SMAP/ONS; impactos de uma alteração da defluência.

**Direção para o texto do TCC:** apresentar resultados como diagnóstico hidrológico e subsídio à discussão, sem afirmar que os indicadores de permanência constituem, por si, vazão mínima ecológica ou autorizada.''')
 st.markdown('#### Roteiro de redação baseado no próprio painel')
 st.write('1. Área de estudo e fontes → Metodologia e dados. 2. Comportamento hidrológico recente → Histórico e operação. 3. Permanência, sazonalidade e eventos críticos → Vazões mínimas. 4. Modelo e validação temporal → Modelo M+1. 5. Relações climáticas → Análises climáticas. 6. Implicações e limitações → Discussão do TCC.')

with abas[6]:
 st.markdown('''### Escopo e rastreabilidade
**Modelo M+1:** usa apenas a exportação diária da ANA desde 2020, convertida para médias mensais de vazão **natural**. Outubro de 2026 está incompleto e não participa do ajuste nem do teste. A última origem válida é setembro de 2026, com previsão para outubro de 2026.

**Entradas do modelo:** vazão natural mensal contemporânea e defasada (0, 1, 2, 3, 6 e 12 meses), médias móveis anteriores de 3 e 6 meses e sazonalidade do mês previsto. Regressão Ridge com padronização. Não usa chuva/ZCAS/bloqueios porque essas séries não foram atualizadas até 2026.

**Teste:** separação temporal fixa. Treinamento em pares com alvo anterior a janeiro de 2025; teste em janeiro de 2025 a setembro de 2026. Após o teste, o modelo final é reajustado com todos os pares conhecidos para emitir a previsão de outubro.

**Análises do professor:** reprocessadas separadamente sobre a base histórica original, pois a ANA disponibilizada cobre somente 2020–2026. A base histórica **não entra no modelo novo**. Os notebooks e resultados anteriores permanecem intactos.

**Limitações:** sem validação operacional, sem simulação completa de balanço hídrico do reservatório e sem comparação com SMAP/ONS. Vazão natural não é sinônimo de defluência mínima. Para prever novembro, aguarde outubro completo e atualize a exportação da ANA.''')

with abas[6]:
 st.markdown('#### Base de dados e arquivos para auditoria')
 st.write('**Fonte:** ANA/SAR, exportação diária de Três Marias, baixada em 19/10/2026, com registros até 18/10/2026. Dados de outubro são parciais e excluídos dos indicadores mensais de treinamento. Não há atualização automática pela internet: para renovar, exporte novo arquivo e execute a preparação e o modelo.')
 st.write('**Tratamento:** médias aritméticas dos registros diários para vazões, cota e volume útil. Mês completo exige registros válidos para todos os dias. Q90/Q95 são quantis empíricos de excedência; resultados dependem da escala temporal e do período de amostragem.')
 for nome,arq in [('ANA diária','ana_diario.csv'),('ANA mensal','ana_mensal.csv'),('Métricas do M+1','metricas.csv'),('Previsões de teste','previsoes_teste.csv')]:
  f=OUT/arq
  if f.exists():st.download_button('Baixar '+nome+' (CSV)',f.read_bytes(),file_name=arq,mime='text/csv',key='download_'+arq)
 st.markdown('#### Publicação e responsabilidade')
 st.caption('Hospedagem não é atualização em tempo real. A versão publicada exibe a última base processada e deve registrar sua data de corte. Projeto acadêmico independente, não é portal oficial da UFF ou da ANA.')

st.markdown('<div class="uff-footer">Pesquisa acadêmica · UHE Três Marias · Fonte de dados: ANA · Identidade visual inspirada na UFF · Resultados não operacionais</div>',unsafe_allow_html=True)
