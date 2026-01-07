# Commandes CLI — Epic Events CRM

Toutes les commandes s’exécutent via la CLI :

```bash
epicevents <commande> [options]
```

L’interface CLI est construite avec **Click** (structure, parsing) et **Rich**
(affichage en tables, messages colorés).

---

## 🔐 Authentification

### Connexion
```bash
epicevents login <email> <password>
```

### Utilisateur courant
```bash
epicevents whoami
```

### Rafraîchir le token
```bash
epicevents refresh-token
```

### Déconnexion
```bash
epicevents logout
```

---

## 👥 Employés

### Créer un employé (bootstrap)
```bash
epicevents create-employee <first_name> <last_name> <email> <password> <ROLE>
```
Rôles possibles : `MANAGEMENT`, `SALES`, `SUPPORT`.

⚠️ Le tout premier employé doit obligatoirement être `MANAGEMENT`.

---

### Lister les employés
```bash
epicevents employees list
epicevents employees list --role SALES
```

---

### Désactiver un employé (soft delete)
```bash
epicevents employees deactivate <employee_id>
```

### Réactiver un employé
```bash
epicevents employees reactivate <employee_id>
```

---

### Supprimer un employé

#### Soft delete (par défaut)
```bash
epicevents employees delete <employee_id>
```

#### Hard delete ⚠️ (irréversible)
```bash
epicevents employees delete <employee_id> --hard --confirm <employee_id>
```

Échoue si l’employé est encore référencé par des clients, contrats ou événements.

---

## 🧑‍💼 Clients

### Lister
```bash
epicevents clients list
```

### Créer (SALES)
```bash
epicevents clients create <first_name> <last_name> <email>   [--phone <phone>] [--company-name <company>]
```

### Mettre à jour
```bash
epicevents clients update <client_id> [options]
```

### Réassigner (MANAGEMENT)
```bash
epicevents clients reassign <client_id> <sales_contact_id>
```

---

## 🧾 Contrats

### Lister
```bash
epicevents contracts list
```

### Créer (MANAGEMENT)
```bash
epicevents contracts create <client_id> <total> <amount_due> [--signed]
```

### Signer
```bash
epicevents contracts sign <contract_id>
```

### Mettre à jour
```bash
epicevents contracts update <contract_id> [options]
```

### Réassigner
```bash
epicevents contracts reassign <contract_id> <sales_contact_id>
```

---

## 📅 Événements

### Lister
```bash
epicevents events list
```

### Créer (SALES, contrat signé requis)
```bash
epicevents events create <client_id> <contract_id>   <start_date> <start_time> <end_date> <end_time>   <location> <attendees> [--notes <notes>]
```

Formats :
- Date : `YYYY-MM-DD`
- Heure : `HH:MM`

### Mettre à jour
```bash
epicevents events update <event_id> [options]
```

### Réassigner le support (MANAGEMENT)
```bash
epicevents events reassign <event_id> --support-contact-id <support_id>
```

---

## 🛡️ Permissions (récap)

| Action | MANAGEMENT | SALES | SUPPORT |
|------|-----------|-------|---------|
| Créer employé | ✔ | ❌ | ❌ |
| Gérer clients | ✔ | ✔ (si propriétaire) | ❌ |
| Gérer contrats | ✔ | ✔ (si propriétaire) | ❌ |
| Gérer événements | ✔ | ❌ | ✔ (si assigné) |
