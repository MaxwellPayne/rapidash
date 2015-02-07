import mongoengine

def inject_dependencies(app, auth, database):
    
    class Favor(mongoengine.Document):
        name = mongoengine.StringField()

    app.register_model(Favor)
