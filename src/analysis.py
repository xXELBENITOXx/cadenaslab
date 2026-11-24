"""CadenasLab: demostración educativa de análisis de cadenas y teoría de números.

Comparación de dos textos mediante shingles de palabras y hashing polinómico
(Rabin–Karp). Las coincidencias de hash se verifican comparando los tokens para
prevenir falsos positivos por colisiones. El índice mide similitud literal, NO plagio.
"""
from __future__ import annotations
import re
import unicodedata
from collections import defaultdict

PRIME = 1_000_000_007
BASE = 911_382_323
MAX_CHARS = 20_000
WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)

EXAMPLE_A = (
    "La teoría de números estudia las propiedades de los números enteros y sus aplicaciones "
    "en informática. Uno de sus conceptos importantes es la aritmética modular, que permite "
    "calcular residuos de divisiones. Los algoritmos de búsqueda de cadenas permiten localizar "
    "patrones dentro de textos y optimizar el procesamiento de información."
)
EXAMPLE_B = (
    "En ciencias de la computación, la teoría de números estudia las propiedades de los números "
    "enteros y sus aplicaciones en informática. También se emplea en sistemas de seguridad. "
    "Los algoritmos de búsqueda de cadenas permiten localizar patrones dentro de textos "
    "para mejorar las consultas en documentos."
)


def normalize_word(s: str) -> str:
    """Normaliza solo para comparar; las posiciones originales no se alteran."""
    s = unicodedata.normalize("NFKD", s.casefold())
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def tokenize(text: str):
    return [(normalize_word(m.group()), m.start(), m.end()) for m in WORD_RE.finditer(text)]


def word_hash(token: str) -> int:
    h = 0
    for ch in token:
        h = (h * 257 + ord(ch)) % PRIME
    return h


def rolling_hashes(tokens: list[str], k: int):
    """Hash polinómico deslizante, módulo primo, sobre k palabras."""
    if k <= 0 or len(tokens) < k:
        return []
    vals = [word_hash(t) + 1 for t in tokens]
    h = 0
    for value in vals[:k]:
        h = (h * BASE + value) % PRIME
    out = [h]
    power = pow(BASE, k - 1, PRIME)
    for i in range(k, len(vals)):
        h = ((h - vals[i - k] * power) * BASE + vals[i]) % PRIME
        out.append(h)
    return out


def _make_ranges(toks, mask):
    out = []
    start = None
    end = None
    for (_, a, b), matched in zip(toks, mask):
        if matched:
            if start is None:
                start = a
            end = b
        elif start is not None:
            out.append([start, end])
            start = end = None
    if start is not None:
        out.append([start, end])
    return out


def analyze(text_a: str, text_b: str):
    if not isinstance(text_a, str) or not isinstance(text_b, str):
        raise ValueError("Los dos textos deben ser cadenas.")
    if len(text_a) > MAX_CHARS or len(text_b) > MAX_CHARS:
        raise ValueError(f"Cada texto puede tener como máximo {MAX_CHARS:,} caracteres.")
    tok_a, tok_b = tokenize(text_a), tokenize(text_b)
    wa = [t[0] for t in tok_a]
    wb = [t[0] for t in tok_b]
    n, m = len(wa), len(wb)
    k = min(5, n, m)
    response = {
        "score": 0.0, "coverage_a": 0.0, "coverage_b": 0.0,
        "words_a": n, "words_b": m,
        "matched_words_a": 0, "matched_words_b": 0,
        "common_shingles": 0, "shingles_a": max(0, n - k + 1),
        "shingles_b": max(0, m - k + 1), "window": k,
        "ranges_a": [], "ranges_b": [], "fragments": [],
        "method": "Rabin–Karp: hash rodante + verificación exacta",
        "base": BASE, "prime": PRIME,
        "notice": "Se compara únicamente el texto proporcionado. Una similitud alta NO demuestra plagio.",
    }
    if k < 3:
        response["notice"] = "Se necesitan al menos tres palabras en cada texto para una comparación útil."
        return response

    ha, hb = rolling_hashes(wa, k), rolling_hashes(wb, k)
    # Hash -> segmentos y posiciones. El tuple exacto evita colisiones de hash.
    index_a, index_b = defaultdict(dict), defaultdict(dict)
    for i, h in enumerate(ha):
        index_a[h].setdefault(tuple(wa[i:i + k]), []).append(i)
    for j, h in enumerate(hb):
        index_b[h].setdefault(tuple(wb[j:j + k]), []).append(j)

    mask_a, mask_b = [False] * n, [False] * m
    common_shingles = set()
    matching_pairs = []
    for h, entries_a in index_a.items():
        entries_b = index_b.get(h)
        if not entries_b:
            continue
        for key, offsets_a in entries_a.items():
            offsets_b = entries_b.get(key)
            if not offsets_b:
                continue
            common_shingles.add(key)
            for pos in offsets_a:
                mask_a[pos:pos + k] = [True] * k
            for pos in offsets_b:
                mask_b[pos:pos + k] = [True] * k
            # Los ejemplos se limitan: no es necesario construir un producto cartesiano.
            for i in offsets_a[:12]:
                for j in offsets_b[:12]:
                    matching_pairs.append((i, j))

    fragments = []
    for i, j in matching_pairs:
        if i > 0 and j > 0 and wa[i - 1] == wb[j - 1]:
            continue  # evitar repetir el medio de una coincidencia mayor
        start_i, start_j = i, j
        while i < n and j < m and wa[i] == wb[j]:
            i += 1
            j += 1
        if i - start_i < k:
            continue
        a_start, a_end = tok_a[start_i][1], tok_a[i - 1][2]
        b_start, b_end = tok_b[start_j][1], tok_b[j - 1][2]
        fragments.append({
            "text_a": text_a[a_start:a_end], "text_b": text_b[b_start:b_end],
            "start_a": a_start, "end_a": a_end,
            "start_b": b_start, "end_b": b_end,
            "words": i - start_i,
        })
    fragments.sort(key=lambda x: (-x["words"], x["start_a"]))
    dedup, seen = [], set()
    for f in fragments:
        key = (f["start_a"], f["end_a"], f["start_b"], f["end_b"])
        if key not in seen:
            dedup.append(f)
            seen.add(key)
        if len(dedup) >= 6:
            break

    matched_a = sum(mask_a)
    matched_b = sum(mask_b)
    coverage_a = round(100 * matched_a / n, 1) if n else 0.0
    coverage_b = round(100 * matched_b / m, 1) if m else 0.0
    response.update({
        "score": round((coverage_a + coverage_b) / 2, 1),
        "coverage_a": coverage_a, "coverage_b": coverage_b,
        "matched_words_a": matched_a, "matched_words_b": matched_b,
        "common_shingles": len(common_shingles),
        "ranges_a": _make_ranges(tok_a, mask_a),
        "ranges_b": _make_ranges(tok_b, mask_b),
        "fragments": dedup,
    })
    return response


def kmp_search(text: str, pattern: str):
    """Encuentra las apariciones de patrón y muestra la tabla prefijo LPS."""
    if not pattern or len(pattern) > 200 or len(text) > MAX_CHARS:
        raise ValueError("Introduce un patrón de 1 a 200 caracteres y un texto válido.")
    p = pattern.casefold()
    t = text.casefold()
    lps = [0] * len(p)
    j = 0
    for i in range(1, len(p)):
        while j > 0 and p[i] != p[j]:
            j = lps[j - 1]
        if p[i] == p[j]:
            j += 1
            lps[i] = j
    matches, j, comparisons = [], 0, 0
    for i, ch in enumerate(t):
        while j and ch != p[j]:
            comparisons += 1
            j = lps[j - 1]
        comparisons += 1
        if ch == p[j]:
            j += 1
        if j == len(p):
            matches.append(i - len(p) + 1)
            j = lps[j - 1]
    return {"pattern": pattern, "positions": matches, "lps": lps, "comparisons": comparisons, "complexity": "O(n + m)"}


def boyer_moore_horspool(text: str, pattern: str):
    """Versión didáctica Boyer–Moore–Horspool, heurística de carácter malo."""
    if not pattern or len(pattern) > 200 or len(text) > MAX_CHARS:
        raise ValueError("Introduce un patrón de 1 a 200 caracteres y un texto válido.")
    t, p = text.casefold(), pattern.casefold()
    n, m = len(t), len(p)
    skip = {p[i]: m - i - 1 for i in range(m - 1)}
    positions, comparisons, shifts, i = [], 0, [], 0
    while i <= n - m:
        j = m - 1
        while j >= 0:
            comparisons += 1
            if t[i + j] != p[j]:
                break
            j -= 1
        if j < 0:
            positions.append(i)
        advance = skip.get(t[i + m - 1], m)
        shifts.append({"start": i, "advance": advance})
        i += advance
    return {"positions": positions, "comparisons": comparisons, "shifts": shifts[:12], "method": "Boyer–Moore–Horspool"}


def euclid(a: int, b: int):
    if abs(a) > 10**12 or abs(b) > 10**12:
        raise ValueError("Usa valores absolutos menores o iguales a 10^12.")
    x, y = abs(a), abs(b)
    steps = []
    while y:
        q, r = divmod(x, y)
        steps.append({"a": x, "b": y, "quotient": q, "remainder": r})
        x, y = y, r
    return {"a": a, "b": b, "gcd": x, "steps": steps}


def modular(base: int, exponent: int, modulus: int):
    if modulus < 2 or modulus > 10**12 or exponent < 0 or exponent > 10**9 or abs(base) > 10**12:
        raise ValueError("Módulo entre 2 y 10^12; exponente entre 0 y 10^9.")
    return {"base": base, "exponent": exponent, "modulus": modulus,
            "result": pow(base, exponent, modulus), "description": "Exponenciación modular rápida"}


def sieve(limit: int = 60):
    if limit < 2 or limit > 1000:
        raise ValueError("Límite entre 2 y 1000.")
    prime = [True] * (limit + 1)
    prime[0] = prime[1] = False
    for p in range(2, int(limit ** .5) + 1):
        if prime[p]:
            for composite in range(p * p, limit + 1, p):
                prime[composite] = False
    return {"limit": limit, "primes": [x for x, ok in enumerate(prime) if ok],
            "values": [{"number": x, "prime": prime[x]} for x in range(1, limit + 1)]}


def algorithm(body: dict):
    kind = body.get("kind", "")
    if kind == "kmp":
        return kmp_search(str(body.get("text", "")), str(body.get("pattern", "")))
    if kind == "boyer":
        return boyer_moore_horspool(str(body.get("text", "")), str(body.get("pattern", "")))
    if kind == "euclid":
        return euclid(int(body.get("a", 48)), int(body.get("b", 18)))
    if kind == "modular":
        return modular(int(body.get("base", 3)), int(body.get("exponent", 7)), int(body.get("modulus", 11)))
    if kind == "sieve":
        return sieve(int(body.get("limit", 60)))
    raise ValueError("Algoritmo no reconocido.")
