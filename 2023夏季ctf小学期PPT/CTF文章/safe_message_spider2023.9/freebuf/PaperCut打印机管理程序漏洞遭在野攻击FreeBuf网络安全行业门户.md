PaperCut 是一款企业打印管理软件，有 PaperCut NG 与 PaperCut MF
两款软件。除了管理打印之外，也可以通过硬件集成来管理扫描、复印与传真。

PaperCut MF 与 PaperCut NG 中发现了远程执行代码漏洞，影响 22.0.9 以及更早版本。该漏洞被确定为
CVE-2023-27350，CVSS 评分为 9.8。

## 漏洞详情

PaperCut 是使用 Java 开发的，专门为多服务器与跨平台而设计。典型使用场景中，一个主 PaperCut
服务器结合其他几台辅助服务器。辅助服务器上只运行轻量级监视组件，开启 9191 端口通过基于 HTTP 的 Web 服务于主服务器进行通信。

研究人员发现该软件存在 CVE-2023-27350 漏洞，该漏洞由于 SetupCompleted 类中的访问控制不当造成。

## 在野利用

几乎每个组织都有网络打印机，但只有极少的打印机直接暴露在互联网上。通过 Shodan 搜索，大概有 850 个 PaperCut
管理的打印机暴露在互联网上。

![image.png-719.7kB](https://image.3001.net/images/20230802/1690987943_64ca6da7ddfd6e688256a.png!small)全球分布情况

下图显示了在野的攻击利用尝试情况：

![image.png-81kB](https://image.3001.net/images/20230802/1690987945_64ca6da985ff1e94485e8.png!small)在野攻击情况

微软也发现 Lace Tempest 开始使用 PaperCut 的漏洞传播 Clop 勒索软件。

![image.png-200kB](https://image.3001.net/images/20230802/1690987946_64ca6daa5401b3ef916b8.png!small)微软披露信息

## 漏洞利用分析

为了更好地了解 PaperCut 的漏洞，针对 SetupCompleted.java 进行了反编译。可以看到，代码使用管理员权限调用了
performLogin 方法，但并没有提供任何管理员权限凭据。

![image.png-409.4kB](https://image.3001.net/images/20230802/1690987947_64ca6dab207aa308d7c7e.png!small)登录功能代码

对文件进一步分析可知，performLogin 函数允许在没有任何凭据的情况下以管理员权限进行访问，从而使攻击者可以绕过身份验证。

![image.png-95.1kB](https://image.3001.net/images/20230802/1690987948_64ca6dac59ff22b0c2fb9.png!small)凭据绕过

为了证实分析结果，检查了 PerformLogin 函数。确认只要用户尝试登就会调用 loginUser 函数，即可通过凭据绕过获取管理员权限。

## 漏洞利用步骤

研究人员部署了测试环境进行分析，在 Windows Server 2016 上运行的 Papercut NG 17.4.4。

![image.png-777.4kB](https://image.3001.net/images/20230802/1690987949_64ca6dad0ece8f728376f.png!small)测试环境部署

### 步骤1

攻击者执行 POC 时，首先利用 CVE-20230=-27350 绕过身份验证并登录 PaperCut。网络请求如下所示，此时即为准备阶段已经完成。

![image.png-861.5kB](https://image.3001.net/images/20230802/1690987949_64ca6daddeb6d7a5d9daf.png!small)攻击准备阶段

应用程序会将攻击者重定向到 /app?service=page/Dashboard 的页面，如下所示。

![image.png-2297.8kB](https://image.3001.net/images/20230802/1690987951_64ca6daf6ff6eeaa9dc53.png!small)跳转页面

网络请求如下所示：

![image.png-321.1kB](https://image.3001.net/images/20230802/1690987952_64ca6db0eb0fcd5f2f41b.png!small)网络请求

### 步骤2

攻击者继续发送 HTTP POST 请求更新设置并启用脚本：

![image.png-491.3kB](https://image.3001.net/images/20230802/1690987954_64ca6db26765c2fbe4f6a.png!small)启用脚本

### 步骤3

启用脚本后，POC 会搜索所有打印机。如下所示，发现了 ID 为 l1001 的打印机：

![image.png-220kB](https://image.3001.net/images/20230802/1690987956_64ca6db40a45a046f372a.png!small)可用打印机列表

### 步骤4

找到打印机的详细信息后，攻击者就可以执行远程代码了。如下所示，执行 calc.exe 作为示例：

![image.png-537.1kB](https://image.3001.net/images/20230802/1690987957_64ca6db52183bb2b9ccb6.png!small)恶意代码执行

脚本执行后，可以看到 calc.exe 会被调用打开。

![image.png-468.3kB](https://image.3001.net/images/20230802/1690987958_64ca6db6145c0cd625090.png!small)远程代码执行成功

在 Process Explorer 中也能够看到该进程成功执行：

![image.png-973.5kB](https://image.3001.net/images/20230802/1690987959_64ca6db72da195748cfcc.png!small)Process
Explorer

pc-server.exe 与 win32calc.exe 都是由用户 NT AUTHORITY\SYSTEM
执行的，两个可执行文件都是从同一目录下运行的：

![image.png-886.1kB](https://image.3001.net/images/20230802/1690987961_64ca6db92e398afd2e110.png!small)子进程计算器

尽管研究人员只是执行了计算器，但攻击者会执行更多其他的恶意攻击。例如执行 PowerShell 脚本建立反向 Shell，或者像微软发现的部署勒索软件。

该漏洞是由于对名为 SetupCompleted 的 Java
类的访问控制不当导致的，理论上只有管理员与本地用户才能访问该类。由于缺少访问控制检查，网络上的任何用户都可以远程访问该文件，从而导致远程代码执行。

## 参考来源

> [Juniper](https://blogs.juniper.net/en-us/threat-> research/cve-2023-27350-papercut-ng-and-mf-remote-code-execution-> vulnerability)

