**OpenVAS，即开放式漏洞评估系统，是一个用于评估目标漏洞的杰出框架。功能十分强大，最重要的是，它是“开源”的——就是免费的意思啦～**

它与著名的Nessus“本是同根生”，在Nessus商业化之后仍然坚持开源，号称“当前最好用的开源漏洞扫描工具”。最新版的Kali Linux(kali
3.0)不再自带OpenVAS了，所以我们要自己部署OpenVAS漏洞检测系统。其核心部件是一个服务器，包括一套网络漏洞测试程序，可以检测远程系统和应用程序中的安全问题。

但是它的最常用用途是检测目标网络或主机的安全性。它的评估能力来源于数万个漏洞测试程序，这些程序都是以插件的形式存在。openvas是基于C/S（客户端/服务器），B/S(浏览器/服务器)架构进行工作，用户通过浏览器或者专用客户端程序来下达扫描任务，服务器端负责授权，执行扫描操作并提供扫描结果。

本文档属于部署方案文档，详细介绍了部署方法，搭建部署过程中有很多踩过的坑，这里整理出来供参考。

##  **OpenVAS** **系统架构**

  

一套完整的openvas系统包括服务器端和客户端的多个组件，如下图所示：

![image001.jpg](https://image.3001.net/images/20170427/14932859869783.jpg!small)

  

 **服务器层组件（建议都安装）**|  **客户层组件（任选其一安装即可）**  
---|---  
OpenVAS-scanner(扫描器)| 负责调用各种漏洞检测插件，完成实际的扫描操作。| OpenVAS-cli（命令行接口）|
负责提供从命令行访问OpenVAS服务层程序。  
OpenVAS-manager(管理器)| 负责分配扫描任务，并根据扫描结果生产评估报告。| Greenbone-security-assistant(安全助手)| 负责提供访问OpenVAS服务层的Web接口，便于通过浏览器来建立扫描任务，是使用最简便的客户层组件。  
OpenVAS-administrator(管理者)| 负责管理配置信息，用户授权等相关工作。| Greenbone-Desktop-Suite(桌面套件)| 负责提供访问OpenVAS服务层的图形程序界面，主要在windows系统中使用。  
  
##  **kali Linux** **安装openvas**

我这里是在kali linux系统上安装的openvas，最新版本的kalilinux系统是不带openvas的

注意：openvas服务器端仅支持安装在linux操作系统中，客户端安装在windows和Linux系统均可。

我的linux系统版本号如下：

![image002.jpg](https://image.3001.net/images/20170427/14932860002415.jpg!small)

![image003.jpg](https://image.3001.net/images/20170427/14932860003888.jpg!small)

虚拟机的网络连接方式如下，设置为桥接模式，设置为NAT。

![image004.jpg](https://image.3001.net/images/20170427/14932860174836.jpg!small)

##  **安装openvas过程**

1\. 更新软件包列表：

> apt-get update

![image005.jpg](https://image.3001.net/images/20170427/14932860414874.jpg!small)

2\. 获取到最新的软件包：

> apt-get dist-upgrade

![image006.jpg](https://image.3001.net/images/20170427/14932860474015.jpg!small)

3\. 安装openvas

> apt-get install openvas

执行以上命令后，如果没有报错，说明已经成功安装openvas。

##  **kali Linux** **配置openvas**

4.下载并更新OpenVAS库

> openvas-setup

![image007.jpg](https://image.3001.net/images/20170427/14932860532938.jpg!small)

在更新openvas库过程中创立了证书，下载及更新了一切扫描插件。

5.在更新OpenVAS库时，自动为admin用户创建了一个密码，只是该密码比较长，不容易记忆，我们使用如下命令将admin密码修改为容易记忆的密码，以kali123为例：

![image008.jpg](https://image.3001.net/images/20170427/14932860617100.jpg!small)

另外，我们新增一个普通用户wdl1，如下图：

![image009.png](https://image.3001.net/images/20170427/14932860684796.png!small)

6.openvas-check setup

这个命令用于查错并用来确认OpenVAS是否成功安装，用apt-get安装总会出现这样那样的错误，我们可以用openvas-check-setup查看安装到哪步出错了，以及缺少什么东西。

![image010.jpg](https://image.3001.net/images/20170427/14932860753366.jpg!small)

当出现如下结果时，表示安装成功：

![image011.jpg](https://image.3001.net/images/20170427/14932860822858.jpg!small)

然后输入openvasmd --rebuild：rebuild the openvasmd database

![image012.png](https://image.3001.net/images/20170427/14932860886100.png!small)

安装完成后，在应用程序---〉漏洞分析中会出现openvas这个应用，如下图：

![image013.png](https://image.3001.net/images/20170427/14932860946408.png!small)

 **注意：openvas** **安装好之后并没有openvas-restart** **命令和openvas-status**
**命令，该命令需要自定义安装。**

在/usr/bin目录下，新建两个文件夹，分别为openvas-restart和openvas-status，然后赋予这两个文件可执行的权限：

![image014.jpg](https://image.3001.net/images/20170427/14932861021005.jpg!small)

openvas-restart和openvas-status内容分别如下：

![image015.png](https://image.3001.net/images/20170427/14932861146628.png!small)

之后就能够使用openvas-restart命令重启系统，使用openvas-status察看openvas系统状态了:

![image016.jpg](https://image.3001.net/images/20170427/14932861211400.jpg!small)

![image017.jpg](https://image.3001.net/images/20170427/14932861278096.jpg!small)

可以看到openvas目前处于运行状态。

##  **kali linux** **启动openvas**

由于OpenVAS是基于C/S，B/S架构进行工作的，所以，如果要使用该漏洞检测系统，必须先将OpenVAS服务启动，客户端才能连接进行测试。

双击应用程序中的openvas start启动openvas服务，出现如下界面：

![image018.png](https://image.3001.net/images/20170427/14932861323614.png!small)

或者输入命令行程序openvas-start来启动openvas服务

![image019.jpg](https://image.3001.net/images/20170427/14932861382557.jpg!small)

##  **使用客户端访问openvas** **服务器**

当openvas服务成功启动后，用户就可以连接openvas服务器并进行扫描了。根据前面的介绍，可知openvas有三种不同的客户端，分别是：OpenVAS命令行接口，Greenbone安全助手和Greenbone桌面套件。而且客户端能够用于各种操作系统。在kali
linux中，默认安装的是Greenbone安全助手。

本部署方案中使用最简单的浏览器客户端方式访问OpenVAS服务。因为，这种使用方式不仅简单，而且不需要客户额外安装应用程序，避免了枯燥的命令行方式，用户在任何操作系统中只要通过浏览器就可以在本地或远程连接OpenVAS服务器来对目标主机或网络进行漏洞检测。

##  **通过使用浏览器客户端访问openvas** **服务器进行漏洞检测**

然后我们使用客户层组件Greenbone-security-assistant访问openvas服务器，通过浏览器来建立扫描任务。

![image020.jpg](https://image.3001.net/images/20170427/14932861455595.jpg!small)

  

![image021.jpg](https://image.3001.net/images/20170427/14932861514635.jpg!small)

绿骨安全助手 GSA（ Greenbone Security Assistant）是开放漏洞评估系统 OpenVAS（OpenVulnerability
Assessment System）的基于网页的用户图形界面。 GSA 通过 OpenVAS Management Protocol (OMP) 连接
OpenVAS Manager。 通过实现完整的 OMP 特性集合，GSA 提供了一个直接了当的、非常强力的途径以管理网络漏洞扫描。

##  **配置外部访问**

安装完成后，openvas默认设置的监听地址为127.0.0.1，每次使用都只能用linux虚拟机打开浏览器通过<https://127.0.0.1:9392>来进行登录扫描，不如通过自己的电脑浏览器连接到openvas服务器直接进行扫描来的方便。

如果openvas安装在远程服务器或者虚拟机里面，则必须用服务器或者虚拟机打开浏览器来扫描，这样比较麻烦。用户更加希望，通过自己的电脑浏览器连接到openvas服务器，直接进行扫描。下面介绍配置外部访问的方法：

openvas新版本有两种方式控制openvas的开关，一种是服务的方式，一种是脚本的方式。

### 1.服务的方式

这种方式是通过openvas-start/openvas-stop脚本启动和关闭的，这两个脚本里调用的是service指令。启动openvas服务的脚本都存放在/lib/systemd/system下。

修改三个配置文件openvas-manager.service，openvas-scanner.service和greenbone-security-assistant.service，将配置文件中的监听IP由127.0.0.1改为0.0.0.0（相比于更改为openvas服务器的实际IP地址，改为0.0.0.0会更好，因为0.0.0.0代表本机的任意地址，适用于服务器有多个IP或者服务器IP有变动的情况）。修改后的三个配置文件内容如下：

![image022.jpg](https://image.3001.net/images/20170427/14932861591943.jpg!small)

![image023.jpg](https://image.3001.net/images/20170427/14932861686842.jpg!small)

![image024.jpg](https://image.3001.net/images/20170427/14932861999226.jpg!small)

### 2.脚本的方式

需要三个脚本控制开启和关闭openvas，

> /etc/init.d/openvas-manager //管理manager服务
>
> /etc/init.d/openvas-scanner //管理scanner服务
>
> /etc/init.d/greenbone-security-assistant //管理gsad服务

这三个脚本对应了三个配置文件，分别为：

> /etc/default/openvas-manager
>
> /etc/default/openvas-scanner
>
> /etc/default/greenbone-security-assistant

![image025.jpg](https://image.3001.net/images/20170427/14932862095677.jpg!small)

分别修改配置文件中的监听ip，由127.0.0.1改为0.0.0.0，保存。修改后三个配置文件的内容分别如下：

![image026.jpg](https://image.3001.net/images/20170427/14932862189903.jpg!small)

![image027.jpg](https://image.3001.net/images/20170427/14932862256116.jpg!small)

![image028.jpg](https://image.3001.net/images/20170427/14932862605911.jpg!small)

察看openvas的监听地址，如下图：

![image029.jpg](https://image.3001.net/images/20170427/14932862678159.jpg!small)

![image030.jpg](https://image.3001.net/images/20170427/14932862776249.jpg!small)

或者使用ps aux | less命令查看系统目前正在运行的进程。

可以看到,openvas监听地址已由127.0.0.1变为0.0.0.0。

察看linux虚拟机的IP地址为192.168.9.208：

![image031.jpg](https://image.3001.net/images/20170427/14932862843282.jpg!small)

在不登录linux服务器的情况下，即可在本机windows系统的客户端浏览器中输入<https://192.168.9.208:9392/login/login.html>连接openvas服务器进行漏洞检测。

 **注意：要保证主机和虚拟机间能通信。经过在多台台式机测试，测试者都能通过自己台式机浏览器连接我部署的openvas**
**漏洞检测系统进行主机和网络安全测试。**

![image032.jpg](https://image.3001.net/images/20170427/14932862952811.jpg!small)

 ***本文作者：魅影儿，转载请注明来自FreeBuf.COM**

