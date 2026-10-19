在苹果和谷歌推送紧急安全更新之后的第二天，微软亦推送了9月的“星期二补丁”，用以修复威胁window及组件的66处漏洞，包括Azure, Office,
BitLocker, and Visual Studio等，其中包括一个于上周曝光的 MSHTML 平台中积极利用零日漏洞。

在这66个漏洞中，3个被评为“critical”（关键）、1
个被评为“moderate”（中等），其余均被评为“important”（重要）。这些不包括该公司自本月初以来解决的基于 Chromium 的
Microsoft Edge 浏览器中的20个漏洞。

最重要的更新涉及[CVE-2021-40444](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-40444)（CVSS 评分：8.8）的补丁，这是 MSHTML
中一个积极利用的远程代码执行漏洞，它利用带有恶意软件的 Microsoft Office 文档，EXPMON
研究人员指出“该漏洞利用逻辑缺陷，所以这种利用是完全可靠的。”

此外还解决了 Windows DNS
中公开披露但未被积极利用的权限提升漏洞——[CVE-2021-36968](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-36968)，严重性等级为 7.8。

其它解决的值得注意的漏洞包括开放管理基础设施 ( [CVE-2021-38647](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-38647))、Windows WLAN 自动配置服务 (
[CVE-2021-36965](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-36965))、Office (
[CVE-2021-38659](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-38659))、Visual Studio 中的许多远程代码执行错误(
[CVE-2021-36952](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-36952)) 和 Word (
[CVE-2021-38656](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-38656)) 以及 Windows 脚本引擎中的内存损坏缺陷 (
[CVE-2021-26435](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-26435))。

更重要的是，Windows 制造商已经[修复](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-38667)了其 Print Spooler
服务中新发现的三个提权漏洞（[CVE-2021-38667](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-38667)、[CVE-2021-38671](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-38671)和[CVE-2021-40447](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-40447)），而[CVE-2021-369021](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-36975)和[CVE-](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-38639)[2021-369021
](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-36975)[-38639](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-38639)（CVSS 分数：7.8）都与 Win32k
中的权限提升漏洞有关，被列为“更有可能被利用”，因此用户必须迅速采取行动进行安全更新。

