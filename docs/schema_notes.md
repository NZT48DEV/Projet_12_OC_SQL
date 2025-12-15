# Schéma de base de données — Notes de conception

## Entités
- employees : collaborateurs (gestion, commercial, support)
- clients : clients suivis par un commercial
- contracts : contrats associés à un client et un commercial
- events : événements associés à un contrat, avec support optionnel

## Relations (logique métier)
- employees (commercial) 1 → N clients : un commercial gère plusieurs clients
- clients 1 → N contracts : un client peut avoir plusieurs contrats
- contracts 1 → N events : un contrat peut couvrir plusieurs événements (choix de conception)
- employees (support) 1 → N events : un support peut gérer plusieurs événements
  - support_contact_id est nullable : un événement peut ne pas avoir de support assigné

## Clés étrangères
- clients.sales_contact_id → employees.id
- contracts.client_id → clients.id
- contracts.sales_contact_id → employees.id
- events.contract_id → contracts.id
- events.client_id → clients.id
- events.support_contact_id → employees.id (nullable)

## Remarques sécurité (à implémenter côté application)
- mots de passe stockés uniquement sous forme de hash
- accès aux données limité selon le rôle (moindre privilège)
