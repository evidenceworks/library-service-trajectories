# Open premises and staffed service in Finnish library territories

This repository reproduces the descriptive analysis of opening hours and library-paid worked FTE in 268 consistent mainland Finnish library reporting territories. It compares 2022–2025 and 2023–2025 trajectories by prior population history, with population and equal-territory weights. Missing source hours remain explicit logical domains.

## Reproduce the reported results

Open [notebooks/reproduce.ipynb](notebooks/reproduce.ipynb) in Jupyter and run all cells. For Colab, use **File → Upload notebook**, then upload a repository ZIP when the first cell requests it. The ZIP should contain `library-service-trajectories/` at its root. The notebook checks the scientific inputs, regenerates the compact tables and verifies the reported comparisons. It then draws Figures 1–4 from the regenerated values. No provider download is needed.

The core run takes about five seconds on the tested Windows machine. The four figures take a few more seconds after the plotting library is installed. Dependency installation time depends on the environment.

## Files

- `data/`: compressed analytic records, territory definitions, source corrections and scientific result references. [Data guide](data/README.md) and [Data S1 crosswalk](data/workbook-guide.md).
- `code/reproduce.py`: rational source-domain calculations and descriptive projections.
- `code/check.py`: input integrity and result checks.
- `results/`: event comparisons, trajectory counts, staffing, denominator reversals and region-omission diagnostics.
- `figure-data/`: endpoint changes and linked denominator components for Figures 1 and 4. Figures 2 and 3 use `results/annual-totals.csv`.
- `code/figures.py`: figure regeneration. SVG files are written to `figures/` when it runs.
- `checksums.sha256`: the eight stable scientific inputs.

## Data

The analysis uses reported service-location hours, which may add simultaneous hours across branches. The unit is a consistent reporting territory, not a branch or individual resident. The deposited layer contains analytic records and source-cell locators, rather than original provider workbooks.

Source: Finnish Public Libraries Statistics, 2017 and 2022–2025, Ministry of Education and Culture, Finland, https://tilastot.kirjastot.fi/. Statistical data are licensed under [CC BY 4.0](https://tilastot.kirjastot.fi/intro.php?lang=en). Prior population references and municipal classifications: Statistics Finland, [open data terms](https://stat.fi/en/about-us/get-to-know-statistics-finland/legislation/terms-of-use). See [third-party terms](licenses/third-party.md) for the separate attribution and rights.

## Local use

Use Python 3.12. From the repository root:

```bash
python -m pip install -r requirements.txt
python code/check.py
python code/reproduce.py
python code/check.py
python code/figures.py
```

Only NumPy is needed for the core calculation. Matplotlib draws the optional figures. When either package is missing, the notebook installs the pinned requirements. It keeps an existing installation when both packages are already available. To use the pinned versions locally, run the installation command above in a fresh environment.

## Scope of reproduction

The normal run recomputes the event domains, both weightings, both endpoint comparisons, 2% and 5% sensitivities, trajectory counts, current-resident denominator components, region omissions and descriptive projection domains. It checks 22 regenerated numerical objects against stored scientific references before exporting the compact results.

The geographic correspondence, population reference adjudication and correction decisions enter as deposited analytic inputs. The run checks their internal consistency; it does not reconstruct them from original workbooks, population responses or documentary evidence. The historical comparison value of 458 FTE for Helsinki is recorded as provenance only; the reported 451 enters the calculation. No excluded aggregate or alias row is needed for the analysis. See the [data guide](data/README.md) for these boundaries.

Siuntio remains in the frame. Its 2025 opening-hour vector has no finite upper limit. A lower bound is not a filled observation, and a source-identification envelope is not a confidence interval. These are descriptive territory comparisons; they do not identify causal effects, individual access or welfare loss.

## Licenses

Original code is MIT. Repository-authored documentation and derived outputs are CC BY 4.0 where the contributors hold the rights. Provider material retains its source terms. [LICENSE](LICENSE) and [licenses/third-party.md](licenses/third-party.md) give the split.
