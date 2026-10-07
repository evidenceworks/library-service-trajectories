# Library service trajectories

This repository contains the data and code used to reproduce the reported comparisons and Figures 1–4 for 268 mainland Finnish library reporting territories.

## Run in Google Colab

[Open in Colab](https://colab.research.google.com/github/evidenceworks/library-service-trajectories/blob/main/notebooks/reproduce.ipynb)

[Download Colab reproduction bundle](https://github.com/evidenceworks/library-service-trajectories/releases/download/reproduction-v1/colab-reproduction.zip)

1. Open the notebook in Colab.
2. Choose **Runtime → Run all**.
3. Download the reproduction bundle using the link above.
4. Upload `colab-reproduction.zip` when prompted.
5. When the run finishes, Colab downloads `reproduction-output.zip`.

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

- `data/` — analytic data and field definitions.
- `code/` — analysis, checks and figure generation.
- `results/` — reproduced tables and diagnostics.
- `figure-data/` — data used by the figures.
- `figures/` — Figures 1–4 in SVG format.
- `notebooks/reproduce.ipynb` — Colab/Jupyter reproduction notebook.
- `checksums.sha256` — checksums for the reference inputs.

For field definitions and the Data S1 crosswalk, see [`data/README.md`](data/README.md) and [`data/workbook-guide.md`](data/workbook-guide.md).

## Data and licenses

Service data come from Finnish Public Libraries Statistics, Ministry of Education and Culture, Finland: https://tilastot.kirjastot.fi/. Statistical data are available under CC BY 4.0. Population references and municipal classifications come from Statistics Finland under its open-data terms.

Original repository code is MIT licensed. Repository-authored documentation and derived outputs use CC BY 4.0 where the contributors hold the rights. Third-party material retains its source terms. See [`LICENSE`](LICENSE) and [`licenses/third-party.md`](licenses/third-party.md).
