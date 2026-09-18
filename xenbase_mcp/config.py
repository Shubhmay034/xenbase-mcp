from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

GENE_INFO_URL = "https://www.xenbase.org/xenbase/static/genePageReports/GenePageGeneralInfo_AllGenes.txt"
HUMAN_ORTHOLOG_URL = "https://www.xenbase.org/xenbase/static/genePageReports/XenbaseGeneHumanOrthologMapping.txt"
