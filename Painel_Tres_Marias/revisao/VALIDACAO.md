# Verificação da revisão

Execução local em instalação limpa a partir dos arquivos rastreados, com Python 3.12, Streamlit 1.52.2, Plotly 6.5.0 e Chromium. As duas aplicações extraíram e leram o acervo compartilhado. As cinco rotinas de teste e auditoria terminaram com código zero.

| Verificação | Resultado |
| --- | --- |
| `testar_calculos_defesa.py` | Agregação mensal SAR, permanência, sequências, associações, quatro defasagens, janela diurna e cenários de lacuna e igualdade. |
| `testar_operacao.py` | 29/30 e 8/31 divergências, caso de 22/10/2026, geração de 24 horas, cache e recuperação de falhas. |
| `auditar_previsao.py` | Backtest, métricas e projeções reproduzidos dentro da tolerância numérica. Todos os treinamentos Ridge terminaram antes da origem e o alfa pertence a {1, 10, 100}. |
| `testar_interface_defesa.py` | Sete páginas, quatro temas no histórico, referências a 19 figuras, ações avançar e voltar, seletor do diagnóstico e fallback de boletins. |
| `testar_interface_publica.py` | Sete páginas em navegação livre, quatro temas do histórico e troca do mês no diagnóstico. |
| Chromium, 1440 × 1000 | Todas as páginas e temas abriram sem exceções Streamlit ou erros JavaScript. O CSV de diagnóstico foi baixado nas duas interfaces. |
| Chromium, 390 × 844 | Os dois inícios carregaram sem rolagem horizontal. A barra lateral abre sob demanda em tela estreita. |

As capturas mostram o topo das 14 páginas e das seis subseções adicionais do histórico, mais as duas capas em largura móvel. O percurso automatizado de navegação levou aproximadamente 12 s na defesa e 11 s na consulta, incluindo pausas e capturas. Esses tempos descrevem o percurso de teste local. O desempenho da implantação depende da infraestrutura e do cliente.

[Capturas da defesa e da versão pública](capturas/)

## Escopo pendente de verificação

- O endereço do Streamlit Community Cloud solicitou autenticação. A branch, o arquivo de entrada e o commit em execução no endereço publicado permanecem pendentes de confirmação administrativa.
- O confronto físico a jusante depende da série horária consistida do posto 41020002, além da estimativa de tempo de viagem.
- A validação móvel cobriu as duas telas iniciais. Testes com leitores de tela, avaliação integral WCAG e desempenho sob carga ficam fora dos resultados verificados.
