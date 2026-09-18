# Xenbase MCP

A small Xenbase-only MCP server for VS Code / GitHub Copilot.

## Tools

The MCP server provides 11 tools:

- `search_genes_tool` — Search Xenbase genes by gene symbol, name, or ID.
- `check_gene_tool` — Check a Xenbase gene identifier using the live Xenbase API.
- `get_gene_page_tool` — Retrieve detailed gene-page information from Xenbase.
- `get_human_orthologs_tool` — Find human orthologs for Xenopus genes.
- `get_mouse_orthologs_tool` — Find mouse orthologs for Xenopus genes.
- `get_expression_tool` — Search curated developmental expression annotations by gene, species, stage, assay, and tissue.
- `get_interactors_tool` — Retrieve genes/proteins reported as interacting with a Xenbase gene.
- `get_interpro_terms_tool` — Retrieve InterPro protein/domain annotations.
- `get_diseases_tool` — Retrieve disease ontology annotations associated with a gene.
- `get_literature_tool` — Find literature associated with a Xenbase gene.
- `research_gene` — Run a combined research query covering gene information, orthologs, expression, interactions, protein domains, diseases, literature, and live Xenbase gene-page data.

## Setup

From the project directory:

```bash
uv sync
uv run python scripts/update_xenbase_data.py
uv run mcp dev xenbase_mcp/server.py

