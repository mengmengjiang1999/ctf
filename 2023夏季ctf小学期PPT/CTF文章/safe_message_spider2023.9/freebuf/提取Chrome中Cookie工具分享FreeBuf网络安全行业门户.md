**这个工具将从Google
Chrome浏览器中提取Cookie，是一个.NET程序集，可以在C2中通过工具如[PoshC2](https://github.com/nettitude/PoshC2.git)使用或CobaltStrike的命令。**

> 项目地址是[SharpCookieMonster](https://github.com/m0rv4i/SharpCookieMonster.git)。

## 用法

只需将站点输入即可。

    
    
    SharpCookieMonster.exe [https://sitename.com] [chrome-debugging-port] [user data dir]

可选的第一个参数分隔chrome启动时最初连接的网站（默认为[https://www.google.com](https://www.google.com/)）。

第二个可选参数指定用于启动chrome调试器的端口（默认为9142）。

最后，可选的第三个参数指定用户数据目录的路径，可以覆盖该路径以访问不同的配置文件（默认为％APPDATALOCAL％\ Google \ Chrome \
User Data）。

![img](https://image.3001.net/images/20200213/1581579397_5e44fc85e808b.png!small)

![img](https://image.3001.net/images/20200213/1581579421_5e44fc9dbdb2d.png!small)

如您所见，它可用于提取session，httpOnly并通过C2传输cookie。它还已作为模块添加到PoshC2中，并设置了自动加载和别名功能，因此可以使用来简单地运行它`sharpcookiemonster`。

这也适用于CobaltStrike的，可以使用`execute-assembly`。

还值得注意的是，您不需要任何特权访问权限即可执行此操作，只需在存储会话的计算机上在该用户上下文中执行代码即可。

## 它是如何工作的？

在后台，这是通过首先启动Google Chrome来实现的。我们首先枚举任何正在运行的chrome.exe进程以提取其镜像路径，但是如果失败，则默认为C：\
Program Files（x86）\ Google \ Chrome \ Application \
chrome.exe。然后，我们启动该可执行文件，设置适当的标志并将该进程的输出重定向到我们的stdout，以便即使在C2通道上运行它时也可以查看它是否出错。

该`--headless`标志意味着chrome.exe实际上将在没有任何用户界面的情况下运行，但可以使用其API进行交互。对于红队成员而言，这是完美的选择，因为它将仅作为另一个chrome.exe进程出现，而不会向用户显示任何内容。然后，通过`--remote-debugging-port`标记为此过程启用远程调试，然后使用将数据目录指向用户的现有数据目录`--user-data-dir`。

![img](https://image.3001.net/images/20200213/1581579461_5e44fcc5d5f5a.png!small)

## 启动

启动后，我们将检查进程是否正在运行，并等待调试器端口打开。

然后，我们可以在该端口上与API交互以获取websocket调试器URL。该URL允许程序通过websockets上的API与Chrome的devtools进行交互，从而为我们提供了这些devtools的全部功能。所有这些操作都是在受害人的计算机上本地完成的，因为该二进制文件正在运行，而无界面的Chrome进程正在运行。

![img](https://image.3001.net/images/20200213/1581579441_5e44fcb1122d3.png!small)

然后，我们可以发出请求以检索该配置文件的缓存中的所有cookie，并将其返回给操作员。

## 编译

如果您想自己构建二进制文件，只需克隆它并在Visual Studio中构建它即可。

该项目已设置为与.NET
3.5兼容，以便与安装较旧版本.NET的受害人兼容。但是，为了使用WebSockets与Chrome进行通信，添加了WebSocket4Net程序包。

如果要在C2上运行此命令（例如使用[PoshC2](https://github.com/nettitude/PoshC2)的`sharpcookiemonster`命令或通过CobaltStrike的命令），请`execute-assembly`使用ILMerge将生成的可执行文件与依赖库合并。

例如，首先重命名原始二进制文件，然后运行：

    
    
    ILMerge.exe /targetplatform:"v2,C:\Windows\Microsoft.NET\Framework\v2.0.50727" /out:SharpCookieMonster.exe SharpCookieMonsterOriginal.exe WebSocket4Net.dll SuperSocket.ClientEngine.dll

***参考来源：[jmpesp](https://jmpesp.me/sharpcookiemonster/)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**
****

