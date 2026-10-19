作者：启明星辰ADLab

#### 一、事件介绍

近期，启明星辰ADLab收到客户反馈：由于不明原因，电脑中的文件被加密，无法打开。在得知这一消息后，启明星辰ADLab迅速派遣技术人员赶往客户现场。通过对现场感染机勘验后，我们发现加密后的文件被统一冠以“.bip”后缀名，另外我们还发现被加密的文件目录中有一个勒索提示文件“FILES
ENCRYPTED.txt”，它是由勒索病毒创建的，目的是通知受害者其数据已经被加密，如果想要解密文件，需按照攻击者提供的联系方式支付赎金。被加密的文件和“FILES
ENCRYPTED.txt”内容如下：

![](https://images.seebug.org/content/images/2018/06/d975e526-e225-45bc-baf9-95842763f4cc.png-w331s) 被加密的文件和“FILES ENCRYPTED.txt”内容

受感染的电脑在加密完成后或电脑重启后会弹出两个提示框，提示框是由mshta.exe调用Info.hta生成的勒索信息。感染机器的两个Info.hta文件存放路径分别为：

%windir%\System32\Info.hta  
%AppData\Romaing\Info.hta

它的主要功能是提示受害人如何联系黑客、如何获得比特币、如何完成支付等信息，提示框内容如下图所示：

![](https://images.seebug.org/content/images/2018/06/0b5973d2-06b7-4b9a-9e05-c9b5b860b082.png-w331s)
勒索提示框

经过现场对受感染机器的技术分析后，我们找到了该勒索病毒的样本程序，样本相关信息如下表所示：

![](https://images.seebug.org/content/images/2018/06/6dcc9c83-ad6b-4c51-95e7-a2136a93e249.png-w331s)

在对该勒索病毒的行为和二进制代码进行深入分析并与已知勒索病毒家族进行横向比对后，我们判定该勒索病毒属于Crysis家族的一个新变种。该家族主要通过钓鱼邮件和利用RDP（Remote
Desktop Protocol)爆破进行传播。

#### 二、攻击历史

![](https://images.seebug.org/content/images/2018/06/ca8820e1-db79-4775-9c30-6a5dc454c24c.png-w331s)

2016年6月，国外安全专家发现，能够通过Java
Applet传播的跨平台（Windows、MacOS）恶意软件Crysis开始加入勒索功能，并于8月份被发现用于攻击澳大利亚和新西兰的企业。Crysis恶意软件不仅能够感染VMware虚拟机，还能够全面收集受害者的系统用户名密码、键盘记录、系统信息、屏幕截屏、聊天信息，控制麦克风和摄像头，现在又加入了加密勒索功能，其威胁性大有取代TeslaCrypt和Locky勒索软件的趋势。它主要通过暴力破解远程桌面（RDP）协议传播，支持185种文件类型加密。

2016年11月12日，勒索病毒 Crysis解密密钥被公开，Crysis2及3的受害者可通过这个密钥恢复丢失的文件。

2017年5月下旬，Crysis/Dharma病毒出现了一个新的变种.cesar，中国境内有部分个人和企业开始受到攻击。

2017年8月30日，ID-Ransomware的Michael Gillespie发现了Crysis/Dharma 勒索软件一个新的变种, 文件被追加
.arena
扩展名。中国境内个人和企业受到攻击数量显著增多。东莞某手机代工厂中病毒后所有的服务器文件后缀变成了.arena，工厂按照提示信息的地址给黑客付款，付款后黑客就消失了，三天后黑客发来信息称自己在出差，并发来了一个解密工具，工厂解密后发现黑客只解密了部分文件，需要再支付一次才能继续解密。下图的勒索邮件图片来自网络：

![](https://images.seebug.org/content/images/2018/06/90c9be51-ae0b-41b1-b18e-01acaa0af96b.png-w331s)
被二次勒索

2018年3月， Crysis/Dharma 勒索软件出现一个新的变种, 文件被追加.java 扩展名。

2018年5月16日， Crysis/Dharma 勒索软件出现一个新的变种, 文件被追加.bip
扩展名。启明星辰ADLab第一时间发现该变种，并对其进行了深入的分析，由于使用了RSA+AES加密，所以目前尚无法被解密。它支持343种文件格式的加密，比最初增长了1.85倍。

#### 三、勒索病毒技术分析

该勒索病毒使用加密的shellcode，在shellcode中利用换体技术对程序地址空间进行修改，以达到干扰杀毒软件的查杀和对抗二进制分析的目的。加密算法实现上并没有使用常见的加密开源库，所以给逆向人员在算法识别上带来一定的困难。我们在做二进制分析的时候，没有发现勒索软件有网络数据产生，推测是黑客的C&C服务器已经关闭了。

##### 3.1 勒索病毒母体执行

###### 3.1.1 勒索病毒执行流程

勒索病毒运行后，首先利用TEA算法解密shellcode，shellcode解密完成后，便开始执行。shellcode的功能是改写勒索病毒自身内存地址空间，对勒索病毒进行换体。流程图如下：

![](https://images.seebug.org/content/images/2018/06/74c82f35-a143-4998-95bb-c32a0243bedf.png-w331s)

###### 3.1.2 解密shellcode

勒索病毒运行后，首先通过LoadLibraryA函数加载Kernel32.dll，然后利用GetProcAddress动态获取LocalAlloc和VirtualProtect的函数地址，再利用LocalAlloc分配0x11C98大小的内存地址作为shellcode数据的存储空间，通过sub_4011D5函数把数据段中的数据赋值给dw_shellcode地址，使用TEA算法解密dw_shellcode地址的数据，解密完成后调用VirtualProtect函数给shellcode添加执行权限，然后执行shellcode代码，相关代码如下图所示：

![](https://images.seebug.org/content/images/2018/06/4cf40c4d-7b0d-48cb-ba08-96cd9745f625.png-w331s)

在分析shellcode解密代码的时候，根据TEA的魔数特征0xC6EF3720，识别出解密代码的算法是TEA算法，代码如下所示：

![](https://images.seebug.org/content/images/2018/06/c56da645-a2c2-43ac-8a00-3f3323468e5a.png-w331s)

##### 3.2 Shellcode执行

勒索病毒母体执行完毕后，开始执行shellcode代码。在shellcode中动态调用VirtualAlloc分配内存，把新的变体内容拷贝到内存中；调用VirtualProctect修改内存属性，把源程序地址空间清零；使用新的变体内容填充，最后调用VirtualFree释放前面分配的内存。相关代码如下图所示：

![](https://images.seebug.org/content/images/2018/06/57dd541e-6e6e-4aad-a386-e8e5085c8700.png-w331s)

##### 3.3 换体后代码执行

换体完成后，勒索病毒便开始执行变体代码。变体代码首先创建一个互斥，防止自身被多次执行；其次，变体代码创建一个线程，用于监控感染机上指定的进程或服务，该线程每隔500毫秒对感染机上的目标进程或服务进行一次关闭操作；再次，变体代码创建开机自启动注册表项，拷贝自身到注册表项所在目录，以达到开机自启动的目的，然后变体代码删除磁盘卷影，防止受害人恢复数据；最后，变体代码创建一个线程，用于扫描局域网共享目录并对扫描到的文件进行加密。遍历逻辑驱动器，每个驱动器创建一个文件加密线程，对逻辑驱动器下的文件进行加密。该变体代码的执行流程图如下所示：

![](https://images.seebug.org/content/images/2018/06/f83eea9a-4e94-4c76-b016-8ce1d857018e.png-w331s)

###### 3.3.1 创建互斥

勒索病毒的字符串都是使用RC4算法加密的，通过内置的一个128字节密钥进行解密。我们用Ollydbg对字符串解密过程进行动态跟踪，得到了RC4的128字节的密钥，如下所示：

![](https://images.seebug.org/content/images/2018/06/fd7216ef-ebb9-4930-bccd-64488379f40a.png-w331s)

互斥体的名称由三部分组成，第一部分是RC4解密出来的字符串`“Global\syncronize_”`，第二部分是RC4解密出来的字符串“45STKM”，第三部分是根据参数选择，如果参数为1就是“A”，否则是“U”。

最终，勒索病毒会创建两个互斥体
`"Global\syncronize_45STKMA"`和`"Global\syncronize_45STKMU"`，相关代码如下：

![](https://images.seebug.org/content/images/2018/06/ba6ed233-d325-4565-9824-0dbef1cff07b.png-w331s)

###### 3.3.2 解锁文件占用

勒索病毒不但会杀死指定的正在运行的进程而且还会停止指定的正在运行的服务，这样做的好处是解锁对应进程的文件占用，从而保证文件加密成功。勒索病毒会使用上文中的RC4算法解密得到要杀死的进程名称和服务名称。相关代码如下图所示：

![](https://images.seebug.org/content/images/2018/06/9cc90480-6b0f-4ad1-a609-0cb76deaa66c.png-w331s)

进程名和服务名列表如下：

![](https://images.seebug.org/content/images/2018/06/e4c84042-1573-4201-b8cd-156dbb4ae2d8.png-w331s)

勒索病毒在完成字符串解密后，创建一个线程，在线程中遍历系统进程，判断目标进程是否存在，如果存在，就杀死目标进程。相应代码如下所示：

![](https://images.seebug.org/content/images/2018/06/21ec3618-49f1-4735-a15a-db2719f357dd.png-w331s)

遍历系统服务名称，判断服务名称是否存在，如果存在就停止服务。相关代码如下所示：

![](https://images.seebug.org/content/images/2018/06/ed72c538-ae3b-49df-88e9-72ba4c236dfb.png-w331s)

该勒索病毒创建一个线程，每隔500毫秒循环一次，判断相应的进程和服务是否存在，如果存在就杀死，反汇编代码如下所示：

![](https://images.seebug.org/content/images/2018/06/eb87eac8-d659-4786-a3a9-921250e121a0.png-w331s)

###### 3.3.3 添加开机自启动

勒索病毒先拷贝设置到以下目录：

启动目录  
%windir%\System32  
%appdata%  
%sh(Startup)%  
%sh(Common Startup)%

拷贝完成后在注册表HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run下新建3个注册表项，注册表内容如下图所示。

![](https://images.seebug.org/content/images/2018/06/6982a8dc-82c4-4734-8b8d-9ee182e10d76.png-w331s)

`“%AppData\Romaing\Info.hta”`是勒索病毒提示用户解锁的提示文件。通过注册表我们可以看到“Info.hta”文件被拷贝了两份，另外一份是在“%System32%”路径下，可能是黑客为了确保这个提示框被受害人能看到，所以特意写了两个路径。

`“load_.exe”`文件是勒索病毒程序自身的拷贝，这样就可以实现每次开机启动后执行加密逻辑，把受害人新增的文件加密。相关代码如下：

![](https://images.seebug.org/content/images/2018/06/cef09990-bfb0-4b21-8f5d-f49f0adb9822.png-w331s)

拷贝文件添加注册表开机自启动

![](https://images.seebug.org/content/images/2018/06/8e864c5e-77ea-443d-b33c-1bd5195f767a.png-w331s)
%sh(Startup)%目录下的开机自启动程序

![](https://images.seebug.org/content/images/2018/06/0cd3aa20-fbcf-49bd-b639-2e06c56dfc54.png-w331s)
%sh(Common Startup)%目录下的开机自启动程序

![](https://images.seebug.org/content/images/2018/06/ab2d5048-6d0a-4588-9c68-307bd18a1281.png-w331s)
%Appdata%目录下支付勒索的提示程序

![](https://images.seebug.org/content/images/2018/06/ff4d6360-e8af-4b38-a4ca-d2cf15fd4c20.png-w331s)
%windir%\System32目录下的开机自启动程序

###### 3.3.4 删除磁盘卷影

卷影副本功能可提供网络共享上的文件的即时点副本。利用共享文件夹的卷影副本，用户可以查看网络文件夹在过去某一时间点的内容。

勒索病毒会删除磁盘卷影，以防止受害人通过磁盘还原方式对文件进行恢复，删除磁盘卷影的命令为“mode con cp select=1251 vssadmin
delete shadows /all /quiet
Exit”，该命令是用上文中的RC4算法解密出来的。勒索病毒通过调用CreateProcess启动“C:\Windows\system32\cmd.exe”调用删除命令来删除磁盘卷影，相关代码如下图所示：

![](https://images.seebug.org/content/images/2018/06/1e6c71c6-e9ee-4392-b2f7-4b26f7657c63.png-w331s)

###### 3.3.5 枚举局域网的共享目录，对共享目录文件进行加密

该勒索病毒创建一个线程，对局域网中共享的文件进行加密。

![](https://images.seebug.org/content/images/2018/06/67181cdc-506c-4ac9-b684-96f5d2038f5e.png-w331s)
创建加密共享磁盘线程

线程中遍历局域网共享资源，加密文件的核心代码如下：
![](https://images.seebug.org/content/images/2018/06/fc5f0873-e44a-4146-a8ce-0d7c3541b6dc.png-w331s)

###### 3.3.6 遍历本地磁盘，对磁盘目录文件进行加密

该勒索病毒先用上文中的RC4算法解密一段数据，解密后的结果为
“ABCDEFGHIJKLMNOPQRSTUVWXYZ”，通过GetLogicalDrives函数获取磁盘驱动器，然后遍历执行文件加密，相关反汇编代码如下所示：

![](https://images.seebug.org/content/images/2018/06/d46bcc65-c377-4864-bd1f-7f37e81f23f4.png-w331s)

为了保证电脑系统正常启动，勒索病毒对保障操作系统正常运行的文件不加密，并把这些文件的文件名加密存储在程序中。通过上文中的RC4算法解密后的文件名列表如下：

解密后的文件名  
boot.ini  
bootfont.bin  
ntldr  
ntdetect.com  
io.sys

###### 3.3.7 文件加密

勒索病毒支持343种类型文件的加密，文件类型（文件的后缀名）是以分号分割并通过上文中的RC4算法加密存储的，运行时动态解密，解密后的字符串在Ollydbg内存中如下图所示：

![](https://images.seebug.org/content/images/2018/06/5c1b86de-f54d-496d-9413-b1be1c82697d.png-w331s)

支持加密的文档扩展名如下：

    
    
    .1cd;.3ds;.3fr;.3g2;.3gp;.7z;.accda;.accdb;.accdc;.accde;.accdt;.accdw;.adb;.adp;.ai;.ai3;.ai4;.ai5;.ai6;.ai7;.ai8;.anim;.arw;.as;.asa;.asc;.ascx;.asm;.asmx;.asp;.aspx;.asr;.asx;.avi;.avs;.backup;.bak;.bay;.bd;.bin;.bmp;.bz2;.c;.cdr;.cer;.cf;.cfc;.cfm;.cfml;.cfu;.chm;.cin;.class;.clx;.config;.cpp;.cr2;.crt;.crw;.cs;.css;.csv;.cub;.dae;.dat;.db;.dbf;.dbx;.dc3;.dcm;.dcr;.der;.dib;.dic;.dif;.divx;.djvu;.dng;.doc;.docm;.docx;.dot;.dotm;.dotx;.dpx;.dqy;.dsn;.dt;.dtd;.dwg;.dwt;.dx;.dxf;.edml;.efd;.elf;.emf;.emz;.epf;.eps;.epsf;.epsp;.erf;.exr;.f4v;.fido;.flm;.flv;.frm;.fxg;.geo;.gif;.grs;.gz;.h;.hdr;.hpp;.hta;.htc;.htm;.html;.icb;.ics;.iff;.inc;.indd;.ini;.iqy;.j2c;.j2k;.java;.jp2;.jpc;.jpe;.jpeg;.jpf;.jpg;.jpx;.js;.jsf;.json;.jsp;.kdc;.kmz;.kwm;.lasso;.lbi;.lgf;.lgp;.log;.m1v;.m4a;.m4v;.max;.md;.mda;.mdb;.mde;.mdf;.mdw;.mef;.mft;.mfw;.mht;.mhtml;.mka;.mkidx;.mkv;.mos;.mov;.mp3;.mp4;.mpeg;.mpg;.mpv;.mrw;.msg;.mxl;.myd;.myi;.nef;.nrw;.obj;.odb;.odc;.odm;.odp;.ods;.oft;.one;.onepkg;.onetoc2;.opt;.oqy;.orf;.p12;.p7b;.p7c;.pam;.pbm;.pct;.pcx;.pdd;.pdf;.pdp;.pef;.pem;.pff;.pfm;.pfx;.pgm;.php;.php3;.php4;.php5;.phtml;.pict;.pl;.pls;.pm;.png;.pnm;.pot;.potm;.potx;.ppa;.ppam;.ppm;.pps;.ppsm;.ppt;.pptm;.pptx;.prn;.ps;.psb;.psd;.pst;.ptx;.pub;.pwm;.pxr;.py;.qt;.r3d;.raf;.rar;.raw;.rdf;.rgbe;.rle;.rqy;.rss;.rtf;.rw2;.rwl;.safe;.sct;.sdpx;.shtm;.shtml;.slk;.sln;.sql;.sr2;.srf;.srw;.ssi;.st;.stm;.svg;.svgz;.swf;.tab;.tar;.tbb;.tbi;.tbk;.tdi;.tga;.thmx;.tif;.tiff;.tld;.torrent;.tpl;.txt;.u3d;.udl;.uxdc;.vb;.vbs;.vcs;.vda;.vdr;.vdw;.vdx;.vrp;.vsd;.vss;.vst;.vsw;.vsx;.vtm;.vtml;.vtx;.wb2;.wav;.wbm;.wbmp;.wim;.wmf;.wml;.wmv;.wpd;.wps;.x3f;.xl;.xla;.xlam;.xlk;.xlm;.xls;.xlsb;.xlsm;.xlsx;.xlt;.xltm;.xltx;.xlw;.xml;.xps;.xsd;.xsf;.xsl;.xslt;.xsn;.xtp;.xtp2;.xyze;.xz;.zip

文件加密功能是在线程函数中执行的，在加密前，它先进行CRC32校验，确保加密成功，并构造加密后文件名的命名，该恶意程序加密后的文件按照{原始文件名}+{.id-}+{C盘序列号}+{.[filedec@tuta.io]
.bip}方式进行重命名。以“test.txt”为例，加密后的文件名为“test.txt
.id-B05844B5.[filedec@tuta.io].bip”。每个文件都随机生成一个0x16字节的IV，从而保障加密的随机性，线程函数核心代码如下：

![](https://images.seebug.org/content/images/2018/06/47631a72-92c4-48c5-a7bb-9e38f5511312.png-w331s)

在加密文件前，勒索病毒先去掉目标文件的只读属性，待加密完成后再还原其原有的文件属性，相关代码如下所示：

![](https://images.seebug.org/content/images/2018/06/95ede90d-b37f-4b34-ae29-06cbf394aead.png-w331s)

###### 3.3.8 加密算法分析

勒索病毒加密文件，使用内置的一段加密的RSA公钥对随机生成的AES密钥进行加密，并将加密后的内容发给黑客，黑客使用RSA私钥进行解密，得到加密文件的AES密钥。为了保障随机性，黑客对每个文件进行加密的时候都使用随机的IV，被加密后的文件按照特定的文件格式进行存储，文件加密算法流程图如下所示：

![](https://images.seebug.org/content/images/2018/06/ed31d789-cf5a-4849-8e95-816fd72ed099.png-w331s)

在加密算法中有一个非常重要的结构体，如下图所示：

![](https://images.seebug.org/content/images/2018/06/0c5fdbbd-0a3c-4453-81cc-4405559bef3e.png-w331s)

这个结构体的初始化过程是：首先利用上文中的RC4算法解密一段内置的0x80字节的数据，解密后的结果作为RSA的公钥；然后对RSA的公钥进行SHA1求值，将其SHA1结果赋值给encrypt->
rsa_pub_sha1。RSA公钥如下图所示：

![](https://images.seebug.org/content/images/2018/06/98c1d28e-614a-4fb1-b48c-4cb176f1251e.png-w331s)

计算RSA公钥的SHA1结果为“23 A0 55 82 B9 C1 12 1E FE 56 71 CE 45 87 38 1D BA 95 B7
F9”，相关代码如下图所示：

![](https://images.seebug.org/content/images/2018/06/3f63a3cb-a74a-45e8-b9ad-9f0aa2a360f8.png-w331s)

勒索病毒使用GetVolumeSerialNumber函数获取C盘序列号，并填充encrypt->disk_id字段，通过rdtsc获取CPU自从启动以来的时钟周期数（也就是一个随机数）；使用RC4加密，RC4加密的结果作为后面对文件加密的AES密钥，填充encrypt->aes_key字段。代码如下图所示：

![](https://images.seebug.org/content/images/2018/06/75c80606-2da4-4ad8-abcf-2a98da677388.png-w331s)

勒索病毒使用RSA公钥加密encrypt->aes_key，加密后的结果填充encrypt->rsa_encrypt_key字段，通过上文的RC4算法解密得到黑客联系邮箱“.[filedec@tuta.io]”和文件后缀名“.bip”，代码如下图所示：

![](https://images.seebug.org/content/images/2018/06/bac76c6d-3458-463f-b59e-e22e24659380.png-w331s)

初始化完加密结构体，勒索病毒会创建线程对文件进行加密，在对文件进行加密的时候，该勒索病毒会判断文件大小是否大于0x180000，如果大于就使用大文件加密方法，否则就使用小文件加密函数。相关代码如下：

![](https://images.seebug.org/content/images/2018/06/3155338f-febf-4b58-afe7-af2f3490c54d.png-w331s)

（1）小于等于0x180000的文件处理方法

加密完成后，勒索病毒把AES加密的结果写入文件中，然后再追加一段数据。假设这段数据的起始地址为0，将这段地址全部初始化为0：

  1. 在第0x04字节后依次写入0x00000002和0x417AFE0C；
  2. 在第0x18字节后写入0x00000020；
  3. 在第0x20字节处写入文件名；
  4. 在文件名后面追加6字节的encrypt->str_45STKM；
  5. 在encrypt->str_45STKM后面追加20字节的encrypt->rsa_pub_sha1；
  6. 在encrypt-> rsa_pub_sha1后面追加16字节的IV；
  7. 在IV后面追加4字节的PadingLen，（对AES明文不足16字节的补齐长度）；
  8. 在PadingLen后面再追加128字节的encrypt->rsa_encrypt_key；
  9. 在encrypt-> rsa_encrypt_key后面写入4字节的偏移（0x20+文件名长度）。

至此，文件加密完成，关闭文件，相关代码如下：

![](https://images.seebug.org/content/images/2018/06/2c763855-721b-43f0-9bee-a45a3757c265.png-w331s)

（2）大于0x180000的文件处理方法

加密完成后，勒索病毒把AES加密的结果写入文件中，然后再追加一段数据。假设这段数据的起始地址为0，将这段地址全部初始化为0：

  1. 在第0x0字节处写入文件名；
  2. 在文件名后面追加6字节的encrypt-> str_45STKM；
  3. 在encrypt-> str_45STKM后面追加20字节的encrypt-> rsa_pub_sha1；
  4. 在encrypt-> rsa_pub_sha1后面追加16字节的IV（用于AES加密）；
  5. 在IV后面追加4字节的0x00（这里可能是为了与小文件格式兼容）； 
  6. 在PadingLen后面再追加128字节的encrypt-> rsa_encrypt_key；
  7. 在encrypt-> rsa_encrypt_key后面写入4字节的文件名长度。

相关代码如下图所示：

![](https://images.seebug.org/content/images/2018/06/b61214fb-abd5-46be-9e34-c5b60b1e3fdd.png-w331s)

#### 四、总结及建议

勒索病毒已经成为了一种越来越普遍和有效的攻击方式，个人用户和企事业组织受害者居多，而且一旦感染勒索病毒，数据被加密就很难还原。因为勒索病毒都采用成熟的密码学算法，使用高强度的对称和非对称加密算法对文件进行加密，所以在通常情况下只能支付高额的赎金。有些勒索病毒在加密过程中使用Windows
Crypto
API生成密钥并进行加密，但此API在某些操作系统上并未将生成密钥时产生的素数从内存中删除，因此若该内存块尚未被覆盖，我们就可以通过截取素数生成出同样的密钥，使用该密钥实现对已被加密的文件进行解密。Crysis勒索病毒没有使用这个API，所以不存在此漏洞。目前互联网上流传的一些勒索病毒的解密工具大多是利用了勒索病毒功能或逻辑上的漏洞或私钥泄露实现的。
勒索病毒的几点防范建议：

  1. 对重要的数据文件定期进行非本地备份。
  2. 不要点击来源不明的邮件以及附件。
  3. 重命名vssadmin.exe进程，防止勒索病毒利用它一次性清除文件的卷影副本。
  4. 开启防火墙，并升级到最新版本，阻止勒索病毒与其C&C服务器通信。
  5. 及时给电脑打补丁，修复漏洞。
  6. 使用长度大于10位的复杂密码，禁用GUEST来宾帐户。
  7. 尽量不要使用局域网共享，或把共享磁盘设置为只读属性，不允许局域网用户改写文件。
  8. 关闭不必要的端口，如：445、135、139、3389等。

* * *

**启明星辰积极防御实验室（ADLab）**

ADLab成立于1999年，是中国安全行业最早成立的攻防技术研究实验室之一，微软MAPP计划核心成员。截止目前，ADLab通过CVE发布Windows、Linux、Unix等操作系统安全或软件漏洞近400个，持续保持国际网络安全领域一流水准。实验室研究方向涵盖操作系统与应用系统安全研究、移动智能终端安全研究、物联网智能设备安全研究、Web安全研究、工控系统安全研究、云安全研究。研究成果应用于产品核心技术研究、国家重点科技项目攻关、专业安全服务等。
![](https://images.seebug.org/content/images/2017/05/adlab.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/619/>

