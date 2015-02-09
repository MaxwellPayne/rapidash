from gevent import monkey; monkey.patch_all()
import os, glob, imp
import bottle, mongoengine


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
    config_dict = imp.load_source('config', os.path.join('config', 'config.py')).config

    config_dict['base_url'] = 'https://%s:%s' % (config_dict['hostname'], config_dict['port'])

    class SSLGeventServer(bottle.GeventServer):
        """Subclass of Bottle's default GeventServer, servers https instead of http"""
        def __init__(self, host='127.0.0.1', port=8080, **options):
            # @important: add SSL config here to make this a true SSL server
            cert_path = os.path.join('config', config_dict['ssl_cert'])
            key_path = os.path.join('config', config_dict['ssl_key'])
            options.update(keyfile=key_path, certfile=cert_path)
            options.update(ssl_version=2)
            super(SSLGeventServer, self).__init__(host, port, **options)
            self.options = options

    app = RapidashApp()
    app.config.load_dict(config_dict)
    db = mongoengine.connect(config_dict['db_name'], host='localhost')

    auth_module = imp.load_source('auth_module', os.path.join('auth', 'auth.py'))
    auth = auth_module


    """Register routes from all modules in the routes/ directory"""
    search_paths = map(lambda dirname: os.path.join(dirname, '*.py'), ['auth', 'models', 'controllers', 'routes'])
    scripts = reduce(lambda found_scripts, search_path: found_scripts + glob.glob(search_path), search_paths, [])

    for script_path in scripts:
        routefile = imp.load_source('routefile', script_path)
        if hasattr(routefile, 'inject_dependencies'):
            routefile.inject_dependencies(app, auth, db, dict(config_dict))

    app.run(host=config_dict['hostname'], server=SSLGeventServer, port=config_dict['port'])

