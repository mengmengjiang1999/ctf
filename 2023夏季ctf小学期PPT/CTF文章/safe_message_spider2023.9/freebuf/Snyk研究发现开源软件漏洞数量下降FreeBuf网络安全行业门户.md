**Snyk 针对开源软件中漏洞的研究报告显示，发现新漏洞的数量下降了五分之一。**

Snyk 是专门发现和修复开源代码中漏洞的工具，其近日的[研究显示](https://www.prnewswire.com/news-releases/snyk-state-of-open-source-security-report-reveals-vulnerabilities-down-as-cybersecurity-responsibilities-are-more-effectively-shared-across-teams-301083314.html)在开源软件中发现的新漏洞数量同比下降了 20%，但被发现的漏洞大都很严重。

Synk 的程序安全推动者 Alyssa Miller 表示，随着[程序开发者对安全的意识日益增加](https://devops.com/what-is-devsecops-and-how-to-enable-it-on-your-sdlc/)，漏洞的数量也在逐渐下降。但同时，只要是人类写的代码，难免会存在安全问题。最新的研究显示，
**越来越多的开发人员将漏洞扫描工具内嵌在开发流程中** ，这样可以在代码进入生产环境前就发现其中的漏洞，开源软件的安全性有望继续改善。

![1.jpg](https://image.3001.net/images/20200628/1593351396_5ef89ce439d28.jpg!small)

Snyk 对五百名开发者、安全从业者和 IT 运营人员进行了调查，结合 Snyk
在开源软件中的扫描数据。发现当前影响最大的漏洞是原型污染，在所有接受调查的项目中有 27% 的项目被发现修改了 JavaScript 程序中的对象。

此外，XSS 等漏洞仍然在报告中大量出现，但 Snyk 认为实际上受此类漏洞影响的项目并不多。Miller 表示，
**相比于鲜为人知的漏洞，这些出名的漏洞似乎可以被更早的发现和修复** 。

该报告指出，发现的大多数漏洞都影响使用如 Node Package
Manager（86%）、Ruby（81%）、Java（74%）等构建程序的间接依赖关系，调查还发现有 60% 的组织没有完全厘清软件的依赖关系树。

调查发现 **有超过 30% 的人不检查 Kubernetes 清单中的不安全配置** 。不仅如此，Kubernetes
中与安全相关的资源控制也没有被广泛采纳。许多标记为 `final` 的容器镜像包含大量已知漏洞。

![2.png](https://image.3001.net/images/20200628/1593351425_5ef89d01bba0c.png!small)

调查发现有 57% 的受访者已经实施了静态代码分析工具（SAST），随后采用了安全测试用例的占 28%。

实施了动态程序安全测试（DAST）的占 20%、软件组成分析占 19%、威胁建模占 19%。

尽管开发过程中对安全工具的依赖程度相对较低，但随着 DevOps 和安全团队之间更加紧密的协作，越来越多的安全工具也会被集成到 DevOps
中，应用程序的安全性可以得到更好的保障。

## 参考来源

> [DevOps](https://devops.com/snyk-report-finds-decline-in-open-source-> vulnerabilities/)

