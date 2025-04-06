from flask import Flask, render_template, redirect, request, abort, jsonify
import requests

from SQL.api_v2.jobs_api_v2 import JobsListResource, JobsResource
from SQL.data.jobs import Jobs
from data.users import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from SQL.api.jobs_api import jobs_blueprint
from SQL.api.users_api import users_blueprint
from flask import make_response
from flask_restful import Api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

app.register_blueprint(jobs_blueprint, url_prefix='/api')
app.register_blueprint(users_blueprint, url_prefix='/api')

api_version2 = Api(app)
api_version2.add_resource(JobsListResource, '/api/v2/jobs')
api_version2.add_resource(JobsResource, '/api/v2/jobs/<int:jobs_id>')

login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


class AddJob(FlaskForm):
    job = StringField('Job Title', validators=[DataRequired()])
    team_leader = StringField('Team Leader id', validators=[DataRequired()])
    duration = StringField('Work Size', validators=[DataRequired()])
    collaborators = StringField('Collaborators', validators=[DataRequired()])
    is_finished = BooleanField('Is job finished?')
    submit = SubmitField('Add')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    second_password = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])

    submit = SubmitField('Submit')


@login_manager.user_loader
def load_user(user_id):
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.second_password.data:
            return render_template('register.html', title='Register form', form=form,
                                   message='Ошибка. Пароли не совпадают')

        elif not form.age.data.isdigit():
            return render_template('register.html', title='Register form', form=form,
                                   message='Ошибка. Неправельно указан возраст')

        db_session.global_init("db/mars.db")
        db_sess = db_session.create_session()

        user = User()
        user.surname = form.surname.data
        user.name = form.name.data
        user.age = form.age.data
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.address = form.address.data
        user.email = form.email.data
        user.hashed_password = form.password.data
        user.set_password(user.hashed_password)

        db_sess.add(user)
        db_sess.commit()
        return redirect("/")
    return render_template('register.html', title='Register form', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_session.global_init("db/mars.db")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def add_job():
    form = AddJob()
    if form.validate_on_submit():
        db_session.global_init("db/mars.db")
        db_sess = db_session.create_session()
        if not (form.team_leader.data.isdigit() and db_sess.query(User).filter(
                User.id == form.team_leader.data)).first():
            return render_template('addjob.html',
                                   message="Неправильный id тим лида",
                                   form=form)
        elif not form.duration.data.isdigit():
            return render_template('addjob.html',
                                   message="Неправильно указано Work size",
                                   form=form)
        job = Jobs()
        job.team_leader = form.team_leader.data
        job.job = form.job.data
        job.work_size = form.duration.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        db_sess.add(job)
        db_sess.commit()
        return redirect("/")
    return render_template('addjob.html', form=form)


@app.route('/edit_job/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = AddJob()
    if request.method == "GET":
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == id).first()
        if job:
            form.job.data = job.job
            form.team_leader.data = job.team_leader
            form.duration.data = job.work_size
            form.collaborators.data = job.collaborators
            form.is_finished.data = job.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == id,
                                         ((Jobs.team_leader == 1) | (Jobs.team_leader == current_user.id))).first()
        if job:
            job.job = form.job.data
            job.team_leader = form.team_leader.data
            job.work_size = form.duration.data
            job.collaborators = form.collaborators.data
            job.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('addjob.html', title='Редактирование новости', form=form)


@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def job_delete(id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == id,
                                     ((Jobs.team_leader == 1) | (Jobs.team_leader == current_user.id))).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/')
def main_window():
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    jobs = requests.get('http://localhost:5000/api/jobs').json()
    users = requests.get('http://localhost:5000/api/users').json()
    return render_template('all_job.html', json=jobs, name=users)


def global_init(db_name):
    db_session.global_init(f"db/{db_name}.db")


def create_session():
    return db_session.create_session()


def main():
    db_session.global_init("db/mars.db")
    app.run(port=5000, host='127.0.0.1')


if __name__ == '__main__':
    main()
