![](https://image.3001.net/images/20200401/1585754400_5e84b1207ccd4.png!small)

**xShock是一款针对Shellshock漏洞的利用工具，该工具由Hulya
Karabag开发，当前版本号为v1.0.0。在xShock的帮助下，广大安全研究人员可以轻松对ShellShock漏洞（CVE-2014-6271）进行漏洞利用测试。**

##  关于工具

该工具创建的所有目录都将保存在vulnurl.txt文件中，命令的执行结果会保存在response.txt中。

##  功能介绍

该工具包括以下几个功能：

> 1、CGI漏洞；
>
> 2、目录扫描；
>
> 3、使用已找到的CGI运行命令；
>
> 4、显示存在漏洞的URL地址；
>
> 5、更新代理；

##  工具安装

广大研究人员需要使用下列命令将项目源码克隆至本地，然后使用requirements.txt安装依赖组件：

    
    
    git clone <https://github.com/capture0x/xShock/>
    
        cd xShock
    
        pip3 install -r requirements.txt

##  工具使用

    
    
    python3 main.py

###  CGI漏洞

检测目标站点的cgi-bin目录，样例如下：

    
    
    http://targetsite.com

###  目录扫描

这个功能需要配合字典文件来使用，并能够扫描目标站点的URL地址。需要注意的是，我们需要在目标URL地址后面添加字典文件的完整路径。

例如：http:// targetsite.com/cgi-bin/selectedworlist

命令使用样例：

[](http://targetsite.com/cgi-bin)

    
    
    <http://targetsite.com/cgi-bin>
    
        /usr/share/wordlists/dirb  --> This is directory of wordlist. Not file!

###  使用已找到的CGI运行命令

通过输入vuln.txt文件中的URL地址，我们可以尝试在已找到的URL地址中运行命令：

    
    
    http://targetsite.com/cgi-bin/status

###  显示存在漏洞的URL地址

显示vuln.txt文件中已找到的存在漏洞的URL地址。

###  更新代理

我们可以手动更新Web代理。

##  工具运行截图

![](https://image.3001.net/images/20200401/1585754565_5e84b1c57d815.png!small)![](https://image.3001.net/images/20200401/1585754564_5e84b1c4b6e53.png!small)![](https://image.3001.net/images/20200401/1585754564_5e84b1c4b9bf6.png!small)![](https://image.3001.net/images/20200401/1585754566_5e84b1c6602fd.png!small)![](https://image.3001.net/images/20200401/1585754569_5e84b1c9da042.png!small)

##  项目地址

> xShock：【[GitHub传送门](https://github.com/capture0x/XSHOCK)】

 ***
参考来源：[capture0x](https://github.com/capture0x/XSHOCK)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

