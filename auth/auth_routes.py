import datetime
import termcolor
import bottle
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from bottle import redirect, request


def inject_dependencies(app, auth, database, config):

    class FBState(object):
        """State strings associated to their Facebook sessions
        Expire after 30 seconds for session security"""
        # @issue - all_states never garbage collects old, neglected session keys
        all_states = dict()

        def __init__(self, state_string, fb_session):
            self.state = state_string
            self.fb_session = fb_session
            self.expiry = datetime.datetime.now() + datetime.timedelta(seconds=30)
            self.__class__.all_states[self.state] = self

        @classmethod
        def retrieve_session_for(cls, state_string):
            """Return a Facebook session object if state is fresh and valid, None otherwise"""
            if state_string in cls.all_states and datetime.datetime.now() < cls.all_states[state_string].expiry:
                saved_state = cls.all_states[state_string]
                del cls.all_states[state_string]
                return saved_state.fb_session
            else:
                return None

    fb_login_success_url = '/auth/facebook/callback'

    @app.get('/auth/facebook')
    def fb_auth():

        authorization_base_url = 'https://www.facebook.com/dialog/oauth'

        facebook = OAuth2Session(config['facebook_app_id'], redirect_uri=config['base_url'] + fb_login_success_url)
        facebook = facebook_compliance_fix(facebook)

        # Redirect user to Facebook for authorization
        authorization_url, state = facebook.authorization_url(authorization_base_url)

        cached_state = FBState(state, facebook)  # create a new facebook state

        redirect(authorization_url)


    @app.get('/auth/facebook/callback')
    def fb_auth_callback():
        state_string = request.params['state']
        saved_session = FBState.retrieve_session_for(state_string)

        if saved_session is not None:
            token_url = 'https://graph.facebook.com/oauth/access_token'

            # Fetch the access token
            token = saved_session.fetch_token(token_url, client_secret=config['facebook_app_secret'],
                                              authorization_response=request.url)

            # Fetch a protected resource, i.e. user profile
            r = saved_session.get('https://graph.facebook.com/me?')

            # @unsure - how does creating vs. just authenticating user work here?
            new_user = auth.User.from_json(r.text, provider='facebook', token=token)
            #new_user.save()
            return new_user.to_json()

        else:
            # failed authentication
            return bottle.HTTPResponse(body='NoGo', status=403)
