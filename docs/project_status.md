## État du projet — Epic Events CRM

### Infrastructure & données
- ✔️ Environnement **Python 3.11+** et **PostgreSQL** correctement configuré
- ✔️ Bases de données **développement** et **test** séparées et fonctionnelles
- ✔️ Utilisateur PostgreSQL **non privilégié** avec droits limités
- ✔️ ORM **SQLAlchemy** opérationnel
- ✔️ Migrations **Alembic** fonctionnelles (schéma versionné)
- ✔️ Modèles et relations conformes à l’ERD et au cahier des charges
- ✔️ Séparation claire entre administration de la base et usage applicatif

---

### Sécurité & authentification
- ✔️ Authentification **JWT** fonctionnelle en CLI (access + refresh tokens)
- ✔️ Stockage local sécurisé des tokens (keyring avec fallback fichier)
- ✔️ Rotation des refresh tokens
- ✔️ Autorisation centralisée par rôle :
  - `MANAGEMENT`
  - `SALES`
  - `SUPPORT`
- ✔️ Mécanisme de **bootstrap sécurisé** pour le premier compte MANAGEMENT

---

### Fonctionnalités métier implémentées

#### Clients
- ✔️ Lecture sécurisée des clients (`clients list`)
- ✔️ Création de clients (`clients create`)
- ✔️ Accès contrôlé par rôle (`SALES` / `MANAGEMENT`)

#### Contrats
- ✔️ Lecture sécurisée des contrats (`contracts list`)
- ✔️ Création de contrats (`contracts create`)
  - autorisée pour les rôles `SALES` et `MANAGEMENT`
- ✔️ Signature des contrats (`contracts sign`)
  - autorisée **uniquement** pour le rôle `MANAGEMENT`
- ✔️ Règles métier validées :
  - montants cohérents
  - client existant
  - impossibilité de signer deux fois le même contrat

#### Événements
- ✔️ Lecture sécurisée des événements (`events list`)
- ✔️ Accès conditionné à une authentification valide (JWT)
- ✔️ Aucune modification possible via les commandes de lecture

---

### Qualité & intégration continue
- ✔️ Tests unitaires et tests d’intégration automatisés (**pytest + PostgreSQL**)
- ✔️ Pipeline **CI GitHub Actions** fonctionnel :
  - linting (pre-commit)
  - exécution des tests
  - base PostgreSQL éphémère pour l’intégration
- ✔️ Architecture respectant la séparation :
  - CLI (interface)
  - Services (règles métier)
  - Repositories (accès aux données)

---

👉 **Prochaines étapes prévues**
- Implémentation des fonctionnalités **UPDATE / DELETE**
  sur les entités métier (**clients**, **contrats**, **événements**)
- Renforcement des règles métier sur les événements
  (ex : création uniquement si contrat signé)
- Ajout de tests d’intégration couvrant les scénarios d’autorisation par rôle
