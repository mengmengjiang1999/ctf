## 0x00 简介

Exchange Server
是Mirosoft的一个消息与协作系统，可以用来构架用于企业或学校的邮件系统或免费邮件系统。它提供了包括从电子邮件、会议安排、团体日程管理、任务管理、文档管理实时会议和工作流等丰富的协作应用，而所有应用支持Internet浏览器来访问。

## 0x01 漏洞概况

该漏洞可在Exchange中构造SSRF漏洞，攻击者可以利用该漏洞构造任意HTTP请求并绕过EXchange
Server身份验证，从而利用该漏洞窃取用户邮箱中的内容或进行内网探测。

## 0x02 影响版本

    
    
    MicrosoftExchange2013  
    ​  
    MicrosoftExchange2016  
    ​  
    MicrosoftExchange2010  
    ​  
    MicrosoftExchange2019

## 0x03 环境搭建

此次测试使用的是Windows Server 2016 ，使用的是管理员身份登录（密码已经设置，不设置密码后面安装的时候会出现错误

新建一个域，打开服务器管理器，选择添加角色和功能

![20210726220834.png](https://image.3001.net/images/20210805/1628152542_610ba2deab1e3a4fe9abd.png!small)

点击下一步至"服务器角色"，勾上"Active Directory域服务"和"DNS服务器"（记得配静态IP）

![20210726220813.png](https://image.3001.net/images/20210805/1628152543_610ba2dfa45fa00b99b19.png!small)

点击下一步至"确认"，勾选"如果需要，自动重新启动目标服务器"

![20210726220902.png](https://image.3001.net/images/20210805/1628152544_610ba2e0a42603769e306.png!small)

下一步至安装，完成后点击页面中的"将此服务器提升为域控制器"

![20210726221303.png](https://image.3001.net/images/20210805/1628152545_610ba2e19aace7172f112.png!small)

点击"添加新林"，并填写根域名

![20210726221349.png](https://image.3001.net/images/20210805/1628152546_610ba2e27ddd23ac12712.png!small)

输入密码

![20210726221603.png](https://image.3001.net/images/20210805/1628152547_610ba2e353065f0c3243f.png!small)

进行先决条件检，通过后点击安装

![20210726221904.png](https://image.3001.net/images/20210805/1628152548_610ba2e44d8e228106383.png!small)

成功后会自动重启

![20210726223119.png](https://image.3001.net/images/20210805/1628152550_610ba2e695a892f73558b.png!small)

![20210727135401.png](https://image.3001.net/images/20210805/1628152553_610ba2e9883958edc5822.png!small)

下载和安装相应的组件 网址为

    
    
    https://docs.microsoft.com/zh-cn/exchange/plan-and-deploy/prerequisites?view=exchserver-2016

组件安装好之后，打开Exchange 的ISO文件，双击setup.exe

![20210726223754.png](https://image.3001.net/images/20210805/1628152554_610ba2ea550c0a6a6b1e0.png!small)

选择不更新

![20210726223827.png](https://image.3001.net/images/20210805/1628152555_610ba2eb53b5d6d7b1f4e.png!small)

下一步，勾选不使用推荐设置

![20210726224127.png](https://image.3001.net/images/20210805/1628152556_610ba2ec3e88e47214345.png!small)

![20210726224208.png](https://image.3001.net/images/20210805/1628152557_610ba2ed2f23884b12bae.png!small)

勾选"邮箱角色"和"自动安装Exchange Server 安装所需的Windows Server角色和功能"

![20210726224233.png](https://image.3001.net/images/20210805/1628152557_610ba2edce8d1d70b30f5.png!small)

可更改Exchange组织的名称，这里我改为 zeeker Organization

![20210727005422.png](https://image.3001.net/images/20210805/1628152558_610ba2ee86b0d01c1d344.png!small)

点击下一步进行准备情况检查，会提示进行更新（上边链接中有给出，下载安装即可）

![20210727005621.png](https://image.3001.net/images/20210805/1628152559_610ba2ef5514049f48f3c.png!small)

点击安装，会提醒重启电脑。

重启后输入<http://ip/ecp>可以到达Exchange管理中心，使用域名/用户名 密码即可登录

![20210727144440.png](https://image.3001.net/images/20210805/1628152560_610ba2f01bc46c2b91c1b.png!small)

![20210727150351.png](https://image.3001.net/images/20210805/1628152560_610ba2f0d157e48db0cb9.png!small)

## 0x04 漏洞复现

1.下载exp

网上有好几种版本的exp，使用最多的那个有些问题，这里不推荐使用

本次测试使用的exp地址为

    
    
    https://github.com/p0wershe11/ProxyLogon

在Windows攻击机上执行以下指令：

    
    
    pythonC:\User\Administrator\Desktop\proxyLogon.py--host-zeeker.com--mail=Administrator@zeeker.com

![20210730194524.png](https://image.3001.net/images/20210805/1628152561_610ba2f1c8bd8f2a85c5e.png!small)

2.成功上传一句话，使用菜刀进行连接

![image-20210730202136958](https://image.3001.net/images/20210805/1628152562_610ba2f2a5a900d21f30c.png!small)

连接成功

![20210730192717.png](https://image.3001.net/images/20210805/1628152563_610ba2f38d21400d4b383.png!small)

aspx文件内容如下

![20210730201049.png](https://image.3001.net/images/20210805/1628152564_610ba2f4528a6c4929e44.png!small)

## 0x05 修复建议

微软官方已经发布了解决上述漏洞的安全更新，建议受影响用户尽快升级到安全版本，官方安全版本下载可以参考以下链接：

    
    
    CVE-2021-26855: https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26855  
    ​  
    CVE-2021-26857: https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26857  
    ​  
    CVE-2021-26858: https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26858  
    ​  
    CVE-2021-27065: https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-27065

