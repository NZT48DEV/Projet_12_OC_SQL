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
- ✔️ Désactivation d’employé via **soft delete** (`is_active = false`)

---

### Fonctionnalités métier implémentées

#### Employés
- ✔️ Création d’employés
- ✔️ Lecture sécurisée
- ✔️ Désactivation / réactivation (soft delete)
- ✔️ Suppression contrôlée (refus si références)
- ✔️ Suppression définitive (**hard delete**) sécurisée

#### Clients
- ✔️ CRUD complet
- ✔️ Réassignation client (cascade contrats)
- ✔️ Règles d’accès strictes par rôle

#### Contrats
- ✔️ CRUD + signature
- ✔️ Réassignation contrat
- ✔️ Validations métier complètes

#### Événements
- ✔️ CRUD complet
- ✔️ Réassignation du support
- ✔️ Règles d’accès et validations métier

---

### Qualité, tests & CI
- ✔️ Tests unitaires services (clients / contrats / events)
- ✔️ Tests CLI
- ✔️ Tests d’intégration DB
- ✔️ CI GitHub Actions fonctionnelle

---

### Observabilité & monitoring

#### Sentry (prochaine étape)
- Intégration de **Sentry** pour le suivi des erreurs runtime
- Capture automatique des exceptions non gérées (CLI & services)
- Enrichissement du contexte :
  - utilisateur connecté
  - rôle
  - commande CLI exécutée
- Séparation des environnements (dev / test / prod)
- Désactivation automatique en environnement de test

👉 **Prochaine étape planifiée : intégration de Sentry pour améliorer l’observabilité et la robustesse du projet.**
