**Loki是一款简单的IOC和事件响应扫描器。**

其检测主要基于以下四种检测方法：

>   1. 文件名IOC  
> 正则表达式匹配完整的文件路径/名称
>   2. Yara规则检查  
> Yara签名匹配文件数据和进程内存
>   3. 哈希检查  
> 将已知的恶意哈希（MD5，SHA1，SHA256）与扫描的文件进行比较
>   4. C2连接后检查  
> 将进程连接端点与C2 IOC进行比较（版本v.10后新增）
>

其他检查：

>   1. Regin文件系统检查（通过--reginfs）
>   2. 处理异常检查（基于Sysforensics）
>   3. SWF解压缩扫描（从版本v0.8开始新增）
>   4. SAM转储检查
>   5. DoublePulsar检查 - 尝试检测端口445/tcp和3389/tcp上的DoublePulsar后门程序
>   6. [PE-Sieve进](https://hshrzd.wordpress.com/pe-sieve/)程检查
>

Windows二进制文件使用PyInstaller 2.1进行编译，并且应该在基于x86和x64的系统上作为x86应用程序运行。

##  **下载**

LOKI的最新发布版本可以[在这里下载](https://github.com/Neo23x0/Loki/releases)到。

##  **如何运行LOKI并分析报告**

###  **运行**

  * 下载最新的LOKI版本
  * 运行一次以检索最新的签名库存储库
  * 将文件夹提供给应扫描的目标系统：可移动媒体，网络共享，目标系统上的文件夹
  * 右键单击loki.exe，然后选择“以管理员身份运行”或以管理员身份打开命令行“cmd.exe”，然后从中运行它（您也可以在没有管理权限的情况运行LOKI，但某些检查将被禁用且相关对象磁盘将无法访问）

###  **报告**

  * 报告内容将会以不同的颜色区分（绿色，黄色或红色）其重要程度。
  * 请自行对报告内容研究分析：

>   1. 将非保密样本上传到 [Virustotal.com](https://www.virustotal.com/)
>   2. 在网上搜索文件名
>   3. 在网络上搜索规则名称中的关键字（例如，EQUATIONGroupMalware_1>搜索“方程组”）
>   4. 在网上搜索样本的MD5哈希
>   5.
> 在我[的客户APT搜索引擎](https://cse.google.com/cse/publicurl?cx=003248445720253387346:turlh5vi4xc)中搜索文件名或标识符
>

  * 欢迎大家通过[Issuesx'axai](https://github.com/Neo23x0/Loki/issues)向我们报告相关的误报问题（误报例如散列和/或文件名以及触发的规则名称）

###  **更新**

自版本0.21.0以来，LOKI包含了一个名为loki-upgrader.exe或loki-upgrader.py的独立更新工具。

    
    
    usage: loki-upgrader.py [-h] [-l log-file] [--sigsonly] [--progonly] [--nolog]
                            [--debug]
    
    Loki - Upgrader
    
    optional arguments:
      -h, --help   显示帮助信息并退出
      -l log-file  日志文件
      --sigsonly   仅更新签名
      --progonly   仅更新程序文件
      --nolog      不要编写本地日志文件
      --debug      调试输出

它允许更新Windows上已编译的loki.exe和基于签名的源代码。

当运行loki.exe --update时，它会创建一个新的升级程序并退出LOKI，以便用新的升级程序代替loki.exe，否则将被锁定。

##  **使用**

    
    
    usage: loki.exe [-h] [-p path] [-s kilobyte] [-l log-file] [-r remote-loghost]
                    [-a alert-level] [-w warning-level] [-n notice-level]
                    [--printAll] [--allreasons] [--noprocscan] [--nofilescan]
                    [--scriptanalysis] [--rootkit] [--noindicator] [--reginfs]
                    [--dontwait] [--intense] [--csv] [--onlyrelevant] [--nolog]
                    [--update] [--debug]
    
    Loki - Simple IOC Scanner
    
    optional arguments:
      -h, --help         显示帮助信息并退出
      -p path            扫描路径
      -s kilobyte        最大文件大小KB（默认5000 KB）
      -l log-file        日志文件
      -r remote-loghost  远程系统日志
      -a alert-level     警报评分
      -w warning-level   警告评分
      -n notice-level    注意评分
      --printAll         打印所有扫描的文件
      --allreasons       打印导致得分的所有原因
      --noprocscan       跳过进程扫描
      --nofilescan       跳过文件扫描
      --scriptanalysis   激活脚本分析（beta版）
      --rootkit          跳过rootkit检查
      --noindicator      不显示进度指示器
      --reginfs          检查Regin虚拟文件系统
      --dontwait         不要等待退出
      --intense          变态扫描模式（也扫描未知的文件类型和所有扩展）                  
      --csv              将CSV日志格式写入标准输出（machine prcoessing）
      --onlyrelevant     仅打印警告或警报
      --nolog            不要编写本地日志文件
      --update           从"signature-base"子知识库更新签名
      --debug            调试输出

##  **构建LOKI**

如果你使用的是release部分的预编译的可执行文件，则无需任何要求。

如果你想自己构建LOKI：

### Linux 或 OS X

  * [yara](https://github.com/VirusTotal/yara/)：只需使用最新版本的源代码，编译并安装它（或者通过pip install yara-python安装）
  * 一些Python软件包：pip install yara-python psutil netaddr pylzma colorama

### Windows

  * [yara](https://github.com/VirusTotal/yara/)：建议使用最新版本的Windows编译软件包（例如yara-python-3.5.0.0.win32-py2.7.exe - 从这里下载：<https://github.com/VirusTotal/yara/releases>
  * pywin32：路径转换（PyInstaller [issue](https://github.com/pyinstaller/pyinstaller/issues/1282)；仅限Windows）
  * Microsoft Visual C++ 2010 Redistributable Package（<https://www.microsoft.com/en-US/download/details.aspx?id=5555>）
  * Microsoft Visual C++Compiler for Python 2.7（<https://www.microsoft.com/en-us/download/details.aspx?id=44266>）：pylzma

    
    
    c:\Python27\python.exe -m pip install --upgrade pip
    pip.exe install psutil netaddr wmi colorama pylzma pycrypto

LOKI可以使用定制的加密规则集进行打包，该规则集嵌入在pyinstaller软件包中。为了包含你自己的规则，你需要将它们放在LOKI目录下名为private-signature的目录中并执行build.bat。

    
    
    loki/
    ├── private-signatures/  <-- YARA rules places in here will by added to loki.exe
    ├── signature-base/      <-- clear text and still required (retrieved by loki-upgrader.exe)
    │   ├── iocs/
    │   ├── yara/

为了成功运行构建脚本，你需要安装PyInstaller。我们使用PyInstaller 2.1是因为使用PyInstaller
3构建的软件包不能在基于Windows 2003和XP的系统上运行。（在事件响应中 - 甚至有运行Windows 2000或Windows NT的生产系统）

安装PyInstaller最简单的方法是：

    
    
    pip install pyinstaller==2.1

之后，你可以运行构建脚本。

    
    
    build.bat

你可以手动调用loki-package-builder.py来验证签名集是否有效。

    
    
    C:\Python27\python.exe loki-package-builder.py --ruledir signatures --target rules

该工具的用法：

    
    
    usage: loki-package-builder.py [-h] --ruledir RULEDIR --target TARGET
    
    Package builder for Loki
    
    optional arguments:
      -h, --help         显示帮助信息并退出
      --ruledir RULEDIR  包含要构建到Loki中的规则的目录
      --target TARGET    目标存储编译的规则集的位置

###  **威胁Intel接收器的必要条件**

> * [OTX Python SDK](https://github.com/AlienVault-Labs/OTX-Python-SDK)
> * [pyMISP](https://github.com/CIRCL/PyMISP)

## 签名和IOCs

你可以下载LOKI发布的ZIP压缩包并运行一次LOKI，以下载带有所有签名的“signature-base”子库。
从版本0.21.0开始，提供了一个单独的更新程序loki-upgrader.exe或loki-upgrader.py。

IOC文件哈希和文件名存储在'./signature-base/iocs'文件夹中。 放置在'./signature-base/yara'文件夹中的所有'.yar'文件将与已包含的规则集一起初始化。使用'score'值来定义签名匹配时的消息级别。

你可以通过将文件添加到'./signature-base/iocs'子文件夹来添加散列，c2和文件名IOC。
所有散列IOC和文件名IOC文件必须采用LOKI使用的格式（请参阅默认文件）。
这些文件的名称中必须包含字符串“hash”，“filename”或“c2”以在初始化过程中被拉取。

对于散列IOC（以换行符分割；自动检测散列类型）

    
    
    Hash;Description [Reference]

对于文件名IOC（以换行符分割）

    
    
    # Description [Reference]
    Regex;Score;False Positive Regex

你可以在你提供给LOKI的YARA规则中使用以下外部变量

    
    
    filename - e.g. condition: $s1 and not filename == 'nmap.exe'
    filepatch - e.g. condition: filepath == 'C:\Windows\cmd.exe'
    extension - e.g. condition: uint32(0) == 0x5a4d and extension == ".txt"
    filetype - eg. condition: extension == ".txt" and filetype == "EXE"
    (see file-type-signatures.cfg in signature-base repo for all detected file types)
    md5 - legacy value

## 用户定义不包含的扫描目录

自版本v0.16.2开始LOKI支持通过新的“./config”文件夹中的“excludes.cfg”来定义用户排除的扫描范围。

''exclude.cfg''文件的内容格式如下所示：

    
    
    # Excluded directories
    #
    # - add directories you want to exclude from the scan
    # - double escape back slashes
    # - values are case-insensitive
    # - remember to use back slashes on Windows and slashes on Linux / Unix / OSX
    # - each line contains a regex that matches somewhere in the full path (case insensitive)
    #   e.g.:
    #   Regex: \\System32\\
    #   Matches C:\Windows\System32\cmd.exe
    #
    #   Regex: /var/log/[^/]+\.log
    #   Matches: /var/log/test.log
    #   Not Matches: /var/log/test.gz
    #
    
    # Useful examples
    \\Ntfrs\\
    \\Ntds\\
    \\EDB[^\.]+\.log
    Sysvol\\Staging\\Nntfrs_cmp
    \\System Volume Information\\DFSR

## PE-Sieve

自0.26版本以来，LOKI集成了@hasherezade的工具[PE-Sieve](https://github.com/hasherezade/pe-sieve)来检测[异常进程](https://hshrzd.wordpress.com/2017/12/18/process-doppelganging-a-new-way-to-impersonate-a-process/)。

如果LOKI在启动过程中在./tools子文件夹中找到它，该工具将被初始化。

##  **威胁Intel接收器**

自v0.10版本以来，LOKI包含各种威胁接收器，使用这些服务的公共API来检索和存储LOKI了解的IOC。Loki仅会使用一次文件名正则表达式或散列，因此对性能不会产生影响）

威胁intel接收器也已被转移到版本为0.15的[基于签名](https://github.com/Neo23x0/signature-base)的子库中，并可在“./signature-base/threatintel”中找到。

通过-k APIKEY提供你的API密钥或在脚本中配置。

## OTX接收器

这是一个简单的脚本，用于下载你订阅的事件/ioc，并将它们以正确的格式存储在'./iocs'子文件夹中。
该脚本位于“./threatintel”文件夹中，名为“get-otx-iocs.py”。

    
    
    usage: get-otx-iocs.py [-h] [-k APIKEY] [-o dir] [--verifycert] [--debug]
    
    OTX IOC Receiver
    
    optional arguments:
      -h, --help    显示帮助信息并退出
      -k APIKEY     OTX API key
      -o dir        输出目录
      --verifycert  验证服务器证书
      --debug       调试输出

## MISP接收器

一个简单的脚本，用于从自定义[MISP](https://github.com/MISP/MISP)实例下载你订阅的事件/ioc，并以正确格式将它们存储在'./iocs'子文件夹中。
存储在MISP中的YARA规则将写入'./iocs/yara'子文件夹，并在启动过程中自动初始化。该脚本位于“./threatintel”文件夹中，名为“get-misp-iocs.py”。

    
    
    usage: get-misp-iocs.py [-h] [-u URL] [-k APIKEY] [-l tframe] [-o dir]
                            [-y yara-dir] [--verifycert] [--debug]
    
    MISP IOC Receiver
    
    optional arguments:
      -h, --help    显示帮助信息并退出
      -u URL        MISP URL
      -k APIKEY     MISP API key
      -l tframe     时间范围（例如2天，12小时-默认=30天）
      -o dir        输出目录
      -y yara-dir   YARA规则输出目录
      --verifycert  验证服务器证书
      --debug       调试输出

## 截图

Loki扫描

![Loki：一款简单强大的IOC和事件响应扫描器](https://image.3001.net/images/20180328/15222038011720.png!small)  

命令行扫描输出

![Loki：一款简单强大的IOC和事件响应扫描器](https://image.3001.net/images/20180328/1522203825782.png!small)  

基于哈希的IOCs

![Loki：一款简单强大的IOC和事件响应扫描器](https://image.3001.net/images/20180328/15222038545490.png!small)  

基于文件名的IOC

![Loki：一款简单强大的IOC和事件响应扫描器](https://image.3001.net/images/20180328/15222038838537.png!small)  

生成的日志文件

![Loki：一款简单强大的IOC和事件响应扫描器](https://image.3001.net/images/20180328/15222039081276.png!small)  

## 联系我们

我们公司主页上关于LOKI的推荐及介绍：<https://www.nextron-systems.com/loki/>

Twitter [@cyb3rOps](https://twitter.com/Cyb3rOps)
[@thor_scanner](https://twitter.com/thor_scanner)

## 编译扫描器

下载PyInstaller v2.1，切换到pyinstaller程序目录并执行：

    
    
    python ./pyinstaller.py -F C:\path\to\loki.py

这将在子文件夹./loki/dist中创建一个loki.exe。

##  Mac OS X上的使用

  * 从[这里下载](https://github.com/VirusTotal/yara/releases)Yara源
  * 安装openssl（brew install openssl，然后sudo cp -r /usr/local/Cellar/openssl/1.0.2h_1/include /usr/local）
  * 运行./build.sh
  * sudo make install
  * 转到文件夹yara-python
  * 运行python setup.py install
  * 安装必要软件包，sudo pip install colorama gitpython, netaddr, pylzma 等...
  * 将<https://github.com/Neo23x0/signature-base>下载并解压到Loki文件夹中
  * cd loki文件夹，sudo python loki.py -p /

## 杀毒软件误报

杀毒引擎可能会对LOKI误报，这是由于其中编译的部分代码也被用于一些恶意软件中。如果你对此并不信任，你可以自行进行编译。

 ***参考来源：[github](https://github.com/Neo23x0/Loki)，FB小编 secist
编译，转载请注明来自FreeBuf.COM **  

