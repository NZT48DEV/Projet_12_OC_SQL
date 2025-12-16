# Epic Events CRM (Back-end Python + PostgreSQL)

![CI](https://github.com/NZT48DEV/Projet_12_OC_SQL/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue?logo=postgresql)

CRM interne sécurisé pour gérer les clients, contrats et événements d’Epic Events.

Ce projet met en place une architecture back-end sécurisée avec Python et PostgreSQL,
en appliquant les bonnes pratiques de modélisation, de sécurité et de qualité logicielle.

---

## Prérequis

- Python **3.11+**
- Pipenv
- PostgreSQL **14+**
- (Optionnel mais recommandé) pgAdmin 4
- Git

---

## Installation rapide

```bash
git clone https://github.com/NZT48DEV/Projet_12_OC_SQL.git
cd Projet_12_OC_SQL
pipenv install --dev
pipenv shell
```

---

## Configuration PostgreSQL (résumé)

- Créer un utilisateur **non privilégié** : `epic_crm_app`
- Créer une base : `epic_crm`
- Assigner la base à `epic_crm_app`

> Principe du moindre privilège appliqué : l’application n’utilise jamais le compte administrateur.

---

## Variables d’environnement

Créer un fichier `.env` à la racine :

```env
DATABASE_URL=postgresql://epic_crm_app:VOTRE_MOT_DE_PASSE@localhost:5432/epic_crm
SQLALCHEMY_DATABASE_URL=postgresql+psycopg://epic_crm_app:VOTRE_MOT_DE_PASSE@localhost:5432/epic_crm
SENTRY_DSN=
```

> ⚠️ Les caractères spéciaux dans le mot de passe doivent être encodés (URL encoding).

Un fichier `.env.example` est fourni comme modèle.

---

## Vérification rapide

```bash
python -m app.main
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

À chaque push ou pull request vers `master` :
- contrôle qualité (pre-commit),
- exécution des tests pytest,
- démarrage d’un service PostgreSQL pour les tests.

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
├── tests/
│   ├── unit/
│   ├── integration/
│   └── functional/
├── .env.example                   # modèle (sans secrets)
├── .flake8                        # config flake8
├── .gitignore
├── .pre-commit-config.yaml        # config pre-commit
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

- ✔️ Phase d’initialisation terminée
- ✔️ Environnement et CI en place
- ✔️ Connexion PostgreSQL validée

👉 Prochaine étape : **implémentation du schéma SQL à partir de l’ERD**.
