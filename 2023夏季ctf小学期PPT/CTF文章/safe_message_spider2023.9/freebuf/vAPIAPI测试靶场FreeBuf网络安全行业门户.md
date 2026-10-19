# vAPI

vAPI is Vulnerable Adversely Programmed Interface which is Self-Hostable API
that mimics OWASP API Top 10 scenarios through Exercises.

项目地址：https://github.com/roottusk/vapi

启动方式：`docker-compose up -d`

访问地址：http://IP/vpi/

漏洞参考：OWASP API Top 10（2019）

工具：

  * Postman

  * Burpsuite

  * XAMPP Server (Apache and MySQL)

如果在postman中测试，要将/vapi/postman中的配置文件导入到postman中，在环境配置文件中将host配置成自己靶机的ip地址，然后保存，保存所有，启用环境配置文件，方可使用。

## API1 - 失效的对象级授权

失效的对象级别授权指未对通过身份验证的用户实施恰当的访问控制。攻击者可以利用这些缺陷访问未经授权的功能或数据（直接的对象引用或限制的URL）。例如：
_访问其他用户的帐户_ 、查看敏感文件、修改其他用户的数据、更改访问权限等。

Broken Object Level Authorization:

You can register yourself as a User , Thats it ....or is there something more?

![image](https://image.3001.net/images/20220506/1651813586_6274acd2aea62f31cfbcd.png!small)

此时访问无Authorization-Token，所以返回500响应码；

接下来需要做的就是拿到一个合法token；

调用 _`API:Create User`_ ，拿到token；

![image](https://image.3001.net/images/20220506/1651813606_6274ace6f14cb696821af.png!small)

使用创建用户的token，再次调用 _`API:Get User`_ ；

![image](https://image.3001.net/images/20220506/1651813618_6274acf2a1a9a257c8ebd.png!small)

成功返回信息。

    
    
    {
      "id": 1,
      "username": "michaels",
      "name": "Michael Scott",
      "course": "flag{api1_d0cd9be2324cc237235b}"
    }
    

依次遍历id；

    
    
    {
      "id": 2,
      "username": "meredithp",
      "name": "Meredith Palmer",
      "course": "The Subtle art of not giving a F***"
    }
    
    
    
    {
      "id": 3,
      "username": "pambeese",
      "name": "Pam Beesly",
      "course": "Sketching for Dummies"
    }
    
    
    
    {
      "id": 4,
      "username": "jimhalp",
      "name": "Jim Halpert",
      "course": "Art of Pranks"
    }
    

此处漏洞属于一种横向越权漏洞。

## API2 - 失效的用户认证

API 通常不会正确验证用户身份。这个问题基本上围绕认证方面，如弱口令、默认口令、明文存储、弱加密、密码爆破、GET方式传输令牌和密码等。

Broken Authentication:

We don't seem to have credentials for this , How do we login? (There's
something in the Resources Folder given to you )

vAPI提供了一个包含用户名和密码的字典，`/vapi/Resources/API2_CredentialStuffing/creds.csv`；

使用postman+burpsuit进行爆破：

  1. 在设置中将postman代理挂给burpsuit；

  2. 抓包；

![image](https://image.3001.net/images/20220506/1651813635_6274ad03c71f8811a1107.png!small)

  3. 将包发给Intruder，选择Pitchforrk，进行爆破；

![image](https://image.3001.net/images/20220506/1651813645_6274ad0d17a43fdab2cfb.png!small)

  4. 将1000条邮箱和密码分别粘贴进对应载荷

![image](https://image.3001.net/images/20220506/1651813652_6274ad14ab94af36bdd9a.png!small)

![image](https://image.3001.net/images/20220506/1651813661_6274ad1d16470df270419.png!small)

注意：不能将payload中的特殊字符进行URL编码，否则，无法成功破解密码；

我还以为是我方法不对，使用Clusterbomb爆破了100w次，哈哈哈哈哈，搞笑了  
run!  
![image](https://image.3001.net/images/20220506/1651813668_6274ad24dea14715b5dc9.png!small)分别拿到token；

    
    
    HTTP/1.1 200 OK
    Host: 10.0.0.128
    Date: Sat, 26 Feb 2022 02:42:46 GMT
    Connection: close
    X-Powered-By: PHP/7.4.7
    Cache-Control: no-cache, private
    Date: Sat, 26 Feb 2022 02:42:46 GMT
    Content-Type: application/json
    
    {"success":"true","token":"1Nkoz6quzJiis1SEonJeSxwkXTzSzcULofbL9O7KPz6_sKGkUcQDzoNfI5aA"}
    
    
    
    HTTP/1.1 200 OK
    Host: 10.0.0.128
    Date: Sat, 26 Feb 2022 02:42:58 GMT
    Connection: close
    X-Powered-By: PHP/7.4.7
    Cache-Control: no-cache, private
    Date: Sat, 26 Feb 2022 02:42:58 GMT
    Content-Type: application/json
    
    {"success":"true","token":"sLqs17RjmdlWoBP2ONdAPP8WtIVNwlyz_qzLwhmJGboWD_asFICYggcE3bPi"}
    

  7. 把拿到token给 _API:Get Details_ ，拿到信息。

    
    
    [
      {
        "id": 1,
        "email": "savanna48@ortiz.com",
        "name": "Evelyn",
        "token": "Fp0r1mty_gxK9DRZ5IUw3sX2enQ6rau68M6YGyoqR3XoBG13wtSbvmdaK5CB",
        "address": "10th Downing",
        "city": "Mesport",
        "country": "USA"
      },
      {
        "id": 2,
        "email": "hauck.aletha@yahoo.com",
        "name": "Tara",
        "token": "1Nkoz6quzJiis1SEonJeSxwkXTzSzcULofbL9O7KPz6_sKGkUcQDzoNfI5aA",
        "address": "flag{api2_6bf2beda61e2a1ab2d0a}",
        "city": "Delhi",
        "country": "India"
      },
      {
        "id": 3,
        "email": "harber.leif@beatty.info",
        "name": "Joyce",
        "token": "sLqs17RjmdlWoBP2ONdAPP8WtIVNwlyz_qzLwhmJGboWD_asFICYggcE3bPi",
        "address": "San Jose",
        "city": "California",
        "country": "USA"
      }
    ]
    

## API3 - 过度的数据暴露

API 可能会返回大量不必要的数据作为响应，并在客户端对其进行过滤以仅显示所需的数据。攻击者可以通过使用 Burpsuite，并访问响应中返回的过多数据。

Excessive Data Exposure:

We have all been there , right? Giving away too much data and the Dev showing
it. Try the Android App in the Resources folder.

调用 _`API:Create User`_ ，创建一个测试用户；

![image](https://image.3001.net/images/20220506/1651813683_6274ad33a8bbc0448886a.png!small)

手机安装app后，启动app，按照格式要求填写url；

![image](https://image.3001.net/images/20220506/1651813694_6274ad3e17f358ac46256.png!small)

使用刚才建立的用户进行登录；

![image](https://image.3001.net/images/20220506/1651813722_6274ad5a76ad3ee3986df.png!small)

放行user login的请求包；

![image](https://image.3001.net/images/20220506/1651813735_6274ad676395fe5cd143d.png!small)

此时，回拦截到一个comment的请求包；

![image](https://image.3001.net/images/20220506/1651813744_6274ad702b8405d5c18ed.png!small)

放行comments包；

![image](https://image.3001.net/images/20220506/1651813753_6274ad79a2cd7075b212e.png!small)

得到过度的数据暴露内容；

    
    
    {
      "id":1,
      "postid":"1",
      "deviceid":"flag{api3_0bad677bfc504c75ff72}",
      "latitude":"45.5426274",
      "longitude":"-122.7944111",
      "commenttext":"THIS POST IS SH***Y",
      "username":"baduser007"
     }
    

![image](https://image.3001.net/images/20220506/1651813764_6274ad845a2477652bd1d.png!small)

手机前端不会显示暴露的信息，但在数据包中会有显示。

## API4 - 资源缺失 & 速率限制

大多数情况下，API 并对客户端/用户可以请求的资源大小或数量施加任何限制。攻击者可以利用此漏洞，通过过多的请求使服务器不堪重负，以执行拒绝服务 (DoS)
或绕过身份验证机制。同时还为诸如暴力破解之类的身份验证漏洞敞开了大门。

 _此题参考资源竞争漏洞。_  
  
Lack of Resources & Rate Limiting:

We believe OTPs are a great way of authenticating users and secure too if
implemented correctly!

调用 _`API:Mobile Login`_ ，确定验证码为4位数字；

![image](https://image.3001.net/images/20220506/1651813781_6274ad95e886b1da302e7.png!small)

调用 _`API:Verify OPT`_ ，抓包进行爆破；

![image](https://image.3001.net/images/20220506/1651814507_6274b06b74df71a33ea6f.png!small)

设置payload；

![image](https://image.3001.net/images/20220506/1651814516_6274b07453e40d78ab17c.png!small)

进行爆破；

![image](https://image.3001.net/images/20220506/1651814529_6274b08101e8547eeace0.png!small)

验证码为1872，使用该码进行登录；

![image](https://image.3001.net/images/20220506/1651814540_6274b08c2348fc07254d1.png!small)

此时，等到一个返回值；

    
    
    {
      "success":"true",
      "key":"FZvjaFlMgUfnpFJDhKx-92xeXx_sCr7Y"
    }
    

这个key就是 _`API:Get Details`_ 的token；

![image](https://image.3001.net/images/20220506/1651814550_6274b0960bd3565ad1640.png!small)

拿到flag。

    
    
    [
      {
        "id": 1,
        "firstname": "john",
        "lastname": "flag{api4_ce696239323ea5b2d015}"
      }
    ]
    

## API5 - 失效的功能级授权

Broken Function Level Authorization:

You can register yourself as a User. Thats it or is there something more? (I
heard admin logins often but uses different route)

有些时候，普通用户可以调整请求的方法，检索到他们不应该检索到的信息，或执行他不应该访问的操作。

此题参考垂直越权漏洞。

调用 _`API:Creat User`_ ，创建一个用户，并拿到一个token；

![image](https://image.3001.net/images/20220506/1651814565_6274b0a5f0f50fcce4543.png!small)

使用这个token可以查看自己的用户信息；

![image](https://image.3001.net/images/20220506/1651814575_6274b0af5ad3fd2338b31.png!small)

但无法查看id为1的用户信息；

![image](https://image.3001.net/images/20220506/1651814588_6274b0bc4613aa2dbfd88.png!small)

调整请求api；

此处的api请求，我也没想明白是怎么构造出来的，这个api应该是一个普通用户正常使用不到的api，可能就是尝试构造出来的；

![image](https://image.3001.net/images/20220506/1651814597_6274b0c5719b9fa977b8c.png!small)

得到flag。

    
    
    {
      "id": 1,
      "username": "admin",
      "name": "Admin User",
      "address": "flag{api5_76dd990a97ff1563ae76}",
      "mobileno": "8080808080"
    },
    

## API6 - 批量分配

有时候，API 会信任从客户端接收到的用户输入，并在不经过过滤的情况下，将其直接保存在数据库中。为了获得对受限功能的未经授权的访问，攻击者可以通过 API
文档、有根据的猜测或 HTTP 回复识别额外的对象，并将它们包含在请求中。例如，攻击者可能会将 &admin=true
参数附加到用户的注册并获得管理员权限。

Mass Assignment:

Welcome to our store, We will give you credits if you behave nicely. Our
credit management is super secure.

听说表现好会有学分，嘿嘿

调用 _`API:Creat User`_ 创建一个用户；

![image](https://image.3001.net/images/20220506/1651814612_6274b0d467684498e73e8.png!small)

调用 _`API:Get User`_ 查看一下用户信息，发现没有学分；

![image](https://image.3001.net/images/20220506/1651814622_6274b0de34a7a1448d48b.png!small)

没有学分，那就创造学分，先给自己来个1w分；

![image](https://image.3001.net/images/20220506/1651814631_6274b0e789de500bce78f.png!small)

欸，这不就有了；

![image](https://image.3001.net/images/20220506/1651814644_6274b0f477bb19885ce2d.png!small)

拿到flag。

    
    
    {
      "id": 5,
      "name": "TEST4",
      "username": "test4",
      "credit": "10000",
      "flag": "flag{api6_afb969db8b6e272694b4}"
    }
    

## API7 - 安全性配置不当

安全配置不当包括默认或不完整的配置、配置不当的HTTP头、不必要的HTTP请求方法、跨源资源共享(CORS)配置不当、以及包含敏感数据的详细的报错消息等问题。攻击者可能会利用这些不当的配置来获得未经授权访问或破坏安全机制。

此题涉及CORS配置不当；

跨域资源共享（CORS）是一种浏览器机制，可实现对位于给定域外部的资源的受控访问。它扩展了同源策略（SOP）并增加了灵活性。但是，如果网站的CORS策略配置和实施不当，它也可能带来用户敏感数据被窃取、基于跨域的攻击等风险。

Security Misconfiguration:

Hey, its an API right ? so we ARE expecting Cross Origin Requests. We just
hope it works fine.

调用 _`API:Create User`_ ，创建用户，拿token；

![image](https://image.3001.net/images/20220506/1651814655_6274b0ff0b49e7cb9b1e4.png!small)

利用得到的token，测试登录；

![image](https://image.3001.net/images/20220506/1651814667_6274b10b7261653e96f9f.png!small)

调用 _`API:Get Key`_ ，发现 `Access-Control-Allow-Origin`字段；

![image](https://image.3001.net/images/20220506/1651814675_6274b113cd559b538cb20.png!small)

    
    
    简单请求：
    浏览器直接发出CORS请求，在头信息中添加一个Origin字段，用来说明请求来自哪个源，服务器根据这个值，决定是否同意这次请求。
    如果Origin指定的源在许可范围内，即验证通过，服务端会在ResponseHeader添加下面几个字段：
    1. Access-Control-Allow-Origin：该字段是必须的。它的值要么是请求时Origin字段的值，要么是一个*，表示接受任意域名的请求。
    2. Access-ControI-AIIow-CredentiaIs：该字段可选。它的值是一个布尔值，表示是否允许发送Cookie。默认情况下，Cookie不包括在CORS请求之中。当设置为true时，即表示服务器明确许可，Cookie可以包含在请求中，一起发给服务器。
    3. Access-ControI-Allow-Headers：用来判断浏览器通过什么方式发起的，默认是content-type，如果后端服务器未配置这个请求头，或者仅允许content-type访问，而浏览器通过XMLHttpRequest发起，也会跨域失败。
    

添加字段后，重放；

![image](https://image.3001.net/images/20220506/1651814690_6274b122717759e004cd2.png!small)

拿到flag。

    
    
    {
      "flag": "flag{api7_e71b65071645e24ed50a}",
      "user": {
        "id": 2,
        "username": "test1",
        "password": "123456",
        "authkey": "5da0c2a9db029e62415ea765e00117c90b57cd24fcc803a54c4c7a2292d2c760"
      }
    }
    

## API8 - 注入

注入攻击不仅在 Web 应用程序中普遍存在，而且在 OWASP 十大 API 安全列表中占有一席之地。在请求中，API 请求可能包括 SQL
查询、NoSQL 查询、LDAP、操作系统命令或其他命令。当服务器未经过滤就盲目地将从用户端收到的输入作为查询时，就会产生注入。

Injection:

I think you won't get credentials for this. You can try to login though.

调用 _`API:User Login`_ ，测试注入；

![image](https://image.3001.net/images/20220506/1651814704_6274b130ae082fbd0d1e2.png!small)

设置payload；

![image](https://image.3001.net/images/20220506/1651814712_6274b138de2fd709c536b.png!small)

润!

![image](https://image.3001.net/images/20220506/1651814722_6274b142b1a75de33717f.png!small)

拿到token；

![image](https://image.3001.net/images/20220506/1651814735_6274b14fea6e6f1183c4d.png!small)

    
    
    {
      "id": 1,
      "username": "admin",
      "secret": "flag{api8_509f8e201807860d5c91}"
    }
    

## API9 - 资产管理不当

在这种情况下，处理所有请求和响应的资产没有得到正确处理。例如，当新的更新进入市场时，开发人员将 API 更新为 v3，但忘记禁用 API
v2。现在，如果某些攻击者将 URL 中的 v3 的值更改为 v2。他可以利用 v2 版本中存在的漏洞。

Improper Assets Management:

Hey Good News!!!!! We just launched our v2 API :)

调用 _`API: Login`_ ，改包；

![image](https://image.3001.net/images/20220506/1651814745_6274b159f089717439f5f.png!small)

没有返回内容，但是返回值200，看来api没问题；

开始爆破pin，pin码一般是纯数字，爆破方法同API4；

![image](https://image.3001.net/images/20220506/1651814754_6274b1627370db2933ca1.png!small)

拿到flag。

    
    
    {
      "id":1,
      "username":"richardbranson",
      "accbalance":"flag{api9_81e306bdd20a7734e244}"
    }
    

## API0 - 日志和监控不足

大多数 API 未配置用于监视、记录或发出警告，从而允许攻击者长时间不被发现，允许他在系统中保持持久性，执行横向移动，以及危及重要系统。

如果系统设置为通过日志记录和监控来检测和阻止攻击尝试，则可以轻松避免这种情况。

Insufficient Logging & Monitoring:

Nothing has been logged or monitored , You caught us :( !

直接调用 _`API: Get Flag`_ ，就拿到flag了，如同碰瓷一般。

    
    
    {
      "message": "Hey! I didn't log and monitor all the requests you've been sending. That's on me...",
      "flag": "flag{api10_5db611f7c1ffd747971f}"
    }
    

