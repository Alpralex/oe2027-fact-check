"""Puxa as séries oficiais dos dossiês e grava dados/series.json.
Uso: python3 -I scripts/conectores.py   (a partir da pasta oe2027; precisa de internet)
Só biblioteca padrão. Cada série guarda a fonte e a data em que foi puxada."""
import json, pathlib, urllib.request, urllib.parse, datetime

base = pathlib.Path(__file__).resolve().parent.parent
HOJE = datetime.date.today().isoformat()

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "checagem-oe2027"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def eurostat(dataset, **filtros):
    """Eurostat, API de disseminação (JSON-stat 2.0). Devolve {geo: {ano: valor}}."""
    q = [("format", "JSON"), ("lang", "PT")] + [(k, v) for k, vs in filtros.items() for v in (vs if isinstance(vs, list) else [vs])]
    js = get_json(f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}?" + urllib.parse.urlencode(q))
    dims, size = js["id"], js["size"]
    idx = {d: {v: k for k, v in js["dimension"][d]["category"]["index"].items()} for d in dims}
    out = {}
    for flat, val in js["value"].items():
        pos, rest = {}, int(flat)
        for d, n in zip(reversed(dims), reversed(size)):
            pos[d] = idx[d][rest % n]; rest //= n
        out.setdefault(pos["geo"], {})[pos["time"]] = val
    return out

def ine(varcd, dim1="T", **dims):
    """INE, API de indicadores (www.ine.pt/ine/json_indicador/pindica.jsp). Devolve a resposta em bruto:
    o formato varia por indicador, por isso cada série do INE é tratada à parte."""
    q = {"op": "2", "varcd": varcd, "Dim1": dim1, "lang": "PT", **dims}
    return get_json("https://www.ine.pt/ine/json_indicador/pindica.jsp?" + urllib.parse.urlencode(q))

def bpstat(serie_id):
    """Banco de Portugal, BPstat (API v1). Devolve {data: valor} de uma série pelo seu id."""
    js = get_json(f"https://bpstat.bportugal.pt/data/v1/series/?series_ids={serie_id}&lang=PT")
    return js

def serie(m, geos, nomes, fonte, desde=None):
    anos = sorted({a for g in geos for a in m.get(g, {}) if not desde or int(a) >= desde})
    return {"x": [int(a) for a in anos], **{g: [m.get(g, {}).get(a) for a in anos] for g in geos},
            "nomes": nomes, "fonte": f"{fonte} · puxado a {HOJE}", "provisorio": False}

GEO = ["PT", "EU27_2020"]; NOMES = {"PT": "Portugal", "EU27_2020": "UE-27"}
S = {}
m = eurostat("gov_10dd_edpt1", unit="PC_GDP", sector="S13", na_item="GD", geo=GEO)
S["divida"] = serie(m, GEO, NOMES, "Eurostat, gov_10dd_edpt1 (dívida bruta consolidada, % do PIB)", 1995)
m = eurostat("gov_10dd_edpt1", unit="PC_GDP", sector="S13", na_item="B9", geo=GEO)
S["saldo"] = serie(m, GEO, NOMES, "Eurostat, gov_10dd_edpt1 (saldo das administrações públicas, % do PIB)", 2000)
m = eurostat("nama_10_gdp", unit="CLV_PCH_PRE", na_item="B1GQ", geo=GEO)
S["pib"] = serie(m, GEO, NOMES, "Eurostat, nama_10_gdp (PIB em volume, variação anual)", 2000)
m = eurostat("une_rt_a", age="Y15-74", sex="T", unit="PC_ACT", geo=GEO)
S["desemprego"] = serie(m, GEO, NOMES, "Eurostat, une_rt_a (taxa de desemprego, 15–74 anos)", 2005)
m = eurostat("prc_hicp_aind", unit="RCH_A_AVG", coicop="CP00", geo=["PT", "EA20"])
S["ihpc"] = serie(m, ["PT", "EA20"], {"PT": "Portugal", "EA20": "Área do euro"}, "Eurostat, prc_hicp_aind (IHPC, variação média anual)", 2005)
m = eurostat("prc_hpi_a", purchase="TOTAL", unit="RCH_A_AVG", geo=GEO)
S["habitacao_precos"] = serie(m, GEO, NOMES, "Eurostat, prc_hpi_a (preços da habitação, variação anual)", 2010)

# Ranking da redução da dívida entre os dois últimos anos, para a ficha F01
m = eurostat("gov_10dd_edpt1", unit="PC_GDP", sector="S13", na_item="GD", sinceTimePeriod="2015")
ult = max(a for a, v in m["PT"].items() if v is not None)
ant = str(int(ult) - 1)
var = sorted(((g, round(v[ult] - v[ant], 1)) for g, v in m.items() if len(g) == 2 and v.get(ult) is not None and v.get(ant) is not None), key=lambda x: x[1])
S["divida_ue_var"] = {"x": [g for g, _ in var], "PT": [v for _, v in var], "nomes": {"PT": f"Variação {ant}→{ult}, p.p."},
                      "fonte": f"Eurostat, gov_10dd_edpt1 · puxado a {HOJE}", "provisorio": False}

(base / "dados" / "series.json").write_text(json.dumps(S, ensure_ascii=False, indent=1), encoding="utf-8")
for k, v in S.items():
    print(f"{k}: {v['x'][0]}–{v['x'][-1]} ({len(v['x'])} pontos)")
print("Posição de Portugal na redução da dívida:", [g for g, _ in var].index("PT") + 1, "de", len(var))
