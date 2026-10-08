# PLAN: Olist Delivery Performance & Customer Satisfaction Analytics

Plan written 9 Oct 2026. Effort figures are my estimates, so adjust after week 1 once you know your real pace.

## 1. Goal and success criteria

**Goal:** a finished, public, reproducible analytics project that proves SQL, modelling and Power BI skill, and ends in recommendations a manager could act on.

**Success means:**
- [ ] Fresh clone reproduces the database from the README.
- [ ] Star schema with documented grain, plus data-quality checks that pass.
- [ ] 8 or more analysis queries that use CTEs and window functions on purpose, each with a header and a recorded finding.
- [ ] A 3-page Power BI report with 6 or more DAX measures; 5 headline numbers reconcile to SQL.
- [ ] A one-page memo with 3 to 5 recommendations tied to numbers.
- [ ] You can explain every query and chart without notes.

## 2. Scope

In: delivery performance, review scores, seller/category/state drill-downs, repeat purchase, freight.
Out: machine learning, forecasting, geospatial maps (optional only), anything from your employer.

## 3. Before you start (decisions and setup)

| Item | Note |
|------|------|
| Power BI Desktop | Windows only. If you are on a Mac, use a Windows PC or a VM. The browser version has limited authoring |
| Kaggle account | Needed to download the dataset (manual download is fine) |
| Docker Desktop + `psql` | Or install PostgreSQL directly |
| GitHub repo | Create `olist-delivery-satisfaction-analytics`, public only once Phase 5 is done |
| Question to settle | Which orders count in GMV? Default: exclude `canceled` and `unavailable`. Record in `docs/decisions.md` |

## 4. Timeline (assumes about 10 hours a week)

| Phase | What | Est. hours | Target week |
|-------|------|-----------|-------------|
| 0 | Setup | 3 | 12 to 18 Oct |
| 1 | Load and profile | 5 | 12 to 18 Oct |
| 2 | Staging and star schema | 7 | 19 to 25 Oct |
| 3 | Analysis queries | 10 | 26 Oct to 8 Nov |
| 4 | Power BI report | 10 | 2 to 15 Nov |
| 5 | Memo, README, publish | 5 | by 15 Nov |
| | **Total** | **about 40** | |

This runs alongside SQL practice (about 3 hours a week) and PL-300 study. If you fall behind, shrink Phase 3 to the 6 core queries (marked ★), not Phase 5.

## 5. Phases

### Phase 0: setup (3 h)
- Create the repo, copy in this folder, `git init`, first commit (no data).
- `cp .env.example .env`, set a password, `docker compose up -d`, check `psql` connects.
- Download the 9 CSVs into `data/raw/`.

**Done when:** `\dn` in psql lists nothing broken, and `data/raw/` contains the CSVs and is gitignored.

### Phase 1: load and profile (5 h)
- Run `sql/00_raw_schema.sql` and `sql/01_load_raw.sql`. Fix header mismatches if your CSVs differ.
- Write `docs/data_quality.md` with, for each table: row count, key uniqueness, null counts for important columns, orphan keys between tables, odd values (negative prices, out-of-order timestamps), and duplicates (`review_id`, multiple reviews per order, multiple payments per order).
- Count orders by `order_status` and decide the "delivered" definition.

**Done when:** `docs/data_quality.md` has real counts for all 9 tables and lists each pitfall from `AGENTS.md` as confirmed or not.

### Phase 2: staging and marts (7 h)
- `sql/02_staging.sql`: typed views (`staging.orders`, `items`, `payments_per_order`, `reviews_latest`, and so on). Cast timestamps and numerics. Deduplicate reviews with `ROW_NUMBER()`. Aggregate payments to one row per order. Join the category translation.
- `sql/03_marts.sql`: build `mart.dim_date`, `dim_customer`, `dim_seller`, `dim_product`, `fact_orders`, `fact_order_items` (spec in section 7). Add primary keys and indexes.
- Add checks (a SQL file or script): row counts match staging, `fact_orders.order_id` is unique, no null keys, `SUM(price)` in the fact table equals the staging total.
- Record every cleaning decision in `docs/decisions.md`.

**Done when:** all checks pass and you can draw the schema from memory.

### Phase 3: analysis queries (10 h)
Write the queries in section 6. For each, run it, read the result critically, and write the finding into the file header. Save result tables as CSV in `docs/results/` if you want them quoted.

**Done when:** each ★ query has a finding written in its header.

### Phase 4: Power BI (10 h)
- Connect to the `mart` schema (Import mode). Build the model with the relationships from the schema. Hide key columns. Mark `dim_date` as a date table.
- Write the DAX measures in section 8, in a dedicated `_Measures` table.
- Build the three pages in section 9.
- Reconcile 5 headline numbers with SQL in `docs/reconciliation.md` (SQL value, Power BI value, match yes/no).
- Export screenshots to `images/` and a PDF to `docs/dashboard.pdf`. Do not rely on "Publish to web" (it needs a work/school account).

**Done when:** reconciliation shows all five numbers match (or each difference is explained).

### Phase 5: memo, README and publish (5 h)
- `docs/memo.md`: one page. Question, 3 to 5 findings with numbers, 3 to 5 recommendations, limitations.
- Fill every `TBD` in `README.md` with real numbers. Add screenshots.
- Pin the repo on your profile. Add topics: `sql`, `postgresql`, `power-bi`, `data-analysis`, `portfolio`.

**Done when:** `grep -rn "TBD" README.md docs/` is empty and a friend can follow the README cold.

## 6. SQL analysis catalogue (`sql/analysis/`)

| File | Question | Techniques | ★ |
|------|----------|-----------|---|
| `01_kpi_overview.sql` | GMV, orders, AOV, customers, monthly trend with month-on-month change | CTE, `LAG`, date truncation | ★ |
| `02_delivery_performance.sql` | Delivery days and on-time rate by month; median and 90th percentile delivery time | `percentile_cont`, conditional aggregation | ★ |
| `03_delay_vs_review.sql` | Average score and share of 1 to 2 star reviews by delay bucket | `CASE` buckets, aggregation | ★ |
| `04_state_delay_hotspots.sql` | Which states have the worst on-time rate and the biggest satisfaction gap (minimum volume) | `RANK`, `HAVING` | ★ |
| `05_seller_scorecard.sql` | Seller quintiles by late rate and score; how concentrated are late orders in the worst sellers | `NTILE`, cumulative `SUM() OVER` (Pareto) | ★ |
| `06_category_analysis.sql` | Categories with low scores and high lateness; freight share of price | joins, ratios, `RANK` | |
| `07_repeat_purchase_cohorts.sql` | Repeat rate by first-order delay bucket; cohort retention by first-purchase month | `MIN() OVER`, cohort CTEs | ★ |
| `08_freight_and_value.sql` | Does freight share relate to lateness or score | aggregation, buckets | |
| `09_payment_mix.sql` | Payment type and instalments vs order value | aggregation | |

Each file starts with this header:

```sql
-- Question:
-- Grain:
-- Definitions used (see README): 
-- Filters and why:
-- Finding (fill after running; real numbers only):
```

## 7. Data model spec (change only with a note in `docs/decisions.md`)

| Table | Grain | Key columns |
|-------|-------|-------------|
| `mart.fact_orders` | one row per order | `order_id` (PK), `customer_unique_id`, `customer_state`, `order_status`, purchase / approved / carrier / delivered / estimated timestamps, `delivery_days`, `delay_days`, `is_delivered`, `is_late`, `delay_bucket`, `review_score`, `items_count`, `items_value`, `freight_value`, `payment_value` |
| `mart.fact_order_items` | one row per order item | (`order_id`, `order_item_id`) PK, `product_id`, `seller_id`, `price`, `freight_value`, `shipping_limit_ts` |
| `mart.dim_customer` | one row per `customer_unique_id` | first order date, order count, first-order state |
| `mart.dim_seller` | one row per seller | city, state |
| `mart.dim_product` | one row per product | category (pt and en), weight, photo count |
| `mart.dim_date` | one row per day | year, quarter, month, month name, week, weekend flag |

## 8. DAX measures (put in a `_Measures` table; verify each against SQL)

- `GMV` = sum of item price
- `Orders` = distinct count of order IDs
- `AOV` = divide GMV by Orders
- `Delivered Orders` = distinct orders where `is_delivered` is true
- `On-Time %` = divide late-false delivered orders by delivered orders
- `Avg Review Score` = average of review score
- `Low Score %` = share of reviews with score 1 or 2
- `Avg Delay Days (late only)` = average delay days where `is_late` is true
- `GMV MoM %` = GMV against the previous month, using time-intelligence on `dim_date`
- `Repeat Customer %` = customers with 2 or more orders, divided by customers

Write each with `DIVIDE()` to avoid divide-by-zero, add a short comment on each, and keep a table of measure → definition in `docs/`.

## 9. Dashboard spec

1. **Executive overview:** KPI cards (GMV, Orders, AOV, On-Time %, Avg Score), monthly GMV trend, on-time % trend.
2. **Delivery performance:** score by delay bucket (the key chart), on-time % by state (bar, sorted), delay distribution.
3. **Seller and category scorecards:** seller table with late % and score, category bars, a Pareto of late orders by seller, slicers for state, category and date, and a drill-through from seller to its orders.

Design rules: one idea per page, titles that state the takeaway ("Orders delivered 8+ days late score X lower"), consistent colours, no 3D, no pie charts with more than 4 slices.

## 10. Risks and how to handle them

| Risk | Handling |
|------|----------|
| Joins multiplying revenue | Check totals after every join against staging |
| Over-claiming | Use "associated with"; list limitations |
| Time overrun | Cut optional queries (06 to 09) and optional map first |
| Repeat purchase rate very low | Report it honestly; it is a finding, not a failure |
| Power BI unavailable | Do phases 0 to 3 and 5 now; do Phase 4 when you have a Windows machine |

## 11. Final QA checklist

- [ ] Fresh clone reproduces the DB following the README
- [ ] No `TBD` in README or docs
- [ ] No data files, `.env` or passwords committed (`git log -p | grep -i password` is clean)
- [ ] 5 numbers reconciled in `docs/reconciliation.md`
- [ ] Every analysis file has a filled header
- [ ] Screenshots render in the README
- [ ] Repo pinned, topics added, description set

## 12. Resume bullet template (fill ONLY after the work is done)

> Built a PostgreSQL star schema from 9 Olist marketplace tables (about [N] orders) and a 3-page Power BI report; used CTEs and window functions to show that orders delivered [X]+ days late score [Y] points lower and that [Z]% of late orders come from [W]% of sellers.

## 13. Interview questions to prepare

1. Why a star schema instead of querying the raw tables?
2. What is the grain of `fact_orders`, and what goes wrong if you join payments before aggregating?
3. Walk me through your Pareto query. Why `NTILE` there?
4. How did you define "late", and what are its weaknesses?
5. How did you deduplicate reviews, and why the latest one?
6. Which result surprised you, and what did you do about it?
7. How do you know your Power BI numbers are right?
8. What would you do next with more time or data?
9. What is the difference between association and causation in this analysis?
10. What recommendation would you make first, and why?
