> 渗透测试辅助工具分享

# Burp插件

### Trubo intruder

 **原理**

Turbo Intruder 使用自定义的 HTTP 栈来和服务器进行通信。

首先它会使 Connection: keepalive 头发起 HTTP 请求，如果是使用默认的 Connection: close
头，那么每次和服务器建立 HTTP 请求时都要重新建立一条 TCP 连接，这样比较浪费时间。

Connection: keepalive 头可以复用同一条 TCP 连接来发送多个 HTTP 请求， 这样就可以节省重复建立 TCP 连接的时间。
从下图可以看出，使用 Connection: keepalive 头后速度是原来的 400% 。

另外， 它还使用了 HTTP Pipelining (HTTP 管道)的方式来发送 HTTP 请求，这种方式会一次性发送几十个 HTTP 请求到服务器，
然后再一次性读取几十个请求响应。通过 HTTP 管道的方式，速度是一开始的 6000% ！

 **安装方式**

Burp-Extendee-BApp Store

 **使用方式**

![image_6tLYD-9hLr.png](https://image.3001.net/images/20220717/1658044557_62d3c08de56c9149e5463.png!small)

### 爆破脚本

#### 基础爆破脚本

    
    
    def queueRequests(target, wordlists):
        engine = RequestEngine(endpoint=target.endpoint,
                               concurrentConnections=5,
                               requestsPerConnection=100,
                               pipeline=False
                               )
    
        for word in open('D:/Illicit/Dictionary/weekness.txt'):
            engine.queue(target.req, word.rstrip())
    
    
    def handleResponse(req, interesting):
        # currently available attributes are req.status, req.wordcount, req.length and req.response
        if req.status != 404:
            table.add(req)
    

在需要爆破的地方标记为%s，修改脚本中的字典地址

注意事项：路径需要采用linux方式的路径，且需要英文目录下

![image_ZYxwdcLe6X.png](https://image.3001.net/images/20220717/1658044596_62d3c0b47e195df10c9e7.png!small)

![image_h4xIy-wvzB.png](https://image.3001.net/images/20220717/1658044613_62d3c0c57af1bbecc87d4.png!small)

#### 密码/用户名/双重爆破脚本

    
    
    from urllib import quote
    
    #爆破密码使用此模块
    #def password_brute(target,engine):
    #  for word in open('D:/Illicit/Dictionary/weekness.txt'):#在此填入密码字典
    #         engine.queue(target.req, quote(word.rstrip()))
    
    #爆破用户名使用此模块
    #def user_brute(target,engine):
    #  for word in open('D:/Illicit/Dictionary/user.txt'):#在此填入用户名字典
    #         engine.queue(target.req, quote(word.rstrip()))
    
    #同时爆破用户名密码，使用此模块，注意用户名的数量，不要太多
    def user_password_brute(target, engine):
      for password in open('D:/Illicit/Dictionary/weekness.txt'):#在此填入密码字典
        for user in open('D:/Illicit/Dictionary/user.txt'):#在此填入用户名字典
                engine.queue(target.req,[quote(user.rstrip()),quote(password.rstrip())])
    
    def queueRequests(target, wordlists):
        engine = RequestEngine(endpoint=target.endpoint,
                concurrentConnections=30,
                requestsPerConnection=100,
                pipeline=False#True启动管道模式,进一步加速爆破速度
                )
        #user_brute(target,engine)#爆破用户名注释26、27行
        #password_brute(target,engine)#爆破密码注释25、27行
        user_password_brute(target,engine)#爆破用户名注释25、26行
    
    def handleResponse(req, interesting):
    # currently available attributes are req.status, req.wordcount, req.length and req.response
        if req.status == 302:
          table.add(req)
    

备份

    
    
    from urllib import quote
    
    #爆破密码使用此模块
    def password_brute(target,engine):
       for word in open('D:/Illicit/Dictionary/weekness.txt'):#在此填入密码字典
             engine.queue(target.req, quote(word.rstrip()))
    
    #爆破用户名使用此模块
    # def user_brute(target,engine):
    #   for word in open('D:/Illicit/Dictionary/user.txt'):#在此填入用户名字典
    #         engine.queue(target.req, quote(word.rstrip()))
    
    #同时爆破用户名密码，使用此模块，注意用户名的数量，不要太多
    #def user_password_brute(target, engine):
    #  for password in open('D:/Illicit/Dictionary/weekness.txt'):#在此填入密码字典
    #    for user in open('D:/Illicit/Dictionary/user.txt'):#在此填入用户名字典
    #            engine.queue(target.req,[quote(user.rstrip()),quote(password.rstrip())])
    
    def queueRequests(target, wordlists):
        engine = RequestEngine(endpoint=target.endpoint,
                concurrentConnections=30,
                requestsPerConnection=100,
                pipeline=False#True启动管道模式,进一步加速爆破速度
                )
        #user_brute(target,engine)
        password_brute(target,engine)
        #user_password_brute(target,engine)
    
    def handleResponse(req, interesting):
    # currently available attributes are req.status, req.wordcount, req.length and req.response
        if req.status == 302:
          table.add(req)
    

#### 目录爆破脚本

    
    
    def mult_host_dir_brute():
        req = '''GET /%s HTTP/1.1
    Host: %s
    Connection: keep-alive
    
    '''
        engines = {}
        for url in open('D:/Illicit/Dictionary/url.txt'):#在此填入url列表
            url = url.rstrip()
            engine = RequestEngine(endpoint=url, 
                concurrentConnections=5,
                requestsPerConnection=100,
                pipeline=True)#True启动管道模式,进一步加速爆破速度
            engines[url] = engine
    
        for word in open('D:/Illicit/Dictionary/spring content.txt'):#在此填入url目录字典
            word = word.rstrip()
        for (url, engine) in engines.items():
                domain = url.split('/')[2]
                engine.queue(req, [word, domain])
    
    def queueRequests(target, wordlists):
        mult_host_dir_brute()
    
    def handleResponse(req, interesting):
    # currently available attributes are req.status, req.wordcount, req.length and req.response
      if req.status != 404:
           table.add(req)
    

### chunked-coding-converter

 **安装方式**

项目地址：<https://github.com/c0ny1/chunked-coding-converter/releases/tag/0.4.0>

 **使用方式**

![image_jVVh5NHRBh.png](https://image.3001.net/images/20220717/1658044672_62d3c1004694fabad978e.png!small)

 **实战演示**

文件上传接口

![image_4_BZUPaVlJT8.png](https://image.3001.net/images/20220717/1658044687_62d3c10f559c30db6f9ac.png!small)

直接上传PHP文件，发现可以正常上传，并回显图片地址

![image_5_Jz3yn8EQ1C.png](https://image.3001.net/images/20220717/1658044714_62d3c12a8b354aad346ab.png!small)

尝试在图片中插入一句话木马，发现系统对文件内容存在检查，存在waf，数据包被直接拦截

![image_6_3hrGkV_mcs.png](https://image.3001.net/images/20220717/1658044725_62d3c13543e2aa455b8fc.png!small)

由于存在waf，使用分块上传的方式绕过

采用此插件进行分块绕过

![image_7_nFmdjGYjn4.png](https://image.3001.net/images/20220717/1658044736_62d3c140bab0b9959e47f.png!small)

### Unicode Auto Decode

 **安装方式**

<https://github.com/KagamigawaMeguri/burp-UnicodeAutoDecode>

 **使用方式**

自动识别uncode编码并转化，HTTP history下的报文经常不能转化

效果如下：转化后会出现—u—xx—u—

![image_5_mQgIGCsDQo.png](https://image.3001.net/images/20220717/1658044749_62d3c14d6dbb8ff2c7040.png!small)

### Burp Collaborator

 **使用方式**

打开 Collaborator 客户端

![image_faAy8V9_Ab.png](https://image.3001.net/images/20220717/1658044760_62d3c158cc8187e82aec0.png!small)

使用 Client

![image_Er0ggLMmI6.png](https://image.3001.net/images/20220717/1658044788_62d3c174864ee93cdfd10.png!small)

注：collaborator客户端在1.7 以后自带，老版本可以通过插件的方式来实现

测试使用

![image_VRq0FiMT5m.png](https://image.3001.net/images/20220717/1658044802_62d3c18210d4a7da890ed.png!small)

 **使用范围**

适用于带外攻击，简单的来说就是测试的过程中目标服务器和外部的服务器有了交互。

如图所示，就是该工具的实际原理：

![aHR0cHM6Ly9ibG9nLTEyNTE4MTYwOTguY29zLmFwLWJlaWppbm.png](https://image.3001.net/images/20220717/1658044824_62d3c198ac67106236c78.png!small)

常规测试中的一些盲打问题，当我们的XSS、SSRF、XXE、命令注入不能看到一些回显信息，无法判断是否存在漏洞时，就可以使用collaborator，在payload中插入该分配的域名进行测试。

还可以通过collaborator来判断目标是否出网，这个工具可以同时监听到HTTP+DNS的请求，并查看post请求包和cookie等，相当于httpslog和dnslog的合体升级版。

日常使用就和DNSlog一样，就不再追述了。

>
> 同时推荐一下下面的这个文章，《无回显条件下的命令执行判断和利用方式》写的很不错，推荐学习一下<https://mp.weixin.qq.com/s/rVOP6eHin6DLKIpvkqh6BA>

### Blaster

 **安装方式**

项目地址：<https://github.com/PoJun-Lab/blaster>

 **使用方式**

### js path

    
    
    userinput_jspath: '' # 用户名输入框js path
    passinput_jspath: '' # 密码输入框js path
    captchainput_jspath: '' # 验证码输入框js path
    captchaimg_jspath: '' # 验证码图片js path
    loginbutton_jspath: '' # 登录按钮 js path

可采用以下方式配置:

客户端配置中的jspath可在浏览器页面对应表单右键选择检查(Inspect)，并在检查中右键选中的表单标签，选择Copy>Copy JS
path即可复制jspath。  
![image](https://image.3001.net/images/20220726/1658820726_62df9876d2e56570cfcd3.png!small)  
![image](https://image.3001.net/images/20220726/1658820762_62df989a0331fc323c0f6.png!small)

 **loginreq_pattern**

抓包获取登录的地址

 **captchabreak_serverurl**

用于指定图片验证码服务，格式为 [http://user:pass@127.0.0.1:port/c](http://127.0.0.1/cb
"http://user:pass@127.0.0.1:port/c")

 **before_all_js_expr**

在开始填写账号密码之前执行的js表达式，如页面打开后有弹出层，可以将通过该参数关闭弹窗，不局限于弹出层一个场景。

示例场景：打开页面出现弹出层，需要关闭弹窗后输入账号密码

示例解决弹出层：判断某按钮（弹出层关闭按钮X）是否存在，如果存在则点击；找出关闭按钮的js path按照格式编写代码即可。

null != jspath && jspath.click() // js代码格式

表达式不限于一个，如有其他场景或多个弹出层，可通过 && 或 || 进行叠加

 **before_login_js_expr**

在点击登录之前执行的js表达式，如登录需要勾选阅读平台使用须知、 隐私政策单选表单等

示例场景：输入账号密码后需要选择阅读平台使用须知、 隐私政策等表单才可登录

示例解决表单勾选：判断某勾选框是否已经勾选如果未勾选则点击；找出表单勾选的js path按照格式编写代码即可。

!jspath.checked && jspath.click() // js代码格式

表达式不限于一个，如有其他场景或多个勾选，可通过 && 或 || 进行叠加

 **body_exclude_regex**

排除请求的正则，即只要命中其中任意一个正则的请求响应将被抛弃，即反向grep。

示例场景：登录后的响应页面长度较大，返回格式为HTML，其中有（账号不存在、密码错误、验证码错误、登录成功）等不同情况，由于响应长度较大我们无法轻易区分测试数据的真实响应情况。

示例解决响应长度较大问题：经过手工登录测试发现响应的HTML中出现这些关键信息（如账号不存在、密码错误、验证码错误），根据自己的需求，编写正则表达式，在发现响应中存在这些匹配内容时不输出到终端及结果文件中。

这里需要具备一些正则表达式的技能，如果使用者技能有些欠缺，可以直接使用关键信息进行排除，或是在交流群内寻求帮助。

body_exclude_regex:

'账号不存在'

'验证码错误'

该参数不限于一个表达式，使用者根据自己的需求来增删表达式即可。

 **使用范围**

 **无法使用**

其他类型的验证码，例如滑动验证码、点选验证码等

密码错误直接重定向或是采用alert的弹窗

 **使用复杂**

出现登录需要勾选阅读平台使用须知、 隐私政策单选表单等

设置：before_login_js_expr

打开页面出现弹出层，需要关闭弹窗后输入账号密码

设置：before_all_js_expr

