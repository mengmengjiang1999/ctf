**近日，深信服安全团队追踪到一新型的挖矿病毒，该病毒与普通挖矿病毒有很大差异，普通挖矿没有特殊防护，而该病毒采用了驱动进行防护，十分罕见。**

与多数挖矿病毒一样，感染主机会出现异常卡顿现象，且CPU占用率过高。该病毒使用了驱动保护，无法通过任务管理器中止病毒进程，很难查杀。深信服已将该病毒命名为ProtectionX。

感染ProtectionX病毒后，系统中会存在3个进程：母体1sass.exe及其子进程wuauc1t.exe与win1ogon.exe，注意名称中是“1”而不是“l”。其中win1ogon.exe进程占用大量CPU资源。

![图片.png](https://image.3001.net/images/20180926/1537933605_5bab01256312d.png!small)尝试终止1sass.exe进程，提示“拒绝访问”。而终止wuauc1t.exe和win1ogon.exe进程后，又会重新起来！这里，是因为有驱动保护了1sass.exe，而1sass.exe又防护了wuauc1t.exe与win1ogon.exe，环环相扣，多层护体。

![图片.png](https://image.3001.net/images/20180926/1537933615_5bab012fcde81.png!small)

## 一、行为分析

病毒执行流程如下：

![图片.png](https://image.3001.net/images/20180926/1537933973_5bab02955478a.png!small)主要包括3个模块：自保护、持久化以及挖矿模块。其中
**自保护模块** 用于保护病毒母体进程不被杀掉， **持久化模块** 添加开机自启动， **挖矿模块**
会进行挖矿并杀掉别的挖矿进程以及其他一些CPU占用高的进程。

### 1.1 病毒文件

病毒母体1sass.exe为一个win32程序，加了VMP壳。

![图片.png](https://image.3001.net/images/20180926/1537933985_5bab02a19a7ad.png!small)

### 1.2 自保护模块

释放ProcessExtended.dll模块到本目录并加载。

![图片.png](https://image.3001.net/images/20180926/1537933996_5bab02ac69ff3.png!small)![图片.png](https://image.3001.net/images/20180926/1537934001_5bab02b1b476e.png!small)

调用ProcessProtectionX函数。

![图片.png](https://image.3001.net/images/20180926/1537934010_5bab02ba17dcb.png!small)ProcessProtectionX函数首先释放一个驱动文件到%Temp%目录，驱动文件名由7个随机的字母加数字组成。

![图片.png](https://image.3001.net/images/20180926/1537934019_5bab02c3ce374.png!small)安装驱动，服务名为hy5.5。

![图片.png](https://image.3001.net/images/20180926/1537934029_5bab02cd73e2d.png!small)与驱动通信，将自身进程ID发送给驱动。

![图片.png](https://image.3001.net/images/20180926/1537934038_5bab02d6ca44f.png!small)驱动中使用了SSDT
HOOK，HOOK掉了NtOpenProcess从而实现进程保护。

![图片.png](https://image.3001.net/images/20180926/1537934047_5bab02dfc63f4.png!small)![图片.png](https://image.3001.net/images/20180926/1537934052_5bab02e45ac9d.png!small)

删除驱动文件。

###
![图片.png](https://image.3001.net/images/20180926/1537934060_5bab02ecba2b5.png!small)1.3
持久化模块

为1sass.exe添加自启动，注册表路径为“HKLM\software\microsoft\windows\CurrentVersion\Run\Registered
font”。

###
![图片.png](https://image.3001.net/images/20180926/1537934075_5bab02fbed040.png!small)1.4
挖矿模块

挖矿模块包含两个进程：wuauc1t.exe和win1ogon.exe。由1sass.exe释放并运行，随后进入循环对这两个进程进程守护。

![图片.png](https://image.3001.net/images/20180926/1537934086_5bab030611b7a.png!small)

 **1.4.1 抢占资源**

wuauc1t.exe的功能为抢占CPU资源，由1sass.exe释放到同一目录下并运行，运行时传入参数“win1ogon.exe”。

![图片.png](https://image.3001.net/images/20180926/1537934138_5bab033ad6772.png!small)![图片.png](https://image.3001.net/images/20180926/1537934142_5bab033e55952.png!small)

首先遍历系统进程并获取其CPU占用率。“Process\ % Processor Time”用于获取过程的所有线程在每个处理器上的处理器时间总和。

![图片.png](https://image.3001.net/images/20180926/1537934149_5bab03459cdd0.png!small)

获取除传入参数“win1ogon.exe”、本进程以及“explorer.exe”以外的CPU占用较高的进程。

![图片.png](https://image.3001.net/images/20180926/1537934159_5bab034f4179a.png!small)![图片.png](https://image.3001.net/images/20180926/1537934163_5bab0353f2f00.png!small)

终止掉CPU占用较高的其他进程以及其他挖矿进程。

![图片.png](https://image.3001.net/images/20180926/1537934171_5bab035bb4740.png!small)

终止的其他挖矿进程列表如下：

![图片.png](https://image.3001.net/images/20180926/1537934180_5bab0364720be.png!small)
**1.4.2 挖矿**

win1ogon.exe为挖矿进程，也是由1sass.exe释放到同一目录下并运行。矿池为pool.minexmr.com:7777。

![图片.png](https://image.3001.net/images/20180926/1537934190_5bab036e66988.png!small)![图片.png](https://image.3001.net/images/20180926/1537934194_5bab037245218.png!small)

有了其他两个进程的保驾护航，挖矿进程可以最大限度的利用系统资源进行挖矿。

## 二、解决方案  

### **病毒防御** ****

1.及时给电脑打补丁，修复漏洞。

2.对重要的数据文件定期进行非本地备份。

3.更改账户密码，设置强密码，避免使用统一的密码。

4.可以尝试使用PC Hunter强制删除并结束进程1sass.exe、wuauc1t.exe、win1ogon.exe。

5.删除注册表项HKLM\software\microsoft\windows\CurrentVersion\Run\Registered font。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

