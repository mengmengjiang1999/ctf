大量带有恶意附件的电子邮件发送到南美洲与欧洲的企业。从 2022 年 8 月 12
日开始针对西班牙、葡萄牙、罗马尼亚和南美洲多个国家的企业进行发送，后续针对德国与阿根廷的企业发起了更大规模的攻击，迄今为止已经发送了超过 26000
封邮件。

## 感染链

攻击者向大量的企业邮箱发送钓鱼邮件。电子邮件有一行文字：“Get Outlook for Android”，该文字会根据攻击目标的位置进行本地化。例如
.de 电子邮件地址的受害者会收到德语电子邮件。电子邮件的主题与附件也都是以不同的语言进行命名的，例如 `Draft Contract`。

![image.png-61.9kB](https://image.3001.net/images/20220827/1661602295_630a09f78eec508f0a40e.png!small)钓鱼邮件

附件通常是一个 .IMG 或者 .ISO 文件，附件中会包含一个 CHM 文件，名为“草稿合同”。打开该文件后，会弹出如下的窗口：

![image.png-41.5kB](https://image.3001.net/images/20220827/1661602296_630a09f84104c7fcb5e39.png!small)CHM
文件

该文件包含混淆的 JavaScript 代码，会启动如下所示的 PowerShell 命令来下载最终 Payload：

![image.png-93.1kB](https://image.3001.net/images/20220827/1661602296_630a09f8c5cbfdef88f01.png!small)PowerShell
代码

最终的 Payload 伪装成 JPG 文件从看起来合法的网站下载，这也是为了规避检测与分析。最终的 Payload 是一个 PowerShell
脚本，用于释放并运行 AgentTesla 恶意软件。

AgentTesla 是窃密软件，可以：

> 从浏览器、电子邮件客户端、VPN 客户端、FTP 客户端、剪贴板中窃取密码
>
> 获取用户按键记录
>
> 获取屏幕截图
>
> 窃取计算机相关信息
>
> 下载其他恶意软件

本次攻击行动的攻击者主要进行窃密，并且收集例如用户名、计算机名称、操作系统、CPU 和 RAM 等失陷主机相关信息。AgentTesla 伪装成
InstallUtil.exe 可执行文件中的注入代码，执行后会将收集的数据回传到攻击者的 FTP 服务器。

![image.png-32.8kB](https://image.3001.net/images/20220827/1661602297_630a09f98133b89d4be23.png!small)感染链

感染链如上所示，FTP 服务器未加密。所有攻击相关的内容都存储在 FTP 服务器上，其中包含大量的文件，攻击者大约每小时取走并删除这些文件一次。

![image.png-143.2kB](https://image.3001.net/images/20220827/1661602298_630a09fa1eadc46eba045.png!small)FTP
服务器

## 影响

攻击行动从 2022 年 8 月 12 日开始，针对南美洲国家、西班牙、葡萄牙和罗马尼亚进行大规模攻击，针对意大利和法国也有小范围攻击。

2022 年 8 月 16 日开始，针对德国的攻击持续了两天。2022 年 8 月 18
日，攻击阿根廷的企业只持续了几个小时。最后观察到的攻击是针对瑞士的，在 2022 年 8 月 23 日的早晨。

## IOC

> 83fe51953a0fe44389e197244faf90afe8ee80101dc33cb294cf6ef710e5aaba  
> 76f707afa3d4b2678aa5af270ea9325de6f8fdc4badf7249418e785438f1b8da  
> eb455ffb1595d1a06fc850ebc49b270ae84dd609e7b52144a60bb45cf4c4eb0e  
> ftp.akmokykla[.]lt  
> assltextile[.]com/Su34M.jpg  
> consult-mob[.]ro/M777.jpg  
> handcosalon[.]com/Su57.jpg

## 参考来源

> [Avast](https://decoded.avast.io/pavelnovak/agenttesla-is-threatening-> businesses-around-the-world-with-a-new-campaign/)

