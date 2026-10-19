## **一、概述**  

**近期，毒霸捕风系统发现“独狼”病毒家族的感染量呈现出上升的趋势，结合数据来看，发现其是从一个名为InstExe_02XX的程序释放而来，在后续的进一步分析中，我们发现多款流氓软件近期同时都在推送该文件，该文件除了会实时从云端服务器接收指令，进行流量暗刷、病毒更新、主页劫持、推广软件的安装等操作外，还会推送安装独狼和老裁缝流量暗刷病毒。**

该木马依附的软件大多功能单一，界面粗糙，表面上看具有一定正常功能，但实则上却会暗中使坏，劫持用户主页、弹广告、流量劫持，从而影响电脑的正常使用。

根据病毒作者网站的名称，我们将此病毒命名为唯心木马。

![15629042447976.png](https://image.3001.net/images/20190712/1562909225_5d281a29c37e8.png!small)

##  **二、技术分析**

我们以其中一个渠道的宿主软件“眼睛守护神”为例，该程序安装完成后，通过接收不同的命令行，执行不同的功能，病毒的感染流程如下：

![image1.png](https://image.3001.net/images/20190712/1562908766_5d28185e70e0f.png!small)

###  **2.1** **命令行：194C90A7CF70**

 **功能：下载配置文件remaintask.dat**

该文件为加密的配置配置文件，下载链接直接写在程序代码中：

![image2.png](https://image.3001.net/images/20190712/1562908777_5d2818691edcf.png!small)

下载的文件，解密后主要是一些要推广安装的软件、老裁缝病毒、独狼病毒驱动模块，具体内容如下：

![image3.png](https://image.3001.net/images/20190712/1562908787_5d281873bbc82.png!small)

主要包含如下软件：

![4.png](https://image.3001.net/images/20190712/1562908799_5d28187f172b6.png!small)

从配置文件不难看出，某些程序的运行会规避部分城市，并且根据电脑上安装杀软的情况（规避毒霸、Q管、360）甚至执行概率，决定是否运行，从而降低被杀软厂商发现的可能性。

我们主要分析推广列表的前2个文件：独狼病毒驱动安装包（acm.exe）和流量暗刷（InstExe_0238.exe）：

 **2.1.1acm.exe** **（推送独狼病毒）**

我们首先分析独狼病毒驱动安装包（acm.exe），该程序内部包含129和130两个驱动文件，分别适用于x86和x64环境。

结合驱动文件本身采用的技术手段，并对照驱动文件的PDB的路径信息，种种迹象表明该病毒属于独狼家族，而safebrain则为其2019年的新代号，独狼的分支可以大致分为BaiduNetdiskDownload和TSoft两条线，暂不清楚2条分支之间是什么关系，相关信息如下：

![image5.png](https://image.3001.net/images/20190712/1562908812_5d28188cf155f.png!small)

驱动的大致功能如下：

![image6.png](https://image.3001.net/images/20190712/1562908827_5d28189b5dce8.png!small)

驱动加载后，会获取系统版本信息，并在注册表服务服务项下记录驱动加载次数，然后创建设备“\Device\SafeBrain”，接着初始化要注入的进程和模块信息，针对32位进程和64位进程分别配置注入模块，同时根据驱动的加载次数，选择不同的DLL版本，大于60次时使用带manifest的DLL：

![image7.png](https://image.3001.net/images/20190712/1562908841_5d2818a99a058.png!small)

接着设置进程回调、映像加载回调、注册表回调、minifilter，以及创建一个内核线程：

 **（1** **）进程回调**

进程创建时先获取进程名，再根据进程注入列表进行匹配，匹配上则注入DLL模块，并记录在链表中。当进程退出时则清除在链表中的进程信息。

该DLL注入到进程后会匹配当前进程名，如果是浏览器进程，则在命令行添加url参数启动实习主页劫持。如果当前启动是explorer.exe则创建线程下载主页劫持配置文件，并加载corp.DLL进行上报，配置文件下载地址117.50.65.169/conf/conf1.ini，配置文件conf.ini内容如下：

![image8.png](https://image.3001.net/images/20190712/1562908860_5d2818bcae87c.png!small)

被劫持的浏览器，基本覆盖国内主流的浏览器：

![image9.png](https://image.3001.net/images/20190712/1562908869_5d2818c574bec.png!small)

当父进程匹配如下列表时，则从CSIDL_COMMON_APPDATA\\\safebrain\\\conf.ini中读取url配置作为命令行参数调用CreateProcess打开浏览器进程：

![image10.png](https://image.3001.net/images/20190712/1562908875_5d2818cb29787.png!small)

而匹配到如下进程时，则会使用IE替代打开：

![image11.png](https://image.3001.net/images/20190712/1562908901_5d2818e54ffb2.png!small)

在corp.DLL的pdb信息中包含“HideBrush”暗刷字样，其具有暗刷功能模块，会创建线程访问<https://whale123.com/stat/corp.html>。该页面根据服务器配置，跳转到指定的页面，之前跳转的为一些搜狐视频的页面，目前<https://whale123.com/stat/corp.html>只包含一段CNZZ统计代码：

![image12.png](https://image.3001.net/images/20190712/1562908922_5d2818fa60694.png!small)

 **（2** **）映像加载回调**

当加载模块是ntDLL.DLL时，会获取LdrLoadDLL、LdrGetProcedureAddress、NtProtectVirtualMemory的地址，并复制shellcode到内存区，用于DLL注入。

 **（3** **）注册表回调**

拦截指定进程对自身注册表服务项的访问，首先匹配进程名称或路径：

![image13.png](https://image.3001.net/images/20190712/1562908935_5d28190770d54.png!small)

当进程名称或路径匹配到上述规则后，如果操作是RegNtPostEnumerateKey，访问路径是services，则返回STATUS_NO_MORE_ENTRIES。

如果操作是RegNtPreCreateKeyEx或RegNtPreOpenKeyEx，且访问路径是自身注册表服务项时直接返回STATUS_ACCESS_DENIED。

 **（4** **）内核线程**

主要用来对抗杀软的进程拦截和防护功能，具体有以下2个操作：

1.查找进程回调数组PspCreateProcessNotifyRoutine并移除系统模块、自身模块、360FsFlt.sys之外的进程回调；

2.查找映像回调数组PspLoadImageNotifyRoutine，并移除系统模块、自身模块之外的进程回调。

 **（5** **）minifilter**

针对特定进程过滤其对指定路径文件的访问，从而阻止浏览器保护相关模块工作，也保护自身不被轻易查杀。

过滤函数针对常见的浏览器进程、杀软进程以及相关的浏览器保护模块都进行了过滤，过滤列表如下：

![image14.png](https://image.3001.net/images/20190712/1562908945_5d281911d232b.png!small)

 **2.1.2 InstExe_0238.exe** **（推送老裁缝模块）**

该模块的后续加载文件全部内存加载不会落地，与之前的老裁缝病毒不同的是，这个版本首先会尝试将自身添加至360白名单，接着再层层解密释放老裁缝病毒模块，从而进行后续的电商劫持和流量暗刷操作，不过在360监控、防护正常的时候，并不能够覆盖成功。

大致流程如下：

![image15.png](https://image.3001.net/images/20190712/1562908955_5d28191b6e3d7.png!small)

程序运行后，首先会解密出一个DLL文件，内存加载后，再次释放出一个压缩包，包内文件如下：

![image16.png](https://image.3001.net/images/20190712/1562908968_5d281928aff4d.png!small)

解压完文件后，病毒会检测当前环境是否为虚拟机以及是否调试状态，并根据系统的不同，加载不同DLL文件，而该DLL文件后续的加载流程，与我们之前分析的老裁缝病毒具有高度相似性：<https://www.freebuf.com/articles/paper/155702.html>，在此对其加载流程不再累述。

当检测到360存在时，会尝试将自身添加进信任区，方式也比较简单，根据config.xml中的配置信息，随机挑选一个路径和文件名，然后根据编号，选择文件夹中对应的360白名单文件：

![image17.png](https://image.3001.net/images/20190712/1562908980_5d281934e326b.png!small)

接着将自身释放到上图中选择的目录，最后将360安全卫士目录下的speedmem2.hg（信任区文件替换掉，从而完成信任区的添加替换操作，被成功添加后的信任区如下：

![image18.png](https://image.3001.net/images/20190712/1562908990_5d28193ee0467.png!small)

在完成上述多层加载后，最终对电商网站进行劫持，并在后台对目标网站进行流量暗刷，被劫持的电商基本上包含了国内主流的网站，部分列表如下：

![image19.png](https://image.3001.net/images/20190712/1562909000_5d28194858a27.png!small)

而暗刷的配置文件也相当多，共有35个：

![image20.png](https://image.3001.net/images/20190712/1562909007_5d28194fd0041.png!small)

其中暗刷的网站，主要如下：

![image21.png](https://image.3001.net/images/20190712/1562909018_5d28195a4d1e5.png!small)

###  **2.2** **命令行：RunTask1** **（同RunTask4** **）**

 **功能：创建广告弹窗**

![image22.png](https://image.3001.net/images/20190712/1562909030_5d281966d4e70.png!small)

调用EPTask.DLL的DLLRun导出函数，弹出的热点资讯广告窗口以及浏览器广告弹窗：

![image23.png](https://image.3001.net/images/20190712/1562909042_5d28197251f0c.png!small)

###  **2.3** **命令行：RunTask2**

 **功能：自更新**

配置文件解密后，内容如下，其中的Url则为病毒的更新升级链接：

![image24.png](https://image.3001.net/images/20190712/1562909061_5d2819854a657.png!small)![image25.png](https://image.3001.net/images/20190712/1562909061_5d28198594c0e.png!small)

###  **2.4** **命令行：RunTask5**

 **功能：下载暗刷模块Flush.DLL**

执行该命令行后，会检测当前环境是否存在FIDDLER、WIRESHARK等抓包工具，若存在，则不继续执行，防止被人发现：

![image26.png](https://image.3001.net/images/20190712/1562909086_5d28199e82c1e.png!small)

通过检测后，会去下载<http://biz.chlbiz.com/files/eyepatron/conf/specaltask.dat>文件，该文件解密后内容如下：

![image27.png](https://image.3001.net/images/20190712/1562909098_5d2819aa600bf.png!small)

Bsh.gjf为一个加密的DLL文件，解密后为flush.DLL，该DLL会加密数据包，然后请求59.57.13.147:80，返回又会得到一个配置文件，内容如下：

![image28.png](https://image.3001.net/images/20190712/1562909106_5d2819b20dd88.png!small)

其中的content字段的内容，不难看出是一个暗刷脚本相关的配置：

![image29.png](https://image.3001.net/images/20190712/1562909113_5d2819b959bd2.png!small)

此处会打开2个链接<http://ysw.jxdaguanlou.com/web_sid=201907041500>和corneey.com/w1HYGz，其中，corneey.com/w1HYGz是个短链接服务商，最终会跳向病毒作者的网站[www.chl.one](http://www.chl.one)：

![image30.png](https://image.3001.net/images/20190712/1562909127_5d2819c79f079.png!small)

##  **三、溯源**

在该网站（[www.chl.one](http://www.chl.one)）的“联系我们”页面和页面代码中，留有“疑似”作者的联系信息：

![image31.png](https://image.3001.net/images/20190712/1562909145_5d2819d9aa964.png!small)![image32.png](https://image.3001.net/images/20190712/1562909154_5d2819e2ea0bb.png!small)

经过对该邮箱注册的域名反查得到的姓名信息，以及该电话号码支付宝的使用者的姓名信息，基本可以确定为真实有效的联系方式：

![image33.png](https://image.3001.net/images/20190712/1562909166_5d2819ee61ac0.png!small)

而独狼的相关上报数据网站，页面数据如下，能看出也是一家广告投放类业务为主的公司：

![image34.png](https://image.3001.net/images/20190712/1562909174_5d2819f6b1183.png!small)

###  **MD5：**

59bd8b1b0a320c153b2529e3bf9bf91f

e36a2683ab0de87f0cd642ac43187f5d

10ba3d14559b9dd0cfa91c687f921459

740cab39d4641e198a8d93456c8214b3

5e4ccdcde107f4a32160769e44baf821

195ab3727e6273a141b90d37814460f1

d618112a4b9acf79f18077aad286a1b5

6c4dc84fe73262ab403fcc324b1a6ed2

d887af476984c992da6b9f44e04011a8

###  **签名：**

南京星洪科技有限公司

###  **URL** **：**

<http://www.chl.one/>

 ***本文作者：安全豹，转载请注明来自FreeBuf.COM**

