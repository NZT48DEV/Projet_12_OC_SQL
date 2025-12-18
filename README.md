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

- Création d’une base de données dédiée :
  - Nom : `epic_crm`
  - Réalisée avec un compte administrateur (`postgres`)

- Attribution des droits nécessaires à l’utilisateur applicatif :
  - Connexion à la base
  - Création et gestion des tables
  - Exécution des migrations Alembic

Exemples de droits accordés :

```sql
GRANT ALL PRIVILEGES ON DATABASE epic_crm TO epic_crm_app;
GRANT ALL ON SCHEMA public TO epic_crm_app;
```

> ⚠️ L’utilisateur `postgres` est utilisé uniquement pour l’installation initiale.
> L’application et les migrations utilisent exclusivement `epic_crm_app`.

---

## Variables d’environnement

Les informations de connexion à la base de données ne sont **jamais stockées en dur** dans le code.

Créer un fichier `.env` à la racine du projet :

```env
DATABASE_URL=postgresql+psycopg://epic_crm_app:VOTRE_MOT_DE_PASSE@localhost:5432/epic_crm
```

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

## Authentification et autorisation (CLI)

L’application implémente une authentification sécurisée adaptée à une interface en ligne de commande (CLI).

### Authentification
- Authentification par **email + mot de passe**
- Mots de passe **hachés** (jamais stockés en clair)
- Vérification centralisée via un service métier dédié
- Authentification persistante via un **stockage de session local**

### Gestion de session
- La session est stockée dans un fichier local : `~/.epiccrm/session.json`
- Le fichier contient uniquement l’**identifiant de l’utilisateur**
- Aucune donnée sensible (mot de passe, rôle en clair) n’est stockée
- Déconnexion explicite possible
- Les sessions invalides sont automatiquement nettoyées

### Autorisation (rôles)
Les actions sont protégées par un système de rôles :
- `MANAGEMENT`
- `SALES`
- `SUPPORT`

Un mécanisme d’autorisation centralisé permet de restreindre certaines commandes
(exemple : commandes réservées au rôle `MANAGEMENT`).

### Exemples de commandes CLI
```bash
python -m app.epicevents login <email> <password>
python -m app.epicevents whoami
python -m app.epicevents management-only
python -m app.epicevents logout
```

> Le choix d’un stockage de session local est volontaire pour une application CLI.
> Une implémentation basée sur des jetons JWT est envisagée comme évolution ultérieure.

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
│       └── ci.yml                 # CI GitHub Actions (lint + tests + postgres)
├── app/
│   ├── __init__.py
│   ├── main.py                    # point d’entrée (smoke test / lancement)
│   ├── core/                      # configuration, sécurité, logging
│   ├── db/                        # connexion DB + base ORM
│   ├── models/                    # modèles ORM (Employee, Client, Contract, Event)
│   ├── repositories/              # accès aux données (DAL)
│   ├── services/                  # logique métier (auth, règles, permissions)
│   └── cli/                       # interface en ligne de commande
├── db/
│   └── 01_schema.sql              # schéma SQL (à implémenter à partir de l'ERD)
├── docs/
│   ├── erd.mmd                    # schéma ERD
│   └── schema_notes.md            # notes de conception
├── htmlcov/
│   └── index.html                 # Coverage HTML
├── migrations/
│   └── versions/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── functional/
├── .env.example                   # modèle (sans secrets)
├── .flake8                        # config flake8
├── .gitignore
├── .pre-commit-config.yaml        # config pre-commit
├── alembic.ini
├── Pipfile
├── Pipfile.lock
├── pyproject.toml                 # config black/isort
├── pytest.ini                     # config pytest
└── README.md
```

---

## Documentation

- ERD : `docs/erd.mmd`
- Notes de conception : `docs/schema_notes.md`

---

## État du projet

- ✔️ Environnement Python et PostgreSQL correctement configuré
- ✔️ Base de données PostgreSQL fonctionnelle et accessible
- ✔️ Utilisateur applicatif non privilégié avec les droits appropriés
- ✔️ ORM SQLAlchemy opérationnel
- ✔️ Migrations Alembic fonctionnelles (schéma versionné)
- ✔️ Modèles et relations conformes à l’ERD et au cahier des charges
- ✔️ Séparation claire entre administration de la base et usage applicatif
- ✔️ Authentification persistante (CLI)
- ✔️ Autorisation par rôle implémentée
- ✔️ Tests unitaires et tests d’intégration en place


👉 **Prochaine étape** : évolution du mécanisme d’authentification vers une solution basée sur des jetons JWT, avant l’implémentation des fonctionnalités métier (**clients**, **contrats**, **événements**).
