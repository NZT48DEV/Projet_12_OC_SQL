# Epic Events CRM
**Back-end Python • PostgreSQL • SQLAlchemy • Alembic**

![CI](https://github.com/NZT48DEV/Projet_12_OC_SQL/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue?logo=postgresql)

CRM interne sécurisé pour gérer les **clients**, **contrats** et **événements** d’Epic Events.

Ce projet met en place une **architecture back-end robuste** avec Python et PostgreSQL, en appliquant :
- une modélisation relationnelle (ERD),
- le principe du moindre privilège,
- un ORM (SQLAlchemy),
- des migrations versionnées (Alembic),
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


## Configuration PostgreSQL

Le projet utilise un **compte applicatif non privilégié**, conformément aux bonnes pratiques de sécurité.

### Mise en place de la base de données

- Création d’un utilisateur applicatif PostgreSQL :
  - Nom : `epic_crm_app`
  - Rôle : non superuser

- Création de bases de données dédiées :
  - **Base de développement** : `epic_crm`
  - **Base de test** : `epic_crm_test`
  - Réalisées avec un compte administrateur (`postgres`)

- Attribution des droits nécessaires à l’utilisateur applicatif :
  - Connexion aux bases
  - Création et gestion des tables
  - Exécution des migrations Alembic
  - Utilisation dans les tests automatisés (pytest)

Exemples de droits accordés :

```sql
-- Bases de données
GRANT ALL PRIVILEGES ON DATABASE epic_crm TO epic_crm_app;
GRANT ALL PRIVILEGES ON DATABASE epic_crm_test TO epic_crm_app;

-- Schéma public
GRANT USAGE, CREATE ON SCHEMA public TO epic_crm_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO epic_crm_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO epic_crm_app;
```

> ⚠️ L’utilisateur `postgres` est utilisé uniquement pour l’installation initiale.
> L’application, les migrations **et les tests automatisés** utilisent exclusivement `epic_crm_app`.

---

## Variables d’environnement

Les informations de connexion à la base de données ne sont **jamais stockées en dur** dans le code.

Créer un fichier `.env` à la racine du projet :

```env
# Base de données (développement / production)
DATABASE_URL=postgresql+psycopg://epic_crm_app:VOTRE_MOT_DE_PASSE@localhost:5432/epic_crm

# Base de données de test (utilisée par pytest)
DATABASE_URL_TEST=postgresql+psycopg://epic_crm_app:VOTRE_MOT_DE_PASSE@localhost:5432/epic_crm_test

# JWT
EPICCRM_JWT_SECRET=VOTRE_CLE_SECRETE_JWT
EPICCRM_JWT_ACCESS_MINUTES=20
EPICCRM_JWT_REFRESH_DAYS=7
EPICCRM_JWT_ALG=HS256
EPICCRM_JWT_ROTATE_REFRESH=true
```

- La base **`epic_crm`** est utilisée en développement et en production
- La base **`epic_crm_test`** est utilisée exclusivement lors de l’exécution des tests
- Les tests ne modifient jamais les données de la base de développement

⚠️ Les caractères spéciaux du mot de passe doivent être encodés (URL encoding).

---

## Base de données et migrations

Le schéma de la base de données est géré via **SQLAlchemy** et **Alembic**.

Une migration initiale a été générée automatiquement à partir des modèles ORM :

```bash
alembic revision --autogenerate -m "Schema initial"
alembic upgrade head
```

Cette migration crée :
- les tables `employees`, `clients`, `contracts`, `events`
- les clés primaires
- les clés étrangères
- les contraintes UNIQUE nommées

---

### Relations principales
- `Client.sales_contact_id -> Employee.id`
- `Contract.client_id -> Client.id`
- `Contract.sales_contact_id -> Employee.id`
- `Event.contract_id -> Contract.id`
- `Event.client_id -> Client.id`
- `Event.support_contact_id -> Employee.id` (nullable)

Les timestamps sont stockés en **UTC**.

### Commandes Alembic
```bash
pipenv run alembic revision --autogenerate -m "description"
pipenv run alembic upgrade head
```

---

## Authentification et autorisation (CLI – JWT)

L’application utilise une **authentification basée sur des jetons JWT**, adaptée à une interface en ligne de commande (CLI), tout en respectant les bonnes pratiques de sécurité.

### Principes généraux
- Authentification par **email + mot de passe**
- Mots de passe **hachés** (jamais stockés en clair)
- Utilisation de **JSON Web Tokens (JWT)** pour l’authentification
- Deux types de jetons :
  - **Access token** (courte durée)
  - **Refresh token** (durée plus longue)
- Les jetons sont stockés **localement** sur la machine de l’utilisateur, de manière sécurisée

---

### Cycle de vie des tokens

- **Access token**
  - Durée de validité : **20 minutes**
  - Utilisé pour authentifier chaque commande protégée
  - Contient l’identifiant de l’utilisateur et son rôle

- **Refresh token**
  - Durée de validité plus longue
  - Permet de régénérer un nouvel access token sans se reconnecter
  - Rotation automatique lors du rafraîchissement

---

### Stockage sécurisé des tokens (CLI)

Le stockage des tokens suit une stratégie **sécurisée avec repli automatique** :

#### 1. Coffre sécurisé du système (prioritaire)
Lorsque cela est possible, les tokens sont stockés dans le **coffre sécurisé du système d’exploitation** via la bibliothèque `keyring` :
- Windows : Credential Manager
- macOS : Keychain
- Linux : Secret Service

Dans ce cas :
- Les tokens **ne sont jamais écrits en clair sur le disque**
- Le chiffrement est géré par l’OS
- Les tokens sont accessibles uniquement à l’utilisateur courant

#### 2. Fallback fichier local (si keyring indisponible)
Si le coffre sécurisé n’est pas disponible, l’application utilise un stockage de secours :

```text
~/.epiccrm/tokens.json
```

---

### Variables d’environnement JWT

Le secret JWT doit être fourni via une variable d’environnement.

Dans le fichier `.env` :

```env
EPICCRM_JWT_SECRET=VOTRE_SECRET_JWT
```

- Le secret doit être **long**, **aléatoire** et **confidentiel**
- Il n’est jamais versionné dans le dépôt Git
- En CI (GitHub Actions), il est fourni via les **Secrets GitHub**

---

### Commandes CLI liées à l’authentification

#### Connexion
```bash
python -m app.epicevents login <email> <password>
```

- Génère un access token et un refresh token
- Stocke les tokens localement

#### Afficher l’utilisateur courant
```bash
python -m app.epicevents whoami
```

- Vérifie la validité de l’access token
- Affiche l’identité et le rôle de l’utilisateur connecté

#### Rafraîchir le token
```bash
python -m app.epicevents refresh-token
```

- Utilise le refresh token pour générer un nouvel access token
- Rotation du refresh token

#### Déconnexion
```bash
python -m app.epicevents logout
```

- Supprime les tokens locaux
- Nécessite une reconnexion complète

---

### Autorisation par rôle

Les commandes sensibles sont protégées par un système de rôles :

- `MANAGEMENT`
- `SALES`
- `SUPPORT`

Un mécanisme d’autorisation centralisé vérifie :
- l’authentification via JWT
- le rôle de l’utilisateur

Exemple :
```bash
python -m app.epicevents management-only
```

Cette commande est accessible **uniquement** aux utilisateurs ayant le rôle `MANAGEMENT`.

---

### Bootstrap du premier compte

Afin d’éviter un système bloquant lors de la première installation :

- Si **aucun employé n’existe en base**, la création du **premier compte MANAGEMENT** est autorisée sans authentification
- Dès qu’un premier employé existe :
  - toutes les créations d’employés nécessitent une authentification
  - le rôle `MANAGEMENT` est requis

Exemple :
```bash
python -m app.epicevents create-employee Anthony Test admin@epiccrm.com Secret123! MANAGEMENT
```

---

### Sécurité et bonnes pratiques

- Les JWT ont une durée de vie courte
- Les refresh tokens sont rotatifs
- Les secrets sont fournis par variables d’environnement
- Les accès sont strictement contrôlés par rôle
- Le mécanisme est compatible CI/CD et environnements multiples

---

## Qualité de code

Outils utilisés :
- black
- isort
- flake8
- pre-commit
- pytest

Installation des hooks :
```bash
pre-commit install
```

---

## Intégration Continue (CI)

Une **CI GitHub Actions** est configurée.

À chaque push ou pull request :
- vérification du style (pre-commit),
- exécution des tests,
- démarrage d’un service PostgreSQL pour les tests d’intégration.

---

## Architecture du projet

```
.
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI GitHub Actions (lint + tests + PostgreSQL)
├── app/
│   ├── __init__.py
│   ├── epicevents.py              # Point d’entrée CLI (argparse)
│   ├── cli/                       # Interface en ligne de commande
│   │   ├── __init__.py
│   │   └── commands.py
│   ├── core/                      # Sécurité, JWT, configuration, logging
│   │   ├── authorization.py
│   │   ├── jwt_service.py
│   │   ├── security.py
│   │   └── token_store.py
│   ├── db/                        # Gestion base de données (SQLAlchemy)
│   │   ├── base.py                # Déclaration Base ORM
│   │   ├── config.py              # Chargement DATABASE_URL
│   │   ├── engine.py              # Création de l'engine SQLAlchemy
│   │   ├── session.py             # SessionLocal
│   │   ├── init_db.py             # Initialisation DB
│   │   └── db_check_sqlalchemy.py # Vérifications de cohérence
│   ├── models/                    # Modèles ORM
│   │   ├── employee.py
│   │   ├── client.py
│   │   ├── contract.py
│   │   └── event.py
│   ├── repositories/              # Accès aux données (DAL)
│   │   ├── employee_repository.py
│   │   ├── client_repository.py
│   │   ├── contract_repository.py
│   │   └── event_repository.py
│   └── services/                  # Logique métier
│       ├── auth_service.py
│       ├── client_service.py
│       ├── contract_service.py
│       ├── current_employee.py
│       └── event_service.py
├── migrations/                    # Migrations Alembic
│   └── versions/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── functional/
├── docs/
│   ├── erd.mmd                    # Schéma ERD
│   └── schema_notes.md            # Notes de conception
├── htmlcov/
│   └── index.html                 # Rapport de couverture pytest
├── .env.example                   # Modèle de configuration (sans secrets)
├── .flake8
├── .gitignore
├── .pre-commit-config.yaml
├── alembic.ini
├── Pipfile
├── Pipfile.lock
├── pyproject.toml
├── pytest.ini
└── README.md
```

---

## Documentation

- ERD : `docs/erd.mmd`
- Notes de conception : `docs/schema_notes.md`

---

## État du projet

- ✔️ Environnement Python et PostgreSQL correctement configuré
- ✔️ Bases de données **développement** et **test** séparées et fonctionnelles
- ✔️ Utilisateur applicatif PostgreSQL non privilégié avec les droits appropriés
- ✔️ ORM SQLAlchemy opérationnel
- ✔️ Migrations Alembic fonctionnelles (schéma versionné)
- ✔️ Modèles et relations conformes à l’ERD et au cahier des charges
- ✔️ Séparation claire entre administration de la base et usage applicatif
- ✔️ Authentification **JWT** fonctionnelle en CLI (access + refresh tokens)
- ✔️ Stockage local sécurisé des tokens
- ✔️ Autorisation par rôle implémentée (MANAGEMENT / SALES / SUPPORT)
- ✔️ Mécanisme de **bootstrap** pour le premier compte MANAGEMENT
- ✔️ Tests unitaires et tests d’intégration automatisés (pytest + PostgreSQL)
- ✔️ Pipeline CI fonctionnel (lint, tests, base PostgreSQL)

👉 **Prochaine étape** : implémentation complète des fonctionnalités métier
(**clients**, **contrats**, **événements**) avec application stricte des règles d’autorisation et des contraintes métier.
