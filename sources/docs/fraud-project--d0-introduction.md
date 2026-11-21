---
version: v17
locale: fr
tags:
  - _RNCP38777
  - _2026
  - aia
  - aia/bc03
  - fraud-project
  - fraud-project/step-0
  - fraud-project/introduction
---

*AUTOMATIC FRAUD DETECTION* PROJECT
===

# 0. Introduction

> *Nicolas Pichon --- AIA RNCP 38777 / BC03 / Introduction / v17 --- 2026/11/26.*
---

## 0.1. Contexte

L'objectif de ce document est de présenter l'exercice de réalisation d'un pipeline de données pour l'apprentissage automatique dans le contexte de détection automatique de fraude bancaire spécifié dans \[R2\].

## 0.2. Enoncé

Reprise de l'énoncé de l'exercice présenté dans \[R2\].

### 0.2.1. Contexte
Dans le cadre de la détection des transactions bancaires frauduleuses par des algorithmes prédictifs basés sur l'apprentissage automatique, il s'agit de prédire les paiements frauduleux en temps réel et d'y réagir de manière appropriée.

### 0.2.2. Objectifs de l'exercice
###### B3-G1. Détection de fraude et notification
Le métier doit être notifié dès qu'une fraude est détectée (une simple notification suffit).
###### B3-G2. Vérification quotidienne des paiements et des fraudes
Le métier doit pouvoir vérifier chaque matin tous les paiements et toutes les fraudes survenus la veille

### 0.2.6. Sources de données
Sources de données utilisables (mais non obligatoires) :

- Un jeu de données de paiements frauduleux pour l'entrainement du modèle : 
	- [https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv](https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv) \[R3\].
- Un simulateur de production de transactions en temps réel :
	- [https://huggingface.co/spaces/sdacelo/real-time-fraud-detection](https://huggingface.co/spaces/sdacelo/real-time-fraud-detection) \[R4\].

Cette API permet de récupèrer des transactions de paiement en temps réel (5 appels / minute au plus). Utilisez-la pour produire des prédictions en temps réel.

### 0.2.7. Livrables

#### 0.2.7.1. Synopsis

| #      | Livrable (fr)                            | Deliverable (en)            |
| ------ | ---------------------------------------- | --------------------------- | 
| **B3-D1** | Diagramme de l'infrastructure de données | Data Infrastructure Diagram |
| **B3-D2** | Code source                              | Source Code |
| **B3-D3** | Capture vidéo                            | Video Capture |

#### 0.2.7.2. Descriptions détaillées

### B3-D1. Le schéma de l'infrastructure de données
Un schéma de l'infrastructure construite et sa justification (on peut s'inspirer du diagramme suivant).

<div style="page-break-after: always;"></div>

###### Exemple
![[step-0/diagrams/fraud-project--data-infrastructure-example-1-diagram-1.svg]]

### B3-D2. Le code source
Le code source de tous les éléments nécessaires à la construction de votre infrastructure

### B3-D3. Une capture vidéo
Une capture vidéo de votre infrastructure en fonctionnement sur un exemple. 

---

## 0.3. Compréhension
On identifie et on formule explicitement les exigences induites par les fiches de référence \[R1\] et \[R2\]. 

### 0.3.1. Identification des acteurs
Les cas d'usage B3-G1 et B3-G2 permettent d'identifier les principaux acteurs qui participent à l'infrastructure à réaliser.

| Acteur                   | Rôle                                    | Activités                                         |
| ------------------------ | --------------------------------------- | ------------------------------------------------- |
| *Analyste de fraude*     | Destinataire des alertes de fraude (B3-G1) | Être prévenu assez tôt pour agir sur un cas isolé |
| *Responsable métier*     | Destinataire des rapports (B3-G2)          | Consulter la vue consolidée de la veille          |
| *Système de paiement*    | Source des transactions                 | S/O                                               |
| *Exploitant du pipeline* | Garant du service                       | S'assurer que la chaîne fonctionne                |

### 0.3.2. Identification des exigences 
Les exigences suivantes sont extraites ou déduites de la fiche de projet \[R2\].
#### 0.3.2.1. Exigences explicites

| #        | Exigence                                                                                                       | Source | Objectif | Type | Vér.  |
| -------- | -------------------------------------------------------------------------------------------------------------- | ------ | -------- | ---- | ----- |
| **B3-EE01** | Prédire les paiements frauduleux en *temps réel* (1)                                                           | §1     | B3-G1       | F    | ✅     |
| **B3-EE02** | Notifier le métier dès qu'une fraude est détectée (2)                                                          | §2/B3-G1  | B3-G1       | F    | ✅     |
| **B3-EE03** | Rapporter au métier, chaque matin, l'ensemble des transactions et des fraudes de la veille (3)                 | §2/B3-G2  | B3-G2       | F    | ✅(\*) |
| **B3-EE04** | B3-D1 : présenter un schéma de l'infrastructure réalisée et la justifier                                          | §4     | B3-D1       | L    | ✅     |
| **B3-EE05** | B3-D2 : présenter le code source de tous les éléments nécessaires à la construction de l'infrastructure           | §4     | B3-D2       | L    | ✅     |
| **B3-EE06** | B3-D3 : présenter une capture vidéo de l'infrastructure en fonctionnement sur un exemple                          | §4     | B3-D3       | L    | ✅     |
| **B3-EE07** | Le *preprocessing* doit être réutilisable (4)                                                                  | §5.1   | B3-G1       | CA/A | ✅     |
| **B3-EE08** | Au minimum : entraîner un algorithme, le mettre en production, stocker les données temps réel dans une base    | §5.2   | B3-G1/B3-G2    | CA/A | ✅     |
| **B3-EE09** | Architecture minimale : un élément qui collecte et qui stocke, un élément qui consomme, un processus *ETL/ELT* | §5.2   | ---      | CA/A | ✅     |
> _Légendes : F : fonctionnelle, L : livrable, CA : critère d'acceptation, A : architecturale, Vér. : vérifiable._

<div style="page-break-after: always;"></div>

###### Remarques

- (1) B3-EE01 : dans le contexte, et au vu des capacités de l'API de démonstration \[R4\] (5 appels / minute au plus), il s'agit de "quasi temps réel", c'est-à-dire d'une cadence de consommation comprise entre quelques secondes et quelques minutes.
- (2) B3-EE02 : un canal de notification "simple" est acceptable. Une sortie standard ou une entrée de journal ne sont pas des canaux de notification, à proprement parler. A priori, les canaux de notifications les plus simples sont : e-mail (SMPT) ou Webhook.
- (3) B3-EE03 : implique une production *automatique* des rapports. Implique, par ricochet, que les transactions perdues à la suite d'une requête échouée ne seront jamais rapportées. En contre-partie, on rapporte les évènements d'échec. (\*) On ne peut pas vérifier la justesse des réponses émises par l'API (hors du périmètre de l'exercice). On ne peut que comparer les réponses émises la veille (et conservées dans cet objectif) avec le contenu du rapport matinal.
- (4) B3-EE07 : dans le contexte, le "preprocessing" concerne la transformation des données d'entrée du *service* de scoring (i.e. les données transmises par la requête de transaction) en *features* attendus par le modèle. En effet, le calcul des features doit être réalisés au moins deux fois : d'une part, sur les données historiques, pour l'entrainement du modèle prédictif, d'autre part, sur les données temps-réelles, pour la détection de fraude à la volée.
- (5) B3-EE07, B3-EE08, B3-EE09 sont des *critères d'acceptation*, et, en ce sens, ce sont encore des exigences, mais de type non fonctionnelles.
#### 0.3.2.2. Exigences implicites

| #        | Exigence                                                                                                                                            | Source      | Objectif | Type | Vér. |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | -------- | ---- | ---- |
| **B3-EI01** | B3-G1 et B3-G2 impliquent une source de vérité-terrain pour les décisions de fraude (1)                                                                   | B3-G1/B3-G2 (2) | B3-G1/B3-G2    | A    | ✅    |
| **B3-EI02** | Le verdict de fraude dans la source de vérité-terrain doit être daté de sa date de connaissance, postérieure à celle de la transaction              | B3-G2/B3-EI01   | B3-G2       | F    | ✅    |
| **B3-EI03** | *Persister* les prédictions du modèle                                                                                                               | B3-EE08 (3)    | B3-G2       | A    | ✅    |
| **B3-EI04** | Disposer d'un jeu de données de transactions étiquetée contenant un historique conséquent d'évènements pour l'entrainement du modèle prédictif      | B3-EE08/B3-EI10 | B3-G1       | A    | ✅    |
| **B3-EI05** | Disposer d’une antériorité de transactions suffisante pour que les features d’antériorité soient calculables dès la première transaction temps réel | B3-G1/B3-EE07   | B3-G1       | A    | ✅    |
| **B3-EI06** | Prendre en compte au moins deux cadences de traitement distinctes                                                                                   | B3-G1 (4)      | B3-G1/B3-G2    | A    | ✅    |
| **B3-EI07** | Définir le domaine horaire d'une *journée*                                                                                                          | B3-G2 (5)      | B3-G2       | F    | ✅    |
| **B3-EI08** | Rapporter les transactions perdues entre l'ingestion et le rapport quotidien                                                                        | B3-G2 (6)      | B3-G2       | F    | ✅    |
| **B3-EI09** | La cadence d'interrogation temp-réelle doit se situer entre de 1 et 5 / minutes (7)                                                                 | B3-EE01/R4   | B3-G1       | A    | ✅    |
| **B3-EI10** | Le modèle prédictif doit être un artefact persistant et retrouvable                                                                                 | B3-EE08        | B3-G1       | A    | ✅    |
| **B3-EI11** | L'infrastructure en fonctionnement doit être observable (8)                                                                                         | B3-EE06        | B3-D3       | F    | ✅    |
| **B3-EI12** | Paramétriser les durées supérieures à celle de la démonstration : délai de verdict, durée de conservation, période de réentraînement                | B3-EI11        | B3-D3       | A    | ✅    |
| **B3-EI13** | L'infrastructure doit être reconstructible par un tiers (9)                                                                                         | B3-EE05        | ---      | A    | ✅    |
| **B3-EI14** | Séparer les processus de collecte et de consommation des données                                                                                    | B3-EE09        | B3-G1/B3-G2    | A    | ✅    |
> _Légendes : F : fonctionnelle, A : architecturale, Vér. : vérifiable._

###### Remarques
- (1) B3-EI01 : bien que la fiche de projet ne définisse pas de source de *vérité-terrain* pour les paiements fournis par l'API de démonstration \[R4\], il s'avère que les transactions transmises par l'API sont étiquetées frauduleuse/légitime. On prendre donc comme hypothèse qu'une source de *vérité-terrain* est disponible (quitte à construire un harnais hors système qui consomme effectivement les données retournées par l'API \[R4\] mais qui détache les verdicts de fraude des transactions, et qui les postdate pour simuler le décalage calendaire du verdict,  avant d'injecter séparément dans le système les transactions non étiquetées et les verdicts de fraude associés).
- (2) B3-EI01/Source : B3-G2 : « the payments and frauds that *happened*  ; B3-G1 : entrainement du modèle prédictif
- (3) B3-EI03/Source : extension de l'exigence de persistence B3-EE08 aux scores et aux décisions.
- (4) B3-EI06/Source : B3-G1 implique un processus *continu* de consommation des transactions, tandis que B3-G2 relève d'un processus  d'agrégation *périodique*.
- (5) B3-EI07/Source : B3-G2 : _« during the previous day »_ implique un découpage horaire et une décision de fuseau.
- (6) B3-EI08/Source : B3-G2 implique la collecte de _toutes_ les transactions entrées la veille.
- (7) B3-EI09 : Voir remarque (1). C'est la limite de l'API de démonstration \[R4\] et la contrainte de "quasi temps réel" qui définit l'intervalle de cadence ciblé.
- (8) B3-EI11 : implique de tracer les processus à démontrer de manière visible : reception des notifications, affichage des rapports, journalisation des exécutions.
- (9) B3-EI13 : implique de documenter les configurations, les dépendances et les ordonnancements, dans un document d'installation, complémentaire du schéma d'infrastructure livré en B3-D1.


### 0.3.3. Identification des exigences complémentaires

Les exigences identifiées dans la section §0.3.2 ne couvrent pas complètement les exigences de compétence spécifiées dans \[R1\] (cf. annexe ci-dessous). Les exigences ci-dessous complètent les exigences issues de \[R2\] pour couvrir complètement les compétences B3-C1 à B3-C5.

| #        | Exigence                                                                                                                                                           | Source       | Type | Vér. |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ---- | ---- |
|          | **B3-C1 : Concevoir**                                                                                                                                                 |              |      |      |
| **B3-EC01** | Définir la typologie de chaque source et de chaque magasin : format, schéma, encodage, cardinalité, encodage temporel                                              | B3-C1           | D/A  | ✅    |
| **B3-EC02** | Chiffrer le débit de transactions attendu et fixer un objectif de latence entre l’arrivée d’une transaction et sa notification                                     | B3-C1/B3-EE04    | D/A  | ✅    |
| **B3-EC03** | Chiffrer la volumétrie de stockage par magasin en régime établi (débit × durée de conservation), distinctement du débit                                            | B3-C1           | D/A  | ✅    |
| **B3-EC04** | Énoncer les contraintes et normes opérationnelles retenues comme hypothèses : disponibilité attendue, fenêtre de maintenance, conformité applicable                | B3-C1           | D    | ✅    |
|          | **B3-C2 : Réaliser**                                                                                                                                                  |              |      |      |
| **B3-EC05** | Mettre en œuvre au moins deux magasins de natures ou de technologies distinctes, et au moins un flux de transformation de l'un vers l'autre                        | B3-C2           | A    | ✅    |
| **B3-EC06** | Implémenter les transformations du pipeline en code versionné                                                                                                      | B3-C2           | A    | ✅    |
| **B3-EC07** | Tenir une matrice de traçabilité des exigences → élément d'infrastructure → emplacement du code                                                                    | B3-C2           | D    | ✅    |
|          | **B3-C3 : Automatiser**                                                                                                                                               |              |      |      |
| **B3-EC08** | Déclencher chaque flux par un ordonnanceur, sans intervention manuelle, et déclarer la cadence de chacun                                                           | B3-C3/B3-EI06     | A    | ✅    |
| **B3-EC09** | Exprimer explicitement les dépendances entre tâches et entre flux : ordre d'exécution et conditions de démarrage                                                   | B3-C3           | D    | ✅    |
| **B3-EC10** | Déclarer et implémenter une politique de reprise en fonction de la nature de chaque tâche : nombre d'essais, délai, comportement terminal en cas d'échec définitif | B3-C3/B3-EE03    | F    | ✅    |
| **B3-EC11** | Mesurer la durée de chaque exécution, et justifier au moins une décision d'optimisation par cette mesure                                                           | B3-C3           | A/D  | ✅    |
|          | **B3-C4 : Surveiller**                                                                                                                                                |              |      |      |
| **B3-EC12** | Journaliser chaque exécution dans un magasin interrogeable : début, fin, état, volumes lus / valides / rejetés, durée                                              | B3-C4           | F    | ✅    |
| **B3-EC13** | Alerter en cas d'échec ou d'anomalie du pipeline, sur un canal distinct de la notification de fraude                                                               | B3-C4/B3-EE02     | F    | ✅    |
| **B3-EC14** | Détecter les absences : exécution manquante, exécution à zéro ligne, fraîcheur dépassée                                                                            | B3-C4           | F    | ✅    |
| **B3-EC15** | Surveiller la qualité dans le temps long : taux de rejet, fraîcheur, complétude                                                                                    | B3-C4           | F    | ✅    |
| **B3-EC16** | Formaliser une politique de gouvernance écrite : données personnelles identifiées, pseudonymisation ou minimisation, rôles et droits, durées de conservation       | B3-C4           | D    | ✅    |
| **B3-EC17** | Pseudonymiser ou minimiser les données personnelles dans les magasins exploités                                                                                    | B3-C4/B3-EC16     | F    | ✅    |
| **B3-EC18** | Appliquer les durées de conservation par un traitement effectif, et tracer les suppressions                                                                        | B3-C4/B3-EC16     | F    | ✅    |
| **B3-EC19** | Externaliser les secrets                                                                                                                                           | B3-C4           | A    | ✅    |
| **B3-EC20** | Restreindre les accès aux magasins par rôle                                                                                                                        | B3-C4/B3-EC16     | F    | ✅    |

<div style="page-break-after: always;"></div>

| #        | Exigence                                                                                                                                                           | Source       | Type | Vér. |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ---- | ---- |
|          | **B3-C5 : Contrôler et corriger**                                                                                                                                     |              |      |      |
| **B3-EC21** | Valider chaque enregistrement entrant : schéma, types, valeurs nulles, doublons, valeurs aberrantes                                                                | B3-C5           | F    | ✅    |
| **B3-EC22** | Valider la cohérence *entre champs* d'un même enregistrement                                                                                                       | B3-C5           | F    | ✅    |
| **B3-EC23** | Définir et implémenter le sort d'un enregistrement invalide : rejet journalisé, quarantaine motivée, ou correction documentée                                      | B3-C5           | F    | ✅    |
| **B3-EC24** | Garantir l'idempotence des processus d'ingestion : un rejeu ne doit pas produire de doublon                                                                        | B3-C5/B3-EI08     | F    | ✅    |
| **B3-EC25** | Permettre le rejeu d'une plage de données déjà ingérée depuis les données conservées, sans réinterroger la source                                                  | B3-C5           | F    | ✅    |
| **B3-EC26** | Provoquer une erreur et montrer sa détection et son traitement dans la capture vidéo                                                                               | B3-C5/B3-EE06     | L    | ✅    |
|          | **Autres sources**                                                                                                                                                 |              |      |      |
| **B3-EC27** | Héberger le code sur **GitHub**                                                                                                                                    | R1/B3-D2       | L    | ✅    |
| **B3-EC28** | Démontrer l'infrastructure dans une configuration déployée, cloud ou on-premise                                                                                    | R1/B3-D3/B3-EE06 | DM   | ✅    |

> _Légendes : F : fonctionnelle, L : livrable, A : architecturale, D : documentaire, DM : démonstration, Vér. : vérifiable._

###### Remarques
- B3-EC04 : adapte système aux contraintes et aux normes opérationnelles de l'entreprise.
- B3-EC05 : réalise le transfert et la transformation des données entre différentes bases (complète B3-EE08 / B3-EE09).
- B3-EC06 : exclue les outils de développement graphiques ou _no-code_ pour coder le pipeline (la tolérance au _no-code_ dans \[R2, §5.1] porte l'algorithme de prédiction). 
- B3-EC07 : prouve l'adéquation du système aux spécifications du cahier des charges (\[R1\]+\[R2\]).
- B3-EC10 : le traitement des échecs est contenu dans l’exigence d’automatisation (un pipeline automatisé doit être capable de reprendre son exécution après un échec sans qu’un humain le intervienne).
- B3-EC11 : prouve la clause finale de B3-C3 (optimiser les performances de l'infrastructure).
- B3-EC14 : un pipeline arrêté est indiscernable d'une absence de fraude, et aucun contrôle portant sur les données traitées ne peut capturer cet évènement. 
- B3-EC15 : marque la frontière entre B3-C4 (surveiller dans la durée) et B3-C5 (contrôler et corriger).
- B3-EC18/B3-EC25 : la durée de conservation est aussi la fenêtre de rejeu (le rejeu a besoin des données brutes que la rétention supprime).
- B3-EC19 : pas d'identifiant ou de clé en clair dans le code versionné.
- B3-EC28 : précise B3-EE06 : \[R1\] dit « en production », ce qui exclut la démonstration depuis un carnet interactif (*notebook*) tout en acceptant l'_on-premise_. 

---

## 0.4. Périmètre

On explicite les fonctionnalités à construire, les contraintes à vérifier et la documentation à produire, et on précise les limites des périmètres fonctionnel et architectural de l'infrastructure à réaliser.

### 0.4.1. Identification des fonctionnalités à construire

Fonctionnalités à construire. D'après §0.3.

| #         | Fonctionnalité                                                                                                                              | C/&nbsp;R1\|R2 | C/ B3-D0      |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ---------- |
|           | **Ingestion**                                                                                                                               |                |            |
| **B3-F02-1** | Interroger le simulateur \[R4\] en quasi-temps réel et récupérer les nouvelles transactions                                                 | B3-G1             | B3-EE01/B3-EI09 |
| **B3-F02-2** | Charger l'historique des transactions \[R3\]                                                                                                |                | B3-EI04/B3-EI05 |
| **B3-F02-3** | Dissocier la transaction de son verdict (et anti-dater ce dernier)                                                                          |                | B3-EI01/B3-EI02 |

<div style="page-break-after: always;"></div>

| #         | Fonctionnalité                                                                                                                              | C/&nbsp;R1\|R2 | C/ B3-D0      |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ---------- |
|           | **Stockage**                                                                                                                                |                |            |
| **B3-F03-1** | Conserver les données brutes, sans changement (en *append-only*)                                                                            | B3-C2/B3-C5         | B3-EC24       |
| **B3-F03-2** | Stocker les transactions *typées*, leurs features et leur prédiction                                                                        | B3-C2             | B3-EE08/B3-EI03 |
| **B3-F03-3** | Répartir les données sur plusieurs bases ou emplacements distincts                                                                          | B3-C2             | B3-EC05       |
|           | **Transformation**                                                                                                                          |                |            |
| **B3-F04-1** | Calculer les features à l'ingestion et les persister sur la transaction, de sorte que l'entraînement et le scoring lisent les mêmes sources |                | B3-EE07/B3-EI05 |
| **B3-F04-2** | Garantir que le calcul des features par ligne et leur rétro-calcul par lot produisent les mêmes valeurs                                     | B3-C5             | B3-EE07       |
|           | **Modèle**                                                                                                                                  |                |            |
| **B3-F05-1** | Entraîner un modèle de scoring sur des verdicts connus à la date de *coupure*                                                               |                | B3-EI02//B3-EI04 |
| **B3-F05-2** | Enregistrer le modèle, sa version et ses métriques, et le mettre à disposition du pipeline                                              |                | B3-EE08/B3-EI10 |
|           | **B3-G1**                                                                                                                                      |                |            |
| **B3-F06-1** | Scorer chaque nouvelle transaction et appliquer le seuil de décision une seule fois                                                     | B3-G1             | B3-EE01       |
| **B3-F06-2** | Notifier l'analyste de fraude sur les transactions prédites frauduleuses                                                                    | B3-G1             | B3-EE02       |
|           | **B3-G2**                                                                                                                                      |                |            |
| **B3-F07-1** | Produire chaque matin le bilan des paiements et des fraudes de la veille, sur fenêtre calendaire                                            | B3-G2             | B3-EE03/B3-EI07 |
| **B3-F07-2** | Confronter les scores aux verdicts échus pour mesurer le rappelet la précision réellement observés, par version de modèle              | B3-C4             | B3-EI02/B3-EI03 |
| **B3-F07-3** | Restituer la répartition des rejets par motif                                                                                               | B3-C4/B3-C5         | B3-EC15/B3-EC22 |
| **B3-F07-4** | Comparer les volumes de transactions entrées avec les volumes de transaction rapportées et rapporter l’écart                                |                | B3-EI08       |
|           | **Automatisation**                                                                                                                          |                |            |
| **B3-F08-1** | Orchestrer les traitements à des cadences distinctes,sans intervention manuelle                                                        | B3-C3             | B3-EI06, B3-EC08 |
| **B3-F08-2** | Exprimer les dépendances entre traitementspar des conditions de garde sur l'historique d'exécution                                     | B3-C3             | B3-EC09       |
| **B3-F08-3** | Appliquer une politique de reprise : essais, délai, comportement terminal                                                                   |                | B3-EC10       |
|           | **Qualité**                                                                                                                                 |                |            |
| **B3-F09-1** | Valider les données entrantes :schéma, types, valeurs nulles, doublons, valeurs aberrantes                                             | B3-C5             | B3-EC20       |
| **B3-F09-2** | Valider la cohérence **entre** colonnes,et non seulement chaque colonne isolément                                                      | B3-C5             | B3-EC21       |
| **B3-F09-3** | Mettre en quarantaine les enregistrements rejetés, avec leur motif                                                                          | B3-C5             | B3-EC22       |
| **B3-F09-4** | Rejouer le traitement depuis la zone brute (par lot, sans produire de doublon)                                                              | B3-C5             | B3-EC23/B3-EC24 |
|           | **Monitoring**                                                                                                                          |                |            |
| **B3-F10-1** | Journaliser les exécutions : volumes lus, valides, rejetés, état, durée, santé du transport                                                 | B3-C4             | B3-EC12       |
| **B3-F10-2** | Détecter les absences : exécution vide, fraîcheur dépassée, exécutions manquantes                                                           | B3-C4             | B3-EC14       |
| **B3-F10-3** | Alerter l'exploitant sur un canal spécifique (distinct de celui de l'analyste de fraude)                                                    | B3-C4             | B3-EC13       |
| **B3-F10-4** | Exposer l’état courant de l’infrastructure en marche                                                                                        |                | B3-EI11       |
|           | **Gouvernance**                                                                                                                             |                |            |
| **B3-F11-1** | Pseudonymiser l'identifiant porteur (sans recopier les données d'identité dans la couche exploitée) (a)                                     | B3-C4             | B3-EC17       |
|           | **Sécurité**                                                                                                                                |                |            |
| **B3-F12-1** | Gérer les secrets                                                                                                                           | B3-C4             | B3-EC19       |
| **B3-F12-2** | Gérer les accès par rôle                                                                                                                    | B3-C4             | B3-EC19       |
| **B3-F12-3** | Purger les données brutes au-delà de la durée de conservation et tracer la purge                                                            | B3-C4             | B3-EC18       |
|           | **Démontrabilité**                                                                                                                          |                |            |
| **B3-F13-1** | Paramétriser les durées qui dépassent celle de la démonstration (délai de verdict, rétention)                                               |                | B3-EE06/B3-EI12 |
> _Légende : C/ R1|R2 : couvre un élément de R1 ou de R2, C/ B3-D0 : couvre une exigence B3-D0 (EE, EI, EC)_

<div style="page-break-after: always;"></div>

###### Remarques
- (a) On suppose qu'une requête de transaction contient nécessairement les informations suivantes : nom, prénom, rue, date de naissance, profession, coordonnées du domicile, numéro de carte bancaire (tokenisé ou non).

### 0.4.2. Contraintes à vérifier

Propriétés d'assemblage à vérifier. D'après §0.3.

| #   | Vérification                                                                                                                       | Constatée sur                | Couvre |
| --- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ------ |
| B3-K01 | Les trois éléments de l'architecture minimale (collecte/stockage, consommation, processus *ETL/ELT*) sont identifiables et nommés | Schéma B3-D1                    | B3-EE09   |
| B3-K02 | Les processus de collecte et de consommation sont distincts                                                                        | Schéma B3-D1                    | B3-EI14   |
| B3-K03 | Les transformations du pipeline sont définies par du code versionné (*SQL*, *Python*, ...)                                             | Dépôt de code                | B3-EC06   |
| B3-K04 | Un tiers reconstruit l'infrastructure depuis B3-D2 et le document d'installation                                                      | Reconstruction effective | B3-EI13   |
| B3-K05 | La démonstration démontre une configuration déployée                                                                               | Capture vidéo B3-D3             | B3-EC27   |

### 0.4.3. Documents à produire

Artefacts documentaires à produire.  D'après §0.3.

| #   | Artefact         | Contenu                                                                            | Couvre |
| --- | ---------------- | ---------------------------------------------------------------------------------- | ------ |
| B3-H01 | B3-D1               | Le schéma de l'infrastructure et sa justification                                  | B3-EE04   |
| B3-H02 | B3-D1               | Typologie de chaque source et de chaque magasin                                    | B3-EC01   |
| B3-H03 | B3-D1               | Débit attendu et objectif de latence                                               | B3-EC02   |
| B3-H04 | B3-D1               | Volumétrie de stockage par magasin                                                 | B3-EC03   |
| B3-H05 | B3-D1               | Contraintes et normes opérationnelles retenues en hypothèse                        | B3-EC04   |
| B3-H06 | B3-D1               | Décision d'optimisation argumentée par les durées mesurées _(alimentée par B3-F10-1)_ | B3-EC11   |
| B3-H07 | B3-D1               | Dépendances entre tâches et flux, exposées _(réalisées par B3-F08-2)_                 | B3-EC09   |
| B3-H08 | B3-D1               | Matrice de traçabilité exigence → infrastructure → code                            | B3-EC07   |
| B3-H09 | B3-D1/Annexe | Gouvernance : données personnelles, pseudonymisation, rôles, conservation                 | B3-EC16   |
| B3-H10 | B3-D2               | Le code source de tous les éléments nécessaires                                    | B3-EE05   |
| B3-H11 | B3-D2               | Hébergement sur GitHub                                                             | B3-EC26   |
| B3-H12 | B3-D3               | La capture vidéo de l'infrastructure en fonctionnement                             | B3-EE06   |
| B3-H13 | B3-D3               | Erreur provoquée en B3-D3, sa détection et son traitement                             | B3-EC25   |

### 0.4.4. Eléments d'architecture écartés

D'après \[R2\].

- Un déploiement *cloud* :
	- Raison : le déploiement *on-premise* est accepté                                                                    
- Un service de scoring *synchrone* avec blocage des paiements frauduleux :
	- Raison : Le métier demande simplement une notification. On n'a aucune exigence sur le chemin critique du paiement : service résident, pas de haute disponibilité synchrone, budget de latence temps-réelle.  
- Un bus d'évènement asynchrone (ex: *Kafka*+*Debezium*)
	- Raison : 1 producteur, 1 consommateur, 7200 messages/jour : le projet n'est pas dimensionné pour un découplage OLTP/OLAP.
- Un orchestrateur des magasins de features (ex: *Feast*)
	- Le magasin de features *online* est justifié par l'existence d'un scoring synchrone à haute disponibilité. En contre-partie, B3-F04-1 garantie la cohérence des features d'entrainement et de features de scoring temps-réel.
- Des outils de transformation et de validation spécifiques (ex: *dbt*, *Great Expectations*) 
	- Raison : du code SQL et une fonction de validation explicite couvrent B3-C2 et B3-C5 correctement à l'échelle de l'exercice et de la démonstration.
- Des entrepôts distribués (ex: *Spark*, *BigQuery*) : 
	- Raison : le volume de transactions de 4 Go / an est trop faible pour justifier un environnement distribué à court terme.                                                                                   
### 0.4.5. Autres limites

- *Performances du modèle prédictif* : basique, conformément aux recommandations de la fiche de projet \[R2\] (qui précise plusieurs fois que la performance du modèle prédictif est secondaire par rapport à la réalisation des pipelines).
- Le *verdict postdaté* est simulé par le harnais (car on n'a pas d'enquête réelle pour alimenter la vérité-terrain).
- *Disponibilité des données* : pas de stratégie de réplication ni de reprise après sinistre.
- *Authentification* : pas d'authentification des consommateurs pour accéder aux rapports quotidiens et aux notifications.

---

## Annexe : Compétences à démontrer

Compétences à démontrer dans le réalisation de l'exercice. D'après \[R1\].

| **#**  | Compétence                                                                                                                                                                                                                                          |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **B3-C1** | **Concevoir** un système de gestion de données temps réel adapté aux contraintes et normes opérationnelles de l'entreprise, pour gérer efficacement la vélocité, le volume des flux, et la typologie des données.                                   |
| **B3-C2** | **Etablir** un pipeline de données à travers des processus ETL/ELT pour le transfert et la transformation des données entre différentes bases, en utilisant des outils de programmation, afin de répondre aux spécifications du cahier des charges. |
| **B3-C3** | **Automatiser** les flux de données dans le pipeline, en utilisant des outils spécifiques ou de la programmation, afin d'optimiser les performances de l'infrastructure de données.                                                                 |
| **B3-C4** | **Surveiller** les flux de données pour assurer la qualité et le respect de la politique de gouvernance, en vue de maintenir les normes, la sécurité et la confidentialité dans les pipelines de données.                                           |
| **B3-C5** | **Développer** des procédures de contrôle qualité et de correction des erreurs dans les pipelines de données, afin de garantir la qualité des données.                                                                                              |

---

## Références
- \[R1\] [Jedha Certification - AIA/BC03](https://app.jedha.co/certifications/rncp38777bc03)
- \[R2\] [Automatic Fraud Detection Project](https://app.jedha.co/course/etl-with-airflow-lds/automatic-fraud-detection-project-lds)
- \[R3\] [Fraudulent Payments full dataset](https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv)
- \[R4\] [Real-time payment API](https://huggingface.co/spaces/sdacelo/real-time-fraud-detection)

---
