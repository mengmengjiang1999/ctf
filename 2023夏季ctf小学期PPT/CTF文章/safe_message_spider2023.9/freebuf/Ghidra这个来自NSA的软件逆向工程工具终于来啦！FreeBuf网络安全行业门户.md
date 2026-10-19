![1.png](https://image.3001.net/images/20190312/1552327280_5c86a270982f1.png!small)

**是的，大家没有看错！Ghidra完全出自[NSA](https://www.nsa.gov/)之手，它是一款软件逆向工程（SRE）框架，由美国国家安全局研究理事会负责开发、升级和维护。这款框架包含了一整套功能齐全的高级软件分析工具，可以帮助广大研究人员在各种常见系统平台上进行源代码分析，其中包括Windows、macOS和Linux。**

## Ghidra项目（下载）地址

> GitHub代码库：<https://github.com/NationalSecurityAgency/ghidra>
>
> Ghidra官方网站：<http://ghidra-sre.org/>
>
> 工具下载：<https://pan.baidu.com/s/1pQ2WhjnfVK9OgfIf6eucpg> 提取码: hn5s（解压密码：123）

![2.png](https://image.3001.net/images/20190312/1552327312_5c86a290dda5a.png!small)

Ghidra的功能非常强大，它不仅能够帮助用户对软件进行反编译、编译和逆向分析，而且还可以让网络安全研究人员更好地了解其网络和系统中存在的潜在漏洞。更值得一提的是，除了这些功能之外，Ghidra还包含了上百种其他的分析功能，可以算是非常强大了，不愧是出自NSA之手。

它提供了用户友好的图形化操作界面，而且支持多种处理器指令集以及可执行文件格式。除此之外，它还支持用户交互和自动化这两种模式。当然了，有些用户可能还需要根据自己的需要来开发Ghidra插件组件，Ghidra同样是支持的，用户可以使用Java或Python来开发自己需要的组件或脚本。

Ghidra旨在解决复杂的软件逆向工程任务，并为分析团队提供额外的功能扩展支持。

就在今年三月份举办的2019年RSA大会上，美国国家安全局首次公开介绍并演示了这款软件的使用，并且将Ghidra作为开源工具开放给了大众使用。

### Ghidra的主要特点

1、 提供了一整套软件分析工具，可在各种系统平台上进行代码分析，支持Windows、macOS和Linux；

2、 功能包括反汇编、汇编、反编译、图形化和脚本支持，以及数百个其他的高级功能；

3、 支持各种处理器指令集以及可执行文件格式，可以在用户交互或自动化模式下运行；

4、 用户可以使用开放的API接口开发自己的Ghidra插件组件或脚本；

![3.png](https://image.3001.net/images/20190312/1552327329_5c86a2a12bda8.png!small)

Ghidra采用Java语言开发，支持跨平台使用，适用于Windows、macOS和Linux，并且提供了友好的图形用户界面（GUI）。Ghidra还可以对主流操作系统的二进制文件进行分析，这里还包括了Android和iOS在内，支持分析的代码有x86、Arm、PowerPC、MIPS、Sparc32/64
和其它处理器代码。

## 工具演示视频

无法观看请[点此跳转](https://v.qq.com/x/page/u0848slqzvg.html)

### 后话

值得一提的是，美国国家安全局在21世纪初期就已经开发了Ghidra，而且在过去的十多年时间里，美国国家安全局以及其他的美国政府机构都一直在使用这款工具。不过，Ghidra的存在并不是严格意义上的国家机密，不过人们也只是在2017年初才知道这回事的。为什么呢？很多同学应该都记得吧？当时维基解密曾公布了著名的Vault7，泄露文档中就提到了这个名叫Ghidra的工具。

![4.png](https://image.3001.net/images/20190312/1552327357_5c86a2bd09c67.png!small)

泄密文档链接：<https://wikileaks.org/ciav7p1/cms/page_51183656.html>

值得一提的是，NSA对外声称（保证）他们并没有在开源的Ghidra代码中安插任何形式的后门，因为NSA表示他们希望通过Ghidra的开源来助力全球的网络安全研究工作。但实际上，也有研究人员认为这种行为/言论纯粹是“此地无银三百两”。

因为有一位研究人员@hackerfantastic就发现，Ghidra开启JDWP并以调试模式在监听端口18001时，将允许我们实现远程代码执行，而且这名研究人员还提供了漏洞的PoC截图，这就非常尴尬了。

![TIM截图20190312020319.jpg](https://image.3001.net/images/20190312/1552327418_5c86a2fa00cbd.jpg!small)

但是研究人员还表示，大家只需要修改一下代码就可以搞定了，而且他还强调称这只是一个漏洞，而不是NSA植入的后门。

***参考来源：[NSA](https://github.com/NationalSecurityAgency/ghidra)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

