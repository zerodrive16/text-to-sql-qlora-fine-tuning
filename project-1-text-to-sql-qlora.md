# Project 1 – Text-to-SQL with Custom QLoRA Fine-Tuning

A portfolio project in which a small language model is fine-tuned to translate natural-language business questions into correct SQL for a fixed database schema, then served as a callable tool.

---

## Task

Build a system that turns natural-language business questions (e.g. *"revenue per region last quarter"*) into correct SQL against a fixed database schema, executes that SQL, and returns the result.

The core and the genuinely new skill here is **fine-tuning a small LLM (1–3B parameters) yourself using QLoRA on Colab** — currently one of the most in-demand ML capabilities, and one not yet represented in the portfolio. This is "training your own model" in a way that carries real weight, not just tuning a classifier.

What makes it more than a toy: the model is measured with **SQL Execution Accuracy** — the generated query is actually run against the database and the *result set* is compared, not the raw text — against a held-out evaluation set. The goal is to show that the fine-tuned small model beats a larger base model **on your own schema**. That metric is exactly what separates a demo from something deployable.

**Definition of Done:**
- A running database with a realistic business schema (revenue, customers, regions, products, orders).
- A QLoRA adapter trained on Colab.
- An evaluation table proving *"base model X% Execution Accuracy → my fine-tune Y%"*.
- An MCP server exposing a `query_database` tool that Claude or another client can call.
- A single `docker compose up` that brings up database + inference + MCP together.
- A README with the result table and an architecture diagram — the actual portfolio artifact.

---

## Example (Task in Action)

Assume this minimal schema:

```sql
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, region TEXT);
CREATE TABLE orders   (id INTEGER PRIMARY KEY, customer_id INTEGER,
                       order_date DATE, amount REAL);
```

1. **The user types a question (text only):** *"What was the revenue per region this quarter (Q3 2026)?"* — they never see SQL and don't know the schema.
2. **Your code builds the real prompt:** your Python code prepends the schema to the question and sends both to the model.
3. **The model generates SQL** as a plain text string (intelligent autocompletion — it has learned from thousands of *(schema + question → SQL)* examples which tokens correctly continue this kind of prompt). Up to this point the model has never touched the database.
4. **Your code executes that SQL string against the DB** (`cursor.execute(...)` → `cursor.fetchall()`).
5. **The DB returns rows** with real numbers.
6. **Optional:** a small "explainer" LLM turns the table into a prose sentence.

> **The one thing to remember:** the model only ever produces *text*. Your code is the bridge that runs that text as a read-only query against the DB. That is exactly why the safety guardrails live in your code, not in the model.

---

## Input and Output

### Input — the prompt actually sent to the model

The model never receives the bare question. Your code glues the fixed schema in front of it:

```
You are an SQL expert. Given the following schema, write a
SQLite query that answers the question. Return SQL only.

Schema:
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, region TEXT);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER,
                     order_date DATE, amount REAL);

Question: What was the revenue per region this quarter (Q3 2026)?
```

The schema is "fixed" because it is injected automatically on every question, so the model always knows which tables and columns exist. Instruct-tuned models expect a specific chat template (system / user / assistant roles) — each training example must use exactly this format, or the model learns format garbage. Rule of thumb: **schema + question in, pure SQL out.**

### Output — what to expect from the model

A pure text string containing the query:

```sql
SELECT c.region, SUM(o.amount) AS revenue
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.order_date >= '2026-07-01' AND o.order_date < '2026-10-01'
GROUP BY c.region;
```

After your code executes it, the database returns the actual result:

```
region | revenue
-------+-----------
Nord   | 1,240,000
Süd    |   980,000
West   |   610,000
```

Optionally, the explainer LLM renders this as: *"In Q3 2026, revenue was 1.24M (Nord), 0.98M (Süd) and 0.61M (West)."*

---

## Tools & Technology (Stack)

| Layer | Choice | Note |
|---|---|---|
| Base model | **Qwen2.5-Coder-Instruct** (1.5B to start, optionally 3B) | Current standard for small Text-to-SQL; check at start whether a small Qwen3-Coder dense variant exists |
| Fine-tuning | **QLoRA** via Hugging Face `transformers` + `peft` + `bitsandbytes` + `trl` (SFTTrainer) | 4-bit quantized base + low-rank adapters |
| Training hardware | **Google Colab (T4 GPU)** | NVIDIA + bitsandbytes 4-bit training runs here; an AMD RX 6700 XT does *not* do 4-bit QLoRA cleanly |
| Serving hardware | **Local machine (Ryzen 7 5800X)** | Runs a quantized 1.5–3B GGUF via Ollama comfortably on CPU |
| Database | **SQLite** (entry) → **Postgres** in a container (later) | Realistic business schema |
| Data source | **Spider dataset** + your own synthetic pairs | €5 API budget generates synthetic question–SQL pairs and optionally the prose explainer |
| Serving | **Ollama / vLLM** | Merge adapter → GGUF → quantize → serve |
| Tool interface | **MCP SDK** (official Python) | Exposes `query_database` |
| Orchestration | **Docker Compose** | DB + inference + MCP as one stack |

**Division of labor to remember:** the T4 in the cloud *trains*, your local machine *serves*.

---

## Value to Company

**Self-service analytics.** Business departments can query data without knowing SQL — non-technical staff ask questions in plain language and get answers straight from the data warehouse. This removes the bottleneck of routing every ad-hoc data question through an analyst or engineer.

The honest business case behind the "fixed schema" decision: a real company has *its* data warehouse, not arbitrary databases. Committing to one schema lets the model effectively memorize the tables, columns and typical joins, which is both far easier to build and a faithful match to how this would actually be deployed.

The Execution-Accuracy metric is what makes the result defensible rather than a demo: it demonstrates measurable, deployable quality on the target schema.

---

## Structured Order of Tasks

The evaluation harness is deliberately built **before** training — without a baseline you train blind.

**Phase 0 — Setup & Foundation (~2–3 days)**
Try Colab, enable GPU runtime, mount Google Drive for checkpoints. Get a Hugging Face account + access token, load the Qwen model once, run one prompt through it. Download and inspect the Spider dataset. *Goal: send a single example through the untrained base model and see what comes out.*

**Phase 1 — Target Schema & Database (~3–4 days)**
Design a realistic business schema (e.g. `customers`, `orders`, `order_items`, `products`, `regions` — 5–8 tables with sensible foreign keys). Fill it with synthetic data via a Python script. Create it as a SQLite file (Postgres in Docker comes later).

**Phase 2 — Build Training Data (~1 week, the underestimated part)**
Pull relevant pairs from Spider for general "SQL feel." Generate your own question–SQL pairs for your schema via the Claude API (spend the €5 here), passing the schema and generating across difficulty tiers (easy: one table; medium: one join; hard: multiple joins + aggregation + date logic). **Execute every generated SQL against the DB and keep only what runs cleanly** (automatic quality filtering). Deduplicate and split into train / validation / test (e.g. 80/10/10) — never touch the test set until the end. Target: 800–2000 clean pairs.

**Phase 3 — Eval Harness (~3–4 days, BEFORE training)**
A script: question → model → SQL → execute against DB → compare result set with the reference query → compute Execution Accuracy over the whole test set. Build it robust: broken SQL simply counts as "wrong" without crashing.

**Phase 4 — Measure Baseline (~1–2 days)**
Run the untrained base model (zero-shot and few-shot) through the harness. Record the number — this is your comparison line. Expect solid results with clear gaps on complex joins/aggregations.

**Phase 5 — QLoRA Training on Colab (~1 week incl. iteration)**
Load the model in 4-bit, set the LoRA config (`r` e.g. 8 or 16, `lora_alpha`, `target_modules` = attention projections, dropout). Train with the `trl` SFTTrainer (start: 2–3 epochs, small batch size + gradient accumulation, learning rate ~2e-4). Save checkpoints to Drive (Colab sessions drop). After each run, measure on the validation set — don't just watch the loss.

**Phase 6 — Re-Eval & Error Analysis (~3–4 days)**
Measure the fine-tune on the test set → your second number. Build the base-vs-fine-tune comparison table. Categorize remaining failures (date logic? multiple joins? `GROUP BY`? `HAVING`?) to decide whether round two needs more data of a specific kind. This is exactly what gets asked about in interviews.

**Phase 7 — Serving (~3–4 days)**
Merge the LoRA adapter into the base model, convert to GGUF, quantize, run locally in Ollama. Verify the fine-tuned model gives the same good answers locally as on Colab.

**Phase 8 — MCP Server (~1 week)**
Build a `query_database(question: str)` tool: question → model → SQL → execute → return result. **Guardrails (critical, the real engineering part):** allow read-only statements only (no `DROP`/`DELETE`/`UPDATE`/`INSERT`), auto-inject a `LIMIT`, set timeouts, and return errors cleanly instead of crashing. Optionally use the €5 to render the result as a prose sentence.

**Phase 9 — Docker Compose & Polish (~3–5 days)**
Wire the Postgres container, inference service and MCP server into one `docker-compose.yml`. Write the README with architecture diagram, result table, example queries, and "what I learned."

### Suggested 6-week timeline
- **Week 1:** Phase 0 + 1 — setup running, schema + DB stand, one prompt goes through the base model.
- **Week 2:** Phase 2 — training data (the heavy lift); start Phase 3 in parallel.
- **Week 3:** Phase 3 + 4 — eval harness done, baseline number recorded.
- **Week 4:** Phase 5 — QLoRA training, several iterations.
- **Week 5:** Phase 6 + 7 — error analysis, retrain if needed, local serving.
- **Week 6:** Phase 8 + 9 — MCP server, Docker Compose, README/portfolio.

Weeks 2 (data) and 4 (training) are experientially the grindy ones.

---

### Concepts you must be able to explain (the "5 minutes in the interview" test)

- **Why QLoRA over full fine-tuning?** (memory/cost — LoRA trains ~0.1–1% of parameters; the "Q" is 4-bit quantization of the frozen base, which is why a 3B model fits on a 15 GB T4).
- **Why this rank `r`?** (capacity vs. overfitting — too small underfits, too large overfits).
- **Why Execution Accuracy over text comparison?** (two different SQL strings can return the same result; text match wrongly penalizes them).
- **Why a fixed schema, and what's the price of "arbitrary DB"?**
- **Why these guardrails in the MCP tool?**

### Biggest pitfalls
- No held-out test set → you measure yourself on training data and fool yourself. Split first.
- Wrong chat template during training → the model learns format garbage.
- Unfiltered synthetic data → you train on broken SQL. Always execute first, then keep.
- Lost Colab session → without Drive checkpoints the run is gone.
- Watching only the loss → falling loss ≠ better queries.
- Overfitting to the schema → test with questions phrased differently than in training.
