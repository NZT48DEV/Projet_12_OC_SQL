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
│   ├── architecture.md            # Structure du projet + responsabilités
│   ├── authentication.md          # JWT, rôles, tokens, bootstrap
│   ├── cli.md                     # Commandes CLI
│   ├── database.md                # PostgreSQL + variables env + Alembic
│   ├── project_status.md          # État du projet + next steps
│   ├── quality_ci.md              # Qualité de code + CI
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
