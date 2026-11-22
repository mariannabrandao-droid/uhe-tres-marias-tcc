# Inventário de arquivos e roteiro de defesa

Base auditada no GitHub em `91e07b19a0c26889c61db24e74802dcf892bf629`, com 25 arquivos rastreados e seis grupos de entradas no acervo compactado. A classificação abaixo indica o papel dos arquivos. A revisão preserva todos os arquivos da base.

| Arquivo | Decisão e justificativa |
| --- | --- |
| `app.py` | Corrigido. Sete páginas, configuração reaproveitável, numeração final das figuras, permanência interativa, controles climáticos e explicações de previsão e diagnóstico. |
| `app_publica.py` | Adicionado. Menu livre, glossário e acesso aos mesmos resultados, fontes e downloads. |
| `analise_defesa.py` | Corrigido. Ano hidrológico do mês-alvo na retirada por ano. |
| `auditar_previsao.py` | Adicionado. Entrada executável para reproduzir e comparar os três CSVs históricos, com diretório de saída opcional. |
| `requirements-auditoria.txt` | Adicionado. scikit-learn isolado nas dependências de reprodução. |
| `README.md` | Corrigido. Execução, testes, acervo, atualização manual e publicação pelas duas entradas. |
| `testar_calculos_defesa.py` | Ampliado. Limites da permanência e passagem de ano hidrológico em quatro defasagens. |
| `testar_interface_defesa.py` | Ampliado. Conferência da numeração final das figuras. |
| `testar_interface_publica.py` | Adicionado. Navegação e fluxo operacional da consulta pública. |
| `revisao/CORRESPONDENCIA_TCC.md` | Adicionado. Matriz de seções, métodos, fontes, resultados, código e telas. |
| `revisao/PARECER.md` | Adicionado. Resultados reproduzidos, interpretação visual e pontos de revisão do TCC. |
| `revisao/INVENTARIO_E_ROTEIRO.md` | Adicionado. Decisões arquivo por arquivo e roteiro de 15 minutos. |
| `revisao/VALIDACAO.md` e `revisao/capturas/` | Adicionados. Evidência da validação local. |
| `INICIAR_WINDOWS.bat` | Mantido. Atalho da defesa e instalação no Windows. |
| `LEIA_PRIMEIRO.txt` | Mantido como orientação antiga do pacote. O README descreve as duas entradas. |
| `auditar_ons.py` | Mantido. Confronto com arquivos ONS originais fornecidos como parâmetros. |
| `dados_painel.zip` | Mantido idêntico. Arquivo canônico de distribuição, com dados, figuras, documentação anterior e scripts históricos. |
| `defluencia_diurna.py` | Mantido. Conversão de carimbos horários e comparação diária–horária. |
| `evidencia_jusante.py` | Mantido. Validação do CSV importado e pareamento exploratório. |
| `figuras_defesa.py` | Mantido como referência de visualização. |
| `figuras_tcc.py` | Mantido. Séries e constantes usadas nos gráficos e no calendário climático. |
| `fontes_https.py` | Mantido. Acesso HTTPS usado nas consultas externas. |
| `hidroclima.py` | Mantido. Cobertura, leitura das séries, quantis e unidades. |
| `informes_ana.py` | Mantido. Consulta a informes e fallback arquivado. |
| `inventariar_series.py` | Mantido. Geração de inventário de cobertura e séries. |
| `mapas.py` | Mantido. Mapas cadastrais e esquema climático. |
| `operacao_ons.py` | Mantido. Leitura, cache, atualizações explícitas e agregação de geração. |
| `pirapora.py` | Mantido. Série contextual da estação Pirapora Barreiro. |
| `postos_defesa.py` | Mantido. Cadastro, seleção e cobertura de postos. |
| `preparar_dados.py` | Mantido. Extração do ZIP pelo hash e substituição atômica de cada arquivo. |
| `requirements.txt` | Mantido. Dependências de execução para as duas interfaces. |
| `secoes_tcc.py` | Mantido como implementação histórica de blocos interativos. |
| `testar_operacao.py` | Mantido. Diagnóstico dos dois outubros, geração, cache e recuperação de falhas. |

O ZIP contém `ANA_Etapa02/` (66 arquivos, entradas, tratamento e resultados), `assets/` (33, figuras e camadas), `dados_ana/` (1, fonte arquivada), `dados_ons/` (17, recortes e inventários), `docs/` (24, relatórios e registros de edições anteriores) e `historico_desenvolvimento/` (36, modelos, documentação e comparativos). As figuras com índices 13–19 no arquivo de origem são referências 15–21 no TCC final. O download da matriz no painel aponta à matriz desta revisão. As versões e registros anteriores permanecem dentro do ZIP para reproduzir a evolução do trabalho.

## Percurso da defesa em 15 minutos

| Tempo | Tela | Condução |
| --- | --- | --- |
| 0–1 min | 00 · Capa | Apresentar o problema e indicar a sequência do estudo. |
| 1–3 min | 01 · Usina | Localizar a usina, o ponto de controle e a discussão de vazão mínima. |
| 3–7 min | 02 · Histórico | Passar pelos postos, 16/81 meses baixos, associação em +2 e comparação de erros da previsão. |
| 7–9 min | 03 · Operação diária | Relacionar a entrada, a descarga e a evolução do volume útil. |
| 9–13 min | 04 · Defluência | Comparar os dois outubros e abrir 22/10/2026. Explicar a janela de 12 horas e o alcance da evidência a jusante. |
| 13–14 min | 05 · Rastreabilidade | Mostrar fontes, cobertura e reprodução. |
| 14–15 min | 06 · Conclusão | Sintetizar a contribuição da plataforma e as limitações da previsão e do diagnóstico. |
