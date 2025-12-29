# Commandes CLI — Epic Events CRM

> Exécution : toutes les commandes se lancent via `python -m app.epicevents ...`

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

## Clients

Toutes les commandes suivantes nécessitent une **authentification valide**.

### Lister les clients
```bash
python -m app.epicevents clients list
```
- Affiche l’ensemble des **clients**
- Lecture seule

---

### Créer un client
```bash
python -m app.epicevents clients create   --full-name "Nom Prénom"   --email "client@email.com"   --phone "0600000000"   --company "Entreprise"   --sales-contact-id <employee_id>
```
- Crée un **client**
- Réservé au rôle `SALES` / `MANAGEMENT`

---

### Mettre à jour un client
```bash
python -m app.epicevents clients update <client_id>   --full-name "Nom Prénom"   --email "client@email.com"   --phone "0600000000"   --company "Entreprise"   --sales-contact-id <employee_id>
```
- Met à jour un **client**
- Champs à fournir selon besoins (vous pouvez omettre ceux qui ne changent pas)

---

## Contrats

Toutes les commandes suivantes nécessitent une **authentification valide**.

### Lister les contrats
```bash
python -m app.epicevents contracts list
```
- Affiche l’ensemble des **contrats**
- Inclut les informations financières et l’état de signature
- Lecture seule

---

### Créer un contrat
```bash
python -m app.epicevents contracts create   --client-id <client_id>   --amount <montant_total>   --remaining <reste_a_payer>   --status unsigned
```
- Crée un **contrat**
- Réservé au rôle `SALES` / `MANAGEMENT`

---

### Signer un contrat
```bash
python -m app.epicevents contracts sign <contract_id>
```
- Marque le contrat comme **signé**
- Réservé au rôle `MANAGEMENT`

---

## Événements

Toutes les commandes suivantes nécessitent une **authentification valide**.

### Lister les événements
```bash
python -m app.epicevents events list
```
- Affiche l’ensemble des **événements**
- Inclut dates, lieu, participants et relations associées
- Lecture seule

---

### Créer un événement
```bash
python -m app.epicevents events create   --contract-id <contract_id>   --name "Nom de l'événement"   --start "YYYY-MM-DD"   --end "YYYY-MM-DD"   --location "Adresse / Ville"   --attendees <nombre>   --support-contact-id <employee_id>
```
- Crée un **événement** rattaché à un contrat signé
- Réservé au rôle `SALES` / `MANAGEMENT`

---

### Mettre à jour un événement
```bash
python -m app.epicevents events update <event_id>   --name "Nom de l'événement"   --start "YYYY-MM-DD"   --end "YYYY-MM-DD"   --location "Adresse / Ville"   --attendees <nombre>   --support-contact-id <employee_id>
```
- Met à jour un **événement**
- Réservé au rôle `SUPPORT` (sur ses événements) / `MANAGEMENT`

---

## Autorisation par rôle

Les commandes sensibles sont protégées par un système de rôles :
- `MANAGEMENT`
- `SALES`
- `SUPPORT`

Un mécanisme d’autorisation centralisé vérifie :
- l’authentification via JWT
- le rôle de l’utilisateur
- et, si applicable, le **périmètre** (ex : un support ne modifie que ses événements)

---

### Exemple de commande réservée au rôle MANAGEMENT
```bash
python -m app.epicevents management-only
```
Accessible **uniquement** aux utilisateurs ayant le rôle `MANAGEMENT`.

---

## Sécurité

- Toute commande exécutée sans authentification valide est rejetée
- Les permissions sont vérifiées **avant tout accès aux données**
- Les commandes de lecture n’effectuent **aucune modification** en base
