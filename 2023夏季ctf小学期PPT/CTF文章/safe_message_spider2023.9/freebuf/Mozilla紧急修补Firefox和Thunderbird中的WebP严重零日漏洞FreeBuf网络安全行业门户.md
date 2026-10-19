![](https://image.3001.net/images/20230913/1694571972_65011dc4369b766c5bd88.png!small)

Mozilla 周二发布了安全更新，修复了 Firefox 和 Thunderbird 中的一个关键零日漏洞。

该漏洞被标记为 CVE-2023-4863，是 WebP 图像格式中的堆缓冲区溢出漏洞，在处理特制图像时可能导致任意代码执行。

Mozilla 在一份公告中说，打开恶意 WebP 图像可能导致内容进程中的堆缓冲区溢出，这个漏洞在其他产品中被广泛利用。

根据国家漏洞数据库（NVD）的描述，该漏洞可能允许远程攻击者通过精心制作的 HTML 页面执行越界内存写入。

苹果公司安全工程与架构部（SEAR）和多伦多大学蒙克学院公民实验室报告了这一安全漏洞。该漏洞已在 Firefox 117.0.1、Firefox ESR
115.2.1、Firefox ESR 102.15.1、Thunderbird 102.15.1 和 Thunderbird 115.2.2 中得到修复。

在谷歌发布 Chrome 浏览器同一漏洞的修补程序后，第二天，谷歌也表示该漏洞在野外被积极利用。

上周，苹果也发布了补丁，以修复这两个被主动利用的安全漏洞。公民实验室称，这两个漏洞已被武器化，成为名为BLASTPASS的零点击iMessage漏洞链的一部分，可在运行iOS
16.6系统的打满补丁的iPhone上部署Pegasus间谍软件。

虽然有关漏洞利用的具体细节尚不清楚，但怀疑这些漏洞都被用来针对身份特殊的个人，如政治家和记者等。

> 参考链接：https://thehackernews.com/2023/09/mozilla-rushes-to-patch-webp-> critical.html

