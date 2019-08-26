# -*- coding: utf-8 -*-
"""

"""


__author__ = 'Marcel Hellkamp'
__version__ = '0.9.dev'
__license__ = 'MIT'



# Backward compatibility
def depr(message, critical=False):
    pass


# Small helpers

def makelist(data):
    pass


class DictProperty(object):
    pass


def cached_property(func):
    pass


class lazy_attribute(object):
    pass


###############################################################################
# Exceptions and Events ########################################################
###############################################################################

class BottleException(Exception):
    pass


class HTTPResponse(BottleException):
    pass


class HTTPError(HTTPResponse):
    pass


###############################################################################
# Routing ######################################################################
###############################################################################

class RouteError(BottleException):
    pass


class RouteSyntaxError(RouteError):
    pass


class RouteBuildError(RouteError):
    pass

class Router(object):
    pass


###############################################################################
# Application Object ###########################################################
###############################################################################

class Bottle(object):
    pass


###############################################################################
# HTTP and WSGI Tools ##########################################################
###############################################################################

class Request(threading.local, DictMixin):
    pass


class Response(threading.local):
    pass


###############################################################################
# Common Utilities #############################################################
###############################################################################

class MultiDict(DictMixin):
    pass


class HeaderDict(MultiDict):
    pass


class WSGIHeaderDict(DictMixin):
    pass


class AppStack(list):
    pass


class WSGIFileWrapper(object):
    pass


###############################################################################
# Application Helper ###########################################################
###############################################################################

def dict2json(d):
    pass


def abort(code=500, text='Unknown Error: Application stopped.'):
    pass


def redirect(url, code=303):
    pass

def send_file(*a, **k):
    pass


def static_file(filename, root, guessmime=True, mimetype=None, download=False):
    pass


###############################################################################
# HTTP Utilities and MISC (TODO) ###############################################
###############################################################################

def debug(mode=True):
    pass


def parse_date(ims):
    pass


def parse_auth(header):
    pass


def _lscmp(a, b):
    pass


def cookie_encode(data, key):
    pass


def cookie_decode(data, key):
    pass


def cookie_is_encoded(data):
    pass


def yieldroutes(func):
    pass


def path_shift(script_name, path_info, shift=1):
    pass


# Decorators
# TODO: Replace default_app() with app()

def validate(**vkargs):
    pass


def auth_basic(check, realm="private", text="Access denied"):
    pass


def make_default_app_wrapper(name):
    pass


for name in 'route get post put delete error mount hook'.split():
    globals()[name] = make_default_app_wrapper(name)
url = make_default_app_wrapper('get_url')
del name


def default():
    pass


###############################################################################
# Server Adapter ###############################################################
###############################################################################

class ServerAdapter(object):
    pass


class CGIServer(ServerAdapter):
    pass


class FlupFCGIServer(ServerAdapter):
    pass


class WSGIRefServer(ServerAdapter):
    pass


class CherryPyServer(ServerAdapter):
    pass


class PasteServer(ServerAdapter):
    pass


class MeinheldServer(ServerAdapter):
    pass


class FapwsServer(ServerAdapter):
    pass


class TornadoServer(ServerAdapter):
    pass


class AppEngineServer(ServerAdapter):
    pass


class TwistedServer(ServerAdapter):
    pass


class DieselServer(ServerAdapter):
    pass


class GeventServer(ServerAdapter):
    pass


class GunicornServer(ServerAdapter):
    pass


class EventletServer(ServerAdapter):
    pass


class RocketServer(ServerAdapter):
    pass


class BjoernServer(ServerAdapter):
    pass


class AutoServer(ServerAdapter):
    pass


server_names = {
    'cgi': CGIServer,
    'flup': FlupFCGIServer,
    'wsgiref': WSGIRefServer,
    'cherrypy': CherryPyServer,
    'paste': PasteServer,
    'fapws3': FapwsServer,
    'tornado': TornadoServer,
    'gae': AppEngineServer,
    'twisted': TwistedServer,
    'diesel': DieselServer,
    'meinheld': MeinheldServer,
    'gunicorn': GunicornServer,
    'eventlet': EventletServer,
    'gevent': GeventServer,
    'rocket': RocketServer,
    'bjoern': BjoernServer,
    'auto': AutoServer,
}


###############################################################################
# Application Control ##########################################################
###############################################################################


def _load(target, **vars):
    pass


def load_app(target):
    pass


def run(app=None, server='wsgiref', host='127.0.0.1', port=8080,
        interval=1, reloader=False, quiet=False, **kargs):
    pass


class FileCheckerThread(threading.Thread):
    pass


def _reloader_child(server, app, interval):
    pass


def _reloader_observer(server, app, interval):
    pass


###############################################################################
# Template Adapters ############################################################
###############################################################################

class TemplateError(HTTPError):
    pass


class BaseTemplate(object):
    pass


class MakoTemplate(BaseTemplate):
    pass


class CheetahTemplate(BaseTemplate):
    pass


class Jinja2Template(BaseTemplate):
    pass


class SimpleTALTemplate(BaseTemplate):
    pass


class SimpleTemplate(BaseTemplate):
    pass


def template(*args, **kwargs):
    pass


mako_template = functools.partial(template, template_adapter=MakoTemplate)
cheetah_template = functools.partial(template, template_adapter=CheetahTemplate)
jinja2_template = functools.partial(template, template_adapter=Jinja2Template)
simpletal_template = functools.partial(template, template_adapter=SimpleTALTemplate)


def view(tpl_name, **defaults):
    pass


mako_view = functools.partial(view, template_adapter=MakoTemplate)
cheetah_view = functools.partial(view, template_adapter=CheetahTemplate)
jinja2_view = functools.partial(view, template_adapter=Jinja2Template)
simpletal_view = functools.partial(view, template_adapter=SimpleTALTemplate)

###############################################################################
# Constants and Globals ########################################################
###############################################################################

TEMPLATE_PATH = ['./', './views/']
TEMPLATES = {}
DEBUG = False
MEMFILE_MAX = 1024 * 100

#: A dict to map HTTP status codes (e.g. 404) to phrases (e.g. 'Not Found')
HTTP_CODES = httplib.responses
HTTP_CODES[418] = "I'm a teapot"  # RFC 2324

#: The default template used for error pages. Override with @error()
ERROR_PAGE_TEMPLATE = """
%try:
    %from bottle import DEBUG, HTTP_CODES, request
    %status_name = HTTP_CODES.get(e.status, 'Unknown').title()
    <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html>
        <head>
            <title>Error {{e.status}}: {{status_name}}</title>
            <style type="text/css">
              html {background-color: #eee; font-family: sans;}
              body {background-color: #fff; border: 1px solid #ddd; padding: 15px; margin: 15px;}
              pre {background-color: #eee; border: 1px solid #ddd; padding: 5px;}
            </style>
        </head>
        <body>
            <h1>Error {{e.status}}: {{status_name}}</h1>
            <p>Sorry, the requested URL <tt>{{request.url}}</tt> caused an error:</p>
            <pre>{{str(e.output)}}</pre>
            %if DEBUG and e.exception:
              <h2>Exception:</h2>
              <pre>{{repr(e.exception)}}</pre>
            %end
            %if DEBUG and e.traceback:
              <h2>Traceback:</h2>
              <pre>{{e.traceback}}</pre>
            %end
        </body>
    </html>
%except ImportError:
    <b>ImportError:</b> Could not generate the error page. Please add bottle to sys.path
%end
"""

#: A thread-save instance of :class:`Request` representing the `current` request.
request = Request()

#: A thread-save instance of :class:`Response` used to build the HTTP response.
response = Response()

#: A thread-save namepsace. Not used by Bottle.
local = threading.local()

# Initialize app stack (create first empty Bottle app)
# BC: 0.6.4 and needed for run()
app = default_app = AppStack()
app.push()
