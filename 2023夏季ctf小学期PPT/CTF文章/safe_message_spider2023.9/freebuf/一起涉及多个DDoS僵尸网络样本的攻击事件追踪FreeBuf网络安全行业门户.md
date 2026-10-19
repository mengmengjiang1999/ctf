## 一．背景

**近期蜜网系统监测到一起涉及利用多个僵尸木马传播进行DDoS攻击的安全事件。木马样本涉及Windows与Linux两个平台，通过对样本的分析，发现这几个样本编写风格都不一样，但是硬编码在程序中的C
&C均指向同一个IP地址。推测这一系列木马的传播者通过购买不同的DDoS木马进行传播，从而构建自己的僵尸网络进行DDoS攻击牟利。其中有两个样本所属家族为XorDDoS和ChinaZ。最后通过一系列的分析，将该威胁定性为小黑客组建僵尸网络进行DDoS攻击事件，同时追踪到了恶意代码传播者的个人信息，包括姓名、QQ号码、手机号、邮箱、微信等。**

## 二．相关样本分析

###  **2.1样本一分析：**

 **2.1.1样本基本信息**

![image.png](https://image.3001.net/images/20180524/15271743832798.png!small)

 **2.1.2样本行为**

该样本首先会执行安装逻辑，包括拷贝自身到Windows目录，然后将自身注册为服务，最后自删除自己，安装完成。接着注册为服务的木马会开始进入功能逻辑，通过爆破局域网来感染传播，与C&C建立通讯后，等待C&C下发指令。

![image.png](https://image.3001.net/images/20180524/15271732341695.png!small)

 **2.1.3样本详细分析**

（1）整体逻辑

![image.png](https://image.3001.net/images/20180524/15271732614688.png!small)

（2）拷贝到Windows目录

生成6个字符的随机进程名拷贝到Windows目录

![image.png](https://image.3001.net/images/20180524/15271732719503.png!small)

（3）创建服务

服务名：Abcdef Hijklmno Qrstuvwx Abcd

服务描述：Abcdefgh Jklmnopqr Tuvwxya Cdefghij Lmn

![image.png](https://image.3001.net/images/20180524/15271733014187.png!small)

![image.png](https://image.3001.net/images/20180524/15271733242049.png!small)![image.png](https://image.3001.net/images/20180524/15271733349999.png!small)

自启动

![image.png](https://image.3001.net/images/20180524/15271733593390.png!small)

（4）自删除

构建“/c del C:\Users\xxx\Desktop\gy.exe > nul”参数，使用ShellExecuteExA创建删除自身的进程。

![image.png](https://image.3001.net/images/20180524/15271733745201.png!small)

![image.png](https://image.3001.net/images/20180524/15271733812052.png!small)

（5）从资源释放hra33.dll并加载

从资源释放文件在文件头加上PE文件头两个字节“MZ”。

![image.png](https://image.3001.net/images/20180524/15271733912496.png!small)

![image.png](https://image.3001.net/images/20180524/15271733999825.png!small)

从释放的文件更新当前木马服务中的资源

![image.png](https://image.3001.net/images/20180524/15271734087949.png!small)（6）爆破感染局域网

内置字典

![image.png](https://image.3001.net/images/20180524/15271734144105.png!small)

爆破成功后会拷贝自身到admin$\\\、C：、D:、E：以及F:等路径下，并创建计划任务，2分钟后执行。

![image.png](https://image.3001.net/images/20180524/15271734232822.png!small)

（7）远控功能部分

与C&C建立通讯

![image.png](https://image.3001.net/images/20180524/15271734336035.png!small)  

解密出C&C地址为web.liancanmou.xyz:6006

![image.png](https://image.3001.net/images/20180524/15271734403953.png!small)

发送上线信息

![image.png](https://image.3001.net/images/20180524/15271734485415.png!small)

![image.png](https://image.3001.net/images/20180524/15271734561500.png!small)  

远程下载执行

![image.png](https://image.3001.net/images/20180524/1527173461469.png!small)更新

![image.png](https://image.3001.net/images/20180524/15271734674773.png!small)![image.png](https://image.3001.net/images/20180524/1527173472765.png!small)

使用iexplorer打开指定网页

![image.png](https://image.3001.net/images/20180524/15271734817085.png!small)

卸载

![image.png](https://image.3001.net/images/20180524/15271734884559.png!small)  

![image.png](https://image.3001.net/images/20180524/15271734934831.png!small)

DDoS攻击模块

![image.png](https://image.3001.net/images/20180524/15271735012623.png!small)  

![image.png](https://image.3001.net/images/20180524/15271735072244.png!small)

**2.1.4 关联分析**

![image.png](https://image.3001.net/images/20180524/15271735174153.png!small)  

该IP对应的位置在新乡电信机房，访问<http://123.160.10.16:3097/gy.exe>下载样本。

通过VT Graph关联分析该样本早在2018-05-08已经被发现了，与本次捕获到的样本分析结果是一致的。

![image.png](https://image.3001.net/images/20180524/15271735231014.png!small)

###  **2.2样本二分析：**

 **2.2.1样本基本信息**

![image.png](https://image.3001.net/images/20180524/15271745085002.png!small)

**2.2.2样本行为**

该样本代码编写十分简单，获取本地信息回传CNC上线，等待CNC的DDoS指令。

![image.png](https://image.3001.net/images/20180524/15271735456226.png!small)

 **2.2.3样本详细分析**

（1）整体逻辑

![image.png](https://image.3001.net/images/20180524/15271735538010.png!small)

![image.png](https://image.3001.net/images/20180524/1527173560856.png!small)

（2）与C2建立通讯

创建连接套接字

C&C地址为 jch.liancanmou.xyz:52527

![image.png](https://image.3001.net/images/20180524/1527173573520.png!small)

木马通讯协议

![image.png](https://image.3001.net/images/20180524/15271735807139.png!small)

（3）DDoS功能

![image.png](https://image.3001.net/images/20180524/15271744347855.png!small)  

并没有用到反射放大攻击，只是一般的flood攻击。

![image.png](https://image.3001.net/images/20180524/15271735954280.png!small)

![image.png](https://image.3001.net/images/20180524/15271736016432.png!small)

 **2.2.4关联分析**

通过VT分析发现该样本与a.lq4444.com这个域名相关，而该域名曾用于Linux/Elknot这个家族。通过VT显示，a.lq4444.com这个域名与9个样本相关。

![image.png](https://image.3001.net/images/20180524/15271736102815.png!small)

###  **2.3样本三分析**

![image.png](https://image.3001.net/images/20180524/15271745514332.png!small)  

样本三与样本二代码是一样的，区别是样本三被编译为x86架构，样本二被编译为x64架构。

###  **2.4样本四分析：**

 **2.4.1样本基本信息**

![image.png](https://image.3001.net/images/20180524/1527174591912.png!small)

 **2.4.2样本行为**

> （1）该样本通过SSH爆破被拷贝到/tmp目录下并开始运行
>
> （2）将自身注册为服务
>
> （3）拷贝自身到其他目录
>
> （4）设置定时任务
>
> （5）修改刷新iptables后，尝试连接到远程主机。
>
> （6）它会删除/etc/resolv.conf并保存初始安装和下载的配置数据（Config.ini）
>
> （7）通过发送用户名信息连接到C&C，作为一个bot与C&C建立通讯
>
> （8）C&C主要发送带目标IP地址作为参数的DDoS命令到bot机器进行DDoS攻击

VT行为分析：

![image.png](https://image.3001.net/images/20180524/15271736327140.png!small)  

**2.4.3样本详细分析**

写入脚本到/etc/init.d/%s/与/etc/rc%d.d/S90%s路径下

![image.png](https://image.3001.net/images/20180524/15271736456096.png!small)  

设置定时任务

![image.png](https://image.3001.net/images/20180524/15271736526250.png!small)

控制网卡接口

![image.png](https://image.3001.net/images/20180524/15271736625207.png!small)

以.chinaz为前缀拷贝自身到/tmp/目录下

![image.png](https://image.3001.net/images/20180524/1527173671594.png!small)

安装完成后会重启计算机

![image.png](https://image.3001.net/images/20180524/15271736791642.png!small)

DDoS相关的一些指纹，其中包含一个QQ号码：2900570290

![image.png](https://image.3001.net/images/20180524/15271736938181.png!small)

![image.png](https://image.3001.net/images/20180524/15271737022741.png!small)

## 三． **事件分析**

###  **3.1事件关联分析**

以liancanmou.xyz这个域名为起点，结合样本分析与VT
Graph关联分析形成以下关联图，可以确定123.160.10.16、180.97.220.35以及123.249.9.157这三个IP是用于作为木马的CNC地址以及木马分发地址。在2018年5月24日域名liancanmou.xyz从指向123.249.9.157被换位指向180.97.220.35这个IP。

![image.png](https://image.3001.net/images/20180524/15271750584521.png!small)

PassiveDNS相关信息

![image.png](https://image.3001.net/images/20180524/15271743432000.png!small)

###  **3.2事件溯源**

 **3.2.1域名注册信息**

![image.png](https://image.3001.net/images/20180524/15271738659781.png!small)

 **3.2.2个人信息**

![image.png](https://image.3001.net/images/20180524/15271738745619.png!small)

![image.png](https://image.3001.net/images/20180524/15271738801683.png!small)

## 四．IoCs

> liancanmou.xyz
>
> web.liancanmou.xyz
>
> jch.liancanmou.xyz
>
> wwt.liancanmou.xyz
>
> wwv.liancanmou.xyz
>
> [www.liancanmou.xyz](http://www.liancanmou.xyz)
>
> <http://180.97.220.35:3066/Linux4.7>
>
> <http://123.160.10.16:3097/gy.exe>
>
> <http://180.97.220.35:3066/33>
>
> <http://180.97.220.35:3066/32>
>
> 180.97.220.35
>
> 123.249.9.157
>
> 123.160.10.16
>
> 123.249.9.15
>
> 123.249.79.250
>
> 180.97.220.35
>
> 103.248.220.196
>
> 892833AB52DAA816918041670519EB6351AE7EC2DB7AF2C97F3AB5EE214DA173
>
> 4A2FB58342D549347D32E54C3DA466A19BFD66364825AC7F2257995356F09AFD  
>
>
> 74D4776A76AD3BCB578C9757D9F18A6ADFFE8802C43E5E59B14C4E905664733D  
>
>
> DBC7FC7748BD201C54B2A0189396F3101C18127A715E480C8CB808F07137822A

 *** 本文作者：任子行，转载注明来自FreeBuf.COM**  

