## Architecture du projet

```
.
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI GitHub Actions (lint + tests + PostgreSQL)
├── app/
│   ├── __init__.py
│   ├── epicevents.py              # Point d’entrée
│   ├── cli/                       # Interface en ligne de commande
│   │   ├── __init__.py
│   │   ├── click_utils.py         # Utilitaires d'adaptation Click -> handlers existants.
│   │   ├── console.py             # Helpers d'affichage pour la CLI.
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── clients.py
│   │   │   ├── contracts.py
│   │   │   ├── employees.py
│   │   │   └── events.py
│   ├── core/                      # Sécurité, JWT, configuration, Sentry
│   │   ├── __init__.py
│   │   ├── authorization.py
│   │   ├── jwt_service.py
│   │   ├── observability.py
│   │   ├── security.py
│   │   └── token_store.py
│   ├── db/                        # Gestion base de données (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── base.py                # Déclaration Base ORM
│   │   ├── config.py              # Chargement DATABASE_URL
│   │   ├── db_check_sqlalchemy.py # Vérifications de cohérence
│   │   ├── engine.py              # Création de l'engine SQLAlchemy
│   │   ├── init_db.py             # Initialisation DB
│   │   └── session.py             # SessionLocal
│   ├── models/                    # Modèles ORM
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── contract.py
│   │   ├── employee.py
│   │   └── event.py
│   ├── repositories/              # Accès aux données (DAL)
│   │   ├── __init__.py
│   │   ├── client_repository.py
│   │   ├── contract_repository.py
│   │   ├── employee_repository.py
│   │   └── event_repository.py
│   └── services/                  # Logique métier
│       ├── __init__.py
│       ├── auth_service.py
│       ├── client_service.py
│       ├── contract_service.py
│       ├── current_employee.py
│       ├── employee_service.py
│       └── event_service.py
├── docs/
│   ├── architecture.md            # Structure du projet + responsabilités
│   ├── authentication.md          # JWT, rôles, tokens, bootstrap
│   ├── cli.md                     # Commandes CLI
│   ├── database.md                # PostgreSQL + variables env + Alembic
│   ├── erd.mmd                    # Schéma ERD
│   ├── observability.md           # Sentry (monitoring)
│   ├── project_status.md          # État du projet + next steps
│   ├── quality_ci.md              # Qualité de code + CI
│   └── schema_notes.md            # Notes de conception
├── migrations/                    # Migrations Alembic
│   └── versions/
├── tests/
│   ├── unit/
│   └── integration/
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
