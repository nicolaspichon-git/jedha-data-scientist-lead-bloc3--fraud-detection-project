---
version: v18
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

> *Nicolas Pichon --- AIA RNCP 38777 / BC03 / Data Infrastructure Design / v18 --- 2026/11/16.*
---
## 1.0. Contexte 

Ce document présente l'architecture de l'infrastructure de données spécifiée dans \[B3-D0\].
## 1.1. Vue d'ensemble

#### 1.1.1. Objectifs métier 

Les deux objectifs métiers posés dans  \[B3-D0\], *B3-G1* et *B3-G2*, sont couverts intégralement par le système : 
- *B3-G1* : une transaction est ingérée, elle est validée, enrichie, scorée, persistée, et l'analyste est notifié en cas de signalement de fraude probable ; 
- *B3-G2* : chaque matin, le métier recoit un bilan du traffic de la veille, incluant la performance observée du modèle.

#### 1.1.2. Pipelines automatisés

Pour couvrir les objectifs du métier et les automatiser, on a mis en place 6 pipelines de données dont 5 sont automatisés :

| Traitement            | Cadence                      | Objet                                                        |
| --------------------- | ---------------------------- | ------------------------------------------------------------ |
| `dag_load_history`    | manuel                       | amorçage : jeu d'entraînement et antériorité comportementale |
| `dag_ingest`          | chaque minute                | ingestion, scoring, notification, contrôles                  |
| `dag_ingest_verdicts` | quotidien, 02:00             | écriture différée du verdict : `label_ts = txn_ts + délai`   |
| `dag_train`           | hebdomadaire, 3:00           | construction du jeu, entraînement, enregistrement            |
| `dag_daily`           | quotidien, 06:00             | bilan métier et performance du modèle                        |
| `dag_purge`           | hebdomadaire, dimanche 04:00 | purge au-delà de la durée de conservation                    |

### 1.1.3. Volumétrie retenue 

| Dimension        | Valeur                                                            | Conséquences |
| ---------------- | ----------------------------------------------------------------- | ------------------------------ |
| **Vélocité**     | 5 appels/minute (plafond API de test)                             | Traitement par *micro-lots*, sans service de scoring résident |
| **Volume**       | 7 200 transactions/jour, 555 719 lignes d'historique,   4 Go/an   | Base relationnelle *mono-noeud*, non distribuée |
| **Typologie**    | JSON, horodatage en millisecondes, 22 attributs dont 8 nominatifs | Normalisation des horodatages, pseudonymisation, règles de validation |
| **Fraudulosité** | 0,386 % (386 / 100_000), soit 28 fraudes/jour | Budget usuel de 2 fraudes / heure) = ok |

### 1.1.4. Pile technique

Les composants principaux de l'infrastructure sont conteneurisés (*Airflow*, *PostgreSQL*, *MLflow*, producteur temps-réel *FastAPI*, dashboard *Streamlit*) mais le système complet n'est encore déployé que *localement* (*on-premise*).

| Technologie                                 | Rôle                                                                                                                          |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Docker&nbsp;Compose**                     | déploiement                                                                                                                   |
| **Airflow**                                 | orchestration des traitements                                                                                                 |
| **Airflow&nbsp;Variables&nbsp;+&nbsp;YAML** | configurations et paramètres des politiques                                                                                   |
| **PostgreSQL**                              | persistence des données structurées :<br/>`raw_events` (JSONB), `transactions`, `ground_truth`, `quarantine`, `pipeline_runs` |
| **MLflow**                                  | registre de modèles                                                                                                           |
| **Parquet**                                 | jeux d'entraînement versionnés                                                                                                |
| **Python**                                  | ingestion, validation, scoring, entraînement                                                                                  |
| **Streamlit**                               | rapport quotidien, pages de notification, vues d'exploitation                                                                 |

###### Justifications

| Technologie             | Justification                                                                     |
| ----------------------- | --------------------------------------------------------------------------------- |
| **Docker&nbsp;Compose** | Reproductibilité                                                                  |
| **Airflow**             | B3-C3 ; reprises, journaux, interface                                             |
| **PostgreSQL**          | volumétrie modeste ; `JSONB` pour la zone brute ; déclencheurs pour l'immuabilité |
| **MLflow**              | « mise en production » exigée par l'énoncé                                        |
| **Parquet**             | Seconde technologie de stockage ; sert B3-C2                                      |
| **scikit-learn**        | modèle : `sklearn.ensemble.HistGradientBoostingClassifier`                        |
| **Streamlit**           | Lit directement les données de rapport dans *PostgreSQL*                          |

*Parquet* : permet de versionner les jeux d'entraînement hors de la base.

<div style="page-break-after: always;"></div>

### 1.1.5. Architecture générale

 *Object :* présenter les principaux composants de l'infrastructure, processus et bases de données, les flux de données entre eux, les flux de contrôles et les dépendances.  
 
###### Diagramme 
![[diagrams/fraud-project--data-infrastructure--diagram-0.md]]

> _\> Les numéros portés par les blocs de pipeline ((1) à (5)) renvoient aux diagrammes détaillés des processus (B3-S1 à B3-S5)._

###### Remarques
**R1.** L'ensemble est formé de trois familles de sous-systèmes :
- Pipelines portant des transactions : 
	- *Historical Data Loading*, *Transactions Ingestion*, *Models Training*, *Daily Reporting*, *Data Retention*.
- Bases de données opérationnelles :
	- *Bronze*, *Silver*
- Données transversales : 
	- *Metadata* (*Runs* et *Models Registry*), *Governance Policy*.

**R2.** L'ensemble des processus est organisé autour de la couche de données centrale *Bronze//Silver/Runs*

**R3.** Le flux de transactions passant par le modèle est presque fermé : 
- *Historical Transactions (1)* → *Models Training (2)* → *Models Registry* → *Transactions Ingestion (3b)* → potential retraining.

**R4.** Le processus d'ingestion, qui comprend également la phase de notification en cas de détection de fraude, est décomposé en 3 sous-processus virtuels pour clarifier les flux de données : (3a) écrit tout de suite les évènements bruts dans le *Bronze* avec de passer la main à (3b) ; (3b) reprend les évènements bruts, les traite, prédit un score de fraude, notifie une fraude détectée, puis passe la main à (3c) ; (3c) compare les évènements bruts avec les logs d'exécution dans *Runs* pour repérer les transactions perdues et notifie un canal d'opérateur en cas d'erreur. La séquence peut éventuellement être rejoué à partir de (3b).

## 1.2. Chargement des données historiques

*Object :* amorcer le système : charger les transactions historiques libellées pour disposer d'un jeu
d'entraînement et d'un historique comportemental.

###### Diagramme détaillé : B3-S1
![[diagrams/fraud-project--data-infrastructure--diagram-1.md]]

<div style="page-break-after: always;"></div>

## 1.3. Entrainement du modèle de scoring de fraude

*Object :* produire et enregistrer un modèle à partir des transactions et des verdicts connus à partir d'une certaine date de coupure.

###### Diagramme
![[diagrams/fraud-project--data-infrastructure--diagram-2.md]]

<div style="page-break-after: always;"></div>

## 1.4. Ingestion continue des données temps-réelles avec notification de fraude

### 1.4.1. Fetching
*Objet :* Récupérer les transactions du simulateur une par une (API \[R4\]) et les stocker en l'état dans le magasin *Raw Events*.

###### Diagramme
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-3-1.md]]

<div style="page-break-after: always;"></div>

### 1.4.2. Processing + Fraud Alerting
*Objet :* Récupérer les dernières transactions de *Raw Events* par lot, les prétraiter, les valider, les pseudonomiser, les enregistrer, prédire les scores de fraude, enregistrer les scores, journaliser la séance d'exécution dans *Runs*, notifier en cas de détection de fraude.

###### Diagramme
![[diagrams/fraud-project--data-infrastructure--diagram-3-2.md]]

<div style="page-break-after: always;"></div>

### 1.4.3. Checking + Ops Alerting
*Objet :* détecter les erreurs d'ingestion en comparant les derniers évènements bruts avec les journaux d'exécution de *Runs*.

###### Diagramme
![[diagrams/fraud-project--data-infrastructure--diagram-3-3.md]]

<div style="page-break-after: always;"></div>

### 1.4.4. Ingestion de verdicts

###### Diagramme
![[diagrams/fraud-project--data-infrastructure--diagram-3-4.md]]

<div style="page-break-after: always;"></div>

## 1.5. Reporting quotidien
*Objet :* produire périodiquement, le matin, un rapport des transactions et des fraudes prédites de la veille.
###### Diagramme détaillé : B3-S4
![[diagrams/fraud-project--data-infrastructure--diagram-4.md]]

<div style="page-break-after: always;"></div>

## 1.6. Purge des données brutes et des journaux

*Objet :* appliquer la politique de rétention de la politique de gouvernance : supprimer les évènements plus âgés que la durée de conservation dans *Raw Events* et dans *Quarantine* .

###### Diagramme 
![[diagrams/fraud-project--data-infrastructure--diagram-5.md|700]]

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
- \[B3-D0\] [*Automatic Fraud Detection Project* Introduction](fraud-project--d0-introduction.pdf)
#### Ressources
- \[R3\] [Fraudulent Payments full dataset](https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv)
- \[R4\] [Real-time payment API](https://huggingface.co/spaces/sdacelo/real-time-fraud-detection)
