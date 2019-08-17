# -*- coding: utf-8 -*-


class Bottle():
    pass


# Module level functions
class AppStack(list):
    def __call__(self):
        """ Return the current default app. """
        return self[-1]

    def push(self, value=None):
        """ Add a new Bottle instance to the stack """
        if not isinstance(value, Bottle):
            value = Bottle()
        self.append(value)
        return value


# BC: 0.6.4 and needed for run()


if __name__ == '__main__':
    bottle1 = Bottle()  # <__main__.Bottle instance at 0x10de5ae60>
    print bottle1
    app = AppStack([bottle1])
    print app  # [<__main__.Bottle instance at 0x10de5ae60>]
    print app()  # <__main__.Bottle instance at 0x10de5ae60>

    bottle2 = Bottle()
    app.push(bottle2)
    print app  # [<__main__.Bottle instance at 0x10de5ae60>, <__main__.Bottle instance at 0x10de5aea8>]