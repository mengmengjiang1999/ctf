**你近期是否购买了一加6手机，或正计划购买一部呢？看完这篇报告性的文章，你可能会望而却步。因为，最近安全研究人员披露在OnePlus 6
bootloader中，存在严重的安全漏洞，即使bootloader被锁定，也可以由他人启动任意或修改过的images，并最终完全控制你的手机。**

**![123.png](https://image.3001.net/images/20180612/15287824345455.png!small)**

引导加载程序（
bootloader）是手机内置固件的一部分，将其锁定可以阻止用户使用任何未经认证的第三方ROM，来更换或修改手机的操作系统，从而确保系统引导至正确的操作系统。

[Edge
Security](https://twitter.com/EdgeSecurity/status/1005461966863917056)的安全研究员Jason
Donenfeld发现，OnePlus 6上的引导加载程序竟然未被完全的锁定，这意味着任何人都可以将任何修改过的image刷入手机上并完全控制手机。

在视频中Donenfeld展示了攻击者是如果通过物理访问设备，使用ADB工具的fastboot命令启动被修改的恶意image，并最终完全控制受害者设备的过程。

## 视频演示

##

正如你在视频中看到的那样，攻击者甚至不需要开启USB调试模式，只需将受害者的OnePlus
6通过数据线插入其计算，重启手机进入Fastboot模式，然后通过修改后的启动映像进行传输即可。

以上步骤仅需短短的几分钟就能完成。因此，为了你的手机的安全，这里建议大家不要让你的手机轻易的离开你的视线，或交由他人和陌生人保管。

***参考来源：[thehackernews](https://thehackernews.com/2018/06/oneplus6-bootloader-root.html)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

