# Atlas Retail 360 — Tests de recette MICRO

## Objectif

Préparer des cas isolés et reproductibles avec des résultats attendus indépendants des transformations de production.

Les résultats monétaires sont calculés en décimal.

## Cas définis par le PDF

| ID | Cas | Résultat attendu |
|---|---|---|
| T01 | Remise globale | Bases 180 et 50 ; allocations 18 et 5 ; ventes 162 et 45 ; CA 207 ; coût 140 ; marge 67 |
| T02 | Retour restocké | Retour : CA -81, coût net -60, marge -21 ; cumul : CA 126, coût net 80, marge 46 |
| T03 | Retour non restocké | Cumul : CA 126, coût net 140, marge -14 |
| T04 | Conversion CHF vers EUR | CA 105 EUR ; coût 63 EUR ; marge 42 EUR |
| T05 | Stock | Stock final 12 ; rejouer les mêmes mouvements ne change pas le résultat |
| T06 | Annulation | CA et coût exclus ; anomalie de cohérence signalée |
| T07 | CDC reçu dans le désordre | Version 3 retenue, prix courant 120 ; une seule ligne métier |
| T08 | Budget | CA 100 ; budget 200 ; atteinte 50 % |
| T09 | Validité historique du coût | Coût 100 ; CA 160 ; marge 60 ; une seule version produit jointe |
| T10 | Taux de change hors délai | Pas de CA EUR certifié ; rejet ou attente de valorisation ; montant source conservé |

## Points à compléter

- Ajouter au moins six oracles conçus par le groupe, conformément au PDF.
- Définir leurs entrées et résultats attendus avant d'écrire les tests.
- Ne pas utiliser les calculs de production comme seule référence des tests.
- Ne pas inventer de données de contrat manquantes : documenter les décisions en attente.

## État

- [ ] Fixtures T01 à T10 créées
- [ ] Résultats attendus vérifiés
- [ ] Tests automatisés exécutés
- [ ] Six oracles supplémentaires définis
