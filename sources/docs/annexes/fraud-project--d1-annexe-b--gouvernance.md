---
version: v05
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

> *Nicolas Pichon --- AIA RNCP 38777 / BC03 / B3-D1 / Annexe B : Data Governance Policy / v05 --- 2026/11/26.*
---

#### 1.D.0. Contexte

Ce document annexe présente la politique de gouvernance référencée dans \[B3-D0, §0.4.3\] comme le document *B3-H09*. Il est versionné en tant que code dans le fichier de configuration `governance.yml`. Il est destiné à satisfaire l'exigence *B3-EC16* : formaliser par écrit les données personnelles identifiées, leur pseudonymisation ou minimisation, les rôles et droits, et les durées de conservation. Il décrit aussi comment ces durées sont **appliquées** (*B3-EC18*).

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

Cette valeur est remplacée par une clé à l'ingestion : `client_key = HMAC-SHA256(poivre, cc_num)`, tronquée à 128 bits (32 caractères hexadécimaux).

*Pourquoi un HMAC?* L'espace de clés ne compte que *924 valeurs*. Un condensé non salé s'inverse en les énumérant toutes, ce qui prend une fraction de seconde. Le poivre est un secret de 256 bits, conservé dans l'environnement de l'hôte mais jamais dans le code versionné (`governance.yml` ou autre).

*Conséquence :* changer le poivre invalide toutes les clés `client_key` déjà calculés, et donc l'historique comportemental.

##### 1.D.2.2. `lat` / `long` : minimisation

Les coordonnées de position du porteur sont éventuellement constantes : les conserver permet d'identifier conserver un domicile fixe associé au client.

Ces coordonnées sont lues dans la zone brute, consommées à l'ingestion pour calculer `f_home_distance_km` (distance orthodromique entre le domicile et le commerçant) mais  n'atteignent jamais la couche exploitée.

Une distance ne permet pas de retrouver une adresse : elle définit un cercle autour du commerçant, mais pas plus. Le signal est donc préservé (la distance domicile/commerçant est l'un des indices de fraude les plus classiques sur ce type de données) sans trahir la confidentialité de la localisation.

##### 1.D.2.3. Colonnes écartées

**`city_pop` : quasi-identifiant.** 835 valeurs distinctes, dont 791 (94,7 %) ne correspondent qu'à une seule ville, et la valeur est constante par porteur. La conserver annulerait l'intérêt du retrait de `city`, `state`, `zip`, `lat` et `long` : la ville du porteur reviendrait sous une forme déguisée.

**`gender` : caractéristique protégée.** Elle n'identifie personne. Mais elle alimenterait le modèle de scoring, et un score de fraude qui diffère selon le genre pose une question d'équité que ce dossier ne prétend pas traiter. L'écarter est la politique par défaut prudente. L'inclure demanderait une justification et une mesure de l'écart de traitement, hors du périmètre de l'exercice.

##### 1.D.2.4. Sorties du système

Les canaux de notification (alerte analyste, canal d'exploitation) refusent tout champ personnel par construction. 
Le rapport du matin doit nommer les transactions par identifiant et par montant.

#### 1.D.3. Rôles et droits

Les rôles de groupe n'ont pas d'attribut `LOGIN` : ils ne peuvent pas ouvrir de connexion. L'application se connecte avec l'identité de `POSTGRES_USER` puis émet `SET ROLE`, après quoi la session perd l'attribut de super-utilisateur et les contrôles de droits s'appliquent normalement.

| Rôle        | Autorisations | Interdictions |
| ----------- | ------------- | ------------- |
| `fd_ingest` | lire et insérer dans la zone brute, la quarantaine, les transactions, les verdicts, les scores, les alertes, les jeux d'entraînement, le journal du canal d'exploitation ; mettre à jour le journal d'exécutions, l'état d'exploitation et les **mesures de B3-M5** d'un jeu d'entraînement | modifier ou supprimer la zone brute, les scores et le journal du canal d'exploitation ; supprimer une alerte ; modifier une colonne métier d'une transaction ; modifier un jeu d'entraînement hors de ses mesures |
| `fd_report` | lire la couche exploitée, la quarantaine, les journaux d'exécutions et de purges ; écrire le journal des rapports | lire la zone brute ; supprimer un rapport |
| `fd_purge`  | lire et supprimer dans la zone brute et la quarantaine ; poser les marqueurs de purge dans le journal d'exécutions ; inscrire une ligne au journal des purges | **lire ou modifier la couche exploitée**, insérer dans la zone brute, supprimer une ligne du journal d'exécutions, modifier ou supprimer le journal des purges |
| `fd_dashboard` | **se connecter** (seul rôle `LOGIN`, mot de passe dans `.env`) ; lire les rapports, les alertes, les transactions, les verdicts, les scores, le journal d'exécutions, l'état des contrôles et le journal du canal d'exploitation ; lire **cinq colonnes** de la quarantaine (`batch_id`, `line_no`, `reason_class`, `reason_code`, `rejected_at`) et **neuf colonnes** du catalogue des jeux (identité, part de fraudes, mesures de B3-M5) | écrire quoi que ce soit ; lire la zone brute, la charge (`payload`) ou le détail (`reason_detail`) d'une ligne rejetée ; lire les chemins ou la liste des features d'un jeu ; endosser un autre rôle ; créer un objet |

Les droits sont accordés à la colonne et non à la table :

- `fd_ingest` n'écrit que les colonnes de features de `fd_transactions` (`f_tx_count`, `f_avg_amount`, `f_home_distance_km`) : les features se recalculent, les faits métier d'une transaction s'écrivent une fois ;
- `fd_ingest` n'écrit que l'état de notification de `fd_frauds` (`notified_at`, `channel`, `attempts`, `last_error`) : une alerte levée ne se réécrit pas ;
- `fd_purge` n'a aucun droit sur la couche exploitée. 

**Remarque.** `fd_report` n'a aucun accès à la zone brute car les charges utiles de `fd_raw_events` portent encore les noms, les adresses et les numéros de carte en clair (la pseudonymisation n'opère qu'à l'entrée de la couche exploitée). Donner au rôle de restitution un droit de lecture sur la zone brute annulerait l'effet de l'exigence *B3-EC17* \[B3-D0\]. Conséquence pratique : un outil qui mesure la volumétrie de la zone brute s'exécute avec le rôle `fd_ingest`, et ne lit que des décomptes et des tailles, jamais des contenus.

**Remarque.** La règle précédente n'est pas tenue pour la quarantaine. `fd_quarantine.payload` conserve la charge brute de chaque ligne rejetée, donc les mêmes données personnelles que la zone brute, et `fd_report` détient un `SELECT` sur toute la table. Le rapport du matin lit bien la quarantaine, mais seulement pour l'invariant de volume (`n_read` = transactions + lignes mises en quarantaine), qui ne touche que `batch_id` et `line_no`. Le correctif est un droit à la colonne excluant `payload`, comme pour les deux cas ci-dessus. Il n'est pas encore appliqué.

**Remarque.** La restriction *append-only* vient de révocations (et non d'une convention) :

```sql
REVOKE UPDATE, DELETE, TRUNCATE ON fd_raw_events FROM fd_ingest;
REVOKE UPDATE, DELETE, TRUNCATE ON fd_scores     FROM fd_ingest;
```

La garantie est vérifiable à l'exécution : la tâche `preflight` du chargement historique tente un `UPDATE` sur `fd_raw_events`, puis sur `fd_transactions.amt`, et exige que les deux échouent. Le journal porte la trace des deux refus (`InsufficientPrivilege`) à chaque exécution.

**Remarque.** Supprimer un lot nommé demande donc deux connexions pour deux rôles différents : 
- d'abord sous `fd_ingest`, qui voit tous les magasins et ne peut rien supprimer, 
- puis sous `fd_purge`, pour exécuter la suppression, qui ne voit pas la couche exploitée sur laquelle repose la décision. 

**Remarque.** Le tableau de bord est le seul composant ouvert à un navigateur, donc le seul rôle qui se connecte directement. Son conteneur ne reçoit ni le mot de passe du propriétaire ni le poivre, et refuse de servir si PostgreSQL dit que la session est un autre rôle ou un super-utilisateur. `fd_dashboard` n'est membre d'aucun rôle : `fd_report`, qui produit le rapport, peut écrire le journal des rapports, et en hériter aurait permis de réécrire l'empreinte qui prouve qu'un document n'a pas été modifié.


#### 1.D.4. Durées de conservation

##### 1.D.4.1. Magasins purgés

| Donnée | Durée | Paramètre |
| --- | --- | --- |
| `fd_raw_events` | 90 jours | `retention.raw_events_days` |
| `fd_quarantine` | 90 jours | `retention.quarantine_days` |
| Journaux d'Airflow | 30 jours | `retention.airflow_logs_days` |

Deux contraintes sont vérifiées au chargement de la configuration :

- *La quarantaine ne dure pas plus longtemps que la zone brute.* Sa charge est celle d'une ligne rejetée, donc la même donnée personnelle ; une ligne rejetée n'a pas moins droit à une conservation limitée qu'une ligne acceptée ;
- *Les journaux d'Airflow ne survivent pas aux données qu'ils peuvent citer.* Une trace d'exception peut reproduire une ligne de données.

**Remarque.** La durée de conservation est aussi la fenêtre de rejeu. Gouvernance et auditabilité sont des contraintes en sens opposés. Les faire coïncider est la solution minimale acceptable à l'échelle de l'exercice. Conséquence : au-delà de 90 jours, une erreur de typage ou de séparation n'est plus rattrapable depuis la zone brute.

##### 1.D.4.2. Magasins conservés

Une liste des magasins est déclaré dans `governance.yml` pour indiquer si un magasin doit être purgé ou non. Un magasin absent de cette déclaration est conservé tel quel.

| Magasin | Justification de la conservation |
| --- | --- |
| `fd_transactions` | aucune colonne identifiante (`client_key` est un pseudonyme) ; sert à l'entraînement et à l'audit |
| `fd_ground_truth` | un verdict par transaction et une date ; c'est la cible d'entraînement |
| `fd_scores`, `fd_frauds` | ce qui a été décidé, par quel modèle, et à qui cela a été notifié ; aucun champ personnel |
| `fd_pipeline_runs` | identifiants, dates, compteurs et **empreintes des lots** : c'est tout ce qui reste d'un lot purgé, et `fd_purge` n'a aucun droit de suppression sur cette table |
| `fd_ops_state` | une ligne par contrôle d'exploitation |
| `fd_ops_notifications` | le journal des messages envoyés au canal d'exploitation : un nom de contrôle, un état, des comptes ; quelques lignes par incident ; `fd_ingest` peut y insérer et rien d'autre |
| `fd_datasets`, jeux Parquet | le lien entre un modèle et les données dont il a appris ; aucun champ identifiant |
| `fd_purges` | la preuve que les durées sont **appliquées** ; `fd_purge` peut y insérer et rien d'autre |
| `fd_reports`, rapports Markdown | le journal et les documents du matin, ni porteur ni adresse |
| registre MLflow | un modèle en service doit rester reproductible |
| cache local du CSV historique | c'est la source, hors dépôt, et elle se retélécharge |

##### 1.D.4.3. Délai de verdict

| Paramètre | Valeur | Rôle |
| --- | --- | --- |
| `verdicts.delay_days` | 30 jours | délai d'enquête simulé, largeur de la bande aveugle avant la coupure |
| `verdicts.demo_delay_seconds` | 300 secondes | même délai, à l'échelle d'une démonstration (*B3-EI12*) |

Un seul commutateur (`verdicts.mode`) choisit l'un ou l'autre, lu par le chargement historique comme par le flux : les étiquettes historiques et temps réel doivent porter le même délai.

#### 1.D.5. Application des durées

La purge est un traitement à part entière (`dag_purge`) et suit les règles suivantes

- Hebdomadaire et non quotidienne : une purge à 90 jours n'a aucune urgence journalière, et une tâche destructrice qui tourne rarement est une tâche dont on remarque l'échec. L'heure doit éviter celle de traitement `dag_ingest_verdicts` (qui lit la zone brute que la purge supprime).
- Par lots entiers : un lot à moitié purgé ne correspond plus à aucune empreinte enregistrée. La borne est donc appliquée à la dernière ligne de chaque lot, jamais ligne par ligne.
- Après l'empreinte : chaque écrivain de la zone brute relève l'empreinte du lot qu'il vient d'écrire et la range dans `fd_pipeline_runs.digests`. La purge refuse un lot sans empreinte, et vérifie l'empreinte avant de supprimer : ce qui reste d'un lot purgé est cette empreinte.
-  Quarantaine avant zone brute. La permission de supprimer la copie dérivée repose sur l'empreinte du lot brut.
- Par tranches. Les suppressions procèdent par tranches de 10 000 lignes, validées une à une, avec un marqueur de reprise : un conteneur arrêté au milieu de procédure laisse un état que l'exécution suivante sait expliquer et terminer.
- Avec un garde-fou. Une purge qui supprimerait plus de la moitié d'un magasin (voir paramètre `purge.max_share`) s'arrête avant toute suppression et demande une confirmation explicite ..
- Avec un journal. Chaque exécution inscrit une ligne par magasin dans `fd_purges`, y compris quand elle n'a rien trouvé à supprimer. Le journal s'écrit après la suppression.
- La purge coupe sur une date. La procédure refuse de purger la zone brute d'un lot qui porte des transactions ou des verdicts, puisque sa zone brute est ce qui permet de les rejouer (*B3-EC24*, \[B3-D0\]).

#### 1.D.6. Application de la politique dans le code

| Décision | Emplacement |
| --- | --- |
| Inventaire, exclusions, durées, conservations | `governance.yml` |
| Contrôle des durées au chargement | `fraud/config.py` |
| Pseudonymisation de `cc_num` | `fraud/transform.py` : `client_key()` |
| Minimisation de `lat` / `long` | `fraud/transform.py` : `home_distance_km()` |
| Absence d'identité en sortie | `tests/test_transform.py`, `fraud/notify.py` |
| Rôles, droits, *append-only* | `sql/ddl/060_roles_grants.sql`, `sql/ddl/120_purge_role.sql`, `sql/ddl/140_dashboard_role.sql` |
| Vérification de l'*append-only* | `airflow/dags/dag_load_history.py` : `preflight()` |
| Tout magasin est déclaré | `tests/test_retention.py` |
| Empreinte des lots | `fraud/runs.py`, `sql/checks/batch_digest.sql` |
| Application des durées | `airflow/dags/dag_purge.py`, `fraud/purge.py`, `sql/purge/` |
| Journal des purges | `sql/ddl/130_purges.sql` |
| Oubli d'un lot nommé | `fraud/purge.py` : `forget_plan()`, `forget()` |
| Acceptation | `sql/checks/s5_acceptance.sql`, `tools/check_s5.py` |

La matrice de traçabilité est produite par `tools/build_traceability.py` et présentée dans le document `TRACEABILITY.md`.

#### Références
##### Spécifications
- \[B3-D0\] [*Automatic Fraud Detection Project* Introduction](../../step-0/fraud-project--d0-introduction.pdf)
- \[B3-D1\] [*Data Infrastructure Design*](../fraud-project--d1-data-infrastructure.pdf)
#### Ressources
- \[R3\] [Fraudulent Payments full dataset](https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv)
- \[R4\] [Real-time fraud detection API](https://huggingface.co/spaces/sdacelo/real-time-fraud-detection)

---
