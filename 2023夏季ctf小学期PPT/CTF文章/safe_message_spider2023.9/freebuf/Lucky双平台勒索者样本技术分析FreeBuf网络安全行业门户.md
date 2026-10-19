作者：360企业安全·华南基地

发布机构：威胁情报中心

lucky是一款具备超强传播能力的勒索者，360威胁情报中心最早监测到该样本于2018-11-03开始在互联网络活动，通过多种漏洞利用组合进行攻击传播，同时支持Windows和Linux两种操作系统平台，加密算法采用高强度的RSA+AES算法。同时该样本还会进行挖矿木马的种植。仅在2018年11月内，已监测到受影响的机构和个人约1000例左右。

![image.png](https://image.3001.net/images/20181128/1543392627_5bfe4d73dbb06.png!small)  

##  **传播模块分析**

Lucky模块之一为.conn，该模块与Satan(勒索者）的传播模块基本上一致，主要利用以下漏洞进行攻击。

横向攻击手法&漏洞利用  
---  
Apache Struts2远程代码执行漏洞  
CVE-2018-1273漏洞  
Tomcat web管理后台弱口令爆破  
系统账户弱口令爆破  
JBoss反序列化漏洞(CVE-2013-4810)  
JBoss默认配置漏洞(CVE-2010-0738)  
Weblogic WLS 组件漏洞（CVE-2017-10271）  
Apache Struts2远程代码执行漏洞S2-045  
Apache Struts2远程代码执行漏洞S2-057  
Windows SMB远程代码执行漏洞MS17-010  
Weblogic 任意文件上传漏洞(CVE-2018-2894)  
Tomcat文件任意上传漏洞  
  
  
通过分析Conn模块发现在该Linux样本中发现了大量“.exe”的字样，可以确定该样本是个跨平台攻击样本，通过Web应用漏洞对Windows、Linux服务器进行无差别、无缝隙的攻击。

![image.png](https://ti.360.net/uploads/2018/11/28/e63dba406b0491c811b025f315edb0d0.png)

###  **主要利用的漏洞**

####  **1\. ApacheStruts2远程代码执行漏洞**

  

![image.png](https://ti.360.net/uploads/2018/11/28/e0180f253dadad743c70442845da37bf.png)

 **2. **CVE-2018-1273 漏洞****  

 **
**![2.png](https://image.3001.net/images/20181128/1543392766_5bfe4dfe62900.png!small)  
  
****

针对Windows系统，利用
CVE-2018-1273上传fast.exe病毒Downloader至C盘根目录下，下载地址为：hxxp://111.90.158.225/d/fast.exe，截至目前能下载到该样本(MD5:
fae322a3ec89c70cb45115779d52cf47)。

  

![image.png](https://image.3001.net/images/20181128/1543372271_5bfdfdefbd422.png!small)

针对Linux系统
，利用CVE-2018-1273漏洞上传ft32和ft64病毒Downloader至服务器，下载地址分别为hxxp://111.90.158.225/d/ft32和
hxxp://111.90.158.225/d/ft64。

  

![image.png](https://image.3001.net/images/20181128/1543372278_5bfdfdf6e605a.png!small)

####  **3.Tomcat管理后台弱口令爆破**  

  

![image.png](https://image.3001.net/images/20181128/1543372283_5bfdfdfb3652a.png!small)

####  **4\. 尝试爆破系统账户和密码**  

另外，除了Tomcat的弱口令爆破，还会去尝试爆破系统账户和密码。

  

![image.png](https://image.3001.net/images/20181128/1543372288_5bfdfe00d9bc7.png!small)

####  **5.JBoss反序列化漏洞利用**  

  

![image.png](https://image.3001.net/images/20181128/1543372294_5bfdfe06f1a64.png!small)

####  **6.JBoss默认配置漏洞**  

  

![image.png](https://image.3001.net/images/20181128/1543372304_5bfdfe103767c.png!small)

####  **7.Weblogic WLS 组件漏洞**  

  

![image.png](https://image.3001.net/images/20181128/1543372311_5bfdfe17640c0.png!small)

####  **8.Struts2远程执行S2-057漏洞**  

  

![image.png](https://image.3001.net/images/20181128/1543372317_5bfdfe1d2ae52.png!small)

####  **9.Struts2远程执行S2-045**  

#### 根据目标OS执行不同的恶意命令。

  

![image.png](https://image.3001.net/images/20181128/1543372324_5bfdfe2409236.png!small)

####  **10．Windows SMB远程代码执行漏洞MS17-010（永恒之蓝）**  

####  Conn模块会通过永恒之蓝工具进行横向移动。

  

**11\. Weblogic任意文件上传漏洞(CVE-2018-2894)**

![3.png](https://image.3001.net/images/20181128/1543392959_5bfe4ebf5f69f.png!small)

 **12\. Tomcat文件任意上传漏洞**  
![4.png](https://image.3001.net/images/20181128/1543392959_5bfe4ebf6a0fb.png!small)  

###  **Linux勒索部分分析**

Lucky勒索者会加密以下后缀名的文件：

bak zip sql mdfldf myd myi dmp xls doc txt ppt csv rtf pdf db vdi vmdk vmx tar
gz pem pfx cerps

  

![image.png](https://image.3001.net/images/20181128/1543372329_5bfdfe29e36b7.png!small)

加密过程中发现为以下目录则直接返回跳过：

/bin, /boot,/sbin , /tmp, /etc, /etc, /lib

  

![image.png](https://image.3001.net/images/20181128/1543372337_5bfdfe31246d6.png!small)

病毒使用RSA+AES 的加密方式对文件进行加密。

  

![image.png](https://ti.360.net/uploads/2018/11/28/71fe91fda290d2bb2fff1630fde94cc6.png)

最后生成加密勒索信息,并将文件名改成[nmare@cock.li]+文件名 + Session + lucky后缀

  

![image.png](https://image.3001.net/images/20181128/1543372369_5bfdfe513d9e4.png!small)

再将被加密文件的数量、大小、session等信息上传到C2地址为111.90.158.225的服务器上。

  

![image.png](https://image.3001.net/images/20181128/1543372375_5bfdfe5781b0c.png!small)

##  **Fast模块分析**

上文说到，针对windows平台，会在c:\释放一个文件fast.exe,
该文件其实是一个Downloader，分别去下载conn.exe和srv.exe到C：\Program Files\Common
File\System目录下然后调用ShellExecute去执行该文件。

  

![image.png](https://image.3001.net/images/20181128/1543372382_5bfdfe5eb228f.png!small)

##  **Conn模块分析**

Conn主要的功能是负责windows平台上的横向移动,
使用到的漏洞和上文中提到的一致，首先Conn会从资源中释放出永恒之蓝攻击模块和Mimikatz（mmkt.exe）到C:\Users\All
Users目录下，如下图。

  

![image.png](https://image.3001.net/images/20181128/1543372390_5bfdfe668af34.png!small)

动态调试结果如下。

  

![image.png](https://image.3001.net/images/20181128/1543372396_5bfdfe6c40464.png!small)

当释放完永恒之蓝攻击模块后，将会先启动 mmkt.exe获取到windows账户密码，用于新起线程进行攻击工作，其中线程一启动永恒之蓝攻击模块,
如果是64位系统，则使用down64.dll作为payload 来使用。

  

![image.png](https://image.3001.net/images/20181128/1543372401_5bfdfe71b56bc.png!small)

该payload会下载fast.exe。  

  

![image.png](https://image.3001.net/images/20181128/1543372407_5bfdfe773a449.png!small)

线程二进行web服务的攻击。

  

![image.png](https://image.3001.net/images/20181128/1543372412_5bfdfe7c27b48.png!small)

以下是conn.exe使用到的Weblogic ,Struts2, JBoss等漏洞攻击
payload，详细的漏洞攻击情况已在上面漏洞版面讲述，就不再赘述了。

  

![image.png](https://image.3001.net/images/20181128/1543372417_5bfdfe81211f6.png!small)

##  **Srv模块分析**

首先该模块会去读一下版本配置文件，检测一遍是否要更新。当前分析时最新版本为1.13。

  

![image.png](https://image.3001.net/images/20181128/1543372423_5bfdfe8701eb3.png!small)

接着下载cpt.exe 和mn32.exe到C:\Program Files\CommonFiles\System目录下并执行。

  

![image.png](https://image.3001.net/images/20181128/1543372427_5bfdfe8b6bc06.png!small)

执行完上述逻辑后，然后判断参数一，是否等于1或者2，如果参数一等于1则调用StartServiceCtrlDispatcherA函数启动服务的回调函数,
如果参数一等于2，再判断参数二的参数是install还是removesrv，分别为安装服务和卸载服务的功能。

  

![image.png](https://image.3001.net/images/20181128/1543372432_5bfdfe90c59d9.png!small)

创建的服务名称叫作LogsServic指向srv本身。

  

![image.png](https://image.3001.net/images/20181128/1543372438_5bfdfe96dff23.png!small)

最后获取系统信息后拼接参数向服务端发送系统配置等信息。

[http://111.90.158.225/token.php?sys=&c_type=&dis_type#=&ver=](http://111.90.158.225/token.php?sys=&c_type=&dis_type&num=&ver=)

  

![image.png](https://image.3001.net/images/20181128/1543372446_5bfdfe9ed632f.png!small)

##  **Cpt模块分析**

Cpt为windows版本的勒索加密者逻辑和linux的一样，首先它尝试关闭一些数据库服务及进程以解除文件占用，方便对文件进行加密。

  

![image.png](https://image.3001.net/images/20181128/1543372453_5bfdfea56268c.png!small)

cpt.exe主要感染以下类型文件：

.bak.sql.mdf.ldf.myd.myi.dmp.xls.xlsx.docx.pptx.eps.txt.ppt.csv.rtf.pdf.db.vdi.vmdk.vmx.pem.pfx.cer.psd

  

![image.png](https://image.3001.net/images/20181128/1543372460_5bfdfeac6fd30.png!small)

不加密含有如下字符串的路径：

windows , python2, python3 , microsoft games , boot , i386 , intel , dvd maker
,recycle ,jdk,lib ,libs ,allusers ,360rec ,360sec ,360sand ,favorites ,common
files,internet explorer ,msbuild ,public ,360downloads ,windows defen ,windows
mail,windows media pl ,windows nt ,windows photo viewer ,windows sidebar
,defaultuser

通过该排除路径的信息，我们猜测该勒索者为国人制作。

同样windows版本的勒索加密部分和linux一样也是lucky后缀。

  

![image.png](https://image.3001.net/images/20181128/1543372466_5bfdfeb283cd5.png!small)

同样加密算法采用AES+RSA加密。

  

![image.png](https://image.3001.net/images/20181128/1543372471_5bfdfeb7a2f44.png!small)

最后将session ID 文件个数，文件大小，系统，等等信息上报到服务端。

  

![image.png](https://image.3001.net/images/20181128/1543372477_5bfdfebd822d7.png!small)

##  **Mn32模块分析**

该模块是挖矿木马使用了如下开源代码。

<https://github.com/alloyproject/xmrig/blob/master/src/core/ConfigLoader_platform.h>

  

![image.png](https://image.3001.net/images/20181128/1543372488_5bfdfec8be8b8.png!small)

挖矿木马的矿池地址如下：  

  

![image.png](https://image.3001.net/images/20181128/1543372495_5bfdfecf73730.png!small)

##  **总结 &防御策略**

该样本使用多种漏洞攻击组合，进行勒索和挖矿等行为，应给系统和应用打全补丁切断传播途径，关闭不必要的网络共享端口，关闭异常的外联访问。  

**附录IOC：**

样本说明：

文件名：.conn

MD5：84DDEE0187C61D8EB4348E939DA5A366

文件名: .crypt

MD5：D1AC4B74EE538DAB998085E0DFAA5E8D

文件名: srv

MD5：E7897629BA5B2D74418D9A9B6157AE80

文件名: cpt.exe

MD5：36E34E763A527F3AD43E9C30ACD276FF

文件名: mn2.exe

MD5：D1AC4B74EE538DAB998085E0DFAA5E8D

文件名：ft32

MD5：8D3C8045DF750419911C6E1BF493C747

文件名：ft64

MD5：E145264CFFA3C01A93871B27A4F569CC

C2 地址:

111.90.158.225

##  

  

