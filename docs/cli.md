# Commandes CLI — Epic Events CRM

> Exécution : toutes les commandes se lancent via `python -m app.epicevents ...`

## 🔐 Authentification

### Connexion
```bash
python -m app.epicevents login <email> <password>
```
- Génère un **access token** et un **refresh token**
- Stocke les tokens localement

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
- Peut faire une **rotation** du refresh token

---

### Déconnexion
```bash
python -m app.epicevents logout
```
- Supprime les tokens locaux

---

## 👥 Employés

Toutes les commandes suivantes nécessitent une **authentification valide**, sauf le bootstrap initial.

### Créer un employé (bootstrap du premier MANAGEMENT)
```bash
python -m app.epicevents create-employee <first_name> <last_name> <email> <password> <ROLE>
```
- Si aucun employé n’existe encore, le premier compte **doit être** `MANAGEMENT`
- Sinon, création réservée au rôle `MANAGEMENT`
- Rôles possibles : `MANAGEMENT`, `SALES`, `SUPPORT`

---

### Lister les employés
```bash
python -m app.epicevents employees list
python -m app.epicevents employees list --role SALES
python -m app.epicevents employees list --role SUPPORT
python -m app.epicevents employees list --role MANAGEMENT
```

---

### Exemple de commande réservée au rôle MANAGEMENT
```bash
python -m app.epicevents management-only
```
Accessible **uniquement** aux utilisateurs ayant le rôle `MANAGEMENT`.

---

## 🧑‍💼 Clients

Toutes les commandes suivantes nécessitent une **authentification valide**.

### Lister les clients
```bash
python -m app.epicevents clients list
```
- Lecture seule

---

### Créer un client (SALES uniquement)
```bash
python -m app.epicevents clients create <first_name> <last_name> <email> [--phone <phone>] [--company-name <company_name>]
```
Exemple :
```bash
python -m app.epicevents clients create John Doe john.doe@email.com --phone 0600000000 --company-name ACME
```

---

### Mettre à jour un client
```bash
python -m app.epicevents clients update <client_id> [--first-name <first_name>] [--last-name <last_name>] [--email <email>] [--phone <phone>] [--company-name <company_name>]
```
Exemples :
```bash
python -m app.epicevents clients update 1 --phone 0612345678
python -m app.epicevents clients update 1 --email new@email.com --company-name "NewCo"
```
- `SUPPORT` : accès interdit
- `SALES` : peut modifier uniquement ses propres clients
- `MANAGEMENT` : peut modifier tous les clients

---

## 🧾 Contrats

Toutes les commandes suivantes nécessitent une **authentification valide**.

### Lister les contrats
```bash
python -m app.epicevents contracts list
```
- Lecture seule

---

### Créer un contrat (SALES / MANAGEMENT)
```bash
python -m app.epicevents contracts create <client_id> <total> <amount_due> [--signed]
```
Exemples :
```bash
python -m app.epicevents contracts create 1 1000.00 200.00
python -m app.epicevents contracts create 1 1000.00 0.00 --signed
```

---

### Signer un contrat (MANAGEMENT)
```bash
python -m app.epicevents contracts sign <contract_id>
```
Exemple :
```bash
python -m app.epicevents contracts sign 10
```

---

### Mettre à jour un contrat (SALES / MANAGEMENT)
```bash
python -m app.epicevents contracts update <contract_id> [--total <total_amount>] [--amount-due <amount_due>]
```
Exemples :
```bash
python -m app.epicevents contracts update 10 --amount-due 150.00
python -m app.epicevents contracts update 10 --total 1500.00 --amount-due 1200.00
```
- `SALES` : peut modifier uniquement ses propres contrats
- La signature n’est pas modifiable ici (utiliser `contracts sign`)

---

## 📅 Événements

Toutes les commandes suivantes nécessitent une **authentification valide**.

### Lister les événements
```bash
python -m app.epicevents events list
```
- Lecture seule

---

### Créer un événement (SALES, contrat signé requis)
```bash
python -m app.epicevents events create <client_id> <contract_id> <start_date> <start_time> <end_date> <end_time> <location> <attendees> [--notes <notes>]
```
Formats :
- `start_date` / `end_date` : `YYYY-MM-DD`
- `start_time` / `end_time` : `HH:MM`

Exemple :
```bash
python -m app.epicevents events create 1 10 2026-01-10 10:00 2026-01-10 12:00 "Paris" 50 --notes "Accueil + badges"
```

---

### Mettre à jour un événement (SUPPORT sur ses événements / MANAGEMENT)
```bash
python -m app.epicevents events update <event_id> [--start-date YYYY-MM-DD --start-time HH:MM] [--end-date YYYY-MM-DD --end-time HH:MM] [--location <location>] [--attendees <attendees>] [--notes <notes>] [--support-contact-id <employee_id>]
```
Exemples :
```bash
python -m app.epicevents events update 5 --location "Lyon" --attendees 80
python -m app.epicevents events update 5 --start-date 2026-01-10 --start-time 09:30
python -m app.epicevents events update 5 --end-date 2026-01-10 --end-time 13:00 --notes "Changement de planning"
```
Assignation support (MANAGEMENT uniquement) :
```bash
python -m app.epicevents events update 5 --support-contact-id 3
```

Rappels de règles :
- `SALES` : ne peut pas modifier un événement
- `SUPPORT` : peut modifier uniquement les événements qui lui sont assignés
- `MANAGEMENT` : peut modifier tous les événements et assigner un support
- Les paramètres dates/heures se donnent **par paire** (`--start-date` + `--start-time`, `--end-date` + `--end-time`)

---

## 🛡️ Autorisation par rôle

Les commandes sont protégées par un système de rôles :
- `MANAGEMENT`
- `SALES`
- `SUPPORT`

Les contrôles portent sur :
- l’authentification via JWT
- le rôle de l’utilisateur
- et, si applicable, le **périmètre** (ex : un support ne modifie que ses événements)
