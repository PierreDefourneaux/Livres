# Projet de moteur de recommandation de livres

## Description

Le projet de moteur de recommandation de livres stocke ses données dans une base de données locale MySQL db_bloc1 et dans une base de données locale MongoDB.

## Table des Matières

- Installation des bases de données MySQL et MongoDB<br>
- Structure de la base de données MySQL<br>
- Configuration<br>
- Automatisationavec Crontab<br>
- Utilisation de l'API


## Installation des bases de données

### Prérequis

- MySQL Server (version 8.0.39)<br>
- Client MySQL (Shell SQL ("Advanced client and code editor for MySQL") ou MySQL Workbench)<br>
- MongoDB server (version 8.0)<br>
- MongoDB Compass (version 1.45.3)

### Étapes d'Installation
#### MySQL
1. **Télécharger le fichier SQL** :<br>
Téléchargez le fichier `bdd.sql` depuis le dépôt github https://github.com/PierreDefourneaux/Livres

2. **Créer la base de données MySQL** :<br>
Dans un terminal se mettre dans le dossier qui contient fichier.sql puis écrire la commande :<br>
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" < bdd.sql -u root -p

#### MongoDB
1. **Créer la base de données MongoDB** :<br>
Dans MongoDB Compass, créez une base de données "mongo_db_livres"<br>
Dans la base de données "mongo_db_livres", créez la collection "images"

## Structure de la base de données MySQL
### Tables principales
#### 1. Table Livres
Description : Contient les informations principales sur les livres.<br>
#### 2. Table Editeurs
Description : Contient les informations sur les éditeurs des livres.<br>
#### 3. Table Thematiques
Description : Contient les thématiques associées aux livres.<br>
#### 4. Table Auteurs
Description : Contient les informations sur les auteurs des livres.<br>
### Tables de jonction (relations many to many)
#### 1. Table auteurs_livres
Description : Lie les livres à leurs auteurs.<br>
Contraintes :<br>
Clé primaire composée : (livre_id, auteur_id).<br>
ON UPDATE CASCADE et ON DELETE CASCADE pour livre_id.<br>
ON UPDATE NO ACTION et ON DELETE NO ACTION pour auteur_id.
#### 2. Table editeurs_livres
Description : Lie les livres à leurs éditeurs.<br>
Contraintes :<br>
Clé primaire composée : (editeur_id, livre_id).<br>
ON UPDATE CASCADE et ON DELETE CASCADE pour livre_id.<br>
ON UPDATE NO ACTION et ON DELETE NO ACTION pour editeur_id.
#### 3. Table thematiques_livres
Description : Lie les livres à leurs thématiques.<br>
Contraintes :<br>
Clé primaire composée : (livre_id, thematique_id).<br>
ON UPDATE CASCADE et ON DELETE CASCADE pour livre_id.<br>
ON UPDATE NO ACTION et ON DELETE NO ACTION pour thematique_id.

## Configuration
Assurez-vous d'avoir un fichier .env à la racine du projet contenant les variables suivantes :

#### CREDENTIALS MYSQL
USER = 'root'<br>
PASSWORD = votre mysql password<br>
HOST = votre mysql local host<br>
PORT = votre mysql port<br>
DATABASE = 'db_bloc1'

#### CREDENTIALS MONGODB
MONGOHOST = "localhost"<br>
MONGOPORT = votre mongo port<br>
MONGODATABASE = "mongo_db_livres"<br>
MONGOCOLLECTION = "images"

#### API LIBRARYTHING
TOKEN_LIBRARYTHING_API = votre token librarything

#### Fast API
SECRET_KEY = votre key<br>
API_PASSWORD = votre password

## Automatisation avec Crontab
Sous WSL, créer un environnement virtuel avec les librairies précisées dans le fichier requirements.txt.
Dans crontab, programmer ces commandes :

5 * * * * . /home/{utilisateur}/{chemin_vers_l_environnement}/bin/activate && cd /mnt/c/{chemin_vers_le_dossier_windows}  && python3 /mnt/c/{chemin_vers_le_dossier_windows}/script_webscrap.py >> /mnt/c/{chemin_vers_le_dossier_windows}/res.log

30 * * * * . /home/{utilisateur}/{chemin_vers_l_environnement}/bin/activate && cd /mnt/c/{chemin_vers_le_dossier_windows}  && python3 /mnt/c/{chemin_vers_le_dossier_windows}/script_nettoyage.py >> /mnt/c/{chemin_vers_le_dossier_windows}/res.log

50 * * * * . /home/{utilisateur}/{chemin_vers_l_environnement}/bin/activate && cd /mnt/c/{chemin_vers_le_dossier_windows}  && python3 /mnt/c/{chemin_vers_le_dossier_windows}/script_insertion.py >> /mnt/c/{chemin_vers_le_dossier_windows}/res.log

## Utilisation de l'API
Dans le terminal, lancer l'API avec la commande suivante :<br>
uvicorn app:app --reload<br>
Dans le navigateur, en fonction de votre port :<br>
aller à http://127.0.0.1:8000/docs<br>
et suivre les instructions pour obtenir un token et pouvoir effectuer des requêtes