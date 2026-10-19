## 一、背景

笔者最近在慕课录制了一套[XSS跨站漏洞
加强Web安全](https://coding.imooc.com/class/242.html)视频教程，课程当中有讲到XSS的挖掘方式，所以在录制课程之前需要做大量实践案例，最近视频已经录制完成，准备将这些XSS漏洞的挖掘过程记录下来，方便自己也方便他人。

>
> 在本篇文章当中会一permeate生态测试系统为例，笔者此前写过一篇文章当中笔者已经讲解如何安装permeate[渗透测试](http://bbs.ichunqiu.com/portal.php)系统，因此这里不再重复讲解如何安装此渗透测试系统，参考文档:[利用PHP扩展Taint找出网站的潜在安全漏洞实践](https://segmentfault.com/a/1190000016032501#articleHeader11)

## 二、内容概要

  1. XSS漏洞原理
  2. 反射型挖掘
  3. 存储型挖掘

## 三、漏洞简介

在实践漏洞之前，笔者准备先简单介绍一下XSS漏洞，不过XSS的相关概念介绍并不是本文的重点，因此不会过多细讲；XSS的漏洞类型主要分为三类：反射型、存储型、DOM型

### 3.1 漏洞成因

XSS的漏洞主要成因是后端接收参数时未经过滤，导致参数改变了HTML的结构，如下图所示  
![image.png](https://image.3001.net/images/20180903/1535957035_5b8cd82b968fc.png!small)  

在图中可以看到攻击者的参数被原样放到了HTML代码当中，导致原本的结构被改变，当这份代码被浏览器执行之后，将执行alert事件。

### 3.2 反射型

反射型XSS在笔者闹钟的定义是，如果URL地址当中的恶意参数会直接被输出到页面中，导致攻击代码被触发，便称之为反射型XSS，如下图所示![image.png](https://image.3001.net/images/20180903/1535957053_5b8cd83d4f01d.png!small)  

在图中可以看到，此处原本是输入一个名字，单实际传递了一个`script`标签，此标签也被原样放到了HTML结构当中，结果`script`标签代码中的代码被触发

### 3.3 存储型

存储型XSS，顾名思义便是恶意参数被存储起来了，通常存储在后端服务器当中，所以存储型XSS在URL地址当中不会包含恶意参数，对于受害者来说，很难发现已经被攻击了，如下图存储型XSS被触发

  
![image.png](https://image.3001.net/images/20180903/1535957066_5b8cd84a55c90.png!small)  

在图中笔者并没有在URL地址当中看到`script`代码，但是攻击代码依然被触发，说明攻击代码来自于服务器，而这个攻击代码确实是由攻击者传递到服务器当中去的。

一般情况下，当攻击者将攻击代码通过表单传递到服务器当中去，会得到一个新页面的地址，这个地址中URL并没有明显异常，比如如下URL地址

    
    
    http://permeate.songboy.net/article/1

但当存在存储型XSS时，受害者打开此URL，攻击代码将会被触发，这种情况下笔者便称之为存储型XSS漏洞。

### 3.4 DOM型

DOM型XSS较为特殊，笔者前面反射型XSS和存储型XSS都是以传播方式来区分的，而DOM型XSS和传参方式无关，而是当开发者做了一些[安全防护](http://bbs.ichunqiu.com/forum-59-1.html)之后，任出现安全问题的一种现象，如下图所示

![image.png](https://image.3001.net/images/20180903/1535957077_5b8cd855c6e6e.png!small)  

在图片中，可以看到参数`name`已经使用函数转义了，按理说此时将参数传递到前端页面是不会产生XSS漏洞的；但当JavaScript代码将参数进行DOM节点操作之后，原本被转义的代码又会被还原，因此还是会被触发，如下图所示

  
![image.png](https://image.3001.net/images/20180903/1535957084_5b8cd85c8bf83.png!small)  

在图中看到XSS代码已经被触发，这种DOM型XSS相对来说更加隐蔽，所以防御XSS漏洞的不能仅仅依靠后端开发者，前端开发者也应当了解XSS漏洞。

## 四、反射型挖掘

经过上一节的原理介绍，笔者相信大家对XSS已经有一些了解，现在笔者需要进行手工XSS漏洞挖掘，在手工挖掘之前笔者需要先逛逛网站有哪些功能点，如下图是permeate的界面

  
![image.png](https://image.3001.net/images/20180903/1535957093_5b8cd86584a21.png!small)  

### 4.1 思路分析

在知道反射型XSS，是通过URL地址传播的，那么笔者就需要思考那些地方会让URL地址的参数在页面中显示；相信读者都用过一些网站的站内搜索，在站内搜索的位置往往会将搜索的关键词展示在页面当中，如下图所示

  
![image.png](https://image.3001.net/images/20180903/1535957100_5b8cd86c8d48a.png!small)  

而在首页笔者也看见此网站有搜索功能，因此可以从搜索位置着手，可以在搜索位置输入一个简单的payload,参考如下

    
    
    <script>alert(123)</script>

当点击搜索后，会自动跳转到以下URL当中，此时浏览器的URL地址已经发生了变化，URL地址如下：

    
    
    http://permeate.songboy.net/home/search.php?keywords=<script>alert(123)</script>

搜索的表单是使用了GET传参，满足了测试反射型的第一步要求

### 4.2 漏洞检验

接下来就需要看看笔者的payload有没有被触发,结果很意外，不但没有被触发还被浏览器所阻止了，如下图

  
![image.png](https://image.3001.net/images/20180903/1535957114_5b8cd87a55e4c.png!small)  

这里就需要跟读者说明一下，谷歌内核浏览器自带XSS筛选器，所以对于反射型XSS测试，尽量不使用谷歌浏览器，笔者建议使用火狐浏览器进行测试；

### 4.3 结果分析

现在笔者将上面的URL地址复制下来，并粘贴到火狐浏览器当中，并按下回车，看到效果如下图

  
![image.png](https://image.3001.net/images/20180903/1535957132_5b8cd88cab671.png!small)  

此时payload已经被触发，说明找到了一个反射型XSS的漏洞，这种漏洞相对来说非常初级，随着浏览器的XSS筛选器变得更加智能，这种漏洞也越来越少，在下面的内容当中笔者将会提到存储型XSS挖掘与绕过。

## 五、存储型挖掘

现在笔者来寻找存储型XSS，存储型的攻击代码是存储在服务端，因此需要找出一些会将表单内容存储到服务端的位置，笔者在之前已经对permeate做了一番了解，因此知道permeate拥有发帖和回帖功能，这些功能正是需要将参数存储起来并展示的地方。

### 5.1 发现漏洞

在首页点击XSS板块，进入到了板块列表当中，如下图

![image.png](https://image.3001.net/images/20180903/1535957141_5b8cd8956f415.png!small)  

在右下角能看到有一个`发帖`按钮，点击发帖按钮后，即可进入发帖界面，如下图

  
![image.png](https://image.3001.net/images/20180903/1535957147_5b8cd89be582b.png!small)  

在permeate渗透测试系统当中，笔者如果要发表帖子，那么就需要有账号，笔者这里随便注册一个账号，注册过程笔者就不详细讲解了

### 5.2 检验漏洞

在注册账号完成并登陆之后，笔者再次打开发帖页面，并在标题处和内容处都填写payload,参考内容如下：

    
    
    <script>alert(123)</script>

在标题处和帖子内容中分别填写payload，填写好之后，应和与下图一致

  
![image.png](https://image.3001.net/images/20180903/1535957163_5b8cd8ab4d114.png!small)  

填写好内容之后，笔者点击下方的`发表`按钮，即可进行发帖，发帖成功会弹出一个提示成功，如下图所示

  
![image.png](https://image.3001.net/images/20180903/1535957169_5b8cd8b1a3cb1.png!small)  

点击`确定`之后，会跳转到发帖列表，并弹出一个123的提示框，如下图所示

![image.png](https://image.3001.net/images/20180903/1535957175_5b8cd8b7a45ec.png!small)  

如果看到这个弹框，说明笔者的payload已经被执行，点击确定就可以看到列表的内容，如下图所示

  
![image.png](https://image.3001.net/images/20180903/1535957180_5b8cd8bcc29e1.png!small)  

在列表中只显示标题，所以帖子内容中的payload并没有被执行；

### 5.3 抓包绕过

现在点击标题，进入帖子详情页面，在详情页笔者发现payload也只触发了一次，而且内容当中的标签被直接显示了出来，如下图

  
![image.png](https://image.3001.net/images/20180903/1535957190_5b8cd8c6ecb75.png!small)  

当标签被直接显示出来，这说明笔者的参数被转义了；转义分为两种，前端转义和后端转义，如果是后端转义通常笔者会放弃测试，如果是前端转义则可以绕过这个限制；在这里笔者发现标题没有被转义，而内容被转，猜测可能是前端做的转义，因此可以通过浏览器的审查工具将数据包拷贝下来；

首先重新打开发帖页面，然后在网页随便一个位置`单击鼠标右键`->选择`审查元素`->切换到`network`标签并勾选`Preserve
log`，打开网络并勾选`Preserve log`的目的是让发表帖子之后，能在网络请求中找到该记录，现在笔者可以填写新的payload，如下图  
![image.png](https://image.3001.net/images/20180903/1535957198_5b8cd8ce670bb.png!small)点击发表按钮之后，笔者可以在控制台中找到刚才的post请求，从请求中可以看出，这个数据发出去就已经被转义了，如下图![image.png](https://image.3001.net/images/20180903/1535957216_5b8cd8e0b4141.png!small)

  

### 5.4 编码替换

当确定这个地方存在前端做了转义处理，如果后端没有做处理，笔者就可以绕过它，现在笔者将请求复制出来，然后改变里面的数据，如下图  
![image.png](https://image.3001.net/images/20180903/1535957232_5b8cd8f014291.png!small)  

复制出来的数据如下

    
    
    curl 'http://permeate.songboy.net/home/_fatie.php?bk=6&zt=0' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' -H 'Origin: http://permeate.songboy.net' -H 'Upgrade-Insecure-Requests: 1' -H 'Content-Type: application/x-www-form-urlencoded' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' -H 'Referer: http://permeate.songboy.net/home/fatie.php?bk=6' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' -H 'Cookie: __cfduid=defc970ef7081e30aedd761da5762b1891532003579; UM_distinctid=1655a61a23343c-03f0904540a333-34657908-1fa400-1655a61a234323; PHPSESSID=rufhm0741qfv55cpfnc80k1g4l' --data 'csrf_token=3908&bk=6&title=222%3Cscript+%3Ealert%28123%29%3C%2Fscript%3E&content=%3Cp%3E222%26lt%3Bscript+%26gt%3Balert%28123%29%26lt%3B%2Fscript%26gt%3B%3C%2Fp%3E' --compressed

笔者找到参数中的`title`和`content`参数值，将title的参数值复制下来，然后替换`content`的参数值，替换后的内容如下

    
    
    curl 'http://permeate.songboy.net/home/_fatie.php?bk=6&zt=0' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' -H 'Origin: http://permeate.songboy.net' -H 'Upgrade-Insecure-Requests: 1' -H 'Content-Type: application/x-www-form-urlencoded' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' -H 'Referer: http://permeate.songboy.net/home/fatie.php?bk=6' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' -H 'Cookie: __cfduid=defc970ef7081e30aedd761da5762b1891532003579; UM_distinctid=1655a61a23343c-03f0904540a333-34657908-1fa400-1655a61a234323; PHPSESSID=rufhm0741qfv55cpfnc80k1g4l' --data 'csrf_token=3908&bk=6&title=222%3Cscript+%3Ealert%28123%29%3C%2Fscript%3E&content=222%3Cscript+%3Ealert%28123%29%3C%2Fscript%3E' --compressed

替换完成之后，笔者将此内容复制到终端当中（如果读者用的是windows操作系统，可以下载一个cmder），然后按下回车键，结果如下图

  
![image.png](https://image.3001.net/images/20180903/1535957239_5b8cd8f737f78.png!small)  

### 5.5 结果分析

在返回结果当中可以看到提示发帖成功，此时就笔者已经成功发布了一个新帖子，回到帖子列表当中看到有三条帖子，在最后面的帖子则是笔者新发布的，如下图

![image.png](https://image.3001.net/images/20180903/1535957245_5b8cd8fd331cf.png!small)  

打开详情页，笔者被弹了两次提示框，说明标题和内容当中的payload都被触发,并且在控制台当中也可以看到`script`变成了DOM节点，而不是文本展现出来，如下图所示

  
![image.png](https://image.3001.net/images/20180903/1535957255_5b8cd907dc1a8.png!small)  

看到此处说明笔者已经成功绕过前端XSS过滤器，晚一些在发表一篇工具盘，和防御篇，大家有兴趣也可以支持一下笔者的视频教程，URL地址如下

    
    
    https://coding.imooc.com/class/242.html

Thanks♪(･ω･)ﾉ

* * *

作者:汤青松

微信:songboy8888

日期:2018-08-21

# 大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~

