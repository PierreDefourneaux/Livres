from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify

from dotenv import load_dotenv
import os

from sqlalchemy import create_engine, text, Column, Integer, String, FLOAT, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker


app = Flask(__name__)

# Page d'accueil
@app.route("/", methods=["GET"])
def index():
    print("Page d'accueil du projet bloc 1 chargée")
    return render_template("index.html")

@app.route("/books", methods=["POST"])
def books():
    if request.method == "POST":
        print("Une méthode POST vient d'être exécutée pour accéder aux books")
        return render_template("books.html")

@app.route("/genres", methods=["POST"])
def genres():
    if request.method == "POST":
        print("LUne méthode POST vient d'être exécutée pour accéder aux genres")
        return render_template("genres.html")


load_dotenv()
user = os.getenv('USER')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
port = os.getenv('PORT')
database = os.getenv('DATABASE')

url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(user, password, host, port, database)
engine = create_engine(url)

Base = declarative_base()

if __name__ == '__main__':
 
    try:       
        conn = engine.connect()
        print(f"Connection to the {host} for user {user} created successfully.")
        Base.metadata.drop_all(bind = conn)
        Base.metadata.create_all(bind = conn)
        Session = sessionmaker(bind=conn)
    except Exception as ex:
        print("Connection could not be made due to the following error: \n", ex)

with engine.connect() as connection:
    result = connection.execute(text("SHOW DATABASES;"))


# # Cette classe définit les modèles qui correspondent aux
# # tables de la base de données. Toutes les classes héritent de Base.

# class Book(Base):
#     __tablename__ = 'books'
#     book_id = Column(Integer, primary_key=True, autoincrement=True)
#     book_title = Column(String(255), unique=True)
#     number_of_pages = Column(Integer)
#     release_date = Column(Date)
#     isbn10 = Column(Integer, unique=True)
#     isbn13 = Column(Integer, unique=True)

# class Author(Base):
#     __tablename__ = 'authors'
#     author_id = Column(Integer, primary_key=True, autoincrement=True)
#     author_name = Column(String(255), unique=True)

    
# class Publisher(Base):
#     __tablename__ = 'publishers'
#     publisher_id = Column(Integer, primary_key=True, autoincrement=True)
#     publisher_name = Column(String(255), unique=True)

# class Literary_genre(Base):
#     __tablename__= 'literary_genres'
#     literary_genre_id = Column(Integer, primary_key=True, autoincrement=True)
#     literary_genre_name = Column(String(255), unique=True)

# class Theme(Base):
#     __tablename__= 'themes'
#     theme_id = Column(Integer, primary_key=True, autoincrement=True)
#     theme_name = Column(String(255), unique=True)

# class Note(Base):
#     __tablename__= 'notes'
#     note_id = Column(Integer, primary_key=True, autoincrement=True)
#     note = Column(FLOAT, unique=True)

# user = 'root'
# password = 'ton_mot_de_passe'
# host = '127.0.0.1'
# port = 3306
# database = 'db_bloc1'
# url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(user, password, host, port, database)
# engine = create_engine(url)



if __name__ == '__main__':
    app.run(debug=True)