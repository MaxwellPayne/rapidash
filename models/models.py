import mongoengine

def inject_dependencies(app, auth, database):
    
    """Example Models"""
    class Author(mongoengine.Document):
        name = mongoengine.StringField()

    class Book(mongoengine.Document):
        title = mongoengine.StringField()

    app.register_model(Author)
    app.register_model(Book)
