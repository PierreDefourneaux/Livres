from datetime import datetime
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import sys
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os
import base64
from tqdm import tqdm

start_time = time.time()  

load_dotenv()

token_librarything_API = os.getenv('TOKEN_LIBRARYTHING_API')

print("################## SCRAPING #################### \nDébut de l'exécution du script :",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("Environnement virtuel requis : env_wsl_bloc_1.")
print("Environnement virtuel et Python utilisés =", sys.executable)


################################################################################################################
############################### DEFINITION DES FONCTIONS D'EXTRACTION DE DONNEES ###############################
################################################################################################################
################################################################################################################

def is_french_isbn(isbn):
    """Vérifie si un ISBN correspond à un ouvrage publié en France.

    Un ISBN est considéré comme français s'il possède l'un des préfixes suivants :
    - "9782" ou "97910" pour un ISBN-13
    - "2" pour un ISBN-10

    Paramètres :
        isbn (str) : Le numéro ISBN à analyser (avec ou sans séparateurs).

    Retourne :
        bool : True si l'ISBN est français, False sinon.
    """
    isbn = isbn.replace("-", "").replace(" ", "")
    if isbn.startswith("9782") or isbn.startswith("97910") or isbn.startswith("2"):
            return True
    return False

def find_french_isbn_in_list(isbns):
    """Recherche le premier ISBN français dans une liste.

    Un ISBN est considéré comme français s'il possède l'un des préfixes suivants :
    - "9782" ou "97910" pour un ISBN-13
    - "2" pour un ISBN-10

    Paramètres :
        isbns (list[str]) : Liste de numéros ISBN (avec ou sans séparateurs).

    Retourne :
        str | None : Le premier ISBN français trouvé, ou None si aucun n'est détecté.
    """
    count = 0
    while count < len(isbns):
        isbn = isbns[count]
        isbn = isbn.replace("-", "").replace(" ", "")
        if isbn.startswith("9782") or isbn.startswith("97910") or isbn.startswith("2"):
            return isbn
        count += 1
    return None

def get_isbn_with_librarything(token_librarything_API,title):
    """Récupère une liste d'ISBN pour un livre donné via l'API LibraryThing.

    Cette fonction interroge l'API LibraryThing à partir du titre d'un livre 
    et retourne une liste des ISBN associés.

    Paramètres :
        token_librarything_API (str) : Clé d'authentification pour l'API LibraryThing.
        title (str) : Titre du livre (écrit naturellement avec espaces).

    Retourne :
        list[str] | None : Liste des ISBN trouvés ou None en cas d'erreur.
    """
    title = title.replace(' ', '+')
    url = f"https://www.librarything.com/api/{token_librarything_API}/thingTitle/{title}"
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content.decode('utf-8'))
        liste = []
        for elem in root.iter("isbn"):
            liste.append(elem.text)
        return liste
    else :
        return None

def get_book_from_isbn(isbn):
    """Envoie une requête à LibraryThing pour récupérer la page d'un livre à partir de son ISBN.
    Cette fonction a été utile à l'exploration, elle ne retourne rien.

    Cette fonction effectue une requête HTTP vers LibraryThing en utilisant l'ISBN fourni 
    et indique si la requête a réussi ou échoué.

    Paramètres :
        isbn (str) : Numéro ISBN du livre.

    Retourne :
        None : Affiche un message en fonction du succès ou de l'échec de la requête.
    """
    url = f"https://www.librarything.com/isbn/{isbn}"
    response = requests.get(url)
    if response.status_code == 200:
        print("requete reussie, pret a scraper")
    else:
        print(f"Erreur lors de la requête https://www.librarything.com/isbn/ : {response.status_code}")

def translate_title_to_french(titre):
    """Traduit un titre de livre en français en utilisant GoogleTranslator.

    Cette fonction détecte automatiquement la langue d'origine et traduit 
    le titre en français.

    Paramètres :
        titre (str) : Titre du livre à traduire.

    Retourne :
        str : Titre traduit en français.
    """
    traduction = GoogleTranslator(source='auto', target='fr').translate(titre)
    return traduction

def google_books_api(title, maxresults = 15):
    """Interroge l'API Google Books pour récupérer des informations sur un livre.

    Cette fonction recherche un livre par son titre en interrogeant l'API Google Books
    et extrait les informations suivantes :
    - Le titre du premier résultat
    - Le nombre de pages du livre (si disponible)
    - Un ISBN français (si détecté)
    - Les auteurs
    - Les catégories/thèmes du livre
    - Le code de statut de la réponse HTTP

    Paramètres :
        title (str) : Titre du livre (les espaces sont autorisés).
        maxresults (int, optionnel) : Nombre maximal de résultats à récupérer (par défaut 15).

    Retourne :
        tuple : Contient les éléments suivants :
            - data (dict | None) : Données brutes retournées par l'API.
            - title (str | None) : Titre du premier livre trouvé.
            - page_count (int | None) : Nombre de pages du livre.
            - isbn_fr (str | None) : ISBN français détecté (ISBN-10 commençant par "2" ou ISBN-13 commençant par "9782"/"97910").
            - author (list[str] | None) : Liste des auteurs du livre.
            - theme (str | None) : Catégories/thèmes du livre.
            - status_code (int) : Code de statut HTTP de la réponse.
    """
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"intitle:{title}",
        "maxResults": maxresults
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "items" in data:
        ######################################################### Extraire le titre
        title = data["items"][0]["volumeInfo"]["title"]
        if not title :
            title = None
        ######################################################### Extraire le nombre de pages
        page_count = 0
        if data.get("items"):
            for livre in data["items"]:
                if livre.get("volumeInfo"):
                    volumeInfo = livre.get("volumeInfo")
                    if volumeInfo.get("pageCount"):
                        if volumeInfo.get("pageCount") > 5:
                            page_count = volumeInfo.get("pageCount")
        if not page_count:
            page_count = None
        ######################################################### Extraire un ISBN français
        isbn_fr = ""
        if data.get("items"):
            for livre in data["items"]:
                if livre.get("volumeInfo"):
                    volumeInfo = livre.get("volumeInfo")
                    if volumeInfo.get("industryIdentifiers"):
                        industryIdentifiers = volumeInfo.get("industryIdentifiers")
                        for i in industryIdentifiers :
                            if i.get("identifier"):
                                code = i.get("identifier")
                                if len(code) == 10 and code.startswith("2"):
                                    isbn_fr = code 
                                if code.startswith("9782") or code.startswith("97910"):
                                    isbn_fr = code
        if not isbn_fr:
            isbn_fr = None   
        ######################################################### Extraire l'auteur
        author = ""
        if data.get("items"):
            for livre in data["items"]:
                if livre.get("volumeInfo"):
                    volumeInfo = livre.get("volumeInfo")
                    if volumeInfo.get("authors"):
                        author = volumeInfo.get("authors")
        if not author:
            author = None

        ######################################################### Extraire les thèmes
        theme = ""
        if data.get("items"):
            for livre in data["items"]:
                if livre.get("volumeInfo"):
                    volumeInfo = livre.get("volumeInfo")
                    if volumeInfo.get("categories"):
                        theme = str(volumeInfo.get("categories"))
        if not theme:
            theme = None
        
        return data, title, page_count, isbn_fr, author, theme, response.status_code
    else : 
        return None, None, None, None, None, None, response.status_code

################################################################################################################
######################################### DEBUT DU CODE DE SCRAPING ############################################
################################################################################################################
################################################################################################################

# print("\nDébut du webscraping de Openlibrary.org")

titres = []
notes = []
auteurs = []
dates_de_publication = []
editeurs = []
nombres_de_pages = []
themes_liste = []
isbn10_français = []
isbn13_français = []
isbn_defaut = []
ISBN_verifie = []
images_openlibrary = []
print("Scraping des livres en vogue à cette heure sur Openlibrary")
for i in tqdm(range(1,11), desc="Scraping des 10 pages \"les livres en vogue du moment\" de Openlibrary.org"):
    url_scrap = f"https://openlibrary.org/trending/now?page={i}"
    response = requests.get(url_scrap)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        liens = soup.find_all("a", class_="results")
        # print("\n\n\nextraction des liens et redirection vers les livres de la page",i)
        for title in liens:
            url2 = f"""https://openlibrary.org/{title.get("href")}"""
            response2 = requests.get(url2)
            if response2.status_code == 200:
                soup2 = BeautifulSoup(response2.text, "html.parser")
                
                try:
                    titre = soup2.find("h1", itemprop="name").text
                    titres.append(titre)
                    # print("\nExtraction des informations du livre",titre)
                except Exception as e:
                    # print("Echec de récupération du titre dans\n\t\t\t",url2,"\n\t\t\t",e,"\n")
                    titres.append("indisponible")
                    titre = "indisponible"
                
                #exctraction des ISBN 10
                try:
                    isbn = soup2.find_all("dd", attrs={"itemprop": "isbn"})
                    french_isbn = ""
                    for number in isbn:
                        s = number.text
                        s = re.sub(r"[^A-Z0-9]", "", s)
                        if len(s) == 10: 
                            if is_french_isbn(s):
                                french_isbn = s
                            else:
                                def_isbn = s
                    if french_isbn:
                        value10 = french_isbn
                    else :
                        value10 = "indisponible"
                except Exception as e:
                    value10 = "indisponible"
                    
                isbn10_français.append(value10)

               #exctraction des ISBN 13
                try:
                    isbn = soup2.find_all("dd", attrs={"itemprop": "isbn"})
                    french_isbn = ""
                    def_isbn =""
                    for number in isbn:
                        s = number.text
                        s = re.sub(r"[^A-Z0-9]", "", s)
                        if len(s) == 13: 
                            if is_french_isbn(s):
                                french_isbn = s
                            else:
                                def_isbn = s
                    if french_isbn:
                        value13 = french_isbn
                    else :
                        value13 = "indisponible"
                except Exception as e:
                    value13 = "indisponible"
                    
                isbn13_français.append(value13)

                if def_isbn:
                    isbn_defaut.append(def_isbn)
                else:
                    def_isbn = "indisponible"
                    isbn_defaut.append(def_isbn)
                    
                if value10 == "indisponible" and value13 == "indisponible":
                    # print("""\tAucun ISBN français trouvé pendant le scraping d'Openlibrary.org.\n\t\tRequête à l'API Librarything en cours pour tenter de récupérer l'ISBN français.""")
                    res = get_isbn_with_librarything(token_librarything_API,titre)
                    if res:
                        # print("\t\tLibrarything propose",len(res),"ISBN...")
                        value = find_french_isbn_in_list(res)
                        if value:
                            if len(value) == 10:
                                value10 = value
                                isbn10_français.pop()
                                isbn10_français.append(value)
                                # print("\t\t...un ISBN 10 français a pu être extrait :",value)
                            if len(value) == 13:
                                value13 = value
                                isbn13_français.pop()
                                isbn13_français.append(value)
                                # print("\t\t... un ISBN 13 français a pu être extrait :",value)
                        if not value :
                            # print("\t\t... mais aucun n'est français.\n\t\tNouvelle tentative en cours vers l'API google books.")
                            a = google_books_api(titre)
                            if a[3]:
                                # print("\t\tRésultat avec google books =",a[3])
                                if a[3] == 10:
                                    value10 = a[3]
                                    isbn10_français.pop()
                                    isbn10_français.append(value10)
                                else:
                                    value13 = a[3]
                                    isbn13_français.pop()
                                    isbn13_français.append(value13)
                            else :
                                # print("\t\tGoogle books n'a pas trouvé d'ISBN français pour", titre)
                                # print("\t\tNouvelle tentative avec cette traduction du titre :", translate_title_to_french(titre))
                                res_translated = google_books_api(translate_title_to_french(titre),3)[3]
                                if res_translated:
                                    # print("\t\tAvec ce nouveau titre, Google books API a trouvé cet ISBN français:",res_translated)
                                    if res_translated == 10:
                                        value10 = res_translated
                                        isbn10_français.pop()
                                        isbn10_français.append(value10)
                                    else:
                                        value13 = res_translated
                                        isbn13_français.pop()
                                        isbn13_français.append(value13)
                                # else :
                                    # print("\t\tLa traduction du titre n'a pas donné de meilleurs résultats.")
                    else:
                        # print("\t\tAucun ISBN trouvé avec l'API de librarything.\n\t\tNouvelle tentative en cours vers l'API google books.")
                        a = google_books_api(titre)
                        if a[3]:
                            # print("\t\tRésultat avec google books =",a[3])
                            if a[3] == 10:
                                value10 = a[3]
                                isbn10_français.pop()
                                isbn10_français.append(value10)
                            else:
                                value13 = a[3]
                                isbn13_français.pop()
                                isbn13_français.append(value13)
                        else :
                            # print("\t\tGoogle books n'a pas trouvé d'ISBN français pour", titre)
                            # print("\t\tNouvelle tentative avec cette traduction du titre :", translate_title_to_french(titre))
                            a = google_books_api(translate_title_to_french(titre),3)[3]
                            if a:
                                # print("\t\tAvec ce nouveau titre, Google books API a trouvé cet ISBN français:",a)
                                if a == 10 :
                                    isbn10_français.pop(0)
                                    isbn10_français.append(a)
                                    value10 = a
                                else:
                                    isbn13_français.pop()
                                    isbn13_français.append(a)
                                    value13 = a
                            # else :
                                # print("\t\tLa traduction du titre n'a pas donné de meilleurs résultats.")
                                
                # if value10 == "indisponible" and value13 == "indisponible" and def_isbn == "indisponible":
                    # print("\t\tAucun isbn extrait.")

                ISBN_verifie.append("ISBN pas encore vérifié")
                #exctraction des notes    
                try:
                    note = soup2.find("span", itemprop="ratingValue").text
                    # note = re.sub(r"\(.*?\)", "", note)
                    notes.append(note)
                except Exception as e:
                    # print("\tEchec de récupération de la note.")
                    notes.append("indisponible")

                #extraction des auteurs
                try:
                    auteur = soup2.find("a", itemprop="author").text
                    if auteur :
                        auteurs.append(auteur)
                    else :
                        # print("\tPas d'auteur extrait depuis Openlibrary.")
                        a = str(google_books_api(titre)[4])
                        if a:
                            auteurs.append(a)
                            # print("\t\tAuteur récuépré via Google_books_API :",a)
                        else:
                            # print("\t\tEchec de récupération de l'auteur, même après une deuxième tentative sur google_books_API.")
                            auteurs.append("indisponible")
                except Exception as e:
                    # print("\tEchec de récupération de l'auteur.")
                    auteurs.append("indisponible")

                #extraction des dates de publication
                try:
                    date_de_publication = soup2.find("span", itemprop="datePublished").text
                    dates_de_publication.append(date_de_publication)
                except Exception as e:
                    # print("\tEchec de récupération de la date de publication.")
                    dates_de_publication.append("indisponible")

                #extraction des éditeurs
                try:
                    editeur = soup2.find("a", itemprop="publisher").text
                    editeurs.append(editeur)
                except Exception as e:
                    # print("\tEchec de récupération de l'éditeur.")
                    editeurs.append("indisponible")

                #extraction des nombres de pages
                try:
                    nombre_de_pages = soup2.find("span", itemprop="numberOfPages").text
                    if nombre_de_pages:
                        if int(nombre_de_pages) > 5: 
                            nombres_de_pages.append(int(nombre_de_pages))
                        else:
                            nombres_de_pages.append("indisponible")
                    else :
                        # print("\tPas de nombre de pages extrait depuis Openlibrary.")
                        a = google_books_api(titre)[2]
                        if a and int(a) > 5:
                            # print("\t\tNombre de pages récuépré via Google_books_API :",a)
                            nombres_de_pages.append(int(a))
                        else:
                            # print("\t\tEchec de récupération du nombre de pages, même après une deuxième tentative sur google_books_API.")
                            nombres_de_pages.append("indisponible")
                except Exception as e:
                    # print("\tEchec de récupération du nombre de pages.")
                    a = google_books_api(titre)[2]
                    if a and int(a) > 5:
                        # print("\t\tNombre de pages récupéré via Google_books_API :",a)
                        nombres_de_pages.append(int(a))
                    else:
                        # print("\t\tEchec de récupération du nombre de pages, même après une deuxième tentative sur google_books_API.")
                        nombres_de_pages.append("indisponible")
        
                #extraction des thèmes
                try:
                    themes_tags = soup2.find_all("a", attrs={"data-ol-link-track": "BookOverview|SubjectClick"})
                    themes_sous_liste = []
                    for tag in themes_tags :
                        themes_sous_liste.append(tag.text)
                    if themes_sous_liste:
                        themes_liste.append(themes_sous_liste)
                    else:
                        # print("\tEchec de récupération des thèmes")
                        theme = google_books_api(titre)[5]
                        if theme :
                            themes_liste.append(theme)
                            # print("\t\tThèmes récupérés via Google_books_API")
                        else:
                            themes_liste.append("indisponible")
                            # print("\t\tEchec également avec Google_books_API")
                except Exception as e:
                    # print("\tEchec de récupération des thèmes")
                    theme = google_books_api(titre)[5]
                    if theme :
                        themes_liste.append(theme)
                        # print("\t\tThèmes récupérés via Google_books_API")
                    else:
                        themes_liste.append("indisponible")
                        # print("\t\tEchec également avec Google_books_API")

                #récupération des images
                try:
                    boite_image = soup2.find("div", class_="illustration edition-cover")
                    img_tag = boite_image.find("img")
                    img_url = "https:" + img_tag["src"]
                    response_img = requests.get(img_url)
                    if response_img.status_code == 200 :
                        image_64 = base64.b64encode(response_img.content).decode('utf-8')
                        if image_64:
                            images_openlibrary.append(image_64)          
                        else:
                            images_openlibrary.append("indisponible")
                    else :
                        images_openlibrary.append("indisponible")
                except Exception as e:
                    # print("\tEchec de récupération de l'image dans\n\t\t",url2,"\n\t\t",e,"\n")
                    images_openlibrary.append("indisponible")
            else:
                print("\t!!redirection vers la description du livre ratée, erreur =",response2.status_code)
    else:
        print("\t!!", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "echec de la requete ",url_scrap, " status_code erreur =",response.status_code)

################################################################################################################
######################################### AGREGATION DES DONNEES ###############################################
################################################################################################################
################################################################################################################

themes = []
for i in themes_liste:
    themes.append(str(i))    

data_webscrap_a_nettoyer = {
    "livre_nom" : titres,
    "livre_note" : notes,
    "livre_nombre_de_pages" : nombres_de_pages,
    "livre_date" : dates_de_publication,
    "ISBN_10" : isbn10_français,
    "ISBN_13" : isbn13_français,
    "ISBN_defaut" : isbn_defaut,
    "ISBN_verifie" : ISBN_verifie,
    "thematique_nom" : themes,
    "editeur_nom" : editeurs,
    "auteur_nom" : auteurs,
    "images_openlibrary" : images_openlibrary
    }

print(len(titres),"titres")
print(len(notes),"notes")
print(len(nombres_de_pages),"nombres de pages")
print(len(dates_de_publication),"dates")
print(len(isbn10_français),"isbn 10")
print(len(isbn13_français),"isbn 13")
print(len(isbn_defaut),"isbn_defaut")
print(len(themes),"thèmes")
print(len(editeurs),"editeurs")
print(len(auteurs),"auteurs")
print(len(images_openlibrary),"images_openlibrary")

df_data_webscrap_a_nettoyer = pd.DataFrame(data_webscrap_a_nettoyer)

missing_livres = df_data_webscrap_a_nettoyer['livre_nom'].value_counts().get('indisponible', 0)
missing_notes = df_data_webscrap_a_nettoyer['livre_note'].value_counts().get('indisponible', 0)
missing_auteurs = df_data_webscrap_a_nettoyer['auteur_nom'].value_counts().get('indisponible', 0)
missing_dates = df_data_webscrap_a_nettoyer['livre_date'].value_counts().get('indisponible', 0)
missing_editeurs = df_data_webscrap_a_nettoyer['editeur_nom'].value_counts().get('indisponible', 0)
missing_pages = df_data_webscrap_a_nettoyer['livre_nombre_de_pages'].value_counts().get('indisponible', 0)
missing_themes = df_data_webscrap_a_nettoyer['thematique_nom'].value_counts().get('indisponible', 0)
missing_isbn = ((df_data_webscrap_a_nettoyer["ISBN_10"] == "indisponible") & (df_data_webscrap_a_nettoyer["ISBN_13"] == "indisponible")& (df_data_webscrap_a_nettoyer["ISBN_defaut"] == "indisponible")).sum()
missing_images = df_data_webscrap_a_nettoyer['images_openlibrary'].value_counts().get('indisponible', 0)
total_missing = int(missing_images)+int(missing_livres)+int(missing_notes)+int(missing_auteurs)+int(missing_dates)+int(missing_editeurs)+int(missing_pages)+int(missing_themes)+int(missing_isbn)

print("\nRapport de Webscraping : sur",len(df_data_webscrap_a_nettoyer), " livres:\n" )
print("\t\tTitres indisponibles =", missing_livres)
print("\t\tNotes indisponibles =", missing_notes)
print("\t\tAuteurs indisponibles =", missing_auteurs)
print("\t\tDates_de_publication indisponibles =", missing_dates)
print("\t\tEditeurs indisponibles =", missing_editeurs)
print("\t\tNombres de pages indisponibles =", missing_pages)
print("\t\tThèmes indisponibles =", missing_themes)
print("\t\tLivres sans aucun ISBN =", missing_isbn)
print("\t\tLivres sans image =", missing_images)

objectif = len(df_data_webscrap_a_nettoyer)*9
reussite = objectif - total_missing
success_rate = reussite / objectif*100
print("\n\t Taux de réussite des extractions =", success_rate,"%")
if success_rate >= 92:
    print("\n\t Excellent travail, Johnson.\n")
elif success_rate >= 86:
    print("\n\t Pas mal, Johnson.\n")
elif success_rate >= 78:
    print("\n\t C'est presque mauvais, Johnson.\n")
else :
    print("\n\t Je ne vous paye pas pour des résultats aussi mauvais, Johnson.\n")


#csv pour nettoyage automatisé
try:
    df_data_webscrap_a_nettoyer.to_csv('df_data_webscrap_a_nettoyer.csv', index=False)
    print('Le fichier "df_data_webscrap_a_nettoyer.csv" a bien été généré.')
except Exception as e:
    print(f"Erreur lors de la création du fichier CSV : {e}")


#csv pour archive
try:
    a = {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    a = re.sub("['{}]","",re.sub("[-: ]","_",str(a)))
    df_data_webscrap_a_nettoyer.to_csv(f'archives_csv/df_data_webscrap_a_nettoyer_{a}.csv', index=False)
    print('Le fichier csv d\'archive a bien été généré.')
except Exception as e:
    print(f"Erreur lors de la création du fichier d\'archive : {e}")

end_time = time.time()  
execution_time = (end_time - start_time)/60
print(f"Temps d'exécution : {execution_time:.0f} minutes")