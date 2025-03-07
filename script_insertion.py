# MEMO : CREER LA BASE DE DONNEES DANS L'INVITE DE COMMANDE :
# Se mettre dans le dossier qui contient fichier.sql puis écrire la commande :
# "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" < bdd.sql -u root -p

from datetime import datetime
import mysql.connector
import os
from dotenv import load_dotenv
import csv
import pandas as pd
import numpy as np
import pymongo
from pymongo import MongoClient
print("\n################# INSERTION ####################\nExécution du script :",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
load_dotenv()

################################################################### Partie MySQL
user = os.getenv('USER')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
database = os.getenv('DATABASE')

connexion = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)
curseur = connexion.cursor()
# Le curseur est utilisé pour exécuter des requêtes SQL
# curseur.execute("select * from livres;")
# for i in curseur:
#      print(i[0])

    
def remplir_sql(table : str, csv : str, connexion):
    """Charge les données d'un fichier CSV dans une table MySQL.

    Cette fonction prend un fichier CSV et insère ses données dans une table spécifiée de la base de données.
    Elle gère la conversion des types de données pour s'assurer que les valeurs manquantes (NaN) sont converties en `None`,
    ce qui est compatible avec MySQL. Des ajustements spécifiques sont effectués sur certaines colonnes en fonction du 
    fichier CSV source, notamment pour le traitement des ISBN.

    Paramètres :
        table (str) : Le nom de la table MySQL dans laquelle insérer les données.
        csv (str) : Le chemin vers le fichier CSV à importer.
        connexion : Connexion active à la base de données MySQL, utilisant `mysql.connector`.
    """
    df = pd.read_csv(csv)
    if csv == "table_livres.csv":
        df["ISBN_defaut"] = df["ISBN_defaut"].astype("str") #df["ISBN_defaut"] ressort des floats. Il faut traiter ça
        def modify_isbn(value):
            try:
                return value[:-2] if float(value) > 5 else value
            except ValueError:
                return value
        df["ISBN_defaut"] = df["ISBN_defaut"].apply(modify_isbn)
        df["ISBN_defaut"] = df["ISBN_defaut"].replace("nan", None)
        df["ISBN_10"] = df["ISBN_10"].astype("str")
        df["ISBN_10"] = df["ISBN_10"].apply(modify_isbn)
        df["ISBN_10"] = df["ISBN_10"].replace("nan", None)
        df["livre_nombre_de_pages"] = df["livre_nombre_de_pages"].astype("object")
        df["livre_note"] = df["livre_note"].astype("object")
        df["ISBN_verifie"] = df["ISBN_verifie"].astype(bool)
        df["livre_date"] = df["livre_date"].astype("object")
        df = df.where(pd.notna(df), None) # where(condition, autre_valeur) conserve les valeurs condition == True sinon remplace par autre_valeur
    else:
        df = df.where(pd.notna(df), None) 
        
    # Récupération des colonnes du dataframe au format string pour définir les colonnes cibles dans la requête sql
    colonnes = ', '.join(df.columns)
    # On génère le bon nombre de placeholders (les %s) au format string pour définir les valeurs à insérer dans la requête sql
    placeholders = ', '.join(['%s'] * len(df.columns))
    sql = f"INSERT INTO {table} ({colonnes}) VALUES ({placeholders})"
    # Définition des valeurs avec des tuples :
    # df.itertuples() est une méthode qui parcourt un DataFrame et extrait les lignes sous forme de tuples, 
    # ce qui est parfait pour executemany()
    valeurs = [tuple(row) for row in df.itertuples(index=False, name=None)]
    curseur = connexion.cursor()
    curseur.executemany(sql, valeurs)
    connexion.commit()
    curseur.close()
    print("Inserts réussis dans",table)

remplir_sql("Livres", "table_livres.csv", connexion)
remplir_sql("Auteurs", "table_auteurs.csv", connexion)
remplir_sql("Editeurs", "table_editeurs.csv", connexion)
remplir_sql("Thematiques", "table_thematiques.csv", connexion)
remplir_sql("auteurs_livres", "table_auteurs_livres.csv", connexion)
remplir_sql("editeurs_livres", "table_editeurs_livres.csv", connexion)
remplir_sql("thematiques_livres", "table_thematiques_livres.csv", connexion)

connexion.close()

################################################################### Partie MongoDB
host = os.getenv('MONGOHOST')
port = int(os.getenv('MONGOPORT'))
database = os.getenv('MONGODATABASE')
collection = os.getenv('MONGOCOLLECTION')

client = MongoClient(host, port)
db = client[database]
images = db[collection]

def remplir_mongo(csv : str):
    """Remplit la BDD locale MongoDB avec les images du fichier CSV issu du webscraping."""
    df = pd.read_csv(csv)
    for i in range(len(df)):
        dico = {
            f"image_id" : int(df['image_id'].loc[i]),
            f"image" : str(df['image'].loc[i]),
            }
        x = images.insert_one(dico)
    print(len(df),"Images insérées dans MongoDB")

remplir_mongo("collection_images.csv")