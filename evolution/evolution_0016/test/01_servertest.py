# -*- coding: utf-8 -*-

import sys, os
test_root = os.path.dirname(os.path.abspath(__file__))  # /root/work/lanzw_frame/evolution/evolution_0016/test
os.chdir(test_root)
# print os.path.dirname(test_root)  # /root/work/lanzw_frame/evolution/evolution_0016
sys.path.insert(0, os.path.dirname(test_root))
sys.path.insert(0, test_root)

import bottle
from bottle import route, run

if 'coverage' in sys.argv:
    import coverage
    # coverage.py是一个用来统计python程序代码覆盖率的工具。
    # 它使用起来非常简单，并且支持最终生成界面友好的html报告。在最新版本中，还提供了分支覆盖的功能。

    cov = coverage.coverage(data_suffix=True, branch=True)
    cov.start()

@route()
def test():
    return "OK"

# python servertest.py wsgiref 8080 coverage
if __name__ == '__main__':
    server = sys.argv[1]
    port   = int(sys.argv[2])
    print server
    print port
    try:
        run(port=port, server=server, quiet=True)
    except ImportError:
        print "Warning: Could not test %s. Import error." % server
    except KeyboardInterrupt:
        pass

    if 'coverage' in sys.argv:
        cov.stop()
        cov.save()

