import config
import helpers

import os
import logging
import requests


def request(method, path, nocache=False, **kwargs):
    """ A wrapper of the requests.request for the App Nexus API,
    which tries to deal with the auth process transparently. 

    Fetches an authorization token (either from cache or new),
    wraps the passed request with it, then makes the request.
    If authentication fails, tries again, by forcing to use a new token
    (by disabling cache) this time."""

    if not config.auth_user or not config.auth_pass:
        raise Exception('You must set a username and password before ' + \
                          'making a request!')


    try:
        token = get_token(nocache=nocache)
    except Exception as e:
        logging.debug('An exception occurred while getting a token (%s): %s',
                      e.__class__.__name__,
                      e.message)
        raise e


    # wrap the request with the token:
    if not kwargs.has_key('headers') or type(kwargs['headers']) != 'dict':
        kwargs['headers'] = {}

    kwargs['headers']['Authorization'] = token


    # make the request
    url  = config.api_endpoint + '/' + path
    resp = requests.request(method, url, **kwargs)


    # deal with possible errors
    if not resp.ok:
        try:
            data = resp.json()['response']

        except ValueError: # means that the response is not JSON
            raise AppNexusError(None, None, resp)

        else:
          if data['error_id'] == 'NOAUTH':
              # try again with a new token (note 'nocache')
              request(method, url, nocache=True, **kwargs)

          elif data['error_id'] in ['NOAUTH_EXPIRED', 'NOAUTH_DISABLED', 'UNAUTH']:
              err = AppNexusError(data['error_id'], data['error'], resp)

              logging.debug('App Nexus auth error: (%s) %s', err.id, err.message)

              raise err


    # ta-da
    return resp


def get_token(nocache=False):
    """ Try to get an auth token from cache or the
    App Nexus auth service """

    cache_file = os.path.join(config.cache_dir, 'pynexus_auth_token')


    token = None

    if not nocache:
        token = fetch_token_from_cache(cache_file)

    if not token: # means no token found in cache
        auth_payload = {'auth': {
            'username': config.auth_user,
            'password': config.auth_pass
        }}

        token = fetch_new_token(auth_payload)

        write_token_to_cache(cache_file, token)


    return token


def fetch_token_from_cache(filename):
    if not os.path.isfile(filename):
        return None

    with open(filename, 'r') as infile:
      return infile.read()


def write_token_to_cache(filename, token):
    with open(filename, 'w') as outfile:
        token = str(token) # in case the value would be None, False, etc.
        outfile.write(token)


def fetch_new_token(payload):
    url  = config.api_endpoint + '/auth'
    resp = requests.post(url, json=payload)

    helpers.raise_for_error(resp)

    return resp.json()['response']['token']
