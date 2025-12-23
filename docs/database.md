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
