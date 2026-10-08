# AGENTS.md: context for AI coding assistants

(Works as `CLAUDE.md` too: copy or symlink it.) Read this file and `PLAN.md` fully before doing anything.

## What this project is

A portfolio project for a junior Business / Data Analyst job search. The owner (Daisy) is a Technical Project Manager moving into analytics.
The goal is **evidence of real analytical skill**: SQL (CTEs, window functions), dimensional modelling, Power BI/DAX, and clear business recommendations.
Business question: *How much do late deliveries cost in satisfaction and repeat business, and which sellers, categories and regions drive them?*

## Your role

You are a pair programmer, not the author of the conclusions. Write and debug code, explain choices, and review work.
Daisy must be able to explain every query and chart in a live interview, so **explain what you write**, prefer simple readable SQL over clever SQL, and comment the reasoning.

## Hard rules (do not break)

1. **Never invent numbers.** Any figure placed in a README, memo, or doc must come from a query or script you ran, and you must cite the file that produced it. If you did not run it, write `TBD`.
2. **Do not commit data.** `data/raw/` is gitignored. Never commit CSVs, `.env`, passwords, or `.pbix` files larger than 50 MB.
3. **No company data.** This project uses only the public Olist dataset. Nothing from Agile Robots or any employer.
4. **Raw is read-only.** Never edit `raw` tables. Fix problems in `staging`, and record each fix in `docs/decisions.md`.
5. **Ask before** changing the metric definitions in `README.md`, dropping rows, or changing the star-schema grain.
6. **Association, not causation.** Do not write "caused by". Write "associated with".
7. Keep every SQL file re-runnable (`CREATE SCHEMA IF NOT EXISTS`, `DROP ... IF EXISTS` / `CREATE OR REPLACE`).

## Environment

- PostgreSQL 16 in Docker (`docker compose up -d`). Connection settings are in `.env` (copy from `.env.example`).
- Schemas: `raw` (all TEXT), `staging` (typed views), `mart` (star schema).
- Python 3.11+ (`pip install -r requirements.txt`) for loading and QA scripts only. Analysis is in SQL.
- Power BI Desktop is Windows-only. Daisy builds the report herself; you can write DAX and check the measures against SQL.

## Conventions

- SQL: lowercase keywords or uppercase, but be consistent. Snake_case names. One CTE per logical step, named for what it holds. Each analysis file starts with a header comment: question, grain, definitions used, and (after running) the finding.
- Analysis files are numbered: `sql/analysis/NN_topic.sql`.
- Delay buckets (exact labels): `On time / early`, `1-3 days late`, `4-7 days late`, `8+ days late`, `Not delivered`.
- Minimum volume for rankings of sellers: at least 30 delivered orders (document the threshold in the file header).
- Dates: store timestamps as `timestamp`; compute delay in whole days with `(delivered::date - estimated::date)`.

## Known Olist data pitfalls (verify each during profiling and record results in `docs/data_quality.md`)

- `order_reviews.review_id` is not unique, and an order can have more than one review. Keep one per order with `ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_creation_date DESC, review_answer_timestamp DESC)`.
- An order has several payment rows (instalments, vouchers). **Aggregate payments to one row per order before joining**, or revenue is multiplied.
- An order has several item rows. Do not join items to orders and then sum order-level columns.
- `geolocation` has many rows per zip prefix. Do not join it directly. Aggregate first, or skip it.
- `customer_id` is per order; the person is `customer_unique_id`. Repeat purchase uses `customer_unique_id`.
- Some delivered orders have missing delivery dates; some timestamps are out of order (for example delivered before approved). Count them, decide, document.
- The products file has the misspelled columns `product_name_lenght` and `product_description_lenght`. Some products have no category; the translation table may not cover every category.
- Header names can differ slightly between dataset versions. Check the CSV headers before loading.

## Workflow

Follow the phases in `PLAN.md` in order. At the end of each phase:
1. Run the phase's "done when" checks.
2. Update the checklist in `PLAN.md`.
3. Summarise in 5 lines: what was built, what you found, what is uncertain, what decision Daisy needs to make.

## Definition of done (project)

- Every box in the "Final QA" list in `PLAN.md` is ticked.
- `grep -rn "TBD" README.md docs/` returns nothing.
- Five headline numbers reconcile between SQL and Power BI (`docs/reconciliation.md`).
- A fresh clone can reproduce the database from the README steps.

## Stop and ask Daisy when

- A decision changes a metric definition or excludes more than 1% of rows.
- A result looks surprising or contradicts the README framing. Report it honestly; do not bend the story.
- You are about to delete or overwrite existing work.
