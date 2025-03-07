# Pour lancer l'application, se mettre dans le terminal :
# uvicorn app:app --reload

import os
import uvicorn
import jwt
import datetime
import mysql.connector
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, Query, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional


# Charger les variables d'environnement 
load_dotenv()

# Récupérer les variables d'environnement MySQL
user = os.getenv('USER')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
database = os.getenv('DATABASE')
SECRET_KEY = os.getenv("SECRET_KEY")
API_PASSWORD = os.getenv("API_PASSWORD")

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









# # Page d'accueil
# @app.get("/", response_class=HTMLResponse)
# def home(request: Request):
#     # Chargement du fichier HTML depuis le dossier templates
#     file_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
#     with open(file_path, 'r', encoding='utf-8') as f:
#         content = f.read()
#     return HTMLResponse(content=content)

# # Fonction pour récupérer un livre depuis la base de données
# def get_livre_from_id(id: int):
#     cursor.execute(f"SELECT livre_nom, ISBN_defaut FROM livres WHERE livre_id = {id}")
#     livres = [{"livre": row[0], "isbn": row[1]} for row in cursor.fetchall()]
#     return livres

# @app.get("/livres/{id}", response_class=HTMLResponse)
# def get_livre(id: int, request: Request):
#     """Route pour afficher un livre avec son ISBN selon son ID"""
#     livre = get_livre_from_id(id)  # Appel de la fonction pour récupérer le livre
#     if not livre:
#         return {"error": "Livre non trouvé"}  # Gestion de cas où le livre n'existe pas
#     return templates.TemplateResponse("result.html", {"request": request, "livre": livre[0]})

# Lancer l'application
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)



# asynch def
#await (verifiy identification)
