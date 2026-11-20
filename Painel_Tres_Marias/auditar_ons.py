"""Confronta o recorte empacotado com os CSVs oficiais e recalcula o cenário."""
import argparse
import hashlib
from pathlib import Path

import pandas as pd

from defluencia_diurna import DATA

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('diario', type=Path)
parser.add_argument('horario', type=Path)
args = parser.parse_args()

sources = {}
for kind, path in [('diario', args.diario), ('horario', args.horario)]:
    local = pd.read_csv(DATA / f'ons_{kind}_sftmar_2026-10.csv')
    raw = pd.read_csv(path, sep=';', usecols=local.columns.to_list())
    cut = raw[raw.id_reservatorio.eq('SFTMAR') & raw.din_instante.str.startswith('2026-10')]
    cut = cut.sort_values('din_instante').reset_index(drop=True)
    pd.testing.assert_frame_equal(local, cut, check_dtype=False)
    assert not cut.din_instante.duplicated().any()
    sources[kind] = cut
    print(kind, 'registros', len(cut), 'SHA256 do CSV original', hashlib.sha256(path.read_bytes()).hexdigest())

# Horas-fim 07:00–18:00, correspondentes aos 12 intervalos iniciados às 06:00–17:00.
hourly = sources['horario']
ends = pd.to_datetime(hourly.din_instante)
diurnal = hourly[ends.dt.hour.between(7, 18)].assign(dia=ends.dt.strftime('%Y-%m-%d'))
daily = sources['diario'].set_index('din_instante')
by_day = diurnal.groupby('dia').val_vazaodefluente.agg(['min', 'count'])
assert by_day.index.equals(daily.index) and by_day['count'].eq(12).all()
missed = daily.val_vazaodefluente.ge(300) & by_day['min'].lt(300)
print('Registros diurnos abaixo:', int(diurnal.val_vazaodefluente.lt(300).sum()), 'de', len(diurnal))
print('Dias com registro diurno abaixo:', int(by_day['min'].lt(300).sum()), 'de', len(by_day))
print('Dias com média >= 300 e mínimo diurno < 300:', int(missed.sum()), 'de', len(daily), list(daily.index[missed]))
assert int(missed.sum()) == 8
example = '2026-10-22'
print(example, 'média', daily.loc[example, 'val_vazaodefluente'], 'mínimo diurno', by_day.loc[example, 'min'])
assert (daily.loc[example, 'val_vazaodefluente'], by_day.loc[example, 'min']) == (450, 164)
sar = pd.read_csv(Path(__file__).resolve().parent / 'ANA_Etapa02/entradas/sar_diario.csv').set_index('data')
overlap = daily.join(sar[['vazao_natural_m3s']], how='inner')
gap = (overlap.val_vazaonatural - overlap.vazao_natural_m3s).abs()
print('Vazão natural, dias em comum', len(gap), 'dias com diferença', int(gap.gt(1e-9).sum()), 'diferença máxima', round(gap.max(), 2))
