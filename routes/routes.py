import random
import bson.json_util as bson_util
from bottle import get, post, request

def inject_dependencies(app, auth, database):
    
    Author = app.models.Author
    Book = app.models.Book

    @app.route('/hello', method='GET')
    def hello_world():
        return 'Hello World'

    @app.get('/authors/:id')
    def favor(id):
        author = Author.objects(id=id).first()
        return author.to_json()

    @app.get('/newauthor')
    def newfavor():
        rand = random.randint(0, 110000)
        print rand
        a = Author(name='Randomly %d' % rand)
        a.save()
        return 'created'
