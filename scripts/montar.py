"""Monta a página da checagem do OE 2027: template + dados.
Uso: python3 -I scripts/montar.py   (a partir da pasta oe2027)"""
import json, pathlib
base = pathlib.Path(__file__).resolve().parent.parent
d = base / "dados"
L = lambda n: json.loads((d / n).read_text(encoding="utf-8"))
CATS_F = {"V", "VR", "I", "E", "F", "N", "NV"}
TIERS = {"N1", "N1*", "N2", "N3", "N4"}

meta, fichas, partidos, temas, dossies, series, prev = (L(n) for n in ("meta.json", "fichas.json", "partidos.json", "temas.json", "dossies.json", "series.json", "previsoes.json"))
PK = {p["k"] for p in partidos}
TK = {t[0] for t in temas}

def classifica(ind, ano):
    """Mesma regra do JavaScript: intervalo das instituições independentes."""
    I, row = prev["indicadores"][ind], prev["valores"][ind][ano]
    vals = [v for k, v in row.items() if k != "GOV" and v is not None]
    if len(vals) < 2: return "SC"
    lo, hi, g, lim = min(vals), max(vals), row["GOV"], I.get("limiar", 0.5)
    if lo - 1e-9 <= g <= hi + 1e-9: return "C"
    acima = g > hi; dist = g - hi if acima else lo - g
    bom = (I["bom"] == "alto") == acima
    return ("MO" if dist > lim + 1e-9 else "O") if bom else ("MP" if dist > lim + 1e-9 else "P")

ids = [f["id"] for f in fichas]
assert len(ids) == len(set(ids)), "ID repetido"
for f in fichas:
    assert f["partido"] in PK, f"Partido desconhecido: {f['id']} {f['partido']}"
    assert f["tema"] in TK, f"Tema desconhecido: {f['id']} {f['tema']}"
    assert str(f["sessao"]) in meta["sessoes"], f"Sessão inválida: {f['id']}"
    if f["tipo"] == "previsao":
        p = f["prev"]; assert p["ind"] in prev["valores"] and p["ano"] in prev["valores"][p["ind"]], f"Previsão sem dados: {f['id']}"
        f["cat_calculada"] = classifica(p["ind"], p["ano"])
    else:
        assert f["tipo"] == "facto" and f["cat"] in CATS_F, f"Categoria inválida: {f['id']}"
        assert f.get("sessao") == 0 or f.get("minuto"), f"Falta o minuto do vídeo: {f['id']}"
    for s in f.get("sources", []):
        assert s["tier"] in TIERS, f"Nível inválido: {f['id']} {s['tier']}"
    assert any(s["tier"] in ("N1", "N1*") for s in f.get("sources", [])), f"Sem fonte oficial: {f['id']}"
for k, D in dossies.items():
    assert k in TK, f"Dossiê sem tema: {k}"
    for c in D["charts"]:
        if c["t"] in ("linha", "barras"): assert c["serie"] in series, f"Série em falta: {c['serie']}"
    pos = D.get("posicoes", [])
    if pos:  # equilíbrio: o mesmo número de argumentos e de críticas para todas as bancadas
        assert len({len(p["pro"]) for p in pos}) == 1 and len({len(p["contra"]) for p in pos}) == 1, f"Número de argumentos desigual em {k}"

safe = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
html = (base / "pagina-template.html").read_text(encoding="utf-8")
for ph, obj in [("__META__", meta), ("__FICHAS__", fichas), ("__PARTIDOS__", partidos), ("__TEMAS__", temas), ("__DOSSIES__", dossies), ("__SERIES__", series), ("__PREVISOES__", prev)]:
    assert ph in html, ph
    html = html.replace(ph, safe(obj))
out = base / "index.html"
out.write_text(html, encoding="utf-8")
nf = sum(f["tipo"] != "previsao" for f in fichas)
print(f"{len(fichas)} fichas ({nf} factos, {len(fichas)-nf} previsões) · {len(dossies)} dossiês -> {out.name} ({len(html)//1024} KB)")
for f in fichas:
    if "cat_calculada" in f: print(f"  {f['id']} {f['prev']['ind']} {f['prev']['ano']}: {f['cat_calculada']}")
