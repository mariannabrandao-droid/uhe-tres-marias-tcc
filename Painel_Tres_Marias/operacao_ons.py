"""Fontes públicas do ONS, snapshots locais e atualização manual."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock
from fontes_https import open_official

import pandas as pd

ROOT = Path(__file__).resolve().parent
SNAPSHOT = ROOT / 'dados_ons' / 'operacao'
CACHE = ROOT / '.cache_ons'
CACHE_LOCK = Lock()
BASE = 'https://ons-aws-prod-opendata.s3.amazonaws.com/dataset'
STAMP = 'din_instante'
RES = 'id_reservatorio'
FLOW_FIELDS = ('val_nivelmontante', 'val_niveljusante', 'val_vazaoafluente',
               'val_vazaodefluente', 'val_vazaoturbinada', 'val_vazaovertida',
               'val_vazaooutrasestruturas')
FIELDS = {'diario': (*FLOW_FIELDS, 'val_volumeutilcon', 'val_vazaonatural', 'val_vazaoincremental'),
          'horario': (*FLOW_FIELDS, 'val_volumeutil'),
          'geracao': ('val_geracao',)}
SOURCES = {'diario': 'https://dados.ons.org.br/dataset/dados-hidrologicos-res',
           'horario': 'https://dados.ons.org.br/dataset/dados_hidrologicos_ho',
           'geracao': 'https://dados.ons.org.br/dataset/geracao-usina-2'}


@dataclass(frozen=True)
class Resource:
    kind: str
    period: str

    @property
    def name(self):
        return f'{self.kind}_{self.period}.csv'

    @property
    def url(self):
        period = self.period.replace('-', '_')
        if self.kind == 'diario':
            return f'{BASE}/dados_hidrologicos_di/DADOS_HIDROLOGICOS_RES_{period}.csv'
        if self.kind == 'horario':
            return f'{BASE}/dados_hidrologicos_ho/DADOS_HIDROLOGICOS_HO_{period}.csv'
        return f'{BASE}/geracao_usina_2_ho/GERACAO_USINA-2_{period}.csv'


def resources(months):
    months = sorted(set(months))
    return ([Resource('diario', year) for year in sorted({month[:4] for month in months})]
            + [Resource(kind, month) for month in months for kind in ('horario', 'geracao')])


def extract(resource, raw):
    identifier = 'id_ons' if resource.kind == 'geracao' else RES
    columns = [identifier, STAMP, *FIELDS[resource.kind]]
    all_rows = pd.read_csv(raw, sep=';', usecols=columns, dtype={identifier: str})
    selected = all_rows[identifier].eq('MGTMAR' if resource.kind == 'geracao' else 'SFTMAR')
    data = all_rows.loc[selected, [STAMP, *FIELDS[resource.kind]]].copy()
    data[STAMP] = pd.to_datetime(data[STAMP], format='ISO8601')
    period = data[STAMP].dt.strftime('%Y' if resource.kind == 'diario' else '%Y-%m')
    if data.empty or data[STAMP].isna().any() or data[STAMP].duplicated().any() or not period.eq(resource.period).all():
        raise ValueError('Recorte vazio, duplicado ou fora do período esperado.')
    for field in FIELDS[resource.kind]:
        data[field] = pd.to_numeric(data[field], errors='raise')
    primary = 'val_geracao' if resource.kind == 'geracao' else 'val_vazaodefluente'
    if data[primary].dropna().empty:
        raise ValueError('Arquivo sem registros utilizáveis para a variável principal.')
    if resource.kind == 'diario' and not data[STAMP].eq(data[STAMP].dt.normalize()).all():
        raise ValueError('Registro diário fora do início de dia.')
    if resource.kind == 'horario':
        from defluencia_diurna import hourly_intervals
        hourly_intervals(data)
    if resource.kind == 'geracao' and not data[STAMP].eq(data[STAMP].dt.floor('h')).all():
        raise ValueError('Registro de geração fora da hora cheia.')
    return data.sort_values(STAMP)


def fetch(resource):
    with open_official(resource.url, timeout=16) as response:
        return extract(resource, BytesIO(response.read()))


def write_resource(resource, data, directory, consulted):
    directory.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode='w', encoding='utf-8', newline='', dir=directory, delete=False) as output:
        path = Path(output.name)
        data.assign(consulta_utc=consulted).to_csv(output, index=False)
    try:
        path.replace(directory / resource.name)
    finally:
        path.unlink(missing_ok=True)


def store_verified(resource, data, directory, consulted):
    with CACHE_LOCK:
        path = directory / resource.name
        if not path.exists():
            path = SNAPSHOT / resource.name
        if path.exists():
            old = pd.read_csv(path, parse_dates=[STAMP])
            if not old[STAMP].isin(data[STAMP]).all():
                raise ValueError('A nova resposta omite horários ou dias já publicados. Cópia anterior preservada.')
        write_resource(resource, data, directory, consulted)


def import_csv(resource, raw, directory=CACHE):
    data = extract(resource, raw)
    store_verified(resource, data, directory, datetime.now(timezone.utc).isoformat(timespec='seconds'))
    return len(data)


def refresh(months, directory=CACHE):
    consulted = datetime.now(timezone.utc).isoformat(timespec='seconds')
    items = resources(months)
    status = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(fetch, resource) for resource in items]
        for resource, future in zip(items, futures):
            try:
                data = future.result()
                store_verified(resource, data, directory, consulted)
                status.append((resource.kind, resource.period, f'{len(data)} registros recebidos'))
            except (OSError, ValueError, KeyError) as error:
                status.append((resource.kind, resource.period, f'Falha na fonte · {error}'))
    return pd.DataFrame(status, columns=['Base', 'Arquivo', 'Resultado'])


def read(kind, directory=CACHE):
    bundled = {path.name: path for path in SNAPSHOT.glob(f'{kind}_*.csv')}
    files = dict(bundled)
    files.update({path.name: path for path in directory.glob(f'{kind}_*.csv')})
    if not files:
        return pd.DataFrame(columns=[STAMP, *FIELDS[kind], 'consulta_utc'])
    pieces = [pd.read_csv(path, parse_dates=[STAMP]) for path in files.values()]
    return pd.concat(pieces, ignore_index=True).sort_values(STAMP).reset_index(drop=True)


def day_mean_generation(hourly):
    if hourly.empty:
        return pd.Series(dtype=float, name='Geração média (MW)')
    grouped = hourly.set_index(STAMP).val_geracao.resample('D')
    return grouped.mean().where(grouped.count().eq(24)).rename('Geração média (MW)')


def slice_days(data, start, end):
    return data[data[STAMP].ge(start) & data[STAMP].lt(end + pd.Timedelta(days=1))]


def initial_months(today):
    current = pd.Period(today, freq='M')
    return [str(current - 1), str(current)]
