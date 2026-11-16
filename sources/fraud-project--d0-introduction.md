---
version: v16
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

> *Nicolas Pichon --- AIA RNCP 38777 / BC03 / Introduction / v16 --- 2026/11/26.*
---

## 0.1. Contexte

L'objectif de ce document est de présenter l'exercice de réalisation d'un pipeline de données pour l'apprentissage automatique dans le contexte de détection automatique de fraude bancaire spécifié dans \[R2\].

## 0.2. Enoncé

Reprise de l'énoncé de l'exercice présenté dans \[R2\].

### 0.2.1. Contexte
Dans le cadre de la détection des transactions bancaires frauduleuses par des algorithmes prédictifs basés sur l'apprentissage automatique, il s'agit de prédire les paiements frauduleux en temps réel et d'y réagir de manière appropriée.

### 0.2.2. Objectifs de l'exercice
###### G1. Détection de fraude et notification
Le métier doit être notifié dès qu'une fraude est détectée (une simple notification suffit).
###### G2. Vérification quotidienne des paiements et des fraudes
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
| **D1** | Diagramme de l'infrastructure de données | Data Infrastructure Diagram |
| **D2** | Code source                              | Source Code |
| **D3** | Capture vidéo                            | Video Capture |

#### 0.2.7.2. Descriptions détaillées

### D1. Le schéma de l'infrastructure de données
Un schéma de l'infrastructure construite et sa justification (on peut s'inspirer du diagramme suivant).

<div style="page-break-after: always;"></div>

###### Exemple
![[step-0/diagrams/fraud-project--data-infrastructure-example-1-diagram-1.svg]]

### D2. Le code source
Le code source de tous les éléments nécessaires à la construction de votre infrastructure

### D3. Une capture vidéo
Une capture vidéo de votre infrastructure en fonctionnement sur un exemple. 

---

## 0.3. Compréhension
On identifie et on formule explicitement les exigences induites par les fiches de référence \[R1\] et \[R2\]. 

### 0.3.1. Identification des acteurs
Les cas d'usage G1 et G2 permettent d'identifier les principaux acteurs qui participent à l'infrastructure à réaliser.

| Acteur                   | Rôle                                    | Activités                                         |
| ------------------------ | --------------------------------------- | ------------------------------------------------- |
| *Analyste de fraude*     | Destinataire des alertes de fraude (G1) | Être prévenu assez tôt pour agir sur un cas isolé |
| *Responsable métier*     | Destinataire des rapports (G2)          | Consulter la vue consolidée de la veille          |
| *Système de paiement*    | Source des transactions                 | S/O                                               |
| *Exploitant du pipeline* | Garant du service                       | S'assurer que la chaîne fonctionne                |

### 0.3.2. Identification des exigences 
Les exigences suivantes sont extraites ou déduites de la fiche de projet \[R2\].
#### 0.3.2.1. Exigences explicites

| #        | Exigence                                                                                                       | Source | Objectif | Type | Vér.  |
| -------- | -------------------------------------------------------------------------------------------------------------- | ------ | -------- | ---- | ----- |
| **EE01** | Prédire les paiements frauduleux en *temps réel* (1)                                                           | §1     | G1       | F    | ✅     |
| **EE02** | Notifier le métier dès qu'une fraude est détectée (2)                                                          | §2/G1  | G1       | F    | ✅     |
| **EE03** | Rapporter au métier, chaque matin, l'ensemble des transactions et des fraudes de la veille (3)                 | §2/G2  | G2       | F    | ✅(\*) |
| **EE04** | D1 : présenter un schéma de l'infrastructure réalisée et la justifier                                          | §4     | D1       | L    | ✅     |
| **EE05** | D2 : présenter le code source de tous les éléments nécessaires à la construction de l'infrastructure           | §4     | D2       | L    | ✅     |
| **EE06** | D3 : présenter une capture vidéo de l'infrastructure en fonctionnement sur un exemple                          | §4     | D3       | L    | ✅     |
| **EE07** | Le *preprocessing* doit être réutilisable (4)                                                                  | §5.1   | G1       | CA/A | ✅     |
| **EE08** | Au minimum : entraîner un algorithme, le mettre en production, stocker les données temps réel dans une base    | §5.2   | G1/G2    | CA/A | ✅     |
| **EE09** | Architecture minimale : un élément qui collecte et qui stocke, un élément qui consomme, un processus *ETL/ELT* | §5.2   | ---      | CA/A | ✅     |
> _Légendes : F : fonctionnelle, L : livrable, CA : critère d'acceptation, A : architecturale, Vér. : vérifiable._

<div style="page-break-after: always;"></div>

###### Remarques

- (1) EE01 : dans le contexte, et au vu des capacités de l'API de démonstration \[R4\] (5 appels / minute au plus), il s'agit de "quasi temps réel", c'est-à-dire d'une cadence de consommation comprise entre quelques secondes et quelques minutes.
- (2) EE02 : un canal de notification "simple" est acceptable. Une sortie standard ou une entrée de journal ne sont pas des canaux de notification, à proprement parler. A priori, les canaux de notifications les plus simples sont : e-mail (SMPT) ou Webhook.
- (3) EE03 : implique une production *automatique* des rapports. Implique, par ricochet, que les transactions perdues à la suite d'une requête échouée ne seront jamais rapportées. En contre-partie, on rapporte les évènements d'échec. (\*) On ne peut pas vérifier la justesse des réponses émises par l'API (hors du périmètre de l'exercice). On ne peut que comparer les réponses émises la veille (et conservées dans cet objectif) avec le contenu du rapport matinal.
- (4) EE07 : dans le contexte, le "preprocessing" concerne la transformation des données d'entrée du *service* de scoring (i.e. les données transmises par la requête de transaction) en *features* attendus par le modèle. En effet, le calcul des features doit être réalisés au moins deux fois : d'une part, sur les données historiques, pour l'entrainement du modèle prédictif, d'autre part, sur les données temps-réelles, pour la détection de fraude à la volée.
- (5) EE07, EE08, EE09 sont des *critères d'acceptation*, et, en ce sens, ce sont encore des exigences, mais de type non fonctionnelles.
#### 0.3.2.2. Exigences implicites

| #        | Exigence                                                                                                                                            | Source      | Objectif | Type | Vér. |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | -------- | ---- | ---- |
| **EI01** | G1 et G2 impliquent une source de vérité-terrain pour les décisions de fraude (1)                                                                   | G1/G2 (2) | G1/G2    | A    | ✅    |
| **EI02** | Le verdict de fraude dans la source de vérité-terrain doit être daté de sa date de connaissance, postérieure à celle de la transaction              | G2/EI01   | G2       | F    | ✅    |
| **EI03** | *Persister* les prédictions du modèle                                                                                                               | EE08 (3)    | G2       | A    | ✅    |
| **EI04** | Disposer d'un jeu de données de transactions étiquetée contenant un historique conséquent d'évènements pour l'entrainement du modèle prédictif      | EE08/EI10 | G1       | A    | ✅    |
| **EI05** | Disposer d’une antériorité de transactions suffisante pour que les features d’antériorité soient calculables dès la première transaction temps réel | G1/EE07   | G1       | A    | ✅    |
| **EI06** | Prendre en compte au moins deux cadences de traitement distinctes                                                                                   | G1 (4)      | G1/G2    | A    | ✅    |
| **EI07** | Définir le domaine horaire d'une *journée*                                                                                                          | G2 (5)      | G2       | F    | ✅    |
| **EI08** | Rapporter les transactions perdues entre l'ingestion et le rapport quotidien                                                                        | G2 (6)      | G2       | F    | ✅    |
| **EI09** | La cadence d'interrogation temp-réelle doit se situer entre de 1 et 5 / minutes (7)                                                                 | EE01/R4   | G1       | A    | ✅    |
| **EI10** | Le modèle prédictif doit être un artefact persistant et retrouvable                                                                                 | EE08        | G1       | A    | ✅    |
| **EI11** | L'infrastructure en fonctionnement doit être observable (8)                                                                                         | EE06        | D3       | F    | ✅    |
| **EI12** | Paramétriser les durées supérieures à celle de la démonstration : délai de verdict, durée de conservation, période de réentraînement                | EI11        | D3       | A    | ✅    |
| **EI13** | L'infrastructure doit être reconstructible par un tiers (9)                                                                                         | EE05        | ---      | A    | ✅    |
| **EI14** | Séparer les processus de collecte et de consommation des données                                                                                    | EE09        | G1/G2    | A    | ✅    |
> _Légendes : F : fonctionnelle, A : architecturale, Vér. : vérifiable._

###### Remarques
- (1) EI01 : bien que la fiche de projet ne définisse pas de source de *vérité-terrain* pour les paiements fournis par l'API de démonstration \[R4\], il s'avère que les transactions transmises par l'API sont étiquetées frauduleuse/légitime. On prendre donc comme hypothèse qu'une source de *vérité-terrain* est disponible (quitte à construire un harnais hors système qui consomme effectivement les données retournées par l'API \[R4\] mais qui détache les verdicts de fraude des transactions, et qui les postdate pour simuler le décalage calendaire du verdict,  avant d'injecter séparément dans le système les transactions non étiquetées et les verdicts de fraude associés).
- (2) EI01/Source : G2 : « the payments and frauds that *happened*  ; G1 : entrainement du modèle prédictif
- (3) EI03/Source : extension de l'exigence de persistence EE08 aux scores et aux décisions.
- (4) EI06/Source : G1 implique un processus *continu* de consommation des transactions, tandis que G2 relève d'un processus  d'agrégation *périodique*.
- (5) EI07/Source : G2 : _« during the previous day »_ implique un découpage horaire et une décision de fuseau.
- (6) EI08/Source : G2 implique la collecte de _toutes_ les transactions entrées la veille.
- (7) EI09 : Voir remarque (1). C'est la limite de l'API de démonstration \[R4\] et la contrainte de "quasi temps réel" qui définit l'intervalle de cadence ciblé.
- (8) EI11 : implique de tracer les processus à démontrer de manière visible : reception des notifications, affichage des rapports, journalisation des exécutions.
- (9) EI13 : implique de documenter les configurations, les dépendances et les ordonnancements, dans un document d'installation, complémentaire du schéma d'infrastructure livré en D1.


### 0.3.3. Identification des exigences complémentaires

Les exigences identifiées dans la section §0.3.2 ne couvrent pas complètement les exigences de compétence spécifiées dans \[R1\] (cf. annexe ci-dessous). Les exigences ci-dessous complètent les exigences issues de \[R2\] pour couvrir complètement les compétences C1 à C5.

| #        | Exigence                                                                                                                                                           | Source       | Type | Vér. |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ---- | ---- |
|          | **C1 : Concevoir**                                                                                                                                                 |              |      |      |
| **EC01** | Définir la typologie de chaque source et de chaque magasin : format, schéma, encodage, cardinalité, encodage temporel                                              | C1           | D/A  | ✅    |
| **EC02** | Chiffrer le débit de transactions attendu et fixer un objectif de latence entre l’arrivée d’une transaction et sa notification                                     | C1/EE04    | D/A  | ✅    |
| **EC03** | Chiffrer la volumétrie de stockage par magasin en régime établi (débit × durée de conservation), distinctement du débit                                            | C1           | D/A  | ✅    |
| **EC04** | Énoncer les contraintes et normes opérationnelles retenues comme hypothèses : disponibilité attendue, fenêtre de maintenance, conformité applicable                | C1           | D    | ✅    |
|          | **C2 : Réaliser**                                                                                                                                                  |              |      |      |
| **EC05** | Mettre en œuvre au moins deux magasins de natures ou de technologies distinctes, et au moins un flux de transformation de l'un vers l'autre                        | C2           | A    | ✅    |
| **EC06** | Implémenter les transformations du pipeline en code versionné                                                                                                      | C2           | A    | ✅    |
| **EC07** | Tenir une matrice de traçabilité des exigences → élément d'infrastructure → emplacement du code                                                                    | C2           | D    | ✅    |
|          | **C3 : Automatiser**                                                                                                                                               |              |      |      |
| **EC08** | Déclencher chaque flux par un ordonnanceur, sans intervention manuelle, et déclarer la cadence de chacun                                                           | C3/EI06     | A    | ✅    |
| **EC09** | Exprimer explicitement les dépendances entre tâches et entre flux : ordre d'exécution et conditions de démarrage                                                   | C3           | D    | ✅    |
| **EC10** | Déclarer et implémenter une politique de reprise en fonction de la nature de chaque tâche : nombre d'essais, délai, comportement terminal en cas d'échec définitif | C3/EE03    | F    | ✅    |
| **EC11** | Mesurer la durée de chaque exécution, et justifier au moins une décision d'optimisation par cette mesure                                                           | C3           | A/D  | ✅    |
|          | **C4 : Surveiller**                                                                                                                                                |              |      |      |
| **EC12** | Journaliser chaque exécution dans un magasin interrogeable : début, fin, état, volumes lus / valides / rejetés, durée                                              | C4           | F    | ✅    |
| **EC13** | Alerter en cas d'échec ou d'anomalie du pipeline, sur un canal distinct de la notification de fraude                                                               | C4/EE02     | F    | ✅    |
| **EC14** | Détecter les absences : exécution manquante, exécution à zéro ligne, fraîcheur dépassée                                                                            | C4           | F    | ✅    |
| **EC15** | Surveiller la qualité dans le temps long : taux de rejet, fraîcheur, complétude                                                                                    | C4           | F    | ✅    |
| **EC16** | Formaliser une politique de gouvernance écrite : données personnelles identifiées, pseudonymisation ou minimisation, rôles et droits, durées de conservation       | C4           | D    | ✅    |
| **EC17** | Pseudonymiser ou minimiser les données personnelles dans les magasins exploités                                                                                    | C4/EC16     | F    | ✅    |
| **EC18** | Appliquer les durées de conservation par un traitement effectif, et tracer les suppressions                                                                        | C4/EC16     | F    | ✅    |
| **EC19** | Externaliser les secrets                                                                                                                                           | C4           | A    | ✅    |
| **EC20** | Restreindre les accès aux magasins par rôle                                                                                                                        | C4/EC16     | F    | ✅    |

<div style="page-break-after: always;"></div>

| #        | Exigence                                                                                                                                                           | Source       | Type | Vér. |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ---- | ---- |
|          | **C5 : Contrôler et corriger**                                                                                                                                     |              |      |      |
| **EC21** | Valider chaque enregistrement entrant : schéma, types, valeurs nulles, doublons, valeurs aberrantes                                                                | C5           | F    | ✅    |
| **EC22** | Valider la cohérence *entre champs* d'un même enregistrement                                                                                                       | C5           | F    | ✅    |
| **EC23** | Définir et implémenter le sort d'un enregistrement invalide : rejet journalisé, quarantaine motivée, ou correction documentée                                      | C5           | F    | ✅    |
| **EC24** | Garantir l'idempotence des processus d'ingestion : un rejeu ne doit pas produire de doublon                                                                        | C5/EI08     | F    | ✅    |
| **EC25** | Permettre le rejeu d'une plage de données déjà ingérée depuis les données conservées, sans réinterroger la source                                                  | C5           | F    | ✅    |
| **EC26** | Provoquer une erreur et montrer sa détection et son traitement dans la capture vidéo                                                                               | C5/EE06     | L    | ✅    |
|          | **Autres sources**                                                                                                                                                 |              |      |      |
| **EC27** | Héberger le code sur **GitHub**                                                                                                                                    | R1/D2       | L    | ✅    |
| **EC28** | Démontrer l'infrastructure dans une configuration déployée, cloud ou on-premise                                                                                    | R1/D3/EE06 | DM   | ✅    |
| ~~**EC29*~~* | ~~Structurer le dossier de sorte que les compétences C1 à C5 soient localisables par une référence explicite~~ | ~~R1, D2~~       | ~~D~~    | ✅    |
> _Légendes : F : fonctionnelle, L : livrable, A : architecturale, D : documentaire, DM : démonstration, Vér. : vérifiable._

###### Remarques
- EC04 : adapte système aux contraintes et aux normes opérationnelles de l'entreprise.
- EC05 : réalise le transfert et la transformation des données entre différentes bases (complète EE08 / EE09).
- EC06 : exclue les outils de développement graphiques ou _no-code_ pour coder le pipeline (la tolérance au _no-code_ dans \[R2, §5.1] porte l'algorithme de prédiction). 
- EC07 : prouve l'adéquation du système aux spécifications du cahier des charges (\[R1\]+\[R2\]).
- EC10 : le traitement des échecs est contenu dans l’exigence d’automatisation (un pipeline automatisé doit être capable de reprendre son exécution après un échec sans qu’un humain le intervienne).
- EC11 : prouve la clause finale de C3 (optimiser les performances de l'infrastructure).
- EC14 : un pipeline arrêté est indiscernable d'une absence de fraude, et aucun contrôle portant sur les données traitées ne peut capturer cet évènement. 
- EC15 : marque la frontière entre C4 (surveiller dans la durée) et C5 (contrôler et corriger).
- EC18/EC25 : la durée de conservation est aussi la fenêtre de rejeu (le rejeu a besoin des données brutes que la rétention supprime).
- EC19 : pas d'identifiant ou de clé en clair dans le code versionné.
- EC28 : précise EE06 : \[R1\] dit « en production », ce qui exclut la démonstration depuis un carnet interactif (*notebook*) tout en acceptant l'_on-premise_. 

---

## 0.4. Périmètre

On explicite les fonctionnalités à construire, les contraintes à vérifier et la documentation à produire, et on précise les limites des périmètres fonctionnel et architectural de l'infrastructure à réaliser.

### 0.4.1. Identification des fonctionnalités à construire

Fonctionnalités à construire. D'après §0.3.

| #         | Fonctionnalité                                                                                                                              | C/&nbsp;R1\|R2 | C/ D0      |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ---------- |
|           | **Ingestion**                                                                                                                               |                |            |
| **F02.1** | Interroger le simulateur \[R4\] en quasi-temps réel et récupérer les nouvelles transactions                                                 | G1             | EE01/EI09 |
| **F02.2** | Charger l'historique des transactions \[R3\]                                                                                                |                | EI04/EI05 |
| **F02.3** | Dissocier la transaction de son verdict (et anti-dater ce dernier)                                                                          |                | EI01/EI02 |

<div style="page-break-after: always;"></div>

| #         | Fonctionnalité                                                                                                                              | C/&nbsp;R1\|R2 | C/ D0      |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ---------- |
|           | **Stockage**                                                                                                                                |                |            |
| **F03.1** | Conserver les données brutes, sans changement (en *append-only*)                                                                            | C2/C5         | EC24       |
| **F03.2** | Stocker les transactions *typées*, leurs features et leur prédiction                                                                        | C2             | EE08/EI03 |
| **F03.3** | Répartir les données sur plusieurs bases ou emplacements distincts                                                                          | C2             | EC05       |
|           | **Transformation**                                                                                                                          |                |            |
| **F04.1** | Calculer les features à l'ingestion et les persister sur la transaction, de sorte que l'entraînement et le scoring lisent les mêmes sources |                | EE07/EI05 |
| **F04.2** | Garantir que le calcul des features par ligne et leur rétro-calcul par lot produisent les mêmes valeurs                                     | C5             | EE07       |
|           | **Modèle**                                                                                                                                  |                |            |
| **F05.1** | Entraîner un modèle de scoring sur des verdicts connus à la date de *coupure*                                                               |                | EI02//EI04 |
| **F05.2** | Enregistrer le modèle, sa version et ses métriques, et le mettre à disposition du pipeline                                              |                | EE08/EI10 |
|           | **G1**                                                                                                                                      |                |            |
| **F06.1** | Scorer chaque nouvelle transaction et appliquer le seuil de décision une seule fois                                                     | G1             | EE01       |
| **F06.2** | Notifier l'analyste de fraude sur les transactions prédites frauduleuses                                                                    | G1             | EE02       |
|           | **G2**                                                                                                                                      |                |            |
| **F07.1** | Produire chaque matin le bilan des paiements et des fraudes de la veille, sur fenêtre calendaire                                            | G2             | EE03/EI07 |
| **F07.2** | Confronter les scores aux verdicts échus pour mesurer le rappelet la précision réellement observés, par version de modèle              | C4             | EI02/EI03 |
| **F07.3** | Restituer la répartition des rejets par motif                                                                                               | C4/C5         | EC15/EC22 |
| **F07.4** | Comparer les volumes de transactions entrées avec les volumes de transaction rapportées et rapporter l’écart                                |                | EI08       |
|           | **Automatisation**                                                                                                                          |                |            |
| **F08.1** | Orchestrer les traitements à des cadences distinctes,sans intervention manuelle                                                        | C3             | EI06, EC08 |
| **F08.2** | Exprimer les dépendances entre traitementspar des conditions de garde sur l'historique d'exécution                                     | C3             | EC09       |
| **F08.3** | Appliquer une politique de reprise : essais, délai, comportement terminal                                                                   |                | EC10       |
|           | **Qualité**                                                                                                                                 |                |            |
| **F09.1** | Valider les données entrantes :schéma, types, valeurs nulles, doublons, valeurs aberrantes                                             | C5             | EC20       |
| **F09.2** | Valider la cohérence **entre** colonnes,et non seulement chaque colonne isolément                                                      | C5             | EC21       |
| **F09.3** | Mettre en quarantaine les enregistrements rejetés, avec leur motif                                                                          | C5             | EC22       |
| **F09.4** | Rejouer le traitement depuis la zone brute (par lot, sans produire de doublon)                                                              | C5             | EC23/EC24 |
|           | **Monitoring**                                                                                                                          |                |            |
| **F10.1** | Journaliser les exécutions : volumes lus, valides, rejetés, état, durée, santé du transport                                                 | C4             | EC12       |
| **F10.2** | Détecter les absences : exécution vide, fraîcheur dépassée, exécutions manquantes                                                           | C4             | EC14       |
| **F10.3** | Alerter l'exploitant sur un canal spécifique (distinct de celui de l'analyste de fraude)                                                    | C4             | EC13       |
| **F10.4** | Exposer l’état courant de l’infrastructure en marche                                                                                        |                | EI11       |
|           | **Gouvernance**                                                                                                                             |                |            |
| **F11.1** | Pseudonymiser l'identifiant porteur (sans recopier les données d'identité dans la couche exploitée) (a)                                     | C4             | EC17       |
|           | **Sécurité**                                                                                                                                |                |            |
| **F12.1** | Gérer les secrets                                                                                                                           | C4             | EC19       |
| **F12.2** | Gérer les accès par rôle                                                                                                                    | C4             | EC19       |
| **F12.3** | Purger les données brutes au-delà de la durée de conservation et tracer la purge                                                            | C4             | EC18       |
|           | **Démontrabilité**                                                                                                                          |                |            |
| **F13.1** | Paramétriser les durées qui dépassent celle de la démonstration (délai de verdict, rétention)                                               |                | EE06/EI12 |
> _Légende : C/ R1|R2 : couvre un élément de R1 ou de R2, C/ D0 : couvre une exigence D0 (EE, EI, EC)_

<div style="page-break-after: always;"></div>

###### Remarques
- (a) On suppose qu'une requête de transaction contient nécessairement les informations suivantes : nom, prénom, rue, date de naissance, profession, coordonnées du domicile, numéro de carte bancaire (tokenisé ou non).

### 0.4.2. Contraintes à vérifier

Propriétés d'assemblage à vérifier. D'après §0.3.

| #   | Vérification                                                                                                                       | Constatée sur                | Couvre |
| --- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ------ |
| K01 | Les trois éléments de l'architecture minimale (collecte/stockage, consommation, processus *ETL/ELT*) sont identifiables et nommés | Schéma D1                    | EE09   |
| K02 | Les processus de collecte et de consommation sont distincts                                                                        | Schéma D1                    | EI14   |
| K03 | Les transformations du pipeline sont définies par du code versionné (*SQL*, *Python*, ...)                                             | Dépôt de code                | EC06   |
| K04 | Un tiers reconstruit l'infrastructure depuis D2 et le document d'installation                                                      | Reconstruction effective | EI13   |
| K05 | La démonstration démontre une configuration déployée                                                                               | Capture vidéo D3             | EC27   |

### 0.4.3. Documents à produire

Artefacts documentaires à produire.  D'après §0.3.

| #   | Artefact         | Contenu                                                                            | Couvre |
| --- | ---------------- | ---------------------------------------------------------------------------------- | ------ |
| D01 | D1               | Le schéma de l'infrastructure et sa justification                                  | EE04   |
| D02 | D1               | Typologie de chaque source et de chaque magasin                                    | EC01   |
| D03 | D1               | Débit attendu et objectif de latence                                               | EC02   |
| D04 | D1               | Volumétrie de stockage par magasin                                                 | EC03   |
| D05 | D1               | Contraintes et normes opérationnelles retenues en hypothèse                        | EC04   |
| D06 | D1               | Décision d'optimisation argumentée par les durées mesurées _(alimentée par F10.1)_ | EC11   |
| D07 | D1               | Dépendances entre tâches et flux, exposées _(réalisées par F08.2)_                 | EC09   |
| D08 | D1               | Matrice de traçabilité exigence → infrastructure → code                            | EC07   |
| D09 | D1/Annexe | Gouvernance : données personnelles, pseudonymisation, rôles, conservation          | EC16   |
| D10 | D2               | Le code source de tous les éléments nécessaires                                    | EE05   |
| D11 | D2               | Hébergement sur GitHub                                                             | EC26   |
| D12 | D3               | La capture vidéo de l'infrastructure en fonctionnement                             | EE06   |
| D13 | D3               | Erreur provoquée en D3, sa détection et son traitement                             | EC25   |
| ~~D14~~ | ~~Dossier~~  | ~~Structure permettant de localiser C1 à C5~~                              | ~~EC28~~   |

### 0.4.4. Eléments d'architecture écartés

D'après \[R2\].

- Un déploiement *cloud* :
	- Raison : le déploiement *on-premise* est accepté                                                                    
- Un service de scoring *synchrone* avec blocage des paiements frauduleux :
	- Raison : Le métier demande simplement une notification. On n'a aucune exigence sur le chemin critique du paiement : service résident, pas de haute disponibilité synchrone, budget de latence temps-réelle.  
- Un bus d'évènement asynchrone (ex: *Kafka*+*Debezium*)
	- Raison : 1 producteur, 1 consommateur, 7200 messages/jour : le projet n'est pas dimensionné pour un découplage OLTP/OLAP.
- Un orchestrateur des magasins de features (ex: *Feast*)
	- Le magasin de features *online* est justifié par l'existence d'un scoring synchrone à haute disponibilité. En contre-partie, F04.1 garantie la cohérence des features d'entrainement et de features de scoring temps-réel.
- Des outils de transformation et de validation spécifiques (ex: *dbt*, *Great Expectations*) 
	- Raison : du code SQL et une fonction de validation explicite couvrent C2 et C5 correctement à l'échelle de l'exercice et de la démonstration.
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
| **C1** | **Concevoir** un système de gestion de données temps réel adapté aux contraintes et normes opérationnelles de l'entreprise, pour gérer efficacement la vélocité, le volume des flux, et la typologie des données.                                   |
| **C2** | **Etablir** un pipeline de données à travers des processus ETL/ELT pour le transfert et la transformation des données entre différentes bases, en utilisant des outils de programmation, afin de répondre aux spécifications du cahier des charges. |
| **C3** | **Automatiser** les flux de données dans le pipeline, en utilisant des outils spécifiques ou de la programmation, afin d'optimiser les performances de l'infrastructure de données.                                                                 |
| **C4** | **Surveiller** les flux de données pour assurer la qualité et le respect de la politique de gouvernance, en vue de maintenir les normes, la sécurité et la confidentialité dans les pipelines de données.                                           |
| **C5** | **Développer** des procédures de contrôle qualité et de correction des erreurs dans les pipelines de données, afin de garantir la qualité des données.                                                                                              |

---

## Références
- \[R1\] [Jedha Certification - AIA/BC03](https://app.jedha.co/certifications/rncp38777bc03)
- \[R2\] [Automatic Fraud Detection Project](https://app.jedha.co/course/etl-with-airflow-lds/automatic-fraud-detection-project-lds)
- \[R3\] [Fraudulent Payments full dataset](https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv)
- \[R4\] [Real-time payment API](https://huggingface.co/spaces/sdacelo/real-time-fraud-detection)

---
