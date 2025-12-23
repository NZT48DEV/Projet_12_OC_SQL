## Qualité de code

Outils utilisés :
- black
- isort
- flake8
- pre-commit
- pytest

Installation des hooks :
```bash
pre-commit install
```

---

## Intégration Continue (CI)

Une **CI GitHub Actions** est configurée.

À chaque push ou pull request :
- vérification du style (pre-commit),
- exécution des tests,
- démarrage d’un service PostgreSQL pour les tests d’intégration.

---
