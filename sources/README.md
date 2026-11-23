*AUTOMATIC FRAUD DETECTION* PROJECT
===

Ce répertoire contient le code source de l'infrastructure de données réalisée pour le projet de détection de fraude automatique [B3-D0](fraud-project--d0-introduction.pdf). 

Le système réalisé est un système de détection de fraude sur les paiements par carte : il ingère minute par minute les transactions d'une application temps-réelle, les score avec un modèle entraîné sur un historique de transaction libellées, notifie un analyste dans une limite de capacité donnée, et rend compte chaque matin des transactions et des fraudes détectées la veille.

L'architecture des pipelines de données est présentée dans \[B3-D1\](fraud-project--d1-data-infrastructure.pdf). 

---

## Introduction au système

### Structure générale

Le système est construit autour de deux à trois points d'entrée, de sept processus, de plusieurs points de sortie, dont 1 dashboard de restitution et 2 canaux de notifications :

- Points d'entrée : 
	- un historique de transactions libellées ;
	- un producteur de transactions en quasi-temps réel accessible par API HTTP ;
	- une source de verdicts pour les transactions produites ;
		- \> la source de verdicts est, fortuitement, le producteur de transaction ;
		- \> mais ce double rôle n'est pas une obligation : il est tout à fait possible d'imaginer deux sources distinctes (de fait, dans la vraie vie, les transactions et les verdicts ne sont pas du tout produits à la même cadence) ;
- Processus : 
	- six processus, exprimés en *DAG* (*Directed Acyclic Graph*) et orchestrés par *Airflow* (cf. détails ci-après) ;
- Points de sortie :
	- 2 canaux de notifications représentés par des fichiers locaux ;
	- 1 application de restitution continue qui affiche un tableau de bord en lecture seule.

Sans compter les interfaces d'administration et les journaux des conteneurs : *Airflow*, *MLflow* et *PostgreSQL*.
	
### Processus détaillés

#### Synopsis

| #          | Processus                                 | DAG |
| ---------- | ----------------------------------------- | --- | 
| **B3-S1**  | chargement de l'historique d'entrainement | `dag_load_history` | 
| **B3-S2**  | entraînement du modèle                    | `dag_train` |
| **B3-S3**  | ingestion des txns en quasi-temps réel    | `dag_ingest` |
| **B3-S3D** | ingestion des verdicts                    | `dag_ingest_verdicts` |
| **B3-S4**  | rapport quotidien                         | `dag_daily` |
| **B3-S5**  | conservation                              | `dag_purge` |

#### B3-S1 :  chargement de l'historique d'entrainement
- *Production* : la zone brute, la quarantaine, les transactions pseudonymisées et leurs features
- *Cadence* : manuel, une fois.

#### B3-S2 : entraînement du modèle
- *Production* : un jeu d'entraînement daté et versionné, un modèle prédictif, son manifeste (`run.json`), ses mesures de référence (la mesure des performances du modèle de base sur le jeu de test de référence : ce sont à la fois les performances du modèle et les performances de références pour les modèles comparables à venir).
- *Cadence* : chaque lundi à 03:00

#### B3-S3 : ingestion des transactions en quasi-temps réel
- *Production* : chaque transaction validée, scorée, alertée si besoin, ainsi que les quatre contrôles d'exploitation.
- *Cadence* : tous les jours, toutes les heures, 1 fois par minute.

#### B3-S3 : ingestion des verdicts
- *Production* : les verdicts, postdatés de 30 jours (en mode *nominal*) ou de 5 minutes (en mode *démo*), par rapport à la date d'émission de la transaction associée.
- *Cadence* : chaque jour à 02:00.

#### B3-S4 : rapport quotidien
- *Production* : un document *Markdown* par journée couverte, ainsi que son empreinte en base.
- *Cadence* : chaque jour à 06:00 (ou à 14:00 en mode *démo*).

#### B3-S5 : conservation
- *Production* : la purge de la zone brute et de la quarantaine au-delà de 90 jours, journalisée. 
- *Cadence* : chaque dimanche à 04:00.

#### Remarques

##### Les fuseaux horaires
*Airflow* évalue la cadence d'un *DAG* dans le fuseau de l'attribut `start_date`, changements d'heure compris. Dans notre système, le fuseau horaire des *DAGs*  est `Europe/Paris`. Le rapport quotidien est produit à 06:00, heure de Paris, tous les jours, été comme hiver. 

Les journaux d'*Airflow*, eux, affichent leurs horodatages en *UTC*. 

Le rapport quotidien découpe ses journées selon le fuseau déclaré dans `governance.yml`.

##### Les canaux de notification
Le système met en place deux canaux de notification distinctes :
- Le canal des *fraudes* notifie l'analyste
	- l'analyste reçoit au plus 60 alertes sur 24 heures glissantes ; 
	- au-delà, une alerte reste levée mais sa notification est retenue. 
- Le canal *ops* notifie le responsable du pipeline quand l'un des quatre contrôles d'exploitation (cf. détails ci-après) change d'état, et seulement dans le cas d'un changement. 

##### Les contrôles d'exploitation
Les quatre contrôles d'exploitation surveillent le processus d'ingestion temps-réelle (`dag_ingest`). Ils sont réalisés à la fin du processus dans la tâche `raise_and_notify_ops`, ils portent sur une fenêtre glissante de 60 minutes, et leurs seuils sont déclarés dans `governance.yml`, section `ops`.

###### Contrôle de fraîcheur (`freshness`)
- *Répond à la question* : quand le pipeline a-t-il réussi pour la dernière fois ?
- *Condition d'alerte* : aucune exécution réussie depuis 10 minutes.
- *Mesure* : capture l'arrêt du pipeline : *DAG* en pause, scheduler tombé, API muette. 
- Par définition, c'est une panne qu'aucun contrôle sur les données ne peut voir.

###### Exécutions vides (`empty_run`)
- *Répond à la question* : combien d'ingestion n'ont lu aucune transaction ?
- *Condition d'alerte* : plus de 10 % des exécutions de la fenêtre.
- *Mesure* : capture les mauvaises réponses des requêtes d'ingestion : les codes `429`, les dépassements de délais.
###### Taux de rejet (`rejection_rate`)
- *Répond à la question* : Quelle part des lignes lues la validation écarte-t-elle ?|
- *Condition d'alerte* : plus de **5 %** des lignes lues
- *Mesure* : un changement de forme du flux, comme un champ renommé ou une horloge qui dérive. Les lignes rejetées ne sont pas scorées.

###### Invariant de volume (`volume_invariant`)
- *Répond à la question* : Chaque lot (*micro-batch*) est-il bien compté ?
- *Condition d'alerte* : un seul lot dans lequel `lues ≠ valides + rejetées`.
- *Mesure* : une ligne perdue en silence entre la lecture et l'écriture.

##### Le mode *démo*
Certains processus peuvent fonctionner en deux modes : un mode *nominal* et un mode de *démonstration*.  Le mode adopté est déclaré dans `governance.yml`. Sauf mention du contraire, le code source et sa documentation décrivent le mode *nominal*.

| Interrupteur    | `nominal` | `demo` |
| ----------------| --------- | --- |
| `report.mode`   | journée de 00:00 à 00:00, rapport à 06:00 | journée de 12:00 à 12:00, rapport à 14:00 |
| `verdicts.mode` | verdict connu 30 jours après le paiement  | verdict connu 5 minutes après (param. `demo_delay_seconds`) |

Chaque rapport enregistre le début de la journée qu'il couvre (`fd_reports.day_start`) : il reste vérifiable après un changement de mode.

Après une bascule de mode, redémarrer le scheduler et le tableau de bord ; le
commentaire de `report.mode` décrit la couture que laisse la bascule et la façon de la combler.

---

## Démarrage 

**Point clé :** le système est conteneurisé mais *on-premise* : tous les conteneurs s'exécutent localement.

**Prérequis :** Windows 11 et **PowerShell**, Docker Desktop, Python 3.11 ou
plus pour lancer les tests hors conteneur.

**`fd-manager`**
L'outil de construction et de diagnostic du système est un script *PowerShell* maison : 
`fd-manager.ps1`. Toutes les commandes se lancent depuis le répertoire `sources`.

Pour lancer le système :

```powershell
cd .\sources
.\fd-manager.ps1 setup            # crée .env : FRAUD_PEPPER, FD_DASHBOARD_PASSWORD
pip install -e ".[dev]"           # pour pytest et ruff hors conteneur

# Lancer Docker Desktop et attendre qu'il soit prêt.

.\fd-manager.ps1 up                # postgres, airflow, mlflow, producer, dashboard
.\fd-manager.ps1 init              # DDL, rôles, migrations ; rejouable
.\fd-manager.ps1 load              # dag_load_history
.\fd-manager.ps1 train             # dag_train
.\fd-manager.ps1 realtime -Start   # dag_ingest
.\fd-manager.ps1 check             # tests d'acceptation, de traçabilité, unitaires
```

Exécuter `fd-manager.ps1` sans argument liste toutes les commandes de l'outil.

**Remarque : `init` est rejouable.** La commande applique tout le DDL, la fonction
des features, les migrations de données et le mot de passe du tableau de bord.
On doit relancer `init` après chaque mise à jour des sources.

**Remarque : `up` recrée les conteneurs dont la configuration a changé.** Un
`docker-compose.yml` modifié n'est lu qu'à la recréation : tant qu'elle n'a pas
eu lieu, `governance.yml` --- monté en lecture --- pourrait déclarer un chemin
que le conteneur n'a pas encore' monté.

### Les services

| Service | Adresse | Accès |
| --------- | --- | --- |
| *Airflow* | <http://localhost:8081> | `admin` / `admin` |
| *MLflow*  | <http://localhost:8001> | --- |
| *PostgreSQL* | `localhost:8431` | identifiants de `.env` |
| Producteur temps réel | <http://127.0.0.1:8801/docs> | cette machine seulement ; le pipeline l'appelle en `http://producer:4000` |
| Tableau de bord | <http://127.0.0.1:8501> | cette machine seulement |

Le tableau de bord écoute sur `127.0.0.1` et non sur le réseau : il ne demande pas d'authentification..

---

## Arborescence

| Emplacement                | Rôle |
| -------------------------- | --- |
| `sources/airflow/dags/`    | l'ordonnancement, mince : il appelle `fraud/` et ne calcule rien |
| `sources/dashboard/`       | le tableau de bord Streamlit : ses pages, son image, sa configuration ; `dashboard/README.md` explique chaque champ |
| `sources/docs/`            | les sources des specs et documents livrables : D0, D1, annexes |
| `sources/fraud/`           | la logique, un module par responsabilité, importable sans Airflow |
| `sources/mlflow/`          | l'image du serveur MLflow |
| `sources/runtime/`         | ce que la pile produit --- voir ci-dessous |
| `sources/sql/ddl/`         | les magasins, les rôles et les droits ; rejouable, appliqué par `init` |
| `sources/sql/functions/`   | la définition des features, en temps réel |
| `sources/sql/backfill/`    | la définition des features, par lot |
| `sources/sql/checks/`      | les critères d'acceptation de B3-S1 à B3-S6, et les contrôles |
| `sources/sql/maintenance/` | les migrations de données (renommages, chemins) |
| `sources/sql/demo/`        | les deux scripts `psql` de la démonstration : un paiement de bout en bout, une erreur et sa quarantaine |
| `sources/sql/…`            | une requête par fichier, rangées par usage : `frauds/`, `reports/`, `ops/`, `dashboard/`… |
| `sources/tests/`           | tests unitaires métiers (hors bases ou Airflow) |
| `sources/tools/`           | les outils lancés par `fd-manager.ps1` : contrôles, mesures, réparations |
| `sources/vendor/realtime-transactions-producer/` | le simulateur de paiements temps réel, copie de l'API du cours ; son `Dockerfile` et son `app.py` adaptés, les originaux dans `_old/` |
| `sources/docker-compose.yml` | la pile : sept services, dont `airflow-init` qui s'arrête une fois la base migrée |
| `sources/governance.yml`   | **les décisions** : durées de conservation, seuils, capacité, canaux, chemins |
| `sources/TRACEABILITY.md`  | exigences ↔ code, **généré** |

###### `runtime/`

```
runtime/channels/frauds/frauds.jsonl  le canal de l'analyste
runtime/channels/ops/ops.jsonl        le canal de l'exploitation
runtime/datasets/                     les jeux Parquet, les modèles, les manifestes
runtime/reports/                      les rapports du matin, un fichier par jour
```

**Un seul montage couvre ce répertoire**, `./runtime:/opt/project/runtime`.  Tout chemin déclaré dans `governance.yml` commence par `runtime/`, et le test
`tests/test_mounts.py` vérifie cette règle. 

###### `runtime/datasets/`
`runtime/datasets/` est hors dépôt : la ligne de `fd_datasets` le rend retrouvable, l'empreinte de la recette le rend reconstructible.

Le dossier `runtime/datasets/` contient, par recette, les fichiers *Parquet* des jeux d'entraînement et de test du modèle (`train.parquet`, `test.parquet`), ainsi que les artéfacts produits par l'entrainement : la copie de travail du modèle, son manifeste, son rapport.  Ces données sont produites par la pile et sont relativement volumineuses (~40 Mo).

###### Autres volumes
Hors `runtime/`, on a quatre volumes *Docker* : `pgdata` (la base), `mlruns` (le registre MLflow), `airflow-logs` et `producer-cache` (le corpus du simulateur). Une politique de conservation est définie pour chacun de ses volumes dans `governance.yml`.

---

## La base

Un schéma, des tables et des rôles préfixés par `fd_`.

###### Rôles
| Rôle           | Ce qu'il fait | Ce qu'il ne peut pas faire |
| -------------- | --- | --- |
| `fd_ingest`    | charge, valide, score, alerte, notifie | modifier la zone brute ou les scores ; supprimer quoi que ce soit |
| `fd_report`    | produit le rapport du matin | lire la zone brute |
| `fd_purge`     | applique la conservation | lire ou modifier la couche exploitée |
| `fd_dashboard` | lit ce que montrent ses pages | écrire quoi que ce soit ; lire la zone brute ou le contenu d'une ligne rejetée |

Seul `fd_dashboard` se connecte directement, avec son propre mot de passe : les autres rôles n'ont pas d'attribut `LOGIN`, l'application se connecte avec le compte propriétaire puis émet `SET ROLE`. Le détail, et ce que chaque rôle peut lire colonne par colonne, est dans l'annexe B de B3-D1 (gouvernance).

*Les données personnelles ne quittent pas la zone brute.* Le porteur y est nommé ; partout ailleurs il est remplacé par `client_key`, un HMAC dont le poivre (`FRAUD_PEPPER`) est défini comme variable d'environnement. Aucun canal de notification ne porte un champ identifiant : la liste est vérifiée à l'envoi.

---

## Vérifications

```powershell
.\fd-manager.ps1 test              # tests unitaires, sans base ni Airflow
.\fd-manager.ps1 check             # tout ce qui suit, d'un coup
```

`check` enchaîne, et s'arrête au premier échec :

- les *critères d'acceptation* de B3-S1 à B3-S6 (`sql/checks/s*_acceptance.sql`) ;
- les *contrôles hors base* de chaque processus (`tools/check_s*.py`) :
  fichiers sur disque, empreintes, conteneur du tableau de bord ;
- l'*absence de fuite du verdict* dans le score ;
- la *traçabilité des exigences dans les deux sens* ;
- les *tests unitaires* ;
- trois contrôles finaux :
	- la concordance des deux modes de calcul des features, 
	- la fermeture des compteurs, 
	- les absences de rapport.

---

## Quelques principes de structuration

**1.** `airflow/dags/` ordonne et ne calcule pas : toute la logique du métier est dans `fraud/`. Les critères d'acceptation sont donc applicables sans *Airflow*.

**2.** Toutes les requêtes *SQL* sont isolées dans des fichiers `/sql/*.sql` et sont gérées comme du code versionné. Indispensable pour comparer les définitions des features dans chacun des deux modes :  temps réel (`sql/functions/`) ou par lot (`sql/backfill/`), et prouver que ces deux expressions sont égales (`sql/checks/reconcile_features.sql`). 

**3.** Les décisions politiques sont déclarées et non codées : durée de conservation, seuil de contrôle, capacité de notification ou un chemin sont déclarés, avec leur justification, dans `governance.yml`

**4.** La matrice de traçabilité des exigences est générée : chaque code source déclare un entête où sont définis un certain nombre de marqueurs qui permettent de positionner le code dans la matrice de tracabilité générée automatiquement par l'outil `tools/build_traceability.py` .  

Exemple (les marqueurs sont : `Block` / `Lot` / `Competency` / `Covers` ) :

```python
def notify_ops(conn, settings, report: dict) -> dict:
    """Send each transition, then record it and journal it.

	Block: B3.
    Lot: B3-N9.
    Competency: B3-C3, B3-C4.
    Covers: B3-EC14, B3-EC17.
    """
```

La matrice de tracabilité des exigences fait correspondre à chaque exigence identifiée en \[D0\] la liste des code sources qui implémente une partie de l'exigence. Cette matrice ne garantie pas la couverture complète d'une exigence par le code mais elle permet quand meme de tracer ce qui a été réalisé pour l'implémenter.

**5.** Envoyer, puis enregistrer : une notification n'est marquée *envoyée* qu'après avoir été *acceptée* par le canal de notification. On évite ainsi de perdre perdrait une alerte en silence ou de l'envoyer deux fois.

---