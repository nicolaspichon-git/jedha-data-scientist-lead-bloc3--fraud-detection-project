---
version: v16
locale: fr
tags:
  - _RNCP38777
  - _2026
  - aia
  - aia/bc03
  - fraud-project
  - fraud-project/step-1
  - fraud-project/data-infrastructure/design
---

*AUTOMATIC FRAUD DETECTION* PROJECT
===

# 1. Data Infrastructure Design

> *Nicolas Pichon --- AIA RNCP 38777 / BC03 / Data Infrastructure Design / v16 --- 2026/11/16.*
---

## 1.1. Vue d'ensemble 

 *Object :* présenter les principaux composants de l'infrastructure, processus et bases de données, les flux de données entre eux, les flux de contrôles et les dépendances.  
 
###### Diagramme
![[diagrams/fraud-project--data-infrastructure--diagram-0.md]]

> _\> Les numéros portés par les blocs de pipeline ((1) à (5)) renvoient aux diagrammes détaillés des processus (S1 à S5)._

<div style="page-break-after: always;"></div>

###### Remarques
**R1.** L'ensemble est formé de trois familles de sous-systèmes :
- Pipelines portant des transactions : 
	- *Historical Data Loading*, *Transactions Ingestion*, *Models Training*, *Daily Reporting*, *Data Retention*.
- Bases de données opérationnelles :
	- *Bronze*, *Silver*
- Données transversales : 
	- *Metadata* (*Runs* et *Models Registry*), *Governance Policy*.

**R2.** L'ensemble des processus est organisé autour de la couche de données centrale *Bronze//Silver/Runs*

**R3.** La boucle du modèle est fermée : 
- *Models Training (2)* → *Models Registry* → *Transactions Ingestion (3b)*.
	- \> L'entraînement produit un champion et l'ingestion le consomme.

**R4.** Le processus d'ingestion, qui comprend également la phase de notification en cas de détection de fraude, est décomposé en ses 3 sous-processus pour clarifier les flux de données : (3a) écrit tout de suite les évènements bruts dans le *Bronze* avec de passer la main à (3b) ; (3b) reprend les évènements bruts, les traite, prédit un score de fraude, notifie une fraude détectée, puis passe la main à (3c) ; (3c) compare les évènements bruts avec les logs d'exécution dans *Runs* pour repérer les transactions perdues et notifie un canal d'opérateur en cas d'erreur. La séquence peut éventuellement être rejoué à partir de (3b).

## 1.2. Chargement des données historiques

*Object :* amorcer le système : charger les transactions historiques pour disposer d'un jeu
d'entraînement et d'un historique comportemental.

###### Diagramme détaillé : S1
![[diagrams/fraud-project--data-infrastructure--diagram-1.md]]

<div style="page-break-after: always;"></div>

## 1.3. Entrainement du modèle de scoring de fraude
*Object :* produire et enregistrer un modèle à partir des transactions et des verdicts connus à partir d'une certaine date de coupure.

###### Diagramme détaillé : S2
![[diagrams/fraud-project--data-infrastructure--diagram-2.md]]

<div style="page-break-after: always;"></div>

## 1.4. Ingestion continue des données temps-réelles avec notification de fraude

### 1.4.1. Fetching
*Objet :* Récupérer les transactions du simulateur une par une (API \[R4\]) et les stocker en l'état dans le magasin *Raw Events*.

###### Diagramme détaillé : S3.1
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-3-1.md]]

<div style="page-break-after: always;"></div>

### 1.4.2. Processing + Fraud Alerting
*Objet :* Récupérer les dernières transactions de *Raw Events* par lot, les prétraiter, les valider, les pseudonomiser, les enregistrer, prédire les scores de fraude, enregistrer les scores, journaliser la séance d'exécution dans *Runs*, notifier en cas de détection de fraude.

###### Diagramme détaillé : S3.2
![[diagrams/fraud-project--data-infrastructure--diagram-3-2.md]]

<div style="page-break-after: always;"></div>

### 1.4.3. Checking + Ops Alerting
*Objet :* détecter les erreurs d'ingestion en comparant les derniers évènements bruts avec les journaux d'exécution de *Runs*.
###### Diagramme détaillé : S3.3
![[diagrams/fraud-project--data-infrastructure--diagram-3-3.md]]

<div style="page-break-after: always;"></div>

### 1.4.3. Verdicts Source
###### Diagramme détaillé : S3.4
![[diagrams/fraud-project--data-infrastructure--diagram-3-4.md]]

<div style="page-break-after: always;"></div>

## 1.5. Reporting quotidien
*Objet :* produire périodiquement, le matin, un rapport des transactions et des fraudes prédites de la veille.
###### Diagramme détaillé : S4
![[diagrams/fraud-project--data-infrastructure--diagram-4.md]]

<div style="page-break-after: always;"></div>

## 1.6. Purge des données brutes et des journaux

*Objet :* appliquer la politique de rétention de la politique de gouvernance : supprimer les évènements plus âgés que la durée de conservation dans *Raw Events* et dans *Quarantine* .
###### Diagramme détaillé : S5
![[diagrams/fraud-project--data-infrastructure--diagram-5.md|700]]

<div style="page-break-after: always;"></div>

## 1.7. Pile technique consolidée

| Technologie        | Rôle                                                                                                              | Pourquoi                                                                          |
| ------------------ | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Airflow**        | orchestration des 5 traitements,<br/>à 5 cadences propres                                                         | C3 ; reprises, journaux, interface                                                |
| **PostgreSQL**     | persistence des données structurées : `raw_events`, `transactions`, `ground_truth`, `quarantine`, `pipeline_runs` | volumétrie modeste ; `JSONB` pour la zone brute ; déclencheurs pour l'immuabilité |
| **MLflow**         | registre de modèles                                                                                               | « mise en production » exigée par l'énoncé                                        |
| **Parquet**        | jeux d'entraînement versionnés                                                                                    | Seconde technologie de stockage ; sert C2                                         |
| **Python**         | ingestion, validation, scoring, entraînement                                                                      | *scikit-learn* ou *LightGBM*                                                      |
| **Streamlit**      | rapport quotidien, pages de notification et vues d'exploitation                                                   | Lit directement les données de rapport dans PostgreSQL                            |
| **Docker Compose** | déploiement                                                                                                       | Reproductibilité                                                                  |

*Parquet* : permet de versionner les jeux d'entraînement hors de la base.

---

<div style="page-break-after: always;"></div>

## Légendes des diagrammes
###### Liens
![[diagrams/fraud-project--data-infrastructure--diagram-legends.svg|200]]

###### Couleurs
![[diagrams/fraud-project--data-infrastructure--diagram-legends-2.svg]]

###### Formes
![[diagrams/fraud-project--data-infrastructure--diagram-legends-3.svg]]

---

## Références

#### Spécifications
- \[D0\] [*Automatic Fraud Detection Project* Introduction](fraud-project--d0-introduction.pdf)

#### Ressources
- \[R3\] [Fraudulent Payments full dataset](https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv)
- \[R4\] [Real-time payment API](https://huggingface.co/spaces/sdacelo/real-time-fraud-detection)

---

<div style="page-break-after: always;"></div>

## TMP : Ce qui est réalisé

###### Les deux objectifs métier 

G1 et G2 sont couverts intégralement : une transaction entre, elle est validée, enrichie, scorée, persistée, et l'analyste est notifié si la décision est « fraude » ; chaque matin, le responsable métier dispose du bilan de la veille, avec la performance réellement observée du modèle.

###### Six traitements automatisés

| Traitement | Cadence | Objet |
| ---------- | ------- | ----- |
| `dag_load_history` | manuel | amorçage : jeu d'entraînement et antériorité comportementale |
| `dag_ingest` | chaque minute | ingestion, scoring, notification, contrôles |
| `dag_ingest_verdicts` | quotidien, 02:00 | écriture différée du verdict : `label_ts = txn_ts + délai` |
| `dag_train` | hebdomadaire, 3:00 | construction du jeu, entraînement, enregistrement |
| `dag_daily` | quotidien, 06:00 | bilan métier et performance du modèle |
| `dag_purge` | hebdomadaire, dimanche 04:00 | purge au-delà de la durée de conservation |

Deux précisions sur ce tableau, apportées par la réalisation.

**Le traitement d'écriture du verdict n'était pas dans la v12**, et son
existence est une décision de conception prise en S3, lot N6. Le diagramme 3.2
fait écrire le verdict par le stade de traitement de `dag_ingest`, et c'est
réalisable : l'API renvoie l'étiquette, donc l'ingestion pourrait écrire
`(txn_id, label, label_ts)` à la seconde zéro.

Ce qui retient le verdict n'est pourtant pas le moment de l'écriture, mais
`label_ts = txn_ts + délai` et le filtre `label_ts <= coupure` appliqué par les
consommateurs : replier l'écriture dans `dag_ingest` **ne réduirait la bande
aveugle d'aucune seconde**. Le traitement séparé achète une seule chose, et elle
est structurelle plutôt que logique : `dag_ingest` n'importe ni le module de
vérité terrain ni celui des verdicts, donc l'étiquette n'est pas *atteignable*
depuis le processus qui score. Non pas « le code ne s'en sert pas », mais « le
nom n'est pas dans la portée » --- une barrière contre une modification future,
et non contre le flux actuel. L'étiquette est en effet déjà présente dans la
charge utile brute que l'ingestion écrit ; ce qu'elle ne fait pas, c'est la
porter là où un scoreur la lit, `transactions` ne portant aucune colonne
d'étiquette.

**`dag_daily` passe de 08:00 à 06:00**, et le traitement d'écriture du verdict
porte le nom `dag_ingest_verdicts` --- il appartient à la famille de
l'ingestion, comme son préfixe le dit désormais. L'heure répond à une
dépendance et à un usage : le bilan lit en section 3 les verdicts échus, écrits
à 02:00, donc il doit passer après ; et un rapport produit à 08:00 ferait
attendre l'analyste qui arrive à 08:00.

###### Volumétrie retenue pour le dimensionnement

| Dimension        | Valeur                                                            | Conséquences |
| ---------------- | ----------------------------------------------------------------- | ------------------------------ |
| **Vélocité**     | 5 appels/minute (plafond API de test) ~~, 1 exécution/minute~~    | Traitement par *micro-lots*, sans service de scoring résident |
| **Volume**       | 7 200 transactions/jour, 555 719 lignes d'historique,   4 Go/an   | Base relationnelle *mono-noeud*, non distribuée |
| **Typologie**    | JSON, horodatage en millisecondes, 22 attributs dont 8 nominatifs | Normalisation des horodatages, pseudonymisation, règles de validation |
| **Fraudulosité** | 0,386 % (386 / 100_000), soit 28 fraudes/jour | Budget usuel de 2 fraudes / heure) = ok |

###### Pile technique

| Technologie                 | Rôle                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------ |
| **Airflow**                 | orchestration des six traitements                                                    |
| **Airflow Variables**<br/>+**YAML** | configurations et paramètres des politiques                                          |
| **PostgreSQL**              | `raw_events` (JSONB), `transactions`, `ground_truth`, `quarantine`, `pipeline_runs`  |
| **MLflow**                  | registre de modèles, traçabilité modèle ↔ jeu de données                             |
| **Parquet**                 | jeux d'entraînement versionnés --- seconde technologie de stockage, au service de C2 |
| **Python**                  | ingestion, validation, scoring, entraînement                                         |
| **Streamlit**               | restitution du bilan quotidien et vue d'exploitation                                 |
| **Docker Compose**          | déploiement local reproductible                                                      |
