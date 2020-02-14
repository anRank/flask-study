from blog import app, db
from blog.models import Users
from blog.forms import LoginForm, NewNoteForm, EditNoteForm, DeleteNoteForm
from flask import request, session
import os
import sys
from flask import redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret string')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', prefix + os.path.join(app.root_path, 'data.sqlite'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# basedir = os.path.abspath(os.path.dirname(__file__))
#
# #app.secret_key = 'secret key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'flask.sqlite')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


###############################################

# Models
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)

    # optional
    def __repr__(self):
        return '<Note %r>' % self.body

###############################################


db.create_all()


@app.route('/homepage')
def homepage():
    return render_template('home.html')


@app.route('/information')
def information():
    return render_template('info.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        session['logged_in'] = True #写入session
        form = LoginForm()
        return render_template('login.html', form=form)
    else:
        name = request.form['username']
        if name:
            session['username'] = name
        return redirect(url_for('homepage1'))


@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('homepage1'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    db.create_all()
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        users = Users(username, password, email)
        db.session.add(users)
        db.session.commit()
        return redirect(url_for('homepage1'))


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/')
@app.route('/homepage1')
def homepage1():
    db.create_all()
    #从session会话中获取用户名
    if 'username' in session:
        name = session['username']
    else:
        name = 'Human'
    return render_template('home1.html', name=name)

######################################################################################################


@app.route('/a')
def index1():
    form = DeleteNoteForm()
    notes = Note.query.all()
    return render_template('index1.html', notes=notes, form=form)


@app.route('/new', methods=['GET', 'POST'])
def new_note():
    form = NewNoteForm()
    if form.validate_on_submit():
        body = form.body.data
        note = Note(body=body)
        db.session.add(note)
        db.session.commit()
        flash('Your note is saved.')
        return redirect(url_for('index1'))
    return render_template('new_note.html', form=form)


@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    form = EditNoteForm()
    note = Note.query.get(note_id)
    if form.validate_on_submit():
        note.body = form.body.data
        db.session.commit()
        flash('Your note is updated.')
        return redirect(url_for('index1'))
    form.body.data = note.body  # preset form input's value
    return render_template('edit_note.html', form=form)


@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    form = DeleteNoteForm()
    if form.validate_on_submit():
        note = Note.query.get(note_id)
        db.session.delete(note)
        db.session.commit()
        flash('Your note is deleted.')
    else:
        abort(400)
    return redirect(url_for('index1'))