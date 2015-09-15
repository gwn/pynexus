import sys


api_endpoint = 'http://api.appnexus.com'
auth_user    = None
auth_pass    = None
cache_dir    = '/tmp'


def set(**kwargs):
    """ Convenience function that updates the chosen global
    configuration variables in one function call """
    sys.modules[__name__].__dict__.update(kwargs)
