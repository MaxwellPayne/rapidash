import random
import bson.json_util as bson_util
from bottle import get, post, request

def inject_dependencies(app, auth, database):
    
    Favor = app.models['Favor']

    @app.route('/hello', method='GET')
    def hello_world():
        return 'Hello World'

    @app.get('/favor/:id')
    def favor(id):
        fav = Favor.objects(id=id).first()
        return fav.to_json()

    @app.get('/newfavor')
    def newfavor():
        rand = random.randint(0, 110000)
        print rand
        fav = Favor(name='Randomly %d' % rand)
        fav.save()
        return 'created'
