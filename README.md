# Library service trajectories

This repository reproduces the descriptive analysis of opening hours and library-paid worked FTE across 268 consistent mainland Finnish library reporting territories. It reproduces the reported comparisons, sensitivity analyses and Figures 1–4 from the deposited analytic inputs.

## Run in Google Colab

[Open in Colab](https://colab.research.google.com/github/evidenceworks/library-service-trajectories/blob/main/notebooks/reproduce.ipynb)

[Download repository ZIP](https://github.com/evidenceworks/library-service-trajectories/archive/refs/heads/main.zip)

1. Open the notebook in Colab.
2. Click **Runtime → Run all**.
3. Download the repository ZIP using the link above.
4. Upload that ZIP when the first notebook cell asks for it.

## Run locally

Python 3.12 is recommended. From the repository root:

```bash
python -m pip install -r requirements.txt
python code/check.py
python code/reproduce.py
python code/check.py
python code/figures.py
```

## Repository contents

- `data/` — analytic records, territory definitions, source corrections and scientific reference objects.
- `code/` — integrity checks, reproduction code and figure generation.
- `results/` — regenerated result tables and diagnostics.
- `figure-data/` — source data used by the figures.
- `figures/` — regenerated SVG figures.
- `notebooks/reproduce.ipynb` — the guided reproduction notebook.
- `checksums.sha256` — checksums for the stable scientific inputs.

For field definitions, source boundaries and the Data S1 crosswalk, see [`data/README.md`](data/README.md) and [`data/workbook-guide.md`](data/workbook-guide.md).

## Data and licenses

Service data come from Finnish Public Libraries Statistics, Ministry of Education and Culture, Finland: https://tilastot.kirjastot.fi/. Statistical data are available under CC BY 4.0. Population references and municipal classifications come from Statistics Finland under its open-data terms.

Original repository code is MIT licensed. Repository-authored documentation and derived outputs use CC BY 4.0 where the contributors hold the rights. Third-party material retains its source terms. See [`LICENSE`](LICENSE) and [`licenses/third-party.md`](licenses/third-party.md).

The deposited repository starts from analytic records and documented source decisions. It does not reconstruct the original provider workbooks or the documentary source-adjudication process.
