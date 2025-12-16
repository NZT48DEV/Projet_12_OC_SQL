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

Le projet utilise un **compte non privilégié** pour l’application.

À créer côté PostgreSQL :
- Utilisateur : `epic_crm_app`
- Base de données : `epic_crm`
- Propriétaire / droits : `epic_crm_app`

> 🔐 Principe du moindre privilège :
> l’application n’utilise **jamais** le compte administrateur `postgres`.

---

## Variables d’environnement

Créer un fichier `.env` à la racine du projet :

```env
DATABASE_URL=postgresql+psycopg://epic_crm_app:VOTRE_MOT_DE_PASSE@localhost:5432/epic_crm
SENTRY_DSN=
```

⚠️ Les caractères spéciaux dans le mot de passe doivent être **encodés** (URL encoding).

Un fichier `.env.example` est fourni.

---

## Base de données & migrations

Le schéma est géré via **SQLAlchemy + Alembic**.

### Modèles ORM implémentés
- `Employee`
- `Client`
- `Contract`
- `Event`

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

## Vérification rapide

```bash
pipenv run python -m app.main
```

Résultat attendu :
```
Connected to database 'epic_crm' as user 'epic_crm_app'
```

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
└── README.md
```

---

## Documentation

- ERD : `docs/erd.mmd`
- Notes de conception : `docs/schema_notes.md`

---

## État du projet

- ✔️ Environnement Python et PostgreSQL opérationnels
- ✔️ ORM SQLAlchemy en place
- ✔️ Migrations Alembic fonctionnelles
- ✔️ Modèles et relations conformes à l’ERD
- ✔️ Séparation claire admin / applicatif

👉 **Prochaine étape** : implémentation de la CLI, de l’authentification et des permissions par rôle.
