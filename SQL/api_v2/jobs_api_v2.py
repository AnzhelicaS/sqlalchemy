import flask
from flask import make_response, jsonify
from flask_restful import Resource
from werkzeug.exceptions import NotFound

from SQL.data import db_session
from SQL.data.jobs import Jobs


class JobsResource(Resource):
    def get(self, jobs_id):
        db_session.global_init("db/mars.db")
        session = db_session.create_session()
        job = session.query(Jobs).get(jobs_id)
        if not job:
            raise NotFound('Работа не найдена')
        return flask.jsonify({'jobs': [job.to_dict(only=('id', 'job', 'team_leader', 'work_size', 'collaborators',
                                                         'start_date', 'end_date', 'is_finished'))]})

    def post(self):
        ...


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return flask.jsonify({'jobs': [item.to_dict(only=('id', 'job', 'team_leader', 'work_size', 'collaborators',
                                                          'start_date', 'end_date', 'is_finished')) for item in jobs]})
