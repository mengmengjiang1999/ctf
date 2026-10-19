**URL重定向**

 **简介：**

HTTP 协议的重定向响应的状态码为 3xx 。浏览器在接收到重定向响应的时候，会采用该响应提供的新的 URL ，并立即进行加载；

大多数情况下，除了会有一小部分性能损失之外，重定向操作对于用户来说是不可见的。

不同类型的重定向映射可以划分为三个类别： **永久重定向、临时重定向和特殊重定向。**

 **HTTP状态码：**

300 Multiple Choices ：可选重定向，表示客户请求的资源已经被转向到另外的地址了，但是没有说明是否是永久重定向

还是临时重定向。

301 Moved Permancently ： **永久重定向** ，同上，但是这个状态会告知客户请求的资源已经永久性的存在在新的重定向的

URL上。

302 Moved Temporarily ： **临时重定向** ，在HTTP1.1中状态描述是Found，这个和300一样，但是说明请求的资源临时被转

移到新的URL上，在以后可能会再次变动或者此URL会正常请求客户的连接。

303 See Other ： 类似于301/302，不同之处在于，如果原来的请求是POST，Location头指定的重定向目标文档应该通过

GET提取（HTTP 1.1新）。

304 Not Modified ： 并不真的是重定向 - 它用来响应条件GET请求，避免下载已经存在于浏览器缓存中的数据。

305 Use Proxy ： 客户请求的文档应该通过Location头所指明的代理服务器提取（HTTP 1.1新）。

306 (废弃，不在使用)

307 Temporary Redirect ： 和302（Found）相同。许多浏览器会错误地响应302应答进行重定向，即使原来的请求是POST

，即使它实际上只能在POST请求的应答是303时 才能重定向。由于这个原因，HTTP 1.1新增了307，以便更加清除地区分几

个状态代码：当出现303应答时，浏览器可以跟随重定向的GET和POST请求；如果是307应答，则浏览器只 能跟随对GET请求

的重定向。（HTTP 1.1新）

 **重定向常见的参数：**

redirect

redirect_to

redirect_url

url

jump

jump_to

target

to

link

linkto

domain

 **重定向位置：**

1.用户登录、统一身份认证处，认证完后会跳转

  2. 用户分享、收藏内容过后，会跳转
  3. 跨站点认证、授权后，会跳转
  4. 站内点击其它网址链接时，会跳转

 **绕过思路：**

  1. 单斜线"/"绕过

https://www.landgrey.me/redirect.php?url=/www.evil.com

  2. 缺少协议绕过

https://www.landgrey.me/redirect.php?url=//www.evil.com

  3. 多斜线"/"前缀绕过

https://www.landgrey.me/redirect.php?url=///www.evil.com

https://www.landgrey.me/redirect.php?url=www.evil.com

  4. 利用"@"符号绕过

https://www.landgrey.me/redirect.php?url=https://www.landgrey.me@www.evil.com

  5. 利用反斜线"\"绕过

https://www.landgrey.me/redirect.php?url=https://www.evil.com\www.landgrey.me

  6. 利用"#"符号绕过

https://www.landgrey.me/redirect.php?url=https://www.evil.com#www.landgrey.me

  7. 利用"?"号绕过

https://www.landgrey.me/redirect.php?url=https://www.evil.com?www.landgrey.me

  8. 利用"\\\"绕过

https://www.landgrey.me/redirect.php?url=https://www.evil.com\\\www.landgrey.me

  9. 利用"."绕过

<span></span>https://www.landgrey.me/redirect.php?url=.evil
(可能会跳转到www.landgrey.me.evil域名)

https://www.landgrey.me/redirect.php?url=.evil.com (可能会跳转到evil.com域名)

10.重复特殊字符绕过

https://www.landgrey.me/redirect.php?url=///www.evil.com//..

<https://www.landgrey.me/redirect.php?url=www.evil.com//>..

 **漏洞危害：**

最为直接的就是钓鱼

 **漏洞防御：**

1.代码固定跳转地址，不让用户控制变量

  2. 跳转目标地址采用白名单映射机制
  3. 合理充分的校验校验跳转的目标地址，非己方地址时告知用户跳转风险

 **URL重定向：**

当点击此处时，即可完成跳转

![1615427328_60497700d6072954a6447.png!small](https://image.3001.net/images/20210311/1615427328_60497700d6072954a6447.png!small)

在此处可以看到后面附带了url参数

![1615427348_604977146ca197abbf84a.png!small](https://image.3001.net/images/20210311/1615427348_604977146ca197abbf84a.png!small)

当我们把i换位其他网址时，发现即可进行重定向访问

![1615427459_60497783871df1b6c1512.png!small](https://image.3001.net/images/20210311/1615427459_60497783871df1b6c1512.png!small)

![1615427470_6049778e0c8f3c4699d34.png!small](https://image.3001.net/images/20210311/1615427470_6049778e0c8f3c4699d34.png!small)

