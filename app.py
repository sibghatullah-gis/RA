"""
Programme Tracker — Streamlit + local Postgres

Run with:
    streamlit run app.py
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from data import (
    fetch_deliverables, fetch_requests,
    insert_deliverable, update_deliverable, delete_deliverable,
    insert_request, update_request, delete_request,
    DELIVERABLE_COLS, REQUEST_COLS,
)

st.set_page_config(page_title="Programme Tracker", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap');

:root{
  --bg:#0E2224; --panel:#14302F; --panel-2:#17383A; --line:#2B4E4C;
  --ink:#EDECE4; --ink-dim:#A9BFB9; --gold:#E3A857; --teal:#4FA69C; --coral:#D97A5C;
}

.stApp{
  background: var(--bg);
  background-image:
    linear-gradient(var(--line) 1px, transparent 1px),
    linear-gradient(90deg, var(--line) 1px, transparent 1px);
  background-size: 64px 64px;
  color: var(--ink);
  font-family: 'Inter', sans-serif;
}
.stApp *:not([class*="material"]):not([data-testid*="Icon"]){
  color: var(--ink);
  font-family: 'Inter', sans-serif;
}
h1, h2, h3{
  font-family: 'Newsreader', serif !important;
  font-weight: 500 !important;
  color: var(--ink) !important;
}
h1 em{ color: var(--gold); font-style: italic; }

/* KPI metric cards */
div[data-testid="stMetric"]{
  background: var(--panel);
  border: 1px solid var(--line);
  padding: 14px 16px;
}
div[data-testid="stMetricLabel"]{
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 10.5px !important;
  letter-spacing: .05em;
  text-transform: uppercase;
  color: var(--ink-dim) !important;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: unset !important;
  line-height: 1.3 !important;
}
div[data-testid="stMetricLabel"] > div{
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: unset !important;
}
div[data-testid="stMetricValue"]{
  font-family: 'Newsreader', serif !important;
  color: var(--gold) !important;
}
div[data-testid="stMetricDelta"]{
  color: var(--ink-dim) !important;
}

/* Panels / containers with a border */
div[data-testid="stVerticalBlockBorderWrapper"]{
  background: var(--panel);
  border: 1px solid var(--line) !important;
}

/* Sidebar */
section[data-testid="stSidebar"]{
  background: var(--panel-2);
  border-right: 1px solid var(--line);
}

/* Inputs */
input, textarea, select, .stSelectbox div[data-baseweb="select"] > div{
  background: var(--panel-2) !important;
  color: var(--ink) !important;
  border-color: var(--line) !important;
}

/* Buttons */
button[kind="primary"], button[kind="secondary"]{
  background: var(--teal) !important;
  color: #0E2224 !important;
  border: none !important;
  font-weight: 600 !important;
}

/* DataFrame / data_editor */
div[data-testid="stDataFrame"], div[data-testid="stDataEditor"]{
  border: 1px solid var(--line) !important;
}

/* Captions */
.stCaption, [data-testid="stCaptionContainer"]{
  color: var(--ink-dim) !important;
}
</style>
""", unsafe_allow_html=True)

PLOTLY_DARK = dict(
    paper_bgcolor="#14302F",
    plot_bgcolor="#14302F",
    font_color="#A9BFB9",
    font_family="Inter, sans-serif",
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)
PLOTLY_GRID = dict(gridcolor="#2B4E4C")

BAD_COUNTRY = {"", "Delivered", "In progress", "Completed", "Pending", None}

STATUS_COLORS = {
    "Completed": "#4FA69C",
    "In progress": "#E3A857",
    "Pending": "#D97A5C",
    "Unknown": "#5A6E6C",
    "Ongoing": "#E3A857",
    "Listed": "#D97A5C",
    "Tbc": "#C4695B",
}

page = st.sidebar.radio("View", ["Dashboard", "Deliverables", "Requests Pipeline"])
st.sidebar.markdown("---")
st.sidebar.caption("Connected to local Postgres. Edits save immediately.")


# ---------------------------------------------------------------- DASHBOARD
# ---------------------------------------------------------------- DASHBOARD
if page == "Dashboard":
    st.title("Resource Assessment Team: Progress")

    deliv = fetch_deliverables()
    req = fetch_requests()

    total = len(deliv)
    completed = (deliv["status"] == "Completed").sum() if total else 0
    in_progress = (deliv["status"] == "In progress").sum() if total else 0
    countries = deliv.loc[~deliv["country"].isin(BAD_COUNTRY), "country"].nunique()
    completed_pct = round(100 * completed / total) if total else 0

    kpis = [
        ("Completed", int(completed), f"{completed_pct}% of {total}"),
        ("In progress", int(in_progress), "active now"),
        ("Countries reached", int(countries), "across deliverables"),
        ("Pipeline requests", len(req), f"{(req['status'] == 'Completed').sum()} completed so far"),
        ("Total deliverables", total, "logged records"),
    ]
    kpi_html = '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--line);border:1px solid var(--line);margin-bottom:8px;">'
    for i, (label, value, sub) in enumerate(kpis):
        value_color = "var(--gold)" if i == 0 else "var(--ink)"
        kpi_html += f'''
        <div style="background:var(--panel);padding:16px 18px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-dim);margin-bottom:8px;">{label}</div>
          <div style="font-family:'Newsreader',serif;font-size:30px;font-weight:500;color:{value_color};">{value}</div>
          <div style="font-size:11px;color:var(--ink-dim);margin-top:3px;">{sub}</div>
        </div>'''
    kpi_html += '</div>'
    st.markdown(kpi_html, unsafe_allow_html=True)

    st.markdown("---")

    def style_fig(fig):
        fig.update_layout(**PLOTLY_DARK)
        fig.update_xaxes(**PLOTLY_GRID)
        fig.update_yaxes(**PLOTLY_GRID)
        return fig

    # =========================================================================
    # NEW INTERACTIVE GLOBAL MAP COMPONENT
    # =========================================================================
        # =========================================================================
    # NEW INTERACTIVE GLOBAL MAP COMPONENT (HIGH CONTRAST EDITION)
    # =========================================================================
    st.subheader("Global Footprint Map")
    cc_map = deliv.loc[~deliv["country"].isin(BAD_COUNTRY)]

    if len(cc_map) > 0:
        # Calculate how many projects are in each country
        map_counts = cc_map["country"].value_counts().reset_index()
        map_counts.columns = ["country", "Project Count"]

        # Build the choropleth map figure
        fig_map = px.choropleth(
            map_counts,
            locations="country",
            locationmode="country names",
            color="Project Count",
            # HIGH CONTRAST COLORS: Shifts from dark coral to bright gold so active spots pop out!
            color_continuous_scale=["#6E3D30", "#D97A5C", "#E3A857"],
            labels={"Project Count": "Deliverables"}
        )

        # Blend the geo layout background elements with your app's custom UI styles
        fig_map.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='equirectangular',
                bgcolor="#14302F",       # Matches container panels
                landcolor="#0B191B",     # Deepened slightly so highlighted countries pop more!
                lakecolor="#14302F",     # Matches container panels
                coastlinecolor="#1D3A38" # Muted slightly to reduce background grid noise
            ),
            margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_colorbar=dict(
                title="Deliverables",
                title_font=dict(color="#A9BFB9"),
                tickfont=dict(color="#A9BFB9")
            )
        )
        st.plotly_chart(style_fig(fig_map), use_container_width=True)
    else:
        st.info("No valid geographical records found in the database to display.")

    st.markdown("---")

    # =========================================================================

    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.subheader("Delivery volume by year")
        if total:
            yr = deliv.dropna(subset=["year"]).groupby(["year", "status"]).size().reset_index(name="count")
            fig = px.bar(
                yr, x="year", y="count", color="status", barmode="stack",
                color_discrete_map=STATUS_COLORS,
            )
            st.plotly_chart(style_fig(fig), use_container_width=True)
        else:
            st.info("No deliverables yet.")

    with c2:
        st.subheader("Status breakdown")
        if total:
            sc = deliv["status"].value_counts().reset_index()
            sc.columns = ["status", "count"]
            fig = px.pie(
                sc, names="status", values="count", hole=0.6,
                color="status", color_discrete_map=STATUS_COLORS,
            )
            fig.update_traces(marker=dict(line=dict(color="#14302F", width=3)))
            st.plotly_chart(style_fig(fig), use_container_width=True)
        else:
            st.info("No deliverables yet.")

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Global reach — top countries")
        cc = deliv.loc[~deliv["country"].isin(BAD_COUNTRY)]
        if len(cc):
            top = cc["country"].value_counts().head(15).reset_index()
            top.columns = ["country", "count"]
            fig = px.bar(top.sort_values("count"), x="count", y="country", orientation="h",
                         color_discrete_sequence=["#4FA69C"])
            st.plotly_chart(style_fig(fig), use_container_width=True)
        else:
            st.info("No country data yet.")

    with c4:
        st.subheader("Requests pipeline")
        if len(req):
            rc = req["status"].value_counts().reset_index()
            rc.columns = ["status", "count"]
            fig = px.bar(rc, x="count", y="status", orientation="h", color="status",
                         color_discrete_map=STATUS_COLORS)
            st.plotly_chart(style_fig(fig), use_container_width=True)
        else:
            st.info("No requests yet.")

    st.caption(
        "Note: the country field mixes real countries with regions (e.g. 'Africa', 'SIDS'). "
        "For a true geocoded map, clean that column first — a bar ranking avoids mis-plotting it."
    )


# ------------------------------------------------------------- DELIVERABLES
elif page == "Deliverables":
    st.title("Deliverables")

    deliv_existing = fetch_deliverables()
    existing_topics = sorted(deliv_existing["topic"].dropna().unique().tolist())
    existing_divisions = sorted(deliv_existing["division"].dropna().unique().tolist())
    existing_countries = sorted(deliv_existing["country"].dropna().unique().tolist())
    NEW_OPTION = "+ Add new…"

    with st.expander("+ Add deliverable"):
        with st.form("add_deliverable", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            year = c1.number_input("Year", min_value=2000, max_value=2100, value=2026, step=1)

            division_choice = c2.selectbox("Division", existing_divisions + [NEW_OPTION])
            division = c2.text_input("New division name") if division_choice == NEW_OPTION else division_choice

            country_choice = c3.selectbox("Country", existing_countries + [NEW_OPTION])
            country = c3.text_input("New country name") if country_choice == NEW_OPTION else country_choice

            c4, c5, c6 = st.columns(3)
            topic_choice = c4.selectbox("Topic", existing_topics + [NEW_OPTION])
            topic = c4.text_input("New topic name") if topic_choice == NEW_OPTION else topic_choice

            output_type = c5.text_input("Output type")
            status = c6.selectbox("Status", ["Completed", "In progress", "Pending", "Unknown"])
            focal_point = st.text_input("Focal point")
            if st.form_submit_button("Save"):
                insert_deliverable({
                    "year": year, "division": division, "country": country,
                    "topic": topic, "output_type": output_type, "status": status,
                    "focal_point": focal_point,
                })
                st.success("Added.")
                st.rerun()

    deliv = deliv_existing
    search = st.text_input("Search country, topic, division…")
    if search:
        mask = (
            deliv["country"].fillna("").str.contains(search, case=False)
            | deliv["topic"].fillna("").str.contains(search, case=False)
            | deliv["division"].fillna("").str.contains(search, case=False)
        )
        deliv = deliv[mask]

    st.caption(f"{len(deliv)} records — edit cells directly, or check a row and press delete below. To add a brand-new topic, use the 'Add deliverable' form above, then it'll appear here as an option too.")
    edited = st.data_editor(
        deliv,
        key="deliv_editor",
        num_rows="fixed",
        disabled=["id", "created_at", "updated_at"],
        use_container_width=True,
        hide_index=True,
        column_config={
            "topic": st.column_config.SelectboxColumn("topic", options=existing_topics),
            "status": st.column_config.SelectboxColumn(
                "status", options=["Completed", "In progress", "Pending", "Unknown"]
            ),
        },
    )

    col_a, col_b = st.columns([1, 5])
    if col_a.button("Save edits"):
        for _, row in edited.iterrows():
            update_deliverable(int(row["id"]), {c: row[c] for c in DELIVERABLE_COLS})
        st.success("Saved.")
        st.rerun()

    with st.expander("Delete a deliverable"):
        if len(deliv):
            del_id = st.selectbox(
                "Choose row (by id)", deliv["id"],
                format_func=lambda i: f'{i} — {deliv.loc[deliv["id"]==i, "country"].values[0]} / {deliv.loc[deliv["id"]==i, "topic"].values[0]}'
            )
            if st.button("Delete", type="primary"):
                delete_deliverable(int(del_id))
                st.success("Deleted.")
                st.rerun()


# ---------------------------------------------------------- REQUESTS PIPELINE
elif page == "Requests Pipeline":
    st.title("Requests pipeline")

    with st.expander("+ Add request"):
        with st.form("add_request", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            country = c1.text_input("Country")
            topic = c2.text_input("Topic")
            division = c3.text_input("Division")
            c4, c5 = st.columns(2)
            status = c4.selectbox("Status", ["Completed", "Ongoing", "Listed", "Tbc", "Unknown"])
            source = c5.text_input("Source of request")
            focal_point = st.text_input("Focal point")
            if st.form_submit_button("Save"):
                insert_request({
                    "country": country, "topic": topic, "division": division,
                    "status": status, "source_of_request": source, "focal_point": focal_point,
                })
                st.success("Added.")
                st.rerun()

    req = fetch_requests()
    search = st.text_input("Search country, topic…")
    if search:
        mask = (
            req["country"].fillna("").str.contains(search, case=False)
            | req["topic"].fillna("").str.contains(search, case=False)
        )
        req = req[mask]

    st.caption(f"{len(req)} records — edit cells directly, or delete below.")
    edited = st.data_editor(
        req,
        key="req_editor",
        num_rows="fixed",
        disabled=["id", "created_at", "updated_at"],
        use_container_width=True,
        hide_index=True,
    )

    col_a, col_b = st.columns([1, 5])
    if col_a.button("Save edits"):
        for _, row in edited.iterrows():
            update_request(int(row["id"]), {c: row[c] for c in REQUEST_COLS})
        st.success("Saved.")
        st.rerun()

    with st.expander("Delete a request"):
        if len(req):
            del_id = st.selectbox(
                "Choose row (by id)", req["id"],
                format_func=lambda i: f'{i} — {req.loc[req["id"]==i, "country"].values[0]} / {req.loc[req["id"]==i, "topic"].values[0]}'
            )
            if st.button("Delete", type="primary"):
                delete_request(int(del_id))
                st.success("Deleted.")
                st.rerun()