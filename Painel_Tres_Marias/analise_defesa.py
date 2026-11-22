"""Cálculos descritivos da edição de defesa."""
import numpy as np
import pandas as pd

from figuras_tcc import OCT_MAR
from hidroclima import DAILY, DRY, FLOW, ROOT, coverage

INPUTS = DAILY.parent
BLOCKS = {'Total': 'bloqueio_total_campos', 'Norte': 'north', 'Norte H1': 'north_h1',
          'Norte H2': 'north_h2', 'Sul': 'south', 'Sul H1': 'south_h1', 'Sul H2': 'south_h2'}
ZCAS = ['SACZ_AB', 'SACZ_C', 'SACZ_DE']
CLIMATE = [*ZCAS, *BLOCKS]
TARGETS = {'Chuva no Barramento': 'chuva_barramento_mm', 'Chuva em Andrequicé': 'chuva_andrequice_mm',
           'Vazão natural SAR': FLOW[0], 'Afluência SAR': FLOW[1], 'Vazão no Indaiá': 'vazao_indaia_m3s',
           'Vazão em Três Marias Jusante': 'vazao_jusante_m3s'}


def consecutive(flags, minimum=1):
    groups = flags.ne(flags.shift()).cumsum()
    return flags & flags.groupby(groups).transform('size').ge(minimum)


def blocking_daily(path):
    fields = pd.read_csv(path, sep=';', decimal=',', parse_dates=['time']).set_index('time')
    fields = fields.sort_index().asfreq('D')[['an_geop500', 'vort850', 'vort500']]
    valid = fields.notna().all(axis=1)
    return consecutive(valid & fields.gt(0).all(axis=1), 3).astype(float).where(valid)


def aggregate_daily(values, operation):
    grouped = values.resample('MS')
    count = grouped.count()
    result = grouped.agg(operation)
    return result.where(count.eq(count.index.days_in_month))


def climate_series():
    zcas = pd.read_csv(INPUTS / 'zcas_diario_fornecido.csv', parse_dates=['time']).set_index('time')
    monthly = {key: aggregate_daily(zcas[key], 'mean') for key in ZCAS}
    counts = []
    for key in ZCAS:
        row = coverage(monthly[key])
        counts.append({'Recorte': key, 'Início': row['inicio'], 'Fim': row['fim'],
                       'Meses completos': row['n'], 'Dias sinalizados': None, 'Episódios detectados': None})
    for name, filename in BLOCKS.items():
        days = blocking_daily(INPUTS / f'{filename}.csv')
        monthly[name] = aggregate_daily(days, 'sum')
        row = coverage(monthly[name])
        flags = days.eq(1)
        counts.append({'Recorte': name, 'Início': row['inicio'], 'Fim': row['fim'],
                       'Meses completos': row['n'], 'Dias sinalizados': int(flags.sum()),
                       'Episódios detectados': int((flags & ~flags.shift(fill_value=False)).sum())})
    return pd.DataFrame(monthly).asfreq('MS'), pd.DataFrame(counts)


def low_runs(series, threshold):
    values = series.asfreq('MS')
    flags = values.lt(threshold)
    runs = values[flags].groupby((~flags).cumsum()[flags])
    return pd.DataFrame(
        [(group.index.min(), group.index.max(), len(group), group.min()) for _, group in runs],
        columns=['Início', 'Fim', 'Meses', 'Mínimo mensal (m³/s)'],
    ).sort_values('Meses', ascending=False)


def pair_matrix(data, predictors, target, lag, season):
    data = data.asfreq('MS')
    paired = data[predictors].join(data[target].shift(-lag).rename('Y')).dropna()
    if season == 'Mai–out':
        paired = paired[paired.index.month.isin(DRY)]
    if season == 'Nov–abr':
        paired = paired[~paired.index.month.isin(DRY)]
    if season == 'Out–mar':
        target_month = (paired.index + pd.DateOffset(months=lag)).month
        paired = paired[paired.index.month.isin(OCT_MAR) & target_month.isin(OCT_MAR)]
    return paired


def _coefficients(pairs, anomalies):
    if anomalies:
        pairs = pairs - pairs.groupby(pairs.index.month).transform('mean')
    if len(pairs) < 3:
        return pd.Series(np.nan, index=pairs.columns.drop('Y'))
    return pairs.drop(columns='Y').corrwith(pairs.Y)


def associations(data, predictors, target, season='Todos', anomalies=True, lags=range(4)):
    rows = []
    for lag in lags:
        pairs = pair_matrix(data, predictors, target, lag, season)
        values = _coefficients(pairs, anomalies)
        target_months = pairs.index + pd.DateOffset(months=lag)
        water_year = (target_months + pd.DateOffset(months=2)).year
        years = sorted(set(water_year))
        trials = pd.DataFrame([
            _coefficients(pairs[water_year != year], anomalies)
            for year in years
        ], columns=predictors)
        for name in predictors:
            rows.append({'Recorte': name, 'Defasagem': lag, 'r': values[name], 'n': len(pairs),
                         'Início X': pairs.index.min(), 'Fim X': pairs.index.max(),
                         'Sensibilidade mín.': trials[name].min(), 'Sensibilidade máx.': trials[name].max(),
                         'Anos hidrológicos': len(years)})
    return pd.DataFrame(rows)


def historical_evidence(sar):
    series = sar[FLOW[0]]
    values = series.dropna()
    medians = values.groupby(values.index.month).median()
    runs = low_runs(series, 150)
    return {'n': len(values), 'low': int(values.lt(150).sum()), 'longest': int(runs.Meses.max()),
            'min_month': int(medians.idxmin()), 'min_median': float(medians.min()),
            'max_month': int(medians.idxmax()), 'max_median': float(medians.max()),
            'start': values.index.min(), 'end': values.index.max()}
