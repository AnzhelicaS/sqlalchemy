import flask
from flask import make_response, jsonify, request

from SQL.data import db_session
from SQL.data.jobs import Jobs

jobs_blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@jobs_blueprint.route('/jobs')
def get_jobs():
    db_session.global_init("db/mars.db")
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return flask.jsonify({'jobs': [item.to_dict(only=('id', 'job', 'team_leader', 'work_size', 'collaborators',
                                                      'start_date', 'end_date', 'is_finished')) for item in jobs]})


@jobs_blueprint.route('/jobs/<int:id>')
def get_one_job(id):
    db_session.global_init("db/mars.db")
    session = db_session.create_session()
    job = session.query(Jobs).get(id)
    if not job:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return flask.jsonify({'jobs': [job.to_dict(only=('id', 'job', 'team_leader', 'work_size', 'collaborators',
                                                     'start_date', 'end_date', 'is_finished'))]})


@jobs_blueprint.route('/jobs', methods=['POST'])
def create_job():
    job = request.json
    if not job:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in job for key in
                 ['job', 'work_size', 'collaborators', 'is_finished', 'team_leader']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    new_job = Jobs(
        job=job['job'],
        collaborators=job['collaborators'],
        team_leader=job['team_leader'],
        work_size=job['work_size'],
        is_finished=job['is_finished']
    )
    db_sess.add(new_job)
    db_sess.commit()
    return jsonify({'id': new_job.id})


@jobs_blueprint.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_news(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(job)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@jobs_blueprint.route('/jobs/<int:job_id>', methods=['PUT'])
def change_job(job_id):
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    different = request.json

    if not job:
        return make_response(jsonify({'error': 'Bad request'}), 400)
    elif not any(key in different for key in
                 ['job', 'work_size', 'collaborators', 'is_finished', 'team_leader']):
        return make_response(jsonify({'error': 'Bad request'}), 400)

    job.job = different['job'] if 'job' in different else job.job
    job.collaborators = different['collaborators'] if 'collaborators' in different else job.collaborators
    job.team_leader = different['team_leader'] if 'team_leader' in different else job.team_leader
    job.work_size = different['work_size'] if 'work_size' in different else job.work_size
    job.is_finished = different['is_finished'] if 'is_finished' in different else job.is_finished
    db_sess.commit()
    return jsonify({'id': job.id})
