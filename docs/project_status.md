## État du projet — Epic Events CRM

### Infrastructure & données
- ✔️ Environnement **Python 3.11+** et **PostgreSQL** correctement configuré
- ✔️ Bases de données **développement** et **test** séparées et fonctionnelles
- ✔️ Utilisateur PostgreSQL **non privilégié** avec droits limités
- ✔️ ORM **SQLAlchemy** opérationnel
- ✔️ Migrations **Alembic** fonctionnelles (schéma versionné)
- ✔️ Modèles et relations conformes à l’ERD et au cahier des charges
- ✔️ Séparation claire entre administration de la base et usage applicatif

---

### Sécurité & authentification
- ✔️ Authentification **JWT** fonctionnelle en CLI (access + refresh tokens)
- ✔️ Stockage local sécurisé des tokens (keyring avec fallback fichier)
- ✔️ Rotation des refresh tokens
- ✔️ Autorisation centralisée par rôle :
  - `MANAGEMENT`
  - `SALES`
  - `SUPPORT`
- ✔️ Mécanisme de **bootstrap sécurisé** pour le premier compte MANAGEMENT

---

### Fonctionnalités métier implémentées

#### Clients
- ✔️ Lecture sécurisée des clients (`clients list`)
- ✔️ Création de clients (`clients create`)
- ✔️ Mise à jour des clients (`clients update`)
- ✔️ Règles d’accès :
  - `SUPPORT` : accès interdit
  - `SALES` : modification limitée à ses propres clients
  - `MANAGEMENT` : modification de tous les clients
- ✔️ Contraintes métier :
  - email unique
  - champs obligatoires non vides

---

#### Contrats
- ✔️ Lecture sécurisée des contrats (`contracts list`)
- ✔️ Création de contrats (`contracts create`)
  - autorisée pour les rôles `SALES` et `MANAGEMENT`
- ✔️ Signature des contrats (`contracts sign`)
  - autorisée **uniquement** pour le rôle `MANAGEMENT`
- ✔️ Mise à jour des contrats (`contracts update`)
  - autorisée pour `SALES` (périmètre restreint) et `MANAGEMENT`
- ✔️ Règles métier validées :
  - montants strictement positifs
  - cohérence `amount_due ≤ total_amount`
  - impossibilité de modifier la signature via update

---

#### Événements
- ✔️ Lecture sécurisée des événements (`events list`)
- ✔️ Création d’événements (`events create`)
  - autorisée pour `SALES`
  - contrat signé requis
- ✔️ Mise à jour des événements (`events update`)
  - `SUPPORT` : uniquement les événements assignés
  - `MANAGEMENT` : tous les événements + assignation support
  - `SALES` : accès interdit
- ✔️ Règles métier validées :
  - cohérence des dates (start < end)
  - participants ≥ 0
  - lieu obligatoire

---

### Qualité & intégration continue
- ✔️ Tests unitaires complets sur la couche **services** (CRUD)
- ✔️ Tests unitaires sur la couche **CLI** (commandes isolées)
- ✔️ Tests d’intégration CLI (`main`, argparse, JWT, DB)
- ✔️ Tests d’intégration DB (contraintes SQL : NOT NULL, UNIQUE, FK, ENUM)
- ✔️ Pipeline **CI GitHub Actions** fonctionnel :
  - linting (pre-commit)
  - exécution des tests unitaires et d’intégration
  - base PostgreSQL éphémère pour l’intégration
- ✔️ Architecture respectant strictement la séparation :
  - CLI (interface)
  - Services (règles métier)
  - Repositories (accès aux données)

---

👉 **Prochaines étapes prévues**
  - Implémentation des fonctionnalités **DELETE** sur les entités métier
  - Intégration de **Sentry** pour le monitoring et le suivi d’erreurs
