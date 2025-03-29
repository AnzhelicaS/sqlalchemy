from flask import Flask, render_template, redirect
from SQL.data.jobs import Jobs
from data import db_session
from data.users import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class RegisterForm(FlaskForm):
    email = StringField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    second_password = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])

    submit = SubmitField('Submit')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.second_password.data:
            return render_template('login.html', title='Register form', form=form,
                                   message='Ошибка. Пароли не совпадают')

        elif not form.age.data.isdigit():
            return render_template('login.html', title='Register form', form=form,
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
        return redirect('/success')
    return render_template('login.html', title='Register form', form=form)


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/')
def main():
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    jobs_json = {}

    for job in db_sess.query(Jobs):
        item = [job.job, job.team_leader, job.work_size, job.collaborators, job.is_finished]
        jobs_json[item[0]] = {'name': item[0], 'leader': [f'{user.surname} {user.name}'
                                                          for user in db_sess.query(User).filter(User.id == item[1])][
            0],
                              'duration': item[2], 'collaborators': item[3], 'finished': item[4]}
    return render_template('all_job.html', json=jobs_json)


def global_init(db_name):
    db_session.global_init(f"db/{db_name}.db")


def create_session():
    return db_session.create_session()


if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')
