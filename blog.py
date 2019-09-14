from flask import Flask,render_template,flash,redirect,url_for,session,logging,request 
from flask_mysqldb import MySQL
#mysql icin gerekli olan fromları dahil ettik
from wtforms import Form,StringField,PasswordField,validators,TextAreaField
#bunlarda formda kullanmak icin dahil ediyourz
from passlib.hash import sha256_crypt #parola gizliligi icin ekledik
#mysql ve flask konfigurasyonu yapıyoruz
from functools import wraps
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if  "logged_in" in session:
           return f(*args, **kwargs)#login yapılmıs bu returnle direk normal fonksiyona gidecek
        else:#giris yapılmamıssa login e yonlendirilecek
            flash("İf you want to view this page ,You must login :(","danger")
            return redirect(url_for("login"))
    return decorated_function

"""Python has a really interesting feature called function decorators. This allows some really neat things for web applications.
Because each view in Flask is a function, decorators can be used to inject additional functionality to one or more functions.
The route() decorator is the one you probably used already. But there are use cases for implementing your own decorator.
For instance, imagine you have a view that should only be used by people that are logged in. If a user goes to the site
and is not logged in, they should be redirected to the login page. This is a good example of a use case where a decorator
is an excellent solution.

Login Required Decorator
So let’s implement such a decorator. A decorator is a function that wraps and replaces another function.
Since the original function is replaced, you need to remember to copy the original function’s information 
to the new function. Use functools.wraps() to handle this for you."""
#User Login Decorator

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
#Kullanıcı kayıt formu
class RegisterForm(Form):
      name = StringField("Full Name:",validators=[validators.length(min =4,max=25)])
    #validators.length ile isim alanını sınırlandırmıs olduk
      username = StringField("Username:",validators=[validators.length(min =5,max=25)])
      mail = StringField("Email Address:",validators=[validators.Email(message = "please enter a valid email address")])
      #email adresi olup olmadıgını kontrol ettik
      password = PasswordField("Password:",validators=[validators.DataRequired(message ="Please create a password."),validators.EqualTo(fieldname = "confirm",message = "Password doesnt  compromise with the first one")])
      confirm = PasswordField("Confirm Password:")
class LoginForm(Form):
     username = StringField("Username:")
     password = PasswordField("Password")
class ProfileForm(Form):
    age = StringField("Age :",validators=[validators.length(min=1,max =11)])
    university = StringField("University :",validators=[validators.length(min=5,max =100)])
    department = StringField("Department :",validators=[validators.length(min=5,max =100)])
    study_field  = StringField("Study Field :",validators=[validators.length(min=5,max =100)])

app = Flask(__name__) 
app.secret_key ="Blog"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] ="Blog"
#dtabase den verileri guzel bir sekilde goruntelemk icin verileri sozluk yapısında tasıyoruz
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)
@app.route("/") 
def index(): 
     return render_template("index.html")
@app.route("/register",methods =["GET","POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
         #simdi formdan aldıgımız bilgileri veritabanına ekliyecez
         name = form.name.data
         username = form.username.data
         mail = form.mail.data
         password = sha256_crypt.encrypt(form.password.data)#password u sifreledik

         cursor = mysql.connection.cursor()

         command = "Insert into users(name,username,mail,password) values(%s,%s,%s,%s)"

         cursor.execute(command,(name,username,mail,password))
       
         mysql.connection.commit()

         cursor.close()
         #simdi usera feedback mesajlarımızı gonderecez flash islemi
         flash("Well Done ! You successfully registered",category="success")
         #bu mesaj hemen bir sonraki requestte yayınalnacak yani index sayfasında
         return redirect(url_for("login"))#index fonksiyonuna iliskili olan url ye gitmek istiyorum demek

    else:
         return render_template("register.html",form = form)

@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mysql.connection.cursor()

    command = "Select * From articles where author = %s"
    
    result = cursor.execute(command,(session["username"],))
   
    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html",articles = articles)
    else:
        return render_template("dashboard.html")
#login islemi
@app.route("/login",methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
      
          username = form.username.data
          password = form.password.data
          cursor = mysql.connection.cursor()
          command = "Select * From users  where username = %s"
          result = cursor.execute(command,(username,))
          if result > 0:
            data = cursor.fetchone()#kullanıcının butun bilgilerini aldık
            real_password = data["password"]#aldıgımız bilgileri sozluk seklinde getirdik
            #parola sifrelendigi icin bu fonksiyonu kullanıyoruz
            if sha256_crypt.verify(password,real_password):
                flash("You successfully loged in ","success")

                session["logged_in"] = True 
                """A session begins when a user logs in to or accesses a particular computer, program or 
                web page and ends when the user logs out of or shuts down the computer, closes the program or web page. 
                A session can temporarily store information related to the activities of the user while connected.
                A session cookie is used in web pages for storing information in case the user leaves the web page or closes down their Internet browser. 
                For example, this is one way a website can remember what is in your shopping cart if you leave and come back.

               In computer programming, session variables are used to store temporary information, sometimes to
                use for retrieving and viewing data on multiple web pages. Websites requiring a username and password
                 use session variables to help transfer data between web pages, but only while the user is logged into the computer.
                
                """
                # session time:How long logged in user is allowed to be in the website when this session time is 
                #extended the user will be logged out from the website 
                session["username"]  = username
                #bir sonraki sayfaya gitmeden once session degerimizi kendimiz belirliyourz
            
                return redirect(url_for("index"))
            else:
                flash("This password is not correct","danger")
                return redirect(url_for("login"))
          else:
             flash("User not found:(",category="danger")
             return redirect(url_for("login"))
    else:         
        return render_template("login.html",form = form)

#makale ekleme
@app.route("/addarticle",methods =["GET","POST"])
def addarticle():
    form = ArticleForm(request.form)

    if request.method == "POST" and form.validate():
       #username session dan alacaz
       username = session["username"]
       title = form.title.data
       content =form.content.data
       
       cursor = mysql.connection.cursor()
       command = "Insert into articles(title,author,content) values(%s,%s,%s)"
       cursor.execute(command,(title,username,content))
       mysql.connection.commit()
       cursor.close()
       flash("Your article successfully added ","success")
       return redirect(url_for("dashboard"))
    else:
         return render_template("addarticle.html",form = form)
#makale form
class ArticleForm(Form):
      title =StringField("Title:",validators=[validators.length(min =5,max =100)])
      content = TextAreaField("Content",validators =[validators.length(min=10)])
#Makale Sayfası 
@app.route("/articles",methods = ["GET","POST"])

def articles():
    cursor = mysql.connection.cursor()
    command = "Select * From articles"
    result = cursor.execute(command)
    if result > 0:
        articles = cursor.fetchall() #fetchall veritabanındaki butun makaleleri alcak
        return render_template("articles.html",articles = articles)
    else:
        return render_template("articles.html")


#Detay sayfası
@app.route("/article/<string:id>")
def article(id):
    cursor = mysql.connection.cursor()

    command = "Select * from articles where id = %s"
    result = cursor.execute(command,(id,))
    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html",article = article)
    else:
        return render_template("article.html")
#makale silme 

@app.route("/delete/<string:id>")
@login_required
def delete_article(id):
      cursor = mysql.connection.cursor()

      command = "Select *from articles where id = %s and author = %s"
      result   = cursor.execute(command,(id,session["username"]))
      
      if result > 0:
          com2 = "Delete from articles where id = %s"
          cursor.execute(com2,(id,))
          mysql.connection.commit()
          return redirect(url_for("dashboard"))
      else:
       flash("You cannot delete a non-existent article or you are not allowed to do that","danger")
       return redirect(url_for("index"))
#makale guncelleme
@app.route("/edit/<string:id>",methods = ["GET","POST"])
@login_required
def updatearticle(id):
    #id it is get we ll need a new form is already filled with the info of article in html page
    if request.method == "GET":
     #get info from database 
        cursor = mysql.connection.cursor()
        com = "Select * from articles where id = %s"
        result = cursor.execute(com,(id,))
        if result == 0:
          #then there is no  data 
            flash("You cannot update a non-existent article or you are not allowed to do that","danger")
            return redirect(url_for("index"))
        else:
          #if there is data
            Data = cursor.fetchone() #it came in dic form
            form = ArticleForm() #creating an empty file
            form.title.data = Data["title"]
            form.content.data = Data["content"]
        #now we filled the form we r sending it to the requested html page
            return render_template("update.html",form = form)
    else:
        #post method
        newform = ArticleForm(request.form) #we got updated form now we r posting it to the db
        newTitle =newform.title.data
        newContent = newform.content.data
        cursor = mysql.connection.cursor()
        com2 = "update articles set title = %s,content = %s where id = %s"
        cursor.execute(com2,(newTitle,newContent,id))
        #since we r changin the db the change should be committed
        mysql.connection.commit()
        cursor.close()
        flash("The article successfully uopdated ( :","success")
        return redirect(url_for("dashboard"))

#logout islemi
@app.route("/logout")
def logout():
    session.clear()#sessionı temizleyecek #we need to clear the session cuz of changing the session when another user login
    return redirect(url_for("index"))

#arama url
@app.route("/search",methods = ["GET","POST"])
def search():
    if request.method =="GET":
        return redirect(url_for("index"))
    else:
        keyword = request.form.get("keyword")
        cursor = mysql.connection.cursor()

        com3 = "Select * From articles where title like '%" +keyword+ "%'"  #icinde keyword gecenleri getir

        result =cursor.execute(com3)
        if result == 0:
            flash("The article not found","warning")
            return redirect(url_for("articles"))
        else:
            articles =cursor.fetchall()
            return render_template("articles.html",articles = articles)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/profile",methods = ["GET","POST"])
@login_required
def profile():
    form = ProfileForm(request.form)

    if request.method == "POST":
          
         age = form.age.data
         uni = form.university.data
         dep = form.department.data
         st_field =form.study_field.data
         cursor = mysql.connection.cursor()
         com = "insert into profile(username,age,university,department,studyField) values(%s,%s,%s,%s,%s)"
         cursor.execute(com,(session["username"],age,uni,dep,st_field))
         mysql.connection.commit()
         cursor.close()
         flash("Your profile successfully created ","success")
         return redirect(url_for("profile"))


    else:
        return render_template("profile.html",form =form)
#About me
@app.route("/about")
@login_required
def about():
    cursor = mysql.connection.cursor()
    com = "Select *from profile where username = %s"
    result = cursor.execute(com,(session["username"],))
    if result == 0:
        return render_template("about.html")
    else:
        user = cursor.fetchone()
        return render_template("about.html",user = user)
#editing profile
@app.route("/updateprofile",methods = ["GET","POST"])
@login_required
def editprofile():
    if request.method =="GET":
        cursor = mysql.connection.cursor()
        com = "Select *from profile where username = %s"
        result = cursor.execute(com,(session["username"],))
        if result == 0:
            flash("There isnt a user with this name or you are not allowed for editing...","danger")
            return redirect(url_for("profile"))
        else:
            form = ProfileForm()
            user = cursor.fetchone()
            form.age.data = user["age"]
            form.university.data = user["university"]
            form.department.data = user["department"]
            form.study_field.data = user["studyField"]
            return render_template("updateprofile.html",form =  form)
    else:
        #post method

        form = ProfileForm(request.form)
       
        newAge = form.age.data
        newUni = form.university.data
        newDep = form.department.data 
        newSt  =  form.study_field.data
        cursor = mysql.connection.cursor()
        com2 = "Update profile set   age = %s,university = %s,department = %s,studyField =%s where username = %s"
        cursor.execute(com2,(newAge,newUni,newDep,newSt,session["username"]))
        mysql.connection.commit()
        cursor.close()
        flash("The profile successfully updated ( :","success")
        return redirect(url_for("about"))

#comment article
@app.route("/comment/<string:id>",methods = ["GET","POST"])
@login_required
def addcomment(id):
    if request.method == "GET":
       return  redirect(url_for("articles"))
    else:
        title =request.form.get("title")
        content = request.form.get("comment")
        cursor =mysql.connection.cursor()
        com ="insert into comments(title,content,article_id) values(%s,%s,%s)"
        cursor.execute(com,(title,content,int(id)))
        mysql.connection.commit()
        cursor.close()
        flash("Your comment successfully posted","success")
        return redirect(url_for("articles"))

@app.route("/article/<string:id>")
def commentdetail(id):
    cursor = mysql.connection.cursor()
    com ="Select * from comments where article_id = %s"
    res = cursor.execute(com,(id,))
    if res == 0:
        flash("result is zero","danger")
        return redirect(url_for("articles"))
    else:
        comments = cursor.fetchall()
        
        return render_template("article.html",comments= comments)
if __name__ == "__main__":
    app.run(debug=True)

#simdi kullanıcı fromunu olusturacaz ama bunu html formlarıyla degil python classını kullanarak yapacaz
#Wt formları


