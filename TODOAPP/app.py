from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
# create the extension
db = SQLAlchemy()
# Users db = db2
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SECRET_KEY"] = "gizli-anahtar"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///veritabanı.db"
# initialize the app with the extension
db.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    todos = db.relationship("Todo", backref="author")
    # Create all the tables in the database
    # back_populates ve backref arasındaki farkı incele
with app.app_context():
    db.create_all()

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslık = db.Column(db.String(50), nullable=False)
    icerik = db.Column(db.String(50), nullable=False)
    durum = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view= "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

@app.route("/")
@login_required
def index():
    todos = Todo.query.filter_by(user_id = current_user.id).all()
    return render_template("index.html", todos=todos, user = current_user)

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method=="POST":
        email = request.form.get("email-login")
        password2 = request.form.get("password-login")
        user = User.query.filter_by(email=email).first()
        if not user:
            print("That email does not exist, please try again.")
            return redirect(url_for("login"))
        elif user.password != password2:
            print('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('index'))
    return render_template("login.html", user=current_user)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name1 = request.form.get("ad")
        email1 = request.form.get("email")
        password1 = request.form.get("password")
        new_user = User(
            email = email1,
            password = password1,
            name = name1
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("index"))
    return render_template("register.html", user=current_user)

@app.route("/add", methods=["POST"])
@login_required
def add():
    name = request.form.get("başlık")
    content = request.form.get("içerik")
    new_todo= Todo(baslık=name, icerik=content, durum=False, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()

    return redirect(url_for("index")) 

@app.route("/delete/<string:id>", methods=["GET"])
@login_required
def deleteTodo(id):
    todo = Todo.query.filter_by(id=id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/complete/<string:id>", methods=["GET"])
@login_required
def completeTodo(id):
    todo = Todo.query.filter_by(id=id).first()
    if (todo.durum == False):
        todo.durum = True
    if todo.durum == True:
        todo.durum == False
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
