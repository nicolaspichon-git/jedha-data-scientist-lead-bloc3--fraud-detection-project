---
version: v13
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

> *Nicolas Pichon --- AIA RNCP 38777 / BC03 / D1 / Annexe A : Design Rationale / v13 --- 2026/11/26.*
---

### 1.A.0. Contexte

Ce document annexe présente les principes qui structurent la conception de l'infrastructure de données du cas d'étude \[D0\].

### 1.A.1. P1 : Le besoin décide de la forme

Le métier demande à être notifié, mais pas de bloquer la transaction. La détection n'est donc pas dans le chemin critique du paiement : aucun budget en millisecondes, aucun service résident, aucune haute disponibilité synchrone. Un traitement par petits lots d'une minute suffit.

**Conséquence.** Un traitement du flux continu par petits lots d'une minute est suffisant (pas besoin de service de scoring synchrone en temps réel).

### 1.A.2. P2 : Le simulateur délivre deux flux logiques

L'API \[R4\] livre à la fois la transaction et son étiquette (le verdict fraude/légitime). Dans une application de paiement réelle, le verdict arrive après enquête, longtemps après la transaction.

**Conséquence.** Le pipeline sépare ces deux entités à l'ingestion :

- la *transaction* part vers le scoring, sans étiquette ;
- le *verdict* est postdaté et ne sera visible qu'une fois l'échéance passée.

L'ingestion des verdicts différés a un temps caractéristique propre, strictement compris entre le quasi-temps réel de l'ingestion des transactions et la périodicité journalière des rapports quotidiens.

### 1.A.3. P3 : Les features sont calculées à l'ingestion

C'est le pivot de la simplification : en calculant et en persistant les features au moment où la transaction arrive, la correction temporelle est automatique.

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
| `governance policy` | **conformité** | pseudonymisation, accès, rétention, purge |
| `decision policy`   | **métier**     | arbitrage faux positif / fraude manquée (seuil de score valant fraude) |
| `verdict delay`     | **simulation** | imite le délai d'enquête (n'existe pas en production) |

### 1.A.7. P7 : Le harnais et le système sont bien différenciés
La validation du contenu appartient au système. Le harnais, lui, imite les imperfections du monde : il injecte des anomalies et diffère les verdicts. Un banc d'essai qui nettoie les données masque la faiblesse du système.

### 1.A.8. P8 : Tout magasin doit être lu

Tous les magasins ont au moins un lecteur.

### 1.A.9. P9 : Les absences sont surveillées autant que les erreurs

Une panne silencieuse est indiscernable d'une absence de fraude. Le dispositif détecte l'absence de données ou d'action : exécution ne produisant aucune ligne, obsolescence, nombre d'exécutions insuffisant. 

Les contrôles d'absence portent sur la chaîne plutôt que sur les transactions :

- *exécutions vides* : plus de 10 % des exécutions de l'heure n'ont rien stocké ;
- *fraîcheur* : plus de dix minutes sans exécution réussie ;
- *taux de rejet* : plus de 5 % des lignes lues envoyées en quarantaine ;
- *invariant de volume* : chaque ligne lue est soit une transaction, soit une ligne en quarantaine.

Les alertes pour ce types d'anomalie sont envoyées sur un canal de notification distinct de celui de l'analyste (canal de notification de fraude).

### 1.A.10. P10 : L'immuabilité est déclarée et appliquée

L'immuabilité d'une table repose sur des révocations de droits : `UPDATE`, `DELETE` et `TRUNCATE` sont révoqués sur la zone brute et sur les scores. 

L'instruction `DELETE` est réservé au rôle de *purgeur*. Celui-ci n'a aucun droit sur la couche exploitée.

**Conséquence.** La garantie d'immuabilité se vérifie à l'exécution.

### 1.A.11. P11 : Chaque technologie est justifiée par une contrainte

*Kafka*, *Debezium*, *Redis*, *Feast*, *dbt* et *Great Expectations* n'ont pas été retenues, faute de contraintes qui pouvaient les justifier à l'échelle de l'exercice. 

### 1.A.12. P12 : Chaque règle n'a qu'une définition et une seule

Une règle n'est implémentée qu'une seule fois : configuration yaml, composant Python, fonction ou script SQL.

---

#### Références
##### Spécifications
- \[D0\] [*Automatic Fraud Detection Project* Introduction](fraud-project--d0-introduction.pdf)
##### Livrables
- \[D1\] [Data Infrastructure Design](fraud-project--d1-data-infrastructure.pdf)
##### Annexes
- \[D1-B\] [Data Governance Policy](fraud-project--d1-annexe-b--gouvernance.pdf)
#### Ressources
- \[R4\] [Real-time fraud detection API](https://huggingface.co/spaces/sdacelo/real-time-fraud-detection)

---
