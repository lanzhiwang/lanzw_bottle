

from bottle import Bottle

mounts = {}

# self.subapp = bottle.Bottle()
# mount(self.subapp, '/test')
# mount(subapp, '/test/t1/t2')
def mount(app, script_path):
    ''' Mount a Bottle application to a specific URL prefix '''
    if not isinstance(app, Bottle):
        raise TypeError('Only Bottle instances are supported for now.')
    print script_path.split('/')
    # ['', 'test']
    # ['', 'test', 't1', 't2']

    script_path = '/'.join(filter(None, script_path.split('/')))
    print script_path
    # test
    # test/t1/t2

    path_depth = script_path.count('/') + 1
    print path_depth
    # 1
    # 3

    if not script_path:
        raise TypeError('Empty script_path. Perhaps you want a merge()?')
    for other in mounts:
        if other.startswith(script_path):
            raise TypeError('Conflict with existing mount: %s' % other)

    print '/%s/:#.*#' % script_path
    # /test/:#.*#
    # /test/t1/t2/:#.*#
    # @self.route('/%s/:#.*#' % script_path, method="ANY")
    # def mountpoint():
    #     request.path_shift(path_depth)
    #     return app.handle(request.environ)

    mounts[script_path] = app


def path_shift(self, shift=1):
    script_name = self.environ.get('SCRIPT_NAME', '/')
    self['SCRIPT_NAME'], self.path = path_shift(script_name, self.path, shift)
    self['PATH_INFO'] = self.path


subapp = Bottle()
mount(subapp, '/test')

mount(subapp, '/test/t1/t2')
