"""Leitura e agregação das séries históricas de vazão e clima."""
import pandas as pd

from hidroclima import ROOT

ASSETS = ROOT / 'assets' / 'tcc'
MONTHS = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
OCT_MAR = (10, 11, 12, 1, 2, 3)
NOAA = 'https://www.cpc.ncep.noaa.gov/data/indices/'
NOAA_DATA = 'https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt'


def historical_flows():
    return pd.read_csv(ASSETS / 'vazao_1931_2023.csv').set_index('ano')


def zcas_annual(series):
    monthly = series.loc['1961':'2023'].asfreq('MS')
    years = monthly.groupby(monthly.index.year)
    annual = years.mean().where(years.count().eq(12)).rename('Índice anual')
    annual = annual.reindex(range(1961, 2024))
    return annual.to_frame().assign(**{
        'Média móvel de 3 anos': annual.rolling(3, min_periods=3).mean(),
        'Média móvel de 5 anos': annual.rolling(5, min_periods=5).mean(),
    })


def blocking_seasonality(series):
    values = series.loc['1961':'2023']
    return values.groupby(values.index.month).agg(['mean', 'count']).reindex(range(1, 13))


def oni_series():
    data = pd.read_csv(ASSETS / 'noaa_oni.txt', sep=r'\s+')
    months = dict(zip(('DJF','JFM','FMA','MAM','AMJ','MJJ','JJA','JAS','ASO','SON','OND','NDJ'), range(1, 13)))
    dates = pd.to_datetime(dict(year=data.YR, month=data.SEAS.map(months), day=1))
    series = pd.Series(data.ANOM.to_numpy(), index=dates, name='ONI (°C)').sort_index()
    return series.asfreq('MS')
