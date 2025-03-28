from flask import Flask, render_template

from SQL.data.jobs import Jobs
from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def main():
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    jobs_json = {}

    for job in db_sess.query(Jobs):
        item = [job.job, job.team_leader, job.work_size, job.collaborators, job.is_finished]
        jobs_json[item[0]] = {'name': item[0], 'leader': [f'{user.surname} {user.name}'
                                                        for user in db_sess.query(User).filter(User.id == item[1])][0],
                              'duration': item[2], 'collaborators': item[3], 'finished': item[4]}
    return render_template('all_job.html', json=jobs_json)


def global_init(db_name):
    db_session.global_init(f"db/{db_name}.db")


def create_session():
    return db_session.create_session()


if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')






