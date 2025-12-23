# Commandes CLI

## Authentification

### Connexion
```bash
python -m app.epicevents login <email> <password>
```

- Génère un **access token** et un **refresh token**
- Stocke les tokens localement (keyring ou fallback fichier)

---

### Afficher l’utilisateur courant
```bash
python -m app.epicevents whoami
```

- Vérifie la validité de l’access token
- Affiche l’identité et le rôle de l’utilisateur connecté

---

### Rafraîchir le token
```bash
python -m app.epicevents refresh-token
```

- Utilise le refresh token pour générer un nouvel access token
- Effectue une **rotation du refresh token**

---

### Déconnexion
```bash
python -m app.epicevents logout
```

- Supprime les tokens locaux
- Nécessite une reconnexion complète

---

## Lecture des entités métier (read-only)

Toutes les commandes suivantes nécessitent une **authentification valide**
et respectent les règles d’autorisation par rôle.

---

### Lister les clients
```bash
python -m app.epicevents clients list
```

- Affiche l’ensemble des **clients**
- Lecture seule
- Accessible aux utilisateurs authentifiés

---

### Lister les contrats
```bash
python -m app.epicevents contracts list
```

- Affiche l’ensemble des **contrats**
- Inclut les informations financières et l’état de signature
- Lecture seule
- Accessible aux utilisateurs authentifiés

---

### Lister les événements
```bash
python -m app.epicevents events list
```

- Affiche l’ensemble des **événements**
- Inclut les dates, le lieu, le nombre de participants et les relations associées
- Lecture seule
- Accessible aux utilisateurs authentifiés

---

## Autorisation par rôle

Les commandes sensibles sont protégées par un système de rôles :

- `MANAGEMENT`
- `SALES`
- `SUPPORT`

Un mécanisme d’autorisation centralisé vérifie :
- l’authentification via JWT
- le rôle de l’utilisateur

---

### Exemple de commande réservée au rôle MANAGEMENT
```bash
python -m app.epicevents management-only
```

Cette commande est accessible **uniquement** aux utilisateurs ayant le rôle `MANAGEMENT`.

---

## Sécurité

- Toute commande exécutée sans authentification valide est rejetée
- Les permissions sont vérifiées **avant tout accès aux données**
- Les commandes de lecture n’effectuent **aucune modification** en base

---
