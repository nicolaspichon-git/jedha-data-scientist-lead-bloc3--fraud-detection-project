*AUTOMATIC FRAUD DETECTION* PROJECT
===

Code source de l'infrastructure de données réalisée pour le projet de détection de fraude automatique [B3-D0](fraud-project--d0-introduction.pdf). 
L'architecture des pipelines est rpésenté dans [B3-D1](fraud-project--d1-data-infrastructure.pdf). 

## Démarrer

Sous Windows : `fd-manager.ps1` est l'outil de construction de projet.
Pour démarrer : 

```powershell
.\fd-manager.ps1 setup             # crée .env et y inscrit un FRAUD_PEPPER
pip install -e ".[dev]"        # pour lancer pytest hors conteneur

# ouvrir Docker Desktop et attendre qu'il soit prêt
.\fd-manager.ps1 up                # postgres + airflow + mlflow + streamlit
.\fd-manager.ps1 init              # applique le DDL
.\fd-manager.ps1 load              # déclenche le chargement des données d'entrainement
.\fd-manager.ps1 check             # vérifie tous les critères d'acceptation
```

La page web du serveur Airflow est sur <http://localhost:8081> (connexion : `admin` / `admin`).
La page web du serveur MLflow sur <http://localhost:8001>.

## Les principes de l'organisation

- `airflow/dags/` ordonne et ne calcule pas ; le code de calcul est dans `fraud/`. 
Les critères d'acceptation du plan tournent donc sans démarrer Airflow.

- Le SQL vit dans des fichiers `.sql`. 
La définition des features est le seul artefact dont deux expressions doivent être prouvées égales : 
elles doivent être comparables côte à côte. 
Voir `sql/functions/` et `sql/backfill/`, et la preuve en `sql/checks/reconcile_features.sql`.

- La traçabilité des exeigences est générée automatiquement.
Chaque code source python ou sql inscrit les exigences qu'il impacte dans sa *docstring* ;
L'outil `tools/build_traceability.py` en déduit le document `TRACEABILITY.md`. 
Le mode `--check` vérifie la tracabilité dans les deux sens.

```python
def check_record(record: dict, line_no: int) -> list[Reject]:
    """Coherence entre champs d'un meme enregistrement.

    Couvre: B3-EC21
    Lot: B3-L2
    Competence: B3-C5
    """
```

## Arborescence

| Emplacement | Rôle |
| --- | --- |
| `fraud/` | code source python. implémente la logique |
| `sql/ddl/` | code sql pour construire les magasins postgre (12) |
| `sql/functions/` | code sql pour calculer des features en mode temps réel |
| `sql/backfill/` | la même, pour le mode batch |
| `sql/checks/` | critères d'acceptation exprimables en SQL |
| `tests/` | test unitaires hors sql et airflow |
| `tools/` | outils divers, y compris de génération et de contrôle de la traçabilité |
| `airflow/dags/` | processus ordonnancés|
| `.local_cache/` | cache local du CSV et des fichiers de conf, hors dépôt |