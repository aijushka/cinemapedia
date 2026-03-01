import re
import secrets
import sqlite3

from flask import Flask
from flask import flash, abort, redirect, render_template, request, session
import markupsafe

import config
import db
import items
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
def index():
    all_items = items.get_items()
    return render_template("index.html", items=all_items)

#user page

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    user_items = users.get_items(user_id)
    return render_template("show_user.html", user=user, items=user_items)

#finding items

@app.route("/find_item")
def find_item():
    query = request.args.get("query")
    if query:
        results = items.find_items(query)
    else:
        query = ""
        results = []
    return render_template("find_item.html", query=query, results=results)

@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    if not item:
        abort(404)
    classes = items.get_classes(item_id)
    comments = items.get_comments(item_id)
    return render_template("show_item.html", item=item, classes=classes, comments=comments)

#new items % comments

@app.route("/new_item")
def new_item():
    require_login()
    classes = items.get_all_classes()
    return render_template("new_item.html", classes=classes)

@app.route("/create_item", methods=["POST"])
def create_item():
    check_csrf()
    require_login()

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description  = request.form["description"]
    if len(description) > 1000:
        abort(403)
    rating = request.form["rating"]
    if not re.search("^[0-9]{0,2}$", rating):
        abort(403)
    user_id = session["user_id"]

    all_classes = items.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
        if class_title not in all_classes:
            abort(403)
        if class_value not in all_classes[class_title]:
            abort(403)
        classes.append((class_title, class_value))

    items.add_item(title, description, rating, user_id, classes)

    item_id = db.last_insert_id()
    return redirect("/item/" + str(item_id))

@app.route("/create_comment", methods=["POST"])
def create_comment():
    check_csrf()
    require_login()

    comment = request.form["comment"]
    if len(comment) > 500:
        abort(403)
    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(403)
    user_id = session["user_id"]

    items.add_comment(item_id, user_id, comment)

    return redirect("/item/" + str(item_id))

#editing + updating

@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    require_login()
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    all_classes = items.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in items.get_classes(item_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_item.html", item=item, classes=classes, all_classes=all_classes)

@app.route("/update_item", methods=["POST"])
def update_item():
    check_csrf()
    require_login()

    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description  = request.form["description"]
    if len(description) > 1000:
        abort(403)
    rating = request.form["rating"]
    if not rating or re.search("^[0-9]{0,2}$", rating):
        abort(403)

    all_classes = items.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
        if class_title not in all_classes:
            abort(403)
        if class_value not in all_classes[class_title]:
            abort(403)
        classes.append((class_title, class_value))

    items.update_item(item_id, title, description, rating, classes)

    return redirect("/item/" + str(item_id))

@app.route("/edit/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    check_csrf()
    require_login()

    comment = items.get_comments(comment_id)
    if not comment:
        abort(404)
    if comment["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit_comment.html", comment=comment)

    if request.method == "POST":
        comment.comment = request.form["comment.comment"]
        items.update_comment(comment_id, comment.comment)
        return redirect("/item/" + str(comment.item_id))

#removing

@app.route("/remove_item/<int:item_id>", methods=["GET", "POST"])
def remove_item(item_id):
    require_login()

    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_item.html", item=item)

    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            items.remove_item(item_id)
            return redirect("/")
        else:
            return redirect("/item/" + str(item_id))

@app.route("/remove/<int:comment_id>", methods=["GET", "POST"])
def remove_comment(comment_id):
    require_login()

    comment = items.get_comments(comment_id)
    if not comment:
        abort(404)
    if comment["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_comment.html", comment=comment)

    if request.method == "POST":
        check_csrf()
        if "continue" in request.form:
            items.remove_comment(comment_id)
        else:
            return redirect("/item/" + str(comment.item_id))

#registration

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1  = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        flash("VIRHE: Salasanat eivät ole samat")
        return redirect("/register")

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: Tunnus on jo varattu")
        return redirect("/register")
    else:
        flash("Tunnus luotu")
        return redirect("/")

#logging in

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

    user_id = users.check_login(username, password)
    if user_id:
        session["user_id"] = int(user_id)
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    else:
        flash("VIRHE: Väärä tunnus tai salasana")
        return redirect("/login")

#logging out

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")