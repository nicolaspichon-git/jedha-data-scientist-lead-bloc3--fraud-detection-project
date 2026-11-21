# Automatic Fraud Detection --- réalisation

Système de détection de fraude sur les paiements par carte : il ingère chaque
minute les transactions d'une API temps réel, les score avec un modèle entraîné
sur l'historique, notifie un analyste dans une limite de capacité déclarée, et
rend compte chaque matin de ce qui s'est passé la veille.

Ce répertoire est la **réalisation**. La conception est en
[B3-D1](../step-1/fraud-project--d1-data-infrastructure.md), les exigences en
[B3-D0](../step-0/fraud-project--d0-introduction.md) §0.4. Les six processus B3-S1 à B3-S6
sont réalisés ; chacun a son plan de développement sous [`ws/`](ws/).

---

## Ce que fait le système

| Processus | Ce qu'il produit | DAG | Cadence (heure de Paris) |
| --- | --- | --- | --- |
| **B3-S1** chargement historique | la zone brute, la quarantaine, les transactions pseudonymisées et leurs features | `dag_load_history` | manuel, une fois |
| **B3-S2** entraînement | un jeu d'entraînement daté, un modèle, son manifeste `run.json`, sa référence B3-M5 en base | `dag_train` | lundi 03:00 |
| **B3-S3** ingestion temps réel | chaque transaction validée, scorée, alertée si besoin ; les quatre contrôles d'exploitation | `dag_ingest` | chaque minute |
| | les verdicts échus, qui ferment la boucle d'apprentissage | `dag_ingest_verdicts` | chaque jour 02:00 |
| **B3-S4** rapport du matin | un document Markdown par journée couverte, et son empreinte en base | `dag_daily` | chaque jour 06:00 |
| **B3-S5** conservation | la purge de la zone brute et de la quarantaine au-delà de 90 jours, journalisée | `dag_purge` | dimanche 04:00 |
| **B3-S6** restitution | un tableau de bord en lecture seule | service `dashboard` | permanent |

Chaque DAG porte un `start_date` dans le fuseau `Europe/Paris`, et Airflow
évalue alors sa cadence **dans ce fuseau**, changements d'heure compris : le
rapport tourne à 06:00 à Paris, l'été comme l'hiver. Les journaux d'Airflow,
eux, affichent leurs horodatages en UTC. Le **rapport** découpe ses journées
dans le fuseau déclaré dans `governance.yml`, le même.

**Deux canaux de notification, deux publics.** Le canal des **fraudes** notifie
l'analyste, au plus 60 alertes sur 24 heures glissantes ; au-delà, une alerte
reste levée mais sa notification est retenue. Le canal **ops** notifie le
responsable du pipeline quand l'un des quatre contrôles de `dag_ingest` change
d'état --- fraîcheur, exécutions vides, taux de rejet, invariant de volume ---
et seulement au changement, jamais à chaque minute. Aucune transaction ne
transite par le second.

---

## Démarrer

**Prérequis** : Windows 11 et **PowerShell**, Docker Desktop, Python 3.11 ou
plus pour lancer les tests hors conteneur.

Pas de `make` ni de `&&` : `fd-manager.ps1` tient ce rôle, et chaque tâche
s'arrête d'elle-même sur la première erreur. Toutes les commandes se lancent
depuis ce répertoire.

```powershell
.\fd-manager.ps1 setup             # crée .env : FRAUD_PEPPER, FD_DASHBOARD_PASSWORD
pip install -e ".[dev]"            # pour pytest et ruff hors conteneur

# ouvrir Docker Desktop et attendre qu'il soit prêt
.\fd-manager.ps1 up                # postgres, airflow, mlflow, dashboard
.\fd-manager.ps1 init              # DDL, rôles, migrations ; rejouable
.\fd-manager.ps1 load              # B3-S1 : l'historique
.\fd-manager.ps1 train             # B3-S2 : le premier modèle
.\fd-manager.ps1 realtime -Start   # B3-S3 : réactive dash_ingest, à la minute
.\fd-manager.ps1 check             # tout : acceptation, traçabilité, tests
```

`.\fd-manager.ps1` seul liste les tâches.

**`init` est rejouable**, et c'est voulu : il applique tout le DDL, la fonction
des features, les migrations de données et le mot de passe du tableau de bord.
Le relancer après une mise à jour du dépôt est le geste normal ; il ne doit
produire aucune erreur.

**`up` recrée les conteneurs dont la configuration a changé.** Un
`docker-compose.yml` modifié n'est lu qu'à la recréation : tant qu'elle n'a pas
eu lieu, `governance.yml` --- monté en lecture --- peut déjà déclarer un chemin
que le conteneur ne monte pas encore.

### Les services

| Service | Adresse | Accès |
| --- | --- | --- |
| Airflow | <http://localhost:8080> | `admin` / `admin` |
| MLflow | <http://localhost:5000> | --- |
| Tableau de bord | <http://127.0.0.1:8501> | cette machine seulement |
| PostgreSQL | `localhost:5432` | identifiants de `.env` |

Le tableau de bord écoute sur `127.0.0.1` et non sur le réseau : il n'a pas
d'authentification, et le jour où il quitte cette machine il lui faut un
frontal qui en a une.

---

## Arborescence

| Emplacement | Rôle |
| --- | --- |
| `fraud/` | la logique, un module par responsabilité, importable sans Airflow |
| `airflow/dags/` | l'ordonnancement, mince : il appelle `fraud/` et ne calcule rien |
| `sql/ddl/` | les magasins, les rôles et les droits ; rejouable, appliqué par `init` |
| `sql/functions/`, `sql/backfill/` | la définition des features, en temps réel et par lot |
| `sql/checks/` | les critères d'acceptation de B3-S1 à B3-S6, et les contrôles |
| `sql/maintenance/` | les migrations de données (renommages, chemins) |
| `sql/…` | une requête par fichier, rangées par usage : `frauds/`, `reports/`, `ops/`, `dashboard/`… |
| `dashboard/` | le tableau de bord Streamlit : ses pages, son image, sa configuration |
| `tools/` | les outils lancés par `fd-manager.ps1` : contrôles, mesures, réparations |
| `tests/` | ce qui s'éprouve sans base ni Airflow |
| `governance.yml` | **les décisions** : durées de conservation, seuils, capacité, canaux, chemins |
| `runtime/` | **ce que la pile produit** --- voir ci-dessous |
| `ws/` | ce qui est écrit à la main : les plans de développement, les maquettes |
| `.local_cache/` | le CSV historique téléchargé ; hors dépôt, il se retélécharge |
| `TRACEABILITY.md` | exigences ↔ code, **généré** |

### `runtime/`

```
runtime/reports/                      les rapports du matin, un fichier par jour
runtime/datasets/                     les jeux Parquet, les modèles, les manifestes
runtime/channels/frauds/frauds.jsonl  le canal de l'analyste
runtime/channels/ops/ops.jsonl        le canal de l'exploitation
runtime/observations/                 les mesures de l'API (B3-N0)
```

**Un seul montage le couvre**, `./runtime:/opt/project/runtime`. Ce projet a
perdu trois fois un répertoire déclaré mais non monté --- 28 observations
réelles, un jeu d'entraînement entier, puis les rapports ---, d'où la règle :
tout chemin déclaré dans `governance.yml` commence par `runtime/`, et
`tests/test_mounts.py` le vérifie. `ws/` n'est monté dans aucun conteneur.

`runtime/datasets/` est hors dépôt : la ligne de `fd_datasets` le rend
retrouvable, l'empreinte de la recette le rend reconstructible.

---

## La base

Un schéma, des tables préfixées `fd_`, et des **rôles qui ne peuvent pas** ---
plutôt que des rôles qui s'abstiennent.

| Rôle | Ce qu'il fait | Ce qu'il ne peut pas faire |
| --- | --- | --- |
| `fd_ingest` | charge, valide, score, alerte, notifie | modifier la zone brute ou les scores ; supprimer quoi que ce soit |
| `fd_report` | produit le rapport du matin | lire la zone brute |
| `fd_purge` | applique la conservation | lire ou modifier la couche exploitée |
| `fd_dashboard` | lit ce que montrent ses pages | écrire quoi que ce soit ; lire la zone brute ou le contenu d'une ligne rejetée |

Seul `fd_dashboard` se connecte directement, avec son propre mot de passe : les
autres n'ont pas d'attribut `LOGIN`, l'application se connecte avec le compte
propriétaire puis émet `SET ROLE`. Le détail, et ce que chaque rôle peut lire
colonne par colonne, est dans l'[annexe B de B3-D1](../step-1/annexes/fraud-project--d1-annexe-b--gouvernance.md).

**Les données personnelles ne quittent pas la zone brute.** Le porteur y est
nommé ; partout ailleurs il est remplacé par `client_key`, un HMAC dont le
poivre (`FRAUD_PEPPER`) n'est que dans `.env`. Aucun canal de notification ne
peut porter un champ identifiant : la liste est vérifiée à l'envoi.

---

## Vérifier

```powershell
.\fd-manager.ps1 test              # tests unitaires, sans base ni Airflow
.\fd-manager.ps1 check             # tout ce qui suit, d'un coup
```

`check` enchaîne, et s'arrête au premier échec :

- les **critères d'acceptation** de B3-S1 à B3-S6 (`sql/checks/s*_acceptance.sql`),
  lus dans la base et non supposés ;
- les **contrôles hors base** de chaque processus (`tools/check_s*.py`) :
  fichiers sur disque, empreintes, conteneur du tableau de bord ;
- l'**absence de fuite du verdict** dans le score ;
- la **traçabilité dans les deux sens** ;
- les **tests unitaires** ;
- trois requêtes qui doivent rendre **vide** : concordance des deux modes de
  calcul des features, fermeture des compteurs, matins sans rapport.

---

## Les principes

**Le DAG est mince ; la logique est importable.** `airflow/dags/` ordonne et ne
calcule pas : tout est dans `fraud/`. Les critères d'acceptation tournent donc
sans démarrer Airflow --- sinon personne ne les lance.

**Le SQL vit dans des fichiers `.sql`.** Du code versionné et relisible, et
surtout comparable : la définition des features existe en deux modes, temps
réel (`sql/functions/`) et par lot (`sql/backfill/`), et ces deux expressions
doivent être prouvées égales (`sql/checks/reconcile_features.sql`). Elles se
comparent côte à côte, pas noyées dans une chaîne Python.

**Les décisions sont déclarées, pas codées.** Une durée de conservation, un
seuil de contrôle, une capacité de notification ou un chemin vivent dans
`governance.yml`, avec leur justification. Une valeur qui n'existe que dans le
code est une décision que personne ne retrouve.

**La traçabilité est générée.** Chaque fonction porte sa couverture dans sa
*docstring* ; `tools/build_traceability.py` en produit `TRACEABILITY.md`, et son
mode `--check` sort en erreur si une exigence n'est portée par rien ou si le
code cite une exigence qui n'existe pas.

```python
def notify_ops(conn, settings, report: dict) -> dict:
    """Send each transition, then record it and journal it.

    Covers: B3-EC14, B3-EC17
    Lot: B3-N9
    Competency: B3-C3, B3-C4
    """
```

**Envoyer, puis enregistrer.** Une notification n'est marquée envoyée qu'après
que le canal l'a acceptée. L'ordre inverse perdrait une alerte en silence et
pour toujours ; celui-ci peut, au pire, en envoyer une deux fois.

---

## Localiser les compétences B3-C1 à B3-C5

[`TRACEABILITY.md`](TRACEABILITY.md), colonne *Code*. Généré, donc à jour par
construction.
