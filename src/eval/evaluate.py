"""Evaluation harness: score any generated test plan against gold data.

Metrics
- structure    : share of REQUIRED canonical sections present with real content (deterministic)
- coverage     : share of must-test BRD facts covered by the plan (LLM judge + evidence check)
- faithfulness : share of project-specific requirement claims backed by cited BRD/architecture lines
- similarity   : per-section closeness to the human reference plan (LLM judge) + embedding cosine (secondary)
- overall      : (0.25*structure + 0.45*coverage + 0.30*similarity) * faithfulness
"""
import re
import json
from difflib import SequenceMatcher

import numpy as np
import pandas as pd

from src.common.config import PROCESSED, GOLD, TEMPLATES, ask_json, embed

SCHEMA = json.loads((TEMPLATES / "test_plan_schema.json").read_text(encoding="utf-8"))
SECTIONS = {s["key"]: s["description"] for s in SCHEMA["sections"]}
REQUIRED = [s["key"] for s in SCHEMA["sections"] if s["required"]]


# ---------------------------------------------------------------- loading
def project_dir(prefix, root=PROCESSED):
    return next(p for p in root.glob("*/*") if p.name.startswith(prefix))


def load_inputs(prefix):
    """Everything the evaluator needs for one project."""
    p, g = project_dir(prefix), project_dir(prefix, GOLD)
    return {"name": p.name,
            "brd": (p / "brd.md").read_text(encoding="utf-8"),
            "arch": (p / "architecture.md").read_text(encoding="utf-8"),
            "gold": json.loads((g / "gold_testplan.json").read_text(encoding="utf-8")),
            "facts": json.loads((g / "facts.json").read_text(encoding="utf-8"))["facts"]}


# ---------------------------------------------------------------- helpers
def _norm(s):
    s = s.lower().replace("–", "-").replace("—", "-").replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[|*#`]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def quote_score(quote, source):
    """1.0 if quote is in source; else share of the quote found as one continuous block."""
    q, src = _norm(quote), _norm(source)
    if not q:
        return 0.0
    if q in src:
        return 1.0
    m = SequenceMatcher(None, src, q, autojunk=False).find_longest_match(0, len(src), 0, len(q))
    return m.size / len(q)


def _heading(line, allow_plain):
    """Return (level, text) if the line is a heading, else None."""
    s = line.strip()
    m = re.match(r"^(#{1,4})\s+(.+)$", s)                                  # markdown heading
    if m:
        return len(m.group(1)), m.group(2).strip(" *")
    m = re.match(r"^\*\*([^*]{2,90})\*\*:?$", s)                           # whole line in bold
    if m:
        t = m.group(1).strip()
        n = re.match(r"^(\d+(?:\.\d+)*)[.)]?\s+", t)
        return (n.group(1).count(".") + 1 if n else 2), t
    if allow_plain:                                                        # "3. Test Strategy" / "3.1 Test levels"
        m = re.match(r"^(\d+(?:\.\d+)*)[.)]?\s+([A-Z][^.:;]{2,80})$", s)
        if m and len(m.group(2).split()) <= 8:
            return m.group(1).count(".") + 1, s
    return None


def md_sections(md):
    """Split a markdown plan into [{heading, level, text}].
    Uses # headings; if the plan has fewer than 5 of them, also accepts bold lines and numbered titles."""
    lines = md.splitlines()
    allow_plain = sum(1 for l in lines if re.match(r"^\s*#{1,4}\s+\S", l)) < 5
    secs, cur = [], {"heading": "(front matter)", "level": 0, "text": []}
    for line in lines:
        h = _heading(line, allow_plain)
        if h:
            if cur["text"] or cur["level"] > 0:
                secs.append({**cur, "text": "\n".join(cur["text"]).strip()})
            cur = {"heading": re.sub(r"^\d+(?:\.\d+)*[.)]?\s+", "", h[1]), "level": h[0], "text": []}
        else:
            cur["text"].append(line)
    if cur["text"] or cur["level"] > 0:
        secs.append({**cur, "text": "\n".join(cur["text"]).strip()})
    return secs


MAP_SYSTEM = ("You are a senior QA lead. You map headings of a software test plan to a fixed list of "
              "canonical section keys. Judge by the heading AND its content preview, not the heading alone. "
              "A sub-section usually belongs to the same key as its parent unless its content clearly fits another key "
              "(e.g. 'Security' under 'Non-Functional Testing' -> security_compliance). A merged section such as "
              "'In Scope / Out of Scope' gets BOTH keys (max 2). Use 'other' only if nothing fits.")
MAP_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["mapping"],
    "properties": {"mapping": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["index", "keys"],
        "properties": {"index": {"type": "integer"},
                       "keys": {"type": "array", "items": {"type": "string", "enum": list(SECTIONS) + ["other"]}}}}}}}


def to_canonical(secs):
    """Group plan sections into {canonical_key: text} using the same LLM mapping as the gold data."""
    keys_txt = "\n".join(f"- {k}: {d}" for k, d in SECTIONS.items())
    rows, parent = [], ""
    for i, s in enumerate(secs):
        if s["level"] == 1:
            parent = s["heading"]
        preview = re.sub(r"\s+", " ", s["text"])[:220]
        par = parent if s["level"] > 1 else "-"
        rows.append(f"[{i}] H{s['level']} {s['heading']} | parent: {par} | {preview}")
    out = ask_json(MAP_SYSTEM, f"CANONICAL KEYS:\n{keys_txt}\n\nTEST PLAN SECTIONS:\n" + "\n".join(rows) +
                   "\n\nReturn one mapping entry for EVERY section index.", MAP_SCHEMA, "section_mapping")
    m = {e["index"]: e["keys"][:2] for e in out["mapping"]}
    grouped = {}
    for i, s in enumerate(secs):
        ks = ["document_control"] if s["level"] == 0 else (m.get(i) or ["other"])
        for k in ks:
            if k != "other":
                block = (f"### {s['heading']}\n" if s["level"] > 1 else "") + s["text"]
                grouped[k] = (grouped.get(k, "") + "\n\n" + block).strip()
    return grouped


# ---------------------------------------------------------------- 1. structure
def score_structure(grouped, min_words=15):
    present = {k for k, t in grouped.items() if len(t.split()) >= min_words}
    missing = [k for k in REQUIRED if k not in present]
    return {"structure": 1 - len(missing) / len(REQUIRED), "missing_sections": missing}


# ---------------------------------------------------------------- 2. coverage
COV_SYSTEM = ("You are a QA auditor. For each requirement fact, decide whether the TEST PLAN covers it. "
              "'yes' = the plan states or plans to verify this fact with its key specifics (value, system, role, rule); "
              "wording may differ. 'partial' = the topic is mentioned but the key specific is missing or vague. "
              "'no' = absent. For yes/partial, plan_quote = the SHORTEST exact span copied from the test plan "
              "(max 20 words) that shows it; empty for 'no'.")
COV_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["results"],
    "properties": {"results": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["id", "verdict", "plan_quote"],
        "properties": {"id": {"type": "string"},
                       "verdict": {"type": "string", "enum": ["yes", "partial", "no"]},
                       "plan_quote": {"type": "string"}}}}}}


def score_coverage(plan_md, facts, chunk_size=25, quote_min=0.6):
    res = {}
    for i in range(0, len(facts), chunk_size):                        # small batches = steadier judge
        chunk = facts[i:i + chunk_size]
        listing = "\n".join(f"{f['id']} [{f['category']}|{f['mvp']}] {f['fact']}" for f in chunk)
        out = ask_json(COV_SYSTEM, f"<test_plan>\n{plan_md}\n</test_plan>\n\n<facts>\n{listing}\n</facts>\n\n"
                       "Return one result for EVERY fact id.", COV_SCHEMA, "fact_coverage")
        res.update({r["id"]: r for r in out["results"]})
    rows = []
    for f in facts:
        r = res.get(f["id"], {"verdict": "no", "plan_quote": ""})
        judge = r["verdict"]
        qs = quote_score(r["plan_quote"], plan_md) if judge != "no" else 0.0
        final = judge if (judge == "no" or qs >= quote_min) else "no"    # evidence must exist in the plan
        rows.append({**f, "judge": judge, "verdict": final, "quote_ok": round(qs, 2), "plan_quote": r["plan_quote"],
                     "points": {"yes": 1.0, "partial": 0.5, "no": 0.0}[final]})
    df = pd.DataFrame(rows)
    must = df[df.must_test]
    return {"coverage": float(must.points.mean()) if len(must) else 0.0,
            "coverage_all": float(df.points.mean()),
            "guard_downgrades": int(((df.judge != "no") & (df.verdict == "no")).sum()),
            "missed_facts": must[must.verdict == "no"][["id", "category", "fact"]].to_dict("records"),
            "coverage_by_category": df.groupby("category").points.mean().round(2).to_dict()}, df


# ---------------------------------------------------------------- 3. faithfulness (cited source-line IDs)
FAITH_SYSTEM = (
    "You are a QA auditor checking a generated test plan for invented content.\n"
    "Extract every PROJECT-SPECIFIC claim as a SHORT ATOMIC statement (max ~20 words): exactly one value, system, "
    "role, rule or scope item per claim. Split compound sentences. Ignore generic testing practice "
    "('defects are logged', 'regression testing', 'XSS checks').\n"
    "kind: 'requirement' = asserts something about the system or project (scope, MVP assignment, features, rules, "
    "NFR targets, systems, integrations, data sources, roles). 'test_design' = a choice made by the test team "
    "(test data values, worked examples, coverage targets, techniques, test schedule).\n"
    "Any claim that NAMES a system, product, vendor, tool, integration, environment or numeric target is ALWAYS "
    "kind='requirement', even inside a test step.\n"
    "verdict vs SOURCE: 'supported' = stated in source; 'derived' = correctly follows from or is calculated from "
    "source; 'contradicted' = source says otherwise; 'not_found' = not in source.\n"
    "The SOURCE is given as numbered lines [S1], [S2], ... source_ids = the IDs of the line(s) that back the verdict "
    "(for supported, derived and contradicted); empty list for not_found.")
FAITH_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["claims"],
    "properties": {"claims": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["claim", "kind", "verdict", "source_ids"],
        "properties": {"claim": {"type": "string"},
                       "kind": {"type": "string", "enum": ["requirement", "test_design"]},
                       "verdict": {"type": "string", "enum": ["supported", "derived", "contradicted", "not_found"]},
                       "source_ids": {"type": "array", "items": {"type": "string"}}}}}}}

NUM_RE = re.compile(r"\d[\d,]*(?:\.\d+)?\s*%?")
STOP = set(("this that with from have will must shall should into their there which when where what each also been "
            "were they them than then only more most such used uses using test tests testing plan system able").split())


def numbers_in(text):
    return {n.replace(",", "").replace(" ", "") for n in NUM_RE.findall(text)}


def key_terms(text):
    """Capitalised names (skip sentence-initial word) + numbers."""
    words = re.findall(r"\b[A-Z][A-Za-z0-9+/&-]+\b", text)[1:]
    return {w.lower() for w in words} | numbers_in(text)


def content_words(text):
    return {w for w in re.findall(r"[a-z0-9][a-z0-9%-]{3,}", text.lower()) if w not in STOP}


def source_units(brd, arch):
    """Split BRD + architecture into numbered lines {'S1': '...', ...}; very long lines are split into sentences."""
    units = []
    for line in (brd + "\n" + arch).splitlines():
        line = line.strip(" -*#\t")
        if len(line) < 3 or set(line) <= set("|-: "):
            continue
        parts = re.split(r"(?<=[.;])\s+(?=[A-Z])", line) if len(line) > 300 else [line]
        units += [p.strip() for p in parts if len(p.strip()) > 2]
    return {f"S{i}": u for i, u in enumerate(units, 1)}


def cited_ok(claim, ids, units, min_overlap=0.25):
    """Cited lines must exist AND share enough content (words, or all names/numbers) with the claim."""
    cited = " ".join(units[i] for i in ids if i in units)
    if not cited:
        return False
    cw = content_words(claim)
    if cw and len(cw & content_words(cited)) / len(cw) >= min_overlap:
        return True
    terms, low, nums = key_terms(claim), cited.lower(), numbers_in(cited)
    return bool(terms) and all((t in nums) if t[0].isdigit() else (t in low) for t in terms)


def score_faithfulness(plan_md, brd, arch):
    units = source_units(brd, arch)
    numbered = "\n".join(f"[{k}] {v}" for k, v in units.items())
    out = ask_json(FAITH_SYSTEM, f"<source>\n{numbered}\n</source>\n\n<test_plan>\n{plan_md}\n</test_plan>",
                   FAITH_SCHEMA, "faithfulness", effort="medium")
    claims = out["claims"]
    for c in claims:
        ids = [i.strip().strip("[]") for i in c["source_ids"]]
        c["ok"] = c["verdict"] in ("supported", "derived") and cited_ok(c["claim"], ids, units)
    req = [c for c in claims if c["kind"] == "requirement"]
    bad = [c for c in req if not c["ok"]] + \
          [c for c in claims if c["kind"] == "test_design" and c["verdict"] == "contradicted"]
    return {"faithfulness": sum(c["ok"] for c in req) / len(req) if req else 1.0,
            "claims": len(claims), "requirement_claims": len(req),
            "test_design_claims": len(claims) - len(req), "invented": len(bad),
            "unverified_supported": sum(1 for c in req if c["verdict"] in ("supported", "derived") and not c["ok"]),
            "invented_claims": [{"claim": c["claim"], "kind": c["kind"], "verdict": c["verdict"]} for c in bad]}


# ---------------------------------------------------------------- 4. similarity
SIM_SYSTEM = ("You compare a GENERATED test plan with the REFERENCE test plan written by a QA lead, section by section. "
              "For each reference section key, score 0-5 how well the generated plan covers the same testing points "
              "(anywhere in the generated plan): 5 = all points, 3 = about half, 0 = none. Ignore wording and order. "
              "List the most important missing points briefly.")
SIM_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["sections"],
    "properties": {"sections": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["key", "score", "missing"],
        "properties": {"key": {"type": "string"}, "score": {"type": "integer"},
                       "missing": {"type": "array", "items": {"type": "string"}}}}}}}


def cosine(a, b):
    a, b = np.array(a), np.array(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def score_similarity(grouped, gold):
    ref = {k: v["text"] for k, v in gold["sections"].items() if v["present"] and k != "document_control"}
    ref_txt = "\n\n".join(f"## [{k}]\n{t}" for k, t in ref.items())
    gen_txt = "\n\n".join(f"## [{k}]\n{t}" for k, t in grouped.items())
    out = ask_json(SIM_SYSTEM, f"<reference>\n{ref_txt}\n</reference>\n\n<generated>\n{gen_txt}\n</generated>\n\n"
                   "Return one entry for EVERY reference key.", SIM_SCHEMA, "similarity", effort="medium")
    for s in out["sections"]:
        s["key"] = s["key"].strip().strip("[]#").strip()              # judge sometimes echoes "[key]"
    llm_scores = {s["key"]: max(0, min(5, s["score"])) / 5 for s in out["sections"] if s["key"] in ref}
    both = [k for k in ref if grouped.get(k)]                          # missing section = 0
    emb = {}
    if both:
        vecs = embed([ref[k][:6000] for k in both] + [grouped[k][:6000] for k in both])
        emb = {k: cosine(vecs[i], vecs[i + len(both)]) for i, k in enumerate(both)}
    return {"similarity": float(np.mean([llm_scores.get(k, 0) for k in ref])),
            "embedding_sim": float(np.mean([emb.get(k, 0) for k in ref])),
            "section_scores": {k: round(llm_scores.get(k, 0), 2) for k in ref},
            "missing_points": {s["key"]: s["missing"] for s in out["sections"] if s["missing"]}}


# ---------------------------------------------------------------- overall
WEIGHTS = {"structure": 0.25, "coverage": 0.45, "similarity": 0.30}   # faithfulness multiplies the total


def score_plan(plan_md, prefix, sections=None):
    """plan_md: generated plan as markdown. sections: optional pre-parsed [{heading, level, text}]."""
    ctx = load_inputs(prefix)
    grouped = to_canonical(sections or md_sections(plan_md))
    s = score_structure(grouped)
    c, cov_df = score_coverage(plan_md, ctx["facts"])
    f = score_faithfulness(plan_md, ctx["brd"], ctx["arch"])
    m = score_similarity(grouped, ctx["gold"])
    result = {"project": ctx["name"], **s, **c, **f, **m}
    result["overall"] = sum(result[k] * w for k, w in WEIGHTS.items()) * result["faithfulness"]
    return result, cov_df


def summary(r):
    keys = ["overall", "structure", "coverage", "coverage_all", "faithfulness", "invented", "similarity", "embedding_sim"]
    return {k: (round(r[k] * 100, 1) if isinstance(r[k], float) else r[k]) for k in keys}