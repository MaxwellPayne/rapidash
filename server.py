from gevent import monkey; monkey.patch_all()
import json, os, glob, imp
import bottle, mongoengine, gevent
from bottle import route, request, abort
from cork import Cork
from cork.mongodb_backend import MongoDBBackend
        

class RapidashApp(bottle.Bottle):
    class JSObject:
        def set_property(self, prop_name, prop_value):
            self.__dict__.update({prop_name: prop_value})
        def remove_property(self, prop_name):
            if prop_name in self.__dict__:
                del self.__dict__[prop_name]


    def __init__(self, catchall=True, autojson=True):
        super(RapidashApp, self).__init__(catchall=catchall, autojson=autojson)
        JSObject = self.__class__.JSObject
        self.models = JSObject()
        self.controllers = JSObject()

    def register_model(self, model_class):
        if not isinstance(model_class, mongoengine.base.metaclasses.TopLevelDocumentMetaclass):
            raise TypeError('not a model')
        self.models.set_property(model_class.__name__, model_class)

    def register_controller(self, controller):
        self.controllers.set_property(controller.__name__, controller)

if __name__ == '__main__':
    config_dict = {}
    """Configure"""
    with open(os.path.join('config', 'dev.json'), 'r') as config_file:
        config_dict = json.load(config_file, encoding='ascii')
        # reformat to ascii
        config_dict = {str(key): str(config_dict[key]) for key in config_dict.keys()}
    
    backend = MongoDBBackend(db_name=config_dict['db_name'])
    auth = Cork(backend=backend)
    app = RapidashApp()
    db = mongoengine.connect(config_dict['db_name'], host='localhost')

    app.config.load_dict(config_dict)

    """Register routes from all modules in the routes/ directory"""
    search_paths = map(lambda dirname: os.path.join(dirname, '*.py'), ['models', 'routes'])
    scripts = reduce(lambda found_scripts, search_path: found_scripts + glob.glob(search_path), search_paths, [])

    print scripts
    for script_path in scripts:
        routefile = imp.load_source('routefile', script_path)
        routefile.inject_dependencies(app, auth, db)

    """Start the app"""
    app.run(host='localhost', server='gevent', port=8000)

