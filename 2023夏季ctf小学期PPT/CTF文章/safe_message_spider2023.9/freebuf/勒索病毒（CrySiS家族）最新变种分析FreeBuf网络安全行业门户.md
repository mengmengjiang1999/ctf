近期，天融信阿尔法实验室捕获到了一款最新的勒索病毒软件，经过分析确定该样本是CrySiS家族的变种。  

 ****

## 一、现象描述

被该病毒感染后的机器桌面上有多个同样的勒索声明窗口，如下图1-1：

![image.png](https://image.3001.net/images/20180820/1534745562_5b7a5bdaa7133.png!small)

图1-1勒索声明

注：加密后的文件名都形如带“id-186103BD” 为磁盘ID也作为声明中感染机器的ID。

硬盘内的除系统所有文件全部被加密了，加密后的文件全部以“.arrow”结尾，如图1-2所示;

![image.png](https://image.3001.net/images/20180820/1534745582_5b7a5bee4493d.png!small)

图1-2加密后的文件名

另外在加密目录里还有一个勒索提示说明文件图1-3：

![image.png](https://image.3001.net/images/20180820/1534745627_5b7a5c1b03230.png!small)

图1-3 加密提示

注：提示感染机器文件已经被锁定，想要解密通过邮件联系作者。

## 二、 样本的基本信息

该勒索病毒的软件基本信息如下：

![image.png](https://image.3001.net/images/20180820/1534745645_5b7a5c2d5652f.png!small)

根据勒索病毒加密后文件命名特点和勒索声明的文字描述，同时对其二进制代码深入分析，判定该勒索病毒为CrySiS家族的样本的最新变种。

该家族可追溯到2016年开始具有勒索活动，2017年5月份采用RDP暴力破解方式进行植入服务器进行勒索，加密后文件后以java后缀结尾，2017年8月发现一个新变种,加密后的文件名以“.arena”结尾，中国境内的工厂受到攻击的较多，2018年6月出现一个新变种，后缀“.bip”结尾，7月最新变种增加了感染文件种类。

![image.png](https://image.3001.net/images/20180820/1534745665_5b7a5c41d2115.png!small)

图2-1crysis家族事件

## 三、勒索软件技术分析

 **该勒索病毒与同家族以前版本不同点在于：**

（1）加了UPX壳，也是为了减少体积更易于传播；

（2）启动开始绘制200*200的窗口，位置在不可见处，在这该窗口中会获取0x774的控件ID字符串，实际上这个窗口没有意义；

（3）监控剪切板，若非空，就会清理；

（4）增加了感染文件种类，比6月份(bip)版本多22种；

（5）加密后的文件名以“[decrypthelp@qq.com].arrow”结尾。

 **与以往版本相同点：**

会添加注册表和系统Startup启动项，删除磁盘卷影以免磁盘恢复，杀死重要进程，为了加密文件时，解除文件占用，遍历A~Z的逻辑磁盘进入加密线程，另启线程来解密准备进行加密文件的可执行代码，之后采用RSA+AES加密算法进行文件加密。

 ****

### 3.1 样本整体行为

勒索软件的整体行为如图3-1

![image.png](https://image.3001.net/images/20180820/1534745730_5b7a5c82144da.png!small)  

图3-1勒索病毒整体行为

### 3.2 绘制窗口

该窗口坐标为（0，0，200，200）在计算机屏幕上看不到，实际上没有用处。

![image.png](https://image.3001.net/images/20180820/1534745755_5b7a5c9bbdbc9.png!small)

 **** 3.3 监控剪切板

若剪切板有数据就清空，以防止发现时数据备份不成功。

![image.png](https://image.3001.net/images/20180820/1534745778_5b7a5cb265ed8.png!small)

### 3.4 禁止文件重定向

勒索病毒有调用“Wow64DisableWow64FsRedirection”API，该功能为：在64位系统下，禁止系统目录重定向到Syswow64目录下，为以管理员身份运行复制自身到system32目录下做准备，实际上并不能以管理员身份运行。

### 3.5 获取网络arp信息

通过调用GetExtentedTcpTable和GetIpNetTable获取邻近主机IP，但没有对IP列表做任何操作。可能这个变种的作者删除了自我攻击传播的功能，这与以往勒索软件不同，以往勒索软件会把获取的邻近
ip作为攻击的目标。

  
  

![image.png](https://image.3001.net/images/20180820/1534745805_5b7a5ccde4cbe.png!small)  
![image.png](https://image.3001.net/images/20180820/1534745824_5b7a5ce09cb42.png!small)  

获取的arp信息，直接释放内存，没有任何操作：

  
![image.png](https://image.3001.net/images/20180820/1534745854_5b7a5cfed18f6.png!small)  

### 3.6 网络Socket活动

创建一个socket，设置为非阻塞模式，实际这些网络活动并没有用。![image.png](https://image.3001.net/images/20180820/1534745884_5b7a5d1ca2c38.png!small)![image.png](https://image.3001.net/images/20180820/1534745888_5b7a5d20d8bbf.png!small)

### 3.7 复制自身到startup目录

把自身复制到“C:\Users\apple\AppData\Roaming\Microsoft\Windows\StartMenu\Programs\Startup”和“C:\Users\apple\AppData\Roaming”目录，

机器感染后勒索病毒（名称为iMounttain.exe）会复制到：

（1）开始菜单启动项目，其中info.hta为勒索声明内容

![image.png](https://image.3001.net/images/20180820/1534745934_5b7a5d4e31ba9.png!small)

  
  

（2）用户的Roaming目录里

![image.png](https://image.3001.net/images/20180820/1534745953_5b7a5d61acf34.png!small)  

### 3.8 以管理员身份启动自身，复制自身添加注册表启动项

创建新线程以管理员身份执行自身

![image.png](https://image.3001.net/images/20180820/1534745982_5b7a5d7e1945a.png!small)  
  

系统会询问是否执行：

![image.png](https://image.3001.net/images/20180820/1534746000_5b7a5d908619c.png!small)  

若点击“是”后会把自身复制到system32目录下，并添加注册表启动项目

![image.png](https://image.3001.net/images/20180820/1534746013_5b7a5d9d227f4.png!small)

### 3.9 删除磁盘卷影

采用执行cmd进程命令执行删除磁盘卷影命令（mode con cp select=125 vssadmin delete shadows
/all），以免恢复磁盘

  
![image.png](https://image.3001.net/images/20180820/1534746032_5b7a5db01fe77.png!small)  

杀死关键进程，以避免加密时文件占用,主要以下进程：

 **mysqld.exe**

 **postgres.exe**

 **mysqld-nt.exe**

 **sqlservr.exe**

 **1cv77.exe**

 **1c8.exe**

 **outlook.exe**

 **services.exe**

结束进程：

  
![image.png](https://image.3001.net/images/20180820/1534746049_5b7a5dc17dc28.png!small)  

### 3.10 磁盘遍历

遍历主机磁盘（ABCDEFGHIJKLMNOPQRSTUVWXYZ）进入加密线程

![image.png](https://image.3001.net/images/20180820/1534746066_5b7a5dd2dd90c.png!small)  
  

该勒索软件把可执行的代码和API都加密保存，阻止静态分析，下面是解密后的API调用入口：

  
![image.png](https://image.3001.net/images/20180820/1534746084_5b7a5de436b05.png!small)  

## 四、文件加密技术

加密目标文件类型，经过统计共365种类型的文件：

1cd",1r4x",3ds",3fr",3g2",3gp",7z",accda",accdb",accdc",accde",accdt",accdw",adb",adp",ai",ai3",ai4",ai5",ai6",ai7",ai8",anim",arrow",arw",as",asa",asc",ascx",asm",asmx",asp",aspx",asr",asx",avi",avs",backup",bak",bat",bay",bootfont",bd",Bin",bmp",bz2",c",cdr",cer",cf",cfc",cfm",cfml",cfu",chm",cin",class",clb",clx",config",cpp",cr2",crt",crw",cs",css",csv",cub",dae",dat",db",dbf",dbx",dc3",dcm",dcr",deepscan",der",dib",dic",dif",divx",djvu",dll,dll",dng",doc",doc;,docm",docx",dot",dotm",dotx",dpx",dqy",DS_Store",dsn",dt",dtd",dwg",dwt",dx",dxf",edml",efd",elf",emf",emz",epf",eps",epsf",epsp",erf",exe,exe",EXE",1cv77",exe",exr",f4v",fido",flm",flv",frm",fxg",geo",gif",grs",gz",h",hdr",hpp",hta",htc",htm",html",icb",ics",id-",iff",inc",indd",ini",iqy",j2c",j2k",java",jp2",jpc",jpe",jpeg",jpf",jpg",jpx",js",jsf",json",jsp",kdc",kmz",kwm",lasso",lbi",lgf",lgp",log",LOG1",LOG2",m1v",m4a",m4v",max",md",mda",mdb",mde",mdf",mdw",mef",mft",mfw",mht",mhtml",mka",mkidx",mkv",mos",mov",mp3",mp4",mpeg",mpg",mpv",mrw",msg",mxl",myd",myi",nef",nrw",obj",odb",odc",odm",odp",ods",oft",one",onepkg",onetoc2",opt",oqy",orf",p12",p7b",p7c",pam",pbm",pct",pcx",pdd",pdf",pdp",pef",pem",pff",pfm",pfx",pgm",php",php3",php4",php5",phtml",pict",pl",pls",pm",png",pnm",pot",potm",potx",ppa",ppam",ppm",pps",ppsm",ppt",pptm",pptx",prn",propdesc",ps",psb",psd",pst",ptx",pub",pwm",pxr",py",qt",r3d",raf",rar",raw",rdf",rgbe",rle",rqy",rss",rtf",rw2",rwl",safe",sct",sdpx",shtm",shtml",slk",sln",sql",sr2",srf",srw",ss,ss",ssi",st",stm",svg",svgz",swf",sys",tab",tar",tbb",tbi",tbk",tdi",tga",thmx",tif",tiff",tld",torrent",tpl",ttf",txt",u3d",udl",uxdc",vb",vbs",vcs",vda",vdr",vdw",vdx",vrp",vsd",vss",vst",vsw",vsx",vtm",vtml",vtx",wav",wb2",wbm",wbmp",wim",wmf",wml",wmv",wpd",wps",x3f",xl",xla",xlam",xlk",xlm",xls",xlsb",xlsm",xlsx",xlt",xltm",xltx",xlw",xml",xps",xsd",xsf",xsl",xslt",xsn",xtp",xtp2",xyze",xz",zip"

### 4.1 加密准备

加密之前需要查找以上文件类型，并查找局域网中的共享文件，同时要检查文件大小，若文件大小大于0x180000，就会采用大文件加密方法进行加密。

### 4.2 整体文件加密过程

文件加密过程

![image.png](https://image.3001.net/images/20180820/1534746104_5b7a5df82c83b.png!small)

图4-2勒索病毒文件加密过程

###  **4.2.3** **遍历本机文件并查找符合条件的文件**

比较文件：

**![image.png](https://image.3001.net/images/20180820/1534746120_5b7a5e0859777.png!small)**

### 4.2.4 同时枚举网络资源加密共享文件

**![image.png](https://image.3001.net/images/20180820/1534746138_5b7a5e1a96bb5.png!small)**

4.2.5通过ReadFile方式把文件内容读入内存，之后完成AES加密，最后以WriteFile方式写入文件保存加密后的内容。

![image.png](https://image.3001.net/images/20180820/1534746148_5b7a5e24d8442.png!small)

写入加密后的文件

![image.png](https://image.3001.net/images/20180820/1534746165_5b7a5e3569b1a.png!small)

  

###  **4.2.6** **大文件加密**

文件大小大于0x180000就会把加密后的内容写入原文件，采用MoveFile对原文件进行更名，以“.arrow”结尾，而不删除原文件。

![image.png](https://image.3001.net/images/20180820/1534746188_5b7a5e4c9f88e.png!small)

###  **4.2.7** **正常文件加密**

对于文件大小小于或等于0x180000就会把加密后的内容写入新建以“.arrow”结尾

文件中，之后删除原文件。

从原始文件读出明文，如下：

![image.png](https://image.3001.net/images/20180820/1534746204_5b7a5e5c6958c.png!small)

写入新文件，如下：

![image.png](https://image.3001.net/images/20180820/1534746217_5b7a5e69a94c4.png!small)删除原文件：  

![image.png](https://image.3001.net/images/20180820/1534746227_5b7a5e73dd1cb.png!small)

###  **4.3** **加密技术**

 ****
加密采用AES加密，密钥AESKEY为256bit，加密后会把AESKEY采用RSA加密（公钥为内置1024bit）和最后一次的IV写入加密文件中，加密算法并不使用公开的加密库，而是把所有加密算法直接写入程序中。

加密时，首先把文件内容读入内存，依次用其16字节每4字节倒序（为计算时采用原文件字节顺序）进行IV异或计算（BUF xor IV），之后再进行AES加密。

 ****

**加密技术如下：**

勒索软件加密技术展现如图4-3

![image.png](https://image.3001.net/images/20180820/1534746248_5b7a5e8800ddc.png!small)

图4-3勒索软件加密过程展现

 **4.3.1 AESKEY** **随机生成**

随机生成32字节AESKEY（前4字节为时间），汇编指令采用rdtsc指令为cpu自启动运行时间周期，这样也可以理解为随机密钥，再用RSA公钥计算SHA1对其32随机数进行更新，生成AESKEY，初始IV，是随机生成16字节（前4字节为时间），再用计算SHA1对其16随机数进行更新，来生成IV。

![image.png](https://image.3001.net/images/20180820/1534746260_5b7a5e9409e93.png!small)

计算SHA1  

![image.png](https://image.3001.net/images/20180820/1534746272_5b7a5ea0a419f.png!small)  
计算SHA1更新随机32字节AESKEY  

![image.png](https://image.3001.net/images/20180820/1534746290_5b7a5eb2a591f.png!small)  

经过RSA加密，是为了加密后的AESKEY保存在加密文件中，为其解密之用：

![image.png](https://image.3001.net/images/20180820/1534746308_5b7a5ec406b6d.png!small)

 **4.3.2 RSA** **公钥**

RSA公钥是内置的需要时采用RC4解密出，才能使用。

**![image.png](https://image.3001.net/images/20180820/1534746317_5b7a5ecd3dd2d.png!small)**

 **RSA** **公钥为数据选择部分：**

![image.png](https://image.3001.net/images/20180820/1534746338_5b7a5ee28d798.png!small)

 **4.3.3** **初始** **IV** **的生成**

初始IV为随机16字节，计算SHA1进行更新

![image.png](https://image.3001.net/images/20180820/1534746347_5b7a5eeb63825.png!small)  

 **计算IV** **的输出作为AES** **加密函数的输入：**

![image.png](https://image.3001.net/images/20180820/1534746358_5b7a5ef6395fa.png!small)

 **4.3.4 AES** **加密**

文件内容进行AES加密时，依次用文件内容的16字节，采用IV进行xor计算，之后AES加密，最后保存，代码如下：

![image.png](https://image.3001.net/images/20180820/1534746373_5b7a5f057cbd2.png!small)

 **4.3.5** **加密过程动态调试**

4.3.5.1文件读入内存

![image.png](https://image.3001.net/images/20180820/1534746388_5b7a5f1458496.png!small)

取16字节，每4字节倒序，为计算时保持文件顺序：

![image.png](https://image.3001.net/images/20180820/1534746399_5b7a5f1fc59a7.png!small)

4.3.5.2与IV进行xor计算：

![image.png](https://image.3001.net/images/20180820/1534746411_5b7a5f2bc76e1.png!small)

4.3.5.3进行AES加密

![image.png](https://image.3001.net/images/20180820/1534746424_5b7a5f38b774d.png!small)

4.3.5.4经过亦或的iv明文：

![image.png](https://image.3001.net/images/20180820/1534746435_5b7a5f43567da.png!small)

4.3.5.5加密后：

![image.png](https://image.3001.net/images/20180820/1534746445_5b7a5f4dd5bde.png!small)

 **4.3.6 AES** **加密后的文件密钥保存**

AES加密后的密文写入新的文件文件名以“Id-xxxxxxxx.[decrypthelp@qq.com.arrow]”结尾，写完密文后会把文件名，最后加密的IV和经过RSA加密后的AESKEY写入本次加密的密文的后面。

![image.png](https://image.3001.net/images/20180820/1534746457_5b7a5f59c008d.png!small)

这样解密时，需要用RSA私钥解密出AESKEY，采用最后加密的IV，按照上述加密的反过程就可以解密了。或可以采用尝试购买作者的解密工具，找到RSA私钥，就可以全部文件解密。  

**4.3.7** **原文件的删除**

加密数据写入新文件（Id…arrow）,设置文件文件末尾。

![image.png](https://image.3001.net/images/20180820/1534746473_5b7a5f697c1a7.png!small)

设置加密后的新文件属性

![image.png](https://image.3001.net/images/20180820/1534746483_5b7a5f73168ec.png!small)删除原文件：  

![image.png](https://image.3001.net/images/20180820/1534746492_5b7a5f7c96c6f.png!small)

## 五、总结与建议

该勒索软件主要针对于windows的服务器，特别是企业服务器比如工厂等，重要的是安全防范有疏漏，容易受攻击。它采用当前流行的强加密算法（RSA+AES）理论上受害者是无法解开的。

若有客户联系作者购买了解密工具，请联系我们，我们会从解密工具中尝试找到关键密钥便可以解密全部文件。

对勒索软件防范建议：

（1） 及时给服务器打补丁，修补漏洞；

（2） 对重要文件实时进行远程备份；

（3） 对重要文件尽量不要共享在局域网上；

（4） 不要点击来历不明的邮件和附件。

