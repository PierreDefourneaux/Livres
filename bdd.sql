/*
CREER LA BASE DE DONNEES DANS L'INVITE DE COMMANDE :
Se mettre dans le dossier qui contient fichier.sql puis écrire la commande :
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" < bdd.sql -u root -p
Souvent le DROP DATABASE IF EXISTS db_bloc1; est interminable si je ne redemarre pas le PC avant. 
Il faut que j'explore les processus bloquant dans mysql


VERIFIER DANS SQL SHELL :
\connect root@localhost   (sans point-virgule)
SHOW databases;
use nom_de_la_base;
show tables;

VERIFIER DANS MySQL WORKBENCH :
Choisir la bonne "local instance mysql 8.0" (ici c'est root, localhost 3306)
Saisir le mot de passe
Les bases de données sont visibles dans l'onglet "schemas"

J'ai utilisé drawDB pour faciliter la conception de ce MPD
Il y a eu des modifications à faire
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
	`livre_note` VARCHAR(255),
	`livre_id` INT NOT NULL UNIQUE,
	`ISBN_10` VARCHAR(255) NOT NULL,
	`ISBN_13` VARCHAR(255) NOT NULL,
	`livre_date` VARCHAR(255),
	`ISBN_verifie` VARCHAR(255) NOT NULL,
	`ISBN_defaut` VARCHAR(255),
	PRIMARY KEY(`livre_id`)
);


CREATE TABLE `Editeurs` (
	`editeur_id` INT NOT NULL UNIQUE,
	`editeur_nom` VARCHAR(255) NOT NULL,
	PRIMARY KEY(`editeur_id`)
);


CREATE TABLE `Thematiques` (
	`thematique_id` INT NOT NULL UNIQUE,
	`thematique_nom` VARCHAR(255) NOT NULL,
	PRIMARY KEY(`thematique_id`)
);


CREATE TABLE `Auteurs` (
	`auteur_id` INT NOT NULL UNIQUE,
	`auteur_nom` VARCHAR(255) NOT NULL,
	PRIMARY KEY(`auteur_id`)
);


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
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `editeurs_livres`
ADD FOREIGN KEY(`livre_id`) REFERENCES `Livres`(`livre_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
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
ON UPDATE NO ACTION ON DELETE NO ACTION;

SELECT 'DATABASE CREATED' as 'INFO';