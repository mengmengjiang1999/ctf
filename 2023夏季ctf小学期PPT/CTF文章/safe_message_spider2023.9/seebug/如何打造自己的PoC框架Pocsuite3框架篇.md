**作者：w7ay@知道创宇404实验室  
English version: <https://paper.seebug.org/914/>  
相关阅读：[如何打造自己的PoC框架-Pocsuite3-使用篇](https://paper.seebug.org/904/ "如何打造自己的PoC框架-Pocsuite3-使用篇")**

本节笔者将按照Pocsuite框架结构以及工程化实践，来实现一款自己的PoC框架。为了开一个好头，我们先取一个好听的名字，想威武霸气一些可以取上古神器之类的，诸如轩辕夏禹赤霄干将，若怀着对游戏的热爱也可以有山丘之王（Mountain
King）剑圣（BladeMaster）月之女神（Priess Of the
moon）。由于笔者比较懒，我们就取一个朴素的名字：AirPoc，中文名叫它"空气炮"吧。

名称取好了，我们还要幻想一下大饼。这里请充分发挥想象力，幻想它的功能，你要记住，没有我们实现不了的功能，如果有，打死产品manager即可。

这里不妨开下脑洞，为了组建兔子安全联盟，我们计划开发一款基于区块链的PoC验证框架AirPoc，限定只对"兔子安全联盟”范围内的网站进行安全检查，由一个AirPoc节点检查出了存在漏洞的地址，将URL和PoC共享到区块中，再由随机的其他节点验证，验证成功则获得"空气币"，而被检测到的网站所有者则需要支付"空气币"作为报酬。

虽然只是暂时的幻想，但是产品小哥哥也略带激动整理出了我们需要的功能。

  1. 使用简单，不要有太多的命令，可以跨平台使用
  2. 人多力量大，能让更多人参与进来的
  3. 能简单操作就能内置到其他产品上
  4. 验证速度与验证准确率极高！
  5. 我也不知道什么好，总之你跑起来能出东西就行！

当然，这位产品小哥哥可能怕被打，没有将分布式，区块链的概念加入进来。

## 具体细节

下面就由笔者来具体实现由笔者兼职的产品manager随便一想（挖坑）的东西。我们逐一分析问题，并给出最后的解决方案。

说到使用简单，我们就任性的选择使用Python了，不信你看看Python之父的头发。在安装了Python之后，也可以一份代码多处使用，但为了足够的简单与原生，我们决定尽量少使用Python的第三方包。而目前Python最新版为3.7，我们就以此为例。

国外的众多开源安全项目都有不少人参与，像Metasploit

![image-20190425142853330](https://images.seebug.org/content/images/2019/05/06/1557118879000-image-20190425142853330.png-w331s)

Sqlmap

![image-20190425142829862](https://images.seebug.org/content/images/2019/05/06/1557118880000-image-20190425142829862.png-w331s)

Routersploit

![image-20190425142732368](https://images.seebug.org/content/images/2019/05/06/1557118880000-image-20190425142732368.png-w331s)

能贡献一份代码到上面可能是安全研究人员最想做的事情吧。

所以笔者有个想法是AirPoc的PoC仓库可以开源到GitHub，并且能够在线调用上面的PoC，这样也不会为了PoC的更新而烦恼了。

内置到其他产品也更是容易，如果是Python类的软件，可以直接把AirPoc当做包来调用，如果其他软件，AirPoc可以开放一个RPC接口提供使用，如果不想要Python的环境，也可以通过pyinstaller之类的工具打包，我们的设计原则是尽量不依赖其他第三方库，所以也会避免很多奇奇怪怪的问题。

想要实现验证速度与验证准确率极高，我们要做好多线程或协程的并发模型，这里我们会在后面在详细叙述。

最后，"我也不知道什么好，总之你跑起来能出东西就行！"，如果上面的事情我们都做好了，这个应该就是水到渠成的了~

## AirPoc的框架

![
](https://images.seebug.org/content/images/2019/05/9bb3236b-483e-4a63-af3c-c39d0940d0a8.jpeg-w331s)

在完成这个"宏伟计划"之前，我们也需要设计一下整体的代码框架。作为一名代码洁癖患者，一个良好的代码结构，是万里长征的第一步。我们建立如下的目录结构，env是虚拟环境，建立两个目录`lib`、`pocs`，`lib`用于存储之后的相关核心文件，`pocs`用于存储poc文件，和一个文件`main.py`用作初始入口。

![
](https://images.seebug.org/content/images/2019/05/9c0da7f1-f80e-4f31-9875-60e8f4e46fb5.png-w331s)

就像盖大楼需要打好地基，接下来完成基础框架，我们可以先不用写具体的功能，但是了解作为"地基"的函数的意义。如下，在`main.py`文件中如下代码，一个初始的框架就完成了。

    
    
    import os
    import time
    
    def banner():
        msg = '''
             ___   _   _____    _____   _____   _____  
        /   | | | |  _  \  |  _  \ /  _  \ /  ___| 
       / /| | | | | |_| |  | |_| | | | | | | |     
      / / | | | | |  _  /  |  ___/ | | | | | |     
     / /  | | | | | | \ \  | |     | |_| | | |___  
    /_/   |_| |_| |_|  \_\ |_|     \_____/ \_____|   {}
        '''.format(version)
        print(msg)
    
    
    def init(config: dict):
        print("[*] target:{}".format(config["url"]))
    
    
    def end():
        print("[*] shutting down at {0}".format(time.strftime("%X")))
    
    
    def start():
        pass
    
    
    def main():
        banner()
        config = {
            "url": "https://www.seebug.org/"
        }
        init(config)
        start()
        end()
    
    
    if __name__ == '__main__':
        version = "v0.00000001"
        main()

![image-20190429110505553](https://images.seebug.org/content/images/2019/05/06/1557118880000-image-20190429110505553.png-w331s)

但是，正如你所见，版本号和我的比特币钱包的数字竟然差不多，我们还要给它加些料。

### 单例模式

在我们软件的初始化的工程中，我们需要得到很多环境相关的信息。比如当前执行的路径是哪？poc目录在哪？我们输出结果文件输出到哪个路径等等。

它们有一个共同的特定是，它们只需要加载一次，在后面使用中直接拿来用就行了。这种模式在软件设计模式中有一个单独的名词，"单例模式"。

幸运的是python的模块就是天然的单例模式，因为模块在第一次导入时，会生成 `.pyc` 文件，当第二次导入时，就会直接加载 `.pyc`
文件，而不会再次执行模块代码。因此，我们只需把相关的函数和数据定义在一个模块中，就可以获得一个单例对象了。

我们在`lib`目录里面新建一个`data.py`用于存储这些信息。同时将版本信息也放到这里来。

    
    
    import os
    
    PATHS_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../")
    PATHS_POCS = os.path.join(PATHS_ROOT, "pocs")
    PATHS_OUTPUT = os.path.join(PATHS_ROOT, "output")
    VERSION = "v0.0000001"

为了更好的来表示这些常量，我们用PEP8标准里的规范，统一约定用大写和下划线来表示常量。为了说明与之前的区别，我们象征性的将VERSION减一个0，来表达我们的比特币又增长了10倍。

### 动态加载

在解决完我们相关的环境问题后，我们在看看如何动态加载模块。在具体细节里我们说过，我们期望PoC能够从本地或者远程网站(如GitHub)上加载。

这里又得分成两种情况，如果是通过文件路径加载动态加载的模块，可以直接用`__import__()`来加载，但是如果要远程加载，可能就又会复杂一点，根据python的相关文档，我们要自己实现"查找器"与"加载器"
<https://docs.python.org/zh-cn/3/reference/import.html>。

当然，你也可以从远程保存到本地后，按照本地加载模式进行加载。但是Pocsuite已经有完整的加载器代码了，我们可以直接拿来用。

新建`lib/loader.py`文件

    
    
    import hashlib
    import importlib
    from importlib.abc import Loader
    
    
    def get_md5(value):
        if isinstance(value, str):
            value = value.encode(encoding='UTF-8')
        return hashlib.md5(value).hexdigest()
    
    
    def load_string_to_module(code_string, fullname=None):
        try:
            module_name = 'pocs_{0}'.format(get_md5(code_string)) if fullname is None else fullname
            file_path = 'airpoc://{0}'.format(module_name)
            poc_loader = PocLoader(module_name, file_path)
            poc_loader.set_data(code_string)
            spec = importlib.util.spec_from_file_location(module_name, file_path, loader=poc_loader)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    
        except ImportError:
            error_msg = "load module '{0}' failed!".format(fullname)
            print(error_msg)
            raise
    
    
    class PocLoader(Loader):
        def __init__(self, fullname, path):
            self.fullname = fullname
            self.path = path
            self.data = None
    
        def set_data(self, data):
            self.data = data
    
        def get_filename(self, fullname):
            return self.path
    
        def get_data(self, filename):
            if filename.startswith('airpoc://') and self.data:
                data = self.data
            else:
                with open(filename, encoding='utf-8') as f:
                    data = f.read()
            return data
    
        def exec_module(self, module):
            filename = self.get_filename(self.fullname)
            poc_code = self.get_data(filename)
            obj = compile(poc_code, filename, 'exec', dont_inherit=True, optimize=-1)
            exec(obj, module.__dict__)

具体如何实现的我们可以不用关心，我们只需要知道，其中我们可以用`load_string_to_module`来从源码中加载模块了。如果你有兴趣了解具体的实现，可以参考上面的python官方文档。

## 规则的制定

从文件或者远程加载好模块后，就可以准备运行的相关事宜了。我们需要对PoC做一个规则的统一约定，让程序更好的调用它们。

你可以将规则定义的详细，也可以一切从简，主要是看使用场景。而前面也提到，为了保护"安全联盟"的安全问题，所以我们需要PoC更够比较简单的快速编写。

同时我们还需要考虑如果PoC需要多个参数如何处理？笔者的规则是这样定义的。

    
    
    def verify(arg, **kwargs):
        result = {}
        if requests.get(arg).status_code == 200:
            result = {
            "name":"漏洞名称",
            "url":arg
          }
        return result

在PoC文件中定义一个`verify`函数用作验证使用，arg作为普通的参数传递，当需要传递较多的参数时，从kwargs中接收。在PoC验证成功后，也只需要返回一个字典即可，如果验证失败，返回`False`或`None`即可。字典内容由PoC编写者制定，给予编写者最大的灵活空间。

但是注意！PoC的质量就需要依靠编写者的维护。

## V0.01

我们最终要实现的目标是，设置好目标，程序自动加载指定的一个或多个PoC或全部的PoC，逐个检测目标。剩下的部分就是怎样将这些功能串联在一起了。

前面我们已经实现了AirPoc的基础框架，现在只需要在其基础上具体实现功能即可。

为了测试的方便，我们先在`pocs`目录下按照之前定义的规则建立两个简陋的PoC。

![image-20190429164121695](https://images.seebug.org/content/images/2019/05/06/1557118880000-image-20190429164121695.png-w331s)

![image-20190429164143909](https://images.seebug.org/content/images/2019/05/06/1557118880000-image-20190429164143909.png-w331s)

现在，`main.py`中的代码如下

    
    
    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-    # @Time    : 2019/4/25 3:13 PM
    # @Author  : w7ay
    # @File    : main.py
    import os
    import time
    from lib.data import VERSION, PATHS_POCS, POCS
    from lib.loader import load_string_to_module
    
    
    def banner():
        msg = '''
         ___   _   _____    _____   _____   _____  
        /   | | | |  _  \  |  _  \ /  _  \ /  ___| 
       / /| | | | | |_| |  | |_| | | | | | | |     
      / / | | | | |  _  /  |  ___/ | | | | | |     
     / /  | | | | | | \ \  | |     | |_| | | |___  
    /_/   |_| |_| |_|  \_\ |_|     \_____/ \_____|   {}
        '''.format(VERSION)
        print(msg)
    
    
    def init(config: dict):
        print("[*] target:{}".format(config["url"]))
    
        # 加载poc，首先遍历出路径
        _pocs = []
        for root, dirs, files in os.walk(PATHS_POCS):
            files = filter(lambda x: not x.startswith("__") and x.endswith(".py") and x not in config.get("poc", []),
                           files)  # 过滤掉__init__.py文件以及指定poc文件
            _pocs.extend(map(lambda x: os.path.join(root, x), files))
    
        # 根据路径加载PoC
        for poc in _pocs:
            with open(poc, 'r') as f:
                model = load_string_to_module(f.read())
                POCS.append(model)
    
    
    def end():
        print("[*] shutting down at {0}".format(time.strftime("%X")))
    
    
    def start(config: dict):
        url_list = config.get("url", [])
        # 循环url_list与pocs，逐一对应执行。
        for i in url_list:
            for poc in POCS:
                try:
                    ret = poc.verify(i)
                except Exception as e:
                    ret = None
                    print(e)
                if ret:
                    print(ret)
    
    
    def main():
        banner()
        config = {
            "url": ["https://www.seebug.org/", "https://paper.seebug.org/"],
            "poc": []
        }
        init(config)
        start(config)
        end()
    
    
    if __name__ == '__main__':
        main()

我们的版本也来到了0.01，它已经是一个"成熟的”能自己跑PoC的框架了。

![image-20190429172118745](https://images.seebug.org/content/images/2019/05/06/1557118880000-image-20190429172118745.png-w331s)

## 多线程模型

为了让我们的框架运行得更快一点，我们使用多线程来处理每个PoC，因为我们处理的任务大多是I/O密集型任务，所以我们也不用太纠结python是不是伪线程这个问题。

多线程模型中最简单的一种是生产者/消费者的模型，启动多个线程来共同消费一个队列就行了。新建`lib/threads.py`

    
    
    import threading
    import time
    
    
    def exception_handled_function(thread_function, args=()):
        try:
            thread_function(*args)
        except KeyboardInterrupt:
            raise
        except Exception as ex:
            print("thread {0}: {1}".format(threading.currentThread().getName(), str(ex)))
    
    
    def run_threads(num_threads, thread_function, args: tuple = ()):
        threads = []
    
        # 启动多个线程
        for num_threads in range(num_threads):
            thread = threading.Thread(target=exception_handled_function, name=str(num_threads),
                                      args=(thread_function, args))
            thread.setDaemon(True)
            try:
                thread.start()
            except Exception as ex:
                err_msg = "error occurred while starting new thread ('{0}')".format(str(ex))
                print(err_msg)
                break
    
            threads.append(thread)
    
        # 等待所有线程完毕
        alive = True
        while alive:
            alive = False
            for thread in threads:
                if thread.isAlive():
                    alive = True
                    time.sleep(0.1)

值得注意的一点是，我们并没有使用Python线程中推荐的`join()`来阻塞线程，因为使用`join()`的话，python将无法响应用户输入的消息了，会导致Ctrl+C退出时没有任何响应，所以以while循环的方式来阻塞线程。

接着将主程序改造成多线程的模式，将原`start()`中的"消费者"提取出来，单独用作一个函数，用队列接收数据即可。如下

    
    
    def worker():
        if not WORKER.empty():
            arg, poc = WORKER.get()
            try:
                ret = poc.verify(arg)
            except Exception as e:
                ret = None
                print(e)
            if ret:
                print(ret)
    
    
    def start(config: dict):
        url_list = config.get("url", [])
    
        # 生产
        for arg in url_list:
            for poc in POCS:
                WORKER.put((arg, poc))
    
        # 消费
        run_threads(10, worker)

另外，线程数量是我们可配置的，我们将它改成从配置中读取。

    
    
    run_threads(config.get("thread_num", 10), worker)

再次运行，会发现比以前快很多！

![image-20190430102952036](https://images.seebug.org/content/images/2019/05/06/1557118880000-image-20190430102952036.png-w331s)

## 统一网络请求

这是我们整个框架的最后一个部分，如何来统一网络请求。有时我们需要让我们的PoC框架发出的网络请求中统一一下代理，UA头等等的设置，这需要我们框架进行统一的处理。在实现我们的目的之前，我们还需要在框架里做一个约定，约定我们的网络请求都需要统一使用`requests`来进行发包。开始时我们说到，我们会尽量不使用第三方模块，但是`requests`模块实在太好用了，我们将它排除在外...

Python语言动态的机制，我们可以很容易在使用一个函数之前Hook它，将它原始的方法重定向到我们自定义的方法中，这是我们能够统一网络请求的一个前提。

    
    
    def hello(arg):
        return "hello " + arg
    
    
    def hook(arg):
        arg = arg.upper()
        return "hello " + arg
    
    
    hello = hook
    
    print(hello("aa"))

![image-20190430112557108](https://images.seebug.org/content/images/2019/05/06/1557118880000-image-20190430112557108.png-w331s)

通过hook一个函数来达到我们自己的目的。

像sqlmap这类工具，基于python内置的`urllib`模块，但是有大量的代码都在处理在了网络请求方面，甚至为了处理`chunked`发包的问题，hook重写了更底层的`httplib`库。

pocsuite为了统一调度网络请求，hook了`requests`模块的相关方法。我们可以具体参考其中的代码。

`pocsuite3/lib/request/patch/__init__.py`代码很清晰的说明了hook的函数

    
    
    from .remove_ssl_verify import remove_ssl_verify
    from .remove_warnings import disable_warnings
    from .hook_request import patch_session
    from .add_httpraw import patch_addraw
    from .hook_request_redirect import patch_redirect
    
    def patch_all():
        disable_warnings() # 禁用了warning提示
        remove_ssl_verify() # 禁用ssl验证
        patch_session() # hook seesion函数
        patch_addraw() # 添加raw原生发包支持
        patch_redirect() # hook 重定向函数

如果你看过requests的源码，会知道这里面的重点是看它如何hook seesion函数的。

`pocsuite3/lib/request/patch/hook_request.py`

    
    
    from pocsuite3.lib.core.data import conf
    from requests.models import Request
    from requests.sessions import Session
    from requests.sessions import merge_setting, merge_cookies
    from requests.cookies import RequestsCookieJar
    from requests.utils import get_encodings_from_content
    
    
    def session_request(self, method, url,
                        params=None, data=None, headers=None, cookies=None, files=None, auth=None,
                        timeout=conf.timeout if 'timeout' in conf else None,
                        allow_redirects=True, proxies=None, hooks=None, stream=None, verify=False, cert=None, json=None):
        # Create the Request
        merged_cookies = merge_cookies(merge_cookies(RequestsCookieJar(), self.cookies),
                                       cookies or (conf.cookie if 'cookie' in conf else None))
    
        req = Request(
            method=method.upper(),
            url=url,
            headers=merge_setting(headers, conf.http_headers if 'http_headers' in conf else {}),
            files=files,
            data=data or {},
            json=json,
            params=params or {},
            auth=auth,
            cookies=merged_cookies,
            hooks=hooks,
        )
        prep = self.prepare_request(req)
    
        proxies = proxies or (conf.proxies if 'proxies' in conf else {})
    
        settings = self.merge_environment_settings(
            prep.url, proxies, stream, verify, cert
        )
    
        # Send the request.
        send_kwargs = {
            'timeout': timeout,
            'allow_redirects': allow_redirects,
        }
        send_kwargs.update(settings)
        resp = self.send(prep, **send_kwargs)
    
        if resp.encoding == 'ISO-8859-1':
            encodings = get_encodings_from_content(resp.text)
            if encodings:
                encoding = encodings[0]
            else:
                encoding = resp.apparent_encoding
    
            resp.encoding = encoding
    
        return resp
    
    
    def patch_session():
        Session.request = session_request

它重写了`session_request`函数的方法，让其中可以自定义我们自定义的文件头等信息。上述代码可能需要你看过requests才会对他有所理解，不过没关系，我们还是以拿来主义的精神直接用即可。

为了达到此目的以及更好的优化框架结构，我们还需要做一些小调整。

新建`lib/requests.py`

    
    
    from lib.data import CONF
    from requests.models import Request
    from requests.sessions import Session
    from requests.sessions import merge_setting, merge_cookies
    from requests.cookies import RequestsCookieJar
    from requests.utils import get_encodings_from_content
    
    
    def session_request(self, method, url,
                        params=None, data=None, headers=None, cookies=None, files=None, auth=None,
                        timeout=None,
                        allow_redirects=True, proxies=None, hooks=None, stream=None, verify=False, cert=None, json=None):
        # Create the Request.
        conf = CONF.get("requests", {})
        if timeout is None and "timeout" in conf:
            timeout = conf["timeout"]
        merged_cookies = merge_cookies(merge_cookies(RequestsCookieJar(), self.cookies),
                                       cookies or (conf.cookie if 'cookie' in conf else None))
    
        req = Request(
            method=method.upper(),
            url=url,
            headers=merge_setting(headers, conf["headers"] if 'headers' in conf else {}),
            files=files,
            data=data or {},
            json=json,
            params=params or {},
            auth=auth,
            cookies=merged_cookies,
            hooks=hooks,
        )
        prep = self.prepare_request(req)
    
        proxies = proxies or (conf["proxies"] if 'proxies' in conf else {})
    
        settings = self.merge_environment_settings(
            prep.url, proxies, stream, verify, cert
        )
    
        # Send the request.
        send_kwargs = {
            'timeout': timeout,
            'allow_redirects': allow_redirects,
        }
        send_kwargs.update(settings)
        resp = self.send(prep, **send_kwargs)
    
        if resp.encoding == 'ISO-8859-1':
            encodings = get_encodings_from_content(resp.text)
            if encodings:
                encoding = encodings[0]
            else:
                encoding = resp.apparent_encoding
    
            resp.encoding = encoding
    
        return resp
    
    
    def patch_session():
        Session.request = session_request

同时在config中预留requests的接口

![image-20190430115617047](https://images.seebug.org/content/images/2019/05/06/1557118880000-image-20190430115617047.png-w331s)

以及init的时候执行我们的hook。

![image-20190430115652364](https://images.seebug.org/content/images/2019/05/06/1557118880000-image-20190430115652364.png-w331s)

我们新编写一个PoC，用这个网站测试一下 最后的效果 <http://www.httpbin.org/get>

`pocs/poc.py`

    
    
    import requests
    
    
    def verify(arg, **kwargs):
        r = requests.get(arg)
        if r.status_code == 200:
            return {"url": arg, "text": r.text}

![image-20190430130417913](https://images.seebug.org/content/images/2019/05/06/1557118880000-image-20190430130417913.png-w331s)

效果很好，但是如果加上https的网站，就有一个警告信息。

![image-20190430130730241](https://images.seebug.org/content/images/2019/05/06/1557118880000-image-20190430130730241.png-w331s)

同样参考Pocsuite的方法禁用掉warning信息

    
    
    from urllib3 import disable_warnings
    disable_warnings()

最后有仪式感的将版本号变更为`0.1`，AirPoc的框架部分大体完成了。

## 最后

AirPoc的很多结构思想都来源于Pocsuite，如果直接阅读Pocsuite，也许能收获很多东西。目前AirPoc
v0.1基础框架已经差不多完成了，已经可以从本地加载一个或多个PoC，进行批量测试。后面我们再尝试些更好玩的，如何验证无回显的情况，如何生成shellcode，以及如何操作回连的shell，敬请期待下节《功能篇》~。

AirPoc下载：<https://images.seebug.org/archive/airpoc.zip>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/913/>

