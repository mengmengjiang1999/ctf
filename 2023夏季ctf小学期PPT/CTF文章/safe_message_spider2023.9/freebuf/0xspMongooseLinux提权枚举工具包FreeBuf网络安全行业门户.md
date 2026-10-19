**![68747470733a2f2f736563706c6f69742e636f6d2f7374617469632f307873702f7472616e732e706e67.png](https://image.3001.net/images/20190719/1563507401_5d313ac988c1e.png!small)**

**0xsp-Mongoose是一个为Linux创建的提权枚举工具包。该工具包可帮助你针对特定的目标系统执行任何可能的提权攻击，从信息收集阶段到报告通过0xsp Web
Application API。**

用户将能够高性能的同时扫描多个linux系统，而不需要花费大量的时间在终端或文本文件中查找信息，Mongoose通过简单的API端点将这些信息直接发送到web应用友好的界面，从而缩短了这一过程。

该项目主要分为两个部分：server & agent。

server已经由PHP（codeigner）进行了编码。你需要将该应用程序安装到预先提供的环境中，你可以在线或在本地主机上使用它。用户可以自由选择。也欢迎你为增强功能做出贡献。

Agent已经由Lazarus Free
Pascal编码为elf，将用（32，64位）释放，同时在目标系统上使用所需参数执行代理。用户可以自由决定是否与Server
App通信。或者也可以使用Web Api Connection来运行这个工具。

## Agent 使用

1、确保赋予其可执行权限chmod +x agent

2、./agent -h（显示帮助说明）

    
    
    -k --check kernel for common used privilige escalations exploits. 
    -u --Getting information about Users , groups , releated information.
    -c --check cronjobs. 
    -n --Retrieve Network information,interfaces ...etc.
    -w --Enumerate for Writeable Files , Dirs , SUID , 
    -i --Search for Bash,python,Mysql,Vim..etc History files.
    -f --search for Senstive config files accessible & private stuff. 
    -o --connect to 0xsp Web Application. 
    -p --Show All process By running under Root,Check For Vulnerable Packages. 
    -e --Kernel inspection Tool, it will help to search through tool databases for kernel vulnerabilities. 
    -x --secret Key to authorize your connection with WebApp API (default is 0xsp). 
    -a --Display README. 

## **Server Web App（<http://host/0xsp/>）**

![68747470733a2f2f736563706c6f69742e636f6d2f7374617469632f307873702f7765622e706e67.png](https://image.3001.net/images/20190719/1563507417_5d313ad95bcb4.png!small)

1、确保PHP版本至少为5.6或以上

2、mysql为5.6版本

3、请确保在根路径/添加Web应用使用文件夹名0xsp，如果配置不正确，Agent将无法连接到它。agent将仅在如下情况连接：

    
    
    ./agent {SCAN OPTION} -o localhost -x secretkey

## 有 WebApi 的示例

    
    
    ./agent -c -o localhost -x 0xsp { enumerate for CRON Tasks and Transfer results into Web Api} 
    ./agent -e -o localhost -x 0xsp { intelligent Exploits Detector }
    ./agent -c -e localhost -x 0sxp { will run two scans together and send found results directly }
    ./agent -m -o 10.10.13.1 -x 0xsp { RUN all Scans together and export it to Web API} 

## 没有 WebApi 的示例

    
    
    ./agent -c -k -p { this will run 3 scans at the same time with out sending results into Web Api }

## Agent 特性

> 1、高性能，稳定性，输出结果在执行时生成无延迟
>
> 2、能够使用智能技术执行大多数功能。
>
> 3、结果将被发送到Quick Web API
>
> 4、异常处理
>
> 5、内置的Json数据集用于公开披露的漏洞利用
>
> 6、速度快

## 视频演示

 ***参考来源：[GitHub](https://github.com/lawrenceamer/0xsp-Mongoose/blob/master/README.md)，FB小编secist编译，转载请注明来自FreeBuf.COM**

