# Data S1 and the repository

Data S1 accompanies the article separately. It is a readable record of accepted values, source annotations and detailed calculations; it is not an executable workbook. This repository recomputes the central results from deposited analytic records.

The workbook’s **Canonical file** and **Canonical row (header = 1)** columns refer to original calculation records. Paths beginning with `outputs/`, `evidence/` or `data/national_panel.csv` are provenance labels, not links to files of those names in this public tree. For CSV-backed sheets, row 1 is the header. JSON-backed sheets use zero-based object indices instead.

Use the crosswalk below to locate the public counterpart. A compact or selected counterpart is not a row-for-row copy of the entire sheet. Where the table below says that a detailed calculation is checked during reproduction, the run creates it temporarily before compact export. The workbook also contains source documentation outside that calculation route.

## Sheet crosswalk

| Data S1 sheet | Public counterpart | Relationship |
| --- | --- | --- |
| Event comparisons | [`results/event-differences.csv`](../results/event-differences.csv) | Same records; join by source domain, period, threshold and weight. |
| Event prevalences | [`results/event-prevalence.csv`](../results/event-prevalence.csv) | Same records; also join by population history. |
| Joint trajectories | [`results/trajectory-summary.csv`](../results/trajectory-summary.csv) | Compact counts for the two endpoint periods. The workbook retains territory-level records and intervening changes; the run calculates and verifies that detail. |
| Staffing and event | [`results/event-staffing.csv`](../results/event-staffing.csv) | Same records; join by source domain, population history, event status and FTE direction. |
| Denominator counts | [`results/denominator-reversals.csv`](../results/denominator-reversals.csv) | Same records; join by period, source domain, measure and definition. |
| Annual context domains | [`results/annual-totals.csv`](../results/annual-totals.csv) | Same records; join by year, source domain, population history and measure. |
| Frame | [`data/territories.csv`](../data/territories.csv) | Selected historical territory fields. Source sums and status annotations remain in the workbook only; see the note below. |
| Memberships | [`data/source-records.csv.gz`](../data/source-records.csv.gz) | Member codes are retained in source-system records, not as a separate copy of the workbook’s membership-row table. |
| Annual observations | [`data/territory-panel.csv.gz`](../data/territory-panel.csv.gz) | Selected panel columns; join by territory and year. |
| Annual hour states | [`data/territory-panel.csv.gz`](../data/territory-panel.csv.gz) | Selected panel columns; join by territory and year. Raw blanks remain blank. |
| Territory hour domains | See relationship | Detailed domains are calculated and checked during reproduction. The workbook retains them; the normal run does not save a separate public table. |
| Opening changes | [`figure-data/endpoint-changes.csv`](../figure-data/endpoint-changes.csv) | Selected S/T changes for the two endpoint periods under published accounting. The workbook retains all modes and periods; the run calculates and checks that detail. |
| Paid staffing | [`data/territory-panel.csv.gz`](../data/territory-panel.csv.gz) | Annual FTE is in paid_fte; join by territory and year. The run also calculates and checks the detailed staffing table. |
| Denominator components | [`figure-data/denominator-components.csv`](../figure-data/denominator-components.csv) | Published-accounting component rows, including exact rational limits and the joint constraint. The workbook also retains the conservative scenario. |
| Denominator cases | See relationship | Territory-level cases are calculated and checked during reproduction. The workbook retains them; compact counts are in results/denominator-reversals.csv. |
| Event cases | See relationship | Territory-level event bounds are calculated and checked during reproduction. The workbook retains them; compact prevalences are in results/event-prevalence.csv. |
| Region contrasts | [`results/region-omission-differences.csv`](../results/region-omission-differences.csv) | Same records; also join by omitted region. |
| Region prevalences | See relationship | Detailed prevalences are calculated and checked during reproduction. The workbook retains them; the public table retains the corresponding contrasts. |
| Reporting changes | See relationship | Detailed source-record comparisons are calculated and checked during reproduction. The workbook retains them. |
| Projection domains | [`results/projection-domains.csv`](../results/projection-domains.csv) | Same coefficient records; join by model and term. Floating-point tolerances apply, as explained in the data guide. |
| Projection regions | [`results/projection-support.csv`](../results/projection-support.csv) | Same region-support records. |
| Projection design | See relationship | The workbook retains the design summary. The run constructs the projections from deposited territory and panel data; there is no separate public design-summary file. |
| Coverage | See relationship | Detailed coverage is calculated and checked during reproduction. The workbook retains it. |
| Blank hour cells | [`data/missing-hour-domains.csv`](../data/missing-hour-domains.csv) | Selected fields from the uncertainty records; join by source record and field. |
| Source markers | See relationship | The workbook includes marker counts from the source review. Analytic source records retain their raw states, but excluded aggregate and alias rows are not deposited; the normal run does not reconstruct this complete marker table. |
| Source corrections | [`data/source-corrections.csv`](../data/source-corrections.csv) | Selected correction and comparison fields with concise source attribution. Raw values and comparison values are not automatically accepted replacements. |
| Native field dictionary | See relationship | The workbook retains provider filenames, hashes and native field/header bindings. Original provider workbooks are not included or reread by the normal run. |
| Annual identities | See relationship | Detailed identity checks are calculated and verified during reproduction. The workbook retains them. |
| Projection specifications | [`results/projection-models.json`](../results/projection-models.json) | Flattened model attributes; Object index is zero-based. Match Specification to model. |
| Missing event witnesses | [`results/unknown-event-witnesses.json`](../results/unknown-event-witnesses.json) | Two endpoint witnesses per object. Object index is zero-based; these are feasible states, not observations. |
| Data notes | [`data/README.md`](../data/README.md) | Workbook reading conventions; the repository data guide supplies the analytic definitions and reproduction boundary. |

## Matching labels and keys

Workbook headings are reader-facing labels. `Territory ID` corresponds to `common_territory_id`, `Source domain` to `source_scenario`, `Prior population history` to `population_context` and `Measure` to `field`. Published accounting and conservative relaxation correspond to `published_accounting` and `conservative_relaxation`; prior contraction and other history correspond to `declining` and `nondeclining`. S, M, U and T correspond to the four hour fields defined in the data guide. Match records by their scientific keys rather than relying on row order after filtering.

Source-system identifiers are year, worksheet and row locators. A membership table may have several rows for one source record. Do not sum its hours once per membership: the analytic run counts each source record once.

## Historical source annotations and accepted values

The Frame sheet preserves historical source-review annotations; `territories.csv` retains only the fields needed for the analysis. In particular, the Alavus 2017 source sum of 11,097 and its unresolved source-conflict label describe the original source discrepancy. They do not replace the accepted population of 11,907 in `territory-panel.csv.gz`. The Source corrections sheet and `source-corrections.csv` document the official overlay. Use `population_accepted`, `population_2017_accepted` and `population_2022_accepted` for the analysis, not the historical source-sum or status columns in the frame.

The same distinction applies to the six native municipality-code discrepancies: documentary member codes determine the accepted links while conflicting native codes remain recorded. Helsinki’s reported 2023 FTE is 451. The comparison value 458 is provenance, not a correction used in the analysis.

Source bounds are not filled observations. Conditional zeros remain raw blanks and Siuntio’s four 2025 hour values remain unbounded above. The workbook and public calculations preserve this distinction.
