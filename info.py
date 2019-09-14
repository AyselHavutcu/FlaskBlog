from flask import Flask,render_template,flash,redirect,url_for,session,logging,request#web sunucumuzu aga kaldıracak 
from flask_mysqldb import MySQL

#mysql icin gerekli olan fromları dahil ettik
from wtforms import From,StringField,PasswordField,validators
#bunlarda formda kullanmak icin dahil ediyourz
from passlib.hash import sha256_crypt #parola gizliligi icin ekledik
app = Flask(__name__) 
#her bir pyhton dosyamız aslında bir modul 
#biz bu pyhton dosyalarını 2 turlu kullanabilriz
#1. si:Biz bu python dosyalarının icine degisik fonksiyonlar yazarız ve 
#daha sonra bu fonksiyonları pyhtonda fonksiyon cagrısı yaparak kullanablirz
#2.si:biz bu python dosyalarını modul olarak baska bir python dosyasında calıstırabilirz
#ve sadece fonksiyonları almak isteyebilir ve fonksiyon cagrılarının calısmamasını saglayabilir
#eger python dosyasını terminalde calıstırısak name in degeri main olursa terminalde calısmıs 
#eger degilse baska bir modul olarak aktarılmıs demektir o zaman ben bu fonksiyon cagrılarını yapamam


@app.route("/") #her url adresi istedigimizde kullanılan bir decorator
def index():
    #yukarda request yaptık ve bu fonksiyon direk bu requestten sonra calısacaktır 
    #response donmemiz lazım 
 
    numbers = [1,2,3,4,5]
    return render_template("index.html",numbers = numbers)

#baska requestler de yapabilirz
@app.route("/about")
def about():
 return render_template("about.html")
#dinamik url tanımlayacaz
@app.route("/article/<string:id>")
def detail(id):
    return "Article ID:" +id
if __name__ == "__main__":
    app.run(debug=True)

#debug true dememizin sebebi debug ı aktiflestiriyoruz 
#yani herhangi bir yerde hatamız olursa bize bir uyarı mesajı fırlatılacak

#jinja templater ı icinde html css kodlarını ve boostrap modullerimiz
#kullanıyoruz aynı zamanda python kodlarımızıda bu template e uygun bir sekilde kullanabiliyoruz
#boylelikle biz fonksiyonlarımızda herhangi bir deger urettigimiz zaman bu template a bu degeri verip template i response olarak donebilioruz
#bunun icin bizim bu template render etmemiz gerekiyor boylece biz bu template bir pythom degeri gonderebiliyoruz


