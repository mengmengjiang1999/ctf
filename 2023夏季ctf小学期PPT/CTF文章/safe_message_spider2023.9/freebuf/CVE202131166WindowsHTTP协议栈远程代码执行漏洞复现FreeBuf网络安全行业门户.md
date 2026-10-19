## 0x00 简介

HTTP全称是Hyper Transfer protocol
，即超文本传输协议，当今普遍采用版本Http1.1，HTTP协议已属于应用层协议，它构建在TCP之上，处于TCP/IP架构的顶端，它是为Web浏览器与
Web 服务器之间的通信而设计的，Windows上的HTTP协议栈用于windows上的Web服务器，例如Internet Information
Services（IIS）等，若该协议栈相关的组件存在漏洞，则可能导致远程恶意代码执行

## 0x01 漏洞概述

微软官方发布5月安全更新补丁，其中修复了一个HTTP协议栈远程代码执行漏洞（CVE-2021-31166），该漏洞存在于Windows 10和Windows
Server中的HTTP协议栈(http.sys)处理程序中。未授权的攻击者可以构造恶意请求包攻击目标服务器，成功利用该漏洞的攻击者可以在目标服务器执行任意代码，微软表示此漏洞可用于蠕虫式传播，影响十分广泛。该漏洞是由于HTTP协议栈相关组件在处理存在多个Accept-Encoding字段的HTTP请求时存在Use-After-Free的漏洞，攻击者可利用该漏洞在未授权的情况下，构造恶意数据执行远程代码执行攻击，最终获取服务器最高权限

## 0x02 影响版本

![1626677122_60f51f825eeacbb15dd8f.png!small?1626676865887](https://image.3001.net/images/20210719/1626677122_60f51f825eeacbb15dd8f.png!small?1626676865887)

## 0x03 环境搭建

1.安装虚拟机应用程序（本次测试使用的是VMware Workstation Pro16.1版本）

软件获取和安装可自行上网搜索相关教程

2.安装受漏洞影响的版本的Windows系统，本次测试使用的操作系统环境如下：

    
    
    版本Windows 10 专业版  
    版本号20H2  
    安装日期•2021/•6/•20  
    操作系统内部版本19042.804  
    体验Windows Feature Experience Pack 120.2212.551.0

3.开启IIS

首先打开控制面板，点击卸载程序，如下图所示：

![image-20210712114514779](https://image.3001.net/images/20210719/1626677870_60f5226e0e50d39a0f316.png!small)

点击“启用或关闭Windows功能”，如下图所示：

![image-20210712114701656](https://image.3001.net/images/20210719/1626677871_60f5226f49dcf7e7b044d.png!small)

找到列表中的"Internet Information Service"项，并点击左边的复选框，如下图所示：

![image-20210712114804668](https://image.3001.net/images/20210719/1626677872_60f52270517d0baaab95b.png!small)

点击后则会自动选择其中的“Web管理工具”和“万维网服务”，如下图所示：

![image-20210712114922251](https://image.3001.net/images/20210719/1626677873_60f52271238dc46b7574f.png!small)

然后点击确定，等待更改完成后重启系统即可

![image-20210712115047220](https://image.3001.net/images/20210719/1626677873_60f52271e6607f75f9a2e.png!small)

## 0x04 漏洞复现

### 1.检测系统组件版本

    
    
    systeminfo|findstr"KB4598481 KB5003173 KB5000736"

其中"KB4598481"是一个独立的 SSU（服务堆栈更新），是另外两个LCU
（累积更新）安装的先决条件，服务堆栈更新（SSU）调整了Windows中的实际更新组件，并解决可能导致补丁无法在电脑上安装的问题

所以若无回显或者仅有"KB4598481"回显则说明没有安装修复CVE-2021-31166的更新补丁，如下图所示：

![image-20210712120540299](https://image.3001.net/images/20210719/1626677874_60f522727a5cf10f8628c.png!small)

  

### 2.查看测试靶机IP

执行以下指令：

    
    
    ipconfig

![image-20210712120611957](https://image.3001.net/images/20210719/1626677875_60f5227321697aa9990de.png!small)

目标靶机IP为 192.168.50.144

### 3.获取POC脚本

    
    
    https://github.com/0vercl0k/CVE-2021-31166/blob/main/cve-2021-31166.py

下载并保存到攻击机上

4.在攻击机Kali上运行POC脚本，执行以下指令：

    
    
    python3 cve-2021-31166.py --target192.168.50.144

其中 --target 参数后面解的是目标靶机的IP

![image-20210712115309379](https://image.3001.net/images/20210719/1626677875_60f52273c9ea358e17e78.png!small)

攻击机运行脚本后可以看到目标靶机立即发生蓝屏，验证了该漏洞确实存在

![image-20210710022041628](https://image.3001.net/images/20210719/1626677876_60f52274739e2806da439.png!small)

## 0x05 修复建议

微软官方已针对支持的产品版本发布了修复此漏洞的安全补丁，官方下载链接：

<https://msrc.microsoft.com/update-guide/en-us/releaseNote/2021-May>

打开上述链接，下载当前系统版本对应

