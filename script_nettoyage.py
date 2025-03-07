# Ce script gère le nettoyage et l'agrégation des données, y compris pour la première itération.

import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime
import csv
import pandas as pd
from unidecode import unidecode
import re
from deep_translator import GoogleTranslator
from tqdm import tqdm
import sys

print("################ NETTOYAGE ################\nDébut de l'exécution du script :",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

load_dotenv()

#####################################################################################################################################
##### MYSQL : RECUPERER LES DERNIERS ID ET LES VARIABLES DEJA PRESSENTES DANS LA BDD POUR GERER LES INSERTIONS ET LES DOUBLONS ######
#####################################################################################################################################
#####################################################################################################################################

# user = os.getenv('USER') Je n'arrive pas pour l'instant à gérer un conflit entre user = pierre pour WSL et user = root(ce qui est attendu)
user = 'root'
# pour les autres variables cachées ça marche, WSL va bien les chercher
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

query_1 = "SELECT MAX(livre_id) FROM livres;"
curseur.execute(query_1)
result = curseur.fetchone() 
current_livre_id = (result[0] or 0)  # Pour python 5 or 0 = 5. Ca permet de gérer le None de primo nettoyage

query_2 = "SELECT MAX(auteur_id) FROM auteurs;"
curseur.execute(query_2)
result = curseur.fetchone() 
current_auteur_id = (result[0] or 0)

query_3 = "SELECT MAX(editeur_id) FROM editeurs;"
curseur.execute(query_3)
result = curseur.fetchone() 
current_editeur_id = (result[0] or 0)

query_4 = "SELECT MAX(thematique_id) FROM thematiques;"
curseur.execute(query_4)
result = curseur.fetchone() 
current_thematique_id = (result[0] or 0)

livres_deja_dans_la_bdd  =[]
query_a = "select livre_nom from livres;"
curseur.execute(query_a)
for i in curseur:
    livres_deja_dans_la_bdd.append(i[0])

auteurs_deja_dans_la_bdd  =[]
query_b = "select auteur_nom from auteurs;"
curseur.execute(query_b)
for i in curseur:
    if i[0] != None:
        auteurs_deja_dans_la_bdd.append(i[0])

editeurs_deja_dans_la_bdd  =[]
query_c = "select editeur_nom from editeurs;"
curseur.execute(query_c)
for i in curseur:
    if i[0] != None:
        editeurs_deja_dans_la_bdd.append(i[0])

thematiques_deja_dans_la_bdd  =[]
query_d = "select thematique_nom from thematiques;"
curseur.execute(query_d)
for i in curseur:
    if i[0] != None:
        thematiques_deja_dans_la_bdd.append(i[0])

dico_auteurs_deja_presents = []
query_00 = "select * from auteurs;"
curseur.execute(query_00)
for i in curseur:
    dico_auteurs_deja_presents.append(i)
dico_auteurs_deja_presents = dict(dico_auteurs_deja_presents)

dico_editeurs_deja_presents = []
query_01 = "select * from editeurs;"
curseur.execute(query_01)
for i in curseur:
    dico_editeurs_deja_presents.append(i)
dico_editeurs_deja_presents = dict(dico_editeurs_deja_presents)

dico_themes_deja_presents = []
query_02 = "select * from thematiques;"
curseur.execute(query_02)
for i in curseur:
    dico_themes_deja_presents.append(i)
dico_themes_deja_presents = dict(dico_themes_deja_presents)

curseur.close()
connexion.close()

#####################################################################################################################################
##################################################### DEBUT DU NETTOYAGE ############################################################
#####################################################################################################################################
#####################################################################################################################################

df = pd.read_csv("df_data_webscrap_a_nettoyer.csv")
nombre_de_livres_au_début = len(df)
# Premier dataframe. Il enverra ses colonnes dans des dataframes secondaires, qui auront vocation à devenir spécifiquement chacun des
# 8 CSV d'insertion pour les 7 tables de la BDD MySQL + 1 collection d'images pour la BDD MongoDB.

df["livre_nom"] = df["livre_nom"].apply(
    lambda x : unidecode(x)
    )
df["livre_nom"] = df["livre_nom"].apply(
    lambda x : x[:255]
    )
df["livre_nom"] = df["livre_nom"].apply(
    lambda x : x.lower()
    )
df = df.drop_duplicates(subset=['livre_nom'])
df = df.drop(df[df['livre_nom'].isin(['mein kampf','my struggle'])].index)
df = df.reset_index(drop = True)

# C'est ici que l'ID est généré, après le drop duplicate par titre. Il reprend à n+1 avec n = current_livre_id
df["id"] = df.index + current_livre_id + 1

df["livre_note"] = df["livre_note"].apply(
    lambda x : re.sub(r"\(.*?\)", "", x)
    )

df["livre_date"] = df["livre_date"].apply(
    lambda x : re.findall(r'\d{4}', x)
    )

df["livre_date"] = df["livre_date"].apply(lambda x: x[0] if x else 0)
df["livre_date"] = df["livre_date"].fillna(0).astype(int)
df.loc[~df["livre_date"].between(1901, 2100), "livre_date"] = None #le format YEAR SQL considère valide la plage entre 1901 et 2155
df["livre_date"] = pd.to_datetime(df["livre_date"], format="%Y").dt.year
df["livre_date"] = df["livre_date"].replace({pd.NA: None, float("nan"): None})

df["livre_id"] = df["id"]

df["auteur_nom"] = df["auteur_nom"].apply(
    lambda x : unidecode(x).strip()
    )

df["editeur_nom"] = df["editeur_nom"].apply(
    lambda x : unidecode(x)
    )

df["thematique_nom"] = df["thematique_nom"].apply(
    lambda x : re.sub(r"[\[\]]", "", x)  
)
df["thematique_nom"] = df["thematique_nom"].apply(
    lambda x : x.split(",")
)
pd.set_option('future.no_silent_downcasting', True)
df.replace("indisponible", None, inplace=True)
df.replace('ISBN pas encore vérifié', 0, inplace=True)

# gestion des doublons par titre avec un masque booleen
masque = df["livre_nom"].isin(livres_deja_dans_la_bdd)
# Supprimer les lignes où le masque est True
df = df[~masque]
# A partir de là je sais que tous les "livre_id" resteront jusqu'à la fin du script.
# Je conclus donc que les tables de jonction comporteront, premières ou pas, tous ces "livre_id".
# Ce n'est pas le cas des 
# auteurs/editeurs/thematiques
# et
# auteurs/editeurs/thematiques_id
# qui pour certains seront des doublons de ce que j'avais déjà dans la BDD : ils seront droppés avant la fin du script.

if not df.empty:
    print("Le dernier webscraping apporte",len(df),"nouveaux livres (sur les",nombre_de_livres_au_début," qui ont été extraits).")
else:
    print("Tous les livres du dernier webscraping (",nombre_de_livres_au_début,") sont déjà connus dans la base de données. Aucun csv ne sera généré.")
    sys.exit()

#####################################################################################################################################
################################################ AGREGATION : UN DATAFRAME PAR TABLE ################################################
#####################################################################################################################################
#####################################################################################################################################

###########################################
################ df_livres ################
###########################################
df_livres = pd.DataFrame()
df_livres["livre_id"] = df["livre_id"]
df_livres["livre_nom"] = df["livre_nom"]
df_livres["livre_nombre_de_pages"] = df["livre_nombre_de_pages"]
df_livres["livre_note"] = df["livre_note"]
df_livres["ISBN_10"] = df["ISBN_10"]
df_livres["ISBN_13"] = df["ISBN_13"]
df_livres["ISBN_defaut"] = df["ISBN_defaut"]
df_livres["ISBN_verifie"] = df["ISBN_verifie"]
df_livres["livre_date"] = df["livre_date"]

###########################################
##### df_auteurs et df_auteurs_livres #####
###########################################
def assigne_un_auteur_id(auteur):
    """
    Attribue un identifiant unique à un auteur.

    Cette fonction recherche un auteur dans le dictionnaire `dico_auteurs_deja_presents` qui vient de la base de données. 
    Si l'auteur est trouvé, son identifiant existant est retourné. 
    Sinon, un nouvel identifiant est généré, enregistré dans le dictionnaire et retourné.
    
    Paramètres :
        auteur (str | None) : Nom de l'auteur. Si c'est None, l'auteur_id = 1 est retourné.

    Retourne :
        int : Identifiant unique de l'auteur.
    """

    global current_auteur_id  # Utilisation de la variable globale current_id = je vais la mettre à jour en dehors du scope de la fonction
    for auteur_id, auteur_nom in dico_auteurs_deja_presents.items(): # .items() déstructure le dictionnaire en donnant une vue sur des tuples
        if auteur == None:
            return 1
        if auteur_nom == auteur:
            return auteur_id
    current_auteur_id += 1   
    dico_auteurs_deja_presents[current_auteur_id] = auteur
    return current_auteur_id

df["auteur_id"] = df["auteur_nom"].apply(assigne_un_auteur_id)

df_auteurs = pd.DataFrame()
df_auteurs["auteur_nom"] = df["auteur_nom"]
df_auteurs["auteur_id"] = df["auteur_id"]

df_auteurs = df_auteurs.drop_duplicates(subset=["auteur_nom"])
dico_auteurs = df_auteurs.set_index("auteur_nom")["auteur_id"].to_dict()

df_auteurs_livres = pd.DataFrame() # c'est ma table de jonction

df_auteurs_livres["livre_id"] = df["livre_id"]
df_auteurs_livres["auteur_id"] = df["auteur_nom"] # j'ai pu me permettre de faire un drop duplicates sur df_auteurs car j'avais conservé la ligne dans ce df originel
df_auteurs_livres["auteur_id"] = df_auteurs_livres["auteur_id"].map(dico_auteurs)
# map remplace chaque valeur de "auteur_id" par son ID en cherchant dans dico_auteurs
# ! Si aucun nom ne correspond dans dico_auteurs, la valeur sera remplacée par NaN 
df_auteurs_livres = df_auteurs_livres.dropna()

# je peux maintenant finir df_auteurs en supprimant ce qui sera un doublon lors de l'insertion SQL

masque_auteurs = df_auteurs["auteur_nom"].isin(auteurs_deja_dans_la_bdd)
df_auteurs = df_auteurs[~masque_auteurs] # supprimer les lignes où le masque est True 
df_auteurs = df_auteurs.dropna(subset=["auteur_nom"])

#############################################
##### df_editeurs et df_editeurs_livres #####
#############################################
def assigne_un_editeur_id(editeur):
    """Attribue un identifiant unique à un éditeur.

    Cette fonction recherche un éditeur dans le dictionnaire `dico_editeurs_deja_presents` généré en interrogeant la base de données. 
    Si l'éditeur est trouvé, son identifiant existant est retourné. 
    Sinon, un nouvel identifiant est généré, enregistré dans le dictionnaire et retourné.

    Paramètres :
        editeur (str | None) : Nom de l'éditeur. Quand il n'y a pas d'éditeur, l'editeur_id 1 est retourné.

    Retourne :
        int : Identifiant unique de l'éditeur.
    """
    global current_editeur_id  
    for editeur_id, editeur_nom in dico_editeurs_deja_presents.items(): 
        if editeur == None:
            return 1
        if editeur_nom == editeur:
            return editeur_id
    current_editeur_id += 1 
    dico_editeurs_deja_presents[current_editeur_id] = editeur
    return current_editeur_id

df_editeurs = pd.DataFrame()
df_editeurs["editeur_id"] = df["editeur_nom"].apply(assigne_un_editeur_id)
df_editeurs["editeur_nom"] = df["editeur_nom"]
df_editeurs["conservation_temporaire_de_livre_id"]= df["livre_id"]

df_editeurs_livres = pd.DataFrame()
df_editeurs_livres["editeur_id"] = df_editeurs["editeur_id"]
df_editeurs_livres["livre_id"] = df_editeurs["conservation_temporaire_de_livre_id"]
df_editeurs_livres = df_editeurs_livres.dropna()
df_editeurs_livres.drop_duplicates()

masque_editeurs = df_editeurs["editeur_nom"].isin(editeurs_deja_dans_la_bdd)

df_editeurs = df_editeurs[~masque_editeurs]
df_editeurs = df_editeurs.drop(columns="conservation_temporaire_de_livre_id")
df_editeurs = df_editeurs.drop_duplicates(subset=["editeur_nom"])
df_editeurs = df_editeurs.dropna()

###################################################
##### df_thematiques et df_thematiques_livres #####
###################################################
def assigne_un_thematique_id(thematique):
    """Attribue un identifiant unique à une thématique.

    Cette fonction recherche une thématique dans le dictionnaire `dico_themes_deja_presents` généré via la base de données. 
    Si la thématique est trouvée, son identifiant existant est retourné. 
    Sinon, un nouvel identifiant est généré, enregistré dans le dictionnaire et retourné.

    Paramètres :
        thematique (str | None) : Nom de la thématique. S'il n'y a pas de thématique, l'id 1 est retourné.

    Retourne :
        int : Identifiant unique de la thématique."""
    global current_thematique_id  
    for thematique_id, thematique_nom in dico_themes_deja_presents.items(): 
        if thematique == None:
            return 1
        if thematique_nom == thematique:
            return thematique_id
    current_thematique_id += 1 
    dico_themes_deja_presents[current_thematique_id] = thematique
    return current_thematique_id

def translate_tag_to_french(tag):
    """Traduit un tag/thématique en français.

    Cette fonction détecte automatiquement la langue d'origine du tag et 
    retourne la traduction en français à l'aide de GoogleTranslator.

    Paramètres :
        tag (str) : Tag ou thématique à traduire.

    Retourne :
        str : Traduction du tag en français.
    """
    traduction = GoogleTranslator(source='auto', target='fr').translate(tag)
    return traduction


future_colonne = []
for i in range(len(df)):
    ligne = []
    x = int(df["livre_id"].iloc[i])
    for j in df["thematique_nom"].iloc[i][:10]:
        tuples = (x,j)
        ligne.append(tuples)
    future_colonne.append(ligne)

df["thematique_tuples"] = future_colonne
tqdm.pandas(desc="Traduction des tags")
def traite_la_liste_de_tags(x):
    liste=[]
    for i in x:
        tag = i[1]
        tag = unidecode(tag.lower())
        tag = translate_tag_to_french(tag)
        tag = re.sub("[éèêë]","e",tag)
        tag = re.sub("[âà]","a",tag)
        tag = re.sub("[ûü]","u",tag)
        tag = re.sub("[ôö]","o",tag)
        tag = re.sub("[^a-zA-Z çïœŒ']","",tag)
        tag = re.sub("^'|'$", "", tag)
        tag = re.sub("^'|'$", "", tag)
        tag = tag.lower()
        tag = tag.lstrip()
        tag = tag.rstrip()
        if "abus" in tag:
            tag = "criminalite"
        tag = i[0],tag
        liste.append(tag)
    liste = list(set(liste))
    return liste

df["thematique_tuples"] = df["thematique_tuples"].progress_apply(traite_la_liste_de_tags)

df_thematiques = pd.DataFrame()
thematiques_du_dataset = []
conservation_des_livre_id = []
for i in range(len(df)):
    x = df["thematique_tuples"].iloc[i]
    for y in x:
        thematiques_du_dataset.append(y[1])
        conservation_des_livre_id.append(y[0])

df_thematiques["thematique_nom"] = pd.DataFrame(thematiques_du_dataset)
df_thematiques["conservation_temporaire_de_livre_id"] = pd.DataFrame(conservation_des_livre_id)
df_thematiques = df_thematiques.sort_values(by="thematique_nom")
df_thematiques = df_thematiques.reset_index(drop = True)
df_thematiques["thematique_id"] = df_thematiques["thematique_nom"].apply(assigne_un_thematique_id)
dico_thematiques = df_thematiques.set_index("thematique_nom")["thematique_id"].to_dict()

df_thematiques_livres = pd.DataFrame()
df_thematiques_livres["livre_id"] = df_thematiques["conservation_temporaire_de_livre_id"]
df_thematiques_livres["thematique_id"] = df_thematiques["thematique_id"]
df_thematiques_livres = df_thematiques_livres.dropna()
df_thematiques_livres = df_thematiques_livres.drop_duplicates()

df_thematiques = df_thematiques.drop_duplicates(subset="thematique_nom")
df_thematiques = df_thematiques.drop(columns="conservation_temporaire_de_livre_id")

masque_thematiques = df_thematiques["thematique_nom"].isin(thematiques_deja_dans_la_bdd)
df_thematiques = df_thematiques[~masque_thematiques] # supprimer les lignes où le masque est True 
df_thematiques = df_thematiques.dropna(subset=["thematique_nom"]) # préventif

#################################
########### df_images ###########
#################################
df_images = pd.DataFrame()
df_images["image"] = df["images_openlibrary"]
df_images["image_id"] = df["id"]
df_images = df_images.fillna("indisponible")

#####################################################################################################################################
############################################### GENERATION DES CSV POUR CHAQUE TABLE ################################################
#####################################################################################################################################
#####################################################################################################################################

#csv pour insertion automatisée
df_livres.to_csv('table_livres.csv', index=False)
df_auteurs.to_csv('table_auteurs.csv', index=False)
df_editeurs.to_csv('table_editeurs.csv', index=False)
df_thematiques.to_csv('table_thematiques.csv', index=False)
df_auteurs_livres.to_csv('table_auteurs_livres.csv', index=False)
df_thematiques_livres.to_csv('table_thematiques_livres.csv', index=False)
df_editeurs_livres.to_csv('table_editeurs_livres.csv', index=False)
df_images.to_csv('collection_images.csv', index=False)

#csv d'insertion pour archive
a = {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
a = re.sub("['{}]","",re.sub("[-: ]","_",str(a)))

df_livres.to_csv(f'archives_csv/table_livres{a}.csv', index=False)
df_auteurs.to_csv(f'archives_csv/table_auteurs{a}.csv', index=False)
df_editeurs.to_csv(f'archives_csv/table_editeurs{a}.csv', index=False)
df_thematiques.to_csv(f'archives_csv/table_thematiques{a}.csv', index=False)
df_auteurs_livres.to_csv(f'archives_csv/table_auteurs_livres{a}.csv', index=False)
df_thematiques_livres.to_csv(f'archives_csv/table_thematiques_livres{a}.csv', index=False)
df_editeurs_livres.to_csv(f'archives_csv/table_editeurs_livres{a}.csv', index=False)
df_images.to_csv(f'archives_csv/collection_images{a}.csv', index=False)

print("Les fichier csv pour les insertions dans les tables ont bien été générés.")
print("\nFin de l'exécution du script de nettoyage :",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))