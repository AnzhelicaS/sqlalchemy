import flask
from flask import request, make_response, jsonify

from SQL.data import db_session
from SQL.data.users import User

users_blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@users_blueprint.route('/users')
def get_users():
    db_session.global_init("db/mars.db")
    session = db_session.create_session()
    users = session.query(User).all()
    return flask.jsonify({'users': [item.to_dict(
        only=('id', 'surname', 'name', 'age', 'position', 'address', 'email', 'hashed_password', 'created_date')) for
        item in users]})


@users_blueprint.route('/users/<int:id>')
def get_one_user(id):
    db_session.global_init("db/mars.db")
    session = db_session.create_session()
    user = session.query(User).get(id)
    return flask.jsonify({'users': [user.to_dict(
        only=('id', 'surname', 'name', 'age', 'position', 'address', 'email', 'hashed_password', 'created_date'))]})


@users_blueprint.route('/users', methods=['POST'])
def create_user():
    user = request.json
    if not user:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in user for key in
                 ['surname', 'name', 'age', 'position', 'address', 'email', 'hashed_password']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    new_user = User(
        surname=user['surname'],
        name=user['name'],
        age=user['age'],
        position=user['position'],
        address=user['address'],
        email=user['email'],
        hashed_password=user['hashed_password']
    )
    db_sess.add(new_user)
    db_sess.commit()
    return jsonify({'id': new_user.id})


@users_blueprint.route('/users/<int:user_id>', methods=['DELETE'])
def delete_news(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@users_blueprint.route('/users/<int:user_id>', methods=['PUT'])
def change_job(user_id):
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    different = request.json

    if not user:
        return make_response(jsonify({'error': 'Bad request'}), 400)
    elif not any(key in different for key in
                 ['surname', 'name', 'age', 'position', 'address', 'email', 'hashed_password']):
        return make_response(jsonify({'error': 'Bad request'}), 400)

    user.surname = different['surname'] if 'surname' in different else user.surname
    user.name = different['name'] if 'name' in different else user.name
    user.age = different['age'] if 'age' in different else user.age
    user.position = different['position'] if 'position' in different else user.position
    user.address = different['address'] if 'address' in different else user.address
    user.email = different['email'] if 'email' in different else user.email
    user.password = different['hashed_password'] if 'hashed_password' in different else user.hashed_password
    db_sess.commit()
    return jsonify({'id': user.id})

