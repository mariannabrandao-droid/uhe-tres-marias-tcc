"""Registra cobertura das séries usadas na edição de defesa."""
import pandas as pd

from analise_defesa import BLOCKS, ZCAS, climate_series
from hidroclima import DATA, LABELS, SAR, coverage, read_series, unit
from preparar_dados import preparar_dados

CODES = {'chuva_barramento_mm': '01845009', 'chuva_andrequice_mm': '01845032',
         'chuva_mesquita_mm': '01944060', 'vazao_jusante_m3s': '41020002', 'vazao_indaia_m3s': '40963000'}


def main():
    preparar_dados()
    frame = read_series().drop(columns=[*ZCAS, 'dias_bloqueio_total']).join(climate_series()[0])
    rows = []
    for key, series in frame.items():
        info = coverage(series)
        source = 'SAR ANA' if key in SAR else 'HidroWeb ANA' if key in CODES else 'Campos fornecidos'
        rows.append({'serie': LABELS.get(key, key), 'fonte': source, 'codigo': CODES.get(key, ''),
                     'unidade': 'dias/mês' if key in BLOCKS else unit(key), 'frequencia': 'Mensal',
                     'origem': 'Diária', 'início': info['inicio'], 'fim': info['fim'], 'válidos': info['n'],
                     'lacunas internas': info['meses_calendario'] - info['n']})
    for frequency, valid in [('Diária', 31), ('Horária', 744)]:
        rows.append({'serie': 'Defluência do reservatório', 'fonte': 'ONS', 'codigo': 'SFTMAR',
                     'unidade': 'm³/s', 'frequencia': frequency, 'origem': frequency,
                     'início': '2026-10-01', 'fim': '2026-10-31', 'válidos': valid, 'lacunas internas': 0})
    pd.DataFrame(rows).to_csv(DATA / 'inventario_series.csv', sep=';', index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    main()
