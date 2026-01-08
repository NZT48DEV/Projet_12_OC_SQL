## Qualité de code

Outils utilisés :
- black
- isort
- flake8
- pre-commit
- pytest
- pytest-cov

Installation des hooks :
```bash
pre-commit install
```

---

## Tests

Lancer l’ensemble des tests automatisés :

```bash
pytest
```

### Couverture de tests (coverage)

La **couverture de code est mesurée automatiquement** lors de l’exécution des tests.

- `pytest-cov` est intégré au projet
- un rapport de couverture est généré à chaque exécution de `pytest`
- en CI, le coverage est calculé sans action supplémentaire

Selon la configuration :
- un rapport **HTML** est généré dans le dossier `htmlcov/`
- et/ou un rapport **XML** est utilisé par la CI

> ℹ️ Il n’est pas nécessaire de lancer une commande spécifique :
> la couverture est calculée automatiquement avec les tests.

---

## Intégration Continue (CI)

Une **CI GitHub Actions** est configurée.

À chaque push ou pull request :
- vérification du style (pre-commit),
- exécution des tests,
- calcul automatique de la couverture de code,
- démarrage d’un service PostgreSQL pour les tests d’intégration.

---
