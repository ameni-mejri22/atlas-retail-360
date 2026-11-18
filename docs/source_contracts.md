# Atlas Retail 360 — Contrats des sources

## 1. Objectif

Ce document décrit les contrats minimaux des sources du projet
Atlas Retail 360, conformément aux sections 4, 5 et 6 du PDF.

Les données générées sont entièrement synthétiques.
Les transformations métier et la correction des anomalies seront
réalisées dans les étapes prévues du pipeline, pas directement
dans les données brutes.

## 2. Paramètres du générateur

Le générateur Python doit accepter au minimum :

- `seed` : graine de génération ; valeur de référence = 42.
- `profile` : profil de volume (MICRO, STANDARD ou SCALE).
- `output_dir` : répertoire de sortie.
- `scenario` : scénario de génération.

Pour une configuration identique, les données métier et les anomalies
doivent être reproductibles.

Période métier :
- Début : 2024-09-01
- Fin : 2026-08-31

Le générateur doit produire :
- un jeu propre ;
- un jeu perturbé, avec des anomalies identifiables.

## 3. Volumes de référence

| Élément | Profil STANDARD |
|---|---:|
| Commandes | 30 000 |
| Lignes de commande | Environ 60 000 |
| Clients | 6 000 |
| Produits | 1 000 |
| Familles de produits | 6 |
| Magasins / entités de vente et de stock | 12 |
| Mouvements de stock | 120 000 |

Les volumes des faits sont indicatifs à ±10 %.
Les cardinalités de référence des magasins et des familles sont fixes.
Un profil STANDARD allégé peut être validé si l'environnement l'exige.

## 4. Conventions générales

- Les identifiants source sont des chaînes de caractères.
- Les montants sont représentés avec une précision décimale adaptée,
  et non par des nombres flottants binaires.
- Les dates et timestamps doivent respecter les contrats des sources.
- Les timestamps locaux sont interprétés avec le fuseau du magasin.
- Chaque source précise si ses timestamps contiennent un décalage UTC.
- Un timestamp local ambigu sans information suffisante est rejeté
  avec un motif explicite.
- Les champs minimaux ci-dessous peuvent être complétés si leur rôle
  est documenté.

## 5. Sources commerciales

### 5.1 `orders`

- Format : JSONL
- Grain : une version d'une commande.
- Clé : `order_id` + `source_version`.

Champs minimaux :
- `order_id`
- `source_version`
- `customer_id` (nullable)
- `store_id`
- `channel`
- `order_ts`
- `status`
- `currency`
- `campaign_id` (nullable)
- `order_discount`
- `updated_at`

### 5.2 `order_lines`

- Format : CSV UTF-8
- Grain : une version d'une ligne de commande.
- Clé : `order_id` + `line_id` + `source_version`.

Champs minimaux :
- `order_id`
- `line_id`
- `source_version`
- `product_id`
- `qty_ordered`
- `qty_invoiced`
- `unit_price_ht`
- `line_discount_ht`
- `invoice_ts` (nullable)
- `is_cancelled`
- `updated_at`

Une ligne porte au maximum une facture dans le socle.
Les livraisons et facturations fractionnées sont hors socle.
`qty_invoiced` peut être inférieure à `qty_ordered`.
Les commandes en attente ne créent pas de revenu.

### 5.3 `returns`

- Format : JSONL
- Grain : un événement de retour.
- Clé : `return_id` + `source_version`.

Champs minimaux :
- `return_id`
- `source_version`
- `order_id`
- `line_id`
- `return_ts`
- `qty_returned`
- `refund_ht`
- `restocked`
- `status`
- `updated_at`

### 5.4 `crm_customers`

- Format : CSV
- Grain : état courant complet d'un client.
- Clé : `customer_id`.

Champs minimaux :
- `customer_id`
- `country`
- `segment`
- `signup_date`
- `email_synthetic`
- `updated_at`

`crm_customers` représente l'état courant.
Il ne doit pas être utilisé pour inventer un historique métier passé.

### 5.5 `customer_segment_events`

- Format : JSONL
- Grain : un événement métier de segment.
- Clé : `event_id`.

Champs minimaux :
- `event_id`
- `customer_id`
- `segment`
- `effective_from`
- `source_version`
- `recorded_at`

Les événements décrivent la temporalité métier des segments.

### 5.6 `product_versions`

- Format : Parquet
- Grain : une version métier d'un produit.
- Clé : `product_id` + `effective_from`.

Champs minimaux :
- `product_id`
- `effective_from`
- `family_id`
- `label`
- `unit_cost`
- `cost_currency`
- `effective_to` (nullable)
- `updated_at`

Les périodes de validité sont de la forme
`[effective_from, effective_to[`.
Une fin nulle signifie que la période est ouverte.

Les 1 000 références appartiennent à six familles.
Les noms des six familles sont choisis par le groupe.

### 5.7 `stores`

- Format : CSV
- Grain : un magasin ou une entité de vente et de stock.
- Clé : `store_id`.

Champs minimaux :
- `store_id`
- `country`
- `timezone`
- `opening_date`
- `closing_date` (nullable)
- `label`

Le périmètre comprend 12 entités.
Le site web est représenté par un canal ; les commandes web possèdent
un `store_id` correspondant au magasin ou centre qui porte la vente
et le stock. Un centre dédié peut faire partie des 12 entités.

## 6. Sources logistiques et financières

### 6.1 `opening_stock`

- Format : CSV
- Grain : produit × magasin au 2024-08-31.
- Clé : `product_id` + `store_id`.

Champs minimaux :
- `product_id`
- `store_id`
- `opening_qty`
- `opening_ts`

Le stock d'ouverture couvre les combinaisons produit-magasin actives
utilisées par les mouvements.

### 6.2 `stock_movements`

- Format : CSV
- Grain : un mouvement de stock.
- Clé : `movement_id` + `source_version`.

Champs minimaux :
- `movement_id`
- `source_version`
- `product_id`
- `store_id`
- `movement_ts`
- `movement_type`
- `qty_signed`
- `related_order_id` (nullable)
- `related_return_id` (nullable)
- `updated_at`

### 6.3 `stock_counts`

- Format : Parquet
- Grain : un comptage observé produit × magasin × date.

Champs minimaux :
- `product_id`
- `store_id`
- `observed_qty`
- `count_ts`
- `updated_at`

Les comptages sont des observations indépendantes.
Ils ne remplacent pas silencieusement les mouvements de stock.

Pour STANDARD, limiter le catalogue actif à environ 1 500 couples
produit-magasin répartis entre les 12 magasins.
Les jours sans mouvement doivent rester reconstructibles.

### 6.4 `fx_rates`

- Format : CSV
- Grain : devise × date de validité.
- Clé : `currency` + `rate_date`.

Champs minimaux :
- `currency`
- `rate_date`
- `eur_per_unit`
- `updated_at`

EUR vaut 1 ; l'absence d'une ligne de taux EUR est normale.
Deux taux contradictoires pour la même devise et le même jour
constituent une anomalie critique.

### 6.5 `budgets`

- Format : CSV
- Grain : mois × pays × canal × famille × version.

Champs minimaux :
- `month`
- `country`
- `channel`
- `family`
- `budget_ca_eur`
- `budget_margin_eur`
- `version`
- `approved_at`

### 6.6 `campaign_spend`

- Format : JSONL
- Grain : campagne × date × pays.

Champs minimaux :
- identifiant de campagne
- date
- pays
- `channel`
- `spend`
- `currency`
- `updated_at`

Les noms exacts des champs d'identification de campagne, de date et
de pays doivent être fixés dans le dictionnaire détaillé du groupe.

### 6.7 `calendar`

- Format : dimension générée par dbt (seed)
- Grain : une date.

Champs minimaux :
- date
- `month`
- `quarter`
- `year`
- `comparable_day`

Le calendrier couvre toute la période requise.

## 7. Métadonnées et lots

### 7.1 Métadonnées CDC obligatoires

Les événements CDC contiennent :
- `source_system`
- `entity_key`
- `op` (`I`, `U` ou `D`)
- `source_version`
- `event_ts`
- `ingested_at`
- `batch_id`
- `schema_version`

`source_version` est un entier croissant par clé.

Les sources `orders`, `order_lines` et `returns` sont alimentées
par un FULL initial, puis par CDC.
Un événement CDC apporte une image complète du nouvel état de
l'enregistrement, pas un patch partiel.

Une suppression CDC d'une ligne signifie que la ligne était erronée ;
elle doit être exclue du résultat retraité, sans être interprétée
comme un remboursement.

### 7.2 Métadonnées FULL

Les sources FULL comprennent :
- `batch_id`
- `extracted_at`
- `schema_version`
- checksum du fichier

Une disparition d'un client du CRM ne constitue une suppression
que si le manifeste certifie que le FULL est complet.

### 7.3 Métadonnées de la couche brute

Préserver également :
- `file_name`
- `row_number`
- `record_hash`
- payload d'origine ou représentation réversible

### 7.4 Manifeste de lot

Le manifeste doit décrire :
- identifiant du lot ;
- source ;
- mode FULL ou CDC ;
- version du schéma ;
- nom du fichier ;
- nombre de lignes ;
- checksum ;
- ordre de simulation ;
- anomalies injectées, sans donner leur correction dans les données brutes.

Le FULL initial représente l'état des ventes et événements connus
au 2026-08-31. Il inclut les mouvements de stock depuis l'ouverture
et toutes les périodes produit nécessaires.

## 8. Anomalies à prendre en charge

Le jeu perturbé doit couvrir au minimum ces 15 types :

1. Doublon exact
2. Doublon conflictuel
3. Clé nulle
4. Date invalide
5. Montant mal formé
6. Référence absente
7. Devise inconnue
8. Taux de change absent
9. Événement tardif
10. Événement désordonné
11. Suppression
12. Réactivation
13. Changement de schéma
14. Retour excessif
15. Stock négatif

La qualité du jeu propre doit être vérifiée par des invariants
indépendants. Les anomalies du jeu perturbé doivent être décrites
dans le manifeste.

## 9. Règles métier à respecter en aval

Ces règles guident la conception des données et leur validation.
Elles ne signifient pas que le générateur doit pré-calculer les KPI.

- Une vente est basée sur une ligne facturée, non annulée, de quantité
  facturée strictement positive.
- La date de vente est la date locale de facture.
- Les commandes en attente ne créent pas de revenu.
- La remise de ligne est une remise totale sur la ligne facturée.
- La remise de commande est répartie au prorata des bases positives
  des lignes facturées éligibles.
- Une allocation impossible bloque la commande.
- Les taux de change sont recherchés à la date de facture ; le taux
  antérieur le plus récent est accepté avec un recul maximal de
  sept jours calendaires. Aucun taux futur n'est accepté.
- Les coûts utilisent la version produit valide à la date de facture.
- Les retours acceptés réduisent le chiffre d'affaires net.
- Les quantités retournées ne dépassent pas les quantités facturées.
- Les comptages de stock ne remplacent pas les mouvements.

Les cas chiffrés communs T01 à T10 et leurs résultats attendus sont
définis dans la section 18 du PDF. Ils seront utilisés pour les tests
de recette indépendants.

## 10. Points à confirmer avant le générateur

- Les six noms de familles retenus par le groupe.
- Le nom exact des champs d'identification de campagne, de date et
  de pays pour `campaign_spend`.
- Les colonnes complémentaires et métadonnées par source.
- La stratégie de génération des lots FULL puis CDC.
- Le découpage du profil STANDARD si les ressources disponibles
  nécessitent un allègement validé.


## Décision en attente — familles de produits

Le projet impose 6 familles de produits.
Les identifiants et les libellés restent à valider par le groupe.

- family_id 1 : À définir
- family_id 2 : À définir
- family_id 3 : À définir
- family_id 4 : À définir
- family_id 5 : À définir
- family_id 6 : À définir


Ce document décrit le minimum contractuel issu du PDF.
Toute décision complémentaire du groupe doit être documentée.