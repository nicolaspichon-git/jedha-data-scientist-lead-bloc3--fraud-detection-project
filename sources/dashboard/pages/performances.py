"""The performance of the model, as the verdicts reveal it (B3-R10).

Block: B3.
Lot: B3-R10.
Competency: B3-C2, B3-C4.
Covers: B3-EE04, B3-EI02, B3-EI03.

Section 3 of the morning report over a period: the verdicts that became known,
the decisions they judge, and what B3-M5 measured on the test set -- read from
fd_datasets, where fit_model copies it. fraud/dashboard.performances_view()
decides what is shown; this page only displays.
"""
import datetime as dt

import streamlit as st

import common
from fraud import dashboard

st.title("Performances du modèle de scoring")

KEY = "performances_period"
settings = common.settings()

# A month by default, ending today in the declared zone: verdicts arrive a few
# a day, and one day of them says little.
day = dashboard.today(settings)
start = day - dt.timedelta(days=dashboard.PERF_DEFAULT_DAYS - 1)
chosen = st.date_input("Période de réception des verdicts", value=(start, day),
                       key=KEY, format="YYYY-MM-DD")
first, last = dashboard.period_of(chosen, day)

with common.connection() as conn:
    view = dashboard.performances_view(conn, settings, first, last)

st.subheader(view["title"])
common.show(view["notices"])

for column, (label, value) in zip(st.columns(len(view["figures"])),
                                  view["figures"]):
    with column:
        st.metric(label, value)
st.caption(view["note"])

st.dataframe(view["comparison"], hide_index=True)
st.dataframe(view["matrix"], hide_index=True)

if view["series"]:
    st.subheader("Jour par jour")
    # A day without a fraud has no recall: a gap in the line, never a zero.
    st.line_chart(view["series"], x="Jour", y=["Rappel (%)", "Précision (%)"])

if view["by_model"]:
    st.subheader("Par version du modèle")
    st.dataframe(view["by_model"], hide_index=True)
