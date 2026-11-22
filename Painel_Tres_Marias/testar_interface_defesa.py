"""Verifica navegação, as figuras do PDF e resultados na interface Streamlit."""
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


def main():
    at = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=60).run()

    def check(figures=()):
        assert not at.exception, [entry.message for entry in at.exception]
        rendered = {item.value.split(' · ')[0] for item in at.markdown if item.value.startswith('**Figura ')}
        expected = {f'**Figura {n} do TCC' for n in figures}
        assert rendered == expected, (rendered, expected)

    check()
    next(b for b in at.button if b.label == 'Iniciar apresentação').click().run()
    check((2, 3, 10))
    pages = at.sidebar.radio[0].options
    next(b for b in at.button if b.label == f'Avançar · {pages[2][5:]}').click().run()
    check((12,))
    topics = at.radio(key='science_topic').options
    for topic, figures in zip(topics[1:], ((1, 4, 9, 15), (5, 6, 7, 8, 16), (17, 18, 19))):
        next(b for b in at.button if b.label == f'Avançar · {topic}').click().run()
        assert at.radio(key='science_topic').value == topic
        check(figures)
    assert at.dataframe[0].value.shape == (6, 6), at.dataframe[0].value

    next(b for b in at.button if b.label == f'Avançar · {pages[3][5:]}').click().run()
    check((20,))
    assert {'186,76 m³/s', '-5,24 m³/s'} <= {metric.value for metric in at.metric}
    with patch('informes_ana.fetch_bulletins', side_effect=OSError('Falha simulada')):
        next(b for b in at.button if b.label == 'Buscar boletins recentes da ANA').click().run()
    check((20,))
    assert any('última lista disponível' in warning.value for warning in at.warning)

    at.sidebar.radio[0].set_value(pages[4]).run()
    check((11, 21))
    comparison = at.dataframe[0].value
    assert comparison.iloc[3, 1:].tolist() == [29, 8]
    at.selectbox[0].select('2025-10').run()
    check((11, 21))

    for page in pages[5:]:
        at.sidebar.radio[0].set_value(page).run()
        check()
    print('Sete páginas e quatro etapas do histórico; 19 figuras, tabelas, seletores e fallback ANA conferidos.')


if __name__ == '__main__':
    main()
