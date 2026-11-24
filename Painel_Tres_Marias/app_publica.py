"""Consulta livre multivariada, independente do estudo de caso."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from explorar_ana import explorer, show_series, download
from painel import configure_page

def monthly(result):
    code, variable, start, end, level, series = result
    x = series.assign(data=pd.to_datetime(series.data)).set_index('data').valor.reindex(pd.date_range(start,end))
    g = x.resample('MS')
    v = g.sum(min_count=1) if variable == 'Chuva' else g.mean()
    return v.where(g.count().eq(v.index.days_in_month))

def label(k):
    return f'{k[0]} · {k[1]} · {k[2]} a {k[3]} · nível {k[4]}'

def correlations(collection):
    st.header('Correlações hidroclimáticas')
    if len(collection)<2:
        st.info('Consulte pelo menos duas séries na configuração. Elas permanecem salvas durante a sessão.')
        return
    keys=list(collection)
    a=st.selectbox('Variável antecedente',keys,format_func=label,key='corr_a')
    b=st.selectbox('Variável resposta',keys,index=1,format_func=label,key='corr_b')
    x,y=monthly(collection[a]),monthly(collection[b])
    st.caption('Pearson sobre meses completos coincidentes. Defasagem positiva: antecedente em t e resposta em t+k. Associação não implica causalidade. Confira a relação espacial entre os postos.')
    rows=[]
    for lag in range(7):
        pair=pd.concat([x.rename('antecedente'),y.shift(-lag,freq='MS').rename('resposta')],axis=1).dropna()
        rows.append({'defasagem_meses':lag,'pares':len(pair),'r':pair.corr().iloc[0,1] if len(pair)>=12 else float('nan')})
    table=pd.DataFrame(rows)
    lag=st.slider('Defasagem para detalhamento',0,6,0)
    pair=pd.concat([x.rename('antecedente'),y.shift(-lag,freq='MS').rename('resposta')],axis=1).dropna()
    left,right=st.columns(2)
    with left:
        fig=go.Figure(go.Bar(x=table.defasagem_meses,y=table.r,marker_color='#0d1d96'))
        fig.update_layout(title='Correlação por defasagem',yaxis_range=[-1,1],xaxis_title='Meses')
        st.plotly_chart(fig)
    with right:
        fig=go.Figure(go.Scatter(x=pair.antecedente,y=pair.resposta,mode='markers',marker_color='#0d6aff'))
        fig.update_layout(title='Pares mensais',xaxis_title=a[1],yaxis_title=b[1])
        st.plotly_chart(fig)
    st.dataframe(table,hide_index=True)
    st.caption('Mínimo exploratório de 12 pares; sazonalidade e autocorrelação podem influenciar r. Não constitui teste de significância.')
    download(table,'Baixar correlações','correlacoes.csv')

def main():
    configure_page('Consulta hidroclimática | ANA')
    collection=st.session_state.setdefault('study_series',{})
    page=st.sidebar.radio('Etapas da análise',['Configuração da área','Histórico e disponibilidade','Correlações hidroclimáticas','Limites e extensões','Síntese e exportação'])
    st.sidebar.caption(f'{len(collection)} séries armazenadas nesta sessão')
    if page=='Configuração da área':
        st.header('Configuração da área de estudo')
        st.info('Consulte uma estação de vazão e uma ou mais de chuva. Repita a busca para adicionar séries sem perder as anteriores. Confira bacia e estado: nomes podem se repetir.')
        explorer()
    elif page=='Histórico e disponibilidade':
        if not collection:
            st.info('Consulte uma série na configuração.')
        else:
            k=st.selectbox('Série',list(collection),format_func=label)
            code,var,start,end,level,series=collection[k]
            show_series(series,code,var,start,end,level)
            if var=='Vazão':
                v=monthly(collection[k])
                limit=st.number_input('Patamar mensal descritivo (m³/s)',min_value=0.,value=150.)
                st.metric('Meses completos abaixo do patamar',int(v.lt(limit).sum()))
                st.caption('Patamar exploratório, não limite legal ou operacional.')
    elif page=='Correlações hidroclimáticas':
        correlations(collection)
    elif page=='Limites e extensões':
        st.header('Requisitos para ampliar a análise')
        st.write('A previsão experimental exige protocolo retrospectivo e histórico suficiente. A análise horária exige registros horários contemporâneos. As séries convencionais ANA consultadas aqui são diárias.')
        st.info('ZCAS e bloqueios exigem índices climáticos com região e período adequados à área selecionada. Os índices de Três Marias não são aplicados automaticamente a outras bacias.')
    else:
        st.header('Síntese e exportação')
        if collection:
            st.dataframe(pd.DataFrame([{'serie':label(k),'dias_validos':len(v[5]),'meses_completos':int(monthly(v).count())} for k,v in collection.items()]),hide_index=True)
            download(pd.concat([v[5] for v in collection.values()],ignore_index=True),'Baixar séries reunidas','series_estudo.csv')
            if st.button('Limpar área de estudo'):
                collection.clear()
                st.session_state.pop('ana_series_result',None)
                st.rerun()
        else:
            st.info('Nenhuma série consultada.')
    st.caption('Marianna Brandão Ferreira · Universidade Federal Fluminense')

if __name__=='__main__':
    main()
