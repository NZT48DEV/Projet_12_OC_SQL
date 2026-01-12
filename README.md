# Epic Events CRM
**Back-end Python • PostgreSQL • SQLAlchemy • Alembic**

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue?logo=postgresql)
![Migrations](https://img.shields.io/badge/migrations-Alembic-blueviolet)
![ORM](https://img.shields.io/badge/ORM-SQLAlchemy-red)
![CLI](https://img.shields.io/badge/CLI-Click%20%2B%20Rich-yellow)
![Auth](https://img.shields.io/badge/auth-JWT-orange)
![CI](https://github.com/NZT48DEV/Projet_12_OC_SQL/actions/workflows/ci.yml/badge.svg)
![Tests](https://img.shields.io/badge/tests-pytest-green)
![Coverage](https://codecov.io/gh/NZT48DEV/Projet_12_OC_SQL/branch/master/graph/badge.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Linting](https://img.shields.io/badge/lint-flake8-blue)
![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen)


CRM interne sécurisé pour gérer les **clients**, **contrats** et **événements** d’Epic Events.

Ce projet met en place une **architecture back-end robuste** avec Python et PostgreSQL, en appliquant :
- une modélisation relationnelle (ERD),
- le principe du moindre privilège,
- un ORM (SQLAlchemy),
- des migrations versionnées (Alembic),
- une CLI moderne avec **Click** et **Rich**,
- et de bonnes pratiques de qualité logicielle.

---

## Prérequis

- Python **3.11+**
- Pipenv
- PostgreSQL **14+**
- (Recommandé) pgAdmin 4
- Git

---

## Installation

```bash
git clone https://github.com/NZT48DEV/Projet_12_OC_SQL.git
cd Projet_12_OC_SQL
pipenv install --dev
pipenv shell
```

---

## Dépendances externes

Le projet nécessite un serveur **PostgreSQL** en fonctionnement.

- PostgreSQL **14+**
- Deux bases de données :
  - `epic_crm` (développement / production)
  - `epic_crm_test` (tests automatisés)
- Un utilisateur applicatif PostgreSQL non privilégié

> La configuration détaillée de PostgreSQL (droits, rôles, migrations)
> est décrite dans [`docs/database.md`](docs/database.md).

---

## Configuration (.env)

Avant de lancer l’application, créer un fichier `.env` à la racine du projet.

Exemple :

```bash
# Base de données (développement / production)
DATABASE_URL=postgresql+psycopg://epic_crm_app:VOTRE_MOT_DE_PASSE@localhost:5432/epic_crm

# Base de données de test (utilisée par pytest)
DATABASE_URL_TEST=postgresql+psycopg://epic_crm_app:VOTRE_MOT_DE_PASSE@localhost:5432/epic_crm_test

# Sentry (monitoring & suivi des erreurs)
SENTRY_DSN=https://<votre-dsn-sentry>
SENTRY_ENVIRONMENT=development
SENTRY_RELEASE=epic-events@1.0.0

# JWT
EPICCRM_JWT_SECRET=VOTRE_CLE_SECRETE_JWT
EPICCRM_JWT_ACCESS_MINUTES=20
EPICCRM_JWT_REFRESH_DAYS=7
EPICCRM_JWT_ALG=HS256
EPICCRM_JWT_ROTATE_REFRESH=true
```

Les variables détaillées et les bonnes pratiques de sécurité sont décrites dans [`docs/database.md`](docs/database.md).

La configuration complète de la journalisation et du monitoring avec Sentry est documentée dans [`docs/observability.md`](docs/observability.md).


---

## Démarrage rapide

⚠️ Le premier employé créé doit obligatoirement avoir le rôle MANAGEMENT.
Ce mécanisme de bootstrap garantit qu’aucun compte non privilégié ne puisse initialiser le système.


```bash
alembic upgrade head
epicevents create-employee John Doe johndoe@test.com Secret123! MANAGEMENT
epicevents login johndoe@test.com Secret123!
epicevents clients list
```

---

## Documentation

### PostgreSQL + Alembic : [`docs/database.md`](docs/database.md)
- Configuration PostgreSQL (utilisateur applicatif)
- Bases dev / test
- Variables d’environnement
- Migrations Alembic

---

### Commandes CLI : [`docs/cli.md`](docs/cli.md)
- Toutes les commandes sont exécutées via l’interface CLI `epicevents`.
- Une authentification valide est requise pour toute commande métier.

---

### JWT + rôles : [`docs/authentication.md`](docs/authentication.md)
- Vol de mot de passe → hash + jamais stocké en clair
- Token expiré → durée courte + refresh token
- Usurpation de rôle → rôle vérifié à chaque commande
- Fuite de secret → variables d’environnement uniquement

---

### Architecture du projet : [`docs/architecture.md`](docs/architecture.md)

#### Principes d’architecture
- Les modèles décrivent uniquement la structure des données.
- Les repositories encapsulent l’accès à la base de données.
- Les services portent la logique métier.
- Le module core centralise la sécurité (JWT, autorisations).
- La CLI ne contient aucune logique métier.

---

### Qualité code + CI : [`docs/quality_ci.md`](docs/quality_ci.md)
- Vérification du respect PEP8
- Détection précoce des régressions

---

### Modélisation - ERD : [`docs/erd.mmd`](docs/erd.mmd)
- Diagramme ERD illustrant la structure relationnelle de la base de données du projet Epic Events.

---

### Notes de conception : [`docs/schema_notes.md`](docs/schema_notes.md)
#### Choix de conception notables
- Un contrat peut couvrir plusieurs événements (choix métier).
- Un événement peut exister sans support assigné.

---

### Observabilité & monitoring : [`docs/observability.md`](docs/observability.md)
- Suivi des erreurs runtime avec Sentry
- Capture centralisée des exceptions
- Gestion des environnements dev / test / prod

---

### Etat d'avancement du projet : [`docs/project_status.md`](docs/project_status.md)

---
