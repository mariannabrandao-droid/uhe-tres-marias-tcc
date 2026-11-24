"""Entrada alternativa: mesma consulta livre, com ajustes de apresentação."""
import streamlit as st
import app_publica

_original = app_publica.configure_page

def configure_responsive(title):
    _original(title)
    st.markdown("""<style>
    .hero > div {min-width:0; overflow-wrap:anywhere}
    .hero img {flex-shrink:0; max-width:25%; height:auto}
    [data-testid="stColumn"] {min-width:0}
    [data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {max-width:100%; min-width:0}
    [data-testid="stMarkdownContainer"] img {max-width:100%; height:auto}
    [data-testid="stMetricValue"] {white-space:normal; overflow-wrap:anywhere}
    [data-testid="stLinkButton"] a {color:white!important}
    .stButton button,.stDownloadButton button,[data-testid="stLinkButton"] a {max-width:100%;white-space:normal;overflow-wrap:anywhere}
    @media(max-width:1200px){
      .block-container {padding:1.25rem 1.5rem 3rem!important}
    }
    @media(max-width:900px){
      .block-container {padding:1rem 1rem 3rem!important}
      [data-testid="stHorizontalBlock"] {flex-wrap:wrap!important}
      [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {flex:1 1 100%!important;width:100%!important;min-width:0!important}
      .hero {gap:12px;padding:16px!important}
      .hero h1 {font-size:1.4rem!important}
      .stPlotlyChart {padding:4px!important}
      [data-testid="stRadio"] [role="radiogroup"] {flex-wrap:wrap}
      [data-baseweb="tab-list"] {overflow-x:auto}
    }
    @media(max-width:480px){
      .block-container {padding:0.75rem 0.6rem 2rem!important}
      .hero h1 {font-size:1.15rem!important}
      .hero p {font-size:0.8rem!important}
      .hero img {width:48px}
    }
    </style>""",unsafe_allow_html=True)

if __name__ == "__main__":
    app_publica.configure_page = configure_responsive
    app_publica.main()
