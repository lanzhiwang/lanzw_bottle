# -*- coding: utf-8 -*-

from bottle import route, run, request, response, send_file, abort, validate

# Lets start with "Hello World!"
# Point your Browser to 'http://localhost:8080/' and greet the world :D
@route('/')
def hello_world():
    return 'Hello World!'
"""
$ curl http://localhost:8080/
Hello World!

{'CONTENT_LENGTH': '',
 'CONTENT_TYPE': 'text/plain',
 'GATEWAY_INTERFACE': 'CGI/1.1',
 'HISTCONTROL': 'ignoredups',
 'HISTSIZE': '1000',
 'HOME': '/root',
 'HOSTNAME': 'lanzhiwang-centos7',
 'HTTP_ACCEPT': '*/*',
 'HTTP_HOST': 'localhost:8080',
 'HTTP_USER_AGENT': 'curl/7.29.0',
 'LANG': 'zh_CN.UTF-8',
 'LESSOPEN': '||/usr/bin/lesspipe.sh %s',
 'LOGNAME': 'root',
 'LS_COLORS': 'rs=0:di=38;5;27:ln=38;5;51:mh=44;38;5;15:pi=40;38;5;11:so=38;5;13:do=38;5;5:bd=48;5;232;38;5;11:cd=48;5;232;38;5;3:or=48;5;232;38;5;9:mi=05;48;5;232;38;5;15:su=48;5;196;38;5;15:sg=48;5;11;38;5;16:ca=48;5;196;38;5;226:tw=48;5;10;38;5;16:ow=48;5;10;38;5;21:st=48;5;21;38;5;15:ex=38;5;34:*.tar=38;5;9:*.tgz=38;5;9:*.arc=38;5;9:*.arj=38;5;9:*.taz=38;5;9:*.lha=38;5;9:*.lz4=38;5;9:*.lzh=38;5;9:*.lzma=38;5;9:*.tlz=38;5;9:*.txz=38;5;9:*.tzo=38;5;9:*.t7z=38;5;9:*.zip=38;5;9:*.z=38;5;9:*.Z=38;5;9:*.dz=38;5;9:*.gz=38;5;9:*.lrz=38;5;9:*.lz=38;5;9:*.lzo=38;5;9:*.xz=38;5;9:*.bz2=38;5;9:*.bz=38;5;9:*.tbz=38;5;9:*.tbz2=38;5;9:*.tz=38;5;9:*.deb=38;5;9:*.rpm=38;5;9:*.jar=38;5;9:*.war=38;5;9:*.ear=38;5;9:*.sar=38;5;9:*.rar=38;5;9:*.alz=38;5;9:*.ace=38;5;9:*.zoo=38;5;9:*.cpio=38;5;9:*.7z=38;5;9:*.rz=38;5;9:*.cab=38;5;9:*.jpg=38;5;13:*.jpeg=38;5;13:*.gif=38;5;13:*.bmp=38;5;13:*.pbm=38;5;13:*.pgm=38;5;13:*.ppm=38;5;13:*.tga=38;5;13:*.xbm=38;5;13:*.xpm=38;5;13:*.tif=38;5;13:*.tiff=38;5;13:*.png=38;5;13:*.svg=38;5;13:*.svgz=38;5;13:*.mng=38;5;13:*.pcx=38;5;13:*.mov=38;5;13:*.mpg=38;5;13:*.mpeg=38;5;13:*.m2v=38;5;13:*.mkv=38;5;13:*.webm=38;5;13:*.ogm=38;5;13:*.mp4=38;5;13:*.m4v=38;5;13:*.mp4v=38;5;13:*.vob=38;5;13:*.qt=38;5;13:*.nuv=38;5;13:*.wmv=38;5;13:*.asf=38;5;13:*.rm=38;5;13:*.rmvb=38;5;13:*.flc=38;5;13:*.avi=38;5;13:*.fli=38;5;13:*.flv=38;5;13:*.gl=38;5;13:*.dl=38;5;13:*.xcf=38;5;13:*.xwd=38;5;13:*.yuv=38;5;13:*.cgm=38;5;13:*.emf=38;5;13:*.axv=38;5;13:*.anx=38;5;13:*.ogv=38;5;13:*.ogx=38;5;13:*.aac=38;5;45:*.au=38;5;45:*.flac=38;5;45:*.mid=38;5;45:*.midi=38;5;45:*.mka=38;5;45:*.mp3=38;5;45:*.mpc=38;5;45:*.ogg=38;5;45:*.ra=38;5;45:*.wav=38;5;45:*.axa=38;5;45:*.oga=38;5;45:*.spx=38;5;45:*.xspf=38;5;45:',
 'MAIL': '/var/spool/mail/root',
 'OLDPWD': '/root/work/code/lanzw_bottle',
 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin',
 'PATH_INFO': '/',
 'PWD': '/root/work/code/lanzw_bottle/evolution/evolution_02',
 'QUERY_STRING': '',
 'REMOTE_ADDR': '127.0.0.1',
 'REMOTE_HOST': 'localhost.localdomain',
 'REQUEST_METHOD': 'GET',
 'SCRIPT_NAME': '',
 'SERVER_NAME': 'localhost.localdomain',
 'SERVER_PORT': '8080',
 'SERVER_PROTOCOL': 'HTTP/1.1',
 'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5',
 'SHELL': '/bin/bash',
 'SHLVL': '1',
 'SSH_CLIENT': '122.189.36.128 49753 22',
 'SSH_CONNECTION': '122.189.36.128 49753 172.29.146.40 22',
 'SSH_TTY': '/dev/pts/3',
 'TERM': 'xterm-256color',
 'USER': 'root',
 'XDG_RUNTIME_DIR': '/run/user/0',
 'XDG_SESSION_ID': '9335',
 '_': '/usr/bin/python',
 'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7f145bdbd1e0>,
 'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x124f6d0>,
 'wsgi.input': <socket._fileobject object at 0x7f145bccad50>,
 'wsgi.multiprocess': False,
 'wsgi.multithread': True,
 'wsgi.run_once': False,
 'wsgi.url_scheme': 'http',
 'wsgi.version': (1, 0)}
"""

# Receiving GET parameter (/hello?name=Tim) is as easy as using a dict.
@route('/hello')
def hello_get():
    name = request.GET['name']
    return 'Hello %s!' % name
"""
$ curl http://localhost:8080/hello?name=Tim
Hello Tim!

{'CONTENT_LENGTH': '',
 'CONTENT_TYPE': 'text/plain',
 'GATEWAY_INTERFACE': 'CGI/1.1',
 'HISTCONTROL': 'ignoredups',
 'HISTSIZE': '1000',
 'HOME': '/root',
 'HOSTNAME': 'lanzhiwang-centos7',
 'HTTP_ACCEPT': '*/*',
 'HTTP_HOST': 'localhost:8080',
 'HTTP_USER_AGENT': 'curl/7.29.0',
 'LANG': 'zh_CN.UTF-8',
 'LESSOPEN': '||/usr/bin/lesspipe.sh %s',
 'LOGNAME': 'root',
 'LS_COLORS': 'rs=0:di=38;5;27:ln=38;5;51:mh=44;38;5;15:pi=40;38;5;11:so=38;5;13:do=38;5;5:bd=48;5;232;38;5;11:cd=48;5;232;38;5;3:or=48;5;232;38;5;9:mi=05;48;5;232;38;5;15:su=48;5;196;38;5;15:sg=48;5;11;38;5;16:ca=48;5;196;38;5;226:tw=48;5;10;38;5;16:ow=48;5;10;38;5;21:st=48;5;21;38;5;15:ex=38;5;34:*.tar=38;5;9:*.tgz=38;5;9:*.arc=38;5;9:*.arj=38;5;9:*.taz=38;5;9:*.lha=38;5;9:*.lz4=38;5;9:*.lzh=38;5;9:*.lzma=38;5;9:*.tlz=38;5;9:*.txz=38;5;9:*.tzo=38;5;9:*.t7z=38;5;9:*.zip=38;5;9:*.z=38;5;9:*.Z=38;5;9:*.dz=38;5;9:*.gz=38;5;9:*.lrz=38;5;9:*.lz=38;5;9:*.lzo=38;5;9:*.xz=38;5;9:*.bz2=38;5;9:*.bz=38;5;9:*.tbz=38;5;9:*.tbz2=38;5;9:*.tz=38;5;9:*.deb=38;5;9:*.rpm=38;5;9:*.jar=38;5;9:*.war=38;5;9:*.ear=38;5;9:*.sar=38;5;9:*.rar=38;5;9:*.alz=38;5;9:*.ace=38;5;9:*.zoo=38;5;9:*.cpio=38;5;9:*.7z=38;5;9:*.rz=38;5;9:*.cab=38;5;9:*.jpg=38;5;13:*.jpeg=38;5;13:*.gif=38;5;13:*.bmp=38;5;13:*.pbm=38;5;13:*.pgm=38;5;13:*.ppm=38;5;13:*.tga=38;5;13:*.xbm=38;5;13:*.xpm=38;5;13:*.tif=38;5;13:*.tiff=38;5;13:*.png=38;5;13:*.svg=38;5;13:*.svgz=38;5;13:*.mng=38;5;13:*.pcx=38;5;13:*.mov=38;5;13:*.mpg=38;5;13:*.mpeg=38;5;13:*.m2v=38;5;13:*.mkv=38;5;13:*.webm=38;5;13:*.ogm=38;5;13:*.mp4=38;5;13:*.m4v=38;5;13:*.mp4v=38;5;13:*.vob=38;5;13:*.qt=38;5;13:*.nuv=38;5;13:*.wmv=38;5;13:*.asf=38;5;13:*.rm=38;5;13:*.rmvb=38;5;13:*.flc=38;5;13:*.avi=38;5;13:*.fli=38;5;13:*.flv=38;5;13:*.gl=38;5;13:*.dl=38;5;13:*.xcf=38;5;13:*.xwd=38;5;13:*.yuv=38;5;13:*.cgm=38;5;13:*.emf=38;5;13:*.axv=38;5;13:*.anx=38;5;13:*.ogv=38;5;13:*.ogx=38;5;13:*.aac=38;5;45:*.au=38;5;45:*.flac=38;5;45:*.mid=38;5;45:*.midi=38;5;45:*.mka=38;5;45:*.mp3=38;5;45:*.mpc=38;5;45:*.ogg=38;5;45:*.ra=38;5;45:*.wav=38;5;45:*.axa=38;5;45:*.oga=38;5;45:*.spx=38;5;45:*.xspf=38;5;45:',
 'MAIL': '/var/spool/mail/root',
 'OLDPWD': '/root/work/code/lanzw_bottle',
 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin',
 'PATH_INFO': '/hello',
 'PWD': '/root/work/code/lanzw_bottle/evolution/evolution_02',
 'QUERY_STRING': 'name=Tim',
 'REMOTE_ADDR': '127.0.0.1',
 'REMOTE_HOST': 'localhost.localdomain',
 'REQUEST_METHOD': 'GET',
 'SCRIPT_NAME': '',
 'SERVER_NAME': 'localhost.localdomain',
 'SERVER_PORT': '8080',
 'SERVER_PROTOCOL': 'HTTP/1.1',
 'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5',
 'SHELL': '/bin/bash',
 'SHLVL': '1',
 'SSH_CLIENT': '122.189.36.128 49753 22',
 'SSH_CONNECTION': '122.189.36.128 49753 172.29.146.40 22',
 'SSH_TTY': '/dev/pts/3',
 'TERM': 'xterm-256color',
 'USER': 'root',
 'XDG_RUNTIME_DIR': '/run/user/0',
 'XDG_SESSION_ID': '9335',
 '_': '/usr/bin/python',
 'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7fe1229091e0>,
 'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x7fe116e0d668>,
 'wsgi.input': <socket._fileobject object at 0x7fe122816d50>,
 'wsgi.multiprocess': False,
 'wsgi.multithread': True,
 'wsgi.run_once': False,
 'wsgi.url_scheme': 'http',
 'wsgi.version': (1, 0)}
"""

# This example handles POST requests to '/hello_post'
@route('/hello_post', method='POST')
def hello_post():
    name = request.POST['name']
    return 'Hello %s!' % name
"""
$ curl -X POST -F "name=user" http://localhost:8080/hello_post
Hello user!

{'CONTENT_LENGTH': '143',
 'CONTENT_TYPE': 'multipart/form-data; boundary=----------------------------a46f39ec5f0b',
 'GATEWAY_INTERFACE': 'CGI/1.1',
 'HISTCONTROL': 'ignoredups',
 'HISTSIZE': '1000',
 'HOME': '/root',
 'HOSTNAME': 'lanzhiwang-centos7',
 'HTTP_ACCEPT': '*/*',
 'HTTP_EXPECT': '100-continue',
 'HTTP_HOST': 'localhost:8080',
 'HTTP_USER_AGENT': 'curl/7.29.0',
 'LANG': 'zh_CN.UTF-8',
 'LESSOPEN': '||/usr/bin/lesspipe.sh %s',
 'LOGNAME': 'root',
 'LS_COLORS': 'rs=0:di=38;5;27:ln=38;5;51:mh=44;38;5;15:pi=40;38;5;11:so=38;5;13:do=38;5;5:bd=48;5;232;38;5;11:cd=48;5;232;38;5;3:or=48;5;232;38;5;9:mi=05;48;5;232;38;5;15:su=48;5;196;38;5;15:sg=48;5;11;38;5;16:ca=48;5;196;38;5;226:tw=48;5;10;38;5;16:ow=48;5;10;38;5;21:st=48;5;21;38;5;15:ex=38;5;34:*.tar=38;5;9:*.tgz=38;5;9:*.arc=38;5;9:*.arj=38;5;9:*.taz=38;5;9:*.lha=38;5;9:*.lz4=38;5;9:*.lzh=38;5;9:*.lzma=38;5;9:*.tlz=38;5;9:*.txz=38;5;9:*.tzo=38;5;9:*.t7z=38;5;9:*.zip=38;5;9:*.z=38;5;9:*.Z=38;5;9:*.dz=38;5;9:*.gz=38;5;9:*.lrz=38;5;9:*.lz=38;5;9:*.lzo=38;5;9:*.xz=38;5;9:*.bz2=38;5;9:*.bz=38;5;9:*.tbz=38;5;9:*.tbz2=38;5;9:*.tz=38;5;9:*.deb=38;5;9:*.rpm=38;5;9:*.jar=38;5;9:*.war=38;5;9:*.ear=38;5;9:*.sar=38;5;9:*.rar=38;5;9:*.alz=38;5;9:*.ace=38;5;9:*.zoo=38;5;9:*.cpio=38;5;9:*.7z=38;5;9:*.rz=38;5;9:*.cab=38;5;9:*.jpg=38;5;13:*.jpeg=38;5;13:*.gif=38;5;13:*.bmp=38;5;13:*.pbm=38;5;13:*.pgm=38;5;13:*.ppm=38;5;13:*.tga=38;5;13:*.xbm=38;5;13:*.xpm=38;5;13:*.tif=38;5;13:*.tiff=38;5;13:*.png=38;5;13:*.svg=38;5;13:*.svgz=38;5;13:*.mng=38;5;13:*.pcx=38;5;13:*.mov=38;5;13:*.mpg=38;5;13:*.mpeg=38;5;13:*.m2v=38;5;13:*.mkv=38;5;13:*.webm=38;5;13:*.ogm=38;5;13:*.mp4=38;5;13:*.m4v=38;5;13:*.mp4v=38;5;13:*.vob=38;5;13:*.qt=38;5;13:*.nuv=38;5;13:*.wmv=38;5;13:*.asf=38;5;13:*.rm=38;5;13:*.rmvb=38;5;13:*.flc=38;5;13:*.avi=38;5;13:*.fli=38;5;13:*.flv=38;5;13:*.gl=38;5;13:*.dl=38;5;13:*.xcf=38;5;13:*.xwd=38;5;13:*.yuv=38;5;13:*.cgm=38;5;13:*.emf=38;5;13:*.axv=38;5;13:*.anx=38;5;13:*.ogv=38;5;13:*.ogx=38;5;13:*.aac=38;5;45:*.au=38;5;45:*.flac=38;5;45:*.mid=38;5;45:*.midi=38;5;45:*.mka=38;5;45:*.mp3=38;5;45:*.mpc=38;5;45:*.ogg=38;5;45:*.ra=38;5;45:*.wav=38;5;45:*.axa=38;5;45:*.oga=38;5;45:*.spx=38;5;45:*.xspf=38;5;45:',
 'MAIL': '/var/spool/mail/root',
 'OLDPWD': '/root/work/code/lanzw_bottle',
 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin',
 'PATH_INFO': '/hello_post',
 'PWD': '/root/work/code/lanzw_bottle/evolution/evolution_02',
 'QUERY_STRING': '',
 'REMOTE_ADDR': '127.0.0.1',
 'REMOTE_HOST': 'localhost.localdomain',
 'REQUEST_METHOD': 'POST',
 'SCRIPT_NAME': '',
 'SERVER_NAME': 'localhost.localdomain',
 'SERVER_PORT': '8080',
 'SERVER_PROTOCOL': 'HTTP/1.1',
 'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5',
 'SHELL': '/bin/bash',
 'SHLVL': '1',
 'SSH_CLIENT': '122.189.36.128 49753 22',
 'SSH_CONNECTION': '122.189.36.128 49753 172.29.146.40 22',
 'SSH_TTY': '/dev/pts/3',
 'TERM': 'xterm-256color',
 'USER': 'root',
 'XDG_RUNTIME_DIR': '/run/user/0',
 'XDG_SESSION_ID': '9335',
 '_': '/usr/bin/python',
 'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7fe1229091e0>,
 'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x7fe116e0d668>,
 'wsgi.input': <socket._fileobject object at 0x7fe12282e650>,
 'wsgi.multiprocess': False,
 'wsgi.multithread': True,
 'wsgi.run_once': False,
 'wsgi.url_scheme': 'http',
 'wsgi.version': (1, 0)}

"""

# Cookies :D
@route('/counter')
def counter():
    old = request.COOKIES.get('counter',0)
    new = int(old) + 1
    response.COOKIES['counter'] = new
    return "You viewed this page %d times!" % new
"""
$ curl http://localhost:8080/counter
You viewed this page 1 times!
$ curl http://localhost:8080/counter
You viewed this page 1 times!
$ curl http://localhost:8080/counter
You viewed this page 1 times!

{'CONTENT_LENGTH': '',
 'CONTENT_TYPE': 'text/plain',
 'GATEWAY_INTERFACE': 'CGI/1.1',
 'HISTCONTROL': 'ignoredups',
 'HISTSIZE': '1000',
 'HOME': '/root',
 'HOSTNAME': 'lanzhiwang-centos7',
 'HTTP_ACCEPT': '*/*',
 'HTTP_HOST': 'localhost:8080',
 'HTTP_USER_AGENT': 'curl/7.29.0',
 'LANG': 'zh_CN.UTF-8',
 'LESSOPEN': '||/usr/bin/lesspipe.sh %s',
 'LOGNAME': 'root',
 'LS_COLORS': 'rs=0:di=38;5;27:ln=38;5;51:mh=44;38;5;15:pi=40;38;5;11:so=38;5;13:do=38;5;5:bd=48;5;232;38;5;11:cd=48;5;232;38;5;3:or=48;5;232;38;5;9:mi=05;48;5;232;38;5;15:su=48;5;196;38;5;15:sg=48;5;11;38;5;16:ca=48;5;196;38;5;226:tw=48;5;10;38;5;16:ow=48;5;10;38;5;21:st=48;5;21;38;5;15:ex=38;5;34:*.tar=38;5;9:*.tgz=38;5;9:*.arc=38;5;9:*.arj=38;5;9:*.taz=38;5;9:*.lha=38;5;9:*.lz4=38;5;9:*.lzh=38;5;9:*.lzma=38;5;9:*.tlz=38;5;9:*.txz=38;5;9:*.tzo=38;5;9:*.t7z=38;5;9:*.zip=38;5;9:*.z=38;5;9:*.Z=38;5;9:*.dz=38;5;9:*.gz=38;5;9:*.lrz=38;5;9:*.lz=38;5;9:*.lzo=38;5;9:*.xz=38;5;9:*.bz2=38;5;9:*.bz=38;5;9:*.tbz=38;5;9:*.tbz2=38;5;9:*.tz=38;5;9:*.deb=38;5;9:*.rpm=38;5;9:*.jar=38;5;9:*.war=38;5;9:*.ear=38;5;9:*.sar=38;5;9:*.rar=38;5;9:*.alz=38;5;9:*.ace=38;5;9:*.zoo=38;5;9:*.cpio=38;5;9:*.7z=38;5;9:*.rz=38;5;9:*.cab=38;5;9:*.jpg=38;5;13:*.jpeg=38;5;13:*.gif=38;5;13:*.bmp=38;5;13:*.pbm=38;5;13:*.pgm=38;5;13:*.ppm=38;5;13:*.tga=38;5;13:*.xbm=38;5;13:*.xpm=38;5;13:*.tif=38;5;13:*.tiff=38;5;13:*.png=38;5;13:*.svg=38;5;13:*.svgz=38;5;13:*.mng=38;5;13:*.pcx=38;5;13:*.mov=38;5;13:*.mpg=38;5;13:*.mpeg=38;5;13:*.m2v=38;5;13:*.mkv=38;5;13:*.webm=38;5;13:*.ogm=38;5;13:*.mp4=38;5;13:*.m4v=38;5;13:*.mp4v=38;5;13:*.vob=38;5;13:*.qt=38;5;13:*.nuv=38;5;13:*.wmv=38;5;13:*.asf=38;5;13:*.rm=38;5;13:*.rmvb=38;5;13:*.flc=38;5;13:*.avi=38;5;13:*.fli=38;5;13:*.flv=38;5;13:*.gl=38;5;13:*.dl=38;5;13:*.xcf=38;5;13:*.xwd=38;5;13:*.yuv=38;5;13:*.cgm=38;5;13:*.emf=38;5;13:*.axv=38;5;13:*.anx=38;5;13:*.ogv=38;5;13:*.ogx=38;5;13:*.aac=38;5;45:*.au=38;5;45:*.flac=38;5;45:*.mid=38;5;45:*.midi=38;5;45:*.mka=38;5;45:*.mp3=38;5;45:*.mpc=38;5;45:*.ogg=38;5;45:*.ra=38;5;45:*.wav=38;5;45:*.axa=38;5;45:*.oga=38;5;45:*.spx=38;5;45:*.xspf=38;5;45:',
 'MAIL': '/var/spool/mail/root',
 'OLDPWD': '/root/work/code/lanzw_bottle',
 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin',
 'PATH_INFO': '/counter',
 'PWD': '/root/work/code/lanzw_bottle/evolution/evolution_02',
 'QUERY_STRING': '',
 'REMOTE_ADDR': '127.0.0.1',
 'REMOTE_HOST': 'localhost.localdomain',
 'REQUEST_METHOD': 'GET',
 'SCRIPT_NAME': '',
 'SERVER_NAME': 'localhost.localdomain',
 'SERVER_PORT': '8080',
 'SERVER_PROTOCOL': 'HTTP/1.1',
 'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5',
 'SHELL': '/bin/bash',
 'SHLVL': '1',
 'SSH_CLIENT': '122.189.36.128 49753 22',
 'SSH_CONNECTION': '122.189.36.128 49753 172.29.146.40 22',
 'SSH_TTY': '/dev/pts/3',
 'TERM': 'xterm-256color',
 'USER': 'root',
 'XDG_RUNTIME_DIR': '/run/user/0',
 'XDG_SESSION_ID': '9335',
 '_': '/usr/bin/python',
 'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7fe1229091e0>,
 'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x7fe116e0d668>,
 'wsgi.input': <socket._fileobject object at 0x7fe122816d50>,
 'wsgi.multiprocess': False,
 'wsgi.multithread': True,
 'wsgi.run_once': False,
 'wsgi.url_scheme': 'http',
 'wsgi.version': (1, 0)}


# 存储网站 Cookie
$ curl --cookie-jar testcookie.txt http://localhost:8080/counter
You viewed this page 1 times!

{'CONTENT_LENGTH': '',
 'CONTENT_TYPE': 'text/plain',
 'GATEWAY_INTERFACE': 'CGI/1.1',
 'HISTCONTROL': 'ignoredups',
 'HISTSIZE': '1000',
 'HOME': '/root',
 'HOSTNAME': 'lanzhiwang-centos7',
 'HTTP_ACCEPT': '*/*',
 'HTTP_HOST': 'localhost:8080',
 'HTTP_USER_AGENT': 'curl/7.29.0',
 'LANG': 'zh_CN.UTF-8',
 'LESSOPEN': '||/usr/bin/lesspipe.sh %s',
 'LOGNAME': 'root',
 'LS_COLORS': 'rs=0:di=38;5;27:ln=38;5;51:mh=44;38;5;15:pi=40;38;5;11:so=38;5;13:do=38;5;5:bd=48;5;232;38;5;11:cd=48;5;232;38;5;3:or=48;5;232;38;5;9:mi=05;48;5;232;38;5;15:su=48;5;196;38;5;15:sg=48;5;11;38;5;16:ca=48;5;196;38;5;226:tw=48;5;10;38;5;16:ow=48;5;10;38;5;21:st=48;5;21;38;5;15:ex=38;5;34:*.tar=38;5;9:*.tgz=38;5;9:*.arc=38;5;9:*.arj=38;5;9:*.taz=38;5;9:*.lha=38;5;9:*.lz4=38;5;9:*.lzh=38;5;9:*.lzma=38;5;9:*.tlz=38;5;9:*.txz=38;5;9:*.tzo=38;5;9:*.t7z=38;5;9:*.zip=38;5;9:*.z=38;5;9:*.Z=38;5;9:*.dz=38;5;9:*.gz=38;5;9:*.lrz=38;5;9:*.lz=38;5;9:*.lzo=38;5;9:*.xz=38;5;9:*.bz2=38;5;9:*.bz=38;5;9:*.tbz=38;5;9:*.tbz2=38;5;9:*.tz=38;5;9:*.deb=38;5;9:*.rpm=38;5;9:*.jar=38;5;9:*.war=38;5;9:*.ear=38;5;9:*.sar=38;5;9:*.rar=38;5;9:*.alz=38;5;9:*.ace=38;5;9:*.zoo=38;5;9:*.cpio=38;5;9:*.7z=38;5;9:*.rz=38;5;9:*.cab=38;5;9:*.jpg=38;5;13:*.jpeg=38;5;13:*.gif=38;5;13:*.bmp=38;5;13:*.pbm=38;5;13:*.pgm=38;5;13:*.ppm=38;5;13:*.tga=38;5;13:*.xbm=38;5;13:*.xpm=38;5;13:*.tif=38;5;13:*.tiff=38;5;13:*.png=38;5;13:*.svg=38;5;13:*.svgz=38;5;13:*.mng=38;5;13:*.pcx=38;5;13:*.mov=38;5;13:*.mpg=38;5;13:*.mpeg=38;5;13:*.m2v=38;5;13:*.mkv=38;5;13:*.webm=38;5;13:*.ogm=38;5;13:*.mp4=38;5;13:*.m4v=38;5;13:*.mp4v=38;5;13:*.vob=38;5;13:*.qt=38;5;13:*.nuv=38;5;13:*.wmv=38;5;13:*.asf=38;5;13:*.rm=38;5;13:*.rmvb=38;5;13:*.flc=38;5;13:*.avi=38;5;13:*.fli=38;5;13:*.flv=38;5;13:*.gl=38;5;13:*.dl=38;5;13:*.xcf=38;5;13:*.xwd=38;5;13:*.yuv=38;5;13:*.cgm=38;5;13:*.emf=38;5;13:*.axv=38;5;13:*.anx=38;5;13:*.ogv=38;5;13:*.ogx=38;5;13:*.aac=38;5;45:*.au=38;5;45:*.flac=38;5;45:*.mid=38;5;45:*.midi=38;5;45:*.mka=38;5;45:*.mp3=38;5;45:*.mpc=38;5;45:*.ogg=38;5;45:*.ra=38;5;45:*.wav=38;5;45:*.axa=38;5;45:*.oga=38;5;45:*.spx=38;5;45:*.xspf=38;5;45:',
 'MAIL': '/var/spool/mail/root',
 'OLDPWD': '/root/work/code/lanzw_bottle',
 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin',
 'PATH_INFO': '/counter',
 'PWD': '/root/work/code/lanzw_bottle/evolution/evolution_02',
 'QUERY_STRING': '',
 'REMOTE_ADDR': '127.0.0.1',
 'REMOTE_HOST': 'localhost.localdomain',
 'REQUEST_METHOD': 'GET',
 'SCRIPT_NAME': '',
 'SERVER_NAME': 'localhost.localdomain',
 'SERVER_PORT': '8080',
 'SERVER_PROTOCOL': 'HTTP/1.1',
 'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5',
 'SHELL': '/bin/bash',
 'SHLVL': '1',
 'SSH_CLIENT': '122.189.36.128 49753 22',
 'SSH_CONNECTION': '122.189.36.128 49753 172.29.146.40 22',
 'SSH_TTY': '/dev/pts/3',
 'TERM': 'xterm-256color',
 'USER': 'root',
 'XDG_RUNTIME_DIR': '/run/user/0',
 'XDG_SESSION_ID': '9335',
 '_': '/usr/bin/python',
 'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7fe1229091e0>,
 'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x7fe116e0d668>,
 'wsgi.input': <socket._fileobject object at 0x7fe12282e650>,
 'wsgi.multiprocess': False,
 'wsgi.multithread': True,
 'wsgi.run_once': False,
 'wsgi.url_scheme': 'http',
 'wsgi.version': (1, 0)}

$ ll
总用量 8
-rw-r--r-- 1 root root  171 8月  29 14:36 testcookie.txt
drwxr-xr-x 3 root root 4096 7月  31 11:17 work

# 发送网站 Cookie
$ curl --cookie testcookie.txt http://localhost:8080/counter
You viewed this page 2 times!

{'CONTENT_LENGTH': '',
 'CONTENT_TYPE': 'text/plain',
 'GATEWAY_INTERFACE': 'CGI/1.1',
 'HISTCONTROL': 'ignoredups',
 'HISTSIZE': '1000',
 'HOME': '/root',
 'HOSTNAME': 'lanzhiwang-centos7',
 'HTTP_ACCEPT': '*/*',
 'HTTP_COOKIE': 'counter=1',
 'HTTP_HOST': 'localhost:8080',
 'HTTP_USER_AGENT': 'curl/7.29.0',
 'LANG': 'zh_CN.UTF-8',
 'LESSOPEN': '||/usr/bin/lesspipe.sh %s',
 'LOGNAME': 'root',
 'LS_COLORS': 'rs=0:di=38;5;27:ln=38;5;51:mh=44;38;5;15:pi=40;38;5;11:so=38;5;13:do=38;5;5:bd=48;5;232;38;5;11:cd=48;5;232;38;5;3:or=48;5;232;38;5;9:mi=05;48;5;232;38;5;15:su=48;5;196;38;5;15:sg=48;5;11;38;5;16:ca=48;5;196;38;5;226:tw=48;5;10;38;5;16:ow=48;5;10;38;5;21:st=48;5;21;38;5;15:ex=38;5;34:*.tar=38;5;9:*.tgz=38;5;9:*.arc=38;5;9:*.arj=38;5;9:*.taz=38;5;9:*.lha=38;5;9:*.lz4=38;5;9:*.lzh=38;5;9:*.lzma=38;5;9:*.tlz=38;5;9:*.txz=38;5;9:*.tzo=38;5;9:*.t7z=38;5;9:*.zip=38;5;9:*.z=38;5;9:*.Z=38;5;9:*.dz=38;5;9:*.gz=38;5;9:*.lrz=38;5;9:*.lz=38;5;9:*.lzo=38;5;9:*.xz=38;5;9:*.bz2=38;5;9:*.bz=38;5;9:*.tbz=38;5;9:*.tbz2=38;5;9:*.tz=38;5;9:*.deb=38;5;9:*.rpm=38;5;9:*.jar=38;5;9:*.war=38;5;9:*.ear=38;5;9:*.sar=38;5;9:*.rar=38;5;9:*.alz=38;5;9:*.ace=38;5;9:*.zoo=38;5;9:*.cpio=38;5;9:*.7z=38;5;9:*.rz=38;5;9:*.cab=38;5;9:*.jpg=38;5;13:*.jpeg=38;5;13:*.gif=38;5;13:*.bmp=38;5;13:*.pbm=38;5;13:*.pgm=38;5;13:*.ppm=38;5;13:*.tga=38;5;13:*.xbm=38;5;13:*.xpm=38;5;13:*.tif=38;5;13:*.tiff=38;5;13:*.png=38;5;13:*.svg=38;5;13:*.svgz=38;5;13:*.mng=38;5;13:*.pcx=38;5;13:*.mov=38;5;13:*.mpg=38;5;13:*.mpeg=38;5;13:*.m2v=38;5;13:*.mkv=38;5;13:*.webm=38;5;13:*.ogm=38;5;13:*.mp4=38;5;13:*.m4v=38;5;13:*.mp4v=38;5;13:*.vob=38;5;13:*.qt=38;5;13:*.nuv=38;5;13:*.wmv=38;5;13:*.asf=38;5;13:*.rm=38;5;13:*.rmvb=38;5;13:*.flc=38;5;13:*.avi=38;5;13:*.fli=38;5;13:*.flv=38;5;13:*.gl=38;5;13:*.dl=38;5;13:*.xcf=38;5;13:*.xwd=38;5;13:*.yuv=38;5;13:*.cgm=38;5;13:*.emf=38;5;13:*.axv=38;5;13:*.anx=38;5;13:*.ogv=38;5;13:*.ogx=38;5;13:*.aac=38;5;45:*.au=38;5;45:*.flac=38;5;45:*.mid=38;5;45:*.midi=38;5;45:*.mka=38;5;45:*.mp3=38;5;45:*.mpc=38;5;45:*.ogg=38;5;45:*.ra=38;5;45:*.wav=38;5;45:*.axa=38;5;45:*.oga=38;5;45:*.spx=38;5;45:*.xspf=38;5;45:',
 'MAIL': '/var/spool/mail/root',
 'OLDPWD': '/root/work/code/lanzw_bottle',
 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin',
 'PATH_INFO': '/counter',
 'PWD': '/root/work/code/lanzw_bottle/evolution/evolution_02',
 'QUERY_STRING': '',
 'REMOTE_ADDR': '127.0.0.1',
 'REMOTE_HOST': 'localhost.localdomain',
 'REQUEST_METHOD': 'GET',
 'SCRIPT_NAME': '',
 'SERVER_NAME': 'localhost.localdomain',
 'SERVER_PORT': '8080',
 'SERVER_PROTOCOL': 'HTTP/1.1',
 'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5',
 'SHELL': '/bin/bash',
 'SHLVL': '1',
 'SSH_CLIENT': '122.189.36.128 49753 22',
 'SSH_CONNECTION': '122.189.36.128 49753 172.29.146.40 22',
 'SSH_TTY': '/dev/pts/3',
 'TERM': 'xterm-256color',
 'USER': 'root',
 'XDG_RUNTIME_DIR': '/run/user/0',
 'XDG_SESSION_ID': '9335',
 '_': '/usr/bin/python',
 'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7fe1229091e0>,
 'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x7fe116e0d668>,
 'wsgi.input': <socket._fileobject object at 0x7fe122816d50>,
 'wsgi.multiprocess': False,
 'wsgi.multithread': True,
 'wsgi.run_once': False,
 'wsgi.url_scheme': 'http',
 'wsgi.version': (1, 0)}

"""

# URL-parameter are a useful tool and generate nice looking URLs
# This handles requests such as '/hello/Tim' or '/hello/Jane'
@route('/hello/:name')
def hello_url(name):
    return 'hhhHello %s!' % name
"""
$ curl http://localhost:8080/hello/Tim
hhhHello Tim!
$ curl http://localhost:8080/hello/tom
hhhHello tom!

{'CONTENT_LENGTH': '',
 'CONTENT_TYPE': 'text/plain',
 'GATEWAY_INTERFACE': 'CGI/1.1',
 'HISTCONTROL': 'ignoredups',
 'HISTSIZE': '1000',
 'HOME': '/root',
 'HOSTNAME': 'lanzhiwang-centos7',
 'HTTP_ACCEPT': '*/*',
 'HTTP_HOST': 'localhost:8080',
 'HTTP_USER_AGENT': 'curl/7.29.0',
 'LANG': 'zh_CN.UTF-8',
 'LESSOPEN': '||/usr/bin/lesspipe.sh %s',
 'LOGNAME': 'root',
 'LS_COLORS': 'rs=0:di=38;5;27:ln=38;5;51:mh=44;38;5;15:pi=40;38;5;11:so=38;5;13:do=38;5;5:bd=48;5;232;38;5;11:cd=48;5;232;38;5;3:or=48;5;232;38;5;9:mi=05;48;5;232;38;5;15:su=48;5;196;38;5;15:sg=48;5;11;38;5;16:ca=48;5;196;38;5;226:tw=48;5;10;38;5;16:ow=48;5;10;38;5;21:st=48;5;21;38;5;15:ex=38;5;34:*.tar=38;5;9:*.tgz=38;5;9:*.arc=38;5;9:*.arj=38;5;9:*.taz=38;5;9:*.lha=38;5;9:*.lz4=38;5;9:*.lzh=38;5;9:*.lzma=38;5;9:*.tlz=38;5;9:*.txz=38;5;9:*.tzo=38;5;9:*.t7z=38;5;9:*.zip=38;5;9:*.z=38;5;9:*.Z=38;5;9:*.dz=38;5;9:*.gz=38;5;9:*.lrz=38;5;9:*.lz=38;5;9:*.lzo=38;5;9:*.xz=38;5;9:*.bz2=38;5;9:*.bz=38;5;9:*.tbz=38;5;9:*.tbz2=38;5;9:*.tz=38;5;9:*.deb=38;5;9:*.rpm=38;5;9:*.jar=38;5;9:*.war=38;5;9:*.ear=38;5;9:*.sar=38;5;9:*.rar=38;5;9:*.alz=38;5;9:*.ace=38;5;9:*.zoo=38;5;9:*.cpio=38;5;9:*.7z=38;5;9:*.rz=38;5;9:*.cab=38;5;9:*.jpg=38;5;13:*.jpeg=38;5;13:*.gif=38;5;13:*.bmp=38;5;13:*.pbm=38;5;13:*.pgm=38;5;13:*.ppm=38;5;13:*.tga=38;5;13:*.xbm=38;5;13:*.xpm=38;5;13:*.tif=38;5;13:*.tiff=38;5;13:*.png=38;5;13:*.svg=38;5;13:*.svgz=38;5;13:*.mng=38;5;13:*.pcx=38;5;13:*.mov=38;5;13:*.mpg=38;5;13:*.mpeg=38;5;13:*.m2v=38;5;13:*.mkv=38;5;13:*.webm=38;5;13:*.ogm=38;5;13:*.mp4=38;5;13:*.m4v=38;5;13:*.mp4v=38;5;13:*.vob=38;5;13:*.qt=38;5;13:*.nuv=38;5;13:*.wmv=38;5;13:*.asf=38;5;13:*.rm=38;5;13:*.rmvb=38;5;13:*.flc=38;5;13:*.avi=38;5;13:*.fli=38;5;13:*.flv=38;5;13:*.gl=38;5;13:*.dl=38;5;13:*.xcf=38;5;13:*.xwd=38;5;13:*.yuv=38;5;13:*.cgm=38;5;13:*.emf=38;5;13:*.axv=38;5;13:*.anx=38;5;13:*.ogv=38;5;13:*.ogx=38;5;13:*.aac=38;5;45:*.au=38;5;45:*.flac=38;5;45:*.mid=38;5;45:*.midi=38;5;45:*.mka=38;5;45:*.mp3=38;5;45:*.mpc=38;5;45:*.ogg=38;5;45:*.ra=38;5;45:*.wav=38;5;45:*.axa=38;5;45:*.oga=38;5;45:*.spx=38;5;45:*.xspf=38;5;45:',
 'MAIL': '/var/spool/mail/root',
 'OLDPWD': '/root/work/code/lanzw_bottle',
 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin',
 'PATH_INFO': '/hello/tom',
 'PWD': '/root/work/code/lanzw_bottle/evolution/evolution_02',
 'QUERY_STRING': '',
 'REMOTE_ADDR': '127.0.0.1',
 'REMOTE_HOST': 'localhost.localdomain',
 'REQUEST_METHOD': 'GET',
 'SCRIPT_NAME': '',
 'SERVER_NAME': 'localhost.localdomain',
 'SERVER_PORT': '8080',
 'SERVER_PROTOCOL': 'HTTP/1.1',
 'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5',
 'SHELL': '/bin/bash',
 'SHLVL': '1',
 'SSH_CLIENT': '122.189.36.128 49753 22',
 'SSH_CONNECTION': '122.189.36.128 49753 172.29.146.40 22',
 'SSH_TTY': '/dev/pts/3',
 'TERM': 'xterm-256color',
 'USER': 'root',
 'XDG_RUNTIME_DIR': '/run/user/0',
 'XDG_SESSION_ID': '9335',
 '_': '/usr/bin/python',
 'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7fe1229091e0>,
 'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x7fe116e0d668>,
 'wsgi.input': <socket._fileobject object at 0x7fe12282e650>,
 'wsgi.multiprocess': False,
 'wsgi.multithread': True,
 'wsgi.run_once': False,
 'wsgi.url_scheme': 'http',
 'wsgi.version': (1, 0)}

"""

# By default, an URL parameter matches everything up to the next slash.
# You can change that behaviour by adding a regular expression between two '#'
# in this example, :num will only match one or more digits.
# Requests to '/number/Tim' won't work (and result in a 404)
@route('/number/:num#[0-9]+#')
def hello_number(num):
    return "Your number is %d" % int(num)
"""
$ curl http://localhost:8080/number/6
Your number is 6
$ curl http://localhost:8080/number/tom
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>Error 404: Not Found</title></head><body><h1>Error 404: Not Found</h1><p>Sorry, the requested URL /number/tom caused an error.</p>Not found</body></html>
"""

# How to send a static file to the Browser? Just name it.
# Bottle does the content-type guessing and save path checking for you.
@route('/static/:filename#.*#')
def static_file(filename):
    send_file(filename, root='/root/work/code/lanzw_bottle/evolution/evolution_02/')
"""
$ curl http://localhost:8080/static/README
Bottle Web Framework
====================

`Bottle` is a simple, fast and useful one-file WSGI-framework. It is not a
full-stack framework with a ton of features, but a useful mirco-framework for
small web-applications that stays out of your way.


$ curl http://localhost:8080/static/README -o README
$ ll
总用量 12
-rw-r--r-- 1 root root 3782 8月  29 14:47 README
-rw-r--r-- 1 root root  171 8月  29 14:39 testcookie.txt
drwxr-xr-x 3 root root 4096 7月  31 11:17 work
$ cat README
Bottle Web Framework
====================

`Bottle` is a simple, fast and useful one-file WSGI-framework. It is not a
full-stack framework with a ton of features, but a useful mirco-framework for
small web-applications that stays out of your way.


{'CONTENT_LENGTH': '',
 'CONTENT_TYPE': 'text/plain',
 'GATEWAY_INTERFACE': 'CGI/1.1',
 'HISTCONTROL': 'ignoredups',
 'HISTSIZE': '1000',
 'HOME': '/root',
 'HOSTNAME': 'lanzhiwang-centos7',
 'HTTP_ACCEPT': '*/*',
 'HTTP_HOST': 'localhost:8080',
 'HTTP_USER_AGENT': 'curl/7.29.0',
 'LANG': 'zh_CN.UTF-8',
 'LESSOPEN': '||/usr/bin/lesspipe.sh %s',
 'LOGNAME': 'root',
 'LS_COLORS': 'rs=0:di=38;5;27:ln=38;5;51:mh=44;38;5;15:pi=40;38;5;11:so=38;5;13:do=38;5;5:bd=48;5;232;38;5;11:cd=48;5;232;38;5;3:or=48;5;232;38;5;9:mi=05;48;5;232;38;5;15:su=48;5;196;38;5;15:sg=48;5;11;38;5;16:ca=48;5;196;38;5;226:tw=48;5;10;38;5;16:ow=48;5;10;38;5;21:st=48;5;21;38;5;15:ex=38;5;34:*.tar=38;5;9:*.tgz=38;5;9:*.arc=38;5;9:*.arj=38;5;9:*.taz=38;5;9:*.lha=38;5;9:*.lz4=38;5;9:*.lzh=38;5;9:*.lzma=38;5;9:*.tlz=38;5;9:*.txz=38;5;9:*.tzo=38;5;9:*.t7z=38;5;9:*.zip=38;5;9:*.z=38;5;9:*.Z=38;5;9:*.dz=38;5;9:*.gz=38;5;9:*.lrz=38;5;9:*.lz=38;5;9:*.lzo=38;5;9:*.xz=38;5;9:*.bz2=38;5;9:*.bz=38;5;9:*.tbz=38;5;9:*.tbz2=38;5;9:*.tz=38;5;9:*.deb=38;5;9:*.rpm=38;5;9:*.jar=38;5;9:*.war=38;5;9:*.ear=38;5;9:*.sar=38;5;9:*.rar=38;5;9:*.alz=38;5;9:*.ace=38;5;9:*.zoo=38;5;9:*.cpio=38;5;9:*.7z=38;5;9:*.rz=38;5;9:*.cab=38;5;9:*.jpg=38;5;13:*.jpeg=38;5;13:*.gif=38;5;13:*.bmp=38;5;13:*.pbm=38;5;13:*.pgm=38;5;13:*.ppm=38;5;13:*.tga=38;5;13:*.xbm=38;5;13:*.xpm=38;5;13:*.tif=38;5;13:*.tiff=38;5;13:*.png=38;5;13:*.svg=38;5;13:*.svgz=38;5;13:*.mng=38;5;13:*.pcx=38;5;13:*.mov=38;5;13:*.mpg=38;5;13:*.mpeg=38;5;13:*.m2v=38;5;13:*.mkv=38;5;13:*.webm=38;5;13:*.ogm=38;5;13:*.mp4=38;5;13:*.m4v=38;5;13:*.mp4v=38;5;13:*.vob=38;5;13:*.qt=38;5;13:*.nuv=38;5;13:*.wmv=38;5;13:*.asf=38;5;13:*.rm=38;5;13:*.rmvb=38;5;13:*.flc=38;5;13:*.avi=38;5;13:*.fli=38;5;13:*.flv=38;5;13:*.gl=38;5;13:*.dl=38;5;13:*.xcf=38;5;13:*.xwd=38;5;13:*.yuv=38;5;13:*.cgm=38;5;13:*.emf=38;5;13:*.axv=38;5;13:*.anx=38;5;13:*.ogv=38;5;13:*.ogx=38;5;13:*.aac=38;5;45:*.au=38;5;45:*.flac=38;5;45:*.mid=38;5;45:*.midi=38;5;45:*.mka=38;5;45:*.mp3=38;5;45:*.mpc=38;5;45:*.ogg=38;5;45:*.ra=38;5;45:*.wav=38;5;45:*.axa=38;5;45:*.oga=38;5;45:*.spx=38;5;45:*.xspf=38;5;45:',
 'MAIL': '/var/spool/mail/root',
 'OLDPWD': '/root/work/code/lanzw_bottle',
 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin',
 'PATH_INFO': '/static/README',
 'PWD': '/root/work/code/lanzw_bottle/evolution/evolution_02',
 'QUERY_STRING': '',
 'REMOTE_ADDR': '127.0.0.1',
 'REMOTE_HOST': 'localhost.localdomain',
 'REQUEST_METHOD': 'GET',
 'SCRIPT_NAME': '',
 'SERVER_NAME': 'localhost.localdomain',
 'SERVER_PORT': '8080',
 'SERVER_PROTOCOL': 'HTTP/1.1',
 'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5',
 'SHELL': '/bin/bash',
 'SHLVL': '1',
 'SSH_CLIENT': '122.189.36.128 49753 22',
 'SSH_CONNECTION': '122.189.36.128 49753 172.29.146.40 22',
 'SSH_TTY': '/dev/pts/3',
 'TERM': 'xterm-256color',
 'USER': 'root',
 'XDG_RUNTIME_DIR': '/run/user/0',
 'XDG_SESSION_ID': '9335',
 '_': '/usr/bin/python',
 'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7fe1229091e0>,
 'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x7fe116e0d668>,
 'wsgi.input': <socket._fileobject object at 0x7fe122816d50>,
 'wsgi.multiprocess': False,
 'wsgi.multithread': True,
 'wsgi.run_once': False,
 'wsgi.url_scheme': 'http',
 'wsgi.version': (1, 0)}

"""

# You can manually add header and set the content-type of the response.
@route('/json')
def json():
    response.header['Cache-Control'] = 'no-cache, must-revalidate'
    response.content_type = 'application/json'
    return "{counter:%d}" % int(request.COOKIES.get('counter',0))
"""
$ curl http://localhost:8080/json
{counter:0}
$ curl --cookie testcookie.txt http://localhost:8080/json
{counter:1}

$ curl --cookie testcookie.txt -v http://localhost:8080/json
* About to connect() to localhost port 8080 (#0)
*   Trying 127.0.0.1...
* Connected to localhost (127.0.0.1) port 8080 (#0)
> GET /json HTTP/1.1
> User-Agent: curl/7.29.0
> Host: localhost:8080
> Accept: */*
> Cookie: counter=1
>
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Date: Sat, 29 Aug 2020 06:54:45 GMT
< Server: WSGIServer/0.1 Python/2.7.5
< Content-Type: application/json
< Cache-Control: no-cache, must-revalidate
<
* Closing connection 0
{counter:1}
"""

# Throwing an error using abort()
@route('/private')
def private():
    if request.GET.get('password','') != 'secret':
        abort(401, 'Go away!')
    return "Welcome!"
"""
$ curl http://localhost:8080/private
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>Error 401: Unauthorized</title></head><body><h1>Error 401: Unauthorized</h1><p>Sorry, the requested URL /private caused an error.</p>Go away!</body></html>

$ curl http://localhost:8080/private?password=secret
Welcome!

$ curl http://localhost:8080/private?password=error
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>Error 401: Unauthorized</title></head><body><h1>Error 401: Unauthorized</h1><p>Sorry, the requested URL /private caused an error.</p>Go away!</body></html>

{'CONTENT_LENGTH': '',
 'CONTENT_TYPE': 'text/plain',
 'GATEWAY_INTERFACE': 'CGI/1.1',
 'HISTCONTROL': 'ignoredups',
 'HISTSIZE': '1000',
 'HOME': '/root',
 'HOSTNAME': 'lanzhiwang-centos7',
 'HTTP_ACCEPT': '*/*',
 'HTTP_HOST': 'localhost:8080',
 'HTTP_USER_AGENT': 'curl/7.29.0',
 'LANG': 'zh_CN.UTF-8',
 'LESSOPEN': '||/usr/bin/lesspipe.sh %s',
 'LOGNAME': 'root',
 'LS_COLORS': 'rs=0:di=38;5;27:ln=38;5;51:mh=44;38;5;15:pi=40;38;5;11:so=38;5;13:do=38;5;5:bd=48;5;232;38;5;11:cd=48;5;232;38;5;3:or=48;5;232;38;5;9:mi=05;48;5;232;38;5;15:su=48;5;196;38;5;15:sg=48;5;11;38;5;16:ca=48;5;196;38;5;226:tw=48;5;10;38;5;16:ow=48;5;10;38;5;21:st=48;5;21;38;5;15:ex=38;5;34:*.tar=38;5;9:*.tgz=38;5;9:*.arc=38;5;9:*.arj=38;5;9:*.taz=38;5;9:*.lha=38;5;9:*.lz4=38;5;9:*.lzh=38;5;9:*.lzma=38;5;9:*.tlz=38;5;9:*.txz=38;5;9:*.tzo=38;5;9:*.t7z=38;5;9:*.zip=38;5;9:*.z=38;5;9:*.Z=38;5;9:*.dz=38;5;9:*.gz=38;5;9:*.lrz=38;5;9:*.lz=38;5;9:*.lzo=38;5;9:*.xz=38;5;9:*.bz2=38;5;9:*.bz=38;5;9:*.tbz=38;5;9:*.tbz2=38;5;9:*.tz=38;5;9:*.deb=38;5;9:*.rpm=38;5;9:*.jar=38;5;9:*.war=38;5;9:*.ear=38;5;9:*.sar=38;5;9:*.rar=38;5;9:*.alz=38;5;9:*.ace=38;5;9:*.zoo=38;5;9:*.cpio=38;5;9:*.7z=38;5;9:*.rz=38;5;9:*.cab=38;5;9:*.jpg=38;5;13:*.jpeg=38;5;13:*.gif=38;5;13:*.bmp=38;5;13:*.pbm=38;5;13:*.pgm=38;5;13:*.ppm=38;5;13:*.tga=38;5;13:*.xbm=38;5;13:*.xpm=38;5;13:*.tif=38;5;13:*.tiff=38;5;13:*.png=38;5;13:*.svg=38;5;13:*.svgz=38;5;13:*.mng=38;5;13:*.pcx=38;5;13:*.mov=38;5;13:*.mpg=38;5;13:*.mpeg=38;5;13:*.m2v=38;5;13:*.mkv=38;5;13:*.webm=38;5;13:*.ogm=38;5;13:*.mp4=38;5;13:*.m4v=38;5;13:*.mp4v=38;5;13:*.vob=38;5;13:*.qt=38;5;13:*.nuv=38;5;13:*.wmv=38;5;13:*.asf=38;5;13:*.rm=38;5;13:*.rmvb=38;5;13:*.flc=38;5;13:*.avi=38;5;13:*.fli=38;5;13:*.flv=38;5;13:*.gl=38;5;13:*.dl=38;5;13:*.xcf=38;5;13:*.xwd=38;5;13:*.yuv=38;5;13:*.cgm=38;5;13:*.emf=38;5;13:*.axv=38;5;13:*.anx=38;5;13:*.ogv=38;5;13:*.ogx=38;5;13:*.aac=38;5;45:*.au=38;5;45:*.flac=38;5;45:*.mid=38;5;45:*.midi=38;5;45:*.mka=38;5;45:*.mp3=38;5;45:*.mpc=38;5;45:*.ogg=38;5;45:*.ra=38;5;45:*.wav=38;5;45:*.axa=38;5;45:*.oga=38;5;45:*.spx=38;5;45:*.xspf=38;5;45:',
 'MAIL': '/var/spool/mail/root',
 'OLDPWD': '/root/work/code/lanzw_bottle',
 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin',
 'PATH_INFO': '/private',
 'PWD': '/root/work/code/lanzw_bottle/evolution/evolution_02',
 'QUERY_STRING': 'password=secret',
 'REMOTE_ADDR': '127.0.0.1',
 'REMOTE_HOST': 'localhost.localdomain',
 'REQUEST_METHOD': 'GET',
 'SCRIPT_NAME': '',
 'SERVER_NAME': 'localhost.localdomain',
 'SERVER_PORT': '8080',
 'SERVER_PROTOCOL': 'HTTP/1.1',
 'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5',
 'SHELL': '/bin/bash',
 'SHLVL': '1',
 'SSH_CLIENT': '122.189.36.128 49753 22',
 'SSH_CONNECTION': '122.189.36.128 49753 172.29.146.40 22',
 'SSH_TTY': '/dev/pts/3',
 'TERM': 'xterm-256color',
 'USER': 'root',
 'XDG_RUNTIME_DIR': '/run/user/0',
 'XDG_SESSION_ID': '9335',
 '_': '/usr/bin/python',
 'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7fe1229091e0>,
 'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x7fe116e0d668>,
 'wsgi.input': <socket._fileobject object at 0x7fe12282e650>,
 'wsgi.multiprocess': False,
 'wsgi.multithread': True,
 'wsgi.run_once': False,
 'wsgi.url_scheme': 'http',
 'wsgi.version': (1, 0)}

"""

# Validating URL Parameter
@route('/validate/:i/:f/:csv')
@validate(i=int, f=float, csv=lambda x: map(int, x.strip().split(',')))
def validate_test(i, f, csv):
    return "Int: %d, Float:%f, List:%s" % (i, f, repr(csv))
"""
$ curl "http://localhost:8080/validate/10/10.2/csv1,csv2"
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>Error 400: Bad Request</title></head><body><h1>Error 400: Bad Request</h1><p>Sorry, the requested URL /validate/10/10.2/csv1,csv2 caused an error.</p>Wrong parameter format for: csv</body></html>

$ curl "http://localhost:8080/validate/10/10.2/1,2"
Int: 10, Float:10.200000, List:[1, 2]

{'CONTENT_LENGTH': '',
 'CONTENT_TYPE': 'text/plain',
 'GATEWAY_INTERFACE': 'CGI/1.1',
 'HISTCONTROL': 'ignoredups',
 'HISTSIZE': '1000',
 'HOME': '/root',
 'HOSTNAME': 'lanzhiwang-centos7',
 'HTTP_ACCEPT': '*/*',
 'HTTP_HOST': 'localhost:8080',
 'HTTP_USER_AGENT': 'curl/7.29.0',
 'LANG': 'zh_CN.UTF-8',
 'LESSOPEN': '||/usr/bin/lesspipe.sh %s',
 'LOGNAME': 'root',
 'LS_COLORS': 'rs=0:di=38;5;27:ln=38;5;51:mh=44;38;5;15:pi=40;38;5;11:so=38;5;13:do=38;5;5:bd=48;5;232;38;5;11:cd=48;5;232;38;5;3:or=48;5;232;38;5;9:mi=05;48;5;232;38;5;15:su=48;5;196;38;5;15:sg=48;5;11;38;5;16:ca=48;5;196;38;5;226:tw=48;5;10;38;5;16:ow=48;5;10;38;5;21:st=48;5;21;38;5;15:ex=38;5;34:*.tar=38;5;9:*.tgz=38;5;9:*.arc=38;5;9:*.arj=38;5;9:*.taz=38;5;9:*.lha=38;5;9:*.lz4=38;5;9:*.lzh=38;5;9:*.lzma=38;5;9:*.tlz=38;5;9:*.txz=38;5;9:*.tzo=38;5;9:*.t7z=38;5;9:*.zip=38;5;9:*.z=38;5;9:*.Z=38;5;9:*.dz=38;5;9:*.gz=38;5;9:*.lrz=38;5;9:*.lz=38;5;9:*.lzo=38;5;9:*.xz=38;5;9:*.bz2=38;5;9:*.bz=38;5;9:*.tbz=38;5;9:*.tbz2=38;5;9:*.tz=38;5;9:*.deb=38;5;9:*.rpm=38;5;9:*.jar=38;5;9:*.war=38;5;9:*.ear=38;5;9:*.sar=38;5;9:*.rar=38;5;9:*.alz=38;5;9:*.ace=38;5;9:*.zoo=38;5;9:*.cpio=38;5;9:*.7z=38;5;9:*.rz=38;5;9:*.cab=38;5;9:*.jpg=38;5;13:*.jpeg=38;5;13:*.gif=38;5;13:*.bmp=38;5;13:*.pbm=38;5;13:*.pgm=38;5;13:*.ppm=38;5;13:*.tga=38;5;13:*.xbm=38;5;13:*.xpm=38;5;13:*.tif=38;5;13:*.tiff=38;5;13:*.png=38;5;13:*.svg=38;5;13:*.svgz=38;5;13:*.mng=38;5;13:*.pcx=38;5;13:*.mov=38;5;13:*.mpg=38;5;13:*.mpeg=38;5;13:*.m2v=38;5;13:*.mkv=38;5;13:*.webm=38;5;13:*.ogm=38;5;13:*.mp4=38;5;13:*.m4v=38;5;13:*.mp4v=38;5;13:*.vob=38;5;13:*.qt=38;5;13:*.nuv=38;5;13:*.wmv=38;5;13:*.asf=38;5;13:*.rm=38;5;13:*.rmvb=38;5;13:*.flc=38;5;13:*.avi=38;5;13:*.fli=38;5;13:*.flv=38;5;13:*.gl=38;5;13:*.dl=38;5;13:*.xcf=38;5;13:*.xwd=38;5;13:*.yuv=38;5;13:*.cgm=38;5;13:*.emf=38;5;13:*.axv=38;5;13:*.anx=38;5;13:*.ogv=38;5;13:*.ogx=38;5;13:*.aac=38;5;45:*.au=38;5;45:*.flac=38;5;45:*.mid=38;5;45:*.midi=38;5;45:*.mka=38;5;45:*.mp3=38;5;45:*.mpc=38;5;45:*.ogg=38;5;45:*.ra=38;5;45:*.wav=38;5;45:*.axa=38;5;45:*.oga=38;5;45:*.spx=38;5;45:*.xspf=38;5;45:',
 'MAIL': '/var/spool/mail/root',
 'OLDPWD': '/root/work/code/lanzw_bottle',
 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin',
 'PATH_INFO': '/validate/10/10.2/1,2',
 'PWD': '/root/work/code/lanzw_bottle/evolution/evolution_02',
 'QUERY_STRING': '',
 'REMOTE_ADDR': '127.0.0.1',
 'REMOTE_HOST': 'localhost.localdomain',
 'REQUEST_METHOD': 'GET',
 'SCRIPT_NAME': '',
 'SERVER_NAME': 'localhost.localdomain',
 'SERVER_PORT': '8080',
 'SERVER_PROTOCOL': 'HTTP/1.1',
 'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5',
 'SHELL': '/bin/bash',
 'SHLVL': '1',
 'SSH_CLIENT': '122.189.36.128 49753 22',
 'SSH_CONNECTION': '122.189.36.128 49753 172.29.146.40 22',
 'SSH_TTY': '/dev/pts/3',
 'TERM': 'xterm-256color',
 'USER': 'root',
 'XDG_RUNTIME_DIR': '/run/user/0',
 'XDG_SESSION_ID': '9335',
 '_': '/usr/bin/python',
 'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7fe1229091e0>,
 'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x7fe116e0d668>,
 'wsgi.input': <socket._fileobject object at 0x7fe122816d50>,
 'wsgi.multiprocess': False,
 'wsgi.multithread': True,
 'wsgi.run_once': False,
 'wsgi.url_scheme': 'http',
 'wsgi.version': (1, 0)}

"""

run(host='localhost', port=8080)
