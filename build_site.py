"""
Hong Kong Stamps before 1997 - website builder.

Reads the checklist spreadsheet and writes index.html (one self-contained
page: home with the five reigns, a sub-page per reign, a page per stamp).

Usage:
    python3 build_site.py  path/to/Hong_Kong_Scott_Checklist.xlsx  [output.html]

Columns it understands (matched by header text, so order does not matter):
  Scott No. | Reign | Year | Value / Description | Colour | Cat used (£)
  Qty held  | Notes
  SG No.         <- optional; add this column and the site shows it
  Sell price ($) <- optional; a stamp shows "Available" only when it has
                    a sell price AND Qty held >= 2 (sell duplicates only)
  Status         <- optional; type "Sold" to mark a stamp sold
"""
import sys, re, json, base64, openpyxl
from pathlib import Path

HERE = Path(__file__).parent
REIGNS = [
    ("qv",  "Queen Victoria",     "VR",    "1862 – 1901"),
    ("e7",  "King Edward VII",    "ER VII", "1903 – 1911"),
    ("g5",  "King George V",      "GR V",  "1912 – 1936"),
    ("g6",  "King George VI",     "GR VI", "1937 – 1952"),
    ("qe2", "Queen Elizabeth II", "EIIR",  "1953 – 1997"),
]

def find_col(headers, *names):
    for i, h in enumerate(headers):
        h2 = (h or "").strip().lower()
        for n in names:
            if h2.startswith(n.lower()):
                return i
    return None

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

COMMEM_WORDS = ("jubilee", "coronation", "centenary", "peace", "silver wedding", "upu")

def kind_of(reign_key, year, desc):
    """'def' (definitive) or 'com' (commemorative), from the catalogue description."""
    d = desc.lower()
    if reign_key == "qe2":
        if re.search(r"\bdef\b", d) or "coil" in d or "-" in year:
            return "def"
        return "com"
    return "com" if any(w in d for w in COMMEM_WORDS) else "def"

def issue_name(desc):
    """Commemorative issue name: the description without its face value or notes in brackets."""
    n = re.sub(r"^\$?\d[\d.,]*c?\s+", "", desc)
    m = re.search(r"\((.*?)\)", n)
    if m and any(w in m.group(1).lower() for w in COMMEM_WORDS):   # e.g. "2c rose (Jubilee ovpt)"
        return m.group(1).replace("ovpt", "overprint").strip()
    n = re.sub(r"\(.*?\)", "", n)
    n = re.sub(r"\s+\d{4}$", "", n).strip()
    return n

def first_year(y):
    m = re.search(r"\d{4}", str(y or ""))
    return int(m.group()) if m else 9999

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "Hong_Kong_Scott_Checklist.xlsx"
    out = sys.argv[2] if len(sys.argv) > 2 else str(HERE / "index.html")
    wb = openpyxl.load_workbook(src, data_only=True)
    ws = next(s for s in wb.worksheets if s.title.lower().startswith("scott"))
    rows = list(ws.iter_rows(values_only=True))
    hdr = [str(h) if h else "" for h in rows[0]]
    c = dict(
        scott=find_col(hdr, "Scott"), reign=find_col(hdr, "Reign"),
        year=find_col(hdr, "Year"), desc=find_col(hdr, "Value"),
        colour=find_col(hdr, "Colour"), cat=find_col(hdr, "Cat used"),
        qty=find_col(hdr, "Qty"), sg=find_col(hdr, "SG"),
        price=find_col(hdr, "Sell price"), status=find_col(hdr, "Status"),
    )
    get = lambda r, k: (r[c[k]] if c[k] is not None and c[k] < len(r) else None)

    by_reign = {k: [] for k, *_ in REIGNS}
    name_to_key = {n: k for k, n, *_ in REIGNS}
    order = 0
    for r in rows[1:]:
        reign = get(r, "reign")
        if reign not in name_to_key or get(r, "scott") is None:
            continue
        order += 1
        price = num(get(r, "price"))
        qty = num(get(r, "qty")) or 0
        st = str(get(r, "status") or "").strip().lower()
        if st == "sold":
            status = "sold"
        elif price and qty >= 2:
            status = "available"
        else:
            status = "none"
        by_reign[name_to_key[reign]].append(dict(
            id=str(get(r, "scott")).strip(),
            sg=str(get(r, "sg") or "").strip(),
            year=str(get(r, "year") or "").strip(),
            desc=str(get(r, "desc") or "").strip(),
            colour=str(get(r, "colour") or "").strip(),
            cat=num(get(r, "cat")),
            price=price,
            status=status,
            kind=kind_of(name_to_key[reign], str(get(r, "year") or ""), str(get(r, "desc") or "")),
            issue=issue_name(str(get(r, "desc") or "")),
            _o=order,
        ))
    # Order: by year, then by catalogue title order within the year
    for k in by_reign:
        by_reign[k].sort(key=lambda s: (first_year(s["year"]), s["_o"]))
        for s in by_reign[k]:
            del s["_o"]

    def head(k):
        f = HERE / "img" / f"{k}.jpg"   # monarch-head stamp shown on the home page
        return ("data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()) if f.exists() else ""
    data = [dict(key=k, name=n, cipher=ci, span=sp, img=head(k), stamps=by_reign[k])
            for k, n, ci, sp in REIGNS]
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    html = tpl.replace("/*__DATA__*/[]", json.dumps(data, ensure_ascii=False))
    Path(out).write_text(html, encoding="utf-8")
    total = sum(len(v) for v in by_reign.values())
    print(f"Wrote {out}: {total} stamps "
          + ", ".join(f"{k}={len(v)}" for k, v in by_reign.items()))

if __name__ == "__main__":
    main()
