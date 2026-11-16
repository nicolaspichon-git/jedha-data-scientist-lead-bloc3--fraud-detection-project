---
version: v12
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

> *Nicolas Pichon --- AIA RNCP 38777 / BC03 / Data Infrastructure Design / v12 --- 2026/11/26.*
---

## 1.1. Vue d'ensemble 

 *Object :* présenter les principaux composants de l'infrastructure, processus et bases de données, les flux de données entre eux, les flux de contrôles et les dépendances.  
 
###### Diagramme
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-0.svg]]

> Les numéros portés par les blocs de pipeline ((1) à (5)) renvoient aux diagrammes détaillés des processus (S1 à S5).
<div style="page-break-after: always;"></div>

###### Remarques
- L'ensemble est formé de trois familles de sous-systèmes :
	- Pipelines portant des transactions : 
		- *Historical Data Loading*, *Transactions Ingestion*, *Models Training*, *Daily Reporting*, *Data Retention*.
	- Bases de données opérationnelles :
		- *Bronze*, *Silver*
	- Données transversales : 
		- *Metadata* (*Runs* et *Models Registry*), *Governance Policy*.
- L'ensemble des processus est organisé autour de la couche de données centrale *Bronze//Silver/Runs*
- La boucle du modèle est fermée : 
	- *Models Training (2)* → *Models Registry* → *Transactions Ingestion (3b)*.
	- > L'entraînement produit un champion et l'ingestion le consomme.
- Le processus d'ingestion, qui comprend également la phase de notification en cas de détection de fraude, est décomposé en ses 3 sous-processus pour clarifier les flux de données : (3a) écrit tout de suite les évènements bruts dans le *Bronze* avec de passer la main à (3b) ; (3b) reprend les évènements bruts, les traite, prédit un score de fraude, notifie une fraude détectée, puis passe la main à (3c) ; (3c) compare les évènements bruts avec les logs d'exécution dans *Runs* pour repérer les transactions perdues et notifie un canal d'opérateur en cas d'erreur. La séquence peut éventuellement être rejoué à partir de (3b).
## 1.2. Chargement des données historiques

*Object :* amorcer le système : charger les transactions historiques pour disposer d'un jeu
d'entraînement et d'un historique comportemental.

###### Diagramme détaillé : S1
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-1.svg]]

## 1.3. Entrainement du modèle de scoring de fraude
*Object :* produire et enregistrer un modèle à partir des transactions et des verdicts connus à partir d'une certaine date de coupure.

###### Diagramme détaillé : S2
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-2.svg]]

<div style="page-break-after: always;"></div>

## 1.4. Ingestion continue des données temps-réelles avec notification de fraude

### 1.4.1. Fetching
*Objet :* Récupérer les transactions du simulateur une par une (API \[R4\]) et les stocker en l'état dans le magasin *Raw Events*.

###### Diagramme détaillé : S3.1
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-3-1.svg]]

<div style="page-break-after: always;"></div>

### 1.4.2. Processing + Fraud Alerting
*Objet :* Récupérer les dernières transactions de *Raw Events* par lot, les prétraiter, les valider, les pseudonomiser, les enregistrer, prédire les scores de fraude, enregistrer les scores, journaliser la séance d'exécution dans *Runs*, notifier en cas de détection de fraude.

###### Diagramme détaillé : S3.2
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-3-2.svg]]

<div style="page-break-after: always;"></div>

### 1.4.3. S3.3 : Checking + Ops Alerting
*Objet :* détecter les erreurs d'ingestion en comparant les derniers évènements bruts avec les journaux d'exécution de *Runs*.
###### Diagramme détaillé : S3.3
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-3-3.svg]]

<div style="page-break-after: always;"></div>

## 1.5. Reporting quotidien
*Objet :* produire périodiquement, le matin, un rapport des transactions et des fraudes prédites de la veille.
###### Diagramme détaillé : S4
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-4.svg]]

## 1.6. Purge des données brutes et des journaux

*Objet :* appliquer la politique de rétention de la politique de gouvernance : supprimer les évènements plus âgés que la durée de conservation dans *Raw Events* et dans *Quarantine* .
###### Diagramme détaillé : S5
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-5.svg]]

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

---

<div style="page-break-after: always;"></div>


## 1.x. TMP : Ce qui est réalisé

###### Les deux objectifs métier 

G1 et G2 sont couverts intégralement : une transaction entre, elle est validée, enrichie, scorée, persistée, et l'analyste est notifié si la décision est « fraude » ; chaque matin, le responsable métier dispose du bilan de la veille, avec la performance réellement observée du modèle.

###### Cinq traitements automatisés

| Traitement | Cadence | Objet |
| ---------- | ------- | ----- |
| `dag_load_history` | manuel | amorçage : jeu d'entraînement et antériorité comportementale |
| `dag_ingest` | chaque minute | ingestion, scoring, notification, contrôles |
| `dag_train` | hebdomadaire | construction du jeu, entraînement, enregistrement |
| `dag_daily` | quotidien, 08:00 | bilan métier, performance du modèle, contrôle d'absence |
| `dag_retention` | quotidien, 02:00 | purge au-delà de la durée de conservation |

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
| **Airflow**                 | orchestration des cinq traitements                                                   |
| **Airflow Variables**<br/>+**YAML** | configurations et paramètres des politiques                                          |
| **PostgreSQL**              | `raw_events` (JSONB), `transactions`, `ground_truth`, `quarantine`, `pipeline_runs`  |
| **MLflow**                  | registre de modèles, traçabilité modèle ↔ jeu de données                             |
| **Parquet**                 | jeux d'entraînement versionnés --- seconde technologie de stockage, au service de C2 |
| **Python**                  | ingestion, validation, scoring, entraînement                                         |
| **Streamlit**               | restitution du bilan quotidien et vue d'exploitation                                 |
| **Docker Compose**          | déploiement local reproductible                                                      |

---

## Légendes des diagrammes
###### Liens
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-legends.svg]]

###### Couleurs
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-legends-2.svg]]

###### Formes
![[step-1/diagrams/fraud-project--data-infrastructure--diagram-legends-3.svg]]

<div style="page-break-after: always;"></div>

---

## Couverture fonctionnelle 

On vérifie dans le tableau suivant que tous les processus présentés dans les diagrammes précédents couvrent bien toutes les fonctionnalités attendues identifiées dans \[D0\] (chaque processus est justifié et chaque fonctionnalité est couverte par au moins un processus).

| Processus                 | Fonctionnalités                                                       |
| ------------------------- | --------------------------------------------------------------------- |
| `dag_load_history`        | F02.2, F03.1, F04.1, F04.2, F09.1, F09.2, F09.3, F09.4                |
| `dag_ingest : fetch`      | F02.1, F03.1, F10.1                                                   |
| `dag_ingest : process`    | F02.3, F03.2, F04.1, F06.1, F06.2, F09.1,  F09.2, F09.3, F09.4, F11.1 |
| `dag_ingest : check`      | F10.1, F10.2, F10.3                                                   |
| `dag_train`               | F05.1, F05.2, F05.3, F08.2                                            |
| `dag_daily`               | F07.1, F07.2, F07.3, F08.2, F10.2                                     |
| `dag_retention`           | F12.2 (purge)                                                         |
| déploiement   | F03.3 (bases), F08.1 (orchestration), F12.1 (accès & secrets), F13.1 (paramètres) |

Les trois registres du diagramme --- decision policy, governance policy et verdict delay --- ne  
réalisent aucune fonctionnalité à eux seuls : ils externalisent les paramètres de F06.1,  
F11.1/F12.2 et F02.3 respectivement, afin qu'une décision métier, une règle de conformité  
ou un réglage de simulation ne soient pas codés en dur.

---

## Références

#### Spécifications
- \[D0\] [*Automatic Fraud Detection Project* Introduction](fraud-project--d0-introduction.pdf)

#### Ressources
- \[R3\] [Fraudulent Payments full dataset](https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv)
- \[R4\] [Real-time payment API](https://huggingface.co/spaces/sdacelo/real-time-fraud-detection)

---
