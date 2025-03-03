/*
CREER LA BASE DE DONNEES DANS L'INVITE DE COMMANDE :
Se mettre dans le dossier qui contient fichier.sql puis écrire la commande :
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" < bdd.sql -u root -p
Souvent le DROP DATABASE IF EXISTS est interminable si j'ai eu une erreur d'insertion avant.
Dans le shell, faire show processlist; puis kill "process bloquant"; (la transaction en "sleep" sur la BDD)

VERIFIER DANS SQL SHELL :
\connect root@localhost   (sans point-virgule)
SHOW databases;
use nom_de_la_base;
show tables;

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