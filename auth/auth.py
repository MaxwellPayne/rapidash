import bottle
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from bottle import request


def inject_dependencies(app, auth, database, config):

    def facebook_fetch_profile(redirect_response):
        token_url = 'https://graph.facebook.com/oauth/access_token'

        facebook = OAuth2Session(config['facebook_app_id'])
        facebook = facebook_compliance_fix(facebook)

        # Fetch the access token
        facebook.fetch_token(token_url, client_secret=config['facebook_app_secret'],
                             authorization_response=redirect_response)

        # Fetch a protected resource, i.e. user profile
        r = facebook.get('https://graph.facebook.com/me?')
        return r

    def requires_secret(func):

        def inner():
            if 'mobile_secret' in request.params and request.params['mobile_secret'] == config['mobile_secret']:
                func()
            else:
                bottle.response(status=403)

        return inner


    # Export these utilities
    __all__ = facebook_compliance_fix, facebook_fetch_profile
