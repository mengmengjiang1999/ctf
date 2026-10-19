## **国内的一些知名网络资产测绘搜索引**

在我们进行渗透及平时的漏洞挖掘中，都需要获取目标的一些信息、某一个系统漏洞的全球分布情况等等，这些都可以通过资产测绘引擎来获取。

###  **[Fofa](https://fofa.so/ "链接")**  

官方介绍

  * FOFA 是白帽汇推出的一款空间搜索引擎，它通过进行空间测绘，能够帮助研究人员或者企业迅速进行网络资产匹配，例如进行漏洞影响范围分析、应用分布统计、应用流行度排名统计等。

![](https://image.3001.net/images/20210613/1623591555_60c60a83d57126449b91f.png!small)

### [Quake ](https://quake.360.cn/ "链接")  

官方介绍

  * Quake是360安全响应中心（360-CERT）自主设计研发的全球空间测绘系统，能够对全球IPv4、IPv6地址进行持续性探测，实时感知全球网络空间中各类资产并发现其安全风险。

![](https://image.3001.net/images/20210613/1623591659_60c60aeb6670ff5bb8cdf.png!small)

###  **[Zoomeye](https://www.zoomeye.org/ "链接")**  

官方介绍

  * 创宇旗下404实验室驱动打造的中国第一款，通过分布在全球的大量测绘节点，针对全球范围内的IPv4、IPv6地址库及网站域名库进行24小时不间断探测、识别，根据对多个服务端口协议进行测绘。

###
![](https://image.3001.net/images/20210613/1623591700_60c60b14ad125c6bfe5bf.png!small)

###

###  **私有的网络测绘系统**

北京华顺信安信息技术有限公司--- **网络资产测绘及风险分析系统**

![](https://image.3001.net/images/20210613/1623591783_60c60b671b867edfdc0f0.png!small)

###

###  **开源的网络测绘系统**

 **w12scan**

官方介绍：w12scan是一款网络资产发现引擎，通过WEB接口下发任务，w12scan会自动将相关的资产聚合在一起方便分析使用。

github： [https://github.com/w-digital-scanner/w12scan
](https://github.com/w-digital-scanner/w12scan "链接")  

![](https://image.3001.net/images/20210613/1623591842_60c60ba2d224934236335.png!small)

### **网络测绘系统的基本使用**

以Quake为例

搜索泛微OA办公系统

语法：`app:"泛微协同办公OA"`

![](https://image.3001.net/images/20210613/1623591893_60c60bd5cabea6d3464c3.png!small)统计

![](https://image.3001.net/images/20210613/1623591910_60c60be602d20ddb92190.png!small)

其他一些有趣的搜索语法

> 目录泄露
>
> `title:"Index of /"`
>
> 未安装的 WordPress
>
> `title:"WordPress Setup Configuration File"`
>
> 运行匿名登录的FTP服务
>
> `"Anonymous user logged in"`
>
> 未安装的 phpwind  
> `title:"phpwind社区产品 - Powered by phpwind"`
>
> MongoDB未授权
>
> `"MongoDB Server Information"`
>
> 惠普打印机
>
> `app:"HP-Officejet-Pro"`

太多就不一 一 列举，如有不足欢迎补充

本文是原创

未经允许禁止转载！

