## 一、 背景介绍

**近日，深信服安全团队捕获到一个新型垃圾邮件，其中包含受密码保护的Word文档，团队中的相关人员对其进行了深入的分析，发现是同样类型的Neutrino最新版本僵尸程序。**

## 二、 样本信息

Neutrino属于Kasidet家族，此次病毒通过伪装成“发票到期”的电子邮件并且带有密码保护的附件进行传播，带有密码保护的电子邮件可能会给人一种安全感。在此深信服提醒广大用户：陌生人发来的陌生文档，邮件不要轻易打开。邮件内容如下：

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809712_5c232f30149f3.png!small)

图1 邮件内容屏幕截图

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809721_5c232f39e5426.png!small)

图2 需要输入密码才能打开的Word文档

“Invoice.doc”附件中包含一个宏，如果用户的宏安全设置为低，则文档将自动启动宏。此外，宏受密码保护。面对这种情况，大多数用户都不知道这份文件会在后台做些什么。如下：

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809728_5c232f40546bb.png!small)

图3 启用宏内容

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809736_5c232f482335b.png!small)

图4宏受密码保护

查看宏内容显示它将从hxxp//209.141.59.124/1.exe下载文件，然后保存至%Temp%\qwerty2.exe并启动。宏内容如下：

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809744_5c232f50acb8e.png!small)

图5宏内容

 **qwerty2.exe** 主要功能如下：

> a) DDOS攻击
>
> b) 信息窃取
>
> c) FTP嗅探
>
> d) 反调试、反虚拟机和反沙箱
>
> e) 文件下载

本次分析涉及的文件信息如下。

## 三、 样本分析

1\. 样本运行后先执行一段混淆代码，然后通过“MapViewOfFile”将文件进行映射。

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809759_5c232f5f39c6d.png!small)![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809759_5c232f5f50863.png!small)

图6 映射后的代码数据

2\. 将映射后的数据进行解密，通过跳转到ZwSetInformationProcess函数将DEP关闭，然后在转入解密后的数据并执行。

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809770_5c232f6aece57.png!small)

图7 解密后的数据

![9.png](https://image.3001.net/images/20181226/1545809782_5c232f769c801.png!small)![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809782_5c232f76a110c.png!small)

图8 跳转到解密后的代码并执行

3\. 获取cpuid信息（包括型号，信息处理器）、操作系统版本、地理位置、网卡配置和IP信息。

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809792_5c232f8088366.png!small)

图9 获取cpuid

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809803_5c232f8b85943.png!small)

图10 获取地理位置

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809812_5c232f947c5ee.png!small)

图11动态加载Getadaptersinfo获取网卡配置和IP

4\. 为了防止恶意程序被多次运行Neutrino恶意软件创建互斥体：“{FC502D82-2B78-8E2F-95F0-8FA2992433F6}”。

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809822_5c232f9e1d200.png!small)

图12 创建互斥体

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809832_5c232fa832687.png!small)

图13 注册表Run启动

6\. 动态加载CreateToolhelp32Snapshot、Module32First、M
odule32Next函数遍历进程模块与事先设定好的进程模块进行比较，如果遍历到相同进程模块，则终止执行。

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809841_5c232fb1526a1.png!small)

图14 遍历进程

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809857_5c232fc1b9bb2.png!small)

图15 判断程序是否被调试

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809866_5c232fca802bb.png!small)

图16 窗口名检测

8\. 如果程序加载成功，便会加载核心程序，使用CryptStringToBinary API函数解密嵌入的C&C URL将获取的信息以
POST的方式发送到securityupdateserver4.com。这些响应包会以注释形式嵌入到空白html页面中，为避免让用户发觉。捕获的流量包如下：

![伪装成“发票到期”电子邮件，传播Neutrino僵尸网络](https://image.3001.net/images/20181226/1545809875_5c232fd37877a.png!small)

图17 捕获到的流量包

### **总结**

僵尸程序最主要的特点就是可以一对多地执行相同的[恶意](https://baike.baidu.com/item/%E6%81%B6%E6%84%8F)行为，比如可以同时对某目标网站进行[分布式拒绝服务](https://baike.baidu.com/item/%E5%88%86%E5%B8%83%E5%BC%8F%E6%8B%92%E7%BB%9D%E6%9C%8D%E5%8A%A1)（DDOS）攻击，同时发送大量的[垃圾邮件](https://baike.baidu.com/item/%E5%9E%83%E5%9C%BE%E9%82%AE%E4%BB%B6)等，而正是这种一对多的控制关系，使得攻击者能够以极低的代价高效地控制大量的资源为其服务。僵尸程序一旦构成了一个攻击平台，便可利用这个平台有效地发起各种各样的攻击行为，可以导致整个基础信息网络或者重要应用系统瘫痪，也可以导致大量机密或个人隐私泄漏，还可以用来从事网络欺诈等其他违法犯罪活动。

## 四、 相关IOC

> Md5：E875E978CCDD5A02AEEFB207F83F7E16
>
> Md5：30B43B2437A5CA665279D4A47A18CE7C
>
> IP：209.141.59.124
>
> 域名：securityupdateserver4.com
>
> Url：http//209.141.59.124/1.exe

## 五、 解决方案

###  **病毒检测查杀**

1\. 可使用免费查杀工具，进行检测查杀：<http://edr.sangfor.com.cn/tool/SfabAntiBot.zip>

2\. 相关防火墙、安全感知平台等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒检测。

###  **病毒防御**

> 1\. 及时给电脑打补丁，修复漏洞。
>
> 2\. 陌生人发来的陌生文档，邮件不要轻易打开
>
> 3\. 对重要的数据文件定期进行非本地备份

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

 ***本文作者：千里目安全实验室，转载请注明来自 FreeBuf.COM**

