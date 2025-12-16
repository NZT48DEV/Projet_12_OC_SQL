# Epic Events CRM (Back-end Python + PostgreSQL)

CRM interne sécurisé pour gérer les clients, contrats et événements d’Epic Events.

Ce projet vise à mettre en place une architecture back-end sécurisée reposant sur
Python et PostgreSQL, avec une attention particulière portée à la modélisation des
données, à la gestion des accès et aux bonnes pratiques de sécurité.

---

## Prérequis

- Python **3.11+**
- Pipenv
- PostgreSQL **14+**
- (Optionnel mais recommandé) pgAdmin 4
- Git

---

## Installation du projet

### 1️⃣ Cloner le repository
```bash
git clone <url_du_repo>
cd epic-events-crm
```

### 2️⃣ Installer les dépendances Python
```bash
pipenv install --dev
pipenv shell
```

---

## Installation et configuration de PostgreSQL

### 1️⃣ Installer PostgreSQL
Télécharger et installer PostgreSQL depuis le site officiel :
https://www.postgresql.org/download/

Pendant l’installation :
- conserver le port par défaut `5432`
- définir un mot de passe pour l’utilisateur administrateur `postgres`
- installer pgAdmin si proposé

---

### 2️⃣ Créer l’utilisateur applicatif (sécurité)

Dans **pgAdmin** :
- Créer un rôle :
  - Nom : `epic_crm_app`
  - Peut se connecter : ✅
  - Superuser : ❌
  - Création de bases : ❌
  - Création de rôles : ❌

Ce compte sera utilisé exclusivement par l’application
(**principe du moindre privilège**).

---

### 3️⃣ Créer la base de données
- Nom : `epic_crm`
- Propriétaire : `epic_crm_app`

---

## Variables d’environnement

### 1️⃣ Créer le fichier `.env`
À la racine du projet, créer un fichier `.env` (non versionné) :

```env
DATABASE_URL=postgresql://epic_crm_app:VOTRE_MOT_DE_PASSE@localhost:5432/epic_crm
SENTRY_DSN=
```

⚠️ Si le mot de passe contient des caractères spéciaux (`@`, `:`, `/`, `%`, `#`),
il doit être encodé (URL encoding).

---

### 2️⃣ Fichier modèle
Le fichier `.env.example` fournit un modèle sans informations sensibles.

---

## Vérification de la connexion à la base

Un test minimal est disponible dans `app/main.py` pour vérifier la connexion à PostgreSQL.

Lancer :
```bash
python -m app.main
```

Résultat attendu :
```
Connected to database 'epic_crm' as user 'epic_crm_app'
```

---

## Qualité de code

Ce projet utilise les outils suivants :
- **black** : formatage du code
- **isort** : organisation des imports
- **flake8** : linting
- **pre-commit** : hooks automatiques
- **pytest** : tests

### Installer les hooks pre-commit
```bash
pre-commit install
```

### Lancer tous les checks
```bash
pre-commit run --all-files
```

---

## Documentation

- Schéma de la base de données (ERD) : `docs/erd.mmd`
- Notes de conception : `docs/schema_notes.md`

---

## État du projet

- ✔️ Phase d’initialisation terminée
- ✔️ Environnement prêt
- ✔️ PostgreSQL configuré avec un utilisateur non privilégié
- ✔️ Connexion Python <> PostgreSQL validée

👉 Prochaine étape : **création du schéma SQL à partir de l’ERD**.
