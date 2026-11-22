"""Verifica navegação, os gráficos calculados e resultados na interface Streamlit."""
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


def main():
    at = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=60).run()

    def check(minimum_charts=0):
        assert not at.exception, [entry.message for entry in at.exception]
        assert len(at.get('plotly_chart')) >= minimum_charts

    check()
    next(b for b in at.button if b.label == 'Iniciar apresentação').click().run()
    check(3)
    pages = at.sidebar.radio[0].options
    next(b for b in at.button if b.label == f'Voltar · {pages[0][5:]}').click().run()
    check()
    next(b for b in at.button if b.label == 'Iniciar apresentação').click().run()
    check(3)
    next(b for b in at.button if b.label == f'Avançar · {pages[2][5:]}').click().run()
    check(2)
    topics = at.radio(key='science_topic').options
    for topic, figures in zip(topics[1:], (4, 4, 2)):
        next(b for b in at.button if b.label == f'Avançar · {topic}').click().run()
        assert at.radio(key='science_topic').value == topic
        check(figures)
        if topic == 'Clima e associações':
            at.radio(key='correlation_mode').set_value('Valores originais').run()
            next(box for box in at.selectbox if box.label == 'Variável-resposta dos índices climáticos').select('Vazão natural SAR').run()
            next(box for box in at.selectbox if box.label == 'Defasagem dos índices (meses)').select(2).run()
            check(figures)
            result = next(item.value for item in at.dataframe if 'Sensibilidade mín.' in item.value and len(item.value) == 10)
            assert result.Defasagem.eq(2).all()
    assert at.dataframe[0].value.shape == (6, 6), at.dataframe[0].value
    at.radio[1].set_value(2).run()
    check(2)

    next(b for b in at.button if b.label == f'Avançar · {pages[3][5:]}').click().run()
    check(2)
    assert {'186,76 m³/s', '-5,24 m³/s'} <= {metric.value for metric in at.metric}
    with patch('painel.fetch_bulletins', side_effect=OSError('Falha simulada')):
        next(b for b in at.button if b.label == 'Buscar boletins recentes da ANA').click().run()
    check(2)
    assert any('última lista disponível' in warning.value for warning in at.warning)

    at.sidebar.radio[0].set_value(pages[4]).run()
    check(2)
    comparison = at.dataframe[0].value
    assert comparison.iloc[3, 1:].tolist() == [29, 8]
    assert {'450 m³/s', '164 m³/s', '5 h'} <= {metric.value for metric in at.metric}
    at.number_input[0].set_value(0.).run()
    check(2)
    assert at.dataframe[0].value.iloc[3, 1:].tolist() == [0, 0]
    at.number_input[0].set_value(300.).run()
    at.selectbox[0].select('2025-10').run()
    check(2)

    for page in pages[5:]:
        at.sidebar.radio[0].set_value(page).run()
        check()
    print('Sete páginas e quatro etapas do histórico; gráficos calculados, tabelas, seletores e fallback ANA conferidos.')


if __name__ == '__main__':
    main()
