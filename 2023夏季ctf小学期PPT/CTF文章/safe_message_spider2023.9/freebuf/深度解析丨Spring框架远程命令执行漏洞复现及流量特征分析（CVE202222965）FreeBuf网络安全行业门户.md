## **0** **1.** **漏洞详情**

 **1、漏洞简介**

2022年3月30日，Spring框架曝出RCE
0day漏洞，国家信息安全漏洞共享平台（CNVD）已收录了Spring框架远程命令执行漏洞（CNVD-2022-23942），考虑到Spring框架的广泛应用，漏洞被评级为危险。

通过该漏洞可写入webshell以及命令执行。在Spring框架的JDK9版本(及以上版本)中，远程攻击者可在满足特定条件的基础上，通过框架的参数绑定功能获取AccessLogValve对象并注入恶意字段值，从而触发pipeline机制并写入任意路径下的文件。

 **2、漏洞利用条件**

  * Apache Tomcat作为Servlet容器；

  * 使用JDK9及以上版本的Spring MVC框架；

  * Spring框架以及衍生的框架spring-beans-*.jar文件或者存在

 **3、漏洞影响范围**

  * JDK JDK 9+

  * Spring Framework 5.3.18+ 5.2.20+

docker已经配置好jdk环境。docker中的环境与宿主机jdk环境无关，只是当时做实验的时候，刚好也装了jdk9，记录了一下安装过程。

ubuntu下jdk9安装：

官网下载jdk，放入解压到路径/usr/lib/jvm

利用update-alternatives 进行jdk版本切换

数字越大，优先级越高

执行命令：

![1.jpg](https://image.3001.net/images/20221206/1670290071_638e9a975e17a8f094764.jpg!small)

修改配置：

![2.jpg](https://image.3001.net/images/20221206/1670290071_638e9a97e97de3dcc4a70.jpg!small)

检查一下：

![3.jpg](https://image.3001.net/images/20221206/1670290072_638e9a986bab0079c783e.jpg!small)

每一个命令都是auto 模式，这样才会自动选择优先级高的。为了确保，可以不用管现在的状态，直接设置一遍这些命令为auto模式。

![4.jpg](https://image.3001.net/images/20221206/1670290073_638e9a9917a85f026b740.jpg!small)

版本检查：

![5.jpg](https://image.3001.net/images/20221206/1670290073_638e9a9985a96a6715732.jpg!small)

##  **0** **2.** **环境配置**

主机系统：Apple M1，macOS Ventura version13.0

虚拟机系统（docker靶场系统）：ubuntu 20.04.2 x86 （腾讯云服务器）

##  **0** **3.** **漏洞复现**

靶场项目：https://github.com/vulhub/vulhub

 **1、ubuntu安装docker**

源：https://lug.ustc.edu.cn/wiki/mirrors/help/docker/

![6.jpg](https://image.3001.net/images/20221206/1670290073_638e9a99ecddb4b507ed6.jpg!small)

 **2、安装pip**

![7.jpg](https://image.3001.net/images/20221206/1670290074_638e9a9a64075ab5d43d5.jpg!small)

 **3、安装docker-compose**

![8.jpg](https://image.3001.net/images/20221206/1670290074_638e9a9abfb6a9e05fef2.jpg!small)

 **4、启动靶场环境**

![9.jpg](https://image.3001.net/images/20221206/1670290075_638e9a9b28bbb487adb4d.jpg!small)

可能遇到的问题：卡在了pulling阶段

因为docker加速器超时导致pull不下来，改成国内镜像

![10.jpg](https://image.3001.net/images/20221206/1670290075_638e9a9b98ef9391af138.jpg!small)

添加以下内容：

![11.jpg](https://image.3001.net/images/20221206/1670290076_638e9a9c016b590df9644.jpg!small)

重启

![12.jpg](https://image.3001.net/images/20221206/1670290076_638e9a9c6578bf25dad3f.jpg!small)

![13.jpg](https://image.3001.net/images/20221206/1670290076_638e9a9cd150799a8e294.jpg!small)

 **5、漏洞版本验证**

进入docker控制台

![14.jpg](https://image.3001.net/images/20221206/1670290077_638e9a9d43c11fd207b57.jpg!small)

JDK

![15.jpg](https://image.3001.net/images/20221206/1670290077_638e9a9ddc3bb2210bc5f.jpg!small)

##  **0** **4.** **利用链**

利⽤class对象构造利⽤链，对Tomcat的日志配置进行修改

然后，向⽇志中写⼊shell

![16.jpg](https://image.3001.net/images/20221206/1670290078_638e9a9e4da34d3c9c998.jpg!small)

 **1、构造payload**

![17.jpg](https://image.3001.net/images/20221206/1670290079_638e9a9fac73e09c712b4.jpg!small)

 **2、GET发送**

![18.jpg](https://image.3001.net/images/20221206/1670290080_638e9aa021c352fa13fff.jpg!small)

![19.jpg](https://image.3001.net/images/20221206/1670290080_638e9aa0aac166ecc6c3d.jpg!small)

服务器上验证，确实已经生成了jsp

![20.jpg](https://image.3001.net/images/20221206/1670290081_638e9aa198fedf3e1b90c.jpg!small)

 **3、访问写入的webshell文件**

![21.jpg](https://image.3001.net/images/20221206/1670290082_638e9aa23c93f1969e90b.jpg!small)

![22.jpg](https://image.3001.net/images/20221206/1670290082_638e9aa2b9a8f26fe20ef.jpg!small)

 **4、清空**

![23.jpg](https://image.3001.net/images/20221206/1670290084_638e9aa4253659144b85d.jpg!small)

总体来说，这个漏洞的利用方法会修改目标服务器配置，导致目标需要重启服务器才能恢复，实际测试中需要格外注意。

##  **0** **5.** **反弹shell**

 **1、用msf生成木马**

**![24.jpg](https://image.3001.net/images/20221206/1670290084_638e9aa4a61e2e1f2cdae.jpg!small)**

Lhost是监听机器的ip。因为目标机也是公网中的，所以监听机器也需要是公网IP，这样才能访问到。

msf生成的shell.elf是在本地的，需要自己想办法传到服务器上。

![25.jpg](https://image.3001.net/images/20221206/1670290085_638e9aa54cde94ab9f9ea.jpg!small)

![26.jpg](https://image.3001.net/images/20221206/1670290085_638e9aa5b4a3319fe3f6d.jpg!small)

 **2、木马上传**

正常情况下，应该是在公网的vps下面生成elf，然后wget下载。但我这次在本地生成的，所以直接scp拷到服务器上去。

宿主机向docker传输文件

![27.jpg](https://image.3001.net/images/20221206/1670290086_638e9aa64bfe757dc62f9.jpg!small)

![28.jpg](https://image.3001.net/images/20221206/1670290086_638e9aa6bb46339c53923.jpg!small)

 **3、赋予木马权限**

![29.jpg](https://image.3001.net/images/20221206/1670290087_638e9aa7519204dfc7adb.jpg!small)

![30.jpg](https://image.3001.net/images/20221206/1670290087_638e9aa7b0be030d23b9a.jpg!small)

 **4、msf开启监听**

在公网服务器上

ubuntu快速安装msf：<https://www.cnblogs.com/tomyyyyy/p/12813299.html>

![31.jpg](https://image.3001.net/images/20221206/1670290088_638e9aa81f74502666d74.jpg!small)

 **5、执行木马**

![32.jpg](https://image.3001.net/images/20221206/1670290088_638e9aa8aaf7da4aa53de.jpg!small)

##  **0** **6.** **抓包**

过滤语句：ip终点选靶机的IP，起点选择攻击机的IP。

因为靶场走的8080端口，http协议，所以筛选条件加上http协议。

![33.jpg](https://image.3001.net/images/20221206/1670290090_638e9aaa0e463bef75ddf.jpg!small)

![34.jpg](https://image.3001.net/images/20221206/1670290090_638e9aaa6e0c636c2736e.jpg!small)

追随No.1277和1566的http流

##  **0** **7.** **特征流量分析**

 **1、pipeline.first.pattern**

![35.jpg](https://image.3001.net/images/20221206/1670290091_638e9aab39a6cb30f12ac.jpg!small)

对get头进行解码：

![36.jpg](https://image.3001.net/images/20221206/1670290092_638e9aac16dd4272bada6.jpg!small)

![37.jpg](https://image.3001.net/images/20221206/1670290092_638e9aacb35dc6bc9e4c5.jpg!small)

 **2、pipeline.first.suffix**

![38.jpg](https://image.3001.net/images/20221206/1670290093_638e9aad4f2948c15f3d3.jpg!small)

 **3、parent.pipeline.first.directory**

![39.jpg](https://image.3001.net/images/20221206/1670290093_638e9aade5559cee994bb.jpg!small)

 **4、pipeline.first.prefix**

![40.jpg](https://image.3001.net/images/20221206/1670290094_638e9aae7d851f067539b.jpg!small)

 **5、pipeline.first.fileDateFormat**

![41.jpg](https://image.3001.net/images/20221206/1670290095_638e9aaf87f8835000ecc.jpg!small)

##  **0** **8.** **漏洞规则**

规则思路如下：

![42.jpg](https://image.3001.net/images/20221206/1670290096_638e9ab03d59c77575527.jpg!small)

##  **0** **9.** **snort规则验证**

snort的各种配置以及环境，见以前的blog：http://985.so/b0etg

把刚刚抓到的数据包放进snort环境中，把写好的规则文件也放进环境中。

 **1、规则配置**

把规则文件放进规则路径，并修改snort.conf配置

![43.jpg](https://image.3001.net/images/20221206/1670290096_638e9ab0b00c5366a1634.jpg!small)

![44.jpg](https://image.3001.net/images/20221206/1670290097_638e9ab1239db7a22b471.jpg!small)

 **2、修改snort.conf的内容**

设置需要保护的ip地址

![45.jpg](https://image.3001.net/images/20221206/1670290097_638e9ab1c9933189ef685.jpg!small)

![46.jpg](https://image.3001.net/images/20221206/1670290098_638e9ab23e88eb9249334.jpg!small)

![47.jpg](https://image.3001.net/images/20221206/1670290098_638e9ab2a77f60fb43b39.jpg!small)

![48.jpg](https://image.3001.net/images/20221206/1670290099_638e9ab33b76e0f973188.jpg!small)

![49.jpg](https://image.3001.net/images/20221206/1670290099_638e9ab3ac500689430c7.jpg!small)

![50.jpg](https://image.3001.net/images/20221206/1670290100_638e9ab41718da5bf2169.jpg!small)

在setp6里，设置输出

![51.jpg](https://image.3001.net/images/20221206/1670290100_638e9ab4edfc217f58e8b.jpg!small)

![52.jpg](https://image.3001.net/images/20221206/1670290101_638e9ab555be04c3ccb90.jpg!small)

翻到最下面，找到规则集列表。

打开local.rules的注释，以允许snort装载个性化规则集。

![53.jpg](https://image.3001.net/images/20221206/1670290101_638e9ab5d13a087bc9631.jpg!small)

![54.jpg](https://image.3001.net/images/20221206/1670290102_638e9ab63f140cb09621a.jpg!small)

保存编辑：wq

 **3、测试是否能正常工作**

![55.jpg](https://image.3001.net/images/20221206/1670290103_638e9ab73bec53f976dea.jpg!small)

 **4、运行成功**

![56.jpg](https://image.3001.net/images/20221206/1670290103_638e9ab79b57e980d25c3.jpg!small)

 **5、规则验证**

![57.jpg](https://image.3001.net/images/20221206/1670290104_638e9ab84d0dbdaab503a.jpg!small)

##  **10.** **修复及防范措施**

 **1、漏洞排查**

  * JDK版本号排查

在业务系统的运行服务器上，执行java -version命令查看运行的JDK版本，如果版本号小于等于8，则不受漏洞影响

  * Spring框架使用情况排查

如果业务系统项目以war包形式部署，按照如下步骤进行判断：

![64.jpg](https://image.3001.net/images/20221206/1670290104_638e9ab8b015cbf2d03d3.jpg!small)

![65.jpg](https://image.3001.net/images/20221206/1670290105_638e9ab92ed8b65a4f4fb.jpg!small)

如果业务系统项目以jar包形式直接独立运行，按照如下步骤进行判断：

![66.jpg](https://image.3001.net/images/20221206/1670290105_638e9ab992dc3fdf829ea.jpg!small)

 **2、漏洞影响**

  * JDK版本号在9及以上的

  * 使用了spring框架或衍生框架

 **3、漏洞修复建议**

![67.jpg](https://image.3001.net/images/20221206/1670290106_638e9aba1b248491d7ef2.jpg!small)

 **4、安全产品部署** 该漏洞的防范规则，现已加入六方云工业互联网安全产品体系。

  * 在网络出口位置部署六方云防火墙，并及时更新特征库；
  * 部署六方云网络威胁检测与回溯系统，及时发现未知威胁。

##  **11.** **附录：** **snort 文件部署路径**

 **1、snort安装包所在路径、相关文档**

![58.jpg](https://image.3001.net/images/20221206/1670290106_638e9aba954937cf7e04a.jpg!small)

  * doc：snort的一些说明文档所在文件夹

 **2、snort规则文件、配置文件**

![59.jpg](https://image.3001.net/images/20221206/1670290107_638e9abb0093e668d06c5.jpg!small)

 **3、snort日志文件**

![60.jpg](https://image.3001.net/images/20221206/1670290107_638e9abb663dfb6b24d7a.jpg!small)

 **4、snort运行**

![61.jpg](https://image.3001.net/images/20221206/1670290108_638e9abc0d7292043a0a7.jpg!small)

 **5、规则路径**

![62.jpg](https://image.3001.net/images/20221206/1670290108_638e9abc9aa0132d5fd6b.jpg!small)

 **6、配置路径**

![63.jpg](https://image.3001.net/images/20221206/1670290109_638e9abd03a3c1b6ff85f.jpg!small)

