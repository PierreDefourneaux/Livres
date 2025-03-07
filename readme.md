# Projet de moteur de recommandation de livres

## Description

Le projet de moteur de recommandation de livres stocke ses données dans la base de données MySQL db_bloc1 et dans une base de données locale MongoDB.

## Table des Matières

- [Installation des bases de données](#Installation des bases de données)<br>
- [Configuration](#configuration)<br>
- [Structure de la Base de Données](#structure-de-la-base-de-données)<br>
- [Utilisation de l'API](#Utilisation de l'API)<br>

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

## Structure de la base de données MySQL
### Tables principales
#### 1. Table Livres
Description : Contient les informations principales sur les livres.<br>
Champs :<br>
livre_id (INT, clé primaire) : Identifiant unique du livre.<br>
livre_nom (VARCHAR(255)) : Nom du livre (doit être unique).<br>
livre_nombre_de_pages (VARCHAR(255)) : Nombre de pages du livre.<br>
livre_note (DECIMAL(2,1)) : Note attribuée au livre.<br>
ISBN_10 (VARCHAR(10)) : Numéro ISBN-10 du livre.<br>
ISBN_13 (VARCHAR(13)) : Numéro ISBN-13 du livre.<br>
livre_date (YEAR) : Année de publication du livre.<br>
ISBN_verifie (BOOLEAN) : Indique si l'ISBN a été vérifié (par défaut FALSE).<br>
ISBN_defaut (VARCHAR(13)) : ISBN par défaut si aucun ISBN français n'a été trouvé.

#### 2. Table Editeurs
Description : Contient les informations sur les éditeurs des livres.<br>
Champs :<br>
editeur_id (INT, clé primaire) : Identifiant unique de l'éditeur.<br>
editeur_nom (VARCHAR(255)) : Nom de l'éditeur.<br>
Donnée par défaut : Un enregistrement avec editeur_id = 1 et editeur_nom = 'None' est ajouté lors de la création de la table.

#### 3. Table Thematiques
Description : Contient les thématiques associées aux livres.<br>
Champs :<br>
thematique_id (INT, clé primaire) : Identifiant unique de la thématique.<br>
thematique_nom (VARCHAR(255)) : Nom de la thématique.<br>
Donnée par défaut : Un enregistrement avec thematique_id = 1 et thematique_nom = 'None' est ajouté lors de la création de la table.

#### 4. Table Auteurs
Description : Contient les informations sur les auteurs des livres.<br>
Champs :<br>
auteur_id (INT, clé primaire) : Identifiant unique de l'auteur.<br>
auteur_nom (VARCHAR(255)) : Nom de l'auteur.<br>
Donnée par défaut : Un enregistrement avec auteur_id = 1 et auteur_nom = 'None' est ajouté lors de la création de la table.

### Tables de jonction (relations many to many)

#### 1. Table auteurs_livres
Description : Lie les livres à leurs auteurs.<br>
Champs :<br>
livre_id (INT) : Identifiant du livre (clé étrangère référençant Livres.livre_id).<br>
auteur_id (INT) : Identifiant de l'auteur (clé étrangère référençant Auteurs.auteur_id).<br>
Contraintes :<br>
Clé primaire composée : (livre_id, auteur_id).<br>
ON UPDATE CASCADE et ON DELETE CASCADE pour livre_id.<br>
ON UPDATE NO ACTION et ON DELETE NO ACTION pour auteur_id.

#### 2. Table editeurs_livres
Description : Lie les livres à leurs éditeurs.<br>
Champs :<br>
editeur_id (INT) : Identifiant de l'éditeur (clé étrangère référençant Editeurs.editeur_id).<br>
livre_id (INT) : Identifiant du livre (clé étrangère référençant Livres.livre_id).<br>
Contraintes :<br>
Clé primaire composée : (editeur_id, livre_id).<br>
ON UPDATE CASCADE et ON DELETE CASCADE pour livre_id.<br>
ON UPDATE NO ACTION et ON DELETE NO ACTION pour editeur_id.

#### 3. Table thematiques_livres
Description : Lie les livres à leurs thématiques.<br>
Champs :<br>
thematique_id (INT) : Identifiant de la thématique (clé étrangère référençant Thematiques.thematique_id).<br>
livre_id (INT) : Identifiant du livre (clé étrangère référençant Livres.livre_id).<br>
Contraintes :<br>
Clé primaire composée : (livre_id, thematique_id).<br>
ON UPDATE CASCADE et ON DELETE CASCADE pour livre_id.<br>
ON UPDATE NO ACTION et ON DELETE NO ACTION pour thematique_id.

## Utilisation de l'API
Dans le terminal, lancer l'API avec la commande suivante :<br>
uvicorn app:app --reload<br>
Dans le navigateur, en fonction de votre port :<br>
aller à http://127.0.0.1:8000/docs<br>
et suivre les instructions pour obtenir un token et pouvoir effectuer des requêtes