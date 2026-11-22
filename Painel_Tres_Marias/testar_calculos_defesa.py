"""Reproduz os resultados centrais diretamente das entradas locais."""
from math import isclose, sqrt

import pandas as pd

from analise_defesa import CLIMATE, associations, climate_series, historical_evidence, low_runs
from defluencia_diurna import analyze, read_october
from hidroclima import DAILY, DATA, FLOW, complete_sar, permanence, read_series, reference_quantile


def monthly_manually(series, operation):
    groups = series.groupby(series.index.to_period('M'))
    result = {}
    for period, values in groups:
        valid = values.dropna()
        if len(valid) == period.days_in_month:
            result[period.start_time] = operation(valid)
    return pd.Series(result)


def pearson_independent(x, y):
    dx = x - x.mean()
    dy = y - y.mean()
    return (dx * dy).sum() / sqrt((dx ** 2).sum() * (dy ** 2).sum())


def main():
    sar_daily = pd.read_csv(DAILY, index_col='data', parse_dates=['data'])[FLOW[0]]
    monthly = monthly_manually(sar_daily, lambda x: sum(x) / len(x))
    sar = complete_sar()
    pd.testing.assert_series_equal(monthly, sar[FLOW[0]].dropna(), check_names=False, check_freq=False)
    evidence = historical_evidence(sar)
    assert (len(monthly), int(monthly.lt(150).sum()), evidence['longest']) == (81, 16, 5)
    assert isclose(evidence['min_median'], 128.167)
    assert isclose(evidence['max_median'], 1350.535357142857)
    curve = permanence(monthly)
    assert round(reference_quantile(curve, 90), 2) == 100.87
    assert round(reference_quantile(curve, 95), 2) == 69.19
    print('SAR diário → mês completo: 16/81 abaixo de 150 m³/s, sequência máxima 5 meses.')
    assert list(low_runs(pd.Series([149., 150., None, 149., 149.],
                                    index=pd.date_range('2000-01', periods=5, freq='MS')), 150).Meses) == [2, 1]

    rain_daily = pd.read_csv(DATA / 'diario/01845032_Chuvas.csv', sep=';', index_col='data', parse_dates=['data'])
    rain = monthly_manually(rain_daily.valor.where(rain_daily.observacao_admitida), sum).rename('rain')
    pairs = rain.to_frame().join(monthly.rename('q').set_axis(monthly.index - pd.DateOffset(months=2))).dropna()
    anomalous = pairs - pairs.groupby(pairs.index.month).transform('mean')
    coefficient = pearson_independent(anomalous.rain, anomalous.q)
    panel = associations(read_series(), ['chuva_andrequice_mm'], FLOW[0], lags=[2]).iloc[0]
    assert len(pairs) == panel.n == 76 and isclose(coefficient, panel.r)
    print(f'ANA Andrequicé diária → total mensal × SAR natural em t+2: n={len(pairs)}, Pearson r={coefficient:.6f}.')

    # Outubro passa a novembro em t+1. O mês-alvo define a retirada.
    index = pd.date_range('2019-09-01', '2022-12-01', freq='MS')
    small = pd.DataFrame({'x': [i % 9 for i in range(len(index))],
                          'q': [(i * i) % 13 for i in range(len(index))]}, index=index)
    for lag in (0, 1, 2, 3):
        manual = [(date, date + pd.DateOffset(months=lag)) for date in index[:-lag or None]]
        years = [target.year + int(target.month >= 11) for _, target in manual]
        trials = []
        for year in sorted(set(years)):
            kept = [pair for pair, water_year in zip(manual, years) if water_year != year]
            x_dates, y_dates = zip(*kept)
            x = small.loc[list(x_dates), 'x'].reset_index(drop=True)
            y = small.loc[list(y_dates), 'q'].reset_index(drop=True)
            trials.append(pearson_independent(x, y))
        row = associations(small, ['x'], 'q', anomalies=False, lags=[lag]).iloc[0]
        assert isclose(row['Sensibilidade mín.'], min(trials))
        assert isclose(row['Sensibilidade máx.'], max(trials))
        assert row['Anos hidrológicos'] == len(set(years))

    frame = read_series()
    climate, counts = climate_series()
    for key in ['SACZ_AB', 'SACZ_C', 'SACZ_DE', 'Total']:
        legacy = 'dias_bloqueio_total' if key == 'Total' else key
        old = frame[legacy].dropna()
        pd.testing.assert_series_equal(climate[key].reindex(old.index), old,
                                       check_names=False, check_freq=False)
    frame = frame.drop(columns=['SACZ_AB', 'SACZ_C', 'SACZ_DE']).join(climate)
    rows = associations(frame, CLIMATE, 'chuva_barramento_mm', lags=[0]).set_index('Recorte')
    assert rows.n.eq(220).all() and round(rows.loc['SACZ_C', 'r'], 3) == .671
    assert int(counts.set_index('Recorte').loc['Total', 'Episódios detectados']) == 1164
    print('ZCAS e bloqueio Total: agregações coincidem na cobertura do legado. A série Total recupera 12 meses de 1960. Chuva Barramento × C: r=0,671, n=220.')

    raw_hours, raw_days = read_october()
    hours = raw_hours[raw_hours.din_instante.dt.hour.between(7, 18)]
    q = hours.val_vazaodefluente
    by_day = q.groupby(hours.din_instante.dt.normalize())
    mean = raw_days.set_index('din_instante').val_vazaodefluente
    flagged = mean.ge(300) & by_day.min().lt(300) & by_day.count().eq(12)
    _, panel = analyze(raw_hours, raw_days, 300)
    assert (len(hours), int(q.lt(300).sum()), int(by_day.min().lt(300).sum()), int(flagged.sum())) == (372, 95, 10, 8)
    assert list(mean.index[flagged]) == list(panel.index[panel.diverge])
    day = pd.Timestamp('2026-10-22')
    assert mean.loc[day] == 450 and by_day.min().loc[day] == 164
    assert hours.loc[q.groupby(hours.din_instante.dt.normalize()).idxmin().loc[day], 'din_instante'].hour == 14
    _, missing = analyze(raw_hours.drop(hours.index[0]), raw_days, 300)
    assert missing.elegivel.sum() == 30
    _, equal_mean = analyze(raw_hours, raw_days, 450)
    equal_hours, _ = analyze(raw_hours, raw_days, 164)
    assert equal_mean.loc[day, 'diverge'] and not equal_hours.loc[
        equal_hours.dia.eq(day) & equal_hours.val_vazaodefluente.eq(164), 'abaixo'].any()
    print('ONS: 95/372 horas, 10/31 dias com horas abaixo e 8/31 divergências. Dia 22: 450 e 164 m³/s.')
    print('Casos de borda: lacuna, igualdade, alinhamento da hora e da defasagem conferidos.')


if __name__ == '__main__':
    main()
