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
  - fraud-project/reference
---

*AUTOMATIC FRAUD DETECTION* PROJECT
===
# 1. Data Infrastructure Design
## Appendices
### 1.A. Appendix A : Design Rationale

> *Nicolas Pichon --- AIA RNCP 38777 / BC03 / D1 / Annexe A : Design Rationale / v12 --- 2026/11/26.*
---

### 1.A.0. Contexte

Ce document annexe présente les principes structurent la conception de l'infrastructure de données du cas d'etude \[D0\].

### 1.A.1. P1 : Le besoin décide de la forme
Le métier demande d'être notifié, mais pas de bloquer de la transaction. La détection n'est donc pas dans le chemin critique du paiement : aucun budget en millisecondes, aucun service résident, aucune haute disponibilité synchrone. Un traitement par petits lots d'une minute suffit.

**Conséquence : absence de scoreur synchrone temps-réel.**

### 1.A.2. Le simulateur de transactions temps-réelles délivre deux flux logiques

L'API \[R4\] livre à la fois la requête de transaction et son étiquette (le verdict fraude/légitime). Dans une application de paiement réelle, le verdict arrive après enquête, longtemps après la date de la transaction proprement dit. 

**Conséquence.** Le pipeline sépare ces deux entités à l'ingestion :

- la *transaction* part vers le scoring, sans étiquette ;
- le *verdict* est postdaté et ne sera visible qu'une fois l'échéance passée.

### 1.A.3. P 3 : Les features sont calculées à l'ingestion

C'est le pivot de la simplification : en calculant et en persistant les features au moment où
la transaction arrive, la correction temporelle est automatique : la ligne porte les valeurs qui
étaient vraies à cet instant.

**Conséquence.** On n'a pas de jointure temporelle à faire, donc pas de magasin de features à gérer. L'entraînement et le scoring lisent les mêmes colonnes de la même table (pas d'écart entre entraînement et service, donc).

### 1.A.4. P4 : La zone brute est le pivot du rejeu
Le processus d'ingestion des transactions (`dag_ingest`) est scindé en deux tâches : `fetch` et `process`. La première écrit la charge brute dans la table `fd_raw_events`,  par micro-lots. La seconde repart de la table des évènements bruts pour processer les transactions.

**Conséquence.** Ce découplage permet de rejouer les ingestions temps-réelles.

### 1.A.5. P5 : La décision de fraude n'a qu'un seul point d'application
La décision de fraude n'est appliquée qu'une seule fois, à l'étape de scoring, et le résultat est persisté dans la colonne `decision` de la table des scores. 

**Conséquence.** Tout les consommateurs de la décision lisent la même décision.

### 1.A.6. P6 : Les politiques sont déclarées hors du code
Les paramètres de gouvernance sont déclarés en configuration et deviennent des nœuds dont les tâches dépendent :

| Paramètre           | Nature         | Utilisation |
| ------------------- | -------------- | ------------- |
| `governance policy` | **conformité** | pseudonymisation, accès, rétention |
| `decision policy`   | **métier**     | arbitrage faux positif / fraude manquée (seuil de score valant fraude) |
| `verdict delay`     | **simulation** | imite le délai d'enquête (n'existe pas en production) |

### 1.A.7. P7 : Le harnais et le système sont bien différenciés
La validation du contenu appartient au système. Le harnais, lui, imite les imperfections du
monde : il injecte des anomalies et diffère les verdicts. Un banc d'essai qui nettoie les données
masque la faiblesse du système.

### 1.A.8. P8 : Tout magasin doit être lu
Tous les magasins ont au moins un lecteur : `fd_quarantine` est examinée au bilan quotidien, `fd_datasets` est relu pour l'idempotence, `fd_pipeline_runs` alimente trois consommateurs, etc.

### 1.A.9. P9 : Les absences sont surveillées autant que les erreurs
Une panne silencieuse est indiscernable d'une absence de fraude. Le dispositif détecte l'absence de données ou d'action : exécution ne produisant aucune ligne, obsolescence, nombre d'exécutions insuffisant. 

Les alertes pour ce types d'anomalie sont envoyées sur un canal de notification distinct de celui de l'analyste (canal de notification de fraude).

### 1.A.10. P10 : L'immuabilité est déclarée et appliquée

L'instruction `UPDATE` est interdite par déclencheur sur les magasins en ajout seul, `DELETE` étant réservé au rôle de *purgeur*.

### 1.A.11. P11 : Chaque technologie est justifiée par une contrainte

*Kafka*, *Debezium*, *Redis*, *Feast*, *dbt* et *Great Expectations* n'ont pas été retenues, faute de
contraintes qui pouvaient les justifier à l''échelle de l'exercice. 

---

#### Références
##### Diagrammes
- `step-0/diagrams/fraud-project--data-infrastructure-4--diagram.md` — complet
- `…-diagram-overview.md`, `…-diagram-1.md` à `…-diagram-5.md`
- `…-diagram-legends.md`
##### Analyses
- `outputs/fraud-project--infra-4--couverture-v09.md`
- `outputs/fraud-project--c4--proposition.md`
- `outputs/fraud-project--couches-et-identifiants.md`
- `outputs/fraud-project--infrastructure-minimale.md`
