import csv
import sqlite3
import sys
from pathlib import Path
from .config import DATA_DIR
DB_PATH = DATA_DIR / "xenbase.db"
csv.field_size_limit(sys.maxsize)
def _read_tsv(path: Path):
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        return list(csv.reader(f, delimiter="\t"))


def _search_rows(path: Path, query: str, limit: int = 10):
    rows = _read_tsv(path)

    if not rows:
        return []

    q = query.strip().lower()
    hits = []

    for row in rows:
        if q in " | ".join(row).lower():
            hits.append(row)

            if len(hits) >= limit:
                break

    return hits


def search_genes(query: str, limit: int = 10):
    """
    Search the local Xenbase gene database.

    Searches:
        - Xenbase Gene Page ID
        - gene symbol
        - gene name
        - category
        - synonyms

    Matching is case-insensitive.
    """

    if not DB_PATH.exists():
        return {
            "error": (
                "Xenbase SQLite database not found. "
                "Run scripts/build_xenbase_db.py first."
            )
        }

    q = query.strip().lower()

    conn = sqlite3.connect(DB_PATH)

    try:
        rows = conn.execute(
            """
            SELECT
                gene_page_id,
                symbol,
                name,
                category,
                synonyms,
                curation
            FROM gene_info
            WHERE LOWER(gene_page_id) LIKE ?
               OR LOWER(symbol) LIKE ?
               OR LOWER(name) LIKE ?
               OR LOWER(category) LIKE ?
               OR LOWER(synonyms) LIKE ?
            LIMIT ?
            """,
            (
                f"%{q}%",
                f"%{q}%",
                f"%{q}%",
                f"%{q}%",
                f"%{q}%",
                limit,
            ),
        ).fetchall()

        return {
            "query": query,
            "results": [list(row) for row in rows],
        }

    finally:
        conn.close()

def search_human_orthologs(query: str, limit: int = 20):
    """
    Search the local Xenbase human-ortholog database.

    Handles:
        - human gene IDs
        - Xenbase Gene Page IDs
        - gene symbols
        - descriptions
    """

    if not DB_PATH.exists():
        return {
            "error": (
                "Xenbase SQLite database not found. "
                "Run scripts/build_xenbase_db.py first."
            )
        }

    q = query.strip().lower()

    conn = sqlite3.connect(DB_PATH)

    try:
        rows = conn.execute(
            """
            SELECT
                human_gene_id,
                gene_page_id,
                symbol,
                description
            FROM human_orthologs
            WHERE LOWER(human_gene_id) LIKE ?
               OR LOWER(gene_page_id) LIKE ?
               OR LOWER(symbol) LIKE ?
               OR LOWER(description) LIKE ?
            LIMIT ?
            """,
            (
                f"%{q}%",
                f"%{q}%",
                f"%{q}%",
                f"%{q}%",
                limit,
            ),
        ).fetchall()

        return {
            "query": query,
            "results": [list(row) for row in rows],
        }

    finally:
        conn.close()

def search_mouse_orthologs(query: str, limit: int = 20):
    """
    Search the local Xenbase mouse-ortholog database.

    Handles:
        - mouse gene IDs
        - Xenbase Gene Page IDs
        - gene symbols
        - descriptions
    """

    if not DB_PATH.exists():
        return {
            "error": (
                "Xenbase SQLite database not found. "
                "Run scripts/build_xenbase_db.py first."
            )
        }

    q = query.strip().lower()

    conn = sqlite3.connect(DB_PATH)

    try:
        rows = conn.execute(
            """
            SELECT
                mouse_gene_id,
                gene_page_id,
                symbol,
                description
            FROM mouse_orthologs
            WHERE LOWER(mouse_gene_id) LIKE ?
               OR LOWER(gene_page_id) LIKE ?
               OR LOWER(symbol) LIKE ?
               OR LOWER(description) LIKE ?
            LIMIT ?
            """,
            (
                f"%{q}%",
                f"%{q}%",
                f"%{q}%",
                f"%{q}%",
                limit,
            ),
        ).fetchall()

        return {
            "query": query,
            "results": [list(row) for row in rows],
        }

    finally:
        conn.close()

def get_expression(gene: str, species: str = "tropicalis", limit: int = 100):
    """
    Search local Xenbase expression data using the SQLite database.

    Handles:
        - Xenbase Gene Page IDs
        - Xenbase Gene IDs
        - gene symbols
        - X. laevis L/S homeologs

    species:
        tropicalis -> Xenopus tropicalis
        laevis     -> Xenopus laevis
    """

    species = species.lower().strip()

    if species not in {"tropicalis", "laevis"}:
        return {
            "error": "species must be 'tropicalis' or 'laevis'"
        }

    if not DB_PATH.exists():
        return {
            "error": (
                "Xenbase SQLite database not found. "
                "Run scripts/build_xenbase_db.py first."
            )
        }

    q = gene.strip().lower()

    conn = sqlite3.connect(DB_PATH)

    try:
        table = f"expression_{species}"

        # Direct Gene ID lookup.
        rows = conn.execute(
            f"""
            SELECT *
            FROM {table}
            WHERE LOWER(gene_id) = ?
            LIMIT ?
            """,
            (q, limit),
        ).fetchall()

        # Exact symbol lookup.
        if not rows:
            rows = conn.execute(
                f"""
                SELECT *
                FROM {table}
                WHERE LOWER(symbol) = ?
                LIMIT ?
                """,
                (q, limit),
            ).fetchall()

        # For a broad X. laevis query such as "h3-3b",
        # return both L and S homeologs.
        if not rows and species == "laevis":
            rows = conn.execute(
                f"""
                SELECT *
                FROM {table}
                WHERE LOWER(symbol) LIKE ?
                LIMIT ?
                """,
                (q + ".%", limit),
            ).fetchall()

        return {
            "query": gene,
            "species": species,
            "results": [list(row) for row in rows],
        }

    finally:
        conn.close()

def get_interactors(gene: str, limit: int = 100):
    """
    Return protein/gene interactors from the local Xenbase SQLite database.

    Handles:
        - Xenbase Gene Page IDs
        - Xenbase Gene IDs
        - gene symbols
    """

    if not DB_PATH.exists():
        return {
            "error": (
                "Xenbase SQLite database not found. "
                "Run scripts/build_xenbase_db.py first."
            )
        }

    q = gene.strip().lower()

    conn = sqlite3.connect(DB_PATH)

    try:
        row = conn.execute(
            """
            SELECT gene_page_id, symbol, raw_interactors
            FROM interactors
            WHERE LOWER(gene_page_id) = ?
               OR LOWER(symbol) = ?
            LIMIT 1
            """,
            (q, q),
        ).fetchone()

        if not row:
            return {
                "query": gene,
                "interactors": [],
            }

        gene_page_id, symbol, raw_interactors = row

        interactors = []

        for item in raw_interactors.strip().rstrip(",").split(","):
            parts = item.split(":")

            if len(parts) >= 3:
                interactors.append({
                    "xenbase_id": parts[0],
                    "symbol": parts[1],
                    "score": parts[2],
                })

        return {
            "query": gene,
            "gene_page_id": gene_page_id,
            "symbol": symbol,
            "interactors": interactors[:limit],
        }

    finally:
        conn.close()

def get_interpro_terms(gene: str, limit: int = 100):
    """
    Return InterPro terms from the local Xenbase SQLite database.

    Handles:
        - Xenbase Gene Page IDs
        - Xenbase Gene IDs
        - gene symbols
    """

    if not DB_PATH.exists():
        return {
            "error": (
                "Xenbase SQLite database not found. "
                "Run scripts/build_xenbase_db.py first."
            )
        }

    q = gene.strip().lower()

    conn = sqlite3.connect(DB_PATH)

    try:
        rows = conn.execute(
            """
            SELECT gene_page_id, gene_id, symbol, terms
            FROM interpro
            WHERE LOWER(gene_page_id) = ?
               OR LOWER(gene_id) = ?
               OR LOWER(symbol) = ?
            LIMIT 1
            """,
            (q, q, q),
        ).fetchall()

        if not rows:
            return {
                "query": gene,
                "interpro_terms": [],
            }

        gene_page_id, gene_id, symbol, raw_terms = rows[0]

        terms = [
            x.strip()
            for x in raw_terms.split("|")
            if x.strip()
        ]

        return {
            "query": gene,
            "gene_page_id": gene_page_id,
            "gene_id": gene_id,
            "symbol": symbol,
            "interpro_terms": terms[:limit],
        }

    finally:
        conn.close()

def get_diseases(gene: str):
    """
    Return disease ontology associations from the local Xenbase SQLite database.

    Handles:
        - Xenbase Gene Page IDs
        - gene symbols
    """

    if not DB_PATH.exists():
        return {
            "error": (
                "Xenbase SQLite database not found. "
                "Run scripts/build_xenbase_db.py first."
            )
        }

    q = gene.strip().lower()

    conn = sqlite3.connect(DB_PATH)

    try:
        row = conn.execute(
            """
            SELECT gene_page_id, symbol, diseases
            FROM diseases
            WHERE LOWER(gene_page_id) = ?
               OR LOWER(symbol) = ?
            LIMIT 1
            """,
            (q, q),
        ).fetchone()

        if not row:
            return {
                "query": gene,
                "diseases": [],
            }

        gene_page_id, symbol, raw_diseases = row

        disease_list = [
            x.strip()
            for x in raw_diseases.split("|")
            if x.strip()
        ]

        return {
            "query": gene,
            "gene_page_id": gene_page_id,
            "symbol": symbol,
            "diseases": disease_list,
        }

    finally:
        conn.close()

def get_literature(gene: str, limit: int = 50):
    """
    Find Xenbase literature records associated with a gene.

    Uses the local SQLite database and joins article IDs to PMIDs/PMCIDs.

    Handles:
        - Xenbase Gene Page IDs
        - gene symbols
    """

    if not DB_PATH.exists():
        return {
            "error": (
                "Xenbase SQLite database not found. "
                "Run scripts/build_xenbase_db.py first."
            )
        }

    q = gene.strip().lower()

    conn = sqlite3.connect(DB_PATH)

    try:
        rows = conn.execute(
            """
            SELECT
                l.article_id,
                l.pmid,
                l.genes,
                a.pmcid
            FROM literature AS l
            LEFT JOIN article_ids AS a
                ON l.article_id = a.xb_art_id
            WHERE LOWER(l.genes) LIKE ?
            LIMIT ?
            """,
            (f"%{q}%", limit),
        ).fetchall()

        results = []

        for article_id, pmid, genes, pmcid in rows:
            matched_genes = [
                item.strip()
                for item in genes.split(",")
                if q in item.lower()
            ]

            results.append({
                "article_id": article_id,
                "pmid": pmid,
                "pmcid": pmcid,
                "matched_genes": matched_genes,
            })

        return {
            "query": gene,
            "papers": results,
        }

    finally:
        conn.close()