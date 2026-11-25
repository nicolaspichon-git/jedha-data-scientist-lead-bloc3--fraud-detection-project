*Automatic Fraud Detection* Project
===

# Scénario de la capture vidéo 

> Examen BC03, RNCP 38777. Durée montée visée : **6 min 30**.
> Version 7 --- 24 novembre 2026. Remplace la version 6 du même jour.
>
> Changements de la v7 : 
> - à l'acte 5, l'alerte de fraîcheur est envoyée à la main (`health -Notify`) : les contrôles tournent dans `dag_ingest`, et s'arrêtent avec lui (défaut connu, à corriger plus tard par un surveillant indépendant) ;
> - l'acte 6 commente l'écart observé : précision tenue, rappel en retrait. Coquilles corrigées.
>
> Changements de la v6 : 
> - le tournage a lieu **après 14:00** le 24/11 ;
> - l'acte 3 suit la journée de démonstration du **23/11** (de 12:00 à 12:00), dont le rapport est livré le 24 à 14:00 : le paiement du 24/11 à 04:29, 1 113,08 ;
> - ce rapport est le premier produit après la correction du fuseau.
>
> Changements de la v5 : 
> - réécriture du texte lu ; 
> - la clôture ne montre plus ni `check` ni la traçabilité.
> 
> Changements de la v4 : 
> - le tournage a lieu le 24 novembre **avant 14:00**, avec
> les deux bascules de `governance.yml` en mode `demo` --- `report.mode` (journée
> de midi à midi, rapport livré à 14:00) et `verdicts.mode` (verdict échu après
> 300 s). L'acte 3 suit donc la journée de démonstration du 22 novembre, dont le
> rapport a été livré le 23 à 14:00 ; l'acte 6 montre une colonne « observé »
> remplie ; le simulateur accepte 10 appels par minute ; la préparation de « la
> veille » devient une liste « avant de tourner ».
>
> La documentation et les diagrammes du projet restent sur le paramétrage
> nominal (journée de minuit à minuit, rapport à 06:00, verdict à 30 jours).

---

## 1. Ce que la capture vidéo doit prouver

Les sources, relues avant d'écrire :

| Source | Ce qu'elle demande à la vidéo |
| --- | --- |
| Fiche projet, B3-D3 | une vidéo de l'infrastructure **en fonctionnement, sur un exemple** |
| Certification BC03, livrables | une capture vidéo de l'infrastructure **en production**, cloud ou *on-premise* |
| B3-D0, **B3-EE06** | présenter l'infrastructure en fonctionnement sur un exemple |
| B3-D0, **B3-EC25** | provoquer une erreur et montrer sa détection et son traitement |
| B3-D0, **B3-EC27**, **B3-K05** | une configuration *déployée* --- pas un carnet interactif |
| Certification, format | le pipeline, l'automatisation, le contrôle qualité, et la *possibilité* de monitorer les performances |
| Fiche projet, conseils | *« The most important part is the Data Pipeline --- not the ML algorithm »* |

Et cinq compétences à démontrer : **concevoir** (B3-C1), **établir** l'ETL (B3-C2),
**automatiser** (B3-C3), **surveiller** qualité, gouvernance, sécurité et
confidentialité (B3-C4), **développer** le contrôle qualité et la correction des
erreurs (B3-C5).

**La durée.** Aucune source n'en fixe pour la vidéo. La **présentation** devant
le jury dure 5 minutes, suivie de 15 minutes de questions. Une vidéo d'environ
six minutes se regarde en entier, et ses actes peuvent servir d'appui à la
présentation.

## 2. La trame : un exemple, une erreur, une panne

###### 2.1. Un paiement suivi de bout en bout
\> de la ligne brute à la notification de l'analyste, puis au rapport de sa journée. 

Couvre : B3-EE06 (présenter l'infrastructure en fonctionnement), B3-C2 (pipeliner), et B3-C4 (garantir la confidentialité).

######  2.2. Une erreur provoquée
\> un enregistrement corrompu, sa détection, son traitement. 

Couvre : B3-EC25 (provoquer/détecter/suivre une erreur d'ingestion) et B3-C5 (contrôler/corriger la qualité).
   
######  2.3. Une panne détectée
\> le pipeline s'arrête, quelqu'un le sait. 

Couvre : B3-C4 (surveiller), et la panne qu'aucun contrôle sur les données ne peut voir.

Le modèle n'a que quelques secondes à l'écran, comme le demande la fiche projet.

---

## 3. Les actes

Pour chaque acte : ce qui est à l'écran, ce qu'on fait, la voix, et ce que l'acte prouve. La voix se lit à environ 130 mots par minute. Les valeurs entre crochets se lisent à l'écran au moment de l'enregistrement.

### Ouverture --- 0:20

**Écran** : le schéma de B3-D1, plan fixe.

**Voix** :
> Le contexte de l'exercice est le suivant : 
> une banque fournit des transactions de paiement par carte bancaire en flux continu. 
> 
> Le système ingère ces transactions par micro-lots toutes les minutes.
> Il repère à la volée celles qui pourraient être des fraudes, et prévient immédiatement un analyste.
> 
> Je vais montrer le système en fonctionnement 
> - sur un paiement, 
> - sur une erreur provoquée, 
> - et sur une panne.

### Acte 1 --- Une pile déployée --- 0:40

**Prouve** : B3-EC27, B3-K05 --- B3-C1.

**Écran** : 
1. Terminal `fd-manager` : 
	- `.\fd-manager.ps1 status` ; 
2. Diagrammes D1 : 
	- *puis* le schéma de B3-D1, zoom sur les deux zones de la base.

**Voix** :
> Le système est une pile de 6 conteneurs, déployée localement sur cette machine :
> - *PostgreSQL* stocke les transactions et les données opérationnelles associées, 
> - *Airflow* orchestre les pipelines automatisés, 
> - *MLflow* enregistre les modèles de scoring, 
> - un tableau de bord *Streamlit* les restitue. 
> 
> Le sixième conteneur local joue le rôle du système de paiement :
> un simulateur API qui sert une transaction à chaque appel. 
> 
> On n'a qu'une seule base pour les données de transactions. 
> En particulier : 
> - une zone de données brutes (*bronze*) qui stocke les évènements de transaction tels quels,
> 	- seules tables à contenir l'identité des porteurs ;
> - une couche d'exploitation (*silver*) qui stocke les transactions structurées et les entités associées (scores, etc.),    
> 	- et où les données personnelles sont pseudonymisées. 
> 
> On a également des rôles à accès limité pour chaque usage spécifique : 
> - le rôle qui produit le rapport ne peut pas lire la zone brute, 
> - le rôle qui récupère les données pour le tableau de bord ne peut pas écrire en base.

### Acte 2 --- Un flux automatisé --- 0:50

**Prouve** : B3-C2, B3-C3.

**Écran** : 
1. *Airflow* :
	1. la liste des six DAG et leurs cadences ; 
	2. la grille de `dag_ingest`, verte à chaque minute ; 
	3. le graphe des tâches d'une exécution ; 
2. *MLflow* :
	1. cinq secondes sur le modèle enregistré.

**Voix** :
> On a 6 DAG orchestrés sous Airflow, chacun ayant sa propre cadence. 
> 
> `dag_ingest` : l'ingestion en temps réel est relancée toutes les minutes : 
> le processus interroge le simulateur de paiement,
> il écrit la ligne brute, la valide, retire l'identité, calcule l'historique du
> porteur, score le paiement, et alerte sur le canal dédié si besoin. 
> 
> Le DAG d'ingestion ne fait qu'ordonner :
> la logique métier est isolée dans du code testable sans Airflow. 
> 
> `dag_train` : le modèle est réentraîné chaque lundi et enregistré dans *MLflow*, 
> avec un seuil de fraudulosité calé sur la capacité de l'analyste à traiter les alertes dans une journée (à savoir, soixante alertes par jour).

### Acte 3 --- Un paiement, de bout en bout --- 1:30

**Prouve** : B3-EE06 --- B3-C2, et B3-C4 pour la confidentialité.

**Écran**, dans l'ordre :

1. Terminal `psql`:
	1. `\set day_start 12:00`
	2. `\i /work/sql/demo/paiement_bout_en_bout.sql` (annexe A). 
		- Le script sélectionne l'exemple suivi : la fraude notifiée qui pèse le plus dans la dernière journée rapportée --- puis il affiche quatre blocs : zone bronze, couche silver, score, alerte.
		- Attendu le 24/11 après 14:00 : 
			- le paiement du **24/11 à 04:29** (heure de Paris), chez `fraud_Kassulke PLC`, 
			- montant de **1 113,08**, score **0,994**, perte attendue **1 106,58**, 
			- journée du **2026-11-23**, « fraude d'hier : oui », 
			- rapport existant.
2. Terminal `PowerShell` : 
	1. La ligne de ce paiement dans le canal de l'analyste :
		- `Select-String -Path runtime\channels\frauds\frauds.jsonl -SimpleMatch '[trans_num]'`.
3. Le tableau de bord
	1. Page **« Alertes de fraude »** : 
		- choisir la journée du **2026-11-23** (après 14:00, la page ouvre par défaut celle du 24, de 12:00 à 12:00, presque vide) : la même ligne, à 04:29.
	2. Page **« Rapports »** : 
		- le rapport « journée du 2026-11-23 (de 12:00 à 12:00) », 
		- livré le 24 à 14:00, 
		  verdict **« conforme »**, 
		- et la section 2 où ce paiement est en tête.

**Vérifier l'heure dans ce rapport.** C'est le premier rapport produit après la correction du fuseau : sa section 2 doit afficher **04:29**, comme le tableau de bord. S'il affiche 03:29 (UTC), la correction n'a pas été prise par le planificateur : ne pas zoomer sur la colonne heure et ne pas lire d'heure à voix haute. Dans tous les cas, ne pas rejouer le rapport : son empreinte est en base.

**Voix** :
> Nous allons suivre un paiement de cette nuit, signalé comme fraude. 
> 
> [commande `psql`]
> 
> [Bloc 1] Dans la zone Bronze, l'évènement est stocké avec l'identité du porteur,
> transmise par l'application de paiement : 
> - nom, adresse, numéro de carte. 
>
> [Bloc 2] Dans la couche Silver, le porteur est un pseudonyme, 
> calculé avec une clé non versionnée. 
> Dans les colonnes finales, on a les données analytiques calculées par le pipeline 
> et qui serviront de features au modèle de scoring : 
> les paiements passés, le montant habituel, la distance au domicile.
>
> [Bloc 3] Le modèle lui donne un score de [score], au-dessus du seuil de fraude de [seuil].
> 
> [Bloc 4] La transaction est donc signalée, et une alerte est levée.
> 
> [dashboard] [fraudes] L'analyste est prévenu dans la minute. 
> 
> [dashboard] [rapport] Le rapport de sa journée le place en tête des alertes, par perte attendue.
> 
> **Noter que**, pour la démonstration, la journée est comptée de midi à midi (au lieu de minuit à minuit, en exploitation) et le rapport arrive à 14 h (au lieu de 6 h).
> 
> **Noter également que** le document chargé par le dashboard est *vérifié*, 
> en comparant son empreinte à celle qui est conservée en base et qui signe le rapport généré.

### Acte 4 --- Une erreur provoquée --- 1:10

**Prouve** : B3-EC25, B3-EC22 --- B3-C5.

**Écran** :
1. Terminal `fd-manager`
	1. `.\fd-manager.ps1 ingest -Corrupt`. 
		   - Couper l'attente des appels à l'API. 
		   - Garder à l'écran la ligne « la dernière lecture a été corrompue volontairement », 
		   - le nombre de transactions scorées, 
		   - puis le bloc « quarantaine : 
			   - 1 ligne(s), 2 motif(s) » avec ses deux codes.
2. Terminal `psql`
	- `psql` : `\i /work/sql/demo/erreur_quarantaine.sql` (annexe B) 
	- Montrer les motifs de la ligne rejetée, puis les compteurs du lot.

**Voix** :
> Nous allons maintenant vérifier que le système contrôle les erreurs en entrée.
> 
> Nous allons exécuter un cycle d'ingestion à la main, et le corrompre volontairement :
> 
> [fd-manager : commande d'ingestion corrompue]
> 
> dans la dernière ligne reçue : 
> - le montant sera réécrit *en lettres*, 
> - et une colonne supprimée. 
> 
> Les erreurs sont détectées en cours de validation, avec deux motifs
> codés, un pour chaque anomalie. 
> 
> [psql : quarantaine]
> 
> La ligne n'est ni perdue ni corrigée, elle part en *quarantaine*, avec ses motifs. 
> 
> Les autres lignes du même lot sont ingérées et scorées normalement. 
>
> Les compteurs le prouvent : 
> - le nombre de lignes lues *égale* les lignes valides *plus* les lignes rejetées. 

### Acte 5 --- Une panne détectée --- 1:00

**Prouve** : B3-EC14 --- B3-C4.

**Pourquoi une notification à la main.** Les quatre contrôles et l'envoi sur le canal d'exploitation tournent dans les deux dernières tâches de `dag_ingest`. Mettre `dag_ingest` en pause arrête donc aussi son surveillant : la fraîcheur devient rouge sur le tableau de bord (qui recalcule les contrôles à chaque affichage), mais aucun message ne part. La correction --- un DAG de surveillance indépendant --- est reportée. Pour la vidéo, les contrôles sont lancés à la main avec envoi, et la voix le dit.

**Écran** :

1. *Carton* : « Ingestion en pause --- dix minutes plus tard ».
2. Page **« Contrôles d'exploitation »** : la fraîcheur en rouge, « Dernière réussite : il y a [n] min ».
3. Terminal `fd-manager` : `.\fd-manager.ps1 health -Notify` --- la fraîcheur en alerte, et la transition envoyée.
4. Page **« Alertes d'exploitation »** : le message de passage en alerte.
5. *Carton* : « Ingestion relancée ».
6. Page **« Alertes d'exploitation »** : le message de retour au vert, envoyé cette fois par `dag_ingest` lui-même, et la durée de l'incident.

**Voix** :
> Nous allons suivre maintenant une panne : l'arrêt du pipeline d'ingestion.
> 
> Le processus d'ingestion a été mis en pause pendant dix minutes. Aucune donnée
> fausse, rien à valider : simplement, plus rien n'arrive.
> 
> Le contrôle de fraîcheur est rouge.
> 
> Dans cette version, les contrôles tournent dans le pipeline lui-même : quand il
> s'arrête, ils s'arrêtent avec lui. Je les lance donc à la main, et le message
> d'alerte part au responsable du pipeline, sur son canal dédié. Un surveillant
> indépendant est la prochaine correction.
> 
> Je relance l'ingestion : le pipeline envoie lui-même un second message, qui
> notifie la reprise et la durée de l'incident.

### Acte 6 --- La performance surveillée --- 0:40

**Prouve** : B3-C4, et le monitoring des performances que demande l'examen.

**Écran** : 

[dashboard]
- Page **« Performances du modèle »**, sur son mois par défaut :
	- Le tableau « observé / mesuré », 
	- Les deux colonnes remplies, 
	- puis la courbe jour par jour (rappel et précision observés).

**Avant de filmer** : 

**déclencher l'écriture des verdicts** (qui ne passe automatiquement qu'à 02:00) :

```
docker compose exec airflow-scheduler airflow dags trigger dag_ingest_verdicts
```

puis recharger la page.

**Voix** :

[dashboard] [performances]

> Le modèle a-t-il raison ?
> 
> En exploitation, le verdict arrive un mois après le paiement, quand le porteur
> conteste. Pour la démonstration, ce délai est réduit à *cinq minutes*.
> 
> Le tableau de bord compare ce qui est *observé* sur le flux à ce qui a été
> *mesuré à l'entraînement*. La précision tient : quand le modèle alerte, il a
> raison à peu près aussi souvent. Le rappel, lui, décroche : le modèle manque
> des fraudes qu'il retrouvait sur le jeu de test.
> 
> Les volumes sont encore petits, une trentaine de fraudes, mais c'est
> exactement le signal que cette page doit montrer : un écart entre les données
> d'entraînement et celles du flux, à instruire avant le prochain réentraînement.

*Les chiffres* (24/11, 15:30) : référence de la recette en service, précision 52,9 % et rappel 75,1 % au seuil 0,89 ; observé jusqu'au 23/11, 9 alertes confirmées sur 15. La courbe jour par jour reste bruitée (2 ou 3 fraudes par jour) : ne pas la commenter point par point. La voix ne donne pas de cause : elle reste vraie quoi que dise l'analyse (§9).

### Clôture --- 0:20

**Prouve** : rien de nouveau ; elle referme les trois histoires.

**Écran** : le schéma de B3-D1, plan fixe, comme à l'ouverture.

**Voix** :
> Un paiement suivi de la ligne brute jusqu'à l'analyste ; une erreur détectée
> et mise en quarantaine ; une panne signalée, puis résolue ; et une performance
> suivie dans le temps.
>
> Le pipeline tourne seul, et il prévient quand quelque chose ne va pas.

*Pourquoi pas `check` ici* : la vidéo montre le système en fonctionnement ; `check` est une vérification lancée à la main, qui à l'écran n'est qu'un défilement de texte. Il est gardé pour les questions (§9), où le lancer en direct pèse davantage.

---

## 4. L'ordre de tournage

On ne filme pas dans l'ordre du montage : l'acte 5 demande dix minutes d'attente, et les actes 3, 4 et 6 se tournent pendant ce temps.

**Rien avant la livraison de 14:00.** L'acte 3 a besoin du rapport de la journée du 23, livré par `dag_daily` à 14:00 : attendre qu'il apparaisse sur la page « Rapports » (quelques minutes). Avant, l'annexe A retombe sur la journée du 22 (« plan de secours »). Et la pause de l'acte 5 ne doit pas chevaucher la livraison : la commencer une fois le rapport là.

1. **Actes 1 et 2**, pendant que `dag_ingest` tourne : la grille doit être verte.
2. `.\fd-manager.ps1 realtime -Stop` --- noter l'heure.
3. **Actes 3, 4 et 6** pendant l'attente. `ingest -Corrupt` ne remet pas la
   fraîcheur à zéro : son exécution est journalisée sous `ingest_once`, et le
   contrôle ne surveille que `dag_ingest`. Et c'est **pendant** la pause qu'il
   doit tourner : le simulateur n'accepte que 10 appels par minute et par
   adresse, partagés avec `dag_ingest` quand il tourne.
4. Dix à onze minutes après la pause : **acte 5**, images 2, 3 et 4 ---
   `.\fd-manager.ps1 health -Notify`, puis la page « Alertes d'exploitation ».
5. `.\fd-manager.ps1 realtime -Start`, attendre une à deux minutes : **acte 5**,
   image 6.
6. **Ouverture**, **clôture** et cartons au montage : voix sur le schéma de B3-D1.

## 5. Préparation

**Avant de tourner (24/11, après 14:00)**

1. Les deux bascules sur `demo` dans `governance.yml` : `report.mode` et
   `verdicts.mode`. Ne rien y changer d'ici la fin du tournage.
2. `.\fd-manager.ps1 up` déjà fait ; vérifier <http://127.0.0.1:8801/docs>.
3. Le rapport de la journée du 23 est livré : dans Airflow, l'exécution de
   14:00 de `dag_daily` est verte, et la page « Rapports » le montre, verdict
   « conforme ». Contrôle, dans `psql` :
   `SELECT report_date, day_start FROM fd_reports ORDER BY report_date DESC LIMIT 3;`
   --- le 2026-11-22 et le 2026-11-23 doivent porter `12:00`.
4. `.\fd-manager.ps1 realtime` : grille verte, transactions qui arrivent. Sinon
   `.\fd-manager.ps1 logs -Service producer`.
5. `.\fd-manager.ps1 check` jusqu'au vert, une fois le rapport du 23 livré.
   Noter sa durée, pour les questions.
6. La référence B3-M5 en base : la page « Performances du modèle » ne doit pas
   afficher « référence indisponible ». Sinon, `.\fd-manager.ps1 reference`.
7. Déclencher l'écriture des verdicts (acte 6), juste avant de le filmer :
   `docker compose exec airflow-scheduler airflow dags trigger dag_ingest_verdicts`.
8. **Jouer une fois les annexes A et B**, l'annexe A avec `\set day_start 12:00`.
   Attendu : le paiement de 1 113,08, journée 2026-11-23, « fraude d'hier : oui »,
   « rapport existe : oui ». Noter le `trans_num` (il commence par `fa7d8e9ced90`).
9. Relire à voix haute les actes 5 et 6, réécrits en v7.
10. Une répétition complète, sans enregistrer (annexe C).

**Après le tournage**

- Remettre `verdicts.mode` sur `nominal` **avant le réentraînement de lundi** :
  le délai de 300 s change la bande aveugle que l'entraînement et le scoring
  doivent partager.
- Remettre `report.mode` sur `nominal` quand la démonstration n'en a plus besoin.

**Le jour du tournage**

- Écran en 1920 × 1080, navigateur à 125 %, police du terminal à 16 pt minimum.
- Notifications Windows coupées, barre des favoris masquée.
- Onglets dans l'ordre des actes : schéma B3-D1, Airflow
  (<http://localhost:8081>), MLflow (<http://localhost:8001>), tableau de bord
  (<http://localhost:8501>), terminal dans `step-2`, une session
  `.\fd-manager.ps1 psql` ouverte.
- Les commandes des annexes A et B prêtes à taper, `\set day_start 12:00` compris.

**Ce qui ne doit jamais apparaître à l'écran**

- `.env`, et `docker compose config`, qui affiche les variables **résolues**, mots de passe compris.
- Le **contenu** d'une ligne brute ou de `fd_quarantine.payload` : les données sont synthétiques, mais la vidéo applique la règle du projet. Le script de l'annexe A n'affiche que le **nom** des champs identifiants.

## 6. Au montage

- Un intertitre par histoire : « Un paiement », « Une erreur », « Une panne ».
- Zoomer sur ce qui doit être lu : les noms de champs de la zone brute, le `client_key`, le score et le seuil, les deux codes de motif, `n_read = n_valid + n_rejected`, la durée de l'incident.
- Couper toutes les attentes : appels à l'API, chargements de page.
- Voix enregistrée à part, posée sur les images.

## 7. Ce que la vidéo ne montre pas, et pourquoi

- **Le détail de l'entraînement** : la fiche projet met le pipeline avant l'algorithme. Le jury peut le demander aux questions ; MLflow et `run.json` y répondent.
- **Le rejeu d'un lot** (B3-EC23, B3-EC24) : il passe par `dag_load_history`, et je n'ai pas vérifié qu'il traite un lot **du flux** comme le flux le fait. À éprouver d'abord hors caméra, sur une copie de la base.
- **La purge** : une purge à blanc tient en vingt secondes et peut s'ajouter avant la clôture si la durée le permet.

## 8. Si un plan ne se filme pas

| Si… | Alors |
| --- | --- |
| l'annexe A affiche « fraude d'hier : non : plan de secours » | elle a pris la dernière journée **rapportée** : montrer le rapport de **cette** journée-là, et dire « un paiement récent » au lieu de « de cette nuit » |
| l'annexe A affiche « rapport existe : NON » | `\set day_start 12:00` a été oublié (la journée est alors calculée de minuit à minuit) : le poser et relancer `\i` |
| l'annexe A propose le paiement de 1 158,64 (journée du 22) | le rapport du 23 n'est pas encore livré : attendre la fin de `dag_daily` et relancer `\i`. Si on ne peut pas attendre, tourner sur la journée du 22 (version précédente : `_to_delete/fraud-project--scenario-video--v5-avant-cloture.md`) : son rapport affiche l'heure en UTC |
| `dag_daily` de 14:00 a échoué | journal de la tâche dans Airflow ; en attendant, l'acte 3 se tourne sur la journée du 22 |
| le simulateur ne répond pas pendant `ingest -Corrupt` | vérifier que `dag_ingest` est en pause (sinon : réponses 429, limite de 10 appels par minute) ; puis `.\fd-manager.ps1 logs -Service producer` (Internet, S3) ; les actes sont indépendants, réessayer plus tard |
| la colonne « observé » est vide | l'écriture des verdicts n'a pas tourné : la déclencher (§5, point 7), attendre la fin de l'exécution dans Airflow, recharger la page |
| la fraîcheur n'est pas rouge après dix minutes | vérifier que `dag_ingest` est bien en pause (`.\fd-manager.ps1 realtime`) |
| `health -Notify` n'envoie rien | la transition a peut-être déjà été envoyée (un seul message par changement d'état) : regarder la page « Alertes d'exploitation » ; sinon, le dernier état enregistré s'affiche en fin de commande |
| aucun message de retour au vert | attendre une exécution complète de `dag_ingest` (une à deux minutes) ; en dernier recours, `.\fd-manager.ps1 health -Notify` une seconde fois |
| `check` échoue pendant la préparation | le corriger avant de tourner : il ne passe pas à l'écran, mais il peut être lancé devant le jury |

## 9. Questions probables du jury

| Question | Réponse préparée |
| --- | --- |
| « Un fichier `frauds.jsonl`, c'est un journal, pas une notification » (B3-D0 le dit lui-même, B3-EE02, remarque 2) | c'est un **canal** dédié à l'analyste, distinct des journaux et du canal d'exploitation, écrit une fois par alerte et lu par la page « Alertes de fraude ». Brancher un webhook ou un e-mail ne touche qu'au module d'envoi ; la sémantique (une alerte, une notification, tentatives tracées) est déjà là |
| « Pourquoi un simulateur local et pas l'API Hugging Face ? » | l'API hébergée ne répondait plus (le rapport du 21 novembre compte 0 paiement) ; c'est le code de la même API, construit sur `python:3.11-slim` avec ses dépendances déclarées, et l'URL d'origine reste en commentaire dans `governance.yml` |
| « Un verdict en cinq minutes, ce n'est pas réaliste » | non : c'est le mode `demo` de `verdicts.mode`, pour la vidéo. En exploitation le délai est de 30 jours, et c'est le paramétrage documenté. La bascule se fait dans `governance.yml`, sans toucher au code ; elle sera remise en nominal avant le réentraînement |
| « Pourquoi une journée de midi à midi ? » | pour montrer, le jour du tournage, une matinée déjà rapportée. C'est `report.mode: demo` (journée de 12:00 à 12:00, rapport à 14:00) ; le nominal est minuit à minuit, livré à 06:00. Le rapport écrit sa plage horaire, et chaque rapport garde en base l'heure de début de sa journée |
| « Pourquoi lancer les contrôles à la main à l'acte 5 ? » | parce que dans cette version ils tournent dans `dag_ingest`, et s'arrêtent avec lui : la panne la plus simple est la seule qu'ils ne signalent pas seuls. Le défaut est identifié ; la correction est un DAG de surveillance indépendant, qui lance les mêmes contrôles (le code existe déjà, `tools/ops_check.py`) toutes les cinq minutes |
| « Pourquoi le rappel observé décroche-t-il ? » | hypothèse, à vérifier par requête : les features d'historique. Elles comptent et moyennent tous les paiements antérieurs du porteur, sans limite de durée. Le simulateur rejoue des lignes de 2020 datées d'aujourd'hui : toute la vie du porteur en 2020 leur est « antérieure », y compris les paiements qui venaient après et la ligne rejouée elle-même. `f_tx_count` est donc toujours au maximum (~600), et une fraude est comparée à une moyenne qui la contient déjà, ainsi que ses voisines. Le signal « montant inhabituel pour ce porteur » s'affaiblit : les alertes du flux sont toutes des gros montants, les fraudes manquées seraient les autres. Vérification : comparer la médiane de `f_tx_count` du flux (`txn_ts >= '2026-01-01'`) à celle de l'historique. Ce n'est pas l'heure : elle est déjà retirée du modèle (`drop_features`) |
| « Une précision à 0 % un jour, le modèle est-il cassé ? » | une journée compte une poignée d'alertes : une ou deux sans fraude confirmée donnent 0 %. Vérifier d'abord que les verdicts du jour sont écrits (`dag_ingest_verdicts`). La référence reste la mesure B3-M5 sur le jeu de test ; une dérive se lit sur plusieurs semaines |
| « Comment savez-vous que tout est conforme ? » | `.\fd-manager.ps1 check`, lancé en direct : il rejoue les critères d'acceptation des étapes S1 à S6, les invariants sur les données (concordance des features, fermeture des compteurs, aucun matin sans rapport) et les tests. Noter sa durée en préparation |
| « Et le rejeu, la purge ? » | hors vidéo, voir §7 ; `.\fd-manager.ps1 purge` à blanc se montre en vingt secondes si on le demande |

---

## Annexe A --- le paiement suivi de bout en bout

**Ne pas coller : lancer le fichier.** Collé dans `psql`, le bloc arrive en une seule ligne, et la première commande `\pset` avale tout le reste comme ses arguments. Le script est donc versionné dans `step-2/sql/demo/`, et se lance depuis `.\fd-manager.ps1 psql` :

```
\set day_start 12:00
\i /work/sql/demo/paiement_bout_en_bout.sql
```

`\set day_start 12:00` donne au script le début de journée du mode `demo` ; `psql` ne lit pas `governance.yml`. Sans lui, le script compte de minuit à minuit (nominal).

Ce que fait le script :

- **Choix de l'exemple.** Parmi les fraudes notifiées, il préfère d'abord celles dont la journée **a un rapport** (l'acte 3 finit sur le rapport), puis celles d'**hier**, puis la journée la plus récente, puis le poids score × montant.
- **En-tête.** L'identifiant, la journée rapportée, le début de journée, « fraude d'hier : oui / non », « rapport existe : oui / NON », et le `trans_num` à chercher dans `frauds.jsonl` (la partie du `txn_id` avant les deux-points).
- **Bloc 1, zone brute** : lot, ligne, instant d'ingestion, et le **nom** des champs identifiants présents --- jamais leurs valeurs.
- **Bloc 2, couche exploitée** : `txn_id`, heure, `client_key`, marchand, catégorie, montant, et les trois features d'historique.
- **Bloc 3, score** : version du modèle, score, seuil, décision, instant du scoring.
- **Bloc 4, alerte** : levée, notification, canal, tentatives.

Le script est en lecture seule. Le texte complet est dans `step-2/sql/demo/paiement_bout_en_bout.sql`.


## Annexe B --- l'erreur, ses motifs et ses compteurs

Dans la même session `psql`, juste après `ingest -Corrupt` :

```
\i /work/sql/demo/erreur_quarantaine.sql
```

Le texte ci-dessous est celui du fichier.

```sql
\x off
SET TIME ZONE 'Europe/Paris';
\echo 'La ligne rejetée : ses motifs, jamais son contenu'
SELECT q.batch_id, q.line_no, q.reason_class, q.reason_code, q.rejected_at
  FROM fd_quarantine q
 WHERE q.batch_id = (SELECT batch_id FROM fd_pipeline_runs
                      WHERE dag_id = 'ingest_once'
                      ORDER BY started_at DESC LIMIT 1)
 ORDER BY q.line_no, q.reason_code;

\echo 'Les compteurs du lot : lues = valides + rejetées'
SELECT run_id, state, n_read, n_valid, n_rejected
  FROM fd_pipeline_runs
 WHERE dag_id = 'ingest_once'
 ORDER BY started_at DESC
 LIMIT 1;
```
## Annexe C --- Plan de travail

Compter *5 à 7 heures* de travail sur *2 jours*. 
Premier jour : le 23/11 (préparation). Second jour : le 24/11, tournage après 14:00 ; l'acte 3 s'appuie sur la journée de démonstration du 23/11, rapportée le 24 à 14:00. 

| Étape | Durée | Risques |
| --- | --- | --- |
| Préparation J1 : `up`, `init`, `check`, référence B3-M5, un essai de l'annexe A | 30-45 min | un `check` qui échoue ajoute du débogage, impossible à chiffrer d'avance |
| J2.1 : Répétition complète sans enregistrement | 45 min | elle inclut les dix minutes de pause de l'acte 5 |
| J2.2 : Tournage, avec prises ratées | 60-90 min | l'API qui répond mal pendant `ingest -Corrupt` |
| J2.3 : Voix off : environ 800 mots, avec les reprises | 30-45 min | ~~malaisance à lire à voix haute~~ |
| J2.4 : Montage : une vingtaine de séquences, la voix, deux cartons, les zooms | 2-3 h | ton habitude du logiciel ; c'est le poste le plus incertain |
| J2.5 : Export, mise en ligne, visionnage complet | 20 min | |

**Deux remarques.**

- **C'est plus que prévu.** Ton plan de travail de B3-D0 comptait 2 à 3 heures pour la vidéo. 
L'écart vient presque entièrement de la voix séparée et du montage. 
Pour tenir le budget initial, une variante : 
**commenter en direct pendant l'enregistrement**, avec le texte sous les yeux, et ne monter que les coupes — l'attente de dix minutes, les appels à l'API. 
Tu retombes vers **2 h 30 à 3 h 30**, avec une vidéo moins lisse mais qui prouve exactement la même chose.

- **Le montage demande un vrai logiciel** pour les zooms et les cartons. 
Windows 11 inclut Clipchamp, qui suffit pour ça. 
Je ne sais pas ce que permet l'éditeur de Vidyard au-delà de la mise en ligne : vérifie-le avant de compter dessus.

La répétition est la ligne à ne pas sauter : c'est elle qui transforme une prise ratée sur trois en une prise ratée sur dix, et c'est là que le tournage gagne ou perd une heure.