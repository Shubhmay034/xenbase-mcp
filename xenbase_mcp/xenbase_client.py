import httpx

BASE = "https://www.xenbase.org/xenbase/gene/geneAjax.do"


class XenbaseError(RuntimeError):
    pass


def _get_json(params: dict):
    try:
        response = httpx.get(
            BASE,
            params=params,
            timeout=30,
            follow_redirects=True,
        )
        response.raise_for_status()

        # Helpful if Xenbase returns HTML/error text instead of JSON.
        content_type = response.headers.get("content-type", "")

        if "json" not in content_type.lower():
            raise XenbaseError(
                f"Xenbase returned non-JSON data "
                f"(HTTP {response.status_code}, "
                f"Content-Type: {content_type})."
            )

        return response.json()

    except XenbaseError:
        raise
    except Exception as e:
        raise XenbaseError(f"Xenbase request failed: {e}") from e


def _clean_gene_id(gene: str) -> str:
    """
    Convert Xenbase accession formats such as:
        XB-GENEPAGE-6042438
        XB-GENE-6042438
        6042438
    into the numeric ID expected by the API.
    """
    gene = gene.strip()

    if gene.upper().startswith("XB-GENEPAGE-"):
        return gene.split("-")[-1]

    if gene.upper().startswith("XB-GENE-"):
        return gene.split("-")[-1]

    return gene


def check_gene(gene: str):
    gene_id = _clean_gene_id(gene)

    return _get_json(
        {
            "method": "genecheck",
            "geneId": gene_id,
        }
    )


def get_gene_page(gene: str, organism: str | None = None, ploidy: str | None = None):
    gene_id = _clean_gene_id(gene)

    params = {
        "method": "jsonifyGene",
        "geneId": gene_id,
    }

    if organism:
        params["orgId"] = organism

    if ploidy:
        params["tetId"] = ploidy

    return _get_json(params)