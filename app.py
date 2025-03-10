# Pour lancer l'application, se mettre dans le terminal :
# uvicorn app:app --reload

import os
import uvicorn
import jwt
import datetime
import mysql.connector
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, Query, Depends, HTTPException, Header, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pymongo import MongoClient

# Charger les variables d'environnement 
load_dotenv()

# Récupérer les variables d'environnement MySQL
user = os.getenv('USER')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
database = os.getenv('DATABASE')
SECRET_KEY = os.getenv("SECRET_KEY")
API_PASSWORD = os.getenv("API_PASSWORD")

# Connexion à la base de données MongoDB
mongohost = os.getenv('MONGOHOST')
mongoport = os.getenv('MONGOPORT')
mongodatabase = os.getenv('MONGODATABASE')
mongocollection = os.getenv('MONGOCOLLECTION')
client = MongoClient(f"mongodb://{mongohost}:{mongoport}/")
db = client[f"{mongodatabase}"]
collection = db[f"{mongocollection}"]

# Configuration de la sécurité
security = HTTPBearer()

# Modèle pour l'authentification
class TokenRequest(BaseModel):
    password: str
    duration: Optional[int] = 3600  # Durée en secondes (1h par défaut)


description = """
Bienvenue sur l'API du projet de recommandation de livres.
## Comment faire des requêtes sur l'API ?
### 1. Obtenir un token
- Obtenez un token en ouvrant l'onglet de la méthode "POST - generate token" ci-dessous
- Cliquez sur "try it out" et remplissez le champ password avec le mot de passe	(&#x1F648; librairie)
- Cliquez sur "execute" et vous obtiendrez le token en scrollant jusqu'à "Response body"
- Copiez-collez-le dans authorize &#x2198;  
- Vous pourrez ensuite éxécuter les requêtes des routes plus bas
"""

# Initialisation de FastAPI et Jinja2 pour les templates
app = FastAPI(
    title = "API Livres",
    description = description
)
templates = Jinja2Templates(directory="templates")


def create_jwt(duration: int) -> str:
    """
    ## Fonction qui permet de générer un token JWT
    - **param duration :** Durée de validité du token en secondes
    - **return :** Token JWT encodé
    """
    expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)
    return jwt.encode(
        {"exp": expiration},
        SECRET_KEY,
        algorithm="HS256"
    )

@app.post("/token")
def generate_token(request: TokenRequest):
    """
    ## Route qui permet de générer un token pour un utilisateur qui saisit son mot de passe
    - **param request:** Objet TokenRequest contenant le mot de passe et la durée
    - **return:** Token JWT
    """
    if request.password != API_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    token = create_jwt(request.duration)
    return {"token": token}

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Fonction qui permet de vérifier le token JWT
    
    :param credentials: Credentials fournis via le bearer token
    :return: None
    :raises: HTTPException si le token est invalide ou expiré
    """
    try:
        jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    


def get_db_connection():
    """
    Fonction qui permet de se connecter à la base de données MySQL    
    - **return :** Objet connexion à la base de données
    """
    return mysql.connector.connect(
        user=user,
        password=password,
        host=host,
        database=database
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False) # retirer de la doc
async def home(request: Request):
    """Page d'accueil de l'API"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/livres")
async def get_livres(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    livre_id: Optional[int] = Query(None, alias="livre_id"),
    limit: Optional[int] = Query(10, alias="limit")
):
    """
    ## Route qui permet de récupérer toutes les informations d'un livre en fonction de l'id
    - **param livre_id :** int = id du livre
    - **param limit :** int = Nombre de livres limite à retourner
    - **return :** Liste des livres
    """
    # Vérification du token
    await verify_token(credentials)
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM livres WHERE 1=1"
    params = []


    if livre_id:
        query += " AND livre_id = %s"
        params.append(livre_id)

    query += " LIMIT %s"
    params.append(limit)

    cursor.execute(query, params)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results

@app.get("/auteurs")
async def get_auteurs(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: Optional[int] = Query(10, alias="limit")
):
    """
    ## Route qui permet de récupérer tous les auteurs connus dans la base de données
    - **param limit :** int = Nombre d'auteurs limite à retourner
    - **return :** Liste des noms d'auteurs, et auteur_id associé
    """
    # Vérification du token
    await verify_token(credentials)
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM auteurs LIMIT %s"
    cursor.execute(query, (limit,))

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results

@app.get("/editeurs")
async def get_editeurs(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: Optional[int] = Query(10, alias="limit")
):
    """
    ## Route qui permet de récupérer tous les editeurs connus dans la base de données
    - **param limit :** int = Nombre d'editeurs limite à retourner
    - **return :** Liste des noms d'editeurs, et editeur_id associé
    """
    # Vérification du token
    await verify_token(credentials)
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM editeurs LIMIT %s"
    cursor.execute(query, (limit,))

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results

@app.get("/thematiques")
async def get_thematiques(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: Optional[int] = Query(10, alias="limit")
):
    """
    ## Route qui permet de récupérer toutes les thématiques connues dans la base de données
    - **param limit :** int = Nombre de thématiques limite à retourner
    - **return :** Liste des noms de thématiques, et thematique_id associé
    """
    # Vérification du token
    await verify_token(credentials)
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM thematiques LIMIT %s"
    cursor.execute(query, (limit,))

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results

@app.get("/livres_par_auteur")
async def get_livres_par_auteur(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auteur_nom: Optional[str] = Query(None, alias="auteur_nom"),
    limit: Optional[int] = Query(10, alias="limit")
):
    """
    ## Route qui permet de récupérer tous les noms de livre d'un même auteur
    - **param auteur_nom :** string = nom de l'auteur
    - **param limit :** int = Nombre de livres limite à retourner
    - **return :** Liste des livres
    """
    # Vérification du token
    await verify_token(credentials)
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT livres.livre_id, livres.livre_nom
    FROM livres
    INNER JOIN auteurs_livres ON livres.livre_id = auteurs_livres.livre_id
    INNER JOIN auteurs ON auteurs_livres.auteur_id = auteurs.auteur_id
    WHERE 1=1"""
    params = []


    if auteur_nom:
        query += " AND auteurs.auteur_nom = %s"
        params.append(auteur_nom)

    query += " LIMIT %s"
    params.append(limit)

    cursor.execute(query, params)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results

@app.get("/livres_par_editeur")
async def get_livres_par_editeur(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    editeur_nom: Optional[str] = Query(None, alias="editeur_nom"),
    limit: Optional[int] = Query(10, alias="limit")
):
    """
    ## Route qui permet de récupérer tous les noms de livre d'un même éditeur
    - **param editeur_nom :** string = nom de l'éditeur
    - **param limit :** int = Nombre de livres limite à retourner
    - **return :** Liste des livres
    """
    # Vérification du token
    await verify_token(credentials)
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT livres.livre_id, livres.livre_nom
    FROM livres
    INNER JOIN editeurs_livres ON livres.livre_id = editeurs_livres.livre_id
    INNER JOIN editeurs ON editeurs_livres.editeur_id = editeurs.editeur_id
    WHERE 1=1"""
    params = []


    if editeur_nom:
        query += " AND editeurs.editeur_nom = %s"
        params.append(editeur_nom)

    query += " LIMIT %s"
    params.append(limit)

    cursor.execute(query, params)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results

@app.get("/livres_par_thematique")
async def get_livres_par_thematique(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    thematique_nom: Optional[str] = Query(None, alias="thematique_nom"),
    limit: Optional[int] = Query(10, alias="limit")
):
    """
    ## Route qui permet de récupérer tous les noms de livre d'une même thematique
    - **param thematique_nom :** string = nom de la thématique
    - **param limit :** int = Nombre de livres limite à retourner
    - **return :** Liste des livres
    """
    # Vérification du token
    await verify_token(credentials)
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT livres.livre_id, livres.livre_nom
    FROM livres
    INNER JOIN thematiques_livres ON livres.livre_id = thematiques_livres.livre_id
    INNER JOIN thematiques ON thematiques_livres.thematique_id = thematiques.thematique_id
    WHERE 1=1"""
    params = []


    if thematique_nom:
        query += " AND thematiques.thematique_nom = %s"
        params.append(thematique_nom)

    query += " LIMIT %s"
    params.append(limit)

    cursor.execute(query, params)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results

# depuis mongoDB
@app.get("/image/{image_id}")
async def get_image(
    image_id : int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    """
    ## Route qui permet de récupérer une image stockée en base 64 dans MongoDB
    - **param image_id :** int = même id que celui du livre dont on veut récupérer l'image encodée
    - **return :** Image encodée

    Lire une image base 64 :
    ```python
    import base64
    from io import BytesIO
    from PIL import Image

    image_base64 = ""
    image_bytes = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_bytes))
    image.show()
    ```
    """
    await verify_token(credentials)

    document = collection.find_one({"image_id": image_id}, {"_id": 0})

    return document

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)