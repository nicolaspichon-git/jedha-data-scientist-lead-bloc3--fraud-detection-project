---
version: v02
locale: fr
tags:
  - _RNCP38777
  - _2026
  - aia
  - aia/bc03
  - fraud-project
  - fraud-project/step-1
  - fraud-project/gouvernance
---

*AUTOMATIC FRAUD DETECTION* PROJECT
===
# 1. Data Infrastructure Design
## Appendices 
### 1.B. Appendix B : Data Governance Policy

> *Nicolas Pichon --- AIA RNCP 38777 / BC03 / D1 / Annexe B : Data Governance Policy / v02 --- 2026/11/26.*
---

#### 1.D.0. Contexte

Ce document annexe présente la politique de gouvernance référencée dans \[D0, §0.4.3\] comme le document *D09*. Il est versionné en tant que code dans le fichier de configuration `governance.yml`. Il est destiné à satisfaire l'exigence *EC16* : formaliser par écrit les données personnelles identifiées, leur pseudonymisation ou minimisation, les rôles et droits, et les durées de conservation.

#### 1.D.1. Données personnelles

Un inventaire des données personnelles est établi sur les colonnes du jeu de données \[R3\]. Les données ci-dessous portent sur les 555719 transactions du jeu complet.

| Colonne | Nature | Constat | Traitement |
| --- | --- | --- | --- |
| `cc_num` | identifiant | 924 valeurs distinctes,<br/>7 longueurs distinctes,<br/>toutes valides au sens de Luhn | pseudonymisée |
| `first`, `last` | identité | — | écartée |
| `street`, `city`, `state`, `zip` | adresse | — | écartée |
| `lat`, `long` | domicile du porteur | constantes pour chacun des 924 porteurs (c'est l'adresse) | minimisée |
| `job`, `dob` | données personnelles | — | écartée |
| `gender` | caractéristique protégée | 250 833 M / 304 886 F ; n'identifie personne | écartée *par choix éthique* |
| `city_pop` | quasi-identifiant | 835 valeurs distinctes, dont 791 (94,7 %) désignent une seule ville ; constante par porteur | écartée |
| `merchant`, `category`, `amt`, `merch_lat`, `merch_long`, `trans_num`, `trans_date_trans_time`, `is_fraud` | données de transaction | — | conservée |

#### 1.D.2. Pseudonymisation et minimisation

##### 1.D.2.1. `cc_num` : pseudonymisation

Cette valeur est remplacée par  une clé à l'ingestion : `client_key = HMAC-SHA256(poivre, cc_num)`, tronqué à 128 bits.

*Pourquoi un HMAC?* L'espace de clés ne compte que *924 valeurs*. Un condensé non salé s'inverse en les énumérant toutes, ce qui prend une fraction de seconde. Le poivre est un secret de 256 bits, conservé dans l'environnement de l'hôte mais jamais dans le code versionné (`governance.yml` ou autre).

*Conséquence :* changer le poivre invalide toutes les clés `client_key` déjà
calculés, et donc l'historique comportemental.

##### 1.D.2.2. `lat` / `long` : minimisation

Les coordonnées de position sont éventuellement constantes par porteur : les conserver permet d'identifier conserver un domicile fixe associé au client.

Ces coordonnées sont lues dans la zone brute, consommées à l'ingestion pour calculer `f_home_distance_km` (distance orthodromique entre le domicile et le commerçant) mais  n'atteignent jamais la couche exploitée.

Une distance ne permet pas de retrouver une adresse : elle définit un cercle autour du commerçant, mais pas plus. Le signal est donc préservé (la distance domicile/commerçant est l'un des indices de fraude les plus classiques sur ce type de données) sans trahir la confidentialité de la localisation.

##### 1.D.2.3. Colonnes écartées

**`city_pop` : quasi-identifiant.** 835 valeurs distinctes, dont 791 (94,7 %) ne correspondent qu'à une seule ville, et la valeur est constante par porteur. La conserver annulerait l'intérêt du retrait de `city`, `state`, `zip`, `lat` et `long` : la ville du porteur reviendrait sous une forme déguisée.

**`gender` : caractéristique protégée.** Elle n'identifie personne. Mais elle alimenterait le modèle de scoring, et un score de fraude qui diffère selon le genre pose une question d'équité que ce dossier ne prétend pas traiter. L'écarter est la politique par défaut prudente. L'inclure demanderait une justification et une mesure de l'écart de traitement, hors du périmètre de l'exercice.

#### 1.D.3. Rôles et droits

Les rôles de groupe n'ont pas d'attribut `LOGIN` : ils ne peuvent pas ouvrir de connexion. L'application se connecte avec l'identité de `POSTGRES_USER` puis émet `SET ROLE`. 

| Rôle | Droits |
| --- | --- |
| `fd_ingest` | `SELECT`, `INSERT` sur les quatre magasins ; `UPDATE` sur `fd_pipeline_runs` seulement |
| `fd_report` | `SELECT` sur la couche exploitée, la quarantaine et le journal |
| `fd_purge`  | \[...\] |

**Remarque.** `fd_report` n'a aucun accès à la zone brute. Les charges utiles de `fd_raw_events` portent encore les noms, les adresses et les numéros de carte en clair : la pseudonymisation n'opère qu'à l'entrée de la couche exploitée. Donner au rôle de restitution un droit de lecture sur la zone brute annulerait l'effet de l'exigence *EC17*. Conséquence pratique : un outil qui mesure la volumétrie de la zone brute doit s'exécuter avec le rôle `fd_ingest`, et ne lire que des décomptes et des tailles, jamais des contenus.

**Remarque.** La restriction d'accès `append-only` de `fd_raw_events` vient d'une révocation :

```sql
REVOKE UPDATE, DELETE, TRUNCATE ON fd_raw_events FROM fd_ingest;
```

Après `SET ROLE`, la session perd l'attribut "super utilisateur" et les contrôles de droits s'appliquent normalement. La garantie est donc vérifiable à l'exécution : la tâche `preflight` du DAG tente un `UPDATE` sur `fd_raw_events` et exige qu'il échoue. Le journal porte la trace du refus (`InsufficientPrivilege`) à chaque exécution.

#### 1.D.4. Durées de conservation

| Donnée | Durée | Paramètre |
| --- | --- | --- |
| `fd_raw_events` | 90 jours | `retention.raw_events_days` |
| `fd_pipeline_runs` | 365 jours | `retention.pipeline_runs_days` |
| Délai de verdict | 30 jours | `verdicts.delay_days` |

**Remarque.** La durée de conservation est aussi la fenêtre de rejeu. Gouvernance et auditabilité sont des contraintes en sens opposés. Les faire coïncider est la solution minimale acceptable à l'échelle de l'exercice. Conséquence : au-delà de 90 jours, une erreur de typage ou de séparation n'est plus rattrapable depuis la zone brute.

Les durées de retention qui dépassent celle de la démonstration sont paramétrées (EI12) : cf. paramètre de configuration `verdicts.demo_delay_seconds`.

#### 1.D.5. Application de la politique dans le code

| Décision | Emplacement |
| --- | --- |
| Inventaire, exclusions, durées | `governance.yml` |
| Pseudonymisation de `cc_num` | `fraud/transform.py` : `client_key()` |
| Minimisation de `lat` / `long` | `fraud/transform.py` : `home_distance_km()` |
| Absence d'identité en sortie | `tests/test_transform.py` |
| Rôles, droits, *append-only* | `sql/ddl/060_roles_grants.sql` |
| Vérification de l'accès '*append-only* | `airflow/dags/dag_load_history.py` : `preflight()` |
| Application des durées | S5 *(à construire)* |

La matrice de traçabilité est produite par `tools/build_traceability.py` et rapportée dans le document `TRACEABILITY.md`.

#### Références
##### Spécifications
- \[D0\] [*Automatic Fraud Detection Project* Introduction](../../step-0/fraud-project--d0-introduction.pdf)
- \[D1\] [*Data Infrastructure Design*](../fraud-project--d1-data-infrastructure.pdf)
#### Ressources
- \[R3\] [Fraudulent Payments full dataset](https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv)

---
