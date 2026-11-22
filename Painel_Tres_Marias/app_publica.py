"""Interface de consulta hidroclimática da UHE Três Marias."""
import streamlit as st

from explorar_ana import explorer
from painel import configure_page, context, load_history, operations, scenarios, science, synthesis


def overview():
    st.header('Consulte os dados de Três Marias')
    st.write(
        'Explore as séries mensais de chuva e vazão, a operação diária da usina '
        'e as horas de menor liberação de água. Use o menu para escolher uma análise.'
    )
    st.markdown(
        '- **Histórico hidroclimático** reúne postos, sazonalidade, baixas vazões, '
        'associações climáticas e previsão experimental. Você também pode pesquisar estações da ANA de outras bacias.\n'
        '- **Operação diária** mostra entradas, saídas e volume útil do reservatório.\n'
        '- **Defluência por dia e hora** permite investigar os intervalos diurnos.\n'
        '- **Dados e reprodução** reúne fontes, métodos e downloads.'
    )


def history():
    source = st.radio('Área de consulta', ('Três Marias · exemplo', 'Outra localização · ANA'),
                      horizontal=True, key='public_history_source')
    if source == 'Três Marias · exemplo':
        science(*load_history(), defense=False)
    else:
        explorer()


def glossary():
    st.header('Glossário')
    terms = {
        'Vazão natural': 'Estimativa da vazão sem os efeitos de intervenções humanas consideradas na reconstituição.',
        'Afluência': 'Vazão que entra no reservatório.',
        'Defluência': 'Vazão que sai da usina, registrada no ponto de descarga.',
        'Vazão turbinada e vertida': 'Parcelas que passam pelas turbinas e pelos vertedouros, respectivamente.',
        'Volume útil': 'Parcela de armazenamento disponível para operação, expressa no painel em porcentagem.',
        'Curva de permanência': 'Relaciona uma vazão à frequência com que ela é igualada ou superada na amostra.',
        'ZCAS': 'Zona de Convergência do Atlântico Sul, faixa persistente de nebulosidade e chuva.',
        'Bloqueio atmosférico': 'Padrão persistente da circulação atmosférica que interfere no deslocamento dos sistemas meteorológicos.',
        'Defasagem': 'Distância em meses entre os registros comparados. Em chuva × vazão, +2 associa chuva de t a vazão de t+2.',
        'MAE e NSE': 'O MAE mede o erro absoluto médio em m³/s. A eficiência de Nash–Sutcliffe compara o erro quadrático ao de uma referência baseada na média observada.',
    }
    for term, definition in terms.items():
        st.markdown(f'**{term}**')
        st.write(definition)


def reproducibility():
    synthesis()
    st.subheader('Como reproduzir e atualizar as análises')
    st.write('O painel usa um acervo de referência versionado. Os recortes de outubro usam os arquivos preservados com o estudo.')
    st.markdown(
        'Consulte o README para instalar as dependências, executar a auditoria da previsão '
        'e verificar os arquivos antes de atualizar uma base. '
        '[Repositório e documentação](https://github.com/mariannabrandao-droid/uhe-tres-marias-tcc)'
    )


def main():
    configure_page('Três Marias | Consulta pública')
    pages = {
        'Visão geral': overview,
        'Usina e contexto': context,
        'Histórico hidroclimático': history,
        'Operação diária': operations,
        'Defluência por dia e hora': scenarios,
        'Dados e reprodução': reproducibility,
        'Glossário': glossary,
    }
    selected = st.sidebar.radio('Páginas', tuple(pages), key='public_page')
    pages[selected]()
    st.caption('Marianna Brandão Ferreira · Universidade Federal Fluminense')


if __name__ == '__main__':
    main()
