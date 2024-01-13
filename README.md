# LitRevu

## Description
Notre nouvelle application, **LitRevu**, permet de demander ou publier des critiques de livres ou d’articles. L’application présente trois cas d’utilisation principaux :

- La publication des critiques de livres ou d’articles.
- La demande des critiques sur un livre ou sur un article particulier.
- La recherche d’articles et de livres intéressants à lire, en se basant sur les critiques des autres.

## Prérequis
Pour exécuter ce projet, vous aurez besoin d'avoir installé Python, Docker, et Git sur votre machine.

## Installation et Exécution

### Avec un Environnement Virtuel Python
1. **Cloner le dépôt Git** :

 ```
git clone https://github.com/PalexM/litrevu.git
```
 ```
cd litrevu
 ```
2. **Créer et activer un environnement virtuel** :
- Sous Windows :
  ```
  python -m venv venv
  .\venv\Scripts\activate
  ```
- Sous Unix ou MacOS :
  ```
  python3 -m venv venv
  source venv/bin/activate
  ```

3. **Installer les dépendances** :
 ```
pip install -r requirements.txt
 ```
4. **Initialiser la base de données** :
 ```
python manage.py migrate
 ```

5. **Lancer le serveur** :
 ```
python manage.py runserver
 ```

### Avec Docker
1. **Télécharger l'image Docker depuis Docker Hub** :
 ```
docker pull mrp0p/litrevu
 ```
2. **Exécuter le conteneur Docker** :
 ```
docker run -p 8000:8000 mrp0p/litrevu
 ```

## Utilisation
Après avoir lancé le serveur (soit via l'environnement virtuel, soit via Docker), vous pouvez accéder à l'application en ouvrant votre navigateur et en allant à l'adresse `http://localhost:8000`.

## Contribution
Les contributions à ce projet sont les bienvenues. N'hésitez pas à proposer des améliorations ou à signaler des problèmes via les issues ou les pull requests sur GitHub.
