"""Reexecuta os métodos descritivos do trabalho do professor com a base histórica original.
Não substitui os notebooks originais; usa os mesmos tipos de análise, com critérios explícitos.
"""
from pathlib import Path
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage,dendrogram
from scipy.spatial.distance import pdist,squareform
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'resultados_v2'/'professor_recalculado';OUT.mkdir(parents=True,exist_ok=True)
base=pd.read_csv(ROOT/'BASE_INTEGRADA_TCC.csv',parse_dates=['data']).set_index('data')
for nome,campos in {'A_quatro_familias_1975_1993':['precipitacao_mm','zcas_ab','zcas_c','zcas_de','dias_bloqueio','vazao_m3s'],'B_tres_familias_periodo_longo':['zcas_ab','zcas_c','zcas_de','dias_bloqueio','vazao_m3s']}.items():
 sub=base[campos].apply(pd.to_numeric,errors='coerce').dropna()
 if nome.startswith('A'):sub=sub.loc['1975-01':'1993-12']
 if len(sub)<30:raise ValueError(f'{nome}: poucos meses completos {len(sub)}')
 pasta=OUT/nome;pasta.mkdir(exist_ok=True)
 sub.describe().T.to_csv(pasta/'01_estatisticas_descritivas.csv')
 corr=sub.corr();corr.to_csv(pasta/'02_correlacao_pearson.csv')
 fig,ax=plt.subplots(figsize=(9,7));im=ax.imshow(corr,vmin=-1,vmax=1,cmap='RdBu_r');ax.set_xticks(range(len(campos)),campos,rotation=45,ha='right');ax.set_yticks(range(len(campos)),campos)
 for i in range(len(campos)):
  for j in range(len(campos)):ax.text(j,i,f'{corr.iloc[i,j]:.2f}',ha='center',va='center',fontsize=9)
 fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(pasta/'02_correlacao.png',dpi=150);plt.close(fig)
 z=StandardScaler().fit_transform(sub);dist=squareform(pdist(z.T));pd.DataFrame(dist,index=campos,columns=campos).to_csv(pasta/'03_distancia_euclidiana_padronizada.csv')
 fig,ax=plt.subplots(figsize=(10,5));dendrogram(linkage(z.T,method='average',metric='euclidean'),labels=campos,ax=ax);ax.set_ylabel('Distância euclidiana padronizada');fig.tight_layout();fig.savefig(pasta/'03_dendrograma.png',dpi=150);plt.close(fig)
 pca=PCA().fit(z);pd.DataFrame({'CP':[f'CP{i+1}' for i in range(len(campos))],'Variancia_Explicada_%':pca.explained_variance_ratio_*100,'Variancia_Acumulada_%':np.cumsum(pca.explained_variance_ratio_)*100}).to_csv(pasta/'04_pca_variancia.csv',index=False)
 pd.DataFrame(pca.components_.T,index=campos,columns=[f'CP{i+1}' for i in range(len(campos))]).to_csv(pasta/'04_pca_pesos_variaveis.csv')
 pd.DataFrame(pca.transform(z),index=sub.index,columns=[f'CP{i+1}' for i in range(len(campos))]).to_csv(pasta/'04_pca_escores_mensais.csv')
 print(nome,'meses=',len(sub),'intervalo=',sub.index.min().date(),sub.index.max().date())
