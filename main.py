from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client.get_database('assemblerium')
TAGS = ["Algorithimique", "Mobile", "JV", "Web Development", "Cyberséccurité", "Data Science", "IA", "Cloud", "DevOps"]

@app.route('/')
def index():
    articles = list(db['articles'].find({}))
    return render_template('index.html', articles=articles)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if not username or not password or not confirm:
            return render_template("front/register.html", erreur="Tous les champs sont requis.")

        if password != confirm:
            return render_template("front/register.html", erreur="Les mots de passe ne correspondent pas.")

        if db["users"].find_one({"username": username}):
            return render_template("front/register.html", erreur="Nom d'utilisateur déjà pris.")

        db["users"].insert_one({
            "username": username,
            "password": password,
            "role": "user"
        })

        session["user_id"] = username
        session["role"] = "user"

        return redirect(url_for("index"))

    return render_template("front/register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db["users"].find_one({
            "username": username,
            "password": password
        })

        if user:
            session["user_id"] = username
            session["role"] = user.get("role", "user")
            return redirect(url_for("index"))

        return render_template("front/login.html", erreur="Identifiants incorrects.")

    return render_template('front/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/post/new_post')
def new_post():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template('front/new_post.html')

@app.route('/post/create', methods=["POST"])
def create_post():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title")
    text = request.form.get("text")
    image = request.files.get("image")

    image_path = ""

    if image and image.filename != "":
        filename = secure_filename(image.filename)
        upload_path = os.path.join(app.static_folder, "images", filename)
        image.save(upload_path)
        image_path = f"/static/images/{filename}"

    tags = request.form.getlist("tags")

    post = {
        "title": title,
        "text": text,
        "image": image_path,
        "created_at": datetime.now(),
        "author": session["user_id"],
        "tag": tags,
        "like": 0,
        "liked_by": []
    }

    db["articles"].insert_one(post)

    return redirect(url_for("index"))

@app.route('/post/like/<article_id>')
def like_post(article_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = session["user_id"]

    article = db["articles"].find_one({"_id": ObjectId(article_id)})

    if user in article.get("liked_by", []):
        return redirect(url_for("index"))
    
    db["articles"].update_one(
        {"_id": ObjectId(article_id)},
        {
            "$inc": {"like": 1},
            "$push": {"liked_by": user}
        }
    )

    return redirect(url_for("article", article_id=article_id))

@app.route('/admin')
def admin():
    if 'user_id' in session and session.get('role') == 'admin':
        articles = list(db['articles'].find({}))
        users = list(db['users'].find({}))
        return render_template('admin/home.admin.html', articles=articles, users=users)
    return "Accès refusé", 403

@app.route('/admin/update_role/<user_id>', methods=['POST'])
def update_role(user_id):
    if 'user_id' in session and session.get('role') == 'admin':
        new_role = request.form.get('role')

        db['users'].update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'role': new_role}}
        )

    return redirect(url_for('admin'))

@app.route('/admin/delete_user/<user_id>')
def delete_user(user_id):
    if 'user_id' in session and session.get('role') == 'admin':
        db["users"].delete_one({'_id': ObjectId(user_id)})

    return redirect(url_for('admin'))

@app.route('/admin/view_user/<user_id>')
def show_user(user_id):
    if 'user_id' in session and session.get('role') == 'admin':
        user = db["users"].find_one({'_id': ObjectId(user_id)})

        if not user:
            return redirect(url_for('admin'))

        return render_template('admin/view_user.html', user=user)

    return redirect(url_for('index'))

@app.route('/user')
def user_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db["users"].find_one({
        "username": session["user_id"]
    })

    if not user:
        return redirect(url_for("index"))

    return render_template("front/user.html", user=user)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)