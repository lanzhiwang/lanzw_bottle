# lanzw.py

## 背景说明

一直使用各种框架做各种项目，用得最多的就是 web 相关的框架了，Python 相关的主要是 flask 和 bottle 两个。之前认真仔细的看过 flask 和 bottle 框架的测试用例，也看过 bottle 的源码，算是对相关框架比较熟悉。在工作中也涉及公司自己开发的小型框架。因此一直想自己写一个小型框架，目的是一方面总结之前在公司写的小型框架，另一方面学习流行的开源框架是怎样写的。所以就有了这个边学习边总结写的这个小型的框架了。

## 框架演进说明

我并不是要写一个和 falsk 或者 bottle 那样的很流行的，很方便使用的开源框架，只是看源码的过程中记录 bottle 框架的写法，一步一步从小到大说明一个框架是怎样成形的。

整个框架的目录结构如下所示：

```bash
$ tree -a .
.
├── README.md
├── evolution
│   └── evolution_0001.py
└── lanzw.py

1 directory, 3 files
$ 
```

其中：evolution 目录中的文件就是从小到大的写出一个小型框架的过程，文件命名已数字结尾，可以按顺序新建文件，在新增加的文件中增加新的功能。

lanzw.py 文件汇总了整个框架的功能。


## 参考

[Bottle.py history](https://github.com/bottlepy/bottle/commits/master?after=357a0cb39cb8337f8467f5396e4b7caaa7e4f25c+979&path%5B%5D=bottle.py)

提交历史

https://github.com/bottlepy/bottle/commits/master?before=357a0cb39cb8337f8467f5396e4b7caaa7e4f25c+980&path%5B%5D=bottle.py

git checkout -b evolution_02 444443ce1d863dbb91e141891f7f514865dcae61