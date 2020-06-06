from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Yang654321@127.0.0.1/test'
db = SQLAlchemy(app)


class Region(db.Model):
    # 给表重新定义一个名称，默认名称是类名的小写，比如该类默认的表名是region。
    __tablename__ = "Region"
    Name = db.Column(db.String(16),primary_key=True,unique=True)
    Cure = db.Column(db.Integer,unique=False)
    Confirm = db.Column(db.Integer,unique=False)
    Import = db.Column(db.Integer,unique=False)
    Mortality = db.Column(db.Integer,unique=False)

    def __init__(self, Name, Cure, Confirm, Import, Mortality):
        self.Name = Name
        self.Cure = Cure
        self.Confirm = Confirm
        self.Import = Import
        self.Mortality = Mortality
        
class Record(db.Model):
 
    __tablename__ = "Daily_record"
    Date = db.Column(db.Date,primary_key=True,unique=True)
    Region = db.Column(db.String(16),unique=True)
    Cure = db.Column(db.Integer,unique=False)
    Confirm = db.Column(db.Integer,unique=False)
    Import = db.Column(db.Integer,unique=False)
    Mortality = db.Column(db.Integer,unique=False)

    def __init__(self, Date, Region, Cure, Confirm, Import, Mortality):
        self.Date = Date
        self.Region = Region
        self.Cure = Cure
        self.Confirm = Confirm
        self.Import = Import
        self.Mortality = Mortality
        
@app.route('/')
def show_all():
   return render_template('show_all.html',Record = Record.query.all() )

@app.route('/new', methods = ['GET', 'POST'])
def new():
   if request.method == 'POST':
      if not request.form['Date'] or not request.form['Region'] or not request.form['Cure'] or not request.form['Confirm'] or not request.form['Import'] or not request.form['Mortality']:
         flash('Please enter all the fields', 'error')
      else:
         Record = Record(request.form['Date'], request.form['Region'],request.form['Cure']
            request.form['Confirm'], request.form['Import'], request.form['Mortality'])
         
         db.session.add(Record)
         db.session.commit()
         flash('Record was successfully added')
         return redirect(url_for('show_all'))
   return render_template('new.html')
