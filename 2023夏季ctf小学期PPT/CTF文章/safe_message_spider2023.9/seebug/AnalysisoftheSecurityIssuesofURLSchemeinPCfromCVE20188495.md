**Author: 0x7F@Knownsec 404 Team**  
**Date: October 18, 2018**  
**Chinese Version:<https://paper.seebug.org/719/>**

### 0x00 Introduction

Inspired by the CVE-2018-8495 vulnerability, this paper analyzes and studies
the security issues of `url scheme` in PC for the purpose of learning.

This is not a new issue when it comes to the security problems of `url
scheme`. As early as 2008, there were related research and exploits. In 2018,
security issues have emerged, including the Electron command injection
(CVE-2018-1000006) in January and the Edge RCE (CVE-2018-8495) in October. So
it's worth exploring the security issues of `url scheme`.

`url scheme` is also known as `url protocol` or `url handler`, and this
article uses `url scheme`.

### 0x01 What’s URL Scheme

**The common application scenario of url scheme**

In the process of using a computer, you will often find that clicking on a
certain link will try to launch a local application, for example, clicking on
`mailto://test@test.com` will launch the Mail client; clicking on
`thunder://xxxxx` will launch the Thunder client. This is just the application
of the `url scheme`. In addition, we can also find that there are some
different prefixes in the address of the browsers, such as `http://`,
`https://`, `ftp://` and `file://`, which is also the application scenario of
`url scheme`.

In order to improve the user experience and enrich the functionality of the
browsers, major operating systems and browser developers allow developers to
associate URLs with local applications so that when a user uses a browser,
they can launch an application by clicking on a link; this function is simply
referred to as a `url scheme`. For example, using IE8 under Windows 7 to
launch the default mail client `outlook`:

![
](https://images.seebug.org/content/images/2018/10/60ecaa63-c34f-4e9c-adac-8c247d6dc9d3.png-w331s)

Due to the excellent function design of `url scheme`, various major operating
system developers have supported it. No matter it is Windows, MAC, Linux for
PC, or iOS, Android for phones, they all have good supports to `url shceme`.
This article analyzes the security issues of `url scheme` under PC. There are
similar problems under the mobile, but the exploits are different, and no more
details here.

**The workflow of url scheme**

Having understood the function of the `url scheme`, you can roughly know about
that the workflow of the `url scheme`. The application registers the `url
scheme` item in the operating system. When the browser or other url-enabled
application accesses a specific `url scheme`, the corresponding `url scheme`
item is matched from the system to start the application; it can be seen that
this is a function supported mutually by three parties.

![
](https://images.seebug.org/content/images/2019/07/7eaba134-9f63-4f40-b99e-7d5573091128.png-w331s)

Because of this, for the function of `url scheme`in the operating system,
browser (or other applications that support url) or application, no matter
which part of them has security issues or there are problems in their mutual
support, it will affect the function of `url scheme` and eventually bring
security issues to users.

### 0x02 Create URL Scheme

So how is the `url scheme` registered in the operating system? Different
operating systems have different ways of implementation, here illustrates by
taking Windows 7 for example.

In Windows 7, the `url scheme` is recorded under the `HKEY_CLASSES_ROOT`
registry, such as the related fields of mailto:

![
](https://images.seebug.org/content/images/2018/10/f57908a8-534f-465f-b754-9058f07119ea.png-w331s)

If you want to create a new `url scheme`, simply add it to `HKEY_CLASSES_ROOT`
and fill in the corresponding values in the corresponding fields. The created
subitem name is just the name of `url scheme` function, and under that subitem
are also two items: `DefaultIcon` and `shell`. `DefaultIcon` contains the
default icon path used by this feature. Continue to create subkeys under the
`shell` item, for example: `open`, and then create a `command` subkey under
the `open` item to describe the path and parameters of the application.

For example, create `calc` to start `C:\Windows\System32\calc.exe`:

    
    
    HKEY_CLASSES_ROOT
        calc
        (Default) = "URL:Calc Protocol"
        URL Protocol = ""
        DefaultIcon
        (Default) = "C:\Windows\System32\calc.exe,1"
        shell
            open
                command
                    (Default) = "C:\Windows\System32\calc.exe" "%1"

PS: In fact, there are two ways to add `url scheme` in Windows. The above is
the way to add the registry directly (Pluggable Protocol), and the other is
the Asynchronous Pluggable Protocol. The registered protocol will be recorded
under `HKEY_CLASSES_ROOT\PROTOCOLS\`. For more details, you can refer to:
<https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa767916(v%3dvs.85)>.

### 0x03 Security Risks

For the `url scheme` function, simply speaking, it's that you can start a
local application through url, which undoubtedly greatly improves the user
experience, but at the same time brings some security risks, such as the user
can start a malicious program through the browser, or the application launched
by the user has special features and can be called (e.g. delete files, start
network connection).

In addition, for related applications that contain urls, the client is often a
user, a reader, not an editor; that is to say, urls can be maliciously
constructed by attackers to achieve the effect of launching local applications
remotely.

![
](https://images.seebug.org/content/images/2019/07/3882fadc-3346-41be-86aa-8ccc2ba74250.png-w331s)

So in the operating system, what `url scheme` can be called? Here are three
scripts for exporting the `url scheme` under the three major PC systems:

Windows: [<https://images.seebug.org/archive/duh4win.vbs>]  
MAC: [<https://images.seebug.org/archive/duh4mac.m>]  
Linux: [<https://images.seebug.org/archive/duh4linux.sh>]

(The scripts source: <https://www.blackhat.com/presentations/bh-europe-08/McFeters-Rios-Carter/Whitepaper/bh-eu-08-mcfeters-rios-carter-WP.pdf>)

When you run scripts, you can see that there are many `url schemes` that can
be called under the system, including those supported by the operating system
by default, such as `HTTP`, `FTP` and `mailto`, as well as third-party
applications, such as QQ and Thunder. If there are security issues with these
applications, such as support for deleting files, launching another programs,
and other sensitive operations, the security issues will be triggered remotely
with the help of the `url scheme`.

In addition to security issues that may arise with the application, browsers
(or other programs) can also have security issues in the process of url
parsing and launching the application. And there may still be problems when
these three parties support each other. No matter which part occurs security
issues, its harm will eventually be magnified in `url scheme`.

This paper analyzes the possible security issues mentioned above and gives
examples.

### 0x04 Issues in Operating System

In 2007, Heise Security exposed a remote command execution vulnerability
caused by `url scheme`, which appeared in Windows XP that has installed IE7,
and affected all applications that supported the `url scheme`.

The constructed PoC is as follows:

    
    
    mailto:test%../../../../windows/system32/calc.exe".cmd

The running results in Windows XP is as follows:

![
](https://images.seebug.org/content/images/2018/10/c3b62a18-7480-469b-8457-062c2426912c.png-w331s)

The image source: <http://www.h-online.com/security/news/item/URI-problem-also-affects-Acrobat-Reader-and-Netscape-733744.html>.

The cause for the vulnerability is that Microsoft changed the operating
system's handling of url by installing IE7 for Windows XP, and the application
directly passes the path to the operating system for startup, eventually
resulting in a special link containing `%` to start arbitrary program.

After the vulnerability was disclosed, Microsoft did not release a fix and
thought it was not the cause of Windows XP. Later, major application
developers fixed the vulnerability. Of course, the upper application can check
the input parameters, but it can also be considered that it is the operating
system that resulted in the `url scheme` remote command execution.

### 0x05 Browser Parameter Injection

In 2018, among the security issues of `url scheme`, there are two problems
caused by the IE and Edge parameters injection under Windows. One is Electron
Custom Protocol Command Injection (CVE-2018-1000006) and the other is Edge
Remote Code Execution (CVE-2018-8495).

Under Windows, IE and Edge handle url scheme differently. After the browser
receives a `url scheme`, it accesses the registry to query the corresponding
application path, and then decodes the url, and then calls the `ShellExecute`
function cluster to launch the application. It is because of the url decoding
that causes the double quotes to close, thus causing the parameter injection.

![
](https://images.seebug.org/content/images/2019/07/a323c9b4-05a2-436d-80e2-e3bf7b3cd504.png-w331s)

**Electron Custom Protocol Command Injection**

In January 2018, Electron released a security bulletin about the custom
protocol command injection (CVE-2018-1000006). It is triggered by parameter
injection, and the constructed PoC is as follows:

    
    
    chybeta://?" "--no-sandbox" "--gpu-launcher=cmd.exe /c start calc

Access the link via IE browser, the final generated startup parameters are as
follows:

    
    
    electron.exe "//?" "--no-sandbox" "--gpu-launcher=cmd.exe /c start calc"

Call the `--gpu-launcher` parameter supported in electron through parameter
injection, and input `cmd.exe`, the calculator is started as shown below:

![
](https://images.seebug.org/content/images/2018/10/b6207ca0-8871-4175-8e06-3e3eb4cef875.png-w331s)

Image via <https://xz.aliyun.com/t/1990>

**Edge Remote Code Execution**

In October 2018, Edge released the security bulletin for remote code execution
(CVE-2018-8495), which also exploited parameter injection to achieve the
effect of remote code execution. The whole exploit is quite ingenious, and
this article analyzes it in detail.

First of all, in the Edge, you can open some illegal `url scheme` (not include
the `URL Protocol` field), such as the `WSHFile` item:

![
](https://images.seebug.org/content/images/2018/10/608e46de-59df-48f5-abee-8aae2384fcbb.png-w331s)

Of course, it cannot be opened under Windows 7 and Windows 8.

And the `WSHFile` item just points to `wscript.exe`. This application is very
familiar, and it is a built-in script interpreter for Windows, then you can
try to use `WSHFile` to run a script. In addition to the above mentioned
problem of parameter injection in the Edge browser, is there a script that can
receive parameters and be used for execution?

Finally, it’s found out that:

    
    
    C:\Windows\WinSxS\amd64_microsoft-windows-a..nagement-appvclient_
    31bf3856ad364e35_10.0.17134.48_none_c60426fea249fc02\SyncAppvPublishingServer.vbs

The script supports receiving parameters and splices commands directly into a
string, and then executes them through `powershell`.

    
    
    psCmd = "powershell.exe -NonInteractive -WindowStyle 
     Hidden-ExecutionPolicy RemoteSigned -Command &{" & syncCmd & "}"

The final constructed PoC is as follows:

    
    
    <a id="q" href='wshfile:test/../../WinSxS/AMD921~1.48_/SyncAppvPublishingServer.vbs" test test;calc;"'>test</a>
    <script>
    window.onkeydown=e=>{
        window.onkeydown=z={};
        q.click()
    }
    </script>

And the triggered results after execution are as follows:

![](https://images.seebug.org/content/images/2018/10/284eb855-65c8-45b3-83cc-a25ba19c6f5e.png-w331s)

A patch has been released on Windows10, and Edge is no longer able to call
this illegal `url scheme`.

In addition, we also found a `url scheme` similar to `WSHFile` in the
`HKEY_CLASSES_ROOT` registry, pointing to `wscript.exe`, which can also
trigger remote code execution. These include:

    
    
    1.wshfile
    2.wsffile
    3.vbsfile
    4.vbefile
    5.jsefile

What’s more, in `C:\Windows\System32\` exists `SyncAppvPublishingServer.vbs`
as well, which can also be exploited and even more reliable than what has been
provided in the released bulletin.

Apart from `SyncAppvPublishingServer.vbs`, the `pubprn.vbs` under
`C:\Windows\System32\Printing_Admin_Scripts\zh-CN` can also trigger the remote
code execution.

PS: Under Windows 7, Chrome has the same features as Edge: some illegal `url
schemes` can be opened, but Chrome has no problem with parameter injection, so
it's temporarily considered to be safe.

### 0x06 The Application Issues

In December 2017, the helpViewer application on MacOS was exposed a file
execution vulnerability (cve-2017-2361) caused by XSS, affecting versions
below MacOS Sierra 10.12.1. The vulnerability also exploits the `url scheme`,
which allows an attacker to construct a malicious page to launch a remote
attack. This is typical security issue of `url scheme` caused by the
application.

For more details about the vulnerability, you can refer to:
[https://bugs.chromium.org/p/project-zero/issues/detail?id=1040&can=1&q=reporter%3Alokihardt%40google.com%20&sort=-reported&colspec=ID%20Status%20Restrict%20Reported%20Vendor%20Product%20Finder%20Summary&start=100](https://bugs.chromium.org/p/project-zero/issues/detail?id=1040&can=1&q=reporter%3Alokihardt%40google.com%20&sort=-reported&colspec=ID%20Status%20Restrict%20Reported%20Vendor%20Product%20Finder%20Summary&start=100).

The constructed PoC is as follows:

    
    
    document.location = "help:///Applications/Safari.app/Contents/
    Resources/Safari.help/%25252f..%25252f..%25252f..%25252f..%25252f..%25252f..
    %25252f/System/Library/PrivateFrameworks/Tourist.framework/Versions/A/
    Resources/en.lproj/offline.html?redirect=javascript%253adocument.write(1)";

During the exploitation of this vulnerability, you can find that the operating
system and the browser do not have problems, but the application opened
through the `url scheme` has problems. Through the analysis of the
exploitation chain, we can learn several clever tricks:

  1. Open the `Safari.help` via the `help` protocol in `url scheme`.

  2. Use double url encoding to bypass the helpViewer's check of the path and open a page where JavaScript can be executed.

  3. Open the application via the built-in protocol `x-help-script` in helpViewer (not included in PoC).

### 0x07 Conclusion

The convenience of `url scheme` comes from the mutual support of the operating
system, the browser (or other applications that support urls), and the
application. In order to ensure the security and reliability of `url scheme`,
the security of these three parties must be firmly guarded.

In addition, different operating systems have different ways of implementing
`url scheme`, different browsers have their own features, and applications
have their own processing methods. As a result of multiple combinations, some
unexpected security issues may occur.

Finally, I would like to appreciate @LoRexxar' and @dawu of Knownsec 404 Team
for helping me.

### References:

  1. CVE-2018-8495分析: <https://leucosite.com/Microsoft-Edge-RCE/>
  2. Seebug.paper: <https://paper.seebug.org/515/>
  3. 先知: <https://xz.aliyun.com/t/1990>
  4. electronjs: <https://electronjs.org/blog/protocol-handler-fix>
  5. blackhat: <https://www.blackhat.com/presentations/bh-europe-08/McFeters-Rios-Carter/Whitepaper/bh-eu-08-mcfeters-rios-carter-WP.pdf>
  6. blackhat: <https://www.blackhat.com/presentations/bh-dc-08/McFeters-Rios-Carter/Presentation/bh-dc-08-mcfeters-rios-carter.pdf>
  7. oreilly: <https://www.oreilly.com/library/view/hacking-the-next/9780596806309/ch04.html>
  8. Github: <https://github.com/ChiChou/LookForSchemes>
  9. MSRC.CVE-2018-8495: <https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8495>
  10. Microsoft: <https://docs.microsoft.com/en-us/windows/uwp/launch-resume/reserved-uri-scheme-names>
  11. Microsoft: <https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa767914(v=vs.85)>
  12. Microsoft: <https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa767916(v%3dvs.85)>
  13. h-online: <http://www.h-online.com/security/news/item/URI-problem-also-affects-Acrobat-Reader-and-Netscape-733744.html>
  14. chromium: [https://bugs.chromium.org/p/project-zero/issues/detail?id=1040&can=1&q=reporter%3Alokihardt%40google.com%20&sort=-reported&colspec=ID%20Status%20Restrict%20Reported%20Vendor%20Product%20Finder%20Summary&start=100](https://bugs.chromium.org/p/project-zero/issues/detail?id=1040&can=1&q=reporter%3Alokihardt%40google.com%20&sort=-reported&colspec=ID%20Status%20Restrict%20Reported%20Vendor%20Product%20Finder%20Summary&start=100)

### About Knownsec & 404 Team

Beijing Knownsec Information Technology Co., Ltd. was established by a group
of high-profile international security experts. It has over a hundred frontier
security talents nationwide as the core security research team to provide
long-term internationally advanced network security solutions for the
government and enterprises.

Knownsec's specialties include network attack and defense integrated
technologies and product R&D under new situations. It provides visualization
solutions that meet the world-class security technology standards and enhances
the security monitoring, alarm and defense abilities of customer networks with
its industry-leading capabilities in cloud computing and big data processing.
The company's technical strength is strongly recognized by the State Ministry
of Public Security, the Central Government Procurement Center, the Ministry of
Industry and Information Technology (MIIT), China National Vulnerability
Database of Information Security (CNNVD), the Central Bank, the Hong Kong
Jockey Club, Microsoft, Zhejiang Satellite TV and other well-known clients.

404 Team, the core security team of Knownsec, is dedicated to the research of
security vulnerability and offensive and defensive technology in the fields of
Web, IoT, industrial control, blockchain, etc. 404 team has submitted
vulnerability research to many well-known vendors such as Microsoft, Apple,
Adobe, Tencent, Alibaba, Baidu, etc. And has received a high reputation in the
industry.

The most well-known sharing of Knownsec 404 Team includes: [KCon Hacking
Conference](http://kcon.knownsec.com/#/ "KCon Hacking Conference"), [Seebug
Vulnerability Database](https://www.seebug.org/ "Seebug Vulnerability
Database") and [ZoomEye Cyberspace Search Engine](https://www.zoomeye.org/
"ZoomEye Cyberspace Search Engine").

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/984/>

