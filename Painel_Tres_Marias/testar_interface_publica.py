"""Verifica as cinco etapas das duas entradas da consulta livre."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

PAGES = ['Configuração da área','Histórico e disponibilidade','Correlações hidroclimáticas','Limites e extensões','Síntese e exportação']

def main():
    for filename in ('app_publica.py','app_publica_responsiva.py'):
        at = AppTest.from_file(str(Path(__file__).with_name(filename)), default_timeout=60).run()
        assert not at.exception, [e.message for e in at.exception]
        assert list(at.sidebar.radio[0].options) == PAGES
        for page in PAGES:
            at.sidebar.radio[0].set_value(page).run()
            assert not at.exception, [e.message for e in at.exception]
            assert all(not b.label.startswith(('Avançar','Voltar')) for b in at.button)
        print(filename, ': cinco etapas conferidas.')

if __name__ == '__main__':
    main()
