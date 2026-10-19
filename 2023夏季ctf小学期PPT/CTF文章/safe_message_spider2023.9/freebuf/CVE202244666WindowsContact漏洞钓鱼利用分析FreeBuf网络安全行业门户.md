![](https://image.3001.net/images/20230804/1691117904_64cc695000fa112e0d5ec.jpg!small)

# ****0x00 背景****

Windows
Contact是一种文件类型，用于存储和管理Windows操作系统中的联系人信息。它是一种通用的联系人数据格式，包含个人或组织的姓名、地址、电话号码、电子邮件地址等联系信息。

此漏洞早在19年就公开发布过0day公告，Windows在处理 Contact 文件时存在特定缺陷，在联系人文件中构建的数据可能会导致 Windows
显示危险的超链接。用户界面无法提供足够的危险指示，攻击者可以利用此漏洞在当前用户的上下文中执行代码。

2022年12月13日，微软针对该漏洞发布了补丁，但是该补丁仍然能够被绕过，影响范围包括最新的Windows系统版本，攻击者通过社会工程学手法诱导用户交互，将导致目标主机失陷。

#  ** **0x01 漏洞成因分析****

首先对公开poc进行分析，发现其在syslink控件中，直接调用了payload.lnk文件，

![](https://image.3001.net/images/20230804/1691117490_64cc67b2bbdd7b78e961d.jpg!small)

由于其是个进程创建事件，为了方便定位漏洞位置，直接上调试器，在进程创建函数也就是在SHELL32!ShellExecuteExW中下断点，定位堆栈如下。

![](https://image.3001.net/images/20230804/1691117523_64cc67d3dcc3141a7e59a.png!small)

可以看出进程创建发生在wab32.dll中的SafeExecute函数中。

![](https://image.3001.net/images/20230804/1691117538_64cc67e254077cba96351.jpg!small)

分析函数功能，函数首先判断URL是否为本地文件（通过UrlIsW函数），如果是，则调用AESAttemptExecute尝试以管理员权限运行文件并返回执行结果；否则，使用ShellExecuteExW函数打开URL对应的应用程序（如果在系统中没有找到该应用程序，则返回错误代码），并返回执行结果。在microsoft文档中对其也有解释，

![](https://image.3001.net/images/20230804/1691117560_64cc67f891126a43e0666.jpg!small)

所以该函数本质上就是提供了执行程序的功能，只是对href中的值没有做足够的过滤，导致其可以执行我们的自定义程序，而这也为我们后续提供其绕过过滤带来了可能性。

#  ** **0x02 漏洞绕过分析****

对补丁进行diff，发现主要在fnSummaryProc→SafeExecute函数的路径上添加了判断，现在在调用SafeExecute前，会判断href字段是否是网络地址，如果不是，则进入IsInternetAddress函数判断地址是否合法后调用SafeExecute。

![](https://image.3001.net/images/20230804/1691117595_64cc681b84f2d98cbada9.png!small)

可能是为了兼容其他协议，IsInternetAddress这里在判断字段中如果存在@，则调用IsDomainName函数判断是否有域名，那么我们构造一个名为@payload.lnk的文件，依然符合域名规范，从而绕过。

![](https://image.3001.net/images/20230804/1691117610_64cc682a6bf7722b842b3.jpg!small)

于是绕过方式就比较简单，只要将我们即将执行的程序带有@字段，则可实现绕过，经过测试，目前最新版本的windows依然存在此问题。

#  ** **0x03 钓鱼利用风险****

### 利用手法赏析

进入文件资源管理器的联系人界面，即可新建Contact文件，如图，保存创建好的Contact文件后通过文本编辑器，可以查看Contact文件对应的原始xml内容。

![](https://image.3001.net/images/20230804/1691117656_64cc68589dafa87408959.png!small)

图：创建并查看Contact文件内容

利用该漏洞在Contact文件中的<c:Address>标签处构造恶意payload，如图，用户点击被恶意修改后的邮件地址信息，即可触发漏洞，打开对应路径下的恶意文件。

![](https://image.3001.net/images/20230804/1691117684_64cc68745609e90f63a9f.png!small)

图：Contact文件触发漏洞打开本地恶意文件

由于该漏洞需要在用户打开文件后诱导其点击才能触发，所以首先想到的就是需要想办法消除Contact文件中的html标签，如图，Contact文件中可显示的内容长度是固定的，只需要通过加入足够长的字符即可隐藏多余的标签显示，为了使Contact文件更具诱导性，下面的例子中通过在文件名中插入长空格和内容简单修改，让受害者误以为是简历文件，点击后将触发漏洞。

![](https://image.3001.net/images/20230804/1691117712_64cc68905601e54ea1a11.png!small)

图：伪装成简历的恶意Contact文件

### 利用可行性

相比用户点击触发，该方式最大的问题其实是默认打开程序限制：当打开.contact的默认程序不为Windows
Contact程序时，文件会被显示为空白图标，并且触发漏洞时，还会丢失文件的运行目录，导致无法打开相对路径下的文件。下图中，利用远程共享文件的方式解决了相对路径读取问题，并且通过
jar文件，绕过远程可执行文件的异常弹框告警问题。

![](https://image.3001.net/images/20230804/1691117747_64cc68b3564e73780be41.png!small)

图：通过远程共享文件的形式打开Contact

除了使用上面的方式，还可以利用Word
文档和LDAP协议远程加载构造好的恶意payload，能实现的效果如图：当打开Word文档时，自动打开恶意Contact文件，这种方式可以解决非默认打开方式时的图标显示和路径读取问题。

![](https://image.3001.net/images/20230804/1691117772_64cc68cc88bc3af5c70dc.png!small)

图：利用Word 文档和LDAP协议远程加载Contact

![](https://image.3001.net/images/20230804/1691117790_64cc68dec36e1065bc216.png!small)

图：LDAP服务端构造的恶意代码

## 0x04 攻击验证

绿盟一体化终端安全管理系统（UES）通过对系统行为的实时监控和深度分析，能够精确识别出与CVE-2022-44666漏洞相关的异常行为模式。一旦发现有可疑的漏洞利用行为，UES将第一时间发出警报，并提供相应的处置措施，帮助管理员及时做出反应并采取必要的防护措施。

![](https://image.3001.net/images/20230804/1691117825_64cc6901381f93512ecd2.png!small)

![](https://image.3001.net/images/20230804/1691117834_64cc690a3fec5f148f15e.png!small)

## 参考文献

https://www.zerodayinitiative.com/advisories/ZDI-19-121/

https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-44666

[https://github.com/j00sean/CVE-2022-44666﻿](https://github.com/j00sean/CVE-2022-44666)

