from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint
from sqlalchemy import func
bp = Blueprint('update', __name__, url_prefix='update')
bp.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Yang654321@127.0.0.1/test'
db = SQLAlchemy(bp)

class Area(db.Model):
    _tablename_ = 'areas'
    Region = db.Column(db.String(64), primary_key = True)
    Cure = db.Column(db.Integer, default =  db.session.query(func.sum(Record.Cure)).filter(Record.Region==Area.Region).scalar())
    Comfirm = db.Column(db.Integer, default =  db.session.query(func.sum(Record.Comfirm)).filter(Record.Region==Area.Region).scalar())
    Import = db.Column(db.Integer, default =  db.session.query(func.sum(Record.Import)).filter(Record.Region==Area.Region).scalar())
    Asymptomatic = db.Column(db.Integer, default =  db.session.query(func.sum(Record.Asymptomatic)).filter(Record.Region==Area.Region).scalar())
    Mortality = db.Column(db.Integer, default =  db.session.query(func.sum(Record.Mortality)).filter(Record.Region==Area.Region).scalar())
    
    records = db.relationship('Record', backref='area')

    def __repr__(self);
        return '<Area %r>' % self.Region

class Record(db.Model):
    _tablename_ = 'records'
    Date = db.Column(db.Date, primary_key = True)
    Region = db.Column(db.String(64), primary_key = True)
    Cure = db.Column(db.Integer)
    Comfirm = db.Column(db.Integer)
    Import = db.Column(db.Integer)
    Asymptomatic = db.Column(db.Interger)
    Mortality = db.Column(db.Integer)
    area_Region = db.Column(db.String(64), db.ForeignKey('areas.Region'))

    def __repr__(self);
        return '<Record %r>' % self.Record  
        
if __name__ == '__main__':
        db.drop_all()
        db.create_all()

@bp.route('/')
def show_all():
   return render_template('show_all.html',Record = Record.query.all() )

@bp.route('/new', methods = ['GET', 'POST'])
def new():
   if request.method == 'POST':
      if not request.form['Date']  or not request.form['Cure'] or not request.form['Confirm'] or not request.form['Import'] or not request.form['Mortality']:
         flash('Please enter all the fields', 'error')
      else:
         Record = Record(request.form['Date'], request.form['Cure'],request.form['Confirm'],
                         request.form['Import'], request.form['Mortality'])
         
         db.session.add(Record)
         db.session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('show_all'))
   return render_template('new.html')
if __name__ == '__main__':
    bp.run()
    bp.run(debug=True)
