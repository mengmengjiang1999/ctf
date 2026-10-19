## **背景** ****

账户密码作为凭证信息的一个子集，一直都是用户最为重视地方，而从用户登陆机制出现的那一刻起，凭证窃取类木马便源源不断的出现，就常见的Agentesla便是其中一种。

而近期，奇安信病毒响应中心发现多个利用CVE-2017-11882漏洞文档下载窃取用户凭证的恶意文档，最后会释放Agentesla变种。

## **样本分析** ****

###  **漏洞文档分析** ****

诱饵名为Request for Quotation.doc，为一贯的商贸信名称，中文翻译为报价要求。

文档启动之后漏洞在地址0x00415A7函数中触发，EAX的位置指向ShellCode保存的地址：

![图片.png](https://image.3001.net/images/20191015/1571105867_5da52c4b6a458.png!small)  

ShellCode执行之后调用URLDownloadToFileA从bit.ly/33fuZgy(短链接经过解析之后地址为：hxxp://gessuae.ae/wp-includes/fonts/lav.jpg)下载payload到Local目录下，payLoad名称为X098765432198.exe。

![图片.png](https://image.3001.net/images/20191015/1571105878_5da52c56e0174.png!small)

调用WinExec执行该EXE，随后调用ExitProcess退出EQNEDT32.EXE公式编辑器。即可在用户无感知的情况下入侵用户系统。

![图片.png](https://image.3001.net/images/20191015/1571105891_5da52c635c5d9.png!small)  

###  **Pay** **Load** **分析** ****

该样本为C#编写的可执行文件，该文件在攻击者服务器上名称为lav.jpg，下载到用户电脑之后的名称为X098765432198.exe，参考编译时间为2019年10月10号。

![图片.png](https://image.3001.net/images/20191015/1571105910_5da52c760156d.png!small)  

该EXE启动之后会在Main函数中获取资源名称为“compressed”的资源，调用Decompress解密该资源并在内存中执行。

![图片.png](https://image.3001.net/images/20191015/1571105921_5da52c817fed2.png!small)  

Compressed资源数据解密并Dump脱壳之后实际也是一个C#编写的PE文件。

该EXE启动之后在Main函数之前会获取系统详细信息，包括实际出口IP地址、计算机名称、用户名称、系统版本信息、系统启动模式、物理内存大小、虚拟内存大小以及当前日期。

![图片.png](https://image.3001.net/images/20191015/1571105938_5da52c92dce07.png!small)![图片.png](https://image.3001.net/images/20191015/1571105942_5da52c96cc663.png!small)

  

代码执行时使用的字符串均使用AES加密并进行Base64编码，每一个加密字符串对应一个不同的解密Key。解密算法如下：

![图片.png](https://image.3001.net/images/20191015/1571105956_5da52ca413135.png!small)  

通过ipconfig.me/ip获取出口IP地址：

![图片.png](https://image.3001.net/images/20191015/1571105966_5da52cae84cb2.png!small)  

随后还会设置多个定时器，但是木马作者并没有调用Timer.Start()函数，所以实际中定时器并不会被触发。

![图片.png](https://image.3001.net/images/20191015/1571105984_5da52cc02431d.png!small)  

Main函数中开始准备窃取受害者系统中保存的用户凭证：

获取Chrome用户凭证信息：

![图片.png](https://image.3001.net/images/20191015/1571105994_5da52ccaecb1d.png!small)  

获取\\.purple\accounts.xml" 即pidgin的密凭证信息：

![图片.png](https://image.3001.net/images/20191015/1571106008_5da52cd8a9161.png!small)  

获取Vivaldi的凭证信息：

![图片.png](https://image.3001.net/images/20191015/1571106025_5da52ce9d0c31.png!small)  

获取FTP 凭证信息：

![图片.png](https://image.3001.net/images/20191015/1571106033_5da52cf13cac4.png!small)  

获取Oprea浏览器凭证信息：

![图片.png](https://image.3001.net/images/20191015/1571106042_5da52cfa09c3b.png!small)  

获取OutLook凭证信息：

![图片.png](https://image.3001.net/images/20191015/1571106051_5da52d036917e.png!small)  

获取UC浏览器凭证信息：

![图片.png](https://image.3001.net/images/20191015/1571106062_5da52d0e3e18a.png!small)  

360浏览器凭证信息：

![图片.png](https://image.3001.net/images/20191015/1571106069_5da52d1532267.png!small)  

猎豹浏览器凭证信息：

![图片.png](https://image.3001.net/images/20191015/1571106077_5da52d1ddf14c.png!small)  

获取Thunderbird凭证信息：

![图片.png](https://image.3001.net/images/20191015/1571106086_5da52d26a09f1.png!small)  

FireFox凭证信息：

![图片.png](https://image.3001.net/images/20191015/1571106093_5da52d2d791b7.png!small)  

获取完成并格式化之后通过SMTP发送到指定邮箱：

![图片.png](https://image.3001.net/images/20191015/1571106102_5da52d36d0448.png!small)  

除去使用的SMTP通信方式，该PE中还集成了另外两种通信方式。程序中硬编码的字符串来决定通过哪一种通信方式：

FTP通信：

![图片.png](https://image.3001.net/images/20191015/1571106112_5da52d40622c9.png!small)  

Http通信：当使用通信时候使用"api.telegram.org/bot”接口，数据为：![图片.png](https://image.3001.net/images/20191015/1571106118_5da52d46a4f99.png!small)![图片.png](https://image.3001.net/images/20191015/1571106139_5da52d5bbce89.png!small)

  

通过样本中代码分析发现该程序还包括键盘记录功能：

![图片.png](https://image.3001.net/images/20191015/1571106147_5da52d6339a8b.png!small)  

从传递的邮件内容来看十月三日截至目前攻击者邮箱已陆续收到三十五位受害者账号密码的邮件，邮件内容包含受害者真实IP及用户保存在计算机中的凭证信息，目前受害者IP分布在全球十几个国家和地区。

![图片.png](https://image.3001.net/images/20191015/1571106155_5da52d6b34e03.png!small)  

##  **总结** ****

从攻击者手法上来看，从他使用盗取的邮箱作为用户信息接收点，并使用入侵的网站作为C2，很明显的看出进行黑产木马行业的娴熟程度，而类似这种攻击未来只会越来越多，只因追溯性难度大，常人不会耗费大量资源进行追捕。

奇安信病毒响应中心发现多个同源样本，说明该样本背后的攻击者一直在改进样本功能，样本投递方式依赖nday漏洞，奇安信病毒响应中心提醒用户应及时安装系统补丁，预防此类恶意样本攻击。

目前奇安信全系产品已支持对该攻击活动的检测。

## **IOCs** ****

C &C：

bit.ly/33fuZgy

hxxp://gessuae.ae/wp-includes/fonts/lav.jpg

/wp-includes/fonts/yaa.exe

MD5：

漏洞文档：

14F28BD8361AE90DBFABCB31767A356B

恶意样本：

FA94E348BABC6C9D0FEAF30F6808FA62

71EA6FE86188E0B487EFBC30678115D0

BF1D4F1808F9FFF09D11B8129D58D4C1

8EDA0309EE2D27408ADF1B**EBA14B82

208F55B5AEC627FC100CAD0703CAF78B

E8EA6BC7445469D4983661AA9191313D

8D536592ACC6050087EE8B70F7E79C64

B3B4CBEA2ACB120296A6C1EFA41864F5

840072E60195F3F593768B3DF42CF99D

CEBA49D659E272DCF60A9ACE17F6C521

35961988631D38424F0D43ACDC3D6040

C08304065BD1288863921A5B447946CC

