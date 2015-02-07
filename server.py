from gevent import monkey; monkey.patch_all()
import json, os, glob, imp
import bottle, mongoengine, gevent
from bottle import route, request, abort
from cork import Cork
from cork.mongodb_backend import MongoDBBackend
        

class MyApp(bottle.Bottle):
    def __init__(self, catchall=True, autojson=True):
        super(MyApp, self).__init__(catchall=catchall, autojson=autojson)
        self._models = {}

    def register_model(self, model_class):
        if not isinstance(model_class, mongoengine.base.metaclasses.TopLevelDocumentMetaclass):
            raise TypeError('not a model')
        self._models[model_class.__name__] = model_class

    @property
    def models(self):
        return dict(self._models)

if __name__ == '__main__':
    config_dict = {}
    """Configure"""
    with open(os.path.join('config', 'dev.json'), 'r') as config_file:
        config_dict = json.load(config_file, encoding='ascii')
        # reformat to ascii
        config_dict = {str(key): str(config_dict[key]) for key in config_dict.keys()}
    
    backend = MongoDBBackend(db_name=config_dict['db_name'])
    auth = Cork(backend=backend)
    app = MyApp()
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

