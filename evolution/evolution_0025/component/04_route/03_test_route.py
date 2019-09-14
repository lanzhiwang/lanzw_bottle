import unittest
import bottle
from tools import api


def x(a, b): pass

def d(f):
    def w():
        return f()

    return w


print d  # <function d at 0x2720410>
print x  # <function x at 0x2720398>
callback = d(x)
print callback  # <function w at 0x2720488>
route = bottle.Route(None, None, None, callback)
print route.get_undecorated_callback()  # <function x at 0x2720398>

print '==============='
print route()

class TestRoute(unittest.TestCase):

    @api('0.12')
    def test_callback_inspection(self):
        def x(a, b): pass
        def d(f):
            def w():
                return f()
            return w
        
        route = bottle.Route(None, None, None, d(x))
        self.assertEqual(route.get_undecorated_callback(), x)
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))

        def d2(foo):
            def d(f):
                def w():
                    return f()
                return w
            return d

        route = bottle.Route(None, None, None, d2('foo')(x))
        self.assertEqual(route.get_undecorated_callback(), x)
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))

