def raise_for_error(response):
    """ Raises an exception if the status of the given response
    is not 200, or there is a key named "error" in the returned json
    object. """
    response.raise_for_status() # Raises an HTTPError if status is not 200

    try:
      data = response.json()['response']

    except ValueError: # means that the response is not JSON
      pass # we allow non-JSON responses to pass

    else:
      if data.has_key('error'):
          raise AppNexusError(data['error_id'], data['error'], response)


class AppNexusError(Exception):
    def __init__(self, error_id, error_message, response):
        self.id       = error_id
        self.message  = error_message
        self.response = response
