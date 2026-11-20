"""Séries e indicadores descritivos mensais do painel."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'ANA_Etapa02' / 'resultados'
DAILY = ROOT / 'ANA_Etapa02' / 'entradas' / 'sar_diario.csv'
ISSUE = pd.Timestamp('2026-11-11')
DRY = (5, 6, 7, 8, 9, 10)
FLOW = ('vazao_natural_m3s', 'afluencia_m3s', 'defluencia_m3s')
LABELS = {
    'vazao_natural_m3s': 'Vazão natural', 'afluencia_m3s': 'Afluência',
    'defluencia_m3s': 'Defluência', 'volume_util_pct': 'Volume útil',
    'cota_m': 'Cota', 'vertida_m3s': 'Vazão vertida', 'turbinada_m3s': 'Vazão turbinada',
    'chuva_barramento_mm': 'Chuva no Barramento', 'chuva_mesquita_mm': 'Chuva em Mesquita',
    'chuva_andrequice_mm': 'Chuva em Andrequicé', 'vazao_jusante_m3s': 'Vazão do posto Jusante',
    'vazao_indaia_m3s': 'Vazão no Indaiá', 'vazao_barramento_m3s': 'Vazão cadastrada no Barramento (auxiliar)', 'SACZ_AB': 'Índice ZCAS AB',
    'SACZ_C': 'Índice ZCAS C', 'SACZ_DE': 'Índice ZCAS DE',
    'dias_bloqueio_total': 'Dias de bloqueio',
}
SAR = (*FLOW, 'volume_util_pct', 'cota_m', 'vertida_m3s', 'turbinada_m3s')


def unit(key):
    if key.endswith('_m3s'):
        return 'm³/s'
    if key.endswith('_mm'):
        return 'mm/mês'
    return {'volume_util_pct': '%', 'cota_m': 'm', 'dias_bloqueio_total': 'dias/mês'}.get(key, 'índice')


def monthly_csv(name):
    return pd.read_csv(DATA / name, sep=';', parse_dates=['data']).set_index('data').sort_index().asfreq('MS')


def complete_sar():
    sar = monthly_csv('04_sar_mensal_cobertura_por_variavel.csv')
    for key in SAR:
        sar[key] = sar[key].where(np.isclose(sar[key + '_cobertura'], 1, rtol=0, atol=1e-9))
    return sar


def read_series():
    series = {key: value for key, value in complete_sar()[list(SAR)].items()}
    for code, key in (
        ('01845009', 'chuva_barramento_mm'), ('01944060', 'chuva_mesquita_mm'),
        ('01845032', 'chuva_andrequice_mm'), ('41020002', 'vazao_jusante_m3s'),
        ('40963000', 'vazao_indaia_m3s'), ('40990080', 'vazao_barramento_m3s'),
    ):
        kind = 'Chuvas' if key.startswith('chuva') else 'Vazoes'
        source = monthly_csv(f'mensal/{code}_{kind}.csv')
        series[key] = source.valor_analise.where(source.cobertura.eq(1))
    climate = monthly_csv('11_indices_climaticos_mensais.csv')
    for key in ('SACZ_AB', 'SACZ_C', 'SACZ_DE', 'dias_bloqueio_total'):
        coverage = 'bloqueio_cobertura' if key.startswith('dias') else key + '_cobertura'
        series[key] = climate[key].where(climate[coverage].eq(1))
    return pd.DataFrame(series).sort_index().asfreq('MS')


def coverage(series):
    valid = series.dropna()
    if valid.empty:
        return dict(inicio=pd.NaT, fim=pd.NaT, n=0, meses_calendario=0)
    return dict(inicio=valid.index.min(), fim=valid.index.max(), n=len(valid),
                meses_calendario=len(series.loc[valid.index.min():valid.index.max()]))


def paired_months(frame, x, y, lag=0, anomalies=False):
    calendar = frame[[x, y]].asfreq('MS')
    if anomalies:
        calendar = calendar - calendar.groupby(calendar.index.month).transform('mean')
    return pd.DataFrame({'x': calendar[x], 'y': calendar[y].shift(-lag)}).dropna()


def correlation(frame, x, y, lag=0, anomalies=False):
    paired = paired_months(frame, x, y, lag, anomalies)
    start, end = paired.index.min(), paired.index.max()
    defined = len(paired) >= 3 and paired.x.nunique() > 1 and paired.y.nunique() > 1
    return dict(k=lag, r=paired.x.corr(paired.y) if defined else np.nan, n=len(paired),
                inicio_x=start, fim_x=end, inicio_y=start + pd.DateOffset(months=lag),
                fim_y=end + pd.DateOffset(months=lag))


def permanence(series):
    values = np.sort(series.dropna().to_numpy())[::-1]
    return pd.DataFrame({'excedencia': 100 * np.arange(1, len(values) + 1) / (len(values) + 1),
                         'vazao': values})


def reference_quantile(curve, exceedance):
    if curve.empty or not curve.excedencia.min() <= exceedance <= curve.excedencia.max():
        return np.nan
    return float(np.interp(exceedance, curve.excedencia, curve.vazao))


def threshold_stats(series, limit, groups=None):
    values = series.dropna()
    below = values.lt(limit)
    if groups is None:
        return dict(meses=len(values), abaixo=int(below.sum()), frequencia=100 * below.mean())
    out = below.groupby(groups.reindex(values.index)).agg(['size', 'sum', 'mean'])
    return out.rename(columns={'size': 'Meses válidos', 'sum': 'Abaixo', 'mean': 'Frequência (%)'}).assign(
        **{'Frequência (%)': lambda df: df['Frequência (%)'] * 100})


def period_groups(index):
    return pd.Series(np.where(index.year <= 2022, '2020–2022', '2023–2026'), index=index)


def longest_below(series, limit):
    flags = series.asfreq('MS').lt(limit)
    return int(flags.groupby((~flags).cumsum()).sum().max()) if len(flags) else 0


def climate_comparison(frame, key, limit):
    rows = []
    for climate in ('chuva_andrequice_mm', 'SACZ_AB', 'dias_bloqueio_total'):
        pairs = frame[[key, climate]].dropna()
        for season, mask in [('Seca', pairs.index.month.isin(DRY)), ('Chuvosa', ~pairs.index.month.isin(DRY))]:
            subset = pairs.loc[mask]
            if subset.empty:
                continue
            below = subset[key].lt(limit)
            for label, group in [('Abaixo', subset[below]), ('Igual ou acima', subset[~below])]:
                rows.append(dict(variavel=LABELS[climate], unidade=unit(climate), temporada=season,
                                 faixa=label, n=len(group), mediana=group[climate].median(),
                                 inicio=subset.index.min(), fim=subset.index.max()))
    return pd.DataFrame(rows)
