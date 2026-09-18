from mcp.server.mcpserver import MCPServer

# Absolute imports are intentional because this file is also loaded directly
# by `mcp dev xenbase_mcp/server.py`.
from xenbase_mcp.index import (
    search_genes,
    search_human_orthologs,
    search_mouse_orthologs,
    get_expression,
    get_interactors,
    get_interpro_terms,
    get_diseases,
    get_literature,
)
from xenbase_mcp.xenbase_client import XenbaseError, check_gene, get_gene_page



from xenbase_mcp.index import (
    search_genes,
    search_human_orthologs,
    search_mouse_orthologs,
    get_expression,
    get_interactors,
    get_interpro_terms,
    get_diseases,
    get_literature,
)

# Absolute imports are intentional because this file is also loaded directly
# by `mcp dev xenbase_mcp/server.py`.
from xenbase_mcp.index import search_genes, search_human_orthologs
from xenbase_mcp.xenbase_client import XenbaseError, check_gene, get_gene_page


mcp = MCPServer("xenbase")


@mcp.tool()
def search_genes_tool(query: str, limit: int = 10):
    """Search the local Xenbase gene-page export."""
    return search_genes(query, limit)


@mcp.tool()
def check_gene_tool(gene: str):
    """Check whether a gene identifier is recognized by Xenbase."""
    try:
        return check_gene(gene)
    except XenbaseError as e:
        return {"error": str(e)}


@mcp.tool()
def get_gene_page_tool(gene: str):
    """Fetch structured gene-page information directly from Xenbase."""
    try:
        return get_gene_page(gene)
    except XenbaseError as e:
        return {"error": str(e)}


@mcp.tool()
def get_human_orthologs_tool(query: str, limit: int = 20):
    """Search the local Xenbase human-ortholog mapping."""
    return search_human_orthologs(query, limit)


@mcp.tool()
def research_gene(gene: str):
    """
    Build a local Xenbase research summary for a gene.

    Combines:
    - local gene-page information
    - human ortholog
    - mouse ortholog
    - Xenopus tropicalis expression
    - Xenopus laevis expression
    - interactors
    - InterPro terms
    - disease associations
    - literature associations
    - live Xenbase gene-page data when available
    """

    local = search_genes(gene, 10)

    if not local.get("results"):
        return {
            "query": gene,
            "error": "No local Xenbase gene match found.",
            "local_matches": local,
        }

    # Use the first matching Gene Page ID as the primary gene.
    primary_row = local["results"][0]

    if len(primary_row) < 1:
        return {
            "query": gene,
            "error": "Malformed Xenbase local record.",
            "local_matches": local,
        }

    xenbase_id = primary_row[0]

    # Extract the symbol from the local gene-page record.
    symbol = primary_row[1] if len(primary_row) > 1 else gene

    # Gather all local datasets.
    human = search_human_orthologs(xenbase_id, 20)
    mouse = search_mouse_orthologs(xenbase_id, 20)

    tropicalis_expression = get_expression(
        symbol,
        "tropicalis",
        100,
    )

    laevis_expression = get_expression(
        symbol,
        "laevis",
        100,
    )

    interactors = get_interactors(
        xenbase_id,
        100,
    )

    interpro = get_interpro_terms(
        xenbase_id,
        100,
    )

    diseases = get_diseases(
        xenbase_id,
    )

    literature = get_literature(
        xenbase_id,
        50,
    )

    # Try the live Xenbase page.
    try:
        live = get_gene_page(xenbase_id)
    except XenbaseError as e:
        live = {
            "error": str(e)
        }

    return {
        "query": gene,

        "primary_gene": {
            "xenbase_gene_page_id": xenbase_id,
            "symbol": symbol,
            "local_record": primary_row,
        },

        "other_local_matches": local["results"][1:],

        "human_orthologs": human,
        "mouse_orthologs": mouse,

        "expression": {
            "tropicalis": tropicalis_expression,
            "laevis": laevis_expression,
        },

        "interactors": interactors,
        "interpro": interpro,
        "diseases": diseases,
        "literature": literature,

        "live_xenbase_gene_page": live,
    }
@mcp.tool()
def get_mouse_orthologs_tool(query: str, limit: int = 20):
    """Search the local Xenbase mouse-ortholog mapping."""
    return search_mouse_orthologs(query, limit)


@mcp.tool()
def get_expression_tool(
    gene: str,
    species: str = "tropicalis",
    limit: int = 100,
):
    """Search local Xenbase gene-expression records."""
    return get_expression(gene, species, limit)


@mcp.tool()
def get_interactors_tool(gene: str, limit: int = 100):
    """Return protein/gene interactors from the local Xenbase export."""
    return get_interactors(gene, limit)


@mcp.tool()
def get_interpro_terms_tool(gene: str, limit: int = 100):
    """Return InterPro terms associated with a Xenbase gene."""
    return get_interpro_terms(gene, limit)


@mcp.tool()
def get_diseases_tool(gene: str):
    """Return disease ontology associations from Xenbase."""
    return get_diseases(gene)


@mcp.tool()
def get_literature_tool(gene: str, limit: int = 50):
    """Find Xenbase literature records associated with a gene."""
    return get_literature(gene, limit)

def main():
    mcp.run()


if __name__ == "__main__":
    main()