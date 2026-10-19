信捷电气股份有限公司（XINJE）是一家专注于工业自动化产品研发与应用的国内知名企业，该公司拥有可编程控制器（PLC）、人机界面（HMI）、工业信息化、伺服控制系统、变频步进等核心产品，在北京奥运会、上海工博会等国家重点工程项目上都有信捷产品的正式应用。  
信捷PLC编程软件是一款功能强大的PLC编程软件，操作简单便利，能够帮助用户使用各种编程模式进行PLC的编程管理工作，让编程更加方便快捷，提高工作效率。  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-1.jpg](https://image.3001.net/images/20220519/1652944134_6285ed0602e4042abeef1.jpg!small)

##  ** **Part1 漏洞状态****

![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-17.jpg](https://image.3001.net/images/20220519/1652944134_6285ed068266334c2011f.jpg!small)

##  **Part2 漏洞描述**

信捷PLC编程软件V3.5.1存在zip
slip漏洞，攻击者在打开特殊制作的项目文件时，可获得任意文件写入权限，该漏洞可以用伪造的含有目录遍历文件名（e.g.
../../evil.sh）的存档进行利用，其结果可导致攻击者在系统中任意写文件，甚至会导致远程命令执行或拒绝服务。  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-18.jpg](https://image.3001.net/images/20220519/1652944134_6285ed06dfcaa0569fe25.jpg!small)

##  ** **Part3 漏洞复现****

### 1\. 实验环境

实验主机：win10  
软件版本：信捷PLC编程软件V3.5.1

### 2\. 涉及工具

Python3  
010editor  
Process Monitor

### 3\. 漏洞复现

1）第一步首先需要构造恶意项目文件，根据如下脚本可以生成一个名为“poc.zip”文件，阅读脚本可知，一旦在有漏洞的环境加载“poc.zip”后，“hello.txt”文件会被解压至C:\temp目录下。  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-2.jpg](https://image.3001.net/images/20220519/1652944135_6285ed07634e92dbc4642.jpg!small)  
“poc.zip”压缩文件内容如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-3.jpg](https://image.3001.net/images/20220519/1652944136_6285ed088b53519d2264d.jpg!small)  
2）将第一步生成的“poc.zip”重命名为“poc.xdp”。  
3）使用信捷PLC编程软件打开“poc.xdp”项目文件，如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-4.jpg](https://image.3001.net/images/20220519/1652944137_6285ed0934975c87113ea.jpg!small)  
点击“打开”按钮后，应用程序报错，同时查看C:\temp目录，发现文件被成功解压至此，如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-5.jpg](https://image.3001.net/images/20220519/1652944137_6285ed09c1f9695305a97.jpg!small)

##  ** **Part4 漏洞分析****

当用信捷PLC编程软件打开项目文件时，程序会提示项目文件的类型为*.xdp或*.xcp文件。  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-6.jpg](https://image.3001.net/images/20220519/1652944138_6285ed0a5990a0d947272.jpg!small)  
通过程序的导出下载文件功能下载PLC项目文件，并用010editor打开，发现项目文件的文件头为PK\x03\x04，文件头与zip格式的文件头一致，如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-7.jpg](https://image.3001.net/images/20220519/1652944138_6285ed0adfff12aacd87f.jpg!small)  
而且该文件类型几乎可以被任何压缩工具(例如7z、zip)提取。更有趣的是，通过Process
Monitor发现当程序打开一个项目文件时，它会立即将其解压缩到安装目录下的一个临时目录，如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-8.jpg](https://image.3001.net/images/20220519/1652944139_6285ed0b7087610fb5eaf.jpg!small)  
这种行为表明程序假定它是用管理员权限执行的。再加上被提取的文件是zip文件，这立即使人怀疑是否可以利用zip
slip漏洞(任意文件覆盖漏洞)来获得任意的写权限。  
使用ProcessMonitor查看解压文件（C:\temp\hello.txt）进程的详细信息，发现该进程加载了ICSharpCode.SharpZipLib.dll库文件，该库文件可用于C#实现文件压缩解压功能，如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-9.jpg](https://image.3001.net/images/20220519/1652944140_6285ed0c1e5a8e4771813.jpg!small)  
使用dnspy
反编译工具对信捷PLC编程软件进行分析，在ICSharpCode.SharpZipLib.dll下的ZipInputStream中的第77行代码处加断点，该行执行完成之后会将解压文件的路径与文件名长度之和赋值“num4”,如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-10.jpg](https://image.3001.net/images/20220519/1652944140_6285ed0cc7f92a60b2a9d.jpg!small)  
跟入，首先代码会将文件名赋值给“ClearText”、“RawDate”,将文件名的长度赋值给“cleartextlength”，如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-11.jpg](https://image.3001.net/images/20220519/1652944141_6285ed0d8c8509a8cb404.jpg!small)  
经过一系列操作，最终会将待解压文件路径的长度赋值“num4”，其值为0x2c（十进制为44），如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-12.jpg](https://image.3001.net/images/20220519/1652944142_6285ed0e2ab8c46c45428.jpg!small)  
第81行执行完将解压文件路径及文件名赋值给数组array，其长度为“num4”即0x2c。  
第82行执行完会将数组“array”转换为字符串并赋值给“name”，其值为“../../../../../../../../../../temp/hello.txt”，如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-13.jpg](https://image.3001.net/images/20220519/1652944142_6285ed0eebb09504c5ad8.jpg!small)  
第83行，当执行到ZipEntry的第39行时，将“name”赋值给Entry.name，如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-14.jpg](https://image.3001.net/images/20220519/1652944143_6285ed0f8eaf5b6c5a585.jpg!small)  
这里没有对目录回退符进行检查，通过一系列操作将“..”赋值给“folderName”，如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-15.jpg](https://image.3001.net/images/20220519/1652944144_6285ed10d80d1e4480cd1.jpg!small)  
通过一系列操作最终将目录会回退符拼接至解压路径，如下图所示：  
![%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B62022-16-16.jpg](https://image.3001.net/images/20220519/1652944145_6285ed1186353c069b634.jpg!small)

##  ** **Part5 修复建议****

联系厂商进行修复。

