"""Reproduz a comparação de dois outubros e as regras de atualização do ONS."""
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd

import operacao_ons as ons
from defluencia_diurna import analyze


def main():
    hourly = ons.read('horario')
    daily = ons.read('diario')
    for month, expected in [('2025-10', (30, 29)), ('2026-10', (31, 8))]:
        start = pd.Timestamp(month + '-01')
        end = start + pd.offsets.MonthEnd()
        hours, result = analyze(ons.slice_days(hourly, start, end), ons.slice_days(daily, start, end),
                                300, start, end)
        assert (result.elegivel.sum(), result.diverge.sum()) == expected
        excluded = result[~result.elegivel]
        assert excluded.maior_sequencia.isna().all()
        if month == '2025-10':
            assert excluded.loc['2025-10-22', 'horas_validas'] == 7
        else:
            case = result.loc['2026-10-22']
            assert (case.media_diaria, case.minimo_diurno, case.maior_sequencia) == (450, 164, 5)
            assert int(hours.abaixo.sum()) == 95
        print(f'{month} · {expected[1]}/{expected[0]} dias elegíveis sinalizados')
    print('22/10/2026 · média 450, mínimo diurno 164 m³/s e 5 horas consecutivas abaixo de 300.')

    resource = ons.Resource('geracao', '2026-11')
    mock_raw = StringIO('id_ons;din_instante;val_geracao\nMGTMAR;2026-11-01 00:00:00;130\n'
                        'CJU_MGJSNU;2026-11-01 00:00:00;1\n')
    selected = ons.extract(resource, mock_raw)
    assert list(selected.val_geracao) == [130]
    assert ons.day_mean_generation(selected).isna().all()
    sample = pd.DataFrame({ons.STAMP: pd.date_range('2026-11-01', periods=24, freq='h'),
                           'val_geracao': [100] * 24})
    assert ons.day_mean_generation(sample).iloc[0] == 100
    with TemporaryDirectory() as name:
        directory = Path(name)
        bundled = ons.read('geracao')
        original = bundled[bundled[ons.STAMP].dt.month.eq(11)].drop(columns='consulta_utc')
        revised = original.copy()
        revised['val_geracao'] += 1
        with patch('operacao_ons.resources', return_value=[resource]):
            with patch('operacao_ons.fetch', return_value=revised):
                status = ons.refresh(['2026-11'], directory)
            assert 'registros recebidos' in status.Resultado.iloc[0]
            result = ons.read('geracao', directory)
            assert len(result) == len(bundled) and not result[ons.STAMP].duplicated().any()
            cache = directory / resource.name
            content = cache.read_bytes()
            with patch('operacao_ons.fetch', return_value=revised.iloc[1:]):
                status = ons.refresh(['2026-11'], directory)
            assert status.Resultado.str.startswith('Falha').all() and cache.read_bytes() == content
            with patch('operacao_ons.fetch', side_effect=OSError('offline')):
                status = ons.refresh(['2026-11'], directory)
            assert status.Resultado.str.startswith('Falha').all() and cache.read_bytes() == content
    print('Geração: identificador exato, média de 24 horas, cache atualizado e preservado em falhas testados.')


if __name__ == '__main__':
    main()
