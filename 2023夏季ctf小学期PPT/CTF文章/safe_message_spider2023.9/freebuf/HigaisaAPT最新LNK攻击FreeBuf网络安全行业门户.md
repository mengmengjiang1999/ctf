**近期确定了Higaisa发起的最新LNK攻击，Higaisa
APT与朝鲜半岛有关，于2019年首次披露。该小组的活动可以追溯到2016年，主要使用木马（例如Gh0st和PlugX）以及移动恶意软件等工具。
其目标包括政府官员和人权组织，以及与朝鲜有关的其他实体。**

在最近的活动中Higaisa使用了恶意快捷方式文件，该文件会发起由多个恶意脚本，有效负载和诱饵PDF文档组成的多阶段攻击。

![1593398579_5ef95533ab018.png!small](https://image.3001.net/images/20200629/1593398579_5ef95533ab018.png!small)

## 传播方式

攻击者把恶意LNK文件捆绑在文件中，通过鱼叉式网络钓鱼传播。可确定的两个变体是在5月12日至31日之间传播分发的：

> “CV_Colliers.rar”
>
> “Project link and New copyright policy.rar”

两个RAR文件都捆绑了恶意LNK文件。 在较新的变体（CV_Colliers.rar）中，LNK文件被伪装成简历和国际英语测试考试结果。
较旧的版本主要针对使用zeplin.io的团队。下面显示了执行恶意LNK文件时的处理流程：

![1593398756_5ef955e42e4a3.png!small](https://image.3001.net/images/20200629/1593398756_5ef955e42e4a3.png!small)

## LNK file

LNK文件包含命令列表和一个blob（base64编码的压缩有效负载）。 执行命令列表如下：

![1593398829_5ef9562d0b5c3.png!small](https://image.3001.net/images/20200629/1593398829_5ef9562d0b5c3.png!small)

运行过程如下：

> 1、将LNK文件的内容复制到%APPDATA%temp目录下的“g4ZokyumB2D**.tmp”
>
> 2、将“ certutil.exe”的内容复制到“ gosia.exe”中（“* ertu * .exe用于绕过安全检测）
>
> 3、使用“ findstr.exe”查找base64 blob，并将其写入“ cSi1rouy4.tmp”
>
> 4、使用“ gosia.exe -decode”（certutil.exe -decode）对“
> cSi1rouy4.tmp”的内容进行解码，并将其写入“ o423DFDS4.tmp”
>
> 5、使用“ expand.exe -F：*”在temp目录中解压缩“ o423DFDS4.tmp”的内容以及诱饵PDF文档
>
> 6、将“ 66DF33DFG.tmp”和“ 34fDKfSD38.js”文件复制到“ C:\Users\Public\Downloads”目录中
>
> 7、通过调用Wscript执行JS文件
>
> 8、打开诱饵文件

![1593399017_5ef956e91192a.png!small](https://image.3001.net/images/20200629/1593399017_5ef956e91192a.png!small)

该LNK快捷方式执行的命令列表与Anomali在Higasia Covid-19中报告的命令列表相同。
唯一的区别是tmp文件名称和certutil.exe名称。文档中嵌入的两个LNK文件都使用不同的命令和控制（C＆C）配置执行命令，他们会显示不同的诱饵文档。

![1593399110_5ef957463ef15.png!small](https://image.3001.net/images/20200629/1593399110_5ef957463ef15.png!small)

![1593399120_5ef95750978bc.png!small](https://image.3001.net/images/20200629/1593399120_5ef95750978bc.png!small)

## JS file

JavaScript文件执行以下命令：

> 1、在“C:\Users\Public\Downloads”中创建“ d3reEW.exe”，并将“ cmd / c ipconfig”存储在其中
>
> 2、删除的“ svchast.exe”
>
> 3、将“ svchhast.exe”复制到启动目录，并将其重命名为“ officeupdate.exe”
>
> 4、将“ officeupdate.exe”添加到计划的任务中
>
> 5、使用“ d3reEW.exe”作为数据将POST请求发送到硬编码的URL

![1593399222_5ef957b64e0f6.png!small](https://image.3001.net/images/20200629/1593399222_5ef957b64e0f6.png!small)

![1593399229_5ef957bdbff76.png!small](https://image.3001.net/images/20200629/1593399229_5ef957bdbff76.png!small)

## svchast.exe

Svchast.exe是一个小型加载程序，它加载存储在“ 63DF3DFG.tmp”中的shellcode：

![1593399261_5ef957dd41475.png!small](https://image.3001.net/images/20200629/1593399261_5ef957dd41475.png!small)

实际上，此shellcode是最终shellcode的外包装。 它执行一些检查，然后调用最终的shellcode。

![1593399315_5ef958137f5cf.png!small](https://image.3001.net/images/20200629/1593399315_5ef958137f5cf.png!small)

最终的shellcode动态解析导入，并为将要执行的内容分配内存。

![1593399344_5ef9583058508.png!small](https://image.3001.net/images/20200629/1593399344_5ef9583058508.png!small)

![1593399353_5ef9583970bd6.png!small](https://image.3001.net/images/20200629/1593399353_5ef9583970bd6.png!small)

最后，它调用“CreateThread”在其内存空间中创建进程，向C＆C服务器发出HTTPS请求。

![1593399389_5ef9585d6d787.png!small](https://image.3001.net/images/20200629/1593399389_5ef9585d6d787.png!small)

## 攻击重现

大多数恶意软件都使用简单的诱饵文档来加载恶意软件有效负载，但高级攻击者通常会使用非常规手段感染受害者。研究人员在实验室中使用电子邮件作为感染媒介重现了攻击，Malwarebytes（在本例中为Nebula商业版本）阻止了WinRAR中LNK文件的执行。

![1593399513_5ef958d9c5e90.png!small](https://image.3001.net/images/20200629/1593399513_5ef958d9c5e90.png!small)

## IOCs

 **CV_Colliers.rar**

df999d24bde96decdbb65287ca0986db98f73b4ed477e18c3ef100064bceba6d

 **Project link and New copyright policy.rar**

c3a45aaf6ba9f2a53d26a96406b6c34a56f364abe1dd54d55461b9cc5b9d9a04

 **Curriculum Vitae_WANG LEI_Hong Kong Polytechnic University.pdf.lnk**

50d081e526beeb61dc6180f809d6230e7cc56d9a2562dd0f7e01f7c6e73388d9

 **Tokbox icon – Odds and Ends – iOS – Zeplin.lnk**

1074654a3f3df73f6e0fd0ad81597c662b75c273c92dc75c5a6bea81f093ef81

 **International English Language Testing System certificate.pdf.lnk**

c613487a5fc65b3b4ca855980e33dd327b3f37a61ce0809518ba98b454ebf68b

 **Curriculum Vitae_WANG LEI_Hong Kong Polytechnic University.pdf.lnk**

dcd2531aa89a99f009a740eab43d2aa2b8c1ed7c8d7e755405039f3a235e23a6

 **Conversations – iOS – Swipe Icons – Zeplin.lnk**

c0a0266f6df7f1235aeb4aad554e505320560967248c9c5cce7409fc77b56bd5

 **C2 domains (ipconfig)**

sixindent[.]epizy[.]com

goodhk[.]azurewebsites[.]net

zeplin[.]atwebpages[.]com

 **C2s**

45.76.6[.]149

[www.comcleanner](http://www.comcleanner/)[.]info

## MITRE ATT&CK techniques

![1593399623_5ef9594775624.png!small](https://image.3001.net/images/20200629/1593399623_5ef9594775624.png!small)

 **参考来源**

> [malwarebytes](https://blog.malwarebytes.com/threat-> analysis/2020/06/higaisa/)

