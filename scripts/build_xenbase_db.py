import csv
import sqlite3
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DB_PATH = DATA / "xenbase.db"


def connect_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    return conn


def create_tables(conn):
    conn.executescript(
        """
        DROP TABLE IF EXISTS gene_info;
        DROP TABLE IF EXISTS human_orthologs;
        DROP TABLE IF EXISTS mouse_orthologs;
        DROP TABLE IF EXISTS expression_tropicalis;
        DROP TABLE IF EXISTS expression_laevis;
        DROP TABLE IF EXISTS expression_tissue_tropicalis;
        DROP TABLE IF EXISTS expression_tissue_laevis;
        DROP TABLE IF EXISTS interactors;
        DROP TABLE IF EXISTS interpro;
        DROP TABLE IF EXISTS diseases;
        DROP TABLE IF EXISTS literature;
        DROP TABLE IF EXISTS article_ids;

        CREATE TABLE gene_info (
            gene_page_id TEXT,
            symbol TEXT,
            name TEXT,
            category TEXT,
            synonyms TEXT,
            curation TEXT
        );

        CREATE TABLE human_orthologs (
            human_gene_id TEXT,
            gene_page_id TEXT,
            symbol TEXT,
            description TEXT
        );

        CREATE TABLE mouse_orthologs (
            mouse_gene_id TEXT,
            gene_page_id TEXT,
            symbol TEXT,
            description TEXT
        );

        CREATE TABLE expression_tropicalis (
            gene_id TEXT,
            symbol TEXT,
            genotype TEXT,
            anatomical_entities TEXT,
            stage TEXT,
            stage2 TEXT,
            assay TEXT,
            image_id TEXT,
            expression_id TEXT,
            submitted_by TEXT,
            notes TEXT,
            curation TEXT
        );

        CREATE TABLE expression_laevis (
            gene_id TEXT,
            symbol TEXT,
            genotype TEXT,
            anatomical_entities TEXT,
            stage TEXT,
            stage2 TEXT,
            assay TEXT,
            image_id TEXT,
            expression_id TEXT,
            submitted_by TEXT,
            notes TEXT,
            curation TEXT
        );

        CREATE TABLE expression_tissue_tropicalis (
            raw_data TEXT
        );

        CREATE TABLE expression_tissue_laevis (
            raw_data TEXT
        );

        CREATE TABLE interactors (
            gene_page_id TEXT,
            symbol TEXT,
            raw_interactors TEXT
        );

        CREATE TABLE interpro (
            gene_page_id TEXT,
            gene_id TEXT,
            symbol TEXT,
            terms TEXT
        );

        CREATE TABLE diseases (
            gene_page_id TEXT,
            symbol TEXT,
            diseases TEXT
        );

        CREATE TABLE literature (
            article_id TEXT,
            pmid TEXT,
            genes TEXT
        );

        CREATE TABLE article_ids (
            xb_art_id TEXT,
            pmid TEXT,
            pmcid TEXT
        );
        """
    )


def read_tsv(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:
        reader = csv.reader(f, delimiter="\t")

        for row in reader:
            yield row


def load_gene_info(conn):
    path = DATA / "GenePageGeneralInfo_AllGenes.txt"

    rows = []

    for row in read_tsv(path):
        row = row[:6]

        while len(row) < 6:
            row.append("")

        rows.append(row)

    conn.executemany(
        """
        INSERT INTO gene_info
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    print(f"gene_info: {len(rows):,}")

def load_human_orthologs(conn):
    path = DATA / "XenbaseGeneHumanOrthologMapping.txt"

    rows = []

    for row in read_tsv(path):
        if len(row) >= 4:
            rows.append(row[:4])

    conn.executemany(
        """
        INSERT INTO human_orthologs
        VALUES (?, ?, ?, ?)
        """,
        rows,
    )

    print(f"human_orthologs: {len(rows):,}")


def load_mouse_orthologs(conn):
    path = DATA / "XenbaseGeneMouseOrthologMapping.txt"

    rows = []

    for row in read_tsv(path):
        if len(row) >= 4:
            rows.append(row[:4])

    conn.executemany(
        """
        INSERT INTO mouse_orthologs
        VALUES (?, ?, ?, ?)
        """,
        rows,
    )

    print(f"mouse_orthologs: {len(rows):,}")


def load_expression(conn, species):
    path = DATA / f"GeneExpression_{species}.txt"
    table = f"expression_{species}"

    rows = []

    for row in read_tsv(path):
        if len(row) >= 12:
            rows.append(row[:12])

            if len(rows) >= 10000:
                conn.executemany(
                    f"""
                    INSERT INTO {table}
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    rows,
                )
                rows.clear()

    if rows:
        conn.executemany(
            f"""
            INSERT INTO {table}
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    count = conn.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count:,}")


def load_expression_tissue(conn, species):
    path = DATA / f"GeneExpPerTissue_{species}.txt"
    table = f"expression_tissue_{species}"

    rows = []

    for row in read_tsv(path):
        rows.append(("\t".join(row),))

        if len(rows) >= 10000:
            conn.executemany(
                f"INSERT INTO {table} VALUES (?)",
                rows,
            )
            rows.clear()

    if rows:
        conn.executemany(
            f"INSERT INTO {table} VALUES (?)",
            rows,
        )

    count = conn.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count:,}")


def load_interactors(conn):
    path = DATA / "GenePageInteractants.txt"

    rows = []

    for row in read_tsv(path):
        if len(row) >= 3:
            rows.append(row[:3])

            if len(rows) >= 5000:
                conn.executemany(
                    """
                    INSERT INTO interactors
                    VALUES (?, ?, ?)
                    """,
                    rows,
                )
                rows.clear()

    if rows:
        conn.executemany(
            """
            INSERT INTO interactors
            VALUES (?, ?, ?)
            """,
            rows,
        )

    count = conn.execute(
        "SELECT COUNT(*) FROM interactors"
    ).fetchone()[0]

    print(f"interactors: {count:,}")


def load_interpro(conn):
    path = DATA / "GenePageIntProTerms.txt"

    rows = []

    for row in read_tsv(path):
        if len(row) >= 4:
            rows.append(row[:4])

    conn.executemany(
        """
        INSERT INTO interpro
        VALUES (?, ?, ?, ?)
        """,
        rows,
    )

    print(f"interpro: {len(rows):,}")


def load_diseases(conn):
    path = DATA / "XenbaseDiseaseOntologyData.txt"

    rows = []

    for row in read_tsv(path):
        if len(row) >= 3:
            rows.append(row[:3])

    conn.executemany(
        """
        INSERT INTO diseases
        VALUES (?, ?, ?)
        """,
        rows,
    )

    print(f"diseases: {len(rows):,}")


def load_literature(conn):
    path = DATA / "LiteratureMatchedGenesByPaper.txt"

    rows = []

    for row in read_tsv(path):
        if len(row) >= 3:
            rows.append(row[:3])

            if len(rows) >= 5000:
                conn.executemany(
                    """
                    INSERT INTO literature
                    VALUES (?, ?, ?)
                    """,
                    rows,
                )
                rows.clear()

    if rows:
        conn.executemany(
            """
            INSERT INTO literature
            VALUES (?, ?, ?)
            """,
            rows,
        )

    count = conn.execute(
        "SELECT COUNT(*) FROM literature"
    ).fetchone()[0]

    print(f"literature: {count:,}")


def load_article_ids(conn):
    path = DATA / "XB-ART-ID_to_PMID_to_PMCID.txt"

    rows = []

    for row in read_tsv(path):
        if not row:
            continue

        # This particular file has a header.
        if row[0] == "XB-ART-ID":
            continue

        if len(row) >= 3:
            rows.append(row[:3])

    conn.executemany(
        """
        INSERT INTO article_ids
        VALUES (?, ?, ?)
        """,
        rows,
    )

    print(f"article_ids: {len(rows):,}")


def create_indexes(conn):
    conn.executescript(
        """
        CREATE INDEX idx_gene_info_page
            ON gene_info(gene_page_id);

        CREATE INDEX idx_gene_info_symbol
            ON gene_info(symbol);

        CREATE INDEX idx_human_page
            ON human_orthologs(gene_page_id);

        CREATE INDEX idx_mouse_page
            ON mouse_orthologs(gene_page_id);

        CREATE INDEX idx_expr_trop_gene
            ON expression_tropicalis(gene_id);

        CREATE INDEX idx_expr_trop_symbol
            ON expression_tropicalis(symbol);

        CREATE INDEX idx_expr_laevis_gene
            ON expression_laevis(gene_id);

        CREATE INDEX idx_expr_laevis_symbol
            ON expression_laevis(symbol);

        CREATE INDEX idx_interactors_page
            ON interactors(gene_page_id);

        CREATE INDEX idx_interpro_page
            ON interpro(gene_page_id);

        CREATE INDEX idx_diseases_page
            ON diseases(gene_page_id);

        CREATE INDEX idx_literature_article
            ON literature(article_id);

        CREATE INDEX idx_article_pmid
            ON article_ids(pmid);

        CREATE INDEX idx_article_xb
            ON article_ids(xb_art_id);
        """
    )


def main():
    print(f"Building Xenbase database:")
    print(f"  {DB_PATH}")

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = connect_db()

    try:
        create_tables(conn)

        load_gene_info(conn)
        load_human_orthologs(conn)
        load_mouse_orthologs(conn)

        load_expression(conn, "tropicalis")
        load_expression(conn, "laevis")

        load_expression_tissue(conn, "tropicalis")
        load_expression_tissue(conn, "laevis")

        load_interactors(conn)
        load_interpro(conn)
        load_diseases(conn)
        load_literature(conn)
        load_article_ids(conn)

        create_indexes(conn)

        conn.commit()

    finally:
        conn.close()

    print("\nXenbase database build complete.")


if __name__ == "__main__":
    main()