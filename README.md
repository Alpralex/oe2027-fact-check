# Fact-checking a budget debate in 72 hours

A fact-check of Portugal's 2027 State Budget debate (27–28 Oct 2026), published by 31 Oct 2026 with about 50 claims checked (14 pre-debate claims and 8 topic dossiers in the current preview).
Every claim is checked against official sources (Eurostat, World Bank, the budget report), and the build fails if a claim has none.
Government forecasts get a computed verdict: they are compared with the range of independent institutions (Banco de Portugal, IMF, European Commission, OECD), not judged by hand.
The same rules apply to every party: the same verdict scale, and topic dossiers give each side an equal number of arguments for and against.
One JSON file per data type, one script (`montar.py`) that validates everything and builds a single-file HTML page.

## Checagem do debate do OE 2027 (pt-PT)

Adaptação da checagem Lula × Flávio (`../v3`) ao debate do Orçamento do Estado para 2027 na Assembleia da República (generalidade a 27 e 28/10/2026).

## Montar a página

```bash
cd oe2027
python3 -I scripts/conectores.py   # puxa as séries do Eurostat e grava dados/series.json (precisa de internet)
python3 -I scripts/montar.py       # valida os dados e gera index.html (a página publicada)
```

## Dados (`dados/`)

| Ficheiro | Conteúdo |
|---|---|
| `meta.json` | sessões, textos fixos, aviso de pré-visualização, verificadores, documentos, limitações |
| `fichas.json` | uma ficha por afirmação: `partido`, `orador`, `cargo`, `sessao` (0 antes do debate, 1 = 27/10, 2 = 28/10), `minuto`, `dar`, `tipo` (`facto` ou `previsao`), `cat` (só factos), `prev` (só previsões), `resumo`, `analise`, `subs`, `riscos`, `contra`, `dados`, `sources`, `agencias` |
| `partidos.json` | bancadas e o campo (`governo` ou `oposicao`) |
| `temas.json` | lista de temas |
| `dossies.json` | dossiês por tema: KPIs, gráficos (`linha`, `barras`, `prev`, `hbar`, `timeline`), contexto, `posicoes` por bancada, fontes |
| `series.json` | séries oficiais (geradas por `conectores.py`) |
| `previsoes.json` | previsões do Governo e das instituições por indicador e ano |

## Regras que o `montar.py` verifica

- Cada ficha tem partido, tema e sessão válidos, e pelo menos uma fonte oficial (N1 ou N1*).
- Factos do plenário têm o minuto do vídeo.
- O veredito das previsões é calculado, não escrito à mão: dentro do intervalo das instituições independentes é "Dentro do consenso"; fora dele é otimista ou pessimista consoante o lado, e "muito" para lá do limiar do indicador. Com menos de duas instituições, "Sem consenso suficiente".
- Nos dossiês, todas as bancadas com posição têm o mesmo número de argumentos a favor e de críticas.

## Estado (24/10/2026)

Pré-visualização com 6 fichas anteriores ao debate (5 metas do relatório e 1 declaração do Ministro das Finanças) e o dossiê de contas públicas. Os números do relatório e das instituições foram lidos em reproduções da imprensa e as séries do Eurostat pela API sem o conector; correr `conectores.py` substitui as séries pelos valores oficiais.
