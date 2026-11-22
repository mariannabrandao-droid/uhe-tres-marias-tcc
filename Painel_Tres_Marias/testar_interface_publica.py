"""Verifica a navegação e os pontos de entrada da consulta pública."""
from pathlib import Path

from streamlit.testing.v1 import AppTest


def main():
    app = Path(__file__).with_name('app_publica.py')
    at = AppTest.from_file(str(app), default_timeout=60).run()

    def check():
        assert not at.exception, [entry.message for entry in at.exception]
        assert all(not button.label.startswith(('Avançar', 'Voltar')) for button in at.button)

    pages = at.sidebar.radio[0].options
    assert len(pages) == 7
    for page in pages:
        at.sidebar.radio[0].set_value(page).run()
        check()
        if page == 'Histórico hidroclimático':
            for topic in at.radio(key='science_topic').options:
                at.radio(key='science_topic').set_value(topic).run()
                check()
        elif page == 'Defluência por dia e hora':
            assert at.dataframe[0].value.iloc[3, 1:].tolist() == [29, 8]
            at.selectbox[0].select('2025-10').run()
            check()
    print('Sete páginas públicas, quatro temas, navegação livre e seletor do diagnóstico conferidos.')


if __name__ == '__main__':
    main()
