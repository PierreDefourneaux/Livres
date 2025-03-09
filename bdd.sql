/*
CREER LA BASE DE DONNEES DANS L'INVITE DE COMMANDE :
Se mettre dans le dossier qui contient fichier.sql puis écrire la commande :
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" < bdd.sql -u root -p
Souvent le DROP DATABASE IF EXISTS est interminable si j'ai eu une erreur d'insertion avant.
Dans le shell, faire show processlist; puis kill "process bloquant"; (la transaction en "sleep" sur la BDD)

VERIFIER DANS SQL SHELL :
\connect root@localhost
SHOW databases;
use nom_de_la_base;
show tables;

STRUCTURE DE LA BASE DE DONNEES :
Tables principales
1. Table Livres
Description : Contient les informations principales sur les livres.
Champs :
livre_id (INT, clé primaire) : Identifiant unique du livre.
livre_nom (VARCHAR(255)) : Nom du livre (doit être unique).
livre_nombre_de_pages (VARCHAR(255)) : Nombre de pages du livre.
livre_note (DECIMAL(2,1)) : Note attribuée au livre.
ISBN_10 (VARCHAR(10)) : Numéro ISBN-10 du livre.
ISBN_13 (VARCHAR(13)) : Numéro ISBN-13 du livre.
livre_date (YEAR) : Année de publication du livre.
ISBN_verifie (BOOLEAN) : Indique si l'ISBN a été vérifié (par défaut FALSE).
ISBN_defaut (VARCHAR(13)) : ISBN par défaut si aucun ISBN français n'a été trouvé.

2. Table Editeurs
Description : Contient les informations sur les éditeurs des livres.
Champs :
editeur_id (INT, clé primaire) : Identifiant unique de l'éditeur.
editeur_nom (VARCHAR(255)) : Nom de l'éditeur.
Donnée par défaut : Un enregistrement avec editeur_id = 1 et editeur_nom = 'None' est ajouté lors de la création de la table.

3. Table Thematiques
Description : Contient les thématiques associées aux livres.
Champs :
thematique_id (INT, clé primaire) : Identifiant unique de la thématique.
thematique_nom (VARCHAR(255)) : Nom de la thématique.
Donnée par défaut : Un enregistrement avec thematique_id = 1 et thematique_nom = 'None' est ajouté lors de la création de la table.

4. Table Auteurs
Description : Contient les informations sur les auteurs des livres.
Champs :
auteur_id (INT, clé primaire) : Identifiant unique de l'auteur.
auteur_nom (VARCHAR(255)) : Nom de l'auteur.
Donnée par défaut : Un enregistrement avec auteur_id = 1 et auteur_nom = 'None' est ajouté lors de la création de la table.

Tables de jonction (relations many to many)

1. Table auteurs_livres
Description : Lie les livres à leurs auteurs.
Champs :
livre_id (INT) : Identifiant du livre (clé étrangère référençant Livres.livre_id).
auteur_id (INT) : Identifiant de l'auteur (clé étrangère référençant Auteurs.auteur_id).
Contraintes :
Clé primaire composée : (livre_id, auteur_id).
ON UPDATE CASCADE et ON DELETE CASCADE pour livre_id.
ON UPDATE NO ACTION et ON DELETE NO ACTION pour auteur_id.

2. Table editeurs_livres
Description : Lie les livres à leurs éditeurs.
Champs :
editeur_id (INT) : Identifiant de l'éditeur (clé étrangère référençant Editeurs.editeur_id).
livre_id (INT) : Identifiant du livre (clé étrangère référençant Livres.livre_id).
Contraintes :
Clé primaire composée : (editeur_id, livre_id).
ON UPDATE CASCADE et ON DELETE CASCADE pour livre_id.
ON UPDATE NO ACTION et ON DELETE NO ACTION pour editeur_id.

3. Table thematiques_livres
Description : Lie les livres à leurs thématiques.
Champs :
thematique_id (INT) : Identifiant de la thématique (clé étrangère référençant Thematiques.thematique_id).
livre_id (INT) : Identifiant du livre (clé étrangère référençant Livres.livre_id).
Contraintes :
Clé primaire composée : (livre_id, thematique_id).
ON UPDATE CASCADE et ON DELETE CASCADE pour livre_id.
ON UPDATE NO ACTION et ON DELETE NO ACTION pour thematique_id.

*/

SELECT 'DROPING ANCIENT DB_BLOC_1 DATABASE' as 'INFO';
DROP DATABASE IF EXISTS db_bloc1;

SELECT 'CREATING NEW DATABASE DB_BLOC_1' as 'INFO';
CREATE DATABASE IF NOT EXISTS db_bloc1;

USE db_bloc1;

SELECT 'CREATING TABLES' as 'INFO';

CREATE TABLE `Livres` (
	`livre_nombre_de_pages` VARCHAR(255),
	`livre_nom` VARCHAR(255) NOT NULL UNIQUE,
	`livre_note` DECIMAL(2,1),
	`livre_id` INT NOT NULL UNIQUE,
	`ISBN_10` VARCHAR(10),
	`ISBN_13` VARCHAR(13),
	`livre_date` YEAR,
	`ISBN_verifie` BOOLEAN NOT NULL DEFAULT FALSE,
	`ISBN_defaut` VARCHAR(13),
	PRIMARY KEY(`livre_id`)
);


CREATE TABLE `Editeurs` (
	`editeur_id` INT NOT NULL UNIQUE,
	`editeur_nom` VARCHAR(255),
	PRIMARY KEY(`editeur_id`)
);
INSERT INTO `Editeurs` (`editeur_id`, `editeur_nom`) VALUES (1, 'None');

CREATE TABLE `Thematiques` (
	`thematique_id` INT NOT NULL UNIQUE,
	`thematique_nom` VARCHAR(255),
	PRIMARY KEY(`thematique_id`)
);
INSERT INTO `Thematiques` (`thematique_id`, `thematique_nom`) VALUES (1, 'None');

CREATE TABLE `Auteurs` (
	`auteur_id` INT NOT NULL UNIQUE,
	`auteur_nom` VARCHAR(255),
	PRIMARY KEY(`auteur_id`)
);
INSERT INTO `Auteurs` (`auteur_id`, `auteur_nom`) VALUES (1, 'None');

CREATE TABLE `auteurs_livres` (
	`livre_id` INT NOT NULL,
	`auteur_id` INT NOT NULL,
	PRIMARY KEY(`livre_id`, `auteur_id`)
);


CREATE TABLE `editeurs_livres` (
	`editeur_id` INT NOT NULL,
	`livre_id` INT NOT NULL,
	PRIMARY KEY(`editeur_id`, `livre_id`)
);


CREATE TABLE `thematiques_livres` (
	`livre_id` INT NOT NULL,
	`thematique_id` INT NOT NULL,
	PRIMARY KEY(`livre_id`, `thematique_id`)
);


ALTER TABLE `thematiques_livres`
ADD FOREIGN KEY(`livre_id`) REFERENCES `Livres`(`livre_id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `editeurs_livres`
ADD FOREIGN KEY(`livre_id`) REFERENCES `Livres`(`livre_id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `editeurs_livres`
ADD FOREIGN KEY(`editeur_id`) REFERENCES `Editeurs`(`editeur_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE `auteurs_livres`
ADD FOREIGN KEY(`auteur_id`) REFERENCES `Auteurs`(`auteur_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE `thematiques_livres`
ADD FOREIGN KEY(`thematique_id`) REFERENCES `Thematiques`(`thematique_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE `auteurs_livres`
ADD FOREIGN KEY(`livre_id`) REFERENCES `Livres`(`livre_id`)
ON UPDATE CASCADE ON DELETE CASCADE;

SELECT 'DATABASE CREATED' as 'INFO';

