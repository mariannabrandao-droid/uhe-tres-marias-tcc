"""Reexecuta o protocolo histórico e confere os resultados arquivados."""
import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd

from preparar_dados import preparar_dados

ROOT = Path(__file__).resolve().parent
HISTORY = ROOT / 'historico_desenvolvimento'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saida', type=Path, help='Diretório separado para exportar os CSVs recalculados.')
    args = parser.parse_args()
    preparar_dados()

    # Os scripts históricos mantêm os imports entre arquivos da pasta original.
    sys.path.insert(0, str(HISTORY))
    try:
        from calibracao_final import ALPHAS
        from previsao import run

        assert ALPHAS == (1., 10., 100.)
        backtest, metrics, projections = run()
    finally:
        sys.path.remove(str(HISTORY))

    assert backtest.treino_fim.lt(backtest.origem).all()
    assert backtest.climatologia_fim.eq(backtest.origem).all()
    assert backtest.loc[backtest.modelo.eq('Ridge'), 'alpha'].isin(ALPHAS).all()
    audit = backtest.query("etapa == 'Auditoria' and horizonte in (1, 2)")
    expected_dates = set(pd.date_range('2025-01-01', '2026-09-01', freq='MS'))
    for _, group in audit.groupby(['horizonte', 'modelo']):
        assert len(group) == len(expected_dates) and set(group.alvo) == expected_dates

    generated = {'backtest': backtest, 'metricas': metrics, 'projecoes': projections}
    for name, frame in generated.items():
        reference = pd.read_csv(HISTORY / 'resultados_entrega' / f'{name}.csv')
        actual = frame.copy()
        for column in frame.select_dtypes(include='datetime').columns:
            actual[column] = actual[column].dt.strftime('%Y-%m-%d')
        pd.testing.assert_frame_equal(actual, reference, check_dtype=False, atol=1e-8, rtol=1e-9)

    global_audit = metrics.query("etapa == 'Auditoria' and recorte == 'Todos' and horizonte in (1, 2)")
    mae = global_audit.pivot(index='modelo', columns='horizonte', values='MAE')
    np.testing.assert_allclose(mae.loc[['Climatologia', 'Ridge', 'Persistência']].round(2),
                               [[200.35, 200.35], [220.86, 338.17], [247.76, 405.55]])
    print(global_audit[['horizonte', 'modelo', 'n', 'MAE', 'NSE']].to_string(index=False))
    if args.saida:
        target = args.saida.resolve()
        if target == ROOT or ROOT in target.parents:
            parser.error('Use uma pasta de saída fora da árvore do painel.')
        target.mkdir(parents=True, exist_ok=True)
        for name, frame in generated.items():
            frame.to_csv(target / f'{name}.csv', index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    main()
