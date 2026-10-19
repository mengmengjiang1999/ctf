**  
**

# **XXE从入门到放弃** ****

  

****一、 **认识XML和XXE**

 **  
**XXE全称XML External Entity
Injection，也就是XML外部实体注入攻击，是对非安全的外部实体数据进行处理时引发的安全问题。要想搞懂XXE，肯定要先了解XML语法规则和外部实体的定义及调用形式。

##  **XML基础知识** ****

XML用于标记电子文件使其具有结构性的标记语言，可以用来标记数据、定义数据类型，是一种允许用户对自己的标记语言进行定义的源语言。XML文档结构包括XML声明、DTD文档类型定义（可选）、文档元素。

##  **XML语法规则如下：** ****

1. **所有的XML元素都必须有一个关闭标签** ****

2. **XML标签对大小写敏感** ****

3. **XML必须正确嵌套** ****

4. **XML属性值必须加引号** **””** ****

5. **实体引用** （在标签属性，以及对应的位置值可能会出现<>符号，但是这些符号在对应的XML中都是有特殊含义的，这时候我们必须使用对应html的实体对应的表示，比如<傅好对应的实体就是lt，>符号对应的实体就是gt）

6\. **在XML中，空格会被保留** （案例如：<p>a空格B</p>，这时候a和B之间的空格就会被保留）

![图片.png](https://image.3001.net/images/20200117/1579256193_5e218981c7cea.png!small)![图片.png](https://image.3001.net/images/20200117/1579256206_5e21898ea5e90.png!small)

### **XML元素介绍** ****

XML元素是指从（且包括）开始标签直到（且包括）结束标签的部分。

每个元素又有可以有对应的属性。XML属性必须加引号。

![图片.png](https://image.3001.net/images/20200117/1579256218_5e21899a09701.png!small)

注意：

(1) **XML文档必须有一个根元素** ****

(2) **XML元素都必须有一个关闭标签** ****

(3) **XML标签对大小写敏感** ****

(4) **XML元素必须被正确的嵌套** ****

(5) **XML属性值必须加引号** ****

## **XML DTD介绍** ****

DTD文档类型定义，约束了xml文档的结构。 拥有正确语法的XML被称为“形式良好”的XML，通过DTD验证约束XML是“合法”的XML。

![图片.png](https://image.3001.net/images/20200117/1579256238_5e2189aea5479.png!small)![图片.png](https://image.3001.net/images/20200117/1579256253_5e2189bdd2074.png!small)![图片.png](https://image.3001.net/images/20200117/1579256266_5e2189ca0f5da.png!small)

###  **DTD是什么？** ****

XML 文档有自己的一个格式规范，这个格式规范是由一个叫做 DTD 文档类型定义（document type definition） 的东西控制的。

DTD用来描述xml文档的结构，一个DTD文档包含：

元素的定义规则；元素之间的关系规则；属性的定义规则。

DTD 可被成行地声明于 XML 文档中，也可作为一个外部引用。

他就是长得下面这个样子：

####  **内部的 DOCTYPE 声明** ****

内部声明DTD类型

内部声明DTD类型声明：<!DOCTYPE 根元素[子 元素声明]>

![图片.png](https://image.3001.net/images/20200117/1579256285_5e2189ddbd221.png!small)

####  **引用外部实体：** ****

我们主要关注XML外部实体的定义和调用方式：

<!ENTITY 实体名称 SYSTEM "URI">

![图片.png](https://image.3001.net/images/20200117/1579256302_5e2189ee2848e.png!small)

#### **DTD数据类型** ****

PCDATA的意思是被解析的字符数据/

PCDATA的意思是被解析的字符数据，PCDATA是会被解析器解析的文本

CDATA的意思是字符数据

CDATA是不会被解析器解析的文本，在这些文本中的标签不会被当作标记来对待，其中的实体也不会被展开。

**DTD实体介绍** ****

（实体定义）

实体是用于定义引用普通文本或者特殊字符的快捷方式的变量

在DTD中的实体类型，一般分为：内部实体和外部实体，细分又分为一般实体和参数实体。除外部参数实体引用以字符（%）开始外，其它实体都以字符（&）开始，以字符（;）结束。

#####  **内部实体：** ****

<!ENTITY 实体名称 "实体的值">

#####  **外部实体：** ****

<!ENTITY 实体名称 SYSTEM "URI/URL">

![图片.png](https://image.3001.net/images/20200117/1579256331_5e218a0b4fbcd.png!small)

#####  **外部参数实体：** ****

<!ENTITY % 实体名 "实体内容”>

![图片.png](https://image.3001.net/images/20200117/1579256343_5e218a175cdd6.png!small)

##  **XML注入产生的原理** ****

XXE漏洞全称XML External Entity
Injection即xml外部实体注入漏洞，XXE漏洞发生在应用程序解析XML输入时，没有禁止外部实体的加载，导致可加载恶意外部文件，造成文件读取、命令执行、内网端口扫描、攻击内网网站、发起dos攻击等危害。xxe漏洞触发的点往往是可以上传xml文件的位置，没有对上传的xml文件进行过滤，导致可上传恶意xml文件。

xxe漏洞触发的点往往是可以上传XML文件约位置，没有对上传的XML文件进行过滤，导致可以上传恶意的XML文件。

### **怎么判断网站是否存在XXE漏洞** ****

最直接的方法就是用burp抓包，然后，修改HTTP请求方法，修改Content-Type头部字段等等，查看返回包的响应，看看应用程序是否解析了发送的内容，一旦解析了，那么有可能XXE攻击漏洞，接下来，来看一个小小的展示：

这个是测试xxe的测试点：http://169.254.4.52/bWAPP/xxe-1.php

我们点击下面的Any bugs然后用burp抓包

###
![图片.png](https://image.3001.net/images/20200117/1579256360_5e218a288b191.png!small)![图片.png](https://image.3001.net/images/20200117/1579256370_5e218a3294b7d.png!small)
****

我们随便输入下

![图片.png](https://image.3001.net/images/20200117/1579256381_5e218a3d3cc12.png!small)

从上面我们可以看到，web应用正在解析xml的内容，接受用户特定或者自定义的输入，然后呈现给用户。为了验证，我们可以构造如下的输入：

 ****

![图片.png](https://image.3001.net/images/20200117/1579256393_5e218a4996976.png!small)

可以看到应用程序确实是直接解析了xml，那么如果xml文档中有一个参数是用来调用远程服务器的内容？这个参数是可控的 ,我们可以做什么？

###  **XXE漏洞-文件读取** ****

PHP中测试POC

 _F_ _ile:///path/to/file.ext_

[ _http://url/file.ext_](http://url/file.ext)

PHP://filter/read=convert.base64-encode/resource=/home/bee/test.php

####  **读取文档** ****

#####  **有回显的xxe利用** ****

Payload:

![图片.png](https://image.3001.net/images/20200117/1579256407_5e218a5790df0.png!small)![图片.png](https://image.3001.net/images/20200117/1579256414_5e218a5e95ad6.png!small)

####  **读取php文件** ****

直接读取php文件会报错，因为php文件里面有 <>//等特殊字符，xml解析时候会当成xml语法来解析。这时候就分不清处哪个是真正的xml语句了，

直接利用file协议读取PHP文件，就会产生报错。那么需要base64编码来读取，

![图片.png](https://image.3001.net/images/20200117/1579256431_5e218a6f2ae83.png!small)![图片.png](https://image.3001.net/images/20200117/1579256438_5e218a76aafd5.png!small)![图片.png](https://image.3001.net/images/20200117/1579256446_5e218a7e01f3e.png!small)

进行解密后得到对应内容

![图片.png](https://image.3001.net/images/20200117/1579256455_5e218a870fd62.png!small)

##### **本地测试无回显注入读取文件** ****

但是，在实际情况中，大多数情况下服务器上的 XML
并不是输出用的，所以就少了输出这一环节，这样的话，即使漏洞存在，我们的payload的也被解析了，但是由于没有输出，我们也不知道解析得到的内容是什么，因此我们想要现实中利用这个漏洞就必须找到一个不依靠其回显的方法——外带数据

先看一下漏洞示例：

![图片.png](https://image.3001.net/images/20200117/1579256469_5e218a95b6b6d.png!small)

相较于前面有回显的漏洞代码，我们去掉了内容输出的一部分。这样，用之前的payload就没有作用了：

![图片.png](https://image.3001.net/images/20200117/1579256481_5e218aa1b5018.png!small)

Payload的构造：

有了前面使用外部DTD文件来拼接内部DTD的参数实体的经验，我们可以知道，通过外部DTD的方式可以将内部参数实体的内容与外部DTD声明的实体的内容拼接起来，那么我们就可以有这样的设想：

(1) 客户端发送payload 1给web服务器

(2) web服务器向vps获取恶意DTD，并执行文件读取payload2

(3) web服务器带着回显结果访问VPS上特定的FTP或者HTTP

(4) 通过VPS获得回显（nc监听端口）

首先，我们使用ncat监听一个端口：

![图片.png](https://image.3001.net/images/20200117/1579256496_5e218ab000b27.png!small)

也可以用python创建一个建议的http服务。

python -m SimpleHTTPServer 端口

然后，我们构造payload：

我们选择使用外部DTD，在我们自己所能掌控（或是自己搭建）的主机上编写一个dtd文件：

<

![图片.png](https://image.3001.net/images/20200117/1579256508_5e218abc1ce01.png!small)

我们注意到，第一个参数实体的声明中使用到了php的base64编码，这样是为了尽量避免由于文件内容的特殊性，产生xml解析器错误。

Payload如下：

如图，我们先声明一个外部的DTD引用，然后再xml文档内容中引用外部DTD中的一般实体。

开始攻击：![图片.png](https://image.3001.net/images/20200117/1579256534_5e218ad605473.png!small)

然后查看我们的端口监听情况，会发现我们收到了一个连接请求，问号后面的内容就是我们读取到的文件内容经过编码后的字符串：

Ps：

有时候也会出现报错的情况（这是我们在漏洞的代码中没有屏蔽错误和警告），比如我们这里的payload没有选用php的base64编码，这里报错了，但是同时也将所读取的内容爆了出来，只是特殊字符经过了HTML实体编码。

![图片.png](https://image.3001.net/images/20200117/1579256551_5e218ae74903f.png!small)

###  **内网探测** ****

xxe 由于可以访问外部 url，也就有类似 ssrf 的攻击效果，同样的，也可以利用 xxe 来进行内网探测。

可以先通过 file 协议读取一些配置文件来判断内网的配置以及规模，以便于编写脚本来探测内网。

一个 python 脚本实例：

![图片.png](https://image.3001.net/images/20200117/1579256611_5e218b2346bf6.png!small)![图片.png](https://image.3001.net/images/20200117/1579256621_5e218b2d7e087.png!small)  

运行起来大概是这样

**![图片.png](https://image.3001.net/images/20200117/1579256631_5e218b374ac88.png!small)**

****

### **DDOS攻击** ****

 ****

![图片.png](https://image.3001.net/images/20200117/1579256642_5e218b429733f.png!small)![图片.png](https://image.3001.net/images/20200117/1579256654_5e218b4e12f74.png!small)

该攻击通过创建一项递归的 XML 定义，在内存中生成十亿个”abc”字符串，从而导致 DDoS
攻击。原理为：构造恶意的XML实体文件耗尽可用内存，因为许多XML解析器在解析XML文档时倾向于将它的整个结构保留在内存中，解析非常慢，造成了拒绝服务器攻击。

##  **影响:** ****

此漏洞非常危险, 因为此漏洞会造成服务器上敏感数据的泄露，和潜在的服务器拒绝服务攻击。

# **防御方法：** ****

1. 禁用外部实体

2\. 过滤和验证用户提交的XML数据

3\. 不允许XML中含有任何自己声明的DTD

4\. 有效的措施：配置XML parser只能使用静态DTD，禁止外来引入；对于Java来说，直接设置相应的属性值为false即可

参考文章如下：

[
_https://www.cnblogs.com/backlion/p/9302528.html_](https://www.cnblogs.com/backlion/p/9302528.html)

[ _https://www.freebuf.com/vuls/175451.html_
_s_](https://www.freebuf.com/vuls/175451.htmls)

[
_https://mp.weixin.qq.com/s/VWofHp5lJLYnbw01copnkw_](https://mp.weixin.qq.com/s/VWofHp5lJLYnbw01copnkw)

[
_https://www.freebuf.com/articles/web/97833.html_](https://www.freebuf.com/articles/web/97833.html)

https://www.freebuf.com/articles/web/86007.html

