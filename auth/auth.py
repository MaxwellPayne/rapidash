import imp, os, datetime
import bottle, mongoengine, termcolor
from bson import json_util
from bottle import request

_config = imp.load_source('config', os.path.join('config', 'config.py')).config


class FacebookProfile(mongoengine.EmbeddedDocument):
    """Data obtained directly from Facebook API"""
    facebook_id = mongoengine.StringField(unique=True)
    first_name = mongoengine.StringField()
    last_name = mongoengine.StringField()
    locale = mongoengine.StringField()
    gender = mongoengine.StringField()
    timezone = mongoengine.IntField()
    verified = mongoengine.BooleanField()


class Oauth2TokenDocument(mongoengine.EmbeddedDocument):
    """Token data from oauthlib.OAuth2Token"""
    access_token = mongoengine.StringField(required=True)
    token_type = mongoengine.StringField()
    expires_at = mongoengine.DateTimeField(required=True)


class User(mongoengine.Document):
    """Auth platform-agnostic basic User class"""
    facebook_id = mongoengine.StringField(required=False)
    facebook_profile = mongoengine.EmbeddedDocumentField(FacebookProfile, required=False)
    token = mongoengine.EmbeddedDocumentField(Oauth2TokenDocument, required=False)

    # @overload
    @classmethod
    def from_json(cls, json_data, provider, token=None):
        json_dict = json_util.loads(json_data)

        if token is not None:
            # convert oauthlib's expires_at UTCtime to datetime.datetime
            token['expires_at'] = datetime.datetime.utcfromtimestamp(token['expires_at'])
            token = Oauth2TokenDocument(**token) if token else None

        if provider == 'custom':
            raise NotImplementedError()

        elif provider == 'facebook':
            # convert facebook's 'id' key to 'facebook_id' in the json
            json_dict['facebook_id'] = json_dict['id']
            del json_dict['id']

            json_data = json_util.dumps(json_dict)
            facebook_embedded_doc = FacebookProfile.from_json(json_data)

            return cls(facebook_id=json_dict['facebook_id'], facebook_profile=facebook_embedded_doc,
                       token=token)

        else:
            raise ValueError('%s is not a supported provider' % provider)


def requires_secret(request_handler):
    """request must have your app's mobile_secret in params to continue"""

    def decorated():
        raise NotImplementedError()
        if 'mobile_secret' in request.params and request.params['mobile_secret'] == _config['mobile_secret']:
            request_handler()
        else:
            bottle.response(status=403)

    return decorated


def authentication_required(request_handler):
    """request must be authenticated by an approved 'provider' to continue"""
    def decorated():
        try:
            provider = request.params['provider']
        except KeyError:
            provider = None

        if provider == 'facebook':
            pass
        elif provider == 'custom':
            pass
        else:
            return bottle.HTTPResponse(code=401, body='Not authorized by a supported provider')

        # authentication approved
        return request_handler()

    return decorated

def attach_user(request_handler):
    """Load user profile from db, attach it to the request before processing regularly"""
    raise NotImplementedError()

    def decorated():
        # database read here
        request.params['attached_user'] = {}
        request_handler()

    return decorated
