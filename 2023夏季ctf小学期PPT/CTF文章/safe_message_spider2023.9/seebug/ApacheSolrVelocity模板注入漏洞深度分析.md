**作者：天融信阿尔法实验室  
公众号：<https://mp.weixin.qq.com/s/h9bhovkDoVdq6HHJcoREvg>**

## 1 漏洞分析环境搭建

  * 漏洞分析环境搭建
  * 需要工具
  * IDEA
  * Apache Ant
  * Apache Solr8.2.0源码
  * Apache Solr8.2.0服务端
  * Chrome
  * Burp

## 2 Apache solr简介和漏洞复现

首先先简单介绍一下Apache Solr

Apache Solr是一个强大的搜索服务器，它支持像API一样的REST。
Solr由Lucene提供支持，可以实现强大的匹配功能，例如短语，通配符，连接，分组和更多的各种数据类型。 它是高度优化的高流量使用Apache
Zookeeper。

介绍完Apache Solr之后我们就来复现一下这次的 Apache Solr Velocity服务端模板注入漏洞

我们首先从Apache Solr官网上下载Apache Solr
8.2.0的服务端https://mirrors.tuna.tsinghua.edu.cn/apache/lucene/solr/8.2.0/solr-8.2.0.tgz下载完成之后解压

![](https://images.seebug.org/content/images/2020/01/1173a3bf-19c2-432b-9ba2-434422371711.png-w331s)

我们通过命令行终端进入bin目录然后输入“./solr start”命令!

![](https://images.seebug.org/content/images/2020/01/a9afaaaf-2334-4f69-84e2-c42a91068ff7.png-w331s)

Apache Solr就会默认在本地的8983端口启动服务,

我们访问一下地址 http://127.0.0.1:8983/solr/#/

查看左侧的Core Selector的集合名称!

![](https://images.seebug.org/content/images/2020/01/8a6be154-3767-4555-ab8c-d36bc7e6e348.png-w331s)

使用burp Repeater模块像服务端发包修改指定集合的配置!

![](https://images.seebug.org/content/images/2020/01/bdca60dd-99a7-444d-a7af-5847e210c74b.png-w331s)

修改配置成功

然后发送事先构造好的payload!

![](https://images.seebug.org/content/images/2020/01/81b1b9bf-353e-48e4-b888-9d99e31d86df.png-w331s)

## 3 模板引擎简介

### 3.1 JSP简介

漏洞复现完成，但是分析漏洞我们还需要一些前置知识，比如什么是模板注入漏洞，以及Velocity究竟是什么，

我们都知道，现在web开发讲究的是一个前后端分离的方式，MVC模式就是其经典的代表。如果抛弃前后端分离，仅仅开发一个能用的网站，只需要一个JSP其实就够了，但是这样很明显会导致开发时逻辑及其混乱，以及后期维护起来成本极高的问题，这样的开发完全违背的我们java这么一个面向对象语言优雅的编程思维。

我们在开发一个程序时希望的就是一个模块尽量是独立完成某一个功能而不依赖别的模块的，也就是我们的高内聚，低耦合的思想。

这种思想用到我们的web开发的架构时，就有了我们的MVC模式，即 Mode，

View，Controller。和我们的web三层架构，即表示层，业务逻辑层，和数据接口层。尽量保证每一层都是独立可用的,在这里特别提示一下，web三层架构是java独有的概念，而MVC架构则是通用的。

在这种情况下，每一层都出现了其相对应开源组件。

首先不得不提的两个使用量最高的MVC框架，Struts2，和SpringMVC。

表现层有我们的JSP和Thymeleaf，Velocity，Freemarker等模板引擎

业务层由我们最火热的开源组件Spring

数据层就有我们最常见的Mybaits和Hibernate两个Dao层框架

而这次我们要重点注意的就是位于我们的表现层，也就是我们的Velocity模板引擎。

对于web不太熟悉的同学可能暂时还不能理解什么是模板引擎，或者说模板引擎是做什么用的。但是相信大家都听过JSP，

JSP的全称是Java Server
Package，与普通的静态html页面相比，区别在于我们可以在JSP页面上书写java代码，以实现和用户进行交互，从而达到动态的这么一个效果。

JSP一开始出现的时候是同时兼具前端和后端的作用，也就是说如果只是开发一个勉强能用的java动态网站，jsp其实就足够了。

在JSP出现之前，实现动态页面的效果用的是Servlet的技术，Servlet可以很好的实现接受用户传来的参数并进行处理。但是把数据返回到前端并输出html页面时确异常的麻烦和痛苦。同常需要一行一行的输出html代码，像下面这样

![](https://images.seebug.org/content/images/2020/01/9ccdfe71-f803-4eab-95f9-ba441d4fdc7b.png-w331s)

后来JSP出现了，如果说Servlet是java代码中写HTML的话，那Jsp就是HTML中穿插写java代码了，jsp相比于Servlet来说并不是一个新的技术，jsp是Servlet的一个扩展，其本质仍是Servlet,

我们看一个最简单的JSP页面

![](https://images.seebug.org/content/images/2020/01/139405ba-6b14-4e8f-beb5-578ca9ca0fca.png-w331s)

看起来就是一个普通的HTML页面，为什么我会说jsp的本质是Servlet呢？

当我们将项目编译打成war包部署在Tomcat下时，会放在Tomcat的WebApp目录下，里面有我们的项目后台的java文件编译成的.class文件。同时也有我们的jsp文件。

但是我们的jsp文件是不能直接被解析的，Jsp不像HTML拿来就能直接返返回给客户，因为jsp文件中是包含有java代码的，浏览器又不能解析我们jsp页面上的java代码，所以将jsp编译成浏览器能解析的html页面的工作就交由了我们的Tomcat来做

当我们启动Tomcat时第一次访问我们的这个jsp页面，往往速度都会稍微慢一些，往后在访问时速度就会很快。这是因为，第一访问时，Tomcat会在他的根目录的work/Catalina/localhos目录下生成我们对应项目名称的一个文件夹。

并生成一个名称为org.apache.jsp的一个package，我们去观察一下!

![](https://images.seebug.org/content/images/2020/01/136abd64-a7a1-40d0-902d-b938d037bedf.png-w331s)

我们可以看到一个java文件和一个.class文件。还记得我刚刚才说过jsp的本质其实就是Servlet么？我们点开这个java文件来一探究竟。

![](https://images.seebug.org/content/images/2020/01/443fa9be-bd7e-49b3-ab3a-00f777c54beb.png-w331s)

我们从中观察到这这么几个重点

![](https://images.seebug.org/content/images/2020/01/1d396586-fb30-4ba1-bad2-1daa3125d112.png-w331s)

首先这是一个java类，它继承了HttpJspBase类同时实现了两个接口

第二个重点在这里

![](https://images.seebug.org/content/images/2020/01/a5e7523c-dd54-4b66-a60c-1ac5caceb1a3.png-w331s)

这是一个静态代码块，静态代码块在类进行加载时就会执行，先于构造代码块和构造方法，是一个java类中最先被执行的代码。

我们根据其代码内容不难看出这静态代码块的作用是用来import Java类的。

接下来是一个名叫_jspService的函数，是不是特别像servlet的doGET和doPost方法？

![](https://images.seebug.org/content/images/2020/01/04eb64bc-aad2-4b61-890f-5dd0b4f496ab.png-w331s)

最后我们在看这里

![](https://images.seebug.org/content/images/2020/01/e86d7873-f31d-430f-bc3d-ae14ec6dea80.png-w331s)

我们发现我们之前看到的jsp文件中的html内容，在这里被替换成了通过

JspWriter对象一句一句的写出的。

此时是不是理解了我之前说的，Jsp的本质就是servlet。表面上上我们是在一堆HTML标签中插入了一个又一个的java代码，本质上Tmocat在接收到客户端对我们这个jsp的请求后，会将我们的整个jsp文件编译成java文件在编译成.class文件。将HTML一句一句通过JspWriter对象的write方法一行一行的输出。

### 3.2 Velocity模板引擎简介

讲解了JSP的基础知识后不知道大家有没有发现一个问题就是，Jsp虽然说是模板引擎的一种，但是如果只做为一个为前端服务的模板引擎来说，它的功能过于强大了，导致它不光可以书写前端页面，因为JSP可以毫无阻碍地访问底层的
Servlet API 和 Java 编程语言，所以同时也可以无缝书写后端的逻辑代码，在展示数据的同时也可以对数据进行处理。

这样就导致前端和后端完全就纠缠在了一起。完全违背了我们MVC的设计思想，你能想象一个前端页面是用Servlet输出，而后端代码使用Jsp来写的网站该怎么去维护么？

面向对象的优雅思想在这一刻荡然无存。

面向对象的核心思想就是，低耦合，高内聚。每一个模块的功能尽可能单一，尽可能的降低和别的模块和功能之间的耦合度。

所以Thymeleaf，Velocity，Freemarker等优秀模板引擎就一个接一个的出现了。

Velocity为主我们来了解，这个在MVC设计模式中，为View层服务的优秀模板引擎。

刚才通过对Jsp的介绍，我们理解了，一个模板引擎他的主要功能就是负责将后端代码也就是servlet处理完成的数据，提取并按照之前写好的样式展示出来。

Velocity是一个基于java的模板引擎（template engine）。它允许任何人仅仅使用简单的模板语言（template
language）来引用由java代码定义的对象。

当Velocity应用于web开发时，界面设计人员可以和java程序开发人员同步开发一个遵循MVC架构的web站点，也就是说，页面设计人员可以只关注页面的显示效果，而由java程序开发人员关注业务逻辑编码。Velocity将java代码从web页面中分离出来，这样为web站点的长期维护提供了便利，同时也为我们在JSP和PHP之外又提供了一种可选的方案。

前面说了这么多，现在我们在这里简单演示下Velocity这个模板引擎，给大家一个更直观的概念。

首先导入以下的包

![](https://images.seebug.org/content/images/2020/01/9d1e7dc4-f60d-48d0-a2fa-387aaeeba25a.png-w331s)

然后我们创建一个演示类

![](https://images.seebug.org/content/images/2020/01/d2ccaf9d-ed10-446a-9161-43ff81335f86.png-w331s)

这里我们首先实例话了一个VelocityEngine，并设置加载加载classpath目录下的vm文件

然后初始化VelocityEngine，接着就是加载一个模板，这里模板的名字叫“Hellovelocity.vm”
接下来的操作就是我们向模板的上下文中添加我们要传递的参数和值了。

最后的t.merget就会开始循环遍历生成的Velocity AST语法书的各个节点，执行每个节点的渲染方法。

我们看一下我们加载的这个模板的具体实现

![](https://images.seebug.org/content/images/2020/01/01b9a048-65ea-4a6f-9ad6-053a6601d533.png-w331s)

和最终的执行结果

![](https://images.seebug.org/content/images/2020/01/e5d4f6cc-e5d2-42ee-a4f1-0ca935cacb86.png-w331s)

我们看到这里可以将我们之前后端代码中传输的值直接取出也可以循环取出。

这样我们就可以提前将静态部分用HTML和JavaScript写好，然后需要动态交互的部分就可以使用Velocity语法来进行编写。

## 4 漏洞和POC构造分析

### 4.1 漏洞分析环境搭建

首先我们下载Apache Slor 8.2.0源码

https://mirrors.tuna.tsinghua.edu.cn/apache/lucene/solr/8.2.0/solr-8.2.0-src.tgz

下载完成后

我们进入Solr源码根目录

执行命令

ant ivy-bootstrap

![](https://images.seebug.org/content/images/2020/01/dfa67499-3be3-4a8c-bf3e-4dca1081b815.png-w331s)

然后再执行ant idea命令将源码转化成idea可以导入的模式!

![](https://images.seebug.org/content/images/2020/01/11748391-3255-464f-af75-52fce9c81192.png-w331s)

然后我们打开idea，选择open!

![](https://images.seebug.org/content/images/2020/01/56c736d7-c68d-450a-b1a1-7405b2a6b66d.png-w331s)

最后导入完成后的样子

![](https://images.seebug.org/content/images/2020/01/126cc748-6dac-497d-a86c-be8a6b96f54e.png-w331s)

为了可以调试源码，我们需要再做一些配置

点开左上角的Edit Configuration

![](https://images.seebug.org/content/images/2020/01/da711da8-8063-42c6-9a6e-a5ae8fc7bffa.png-w331s)

然后新增Remote

![](https://images.seebug.org/content/images/2020/01/a6110401-8069-4a8f-9316-b6c5292f9e35.png-w331s)
并按照如下配置

![](https://images.seebug.org/content/images/2020/01/f6de064a-72b4-4878-b38e-cf6afb969f37.png-w331s)

配置完成后我们进入solr的服务端的bin目录，并执行如下命令

![](https://images.seebug.org/content/images/2020/01/eaadb750-cc6a-4c99-ae1a-3fcb70e5754f.png-w331s)

![](https://images.seebug.org/content/images/2020/01/8fffb783-a10d-47ae-958c-0dc6d612d979.png-w331s)

然后我们带idea中点击debug按钮，当有如下显示时代表调试环境搭建成功

![](https://images.seebug.org/content/images/2020/01/a1a50ca4-d169-431d-8bf2-54c721c3364d.png-w331s)

接下来我们就可以在自己想下断点的地方下断点了。

### 4.2 POC第一部分执行和构造分析

首先我们就来一步一步分析这个漏洞吧，审计一个web项目我们首先先看有没有web.xml这个文件

![](https://images.seebug.org/content/images/2020/01/c3d83ea1-96b5-4001-9181-03b3c868f57c.png-w331s)

我们找到了web.xml这个文件，位置在solr/webapp/WEB-INF/目录下

我们打开看一下内容

首先这个web.xml文件一开始就是一个filter过滤器，这个过滤器类路径是

org.apache.solr.servlet.SolrDispatchFilter，拦截的范围是所有请求

![](https://images.seebug.org/content/images/2020/01/8ca0265c-353f-48d1-b332-770ae04e81ec.png-w331s)

所以我们首先就需要去这个SolrDispatchFilter这个类去观察

此时我们有两条分析接下来漏洞走向的方式，我们通过查阅网上的资料得知

![](https://images.seebug.org/content/images/2020/01/74564515-a448-49c2-8d82-064b9d089d21.png-w331s)

我们去目录下查看一下

![](https://images.seebug.org/content/images/2020/01/a009f6f2-fa64-4da7-9dee-2013b91d6970.png-w331s)

果然有这两个文件

然后我们看下两个文件的部分内容，先看下solrconfig.xml

![](https://images.seebug.org/content/images/2020/01/b145f3c4-6730-4847-86cc-cbf04b275434.png-w331s)

可以看到velocity.params.resource.loader.enabled参数默认是flase，也就是说是默认是不开启的。

我们在看一看configoverlay.json文件

![](https://images.seebug.org/content/images/2020/01/ed0d273f-22e6-4a0b-818d-58da7fef398c.png-w331s)

看到这里存储着我们上传上来的参数，这里我们将params.resource.loader.enabled制为true

我们可以通过观察该文件何时被修改来判断，是否该跟进代码中。

然后我们观察poc的时候不难发现请求的API为“/config”

我们通过查阅资料发现

![](https://images.seebug.org/content/images/2020/01/c5d96e01-3437-4401-b678-0bccccb20c01.png-w331s)

Solr中有很多的RequestHandler，默认配置在solrconfig.xml中，同时也有很多没有配置在solrconfig.xml，称为隐式RequestHandler。而“/config”就是其中之一，我们可以看到SolrConfigHandler便是处理提交我们提交poc的API之一

但是为了，讲的更加清晰，我们还是从SolrDispatchFilter.doFilter方法来一步一步的跟踪。

首先SolrDispatchFilter.doFilter方法执行到第 423行的时候，

会调用HttpSolrCall.call方法

![](https://images.seebug.org/content/images/2020/01/a4aff3a3-f36f-4f9e-b92e-93d9d2ac7ff3.png-w331s)

我们跟进这个方法

然后代码执行到execute()方法时configoverlay.json文件更新了 所以我们跟进这个函数继续跟进

![](https://images.seebug.org/content/images/2020/01/c2d197b0-d2f7-4ddf-8d85-783ce6041725.png-w331s)

![](https://images.seebug.org/content/images/2020/01/a4cae648-0727-47c8-9765-1fd170aaa1ee.png-w331s)

按照上面的思路，执行到handler.handleRequest()继续跟进

![](https://images.seebug.org/content/images/2020/01/85b0d27a-aad2-438e-96b4-2ea9bcbce826.png-w331s)

![](https://images.seebug.org/content/images/2020/01/c61838f6-b78f-4c7b-bf8a-a6f32e81c5c3.png-w331s)

此时就进入到了一开始我们从资料中所看到的“/config”所对应的类SolrConfigHandler

![](https://images.seebug.org/content/images/2020/01/434af0df-5643-4e71-b7a2-8f80e5271d5d.png-w331s)

由于此时进入这个函数是为了调用它的handleRequestBody方法，所以我们接着向下执行

这里POST用来修改数据。GET用来查询数据，所以我们执行到

command.handlePOST()方法然后跟进

![](https://images.seebug.org/content/images/2020/01/ede125be-80c1-4814-8eb8-2399abe0ffbf.png-w331s)

执行到handleCommands()方法 此时传入的opsCopy就是我们从前端传入的配置信息，而overlay时当前的配置信息

![](https://images.seebug.org/content/images/2020/01/0da8502a-0602-4569-b33c-ab3900271cd4.png-w331s)

继续跟进，当执行到SolrResourceLoader.persistConfLocally()方法时

configoverlay.json，文件更新了

![](https://images.seebug.org/content/images/2020/01/d6375704-6444-4d7b-bed4-e2cf09614d8c.png-w331s)

此时我们看到，关键参数时overlay.toButeArray()

![](https://images.seebug.org/content/images/2020/01/6328f331-b048-4ca2-a59f-7dad7d5e824d.png-w331s)

而overlay参数最近的一次赋值动作是在这行代码里进行的，我们先跟进updateNamedPlugin()方法看一看

![](https://images.seebug.org/content/images/2020/01/5f21f0e3-ca65-4b02-a65e-172e0f78c55d.png-w331s)

updateNamedPlugin方法中将op 和overlay参数都传入了进去

当执行到这个if判断时，判断为真，返回overlay，所以关键在于

Verifyclass()这个函数。

这里op仍然为我们 post传入的配置参数 clz的值为“solr.VelocityResponseWriter”

继续跟进

![](https://images.seebug.org/content/images/2020/01/2fabe6dc-5721-44af-bb18-47b0490ed833.png-w331s)

跟进函数之后我们看到这样一行代码

![](https://images.seebug.org/content/images/2020/01/16045270-a384-4b9d-ac99-cf0339dfefc9.png-w331s)

根据执行逻辑首先执行getCore方法，返回一个SolrCore对象

![](https://images.seebug.org/content/images/2020/01/24070500-f70f-4e4f-9261-8f91d7359fd9.png-w331s)

![](https://images.seebug.org/content/images/2020/01/597955d2-6c90-4a71-aac6-273b368cd373.png-w331s)

然后执行op.getDataMap()方法，返回一个Map对像

![](https://images.seebug.org/content/images/2020/01/1f937469-6ea2-4a42-ba4a-e62267d7f02a.png-w331s)

![](https://images.seebug.org/content/images/2020/01/ab63634c-3878-46d4-9e7d-3947727686af.png-w331s)

然后new 一个PluginInfo对象，构造方法里的主要操作就是向一个 NameList类型的对象中存值，存入的是我们POST传入的配置参数

![](https://images.seebug.org/content/images/2020/01/e28222df-d772-4f3d-80d2-0e99fb691b92.png-w331s)

![](https://images.seebug.org/content/images/2020/01/4ca9cddf-a32f-4591-9aef-b06e23779b6b.png-w331s)

![](https://images.seebug.org/content/images/2020/01/ce3f2385-b0ea-472b-a6aa-2e7e02a1d62b.png-w331s)

createInitInstance()方法

![](https://images.seebug.org/content/images/2020/01/b35bd254-f0a3-4d41-8ee9-19f05ba7dd54.png-w331s)

泛型变量o是根据我们传入的参数PulginInfo对象的className属性“solr.VelocityResponseWriter”然后通过createInstance()方法反射获得的VelocityResponseWriter对象

因为VelocityResponseWriter对象实现了NamedListInitializedPlugin接口

![](https://images.seebug.org/content/images/2020/01/78cd5e67-7762-4498-85e9-37e51ab84a4d.png-w331s)

所以执行

![](https://images.seebug.org/content/images/2020/01/715f722a-e23c-4254-a5d9-b8d905dbce68.png-w331s)

跟进

然后我们进入了VelocityResponseWriter对象的init方法，在这里有这么几行代码

![](https://images.seebug.org/content/images/2020/01/fc61cdaa-61b2-4f83-bff0-e6babef935f3.png-w331s)

可以看到在这里我们将VelocityResponseWriter对像的两个重要属性

paramsResourceLoaderEnabled，

solrResourceLoaderEnabled

设置为了true，也就是允许我们上传自定义模板了

紧接着init方法执行结束后，就会将VelocityResponseWriter对象按原路返回到SolrConfigHandler并赋值给overly属性

![](https://images.seebug.org/content/images/2020/01/78d2ecdf-68ac-4303-b76e-3e5d0e4bb1e8.png-w331s)

紧接着执行到第504行代码时configoverlay.json文件更新了，我们跟进这个方法

![](https://images.seebug.org/content/images/2020/01/728cdaa8-ea95-48ca-a56b-12e31b5f9f90.png-w331s)

在调用SolrResourceLoader.persistConfLocally()方法时，可以看到我们将

overly作为参数传递了进去

![](https://images.seebug.org/content/images/2020/01/945a04b0-7069-4dae-9a9a-54c956f25c7c.png-w331s)
此时观察代码我们就明白了，真正将我们post传递的配置参数写入文件的操作是在这一步进行的。至此 poc的第一部分追踪完毕。

### 4.3 POC第二部分执行和构造分析

接下来是poc执行的第二阶段

老规矩先从SolrDispatchFilter类看起

执行到HttpSolrCall.call步入

![](https://images.seebug.org/content/images/2020/01/fd5f95e0-ddef-410f-bf5b-2877e1e58847.png-w331s)

紧接着执行到HttpSolrCall.writeResponse方法

![](https://images.seebug.org/content/images/2020/01/e985f25d-de82-45d2-9563-3cfa686da753.png-w331s)

观察此刻传入的三个参数，solrRsp参数是一个 SolrQueryResponse对象，我们GET传入的playload存储在该对象的value属性中

![](https://images.seebug.org/content/images/2020/01/2524b01e-58a1-429a-9b20-0fd3a165bfe3.png-w331s)

这个responseWriter对象相当重要，这里我们看到了两个参数

paramsResourceLoaderEnabled和solrResourceLoaderEnabled

这是我们poc第一步中修改的两个配置属性，只有这两个属性为true我们才可以上传自定义模板成功

![](https://images.seebug.org/content/images/2020/01/e8bae755-3415-4986-94da-40059fdf4882.png-w331s)

responseWriter参数指向的是一个VelocityResponseWriter对象，responseWriter最近一次被赋值是在，下面这行代码中

![](https://images.seebug.org/content/images/2020/01/af5bb70a-0c37-4ca1-b4a1-da426a2d002e.png-w331s)

本着刨根问底，以及锻炼我们分析代码执行逻辑能力的目的，我们深入了解一下

我们跟踪进HttpSolrCall.getResponseWriter方法

![](https://images.seebug.org/content/images/2020/01/8ad61f28-2de3-40e1-ab0e-b24b87feb856.png-w331s)
可以看到，这里将我们GET穿入的key的值为wt的属性里面的值velocity取出并作为参数传给了core.getQueryResponseWriter方法，core参数指向的是一个SolrCore对象

![](https://images.seebug.org/content/images/2020/01/e43cb687-9cd6-444c-8341-9695a0e86eaf.png-w331s)

跟入SolrCore.getQueryResponseWriter方法

![](https://images.seebug.org/content/images/2020/01/9a3a4d59-9ae3-4e61-803c-0d4650589473.png-w331s)

跟入responseWriters.get方法

此时我们来到了一个PluginBag对象的get方法

![](https://images.seebug.org/content/images/2020/01/23d4dcfc-0e51-41d8-8e0f-0b75213a4ee3.png-w331s)

在执行完T result = get(name)方法后 result的结果中是一个VelocityResponseWriter对象且

paramsResourceLoaderEnabled和solrResourceLoaderEnabled属性都已被置为true，就是说给这两个属性赋值的操作就在get(name)这个方法里。继续跟进

![](https://images.seebug.org/content/images/2020/01/45853ac6-8127-4be6-88be-1e4ff26e398a.png-w331s)

还是继续跟进result的无参get方法

![](https://images.seebug.org/content/images/2020/01/ec854d1a-2136-4de1-a4a3-b4d0b358d58d.png-w331s)

到这里，就出现问题了

这里会判断一个名字叫lazyInst的属性是否为空，如果不为空，则返回这个属性

![](https://images.seebug.org/content/images/2020/01/0779bfcc-eb28-4fcd-a0ca-149c500a0ff4.png-w331s)

我们来看看此时这个lazyInst属性是什么，

![](https://images.seebug.org/content/images/2020/01/5468b0cf-72b0-4d2e-9984-f1103378e683.png-w331s)

可以看到就是我们最终返回的VelocityResponseWriter对象。

那么问题就来了，我们这执行过程中并没有看到lazyInst对象被赋值，那么lazyInst属性指向的VelocityResponseWriter对象是哪来的呢？

我们会退一步，观察这行代码

PluginHolder result = registry.get(name);

![](https://images.seebug.org/content/images/2020/01/16100b94-f199-4364-ab8e-017f8d181355.png-w331s)

registry是一个hashmap类型，有final标识符

![](https://images.seebug.org/content/images/2020/01/ad79a087-23cb-4d72-9ee4-6d43c986f543.png-w331s)

观察此时registry里面的内容

![](https://images.seebug.org/content/images/2020/01/e314e402-d76a-46c1-b356-f09bd50ceb7d.png-w331s)

又因为registry.get(name)传入的name参数的值为velocity

我们打开这里的velocity

![](https://images.seebug.org/content/images/2020/01/5ae9141d-e164-4498-848a-4b5a1c11ccbb.png-w331s)

赫然看到那个lazyInst就在里面，我们知道标示的final的属性就是常量了，在对像生成被赋值了一次以后就不会再更改了。我通过多次发送poc请求测试发现每次到这个断点时当前的对象ID都是相同的，所以每次执行调用的都是同一个对像。

我们重新发送poc的第一部分。Poc第一部分请求完成后再在此处下断点

![](https://images.seebug.org/content/images/2020/01/d4424027-719e-4c01-9d30-1a9f970422e4.png-w331s)

此时lazyInst属性就为空了

我们继续执行

![](https://images.seebug.org/content/images/2020/01/7a0eef8b-8d55-4e00-9f7e-253dac7cfa7a.png-w331s)

此时由于lazyInst为空了，所以不会直接返回，我们跟进createInst方法，

看到在createInst方法的最后lazyInst属性被赋值，我们向上寻找这个localInst变量

![](https://images.seebug.org/content/images/2020/01/e807e98a-1b4c-4bd2-921e-44e78cac5843.png-w331s)

在下面这行代码中localInst第一次被赋值

![](https://images.seebug.org/content/images/2020/01/a783fb94-2065-4754-986b-91e0a369d559.png-w331s)

此时localInst中的内容为

![](https://images.seebug.org/content/images/2020/01/5d02d3e7-077b-420c-9029-34356f1bd29c.png-w331s)

也就是说此时程序只是从solrconfig.xml中读取了默认的配置，还并没有读取

configoverlay.json中我们更新的配置。

所以这行就不跟进了。

![](https://images.seebug.org/content/images/2020/01/76045fb0-2499-436d-94be-7799e1f6f379.png-w331s)

我们清楚的看到参数被更新了，那我们就跟入这行代码

![](https://images.seebug.org/content/images/2020/01/8272923d-26d9-460e-8600-546955b268d9.png-w331s)

跟入((NamedListInitializedPlugin) inst).init(info.initArgs)

![](https://images.seebug.org/content/images/2020/01/592fe662-4b6d-4b78-889a-4a06bb923145.png-w331s)

然后就又看到了我们执行poc第一部分时所碰到的代码了，至此获取

configoverlay.json中我们更新的配置信息的执行逻辑我们已经分析完毕

![](https://images.seebug.org/content/images/2020/01/661fd7dc-f723-488d-ac3b-3abb5646a03b.png-w331s)

接下来继续原路返回到我们调用HttpSolrCall.getResponseWriter的位置

![](https://images.seebug.org/content/images/2020/01/8627eea8-9c28-4881-9bf9-578e8f6eda69.png-w331s)

继续跟进writeResponse(solrRsp, responseWriter, reqMethod);

此时solrRsp中存放的是我们Get传入的poc，responseWriter中存放的是我们configoverlay.json文件中存放的更新配置。

跟入QueryResponseWriterUtil.writeQueryResponse方法

![](https://images.seebug.org/content/images/2020/01/dd0bf669-e056-40f4-89e7-0f8720b1ae63.png-w331s)

跟入responseWriter.write方法

![](https://images.seebug.org/content/images/2020/01/e8bfca76-df36-42a2-a054-f38685540511.png-w331s)

我们执行createEngine()方法时生成了一个VelocityEngine对象

![](https://images.seebug.org/content/images/2020/01/cb9e89d3-e06b-4175-972d-b56b3736a677.png-w331s)

我们进入createEngine()方法后可以看到方法内的第一行代码就是new一个VelocityEngine对象

![](https://images.seebug.org/content/images/2020/01/0755ef14-43db-47bd-8550-e72aeb6d1df0.png-w331s)

关键点在以下这几行代码，这里对

paramsResourceLoaderEnabled

solrResourceLoaderEnabled两个参数进行了判断，当

paramsResourceLoaderEnabled参数为true时执行

loaders.add("params");

engine.setProperty("params.resource.loader.instance", new
SolrParamResourceLoader(request));

![](https://images.seebug.org/content/images/2020/01/ced3ea45-c6c8-4c9a-9547-c83546f9d9d3.png-w331s)

根据网上查到的资料我们可以看到params.resource.loader.instance这个属性的含义

![](https://images.seebug.org/content/images/2020/01/5cbce4ed-59b4-4ece-946d-48dc55526c39.png-w331s)

也就是说当开启这个属性的时候，我们就可以通过Solr来上传我们自定义的模板了。

最后返回VelocityEngine对象

![](https://images.seebug.org/content/images/2020/01/dc8bcb12-0a35-4d5c-a863-958d2d36fc93.png-w331s)

返回到responseWriter.write方法，继续执行到

Template template = getTemplate(engine, request);

![](https://images.seebug.org/content/images/2020/01/6f16f617-899f-4cb7-a417-3a7159f0428a.png-w331s)

这里我们生成了一个template

跟进去后我们看到

![](https://images.seebug.org/content/images/2020/01/962ba519-a50a-4356-b18d-b090e286958f.png-w331s)

从我们Get传入的参数中获取V.template作为模板的名字

![](https://images.seebug.org/content/images/2020/01/686ca02e-0a62-475b-a0f2-7b32a2bcd573.png-w331s)

![](https://images.seebug.org/content/images/2020/01/0d4e2d5b-ad3f-48c5-a7fe-e233e9a436f8.png-w331s)

同时将我们传入的Poc也就时Velocity模板语句解析成AST抽象语法树

这里就要对velocity的AST抽象语法树做一下简单的介绍了

在计算机科学中，抽象语法树（abstract syntax tree 或者缩写为 AST），或者语法树（syntax
tree），是源代码的抽象语法结构的树状表现形式，这里特指编程语言的源代码。树上的每个节点都表示源代码中的一种结构。

之所以说语法是「抽象」的，是因为这里的语法并不会表示出真实语法中出现的每个细节。

Velocity是通过JavaCC和JJTree生成抽象语法树的,

javaCC
是一个能生成语法和词法分析器的生成程序。语法和词法分析器是字符串处理软件的重要组件，[javacc](http://www.google.com/url?sa=t&ct=res&cd=1&url=https%3A%2F%2Fjavacc.dev.java.net%2F&ei=9DVYRYiNNqOEpgKyrbivCQ&usg=__mFYMOj71sh29a1K1V8lPTOwCBok=&sig2=hEpGu_jpqYUmHxmOExyoMg)是类似lex/yacc的parser生成器，可以把一段文本转换为抽象语法树（AST）。

JJTree是javaCC的预处理器，用于在JavaCC生成的源代码中的各个地方插入表示语义动作的分析树

用网上的一张图来介绍一下AST的一些节点

![](https://images.seebug.org/content/images/2020/01/f58ac2d2-faf8-4ec9-9484-01e1ab666c9e.png-w331s)

Velocity的语法相对简单，所以它的语法节点并不是很多，总共有50几个，它们可以划分为如下几种类型。

  1. 块节点类型：主要用来表示一个代码块，它们本身并不表示某个具体的语法节点，也不会有什么渲染规则。这种类型的节点主要由ASTReference、ASTBlock和ASTExpression等组成。

  2. 扩展节点类型：这些节点可以被扩展，可以自己去实现，如我们上面提到的#foreach，它就是一个扩展类型的ASTDirective节点，我们同样可以自己再扩展一个ASTDirective类型的节点。

  3. 中间节点类型：位于树的中间，它的下面有子节点，它的渲染依赖于子节点才能完成，如ASTIfStatement和ASTSetDirective等。

  4. 叶子节点：它位于树的叶子上，没有子节点，这种类型的节点要么直接输出值，要么写到writer中，如ASTText和ASTTrue等。

我们再来看一下poc中的Velocity语句，和children中的节点信息

#set($x='')

#set(x.class.forName('java.lang.Runtime'))

#set(rt.getRuntime().exec('open /Applications/Calculator.app/'))

![](https://images.seebug.org/content/images/2020/01/a11ef5fc-67d5-44ef-917c-8218c9670260.png-w331s)

#set最终被解析为Velocity AST语法树中的ASTSetDirective类，根据上面的Velocity
AST语法树的图我们看到ASTSetDirective节点有两个字节点

分别是ASTReference,和ASTExpression,

![](https://images.seebug.org/content/images/2020/01/f8537831-20ef-4c94-ade0-1a4806e75e11.png-w331s)

我们看到下标为0的ASTSetDirective类中有两个属性。right和left

分别代表了$x=''中“=”号的两边，左边的ASTReference有两种可能，

一就是用来进行赋值操作的变量名

例：#set( $iAmVariable = 'good!')将字面量“good”赋值给名字为iAmVariable的变量

第二种也是赋值操作，但是赋值操作的目标是一个对象的某个属性

例：#set($Persion.name = 'kkk')

这种赋值方式的本质其实是调用Persion的setName方法。

区分这两种赋值方式我们可以动过观察此时的ASTReference这个节点是否有子节点来判断

譬如第一种#set( $iAmVariable = 'good!') 我们观察一下

![](https://images.seebug.org/content/images/2020/01/36a7c234-74f3-4b4d-8003-44fece528b10.png-w331s)

可以看到最后的children属性为空

再观察第二种#set($Persion.name = 'kkk')

![](https://images.seebug.org/content/images/2020/01/a99393cd-f5ef-4de4-a154-d26438632476.png-w331s)

可以看到children属性中，是有子节点的。

Velocity通过ASTReference类来表示一个变量和变量的方法调用，ASTReference类如果有子节点，就表示这个变量有方法调用，方法调用同样是通过“.”来区分的，每一个点后面会对应一个方法调用。ASTReference有两种类型的子节点，分别是ASTIdentifier和ASTMethod。它们分别代表两种类型的方法调用，其中ASTIdentifier主要表示隐式的“get”和“set”类型的方法调用。而ASTMethod表示所有其他类型的方法调用，如所有带括号的方法调用都会被解析成ASTMethod类型的节点。

所谓隐式方法调用在Velocity中通常有如下几种。

1.Set类型，如#set($person.name=”junshan”)，如下： \- person.setName(“junshan”)

  * person.setname(“junshan”)

  * person.put(“name”,”junshan”)

2.Get类型，如#set(person.name)中的$person.name，如下：

  * person.getName()

  * person.getname()

  * person.get(“name”)

  * person.isname()

  * person.isName()

接下来我们来看ASTText节点，我们从节点图中看到ASTText没有任何子节点了，它是一个叶子结点，所以这种类型的节点要么直接输出值，要么写到writer中。

![](https://images.seebug.org/content/images/2020/01/ece4ce5b-2622-435c-844e-427bbb2e4ed2.png-w331s)

到这里我们简单介绍了下Velocity AST语法树的一些基础知识。接下来我们回归我们程序的执行逻辑。

接下来的velocity模板引擎的执行逻辑现在这里简单说明一下，其实也很简单，其实就是会不停的遍历和执行各个子节点中的render方法

首先根据Velocity AST语法树的那张图，我们看到总的根节点是ASTprocess

所以会首先调用ASTprocess的render方法，具体在哪里调用呢，我们来看代码

![](https://images.seebug.org/content/images/2020/01/c9ddef91-e5aa-4ad0-9091-3e85fcb0c406.png-w331s)

继续跟入

![](https://images.seebug.org/content/images/2020/01/f20bc5f9-126b-42ca-a0a0-ec8f68dd0ee7.png-w331s)

当执行到((SimpleNode)data).render(ica,writer);

这行代码是，我们可以看到此时的data就是ASTprocess节点，所以Template.merge方法中调用了AST的根节点(ASTprocess)的render方法((SimpleNode)data).render(ica,writer);。此调用将迭代处理各个子节点render方法。如果是ASTReference类型的节点则在render方法中会调用execute方法执行反射替换相关处理。

![](https://images.seebug.org/content/images/2020/01/f14abc84-4edd-4f0d-84f2-4d9d4a22a515.png-w331s)

当进入到ASTprocess节点的render方法后会根据深度优先遍历算法开始遍历整棵树，遍历算法如下

![](https://images.seebug.org/content/images/2020/01/bb47a2d7-b358-47e6-8fcc-16de7dec0bed.png-w331s)

即依次执行当前节点中的所有子节点的render方法，而每个节点的具体渲染规则都在其对应节点的render方法中实现。

这里我们可以打印一下我们poc所生成的语法树的详细结构

![](https://images.seebug.org/content/images/2020/01/b3ac7e4e-f3ab-4da1-a82f-a88060607c88.png-w331s)

有了这个语法树结构后，程序的执行顺序就相当清晰了。

我们首先调用了ASTSetDirective类的render方法，看到该方法中首先调用了ASTExpression类value方法。

![](https://images.seebug.org/content/images/2020/01/889d45e1-ef85-4893-a03f-64b5479926c4.png-w331s)

而ASTExpression类value方法中又调用了它的子节点ASTStringLiteral

节点的value方法

![](https://images.seebug.org/content/images/2020/01/b6c94ba2-1ad1-429b-9e3d-f49c98a78959.png-w331s)

最后ASTStringLiteral类的value方法返回一个字面量

![](https://images.seebug.org/content/images/2020/01/a1334158-d857-4760-b5b5-e1eaf94e566e.png-w331s)

接着返回到ASTSetDirective类执行它的第二个子节点也就是等号左边的$x

这里对应的是ASTReference类，这里是调用了ASTReference类的setValue方法

![](https://images.seebug.org/content/images/2020/01/fc023502-895f-456d-b831-dc30b0cce0e9.png-w331s)

跟入方法后可以看到，由于该ASTReference节点没有子节点了，所以

直接执行

context.put(rootString, value);这里的value就是我们刚刚获得的“=”号右边的字面量!

![](https://images.seebug.org/content/images/2020/01/7c291658-9790-4192-a04a-adec7b226a45.png-w331s)

我们跟进去看一眼，能看得出后续就是赋值操作了，就不继续深入了

![](https://images.seebug.org/content/images/2020/01/4f5d1c95-2b2b-4924-b1e5-338f10180e28.png-w331s)

Poc第一行#set($x='')执行完毕

然后开始遍历第二个节点

第二个节点是ASTText节点，这个没什么好说的，就只是直接输出或着写到write中

![](https://images.seebug.org/content/images/2020/01/3efeef51-f9aa-40c4-896b-a078fb574dec.png-w331s)

然后开始遍历第三个节点

第三个节点仍然是ASTSetDirective类，它的render方法中仍然是先执行“=”号右边的子节点ASTExpression类的value方法

当执行到该方法时我们可以看到，此时的ASTExpression节点还有一个子节点，但是不是ASTStringLiteral节点了，而是ASTReference节点

![](https://images.seebug.org/content/images/2020/01/7e05496b-d8ba-4646-8970-7786cdea216c.png-w331s)

所以此次执行的将会是ASTReference类的value方法

![](https://images.seebug.org/content/images/2020/01/3cf213ed-e1e5-40ae-8c2d-f5f0e259146a.png-w331s)

执行execute方法

我们重点看execute中的这行代码

Object result = getVariableValue(context, rootString);

这里返回的是我们给$x所赋的值“”然后程序会判断该值是否为空

如果一开始我们没有执行#set(x赋一个值的话，此时会执行下面的

EventHandlerUtil.invalidGetMethod()方法，该方法会因为$x的值为空而不会向下继续执行。

所以我们poc的第一步就需要先为一个变量赋值，赋任何值都可以。

![](https://images.seebug.org/content/images/2020/01/a9094790-0d50-4fc6-a05f-3371741f09c7.png-w331s)

接下来执行到下面这些代码时，就开始遍历当前ASTReference的两个子节点

![](https://images.seebug.org/content/images/2020/01/1a643a5d-20a5-4e0b-ab71-2ede31d289de.png-w331s)

![](https://images.seebug.org/content/images/2020/01/71cd6380-08ae-405b-82c0-9a949e3a3a91.png-w331s)

执行完ASTIdentifier类的execute返回一个Class对象

![](https://images.seebug.org/content/images/2020/01/9f8f4e11-1fdd-4e1f-af19-2f8afb9fb9be.png-w331s)

接下来就是遍历第二个节点也就是ASTMethod节点，

执行ASTMethod节点的execute方法。

Execute方法中执行了method的invoke方法跟入

![](https://images.seebug.org/content/images/2020/01/1ea5bdb5-cf21-4784-8e02-ba4521ef7fb5.png-w331s)

最调用doInvoke方法

![](https://images.seebug.org/content/images/2020/01/aed1c1c8-e320-49b8-9855-6360d73ab1ee.png-w331s)

我们看一下doInvoke方法的内容

![](https://images.seebug.org/content/images/2020/01/4fc82137-268c-4c43-bc38-cbcdef8c35c5.png-w331s)

这一路下来的反射调用到最终获取Runtime类的class对象我用更直观的方式重写了一下方便理解

![](https://images.seebug.org/content/images/2020/01/73dfcf25-c3ef-4202-ad3b-3b65f7d3b8f2.png-w331s)

这一系列的操作等同于Class.forName("java.lang.Runtime")

后面的poc的第三行

#set(rt.getRuntime().exec('open /Applications/Calculator.app/'))

执行逻辑和上面的如出一辙，就不再深入分析了，感兴趣的朋友可以自己跟踪代码分析一下。

最后放一下最终的一个调用链

![](https://images.seebug.org/content/images/2020/01/20503c98-3f72-4039-a2c3-98e7fc86826a.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1107/>

