# app.py
from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv('MONGO_URI')
print(MONGO_URI)

client = MongoClient(MONGO_URI)
db = client.get_database('assemblerium') # ici db assemblerium (niveau au dessus de articles)

@app.route('/')
def index():
    assemblerium_data = list(db['articles'].find({})) # ici db collection articles
    return render_template('index.html', articles = assemblerium_data)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if "username" not in request.form or "password" not in request.form or "confirm_password" not in request.form:
            return render_template("register.html", erreur="Veuillez remplir tous les champs.")
        
        db_user = db["users"]
        new_user = db_user.find_one({"username": request.form["username"]})
        if new_user:
            return render_template("register.html", erreur="Nom d'utilisateur déjà pris.")
        else:
            if request.form["password"] == request.form["confirm_password"]:
                db_user.insert_one({
                    "username": request.form["username"],
                    "password": request.form["password"]
                })
                session["user_id"] = request.form["username"]
                return redirect(url_for("index"))
            else:
                return render_template("register.html", erreur="Les mots de passe ne correspondent pas.")
    return render_template("register.html")

@app.route('/login')
def login():
    return render_template('/front/login.html')
# articles = {}
# next_id = 1

# @app.route('/api/articles', methods=['GET'])
# def get_articles():
#     return jsonify(list(articles.values()))

# @app.route('/api/articles/<int:article_id>', methods=['GET'])
# def get_article(article_id):
#     if article_id in articles:
#         return jsonify(articles[article_id])
#     return jsonify({'error': 'Article non trouvé'}), 404

# @app.route('/api/articles', methods=['POST'])
# def create_article():
#     global next_id
#     data = request.json
#     article = {
#         'id': next_id,
#         'title': data.get('title', 'Sans titre'),
#         'blocks': data.get('blocks', []),
#         'created_at': datetime.now().isoformat(),
#         'updated_at': datetime.now().isoformat()
#     }
#     articles[next_id] = article
#     next_id += 1
#     return jsonify(article), 201

# @app.route('/api/articles/<int:article_id>', methods=['PUT'])
# def update_article(article_id):
#     if article_id not in articles:
#         return jsonify({'error': 'Article non trouvé'}), 404
    
#     data = request.json
#     articles[article_id]['title'] = data.get('title', articles[article_id]['title'])
#     articles[article_id]['blocks'] = data.get('blocks', articles[article_id]['blocks'])
#     articles[article_id]['updated_at'] = datetime.now().isoformat()
#     return jsonify(articles[article_id])

# @app.route('/api/articles/<int:article_id>', methods=['DELETE'])
# def delete_article(article_id):
#     if article_id in articles:
#         del articles[article_id]
#         return jsonify({'message': 'Article supprimé'})
#     return jsonify({'error': 'Article non trouvé'}), 404

app.run(host="0.0.0.0", port=81, debug=True)