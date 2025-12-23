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
