#!/usr/bin/env python
# -*- coding: utf-8 -*-
from evolution_0016 import route, view, response
import evolution_0016
import markdown
import os.path
import sys
import re
import codecs
import glob
import datetime
import cgi

class Page(object):
    pagedir  = '../docs'
    cachedir = './cache'
    options = ['codehilite(force_linenos=True)', 'toc']

    def __init__(self, name):
        self.name = name
        self.filename  = os.path.join(self.pagedir,  self.name+'.md')
        self.cachename = os.path.join(self.cachedir, self.name+'.html')

    @property
    def exists(self):
        return os.path.exists(self.filename)

    @property
    def rawfile(self):
        #if not self.exists:
        #    open(self.filename, 'w').close()
        return codecs.open(self.filename, encoding='utf8')

    @property
    def raw(self):
        return self.rawfile.read()

    @property
    def cachefile(self):
        if not os.path.exists(self.cachename) \
        or os.path.getmtime(self.filename) > os.path.getmtime(self.cachename):
           with self.rawfile as f:
               html = markdown.markdown(f.read(), self.options)
           with open(self.cachename, 'w') as f:
               f.write(html.encode('utf-8'))
        return codecs.open(self.cachename, encoding='utf8')

    @property
    def html(self):
        return self.cachefile.read()

    @property
    def title(self):
        ''' The first h1 element '''
        for m in re.finditer(r'<h1[^>]*>(.+?)</h1>', self.html):
            return m.group(1).strip()
        return self.name.replace('_',' ').title()

    @property
    def preview(self):
        for m in re.finditer(r'<p[^>]*>(.+?)</p>', self.html, re.DOTALL):
            return m.group(1).strip()
        return '<i>No preview available</i>'

    @property
    def blogtime(self):
        try:
            date, name = self.name.split('_', 1)
            year, month, day = map(int, date.split('-'))
            return datetime.date(year, month, day)
        except ValueError:
            raise AttributeError("This page is not a blogpost")

    @property
    def is_blogpost(self):
        try:
            self.blogtime
            return True
        except AttributeError:
            return False

def iter_blogposts():
    # print os.path.join(Page.pagedir, '*.md')  # ../docs/*.md
    # print glob.glob(os.path.join(Page.pagedir, '*.md'))  # ['../docs/contact.md', '../docs/docs.md']
    for post in glob.glob(os.path.join(Page.pagedir, '*.md')):
        name = os.path.basename(post)[:-3]
        if re.match(r'20[0-9]{2}-[0-9]{2}-[0-9]{2}_', name):
            # print name
            yield Page(name)

# for page in iter_blogposts():
#     print page




# Static files

# @route('/:filename#.+\.(css|js|ico|png|txt|html)#')
def static(filename):
    return evolution_0016.static_file(filename, root='./static/')

print '处理第1个路由'
print 'route(\'/:filename#.+\.(css|js|ico|png|txt|html)#\')'
route = route('/:filename#.+\.(css|js|ico|png|txt|html)#')
print 'route(static)'
route(static)


# Bottle Pages

# @route('/')
# @route('/page/:name')
# @view('page')
def page(name='start'):
    p = Page(name) #replace('/','_')? Routes don't match '/' so this is save
    if p.exists:
        return dict(page=p)
    else:
        return evolution_0016.HTTPError(404, 'Page not found')

print '处理第2个路由'

route('/')(route('/page/:name')(view('page')(page)))


# decorator = view('page')
# p = decorator(page)
# print p  # <function page at 0x21c9320>
# wrapper = route('/page/:name')
# print wrapper(p)



#
# @route('/rss.xml', method='POST')
# @view('rss')
# def blogrss():
#     response.content_type = 'xml/rss'
#     posts = [post for post in iter_blogposts() if post.exists and post.is_blogpost]
#     posts.sort(key=lambda x: x.blogtime, reverse=True)
#     return dict(posts=posts)
#
#
# @route('/blog')
# @view('blogposts')
# def bloglist():
#     posts = [post for post in iter_blogposts() if post.exists and post.is_blogpost]
#     posts.sort(key=lambda x: x.blogtime, reverse=True)
#     return dict(posts=posts)


# Start server
# print sys.argv  # ['app.py', '8080']
evolution_0016.debug(True)
evolution_0016.run(host='0.0.0.0', reloader=False, port=int(sys.argv[1]), server=evolution_0016.WSGIRefServer)



