import sqlite3
from flask import Flask
from flask import flash, abort, redirect, render_template, request, session
import config
import db
import items
import users

app = Flask(__name__)
app.secret_key = config.secret_key

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
  items = users.get_items(user_id)
  return render_template("show_user.html", user=user, items=items)

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
  return render_template("show_item.html", item=item, classes=classes)

#new items

@app.route("/new_item")
def new_item():
  classes = items.get_all_classes()
  return render_template("new_item.html", classes=classes)

@app.route("/create_item", methods=["POST"])
def create_item():
  title = request.form["title"]
  if not title or len(title) > 100:
    abort(403)
  description  = request.form["description"]
  if len(description) > 1000:
    abort(403)
  rating = request.form["rating"]
  user_id = session["user_id"]

  classes = []
  for entry in request.form.getlist("classes"):
    if entry:
      parts = entry.split(":")
      classes.append((parts[0], parts[1]))

  items.add_item(title, description, rating, user_id, classes)

  return redirect("/")

@app.route("/create_comment", methods=["POST"])
def create_item():
  comment = request.form["comment"]
  if len(comment) > 500:
    abort(403)
  item_id = request.form["item_id"]
  item = items.get_item(item_id)
  if not item:
    abort(403)
  user_id = session["user_id"]

  items.add_comment(item_id, user_id, comment)

  return redirect("/item" + str(item_id))

#editing + updating items

@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
  item = items.get_item(item_id)
  if item["user_id"] != session["user_id"]:
    abort(403)
  return render_template("edit_item.html", item=item)

@app.route("/update_item", methods=["POST"])
def update_item():
  item_id = request.form["item_id"]
  item = items.get_item(item_id)
  if item["user_id"] != session["user_id"]:
    abort(403)

  title = request.form["title"]
  if not title or len(title) > 100:
    abort(403)
  description  = request.form["description"]
  if not description or len(description) > 1000:
    abort(403)
  rating = request.form["rating"]

  items.update_item(item_id, title, description, rating)

  return redirect("/item/" + str(item_id))

#removing items

@app.route("/remove_item/<int:item_id>", methods=["GET", "POST"])
def remove_item(item_id):
  item = items.get_item(item_id)
  if item["user_id"] != session["user_id"]:
    abort(403)

  if request.method == "GET":
    return render_template("remove_item.html", item=item)

  if request.method == "POST":
    if "remove" in request.form:
      items.remove_item(item_id)
      return redirect("/")
    else:
      return redirect("/item/" + str(item_id))

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
    flash("VIRHE: salasanat eivät ole samat")
    return redirect("/register")

  try:
    users.create_user(username, password1)
  except sqlite3.IntegrityError:
    flash("VIRHE: tunnus on jo varattu")
    return redirect("/register")

  return "Tunnus luotu"
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
    session["user_id"] = user_id
    session["username"] = username
    return redirect("/")
  else:
    return "VIRHE: väärä tunnus tai salasana"

#logging out

@app.route("/logout")
def logout():
  if "user_id" in session:
    del session["user_id"]
    del session["username"]
  return redirect("/")