## 1 概述

安天CERT近期发现APT组织Konni的攻击活动，结合诱饵文件内容及以往的攻击活动推测，此次攻击可能为针对韩国企业进行的网络攻击。APT组织Konni的攻击活动最早可以追溯至2014年，并一直活跃至今。该组织长期针对俄罗斯、韩国等国家进行定向攻击活动，擅长使用社会热点话题作为诱饵对目标进行鱼叉式网络钓鱼攻击。

近期发现，Konni组织可能通过向目标投递与税务相关的ZIP文件实施攻击。在用户打开ZIP文件内的诱饵LNK文件时，执行设置好的PowerShell指令，打开LNK文件内包含的掩饰文档以及压缩包，执行压缩包内的脚本文件，设置注册表实现持久化机制，获取目标机的部分文件列表、进程列表等基础信息并回传至服务端，最终下载后续载荷并执行。

## 2 Konni攻击活动分析

表 2‑1 ZIP文件

![1690866046_64c8917e2723c6309b696.png!small](https://image.3001.net/images/20230801/1690866046_64c8917e2723c6309b696.png!small)

Konni组织可能通过钓鱼攻击的手法投递税务相关主题的ZIP文件，ZIP文件内容如下表：

表 2‑2 ZIP文件内容

![1690866052_64c8918458916069a4510.png!small](https://image.3001.net/images/20230801/1690866052_64c8918458916069a4510.png!small)

ZIP文件的内容如下图所示：

![1690866060_64c8918cc7611657341e8.png!small](https://image.3001.net/images/20230801/1690866060_64c8918cc7611657341e8.png!small)

  

图 2‑1 ZIP文件内容

表 2‑3 LNK文件

![1690866068_64c89194dc41ea5ede5a2.png!small](https://image.3001.net/images/20230801/1690866068_64c89194dc41ea5ede5a2.png!small)

上表中的LNK文件包含在ZIP文件内，LNK文件指向攻击者构造的一段PowerShell代码，该代码用于解码其中十六进制编码的数据并执行，将这段PowerShell代码提取出来如下所示。

![1690866604_64c893ac5e759a3ff98c6.png!small](https://image.3001.net/images/20230801/1690866604_64c893ac5e759a3ff98c6.png!small)

图 2‑2 LNK文件指向的PowerShell代码

解码后的内容用于释放掩饰文档소명자료 목록(국세징수법
시행규칙).hwp到LNK文件所在的目录、删除LNK文件、提取内嵌的ZIP文件并将ZIP文件中的条目提取到%public%\documents目录下，最终执行start.vbs。

![1690866610_64c893b24f95e2693302c.png!small](https://image.3001.net/images/20230801/1690866610_64c893b24f95e2693302c.png!small)

  

图 2‑3 释放后续文件

LNK文件内存储的掩饰文档及ZIP文件数据相连，数据结构如下图所示。

  

![1690867010_64c895424a95ddc246e7c.png!small](https://image.3001.net/images/20230801/1690867010_64c895424a95ddc246e7c.png!small)

图 2‑4 LNK文件内存储的掩饰文档及ZIP文件

LNK文件释放的掩饰文档正文内容如下所示。

![1690867014_64c89546e02a1bd3c3b51.png!small](https://image.3001.net/images/20230801/1690867014_64c89546e02a1bd3c3b51.png!small)

  

图 2‑5 소명자료 목록(국세징수법 시행규칙).hwp 申明资料目录（国税征收法实施规则）

ZIP文件内包含的条目及对应文件的功能如下所示。

![1690867020_64c8954c68b48782591c4.png!small](https://image.3001.net/images/20230801/1690867020_64c8954c68b48782591c4.png!small)

  

图 2‑6 ZIP文件内包含的条目

表2-4 ZIP内的文件及对应功能

![1690867029_64c895552165ba02bea23.png!small](https://image.3001.net/images/20230801/1690867029_64c895552165ba02bea23.png!small)

ZIP文件内各文件之间的调用关系如下图所示：

![1690867039_64c8955f8fe4b173d597d.png!small](https://image.3001.net/images/20230801/1690867039_64c8955f8fe4b173d597d.png!small)

  

图 2‑7调用关系图

start.vbs，该文件用于执行78788188.bat文件。

  

![1690867048_64c895681d3f46195a49c.png!small](https://image.3001.net/images/20230801/1690867048_64c895681d3f46195a49c.png!small)

图 2‑8 Start.vbs文件

78788188.bat，执行流程如下：

  * 判断是否存在bat，如果存在23965250.bat，会将Start.vbs添加至注册表RUN中实现开机自启动，执行23965250.bat、27355145.bat后删除23965250.bat文件。如果不存在23965250.bat，判断是否存在upok.txt文件，如果upok.txt存在，执行步骤2)；如果upok.txt不存在，执行27355145.bat，该文件用于收集本地数据并回传至服务端，然后执行步骤2)。
  * 判断是否存在txt，如果存在pakistan.txt，删除该文件并退出；如果不存在pakistan.txt，执行步骤3)。
  * 判断是否存在bat，如果存在temprun.bat，删除该文件，执行步骤4)；如果不存在temprun.bat，直接执行步骤4)。
  * 执行bat，该文件用于下载文件。传递参数http[:]//overseeby.com/list.php?f=%COMPUTERNAME%.txt、%~dp0SbJAZ.cab、1，下载SbJAZ.cab文件。如果第三个参数为0，会进行加密传输。以上操作完成后，执行步骤5)。
  * 解压cab到当前路径下，而后删除SbJAZ.cab并执行temprun.bat。以上操作完成后，执行步骤6)。
  * 等待57秒，再次判断是否存在txt，如果不存在pakistan.txt，跳到步骤3)继续执行。若存在pakistan.txt，删除该文件并退出。

![1690867156_64c895d48039965f5c3a1.png!small](https://image.3001.net/images/20230801/1690867156_64c895d48039965f5c3a1.png!small)

图 2‑9 78788188.bat文件

23965250.bat，执行流程如下：

  * 调用bat，发送http请求，下载97157.zip文件，请求的网址为https[:]//naver.cloudfiles001.com/v2/read/get.php?hs=ln3&fj=bv8702。然后判断下载是否成功，如果97157.zip文件存在，执行步骤2)。如果该文件不存在，退出。
  * 获取压缩包中的第一个条目的名字，如果该名字存在，以字符a作为密码解压zip，而后删除压缩包，执行步骤3)；若该名字不存在，直接删除压缩包并退出。
  * 判断压缩包中的第一个条目对应的文件是否存在。若存在，使用exe执行该文件的Run导出函数，等待60s；若不存在，等待60s，退出。此次操作将会循环执行三次。

![1690867161_64c895d9e3276d69bdbb7.png!small](https://image.3001.net/images/20230801/1690867161_64c895d9e3276d69bdbb7.png!small)

图 2‑10 23965250.bat文件

  

27355145.bat，执行流程如下：

  * 获取C:\Users\%username%目录下downloads、documents、desktop以及C:\Program Files中的文件及文件夹列表，并将其输出到bat文件所在目录对应的txt、cuserdocu.txt、cuserdesk.txt、cprot.txt中。然后通过nslookup命令获取myip.opendns.com、resolver1.opendns.com的域名解析地址，通过tasklist和systeminfo获取进程列表和系统信息，将他们分别输出到对应的ipinfo.txt、tsklt.txt、systeminfo.txt中，然后执行步骤2)。
  * 等待5秒后，调用bat，将其加密处理后上传到http[:]//overseeby.com/upload.php地址。

![1690867167_64c895dfb7487f77eff69.png!small](https://image.3001.net/images/20230801/1690867167_64c895dfb7487f77eff69.png!small)

图 2‑11 27355145.bat

28499076.bat，该文件内部存在一个自定义的加密函数，获取当前时间作为密钥。该文件的主要功能为加密27355145.bat生成的存放信息的txt文件，并将传入的带有计算机名称的文件名在加密后，与key和加密后的txt文件一同上传到指定的URL。在上传成功后会删除txt文件并在当前目录下新建一个upok.txt文件。

![1690867171_64c895e3963c5d2e87cc9.png!small](https://image.3001.net/images/20230801/1690867171_64c895e3963c5d2e87cc9.png!small)

图 2‑12 28499076.bat

60937671.bat，主要功能用于下载文件，可根据传递的第三个参数来选择是否进行加密传输。若选择加密传输，则会获取当前时间作为密钥，并将其作为参数添加到URL中传递至服务端。

![1690867177_64c895e9c62690ff9b235.png!small](https://image.3001.net/images/20230801/1690867177_64c895e9c62690ff9b235.png!small)

图 2‑13 60937671.bat

## 3 关联归因

根据初始压缩包内的诱饵文档以及脚本代码的相似性进行关联，发现了几个同为税务主题的压缩包，压缩包内同样包含LNK文件，且LNK文件中的掩饰文档与ZIP数据相连。将包含在LNK文件内的ZIP内容提取出来，发现内部脚本的功能大致相同，部分文件在传输加密、变量命名和文件命名上存在不同。

对关联到的所有文件进行分析，压缩包内的恶意LNK文件及对应域名列表如下所示：

表3-1 LNK文件对应的hash、文件名及域名列表

![1690867191_64c895f7f29c0d0ad7add.png!small](https://image.3001.net/images/20230801/1690867191_64c895f7f29c0d0ad7add.png!small)

其中最早发现的两个文件的上传、下载功能的脚本文件内并无加密函数。

![1690867200_64c896001249e9f5e5b4b.png!small](https://image.3001.net/images/20230801/1690867200_64c896001249e9f5e5b4b.png!small)

图 3‑1 早期攻击活动中用于文件上传、下载的脚本

![1690867204_64c89604585e1e786c473.png!small](https://image.3001.net/images/20230801/1690867204_64c89604585e1e786c473.png!small)

图 3‑2 之后捕获到的攻击活动中用于文件上传、下载的脚本

此次捕获到的样本中，存在从伪装成韩国Naver公司相关的URL中下载文件的行为，具体URL如下表所示：

表3-2 URL列表

![1690867212_64c8960c751a50405da65.png!small](https://image.3001.net/images/20230801/1690867212_64c8960c751a50405da65.png!small)

归因分析：

诱饵文件类型均为HWP文件，为韩国常用的文档格式。诱饵文件的文件名与内容所用语言均为韩语，且诱饵文档内容为税务相关内容，与以往Konni组织的攻击目标相符[1]。

在代码层面，仍沿用之前的脚本模式来进行文件的调用、初步的信息收集、文件的上传与下载，代码结构及内容与以往攻击活动相似程度较高，部分内容存在重叠。

![1690867221_64c89615e5dc2829f9568.png!small](https://image.3001.net/images/20230801/1690867221_64c89615e5dc2829f9568.png!small)

图 3‑3 左侧为本次攻击活动中的信息收集脚本，右侧为以往攻击活动中的信息收集脚本[2]

  

![1690867226_64c8961acd8f7f8da99e8.png!small](https://image.3001.net/images/20230801/1690867226_64c8961acd8f7f8da99e8.png!small)

图 3‑4 左侧为本次攻击活动中用作文件调用和下载的脚本，右侧为以往攻击活动中用作文件调用和下载的脚本[2]

## 4 威胁框架映射

本次捕获到的Konni组织疑似针对韩国企业的攻击活动共涉及ATT&CK框架中9个阶段的15个技术点，具体行为描述如下表：

表4-1 本次Konni组织攻击活动的技术行为描述表

![1690867235_64c896238bbba1dc59b66.png!small](https://image.3001.net/images/20230801/1690867235_64c896238bbba1dc59b66.png!small)

将涉及到的威胁行为技术点映射到ATT&CK框架如下图所示：

![1690867246_64c8962eaf76e1e73d058.png!small](https://image.3001.net/images/20230801/1690867246_64c8962eaf76e1e73d058.png!small)

图 4‑1 本次Konni组织攻击活动对应的ATT&CK映射图

## 5 总结

根据捕获的样本内容并结合已有情报来看，Konni组织从今年年初开始便以采用税务相关主题的诱饵进行钓鱼攻击。该组织继续沿用以往的LNK攻击手法，将恶意脚本文件添加到压缩包内并嵌入LNK文件中，待受害者打开LNK文件，执行恶意脚本文件，下载后续载荷。相比于早些时间捕获到的样本，差别主要存在于脚本中新增的数据传输前的加密功能。

## IoCs

![1690867259_64c8963b332944d9915c0.png!small](https://image.3001.net/images/20230801/1690867259_64c8963b332944d9915c0.png!small)

## 参考资料

  * 세무조사관련정상한글문서로위장한악성링크파일유포

https://www.boannews.com/media/view.asp?idx=113686

  * 코니(Konni) APT 조직, HWP 취약점을이용한 'Coin Plan' 작전감행

https://blog.alyac.co.kr/2543

