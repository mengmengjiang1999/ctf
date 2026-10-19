![](https://image.3001.net/images/20210201/1612161631_6017a25faa565a93899ae.jpg!small)

根据媒体的最新报道，意大利CERT的研究人员警告称，近期出现的新型Android恶意软件[ _Oscorp_](https://cert-agid.gov.it/news/oscorp-il-solito-malware-per-android/)正在利用手机的辅助服务（Accessibility Service）来进行恶意攻击。

近期，来自安全公司[ _AddressIntel_](https://www.addressintel.com/it/)的研究人员发现了一个名为[
_Oscorp_](https://cert-agid.gov.it/news/oscorp-il-solito-malware-per-android/)的新型Android恶意软件，而Oscorp这个名字来源于其命令和控制服务器登录页面的标题。

跟其他的Android恶意软件一样，Oscorp恶意软件会想办法欺骗用户授予恶意软件访问Android设备辅助功能服务的权限。这也就意味着，攻击者将能够通过[
_Oscorp_](https://cert-agid.gov.it/news/oscorp-il-solito-malware-per-android/)来读取目标Android设备屏幕上的文本信息，确认应用程序弹出的安装提示，滚动权限列表并冒充用户点击屏幕上的安装确认按钮。

来自意大利CERT的研究人员在其发布的[ _安全报告_](https://cert-agid.gov.it/news/oscorp-il-solito-malware-per-android/)中提到：“由于无法访问其他应用程序的私有文件，这些恶意应用程序的行为“仅限于”通过网络钓鱼页面来实现凭证窃取、锁定屏幕（设备）以及捕捉和记录音频和视频信息等恶意行为。”

就在几天之前，安全研究专家还发现了一个地址为“supportoapp [.] Com”的域名，这个域名主要负责托管恶意软件的“Client
assistance.apk”文件。

当这个APK文件在目标设备上安装成功之后，将会显示一个名为“Customer
Protection”的应用程序，它会要求用户启用Android设备的辅助功能服务。

![](https://image.3001.net/images/20210201/1612161643_6017a26bd452d52caa748.png!small)

这款恶意软件会使用Geny2服务来诱导用户启用辅助功能服务，一旦激活该服务，就会自动启用一些其他的权限。

恶意软件Oscorp的代码每八秒便会重新打开一次设置界面，并强制用户授予恶意软件所请求的访问权限以及设备使用统计信息。

启用辅助功能服务之后，恶意软件将能够实现下列操作：

> 启用键盘记录功能；
>
> 自动获取恶意软件所需的权限和功能；
>
> 卸载应用程序；
>
> 拨打电话；
>
> 发送短信；
>
> 窃取加密货币；
>
> 窃取Google的双因素PIN码；

在研究人员对这款恶意软件样本进行分析时，恶意软件所使用的钱包里面只剩了584美元。

CERT的报告提供了有关恶意软件Oscorp所实现的技术细节，比如对服务的描述，例如用于在设备上收集信息的PJService等等。而恶意软件在跟远程C2服务器进行通信时，使用的是HTTP
POST请求。

当用户打开Oscorp针对的某个应用程序时，恶意代码将显示一个仿冒网页，并要求用户提供自己的用户名和密码。

其实，每个应用程序所显示的伪造界面样式都是不一样的，其核心目的就是为了诱导目标用户提供自己的个人信息以及凭证数据。

CERT-AGID的报告总结道：“在用户启用辅助功能服务之前，Android系统的保护机制可以防止恶意软件对目标设备或目标用户造成任何形式的损害。但是，一旦启用了辅助功能服务，那么后果将不堪设想。实际上，Android对应用程序开发者一直有着非常宽松的政策，最终决定是否信任某个应用程序的是终端用户。”

