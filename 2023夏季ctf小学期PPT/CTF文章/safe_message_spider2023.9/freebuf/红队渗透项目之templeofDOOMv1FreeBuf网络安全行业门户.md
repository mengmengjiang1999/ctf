本项目是[0katz](https://www.vulnhub.com/author/0katz,587/)作者精心制作的项目环境，目标是获取获得root权限并找到flag.txt文本信息，该项目作为OSCP考试培训必打的一个项目环境，该作者评定该环境为渗透中级水准难度。不管是零基础的学习者，还是从事安全行业的人员，都可以通过这个项目学习到一些技巧或知识。

 **注意：**

本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

![1661052367_6301a5cf75fbb0684f280.png!small?1661052367588](https://image.3001.net/images/20220821/1661052367_6301a5cf75fbb0684f280.png!small?1661052367588)

信息收集非常重要，有了信息才能知道下一步该如何进行，下面使用nmap进行信息收集

### 1\. nmap全端口扫描

本项目已经显示出ip地址，所以直接使用nmap进行信息收集，全端口服务扫描

    
    
    nmap -p- 192.168.27.129 -A

![1661052381_6301a5dd8fa9986b5a92a.png!small?1661052381804](https://image.3001.net/images/20220821/1661052381_6301a5dd8fa9986b5a92a.png!small?1661052381804)

### 2\. web信息枚举

![1661052390_6301a5e6d433c7976bc50.png!small?1661052391002](https://image.3001.net/images/20220821/1661052390_6301a5e6d433c7976bc50.png!small?1661052391002)

Under Construction, Come Back Later!

正在建设中，稍后再来！

  

dirb nikto都爆破不出来，那么就进行BP流量包分析！

下面使用Burp抓包进行流量分析

### 3\. BurpSuite分析

![1661052402_6301a5f26c57c1cb6b24a.png!small?1661052402554](https://image.3001.net/images/20220821/1661052402_6301a5f26c57c1cb6b24a.png!small?1661052402554)

Cookie:
profile=eyJ1c2VybmFtZSI6IkFkbWluIiwiY3NyZnRva2VuIjoidTMydDRvM3RiM2dnNDMxZnMzNGdnZGdjaGp3bnphMGw9IiwiRXhwaXJlcz0iOkZyaWRheSwgMTMgT2N0IDIwMTggMDA6MDA6MDAgR01UIn0%3D

这里的%3D是url编码：=

所以下面尝试进行解码

base64解码：

{"username":"Admin","csrftoken":"u32t4o3tb3gg431fs34ggdgchjwnza0l=","Expires=":Friday,
13 Oct 2018 00:00:00 GMTIn0%3D

![1661052411_6301a5fb838cb7ba42530.png!small?1661052411684](https://image.3001.net/images/20220821/1661052411_6301a5fb838cb7ba42530.png!small?1661052411684)

  

存在u32t4o3tb3gg431fs34ggdgchjwnza0l=值！

把抓到的包从BP放掉会发现存在报错

![1661052419_6301a603106ba49896192.png!small?1661052419396](https://image.3001.net/images/20220821/1661052419_6301a603106ba49896192.png!small?1661052419396)

从错误的信息可以看出 Nodeadmin 和 Node-Serialize 正在目标应用程序上使用

发现Web服务正在使用JSON，并且Nmap扫描中有Node.js框架

谷歌搜索Node-Serialize exploit！

### 4\. Node.js反序列化

Java、PHP、Ruby和Python有相当多的反序列化问题！

serialize：序列化

<https://www.php.net/serialize>

unserialize：反序列化

<https://www.php.net/manual/zh/function.unserialize.php>

PHP允许对象序列化。序列化是一个允许保存对象并在以后重用它的过程。例如，可以保存一个包含一些用户信息的对象，然后再使用它。

为了序列化一个对象，需要调用“序列化”函数。它将返回一个字符串表示形式，可以通过调用“unserialize”函数重新创建新的对象来重用它。

首先需要知道一点，序列化后在反序列化数据，该数据是要经过程序是：反序列化->序列化->存储调用

unserialize()通过传递带有立即调用函数表达式(IIFE)的序列化JavaScript的对象，可以利用传递到节点中的序列化模块的函数，使得不受信任的数据来实现任意代码执行。

<https://opsecx.com/index.php/2017/02/08/exploiting-node-js-deserialization-bug-for-remote-code-execution/>

IIFE：全称为立即调用函数表达式IIFE(Imdiately Invoked Function Expression)

![1661052430_6301a60e31aeebd0c09ed.png!small?1661052430414](https://image.3001.net/images/20220821/1661052430_6301a60e31aeebd0c09ed.png!small?1661052430414)

但有时需要在定义函数之后，立即调用该函数（函数只使用一次）

<https://segmentfault.com/a/1190000015089341>

参考文章知道通过()可以使得一个函数表达式立即执行！

* * *

开始利用！

  

说存在反序列化漏洞利用，这边先测试下是否存在用，反序列化函数试试：构建参数

{"username":"Admin"}

base64编码：eyJ1c2VybmFtZSI6IkFkbWluIn0=

Send回显：Hello Admin

![1661052436_6301a614d80f6bf64e2f2.png!small?1661052437075](https://image.3001.net/images/20220821/1661052436_6301a614d80f6bf64e2f2.png!small?1661052437075)

在opsecx上面连接中，存在利用的payload：

\------------------------------------------
{"rce":"$$ND_FUNC$$function (){\n \t require('child_process').exec('ls /',

function(error, stdout, stderr) { console.log(stdout) });\n }()"}

  

var serialize = require('node-serialize');

var payload = '{"rce":"$$ND_FUNC$$function
(){require('child_process').exec('ls /', function(error, stdout, stderr) {
console.log(stdout) });}()"}';

serialize.unseri

