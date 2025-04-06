from requests import get, put, post, delete


print(post('http://localhost:5000/api/users', json={
    'surname': 'Laufeyson',
    'name': 'Loki',
    'age': '1000',
    'position': 'Принц Асгарда',
    'address': 'Асгард',
    'email': 'Loki@emal.ru',
    'hashed_password': 'loki'
}).json())

print(get('http://localhost:5000/api/users').json())

print(put('http://localhost:5000/api/users/9', json={'age': '1001'}).json())

print(get('http://localhost:5000/api/users').json())

print(delete('http://localhost:5000/api/users/9').json())

print(get('http://localhost:5000/api/users').json())