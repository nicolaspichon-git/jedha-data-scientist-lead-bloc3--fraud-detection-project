# Guide d'utilisation du dashboard

Explications des champs du tablea de bord pour chaque page. 

> Rappel : le tableau de bord ne calcule aucune décision : il relit simplement ce que le pipeline enregistre.

###### Conventions :
- Les dates sont à l'heure de Paris. 
- Le code couleur du bandeau en entête de chaque page suit la convention suivante :
    - *vert* : tout va bien ;
    - *bleu* : une information ;
    - *orange* : un point à surveiller ;
    - *rouge*  : un problème à traiter.

---

## Analyse

### 1. Rapports

###### Le sélecteur de journée : 
Sélectionne la date de la journée couverte par le rapport. Par défaut, c'est la date du rapport le plus récent.

> *Attention* : selon le mode de fonctionnement du système, une *journée* est comptée à partir de 00:00:00 (mode *nominal*) ou de 12:00:00 (mode *demo*). Par exemple, la journée couverte du 22/11 en mode *demo* s'étend du 22/11 à 12:00:00 au 23/11 à 12:59:59.

###### Les bandeaux d'entête :
- les matins **sans rapport**, sur toute la série et pas seulement le jour choisi ;
- l'état du document :
  - vert, « conforme à son empreinte » ;
  - rouge, « modifié après sa production » ;
  - rouge, « introuvable sur le disque » ;
- orange, si le document n'est pas lu au même chemin que celui où il a été écrit.

###### Les indicateurs :
Lus dans la ligne `fd_reports` du jour :

| Champ | Signification |
|---|---|
| Paiements | transactions de la journée couverte |
| Alertes | paiements de cette journée jugés frauduleux par le modèle |
| Verdicts échus | verdicts connus pour ces paiements au moment du rapport |
| En attente de verdict | paiements dont on ne sait pas encore s'ils étaient frauduleux (le verdict arrive environ 30 jours plus tard) |
| Modèle | version du modèle qui a levé les alertes (« aucune alerte, aucun modèle à nommer » s'il n'y en a pas) |
| Seuil | score à partir duquel le modèle lève une alerte |
| Connaissance au | instant où les informations du rapport ont été arrêtées, 06:00 le lendemain |
| Produit le | instant où le rapport a été écrit |

**En dessous**, le rapport complet, tel que le métier le reçoit.

### 2. Alertes de fraude

###### Le sélecteur de période : 
Un jour ou une plage, 92 jours au plus. Par défaut, aujourd'hui.

###### Les bandeaux d'entête :
- rouge, si des alertes ont échoué à l'envoi ;
- orange, si le **plafond de notification** est atteint. Les alertes suivantes sont levées mais pas envoyées : c'est une décision voulue, pas une panne ;
- bleu, s'il n'y a aucune alerte.

###### Les indicateurs :

| Champ | Signification |
|---|---|
| Alertes de la période | nombre d'alertes levées |
| Notifiées | celles qui ont été envoyées à l'analyste |
| Non notifiées | levées mais pas encore envoyées (échec, ou plafond atteint) |
| Notifiées sur 24 h glissantes | « x / 60 » : ce qui a été envoyé sur les dernières 24 heures, face au plafond |

**Note sous les indicateurs** : le canal déclaré, et le nombre d'alertes en attente toutes journées confondues.

###### Le tableau des alertes :

Les alertes triées par perte attendue décroissante, comme dans le rapport :

| Colonne | Signification |
|---|---|
| Date et heure | moment du paiement |
| Montant | montant du paiement |
| Commerçant, Catégorie | où et quoi |
| Score | probabilité de fraude donnée par le modèle |
| Seuil | seuil en vigueur au moment du scoring |
| × habituel | montant divisé par le montant moyen du porteur : « 16,9 » veut dire 17 fois sa dépense habituelle |
| Perte attendue | score × montant, l'ordre de priorité pour l'analyste |
| Notifiée le | moment de l'envoi, ou « non » |
| Canal | canal qui a effectivement reçu l'alerte ; vide si elle n'est pas partie |
| Tentatives | nombre d'essais d'envoi |
| Dernière erreur | motif du dernier échec d'envoi |
| Modèle | version du modèle qui a décidé |
| Transaction | identifiant de la transaction (`trans_num:n`) |

Le pseudonyme du porteur n'apparaît pas : l'analyste n'en a pas besoin.

## Exploitation

### 3. Contrôles d'exploitation

C'est l'état du pipeline temps réel **maintenant**, sur les 60 dernières minutes. Ce sont les mêmes contrôles que ceux que `dag_ingest` lance chaque minute.

###### Les bandeaux d'entête :
- rouge, un par contrôle en alerte ;
- orange, si un changement d'état n'est pas encore notifié. Si ce bandeau dure, le DAG ne tourne plus ;
- vert, si tout est bon.

###### Les indicateurs :

| Champ | Signification |
|---|---|
| Dernière réussite | temps écoulé depuis la dernière exécution réussie : c'est la fraîcheur |
| Exécutions terminées | exécutions de `dag_ingest` sur la fenêtre |
| En échec | celles qui ont échoué |
| Vides | celles qui n'ont lu aucune transaction |
| Lignes lues | transactions reçues du simulateur |
| Lignes rejetées | celles écartées par la validation |

###### Le tableau des contrôles :
Une ligne d'information par contrôle :
- **Contrôle** : le nom du contrôle ;
- **État** : ALERTE ou ok ;
- **Constat** : ce que le contrôle a mesuré ;
- **Seuil déclaré** : la limite fixée dans `governance.yml` ;
- **Dernier état notifié** : le dernier état envoyé sur le canal d'exploitation ;
- **Depuis** : depuis quand cet état dure.

Les quatre contrôles :

| Contrôle | Ce qu'il surveille | Seuil |
|---|---|---|
| Fraîcheur (« Fressness check ») | plus aucune exécution réussie | 10 min sans réussite |
| Empty run | trop d'exécutions vides | 10 % des exécutions |
| Rejection rate | trop de lignes rejetées | 5 % des lignes lues |
| Volume invariant | un lot où lues ≠ valides + rejetées | 0 lot |

**Le tableau « Dernières exécutions »** liste les 30 dernières : Début, Durée (s), État, Lues, Valides, Rejetées, Exécution (identifiant Airflow).

Deux remarques sur les libellés des contrôles :
- « Fressness check » contient une faute de frappe ;
- ils sont en anglais alors que le reste de la page est en français. Je peux corriger.

### 4. Alertes d'exploitation

Ce que le canal d'exploitation a envoyé, d'après son journal.

La page « Contrôles » montre l'état présent, celle-ci montre l'historique des messages.

###### Les bandeaux d'entête :
- rouge, pour tout contrôle encore en alerte, même si l'alerte a été envoyée avant la période ;
- bleu, s'il n'y a aucun message. Le canal ne parle qu'aux changements d'état, donc un silence n'est pas une panne.

###### Les indicateurs :
- Messages envoyés, Passages en alerte, Retours au vert, Incident le plus long.

###### Le tableau :
Historique des messages envoyés :
- **Envoyé le** : moment de l'envoi ;
- **Contrôle** : le contrôle concerné ;
- **Devenu** : ALERTE ou ok ;
- **Constat** : la mesure qui a déclenché le changement ;
- **Durée de l'incident** : remplie sur un retour au vert, du message d'alerte à celui de retour ;
- **Canal** : le canal utilisé ;
- **Exécution** : l'évènement d'exécution de `dag_ingest` qui a envoyé le message.

## Suivi

### 5. Rejets de validation

###### Les bandeaux d'entête :
- orange, si le taux de rejet du flux dépasse 5 % : la forme des données reçues a changé ;
- orange, si un motif n'est pas dans le vocabulaire déclaré ;
- bleu, si rien n'a été rejeté.

###### Les indicateurs :
| Indicateur | Signification |
| -- | --- |
| Lignes rejetées | lignes mises en quarantaine sur la période |
| Motifs relevés | nombre total de motifs : une ligne peut en avoir plusieurs |
| Lots touchés | lots d'ingestion qui contenaient au moins un rejet |
| Taux de rejet du flux | rejetées / lues, pour le seul flux temps réel |

###### Le tableau par motif :
Regroupement des évènements de rejet par *motif* :
- **Classe** : la famille de défaut (schéma, type, valeur, cohérence…) ;
- **Motif** : le libellé lisible ;
- **Code** : le code technique, par exemple celui de l'acte 4 de la vidéo ;
- **Motifs** : nombre d'occurrences de ce motif ;
- **Lignes** : nombre de lignes concernées ;
- **Lots** : nombre de lots concernés.

La colonne « Lignes » ne s'additionne pas, puisqu'une ligne compte une fois par motif. Le contenu des lignes rejetées n'est jamais affiché.

### 6. Performances du modèle

###### Sélecteur « Période de réception des verdicts » : 
Les 30 derniers jours par défaut. On regarde les verdicts reçus pendant la période sélectionnée. Ceux-ci portent sur les paiements datant de 30 jours (5 minutes en mode de *démonstration*).

###### Les bandeaux d'entête :
- *orange*, si la référence est indisponible. 
    - dans ce cas, le remède est `.\fd-manager.ps1 reference` ;
- *bleu*, si aucun verdict n'est reçu ;
- *bleu*, si plusieurs versions du modèle ont décidé (???).

###### Les indicateurs :
- *Verdicts reçus*, *Fraudes confirmées*,* Fraudes manquées* (non alertées mais frauduleuses), *Fausses alertes* (alertées mais légitimes).

- *note* : la note sous le badeau des chiffres rappelle quels paiements sont jugés et nomme la recette de référence.

###### Tableau de comparaison : 
Le tableau de comparaison, observé contre mesuré sur le jeu de test (B3-M5) :
- **Fraudes retrouvées (rappel)** : 
    - la part des vraies fraudes que le modèle a alertées ;
- **Alertes justes (précision)** : 
    - la part des alertes qui étaient de vraies fraudes ;
- **Part de fraudes** : 
    - le taux de base. Les deux colonnes ne se comparent que si cette part est voisine.

###### Matrice de confusion :
La matrice croise les paiements alertés ou non avec les fraudes confirmées ou non. Ses quatre cases donnent les vrais et faux positifs et les vrais et faux négatifs.

##### [Performances] jour par jour :
- La courbe du rappel et de la précision observés.
- Section non affichée si il n'existe pas de verdicts établis sur les transactions de la période sélectionnée.

###### [Performances] par version du modèle : 
- Table rapportant pour chaque version de modèle : la recette, les verdicts, les fraudes, le rappel et la précision observés.
- Les versions de modèle rapportées sont les versions qui ont scoré des transaction de la période sélectionnée.
- Section non affichée si il n'existe pas de verdicts établis sur les transaction de la période sélectionnée.
