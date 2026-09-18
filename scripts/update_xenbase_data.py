from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

BASE_URL = "https://download.xenbase.org/xenbase/GenePageReports/"

FILES = [
    # Gene identity / annotation
    "GenePageGeneralInfo_AllGenes.txt",
    "GenePageGeneralInfo_ManuallyCurated.txt",

    # Orthology
    "XenbaseGeneHumanOrthologMapping.txt",
    "XenbaseGeneMouseOrthologMapping.txt",

    # Expression
    "GeneExpression_laevis.txt",
    "GeneExpression_tropicalis.txt",
    "GeneExpPerTissue_laevis.txt",
    "GeneExpPerTissue_tropicalis.txt",

    # Protein interactions
    "GenePageInteractants.txt",

    # Literature
    "LiteratureMatchedGenesByPaper.txt",
    "XB-ART-ID_to_PMID_to_PMCID.txt",

    # Gene Ontology / protein annotation
    "GenePageIntProTerms.txt",

    # Disease / phenotype-related annotation
    "XenbaseDiseaseOntologyData.txt",
]


def download_file(filename: str):
    url = BASE_URL + filename
    out = DATA / filename

    print(f"\nDownloading {filename}")
    print(f"  URL: {url}")

    try:
        with httpx.stream(
            "GET",
            url,
            timeout=120,
            follow_redirects=True,
        ) as response:

            response.raise_for_status()

            with out.open("wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

        print(f"  Saved: {out}")

    except Exception as e:
        print(f"  ERROR: {e}")


for filename in FILES:
    download_file(filename)

print("\nXenbase data update complete.")