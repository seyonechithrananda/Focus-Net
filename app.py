# app.py
import os
import socket
import struct
import numpy as np
from keras.models import load_model
from forms import IPForm
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'

sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP

data= []

def getBand(band):
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        if band in str(data):
            break
    title,args,flt1,flt2,flt3,flt4 = struct.unpack('>36s8sffff', data)
    EEG = [flt1, flt2, flt3, flt4]
    print(EEG)
    return np.array(EEG)



#########################
##### SQL DATABASE ######
#########################

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

#########################
#####    MODELS    ######
#########################

class Puppy(db.Model):

    __tablename__ = 'puppies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    owner = db.relationship('Owner', backref='puppy', uselist=False)


    def __init__(self, name):
        self.name = name

    def __repr__(self):
        if self.owner:
            return "Puppy name is {} and owner is {}".format(self.name, self.owner.name)
        else:
            return "Puppy name is {} and it has no owner yet".format(self.name)

class Owner(db.Model):

    __tablename__ = "owners"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    puppy_id = db.Column(db.Integer, db.ForeignKey('puppies.id'))

    def __init__(self, name, puppy_id):
        self.name = name
        self.puppy_id = puppy_id

###########################
##### VIEW FUNCTIONS ######
###########################


@app.route('/', methods=["GET", "POST"])
def index():
    form = IPForm()

    if form.validate_on_submit():
        UDP_IP = form.address.data
        UDP_PORT = form.port.data
        sock.bind((UDP_IP, UDP_PORT))
        return redirect(url_for('dashboard'))     

    
    return render_template('index.html', form=form)

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    while True:
        data.append(getBand('gamma_absolute'))
        return render_template('dashboard.html', data=data)

'''
@app.route('/add', methods=['GET', 'POST'])
def add_pup():

    form = AddForm()

    if form.validate_on_submit():
        name = form.name.data

        new_pup = Puppy(name)
        db.session.add(new_pup)
        db.session.commit()

        return redirect(url_for('list_pup'))

    return render_template('add.html', form=form)

@app.route('/list')
def list_pup():
    puppies = Puppy.query.all()
    return render_template('list.html', puppies=puppies)


@app.route('/delete', methods=['GET', 'POST'])
def del_pup():
    form = DeleteForm()

    if form.validate_on_submit():
        id = form.id.data
        pup = Puppy.query.get(id)
        db.session.delete(pup)
        db.session.commit()

        return redirect(url_for('list_pup'))
    return render_template('delete.html', form=form)


@app.route('/owner', methods=["GET", "POST"])
def add_owner():
    form = OwnerForm()

    if form.validate_on_submit():
        owner = form.owner_name.data
        puppy_id = form.puppy_id.data
        db.session.add(Owner(owner, puppy_id))
        db.session.commit()

        return redirect(url_for('list_pup'))

    return render_template("owner.html", form=form)

'''

if __name__ == '__main__':
    app.run(debug=True)
