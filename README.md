# Programme Tracker — local Streamlit + Postgres

A dashboard + editable tables for your deliverables and requests pipeline,
running entirely on your machine: Python, Streamlit, and a local Postgres
database.

## What's here

```
streamlit_app/
├── app.py              # the Streamlit app (Dashboard / Deliverables / Requests)
├── data.py             # all SQL reads/writes
├── db_conn.py          # database connection helper
├── requirements.txt
├── .env.example
└── db/
    ├── schema.sql              # table definitions
    ├── seed.py                 # loads seed_*.json into Postgres
    ├── seed_deliverables.json  # your actual 196 deliverables
    └── seed_requests.json      # your actual 48 pipeline requests
```

## 1. Install Postgres locally

Easiest on most machines is Docker — no system install needed:

```bash
docker run --name programme-pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
docker exec -it programme-pg psql -U postgres -c "CREATE DATABASE programme_tracker;"
```

Or install Postgres natively (postgresql.org) and create the database with:

```bash
createdb programme_tracker
```

## 2. Set up the Python environment

```bash
cd streamlit_app
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configure the connection

The app reads connection settings from environment variables (see
`.env.example`). If your Postgres matches the defaults (localhost:5432,
user `postgres`, password `postgres`, db `programme_tracker`), you can skip
this — those are already the built-in defaults in `db_conn.py`.

Otherwise, export the variables before running, e.g.:

```bash
export PGPASSWORD=your_actual_password
```

## 4. Create tables and load your data

```bash
psql -h localhost -U postgres -d programme_tracker -f db/schema.sql
python db/seed.py
```

`seed.py` loads the exact data from your original workbook (already cleaned
— single header row, no merged cells) so the app opens pre-populated.

## 5. Run the app

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Only reachable from your machine by
default — that's expected for a local setup.

## Re-running the seed later

`seed.py` wipes and reloads both tables — handy for resetting to a known
state, but don't run it once you've started editing live data in the app,
or you'll lose those edits. It's meant for first-time setup only.

## Where this can go from here

- **Share it with others on your network**: run with
  `streamlit run app.py --server.address 0.0.0.0`, then colleagues on the
  same network can reach it at `http://<your-ip>:8501`.
- **Deploy it properly**: host Postgres somewhere (Supabase, Railway,
  RDS) and deploy the Streamlit app (Streamlit Community Cloud is free,
  or any small VM) — then it's reachable from anywhere, not just your
  machine.
- **Add authentication**: Streamlit has no built-in login. For a shared
  deployment, `streamlit-authenticator` (a community package) is a common
  lightweight option.
