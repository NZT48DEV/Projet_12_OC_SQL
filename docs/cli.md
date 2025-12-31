# Commandes CLI — Epic Events CRM

> Toutes les commandes se lancent via :
> `python -m app.epicevents ...`

---

## 🔐 Authentification

### Connexion
```bash
python -m app.epicevents login <email> <password>
```

### Utilisateur courant
```bash
python -m app.epicevents whoami
```

### Rafraîchir le token
```bash
python -m app.epicevents refresh-token
```

### Déconnexion
```bash
python -m app.epicevents logout
```

---

## 👥 Employés

### Créer un employé
```bash
python -m app.epicevents create-employee <first_name> <last_name> <email> <password> <ROLE>
```
Rôles possibles : `MANAGEMENT`, `SALES`, `SUPPORT`

---

### Lister les employés
```bash
python -m app.epicevents employees list
python -m app.epicevents employees list --role MANAGEMENT
python -m app.epicevents employees list --role SALES
python -m app.epicevents employees list --role SUPPORT
```

---

### Désactiver un employé (soft delete)
```bash
python -m app.epicevents employees deactivate <employee_id>
```

### Réactiver un employé
```bash
python -m app.epicevents employees reactivate <employee_id>
```

---

### Supprimer un employé (suppression contrôlée)
```bash
python -m app.epicevents employees delete <employee_id>
```

**Suppression** uniquement si aucune référence n’existe

**Refus** si l’employé est encore lié à :
- un client
- un contrat
- un événement

---

### Supprimer définitivement un employé (HARD DELETE ⚠️)
```bash
python -m app.epicevents employees delete <employee_id> --hard --confirm <employee_id>
```
⚠️ **Action irréversible** :
- supprime définitivement l’employé
- échoue si des entités (clients / contrats / events) sont encore référencées

---

## 🧑‍💼 Clients

### Lister les clients
```bash
python -m app.epicevents clients list
```

### Créer un client (SALES)
```bash
python -m app.epicevents clients create <first_name> <last_name> <email>   [--phone <phone>] [--company-name <company_name>]
```

---

### Mettre à jour un client
```bash
python -m app.epicevents clients update <client_id>   [--first-name <first_name>]   [--last-name <last_name>]   [--email <email>]   [--phone <phone>]   [--company-name <company_name>]
```

Règles :
- `SUPPORT` ❌ interdit
- `SALES` ✔ uniquement ses clients
- `MANAGEMENT` ✔ tous les clients

---

### Réassigner un client (MANAGEMENT)
```bash
python -m app.epicevents clients reassign <client_id> <sales_contact_id>
```
➡️ Réassigne le client **et tous ses contrats** au nouveau commercial.

---

## 🧾 Contrats

### Lister les contrats
```bash
python -m app.epicevents contracts list
```

---

### Créer un contrat (MANAGEMENT)
```bash
python -m app.epicevents contracts create <client_id> <total_amount> <amount_due> [--signed]
```

---

### Signer un contrat (MANAGEMENT)
```bash
python -m app.epicevents contracts sign <contract_id>
```

---

### Mettre à jour un contrat
```bash
python -m app.epicevents contracts update <contract_id>   [--total <total_amount>]   [--amount-due <amount_due>]
```

Règles :
- `SALES` ✔ uniquement ses contrats
- `MANAGEMENT` ✔ tous

---

### Réassigner un contrat
```bash
python -m app.epicevents contracts reassign <contract_id> <sales_contact_id>
```
Règles :
- `SALES` ✔ uniquement ses contrats
- `MANAGEMENT` ✔ tous

---

## 📅 Événements

### Lister les événements
```bash
python -m app.epicevents events list
```

---

### Créer un événement (SALES, contrat signé requis)
```bash
python -m app.epicevents events create <client_id> <contract_id>   <start_date> <start_time> <end_date> <end_time>   <location> <attendees> [--notes <notes>]
```

Formats :
- Dates : `YYYY-MM-DD`
- Heures : `HH:MM`

---

### Mettre à jour un événement
```bash
python -m app.epicevents events update <event_id>   [--start-date YYYY-MM-DD --start-time HH:MM]   [--end-date YYYY-MM-DD --end-time HH:MM]   [--location <location>]   [--attendees <attendees>]   [--notes <notes>]   [--support-contact-id <employee_id>]
```

Règles :
- `SUPPORT` ✔ uniquement ses événements
- `MANAGEMENT` ✔ tous
- `SALES` ❌ interdit

---

### Réassigner le support d’un événement (MANAGEMENT)
```bash
python -m app.epicevents events reassign <event_id> --support-contact-id <support_employee_id>
```

---

## 🛡️ Récapitulatif des permissions

| Action | MANAGEMENT | SALES | SUPPORT |
|------|-----------|-------|---------|
| Créer employé | ✔ | ❌ | ❌ |
| Réassigner client | ✔ | ❌ | ❌ |
| Réassigner contrat | ✔ | ✔ (si propriétaire) | ❌ |
| Réassigner event | ✔ | ❌ | ❌ |
| Modifier event | ✔ | ❌ | ✔ (si assigné) |
