from data import db_session, jobs_api

from flask import render_template, Flask, jsonify, make_response
from werkzeug.utils import redirect

from data import db_session
from data.users import User
from data.jobs import Jobs
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user

import os


app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/users.sqlite")
db_sess = db_session.create_session()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/<title>')
@app.route('/index/<title>')
def index(title):
    return render_template('base.html', title=title)


@app.route('/')
def base():
    return render_template('base.html', title='Mars One')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


def add_user(name, surname, age, pos, spec, ad, em):
    user = User()
    user.name = name
    user.surname = surname
    user.age = age
    user.position = pos
    user.speciality = spec
    user.address = ad
    user.email = em
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()


def add_job(tl, jobs, ws, collab, st, isfin):
    job = Jobs()
    job.team_leader = tl
    job.job = jobs
    job.work_size = ws
    job.collaborators = collab
    if st != "now":
        job.start_date = st
    job.is_finished = isfin
    db_sess = db_session.create_session()
    db_sess.add(job)
    db_sess.commit()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.register_blueprint(jobs_api.blueprint)
    app.run()
    app.run(port=8080, host='127.0.0.1')