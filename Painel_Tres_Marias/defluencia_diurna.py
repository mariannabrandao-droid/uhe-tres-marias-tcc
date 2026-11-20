"""Diagnóstico da escala temporal da defluência em Três Marias."""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent / 'dados_ons'
THRESHOLD = 300.0


def read_october():
    hourly = pd.read_csv(DATA / 'ons_horario_sftmar_2026-10.csv', parse_dates=['din_instante'])
    daily = pd.read_csv(DATA / 'ons_diario_sftmar_2026-10.csv', parse_dates=['din_instante'])
    return hourly, daily


def analyze(hourly, daily, limit, start="2026-10-01", end="2026-10-31"):
    """Compara a média diária oficial com os 12 intervalos diurnos completos."""
    series = hourly_intervals(hourly)
    window = series[series.inicio.dt.hour.between(6, 17)].copy()
    return daily_diagnosis(window, daily, limit, start, end)


def hourly_intervals(hourly):
    ends = hourly.din_instante
    if not (ends.dt.minute.eq(0) | ends.dt.strftime('%H:%M').eq('23:59')).all():
        raise ValueError('Horário de fim fora da convenção ONS observada.')
    starts = ends.where(ends.dt.minute.eq(59), ends - pd.Timedelta(hours=1)).dt.floor('h')
    series = hourly.assign(inicio=starts, dia=starts.dt.normalize())
    if series.inicio.duplicated().any():
        raise ValueError('Há horários ou dias duplicados no recorte ONS.')
    return series.sort_values('inicio')


def longest_run(flags):
    groups = flags.ne(flags.shift()).cumsum()
    return int(flags.groupby(groups).sum().max()) if len(flags) else 0


def daily_diagnosis(window, daily, limit, start, end):
    if daily.din_instante.duplicated().any():
        raise ValueError('Há dias duplicados no recorte ONS.')
    window['abaixo'] = window.val_vazaodefluente.lt(limit) & window.val_vazaodefluente.notna()
    counts = window.groupby('dia').agg(
        horas_validas=('val_vazaodefluente', 'count'),
        horas_abaixo=('abaixo', 'sum'),
        minimo_diurno=('val_vazaodefluente', 'min'),
        maior_sequencia=('abaixo', longest_run),
    )
    official = daily.set_index('din_instante').val_vazaodefluente.rename('media_diaria')
    calendar = pd.date_range(start, end, name='dia')
    result = counts.join(official, how='outer').reindex(calendar)
    result['elegivel'] = result.horas_validas.eq(12) & result.media_diaria.notna()
    result['diverge'] = (result.elegivel & result.media_diaria.ge(limit) & result.horas_abaixo.gt(0))
    result.loc[~result.elegivel, ['horas_abaixo', 'maior_sequencia', 'minimo_diurno']] = float('nan')
    eligible_hours = window[window.dia.isin(result.index[result.elegivel])]
    return eligible_hours, result
