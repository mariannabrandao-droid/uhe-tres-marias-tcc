"""Confronto exploratório de registros horários da usina com a estação 41020002."""
from pathlib import Path

import numpy as np
import pandas as pd

STATION = '41020002'
FIELDS = ['estacao', 'inicio_intervalo', 'vazao_m3s']
DATA = Path(__file__).resolve().parent / 'dados_ons'


def load_station_csv(file):
    data = pd.read_csv(file, dtype={'estacao': str}, encoding='utf-8-sig')
    if not set(FIELDS).issubset(data.columns) or data.empty:
        raise ValueError('Use as três colunas do modelo CSV e preencha os registros disponíveis.')
    if not data.estacao.eq(STATION).all():
        raise ValueError('Todos os registros devem identificar a estação 41020002.')
    stamp = pd.to_datetime(data.inicio_intervalo, format='%Y-%m-%d %H:%M', errors='raise')
    if stamp.isna().any() or not stamp.eq(stamp.dt.floor('h')).all() or stamp.duplicated().any():
        raise ValueError('Informe uma única linha por hora, com início do intervalo em hora cheia.')
    values = pd.to_numeric(data.vazao_m3s, errors='raise')
    if not np.isfinite(values).all() or values.lt(0).any():
        raise ValueError('Informe vazões horárias válidas, não negativas, em m³/s. Omita horas sem dados.')
    return pd.Series(values.to_numpy(), index=stamp, name='vazao_41020002_m3s').sort_index()


def compare(hourly, days, threshold, downstream=None):
    paired = hourly[['inicio', 'dia', 'val_vazaodefluente']].copy().rename(
        columns={'val_vazaodefluente': 'defluencia_ons_m3s'})
    paired['limiar_m3s'] = threshold
    paired['vazao_41020002_m3s'] = paired.inicio.map(downstream) if downstream is not None else np.nan
    paired['ons_abaixo'] = paired.defluencia_ons_m3s.lt(threshold)
    paired['jusante_abaixo'] = paired.vazao_41020002_m3s.lt(threshold).where(
        paired.vazao_41020002_m3s.notna()).astype('boolean')
    counts = paired.groupby('dia').agg(
        intervalos_jusante=('vazao_41020002_m3s', 'count'),
        minimo_disponivel_jusante=('vazao_41020002_m3s', 'min'),
        intervalos_jusante_abaixo=('jusante_abaixo', lambda values: values.sum(min_count=1)),
    )
    summary = days.join(counts)
    coverage = summary.intervalos_jusante.fillna(0).astype(int)
    summary['intervalos_jusante'] = coverage
    summary['cobertura_jusante'] = np.select(
        [coverage.eq(0), coverage.eq(12)], ['Sem registros pareados', '12 de 12 intervalos'], default='Parcial')
    return paired, summary


def operational_context():
    return pd.read_csv(DATA / 'ons_contexto_sftmar_2026-10.csv', parse_dates=['din_instante']).set_index('din_instante')
