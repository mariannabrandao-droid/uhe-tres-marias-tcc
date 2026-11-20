"""Série diária convencional de Pirapora Barreiro, HidroWeb/ANA."""

import pandas as pd

from hidroclima import ROOT

SOURCE = ROOT / 'dados_ana' / '41135000_Vazoes.csv'


def daily_series():
    with SOURCE.open(encoding='latin1') as source:
        header = next(i for i, line in enumerate(source) if line.startswith('EstacaoCodigo;'))
    raw = pd.read_csv(SOURCE, encoding='latin1', sep=';', skiprows=header, decimal=',',
                      dtype={'EstacaoCodigo': str})
    raw = raw.loc[raw.EstacaoCodigo.eq('41135000') & raw.MediaDiaria.eq(1)].copy()
    raw['Data'] = pd.to_datetime(raw.Data, format='%d/%m/%Y')
    fields = [f'Vazao{day:02}' for day in range(1, 32)]
    daily = raw.melt(id_vars=['Data', 'NivelConsistencia'], value_vars=fields,
                     var_name='campo', value_name='vazao_m3s').dropna(subset=['vazao_m3s'])
    day = daily.campo.str[-2:].astype(int)
    valid = day.le(daily.Data.dt.days_in_month)
    daily = daily.loc[valid].assign(dia=daily.Data[valid] + pd.to_timedelta(day[valid] - 1, unit='D'))
    distinct = daily[['dia', 'NivelConsistencia', 'vazao_m3s']].drop_duplicates()
    # Valores divergentes no mesmo nível são excluídos daquele nível.
    clean = distinct.drop_duplicates(['dia', 'NivelConsistencia'], keep=False)
    return clean.sort_values(['dia', 'NivelConsistencia']).reset_index(drop=True)
