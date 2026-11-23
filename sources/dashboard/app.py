"""The dashboard of B3-S6: its entry point. `streamlit run dashboard/app.py`.

Block: B3.
Lot: B3-R2.
Competency: B3-C4.
Covers: B3-EE03.

Declares the pages and nothing else. No data is read here: every page opens
its own connection, as fd_dashboard, through common.connection().
"""
import streamlit as st

st.set_page_config(page_title="Fraud Detection : Dashboard", layout="wide")

PAGES = {
    "Analyse": [
        st.Page("pages/report.py", title="Rapports", url_path="report", default=True),
        st.Page("pages/frauds.py", title="Alertes de fraude", url_path="frauds"),
    ],
    "Exploitation": [
        st.Page("pages/operations.py", title="Contrôles d'exploitation", url_path="operations"),
        st.Page("pages/ops.py", title="Alertes d'exploitation", url_path="ops"),
    ],
    "Suivi": [
        st.Page("pages/rejects.py", title="Rejets de validation", url_path="rejects"),
        st.Page("pages/performances.py", title="Performances du modèle", url_path="performances"),
    ],
}

st.navigation(PAGES).run()
