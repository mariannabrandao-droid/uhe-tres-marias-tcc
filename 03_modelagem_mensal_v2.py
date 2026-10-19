"""Previsão de vazão natural mensal M+1, treinada EXCLUSIVAMENTE com ANA 2020+."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error,mean_squared_error
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'resultados_v2';OUT.mkdir(exist_ok=True)
if not (OUT/'ana_mensal.csv').exists():raise FileNotFoundError('Execute primeiro: python 02_preparar_ana.py')
a=pd.read_csv(OUT/'ana_mensal.csv',parse_dates=['data']).set_index('data').asfreq('MS')
q=a['vazao_natural_m3s'].where(a['mes_completo'].fillna(False)).astype(float)
# Para prever t+1: usa Q(t), Q(t-1)...; NÃO usa observação do mês previsto.
x=pd.DataFrame(index=q.index)
for lag in (0,1,2,3,6,12):x[f'q_lag{lag}']=q.shift(lag)
for win in (3,6):x[f'media{win}']=q.rolling(win,min_periods=win).mean()
mes=((x.index.month%12)+1)
x['seno_mes_alvo']=np.sin(2*np.pi*mes/12);x['cosseno_mes_alvo']=np.cos(2*np.pi*mes/12)
features=list(x.columns)
x['observado']=q.shift(-1);x['data_prevista']=x.index+pd.offsets.MonthBegin(1)
d=x.dropna(subset=features+['observado']).copy()
# Corte fixo: teste em 2025-2026, com treino exclusivamente anterior.
tr=d[d.data_prevista<'2025-01-01'];te=d[d.data_prevista>='2025-01-01']
if len(tr)<24 or len(te)<6:raise ValueError(f'Amostra insuficiente: treino={len(tr)}, teste={len(te)}')
model=make_pipeline(StandardScaler(),Ridge(alpha=10.0));model.fit(tr[features],tr.observado)
pred=np.maximum(model.predict(te[features]),0)
resultado=te[['data_prevista','observado']].copy();resultado['Autorregressivo']=pred;resultado['Persistencia']=te.q_lag0.to_numpy()
resultado.to_csv(OUT/'previsoes_teste.csv',index_label='data_origem')
def metricas(nome,p):
 y=te.observado.to_numpy();p=np.asarray(p);den=np.sum((y-y.mean())**2)
 return dict(Modelo=nome,Inicio_teste=str(te.data_prevista.min().date()),Fim_teste=str(te.data_prevista.max().date()),N_teste=len(y),MAE_m3s=round(mean_absolute_error(y,p),2),RMSE_m3s=round(np.sqrt(mean_squared_error(y,p)),2),NSE=round(1-np.sum((y-p)**2)/den,3) if den else None,Vies_m3s=round(np.mean(p-y),2))
met=pd.DataFrame([metricas('Persistencia',te.q_lag0),metricas('Autorregressivo',pred)]);met.to_csv(OUT/'metricas.csv',index=False)
# Reajusta com TODOS os pares conhecidos até setembro/2026, mantendo outubro fora.
final=make_pipeline(StandardScaler(),Ridge(alpha=10.0));final.fit(d[features],d.observado)
orig=x.dropna(subset=features).iloc[[-1]]
prev=float(max(0,final.predict(orig[features])[0]));mes_alvo=orig.index[0]+pd.offsets.MonthBegin(1)
info={'ultimo_mes_completo':str(orig.index[0].date()),'mes_previsto':str(mes_alvo.date()),'previsao_m3s':round(prev,2),'tipo_vazao':'Vazão natural (ANA)','fonte':'ANA - Histórico Três Marias (2020-2026)','aviso':'Previsão acadêmica M+1. Outubro de 2026 está incompleto; não utilizar como entrada do modelo ou previsão operacional.'}
(OUT/'ultima_previsao.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
print(met.to_string(index=False));print(info)
