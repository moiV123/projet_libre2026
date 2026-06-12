import uuid
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from datetime import datetime
import os

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client.get_database("assemblerium")

TAGS = [
    "Algorithmique",
    "Mobile",
    "JV",
    "Web Development",
    "Cybersécurité",
    "Data Science",
    "IA",
    "Cloud",
    "DevOps"
]

@app.route("/")
def index():

    articles = list(
        db["articles"]
        .find({})
        .sort("created_at", -1)
    )

    return render_template(
        "index.html",
        articles=articles
    )

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password or not confirm_password:
            return render_template(
                "front/register.html",
                erreur="Tous les champs sont obligatoires."
            )

        if password != confirm_password:
            return render_template(
                "front/register.html",
                erreur="Les mots de passe ne correspondent pas."
            )

        existing_user = db["users"].find_one({
            "username": username
        })

        if existing_user:
            return render_template(
                "front/register.html",
                erreur="Nom d'utilisateur déjà utilisé."
            )

        db["users"].insert_one({
            "username": username,
            "password": password,
            "role": "user"
        })

        session["user_id"] = username
        session["role"] = "user"

        return redirect(url_for("index"))

    return render_template("front/register.html")

@app.route("/login", methods=["GET", "POST"])
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

        return render_template(
            "front/login.html",
            erreur="Identifiants incorrects."
        )

    return render_template("front/login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))

@app.route("/user")
def user_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db["users"].find_one({
        "username": session["user_id"]
    })

    if not user:
        return redirect(url_for("index"))

    return render_template(
        "front/user.html",
        user=user
    )

@app.route("/post/new_post")
def new_post():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "front/new_post.html",
        tags=TAGS
    )

@app.route("/post/create", methods=["POST"])
def create_post():
    if "user_id" not in session:
        return redirect(url_for("login"))

    image = request.files.get("image")
    print("=== IMAGE DEBUG ===")
    print(f"image: {image}")
    print(f"filename: {image.filename if image else 'NO IMAGE'}")
    print(f"content_type: {image.content_type if image else 'NO IMAGE'}")
    print("===================")

    title = request.form.get("title")
    image = request.files.get("image")
    tags = request.form.getlist("tags")

    blocks_text = request.form.getlist("blocks[]")
    codes = request.form.getlist("codes[]")
    languages = request.form.getlist("languages[]")

    content = []

    for b in blocks_text:
        if b and b.strip():
            content.append({
                "type": "text",
                "value": b.strip()
            })

    for i, c in enumerate(codes):
        if c and c.strip():
            lang = languages[i] if i < len(languages) else "code"
            content.append({
                "type": "code",
                "lang": lang,
                "value": c
            })

    image_path = ""

    if image and image.filename:
        print(f"filename: {image.filename}")
        print(f"content_type: {image.content_type}")
        print(f"ext: {os.path.splitext(image.filename)[1]}")
        upload_folder = os.path.join(app.static_folder, "images")
        os.makedirs(upload_folder, exist_ok=True)

        ext = os.path.splitext(image.filename)[1].lower()  # .jpg, .png, etc.
        name = secure_filename(os.path.splitext(image.filename)[0])  # nom sans extension
        filename = f"{name}{ext}"  # on recolle proprement

        upload_path = os.path.join(upload_folder, filename)
        image.save(upload_path)
        image_path = f"/static/images/{filename}"

        if not os.path.splitext(filename)[1]:
            filename = filename + ext

        upload_path = os.path.join(upload_folder, filename)
        image.save(upload_path)
        image_path = f"/static/images/{filename}"

    post = {
        "title": title,
        "content": content,
        "image": image_path,
        "author": session["user_id"],
        "tag": tags,
        "created_at": datetime.now(),
        "like": 0,
        "liked_by": []
    }

    db["articles"].insert_one(post)

    return redirect(url_for("index"))

@app.route("/article/<article_id>")
def show_article(article_id):

    try:
        article = db["articles"].find_one({
            "_id": ObjectId(article_id)
        })

        if not article:
            return redirect(url_for("index"))

        return render_template(
            "front/articles.html",
            article=article
        )

    except Exception as e:
        print(e)
        return redirect(url_for("index"))

@app.route("/post/like/<article_id>")
def like_post(article_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = session["user_id"]

    article = db["articles"].find_one({
        "_id": ObjectId(article_id)
    })

    if not article:
        return redirect(url_for("index"))

    if user in article.get("liked_by", []):
        return redirect(
            url_for(
                "show_article",
                article_id=article_id
            )
        )

    db["articles"].update_one(
        {"_id": ObjectId(article_id)},
        {
            "$inc": {"like": 1},
            "$push": {"liked_by": user}
        }
    )

    return redirect(
        url_for(
            "show_article",
            article_id=article_id
        )
    )

@app.route("/admin")
def admin():

    if (
        "user_id" in session
        and session.get("role") == "admin"
    ):

        articles = list(db["articles"].find({}))
        users = list(db["users"].find({}))

        return render_template(
            "admin/home.admin.html",
            articles=articles,
            users=users
        )

    return "Accès refusé", 403

@app.route("/admin/update_role/<user_id>", methods=["POST"])
def update_role(user_id):

    if (
        "user_id" in session
        and session.get("role") == "admin"
    ):

        new_role = request.form.get("role")

        db["users"].update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "role": new_role
                }
            }
        )

    return redirect(url_for("admin"))

@app.route("/admin/delete_user/<user_id>")
def delete_user(user_id):

    if (
        "user_id" in session
        and session.get("role") == "admin"
    ):

        db["users"].delete_one({
            "_id": ObjectId(user_id)
        })

    return redirect(url_for("admin"))

@app.route("/admin/view_user/<user_id>")
def show_user(user_id):

    if (
        "user_id" in session
        and session.get("role") == "admin"
    ):

        user = db["users"].find_one({
            "_id": ObjectId(user_id)
        })

        if not user:
            return redirect(url_for("admin"))

        return render_template(
            "admin/view_user.html",
            user=user
        )

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=True
    )