from enum import unique
from MySQLdb.cursors import Cursor
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQLdb,MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from wtforms.fields.html5 import EmailField, TelField
from flask_sqlalchemy import SQLAlchemy
from functools import wraps


#User login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:#Session içinde bir anahtar değer var mı yok mu anlamına geliyor.
            return f(*args, **kwargs)
        else:
            flash("Please sign in to see the buy page.🎨","danger")
            return redirect(url_for("login"))
    return decorated_function


#User register form
class RegisterForm(Form):
    
    name = StringField("Name:", validators=[validators.DataRequired(), validators.Length(min=2, max=20)])
    username = StringField("Username:", validators=[validators.Optional(), validators.Length(min=4, max=20)])
    email = StringField("Email:", validators=[validators.DataRequired(), validators.Length(min=6), validators.Email(message = "Lütfen geçerli bir email adresi giriniz")])
    password = PasswordField("Password:", validators=[validators.DataRequired(), validators.EqualTo(fieldname = "confirm" , message = "Parolanız Uyuşmuyor."), validators.Length(min = 8)])
    confirm = PasswordField("Verify password:")



class LoginForm(Form):
    username = StringField("Username:")
    password = PasswordField("Password:")

app = Flask(__name__)   
app.secret_key = "sinansinan" 
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "sinanveritabanı"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)  

@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(form.password.data)
        
        
        cursor = mysql.connection.cursor()

        sorgu = "INSERT INTO user(name,email,username,password) VALUES(%s,%s,%s,%s)"
        
        cursor.execute(sorgu,(name,email,username,password))
        
        mysql.connection.commit()
        
        cursor.close()  

        flash("Registration completed successfully✔","success")


        return redirect(url_for("login"))
    else:
        return render_template("register.html",form = form)

@app.route("/",methods=["GET","POST"])
def Mainpage():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        name = form.password
        password_entered = form.password.data
    

        cursor = mysql.connection.cursor()

        sorgu = "Select * From user where username = %s"
        
       
        result = cursor.execute(sorgu,(username,))
        


        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("You have successfully logged in✔","success")

                session["logged_in"] = True
                session["username"] = username
                
               
                

                return redirect(url_for("login"))
                
            else:
                flash("Login failed, please try again❌","danger")
                
        else:
            flash("This user does not exist⛔","danger")
            
    
    return render_template("index.html",form = form)

@app.route("/buy")
@login_required
def buy():
    return render_template("buy.html")

@app.route("/intro")
def intro():    
    return render_template("intro.html")

@app.route("/photos")
def photo():
    return render_template("photos.html")

@app.route("/?")
def search():
    return render_template("search.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login",methods=["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        name = form.password
        password_entered = form.password.data
    

        cursor = mysql.connection.cursor()

        sorgu = "Select * From user where username = %s"
        
       
        result = cursor.execute(sorgu,(username,))
        


        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("You have successfully logged in✔","success")

                session["logged_in"] = True
                session["username"] = username
                
               
                

                return redirect(url_for("login"))
                
            else:
                flash("Login failed, please try again❌","danger")
                
        else:
            flash("This user does not exist⛔","danger")
            
    return render_template("login.html",form = form)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out🖐","success")
    return redirect(url_for("login"))
 

#add article
@app.route("/addarticle",methods = ["GET","POST"])
@login_required
def article():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        canvas_name = form.canvas_name.data
        content = form.content.data

        cursor = mysql.connection.cursor()
        sorgu = "Insert into articles(canvas_name,author,content) VALUES(%s,%s,%s)"
        cursor.execute(sorgu,(canvas_name,session["username"],content))
        mysql.connection.commit()
        cursor.close()
        flash("Article successfully added","success")
        return redirect(url_for("article"))

    return render_template("addarticle.html",form = form)

#article form
class ArticleForm(Form):
    canvas_name = StringField("Canvas name",validators=[validators.length(min = 2,max = 50)])
    content = TextAreaField("Offer and notes",validators=[validators.length(min = 5)])


if __name__ == "__main__":
    app.run(host="localhost", port=9000, debug=True)



















