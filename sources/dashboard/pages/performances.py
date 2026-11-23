"""The performance of the model, as the verdicts reveal it (B3-R10).

Block: B3.
Lot: B3-R10.
Competency: B3-C2, B3-C4.
Covers: B3-EE04, B3-EI02, B3-EI03.

Section 3 of the morning report over a period: the verdicts that became known,
the decisions they judge, and what training measured on the test set -- read from
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
    st.subheader("Evolution des métriques dans le temps")
    # A day without a fraud has no recall: a gap in the line, never a zero.
    # A VEGA-LITE SPEC rather than st.line_chart, for two defects seen on
    # 2026-11-23: the day was a string, so the x axis had no scale -- and no
    # labels at all with a single day; and a line through one point draws
    # nothing. Here the axis is TIME, spans the whole period selected, and
    # every day carries a point, so one day of verdicts is still visible.
    values = [{"Jour": row["Jour"], "Indicateur": name, "Valeur": row[name]}
              for row in view["series"]
              for name in ("Rappel (%)", "Précision (%)")
              if row.get(name) is not None]
    domain = ([view["first"].isoformat(), view["last"].isoformat()]
              if view.get("first") and view.get("last") else None)
    x = {"field": "Jour", "type": "temporal",
         "title": "Jour de réception des verdicts",
         "axis": {"format": "%d/%m", "labelAngle": 0}}
    if domain:
        x["scale"] = {"domain": domain}
    st.vega_lite_chart({
        "data": {"values": values},
        "mark": {"type": "line", "point": {"size": 80}},
        "encoding": {
            "x": x,
            "y": {"field": "Valeur", "type": "quantitative",
                  "title": "Rappel et précision observés (%)",
                  "scale": {"domain": [0, 100]}},
            "color": {"field": "Indicateur", "type": "nominal", "title": None},
            "tooltip": [{"field": "Jour", "type": "temporal", "format": "%d/%m/%Y"},
                        {"field": "Indicateur", "type": "nominal"},
                        {"field": "Valeur", "type": "quantitative", "format": ".1f"}],
        },
    }, use_container_width=True)

if view["by_model"]:
    st.subheader("Métriques en fonction de la version du modèle")
    st.dataframe(view["by_model"], hide_index=True)
    st.caption(
        "« non mesurable » : un ratio dont le dénominateur est nul."
        "Le *rappel observé* d'une version n'est défini que si au moins un "
        "verdict était une fraude confirmée, parmi les paiements qu'elle a "
        "scorés et dont le verdict est tombé ; sa *précision observée* n'est "
        "définie que si elle a levé au moins une alerte sur ces paiements. "
        "Avec environ 0,4 % de fraudes, une version qui a jugé peu de paiements "
        "n'a souvent ni l'un ni l'autre. Dans les colonnes « mesuré », la "
        "mention \"non mesurable\" veut dire que la recette de la "
        "version n'a pas de mesure enregistrée en base : "
        ".\\fd-manager.ps1 reference la recopie depuis son run.json.")
