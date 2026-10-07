# Data guide

The deposited data describe 268 common reporting territories across 2017 and 2022–2025. Each source-system record contributes once. Historical correspondence and whole-participant envelopes reconcile mergers, partial transfers and joint reporting without fractional allocation of hours. Consortium membership alone does not define a territory.

## Analytic tables

| File | Rows | Role |
| --- | ---: | --- |
| `territory-panel.csv.gz` | 1,340 | One territory-year row; 2017 is population-only and 2022–2025 supply the core outcomes. |
| `source-records.csv.gz` | 1,384 | Reported system-year values, raw states, cell locators and documentary member codes. |
| `territories.csv` | 268 | Fixed historical envelopes, annual source-record links, 2022 regions and population-based municipality group shares. |
| `source-corrections.csv` | 8 | One official population overlay, six documentary municipality-code mappings and one FTE comparison. Raw source values remain unchanged. |
| `missing-hour-domains.csv` | 16 | Raw blank hour cells and the published-accounting and conservative domains. |
| `projection-reference.csv` | 24 | Reference coefficient domains for the two descriptive models; used only to check recomputed coefficients. |
| `expected-results.json` | 22 objects | SHA-256 references for detailed calculations before compact export. |
| `public-results-reference.json` | 12 files | Scientific references for compact tables and figure data. |

CSV files use UTF-8. The `.gz` files decompress to ordinary CSV. Input numbers retain the published decimal values. Empty hour cells denote missing source observations, never numeric zero.

## Reading Data S1 alongside this repository

Data S1 is the article’s supplementary workbook, supplied separately from this repository. Its canonical paths identify the original calculation records, not paths in this public tree. The [workbook crosswalk](workbook-guide.md) maps all 31 sheets to the deposited data, compact results or detailed calculations. It also distinguishes historical source annotations from the accepted population and membership fields.

## Main fields

`common_territory_id` is a study identifier for a consistent envelope. `record_id` is year, worksheet and Excel row, not a provider-issued longitudinal ID. Pipe-separated lists link annual source records and documentary municipality codes. Region codes refer to 2022. The cross-region territory is `CRT_171+178+681`; it is never counted twice.

| Field | Meaning |
| --- | --- |
| `staff_service_hours` | S: opening with professional staff serving users. |
| `staff_present_no_service_hours` | M: staff present without service; this may include other personnel. |
| `no_library_staff_hours` | U: opening without library-paid staff; some premises or functions may be unavailable. |
| `total_hours` | T: total reported opening. |
| `paid_fte` | Library-paid worked FTE, not an imputation for hours. |
| `population_raw_source_sum` | Unchanged sum of population values in library source records. |
| `population_accepted` | Prior official reference for 2017 and 2022; reported annual population for later years. |
| `population_2017_accepted`, `population_2022_accepted` | Fixed prior population references on the common territory. |
| `population_context` | Declining when population in 2022 is below that in 2017; otherwise nondeclining. |
| `prior_annualized_population_change` | log(population 2022 / population 2017) / 5. |
| `rural_population_share_2022` | Population share in municipality group 3; mixed territories retain their shares. |

The `_raw`, `_state` and `_cell` columns in `source-records.csv.gz` preserve native values, markers and locations. Actual core hours have numeric or blank states. The missing M field in the 2017 schema remains `field_not_in_schema`; no 2017 service trajectory is inferred.

## Definitions used by the calculation

The focal event is T at the endpoint at least as large as at the baseline and S strictly smaller. The normal comparisons use 2022–2025 and 2023–2025. The 2% and 5% staffed-decline sensitivities require a positive staffed baseline and retain zero-baseline cases separately. Population weighting always uses the fixed 2022 population; the counterpart gives each applicable territory equal weight.

Complete reported hour vectors satisfy T = S + M + U exactly. Under `published_accounting`, incomplete vectors retain the nonnegative residual domain subject to this identity. Twelve blanks have a conditional zero residual; they remain blanks in the source table. Under `conservative_relaxation`, missing modes are separately bounded by the observed total. Siuntio has a completely unknown 2025 vector: all four hours have nonnegative, unbounded domains. Its components share an unknown endpoint state, and its event has both feasible true and false states.

Current-resident decomposition uses the same H0 and H1 in all components:

```text
ratio change = H1/N1 - H0/N0
hours component = (H1-H0) × (1/N0+1/N1)/2
population component = (1/N1-1/N0) × (H0+H1)/2
```

Component extrema cannot be chosen independently. `figure-data/denominator-components.csv` retains exact rational limits and the joint constraint. `unbounded` and `-unbounded` denote infinite limits.

The projections describe 2022–2025 S change per 1,000 fixed 2022 residents. The first model uses prior population change. The second adds baseline population, staffed intensity, rural share and region indicators, excluding the one cross-region territory. Both retain Siuntio through a shared unbounded response increment. Lower anchors are not point estimates. Observed-response fits are separate sensitivities. Projection arithmetic uses floating linear algebra; checks allow 1e-10 absolute or relative error across numerical libraries while requiring identical support and bound directions. All other core calculations use exact rational arithmetic.

## Provenance and reproduction boundary

Source: Finnish Public Libraries Statistics, 2017 and 2022–2025, Ministry of Education and Culture, Finland, https://tilastot.kirjastot.fi/. Population references and annual municipality classifications come from Statistics Finland open statistical data. Annual hour definitions are documented in the [2022](https://www.kirjastot.fi/sites/default/files/content/Yleisten_kirjastojen_tilasto-ohjeet_2022_0.pdf), [2023](https://www.kirjastot.fi/sites/default/files/content/Yleisten_kirjastojen_tilasto-ohjeet_2023.pdf), [2024](https://www.kirjastot.fi/sites/default/files/content/Yleisten_kirjastojen_tilasto-ohjeet_2024.pdf) and [2025](https://www.kirjastot.fi/sites/default/files/content/Yleisten_kirjastojen_tilasto-ohjeet_2025.pdf) instructions. Those documents are linked, rather than redistributed or relicensed.

The analytic layer includes the Alavus 2017 population overlay: raw 11,097, official reference 11,907. It also retains the six conflicting native municipality codes while using exact-name documentary membership. Helsinki 2023 worked FTE is the reported 451; the historical comparison value 458 does not replace it. The causes of these discrepancies are not asserted.

The run verifies the deposited decisions and recomputes their numerical consequences. It does not independently re-adjudicate geographic correspondence, validate historical population responses or reread original workbook cells. The five national aggregate rows and two population-only aliases excluded before the analytic layer are not deposited; their marker profiles are outside the reproduction route. Annual 2023–2025 population uses reported source sums under the January 1 guide binding, without a new independent population parity audit. No central reported result is substituted by a stored result table.
