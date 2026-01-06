# Observabilité & monitoring

## Objectif
Assurer la traçabilité des erreurs runtime et améliorer la robustesse du projet.

## Sentry
- capture automatique des exceptions non gérées
- intégration dans les commandes CLI
- enrichissement du contexte (utilisateur, rôle, commande)
- désactivation automatique en environnement de test

## Tests
- tests unitaires validant la capture des erreurs
- aucun appel réseau réel lors des tests

## Bénéfices
- détection rapide des erreurs en production
- meilleure maintenabilité
- séparation claire dev / test / prod
