"""Converte a exportação HTML .xls da ANA em série diária e mensal auditável."""
from pathlib import Path
from html.parser import HTMLParser
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'Histórico_TRÊS MARIAS (1).xls'
OUT=ROOT/'resultados_v2';OUT.mkdir(exist_ok=True)
class Tabela(HTMLParser):
    def __init__(self): super().__init__();self.rows=[];self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='tr':self.row=[]
        if tag in ('td','th'):self.cell=[]
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:self.row.append(''.join(self.cell).strip());self.cell=None
        if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
p=Tabela();p.feed(SOURCE.read_text(encoding='utf-8-sig',errors='replace'))
headers=p.rows[0];df=pd.DataFrame(p.rows[1:],columns=headers)
col_data=next(c for c in df if 'Data da' in c)
df['data']=pd.to_datetime(df[col_data],format='%d/%m/%Y',errors='coerce')
cols={'Afluência (m³/s)':'afluencia_m3s','Defluência (m³/s)':'defluencia_m3s','Vazão Natural (m³/s)':'vazao_natural_m3s','Volume Útil (%)':'volume_util_pct','Cota (m)':'cota_m','Vazão Vertida (m³/s)':'vertida_m3s','Vazão Turbinada (m³/s)':'turbinada_m3s'}
for nome,dest in cols.items():
    if nome not in df:raise ValueError(f'Coluna ausente: {nome}; disponíveis: {list(df)}')
    df[dest]=pd.to_numeric(df[nome].str.replace('.','',regex=False).str.replace(',','.',regex=False),errors='coerce')
df=df.dropna(subset=['data']).sort_values('data').drop_duplicates('data',keep='last').set_index('data')
if not df.index.is_monotonic_increasing:raise ValueError('Datas não ordenadas')
daily=df[list(cols.values())].copy();daily.to_csv(OUT/'ana_diario.csv',index_label='data')
mensal=daily.resample('MS').mean();mensal['dias_registrados']=daily['vazao_natural_m3s'].resample('MS').count();mensal['dias_mes']=mensal.index.days_in_month
mensal['mes_completo']=mensal['dias_registrados'].eq(mensal['dias_mes'])
mensal.to_csv(OUT/'ana_mensal.csv',index_label='data')
print('ANA:',len(daily),'dias',daily.index.min().date(),'até',daily.index.max().date())
print('Meses completos:',int(mensal.mes_completo.sum()),'de',len(mensal))
print(mensal.tail(4)[['vazao_natural_m3s','dias_registrados','dias_mes','mes_completo']].to_string())
