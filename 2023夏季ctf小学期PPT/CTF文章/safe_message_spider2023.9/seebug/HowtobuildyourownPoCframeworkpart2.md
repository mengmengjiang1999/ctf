**Author: w7ay@Knownsec 404 Team  
Chinese version: <https://paper.seebug.org/913/>  
Related reading: [How to build your own PoC framework - the use of
Pocsuite3](https://paper.seebug.org/905/ "How to build your own PoC framework
- the use of Pocsuite3")**

In this article, I want to use Poscuite to implement my own PoC framework.

First of all, let's take a nice name, such as Captain America, Thor, Ant-Man
or Thanos. If you like playing Dota, you can also call it Mountain King,
BladeMaster, Priess Of the moon.

I call it AirPoc because I'm lazy.

The next step is to design its function. We can assume that there exists a
"rabbit security alliance". We plan to develop a blockchain-based PoC
verification framework named as AirPoc, which is only responsible for the
websites within "rabbit security alliance".

When one AirPoc node checks out the vulnerability point, the URL and the PoC
is shared via block, and then verfied by other random nodes. If the
verification succeed, the "air currency" can be obtained, and the detected
website owner needs to pay "air currency" as compensation.

First just imagine what kind of PoC framework we need:

  1. Simple and cross-platform
  2. Can make more people contribute
  3. Easy to build into other software
  4. High verfication speed and accuracy
  5. I don't know what to include in the framework. But the first thing is to build a runable one!

Of course, I didn't add the blockchain, it's just a joke.

## Detail

We use python(3.7 the last version) as the programming language and decide not
to use third-party dependencies.

It is cool to make contribution to some open source projects like sqlmap,
Metasploit and Routersploit. So I decide to publish the AirPoc's PoC on Github
and then we can call the PoC via online API. That's cool!

It is also easier to integrate into other softwares. If it uses Python, you
can import AirPoC as a package. For other software, AirPoc designs the RPC
interface for them to call. Besides, if you don't have a Python environment,
you can also use`pyinstaller` to package it. Don't rely on other libraries is
our design principle, which will help to avoid many other problems.

To achieve high verification speed and high verification accuracy, we need to
build a concurrency model with multi-thread and coroutine, which I will
describe later.

## AirPoc's framework

![
](https://images.seebug.org/content/images/2019/05/9bb3236b-483e-4a63-af3c-c39d0940d0a8.jpeg-w331s)

Before we complete the plan, we also need to design code structure. As a
perfectionist programmer, the good code structure is the first step when
constructing a big project. We create the directory as following. , `env` is
the directory for managing packages in a virtual environment. `lib`is the
directory for storing related core files. `pocs` is the directory for storing
poc files, and a file `main .py` is used as the initial entry.

![
](https://images.seebug.org/content/images/2019/05/9c0da7f1-f80e-4f31-9875-60e8f4e46fb5.png-w331s)

As building depends on its foundations, the basic framework is the base for
our future work. We don't need to write the specific functions, but should
understand "foundation" function. In the `main.py` file, an initial framework
is completed.

    
    
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

![image-20190429110505553](https://images.seebug.org/content/images/2019/05/06/1557131388000-image-20190429110505553.png-w331s)

However, as you can see, the version number is as low as how much bitcoin in
my wallet, we need to add some material.

### Singleton

In the initialization stage of software engineering, we need to store a lot of
environment-related information. For example, what is the current execution
path, where is the PoC directory, where is the directory the output file
located and so on.

All those information has the same attribute. Those information should be
loaded once and then can be used directly without change. In the software
engineering, the "singleton" pattern, one pattern in software engineering,
fits that need very well.

Fortunately, the python module is a natural singleton, because when the code
is executed for the first time, it will generate the`.pyc` file for the future
use. Then the import of that module will use the previous file without extra
execution. Therefore, we only need to define related functions and data in a
module to get a singleton object.

We create a new `data.py` in the `lib` directory to store this information.
Also put the version information here.

    
    
    import os
    
    PATHS_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../")
    PATHS_POCS = os.path.join(PATHS_ROOT, "pocs")
    PATHS_OUTPUT = os.path.join(PATHS_ROOT, "output")
    VERSION = "v0.0000001"

We use the PEP8 standard with uppercase and underscores to represent these
constants. To illustrate the difference from the previous one, we symbolically
reduce version number by a 0 to express our "bitcoin" and increased by 10
times.

### Dynamic module

After solving our delete related environmental problems, let's take a look at
how to dynamically load modules. As what we discuss before. we expect PoC to
be able to load from local or remote sites such as GitHub.

There are two cases here. If you load the module through the file path, you
can directly use `__import__ ()` to load. If you want to load remotely, it may
be more complicated. According to python related documents, we have to
implement the "Finder" and "Loader". <https://docs.python.org/en-us/3/reference/import.html>.

Of course, you can also use the local storage mode after saving from remote
websites. But we can use the loader code the PocSuite provided already.

Create a new `lib/loader.py` file

    
    
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

The detail of the implement is not what we should care about. We only need to
know that we can use `load_string_to_module` to load modules from the source
code. If you are interested in how that works, you can refer to the official
python documentation mentioned above.

## PoC's code format development

After loading the module, we can code for the operation. We need to set some
uniform convention for the PoC, thus the program can call them better.

The complexity of the PoC depends on the design structure we need, it can be
completed and detailed or as simple as possible.As mentioned earlier, in order
to protect the security of the "security alliance", we need PoC to be simpler
and faster to write.

At the same time, we also need to consider the case in which the PoC needs to
handle multiple parameters. My rules are defined as follows:

    
    
    def verify(arg, **kwargs):
        result = {}
        if requests.get(arg).status_code == 200:
            result = {
            "name":"vulnerability name",
            "url":arg
          }
        return result

Define a `verify` function in the PoC file for validation, arg as a normal
parameter, and receive from kwargs when more parameters need to be passed.
After the PoC verification succeed, we return a dictionary, otherwise return
`False` or `None`. The content of the dictionary can be designed by the PoC
writer with the author maximum flexibility.

Attention please! The quality of a PoC relies on the maintenance of the
author.

## V0.01

The ultimate goal we have to achieve is to set the target, and then the
program automatically loads the specified one or more PoCs or all PoCs, and
detects the targets one by one. The rest of our work is integrating these
functions together. We have already implemented the basic framework of AirPoc,
and now we only need to implement the functions on top of that.For the
convenience of testing, we first create two simple PoCs in the `pocs`
directory according to the previously defined rules.

![image-20190429164121695](https://images.seebug.org/content/images/2019/05/06/1557131388000-image-20190429164121695.png-w331s)

![image-20190429164143909](https://images.seebug.org/content/images/2019/05/06/1557131388000-image-20190429164143909.png-w331s)

Now,`main.py` code is

    
    
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
    
        # Load the poc, first traverse the path
        _pocs = []
        for root, dirs, files in os.walk(PATHS_POCS):
            files = filter(lambda x: not x.startswith("__") and x.endswith(".py") and x not in config.get("poc", []),
                           files)  # Filter out the __init__.py file and specify the poc file
            _pocs.extend(map(lambda x: os.path.join(root, x), files))
    
        # Load PoC according to the path
        for poc in _pocs:
            with open(poc, 'r') as f:
                model = load_string_to_module(f.read())
                POCS.append(model)
    
    
    def end():
        print("[*] shutting down at {0}".format(time.strftime("%X")))
    
    
    def start(config: dict):
        url_list = config.get("url", [])
        # The loop url_list and pocs are executed one by one.
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

Our version has also come to 0.01, it is already a "mature" framework which
can run PoC on its
own.![image-20190429172118745](https://images.seebug.org/content/images/2019/05/06/1557131388000-image-20190429172118745.png-w331s)

## Multi-threaded

In order to make our framework run faster, we use multithreading to handle
each PoC, because most of the tasks we deal with are I/O intensive tasks, so
we don't have to worry about whether Python is a pseudo-thread.

The simplest of the multithreaded models is the producer/consumer model, which
starts multiple threads to consume a queue together. Create a new
`lib/threads.py`

    
    
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
    
        # Start multiple threads
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
    
        # Waiting for all threads to finish
        alive = True
        while alive:
            alive = False
            for thread in threads:
                if thread.isAlive():
                    alive = True
                    time.sleep(0.1)

It's worth noting that we didn't use the `join()` recommended in the Python
thread to block the thread, because with `join()`, python will not be able to
respond to user-entered messages, causing Ctrl+C to exit. There is no
response, so the thread is blocked in a while loop.

Then the main program is transformed into a multi-threaded mode, and the
"consumer" in the original `start()` is extracted and used as a function
alone, and the data can be received by the queue. As follows:

    
    
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
    
        # producer
        for arg in url_list:
            for poc in POCS:
                WORKER.put((arg, poc))
    
        # comsumer
        run_threads(10, worker)

In addition, the number of threads is configurable and we change it to read
from the configuration.

    
    
    run_threads(config.get("thread_num", 10), worker)

Run it again and you will find it much faster than before!

![image-20190430102952036](https://images.seebug.org/content/images/2019/05/06/1557131388000-image-20190430102952036.png-w331s)

## Network request

This is the last part of our entire framework, how to unify network requests.
Sometimes we need to make the settings of the proxy, UA header, etc. in the
network request sent by our PoC framework, which requires our framework to
handle it uniformly. Before we can achieve our goal, we also need to make an
agreement in the framework, agree that our network requests need to use
`requests` to send packets. At the beginning we said that we will try not to
use third-party modules, but the `requests` module is so good that we exclude
it...

The dynamic mechanism of the Python language, we can easily hook it before
using a function, and redirect its original method to our custom method, which
is a prerequisite for us to unify the network request.

    
    
    def hello(arg):
        return "hello " + arg
    
    
    def hook(arg):
        arg = arg.upper()
        return "hello " + arg
    
    
    hello = hook
    
    print(hello("aa"))

![image-20190430112557108](https://images.seebug.org/content/images/2019/05/06/1557131389000-image-20190430112557108.png-w331s)

By hooking a function to achieve our own purpose.

Tools like sqlmap are based on Python's built-in `urllib` module, but a lot of
code is being processed in network requests, and even to handle the `chunked`
issue, hooks rewrite the lower-level `httplib` library.

In order to uniformly schedule network requests, pocsuite hooks the related
methods of the `requests` module. We can refer to the code in detail.

The `pocsuite3/lib/request/patch/__init__.py` code clearly illustrates the
hook function.

    
    
    from .remove_ssl_verify import remove_ssl_verify
    from .remove_warnings import disable_warnings
    from .hook_request import patch_session
    from .add_httpraw import patch_addraw
    from .hook_request_redirect import patch_redirect
    
    def patch_all():
        disable_warnings() 
        remove_ssl_verify()
        patch_session()
        patch_addraw()
        patch_redirect()

If you look at the source of the requests, you will know that the focus is on
how it hooks the seesion function.

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

It overrides the method of the `session_request` function, which allows you to
customize the information such as our custom headers. The above code may
require you to read the requests to understand him, but it doesn't matter, we
can use it directly in the spirit of takership.

In order to achieve this and better optimize the framework, we also need to
make some minor adjustments.

Create a new `lib/requests.py`

    
    
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

Also reserve the request interface in config

![image-20190430115617047](https://images.seebug.org/content/images/2019/05/06/1557131389000-image-20190430115617047.png-w331s)

And execute our hooks when init.

![image-20190430115652364](https://images.seebug.org/content/images/2019/05/06/1557131389000-image-20190430115652364.png-w331s)

Let's write a new PoC and use this site to test the final effect
<http://www.httpbin.org/get>

`pocs/poc.py`

    
    
    import requests
    
    
    def verify(arg, **kwargs):
        r = requests.get(arg)
        if r.status_code == 200:
            return {"url": arg, "text": r.text}

![image-20190430130417913](https://images.seebug.org/content/images/2019/05/06/1557131389000-image-20190430130417913.png-w331s)

The effect is very good, but if you add https website, there is a warning
message.

![image-20190430130730241](https://images.seebug.org/content/images/2019/05/06/1557131389000-image-20190430130730241.png-w331s)

Also refer to the Pocsuite method to disable the warning information.

    
    
    from urllib3 import disable_warnings
    disable_warnings()

Finally, change the version number to `0.1`, and the framework part of AirPoc
is generally completed.

## At last

Many of AirPoc's structural ideas are come from Pocsuite. If you read Pocsuite
directly, you may get a lot of things. At present, the AirPoc v0.1
infrastructure has been almost completed, and one or more PoCs can be loaded
locally for batch testing. Later, we are trying to play some more fun,eg: how
to verify the situation without echo, how to generate shellcode, and how to
operate the shell back, so stay tuned for the next section~zzzzz.

Download AirPoc: <https://images.seebug.org/archive/airpoc.zip>

## About Knownsec & 404 Team

Beijing Knownsec Information Technology Co., Ltd. was established by a group
of high-profile international security experts. It has over a hundred frontier
security talents nationwide as the core security research team to provide
long-term internationally advanced network security solutions for the
government and enterprises.

Knownsec's specialties include network attack and defense integrated
technologies and product R&D under new situations. It provides visualization
solutions that meet the world-class security technology standards and enhances
the security monitoring, alarm and defense abilities of customer networks with
its industry-leading capabilities in cloud computing and big data processing.
The company's technical strength is strongly recognized by the State Ministry
of Public Security, the Central Government Procurement Center, the Ministry of
Industry and Information Technology (MIIT), China National Vulnerability
Database of Information Security (CNNVD), the Central Bank, the Hong Kong
Jockey Club, Microsoft, Zhejiang Satellite TV and other well-known clients.

404 Team, the core security team of Knownsec, is dedicated to the research of
security vulnerability and offensive and defensive technology in the fields of
Web, IoT, industrial control, blockchain, etc. 404 team has submitted
vulnerability research to many well-known vendors such as Microsoft, Apple,
Adobe, Tencent, Alibaba, Baidu, etc. And has received a high reputation in the
industry.

The most well-known sharing of Knownsec 404 Team includes: [KCon Hacking
Conference](http://kcon.knownsec.com/ "KCon Hacking Conference"), [Seebug
Vulnerability Database](https://www.seebug.org/ "Seebug Vulnerability
Database") and [ZoomEye Cyberspace Search Engine](https://www.zoomeye.org/
"ZoomEye Cyberspace Search Engine").

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/914/>

