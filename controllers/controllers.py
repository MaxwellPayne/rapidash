
def inject_dependencies(app, auth, database, config):

    class AuthorController(object):
        def author_by_id(self, author_id):
            pass

        def create(self, author_name):
            pass

    app.register_controller(AuthorController)

