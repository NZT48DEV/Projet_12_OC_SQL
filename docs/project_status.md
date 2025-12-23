## État du projet

- ✔️ Environnement Python et PostgreSQL correctement configuré
- ✔️ Bases de données **développement** et **test** séparées et fonctionnelles
- ✔️ Utilisateur applicatif PostgreSQL **non privilégié** avec les droits appropriés
- ✔️ ORM **SQLAlchemy** opérationnel
- ✔️ Migrations **Alembic** fonctionnelles (schéma versionné)
- ✔️ Modèles et relations conformes à l’ERD et au cahier des charges
- ✔️ Séparation claire entre administration de la base et usage applicatif

### Sécurité & authentification
- ✔️ Authentification **JWT** fonctionnelle en CLI (access + refresh tokens)
- ✔️ Stockage local sécurisé des tokens (keyring avec fallback fichier)
- ✔️ Rotation des refresh tokens
- ✔️ Autorisation centralisée par rôle (**MANAGEMENT / SALES / SUPPORT**)
- ✔️ Mécanisme de **bootstrap sécurisé** pour le premier compte MANAGEMENT

### Fonctionnalités métier – lecture sécurisée
- ✔️ Lecture sécurisée des **clients** (`clients list`)
- ✔️ Lecture sécurisée des **contrats** (`contracts list`)
- ✔️ Lecture sécurisée des **événements** (`events list`)
- ✔️ Accès conditionné à une authentification valide (JWT)
- ✔️ Aucune modification possible via les commandes de lecture

### Qualité & intégration continue
- ✔️ Tests unitaires et tests d’intégration automatisés (**pytest + PostgreSQL**)
- ✔️ Pipeline **CI GitHub Actions** fonctionnel :
  - linting (pre-commit)
  - exécution des tests
  - base PostgreSQL éphémère pour l’intégration

---

👉 **Prochaine étape** :
implémentation des fonctionnalités **CREATE / UPDATE / DELETE** sur les entités métier
(**clients**, **contrats**, **événements**), avec :
- application stricte des règles d’autorisation par rôle,
- validation des données,
- respect du principe du moindre privilège.

---
