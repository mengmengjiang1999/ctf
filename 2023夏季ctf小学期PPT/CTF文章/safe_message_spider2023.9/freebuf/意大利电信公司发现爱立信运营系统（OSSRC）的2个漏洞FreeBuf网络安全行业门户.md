意大利电信公司TIM的漏洞研究部门Red Team Research (RTR) 发现了2个影响爱立信 OSS-RC 的新漏洞。TIM
RTR已向爱立信报告了这些漏洞。

据悉，这2个漏洞均存在 18B 及更早版本的 OSS-RC 系统中，升级后的系统使用新的爱立信库浏览工具 ELEX可以规避掉类似漏洞。

让我们来看看当一条新电话线被激活时客户端的情况：CRM系统收到了用户请求数据，OSS进行自动化的网络配置，允许电信运营商自动执行此过程并执行网络管理操作如更新城市建筑物上的基带系统。

![](https://image.3001.net/images/20211027/1635333299_617934b3674697c0f7dec.png!small)

运营支持系统 - 无线电核心 (OSS-RC)
为无线电和核心组件提供了一个集中接口，网络通信集成服务提供商可以通过这一接口访问所有的系统。不幸的是，OSS系统也代表了“单点故障”，意味着OSS的远程代码执行（RCE）漏洞可能允许攻击者危及包括基带在内的所有连接系统。

TIM作为领先的零日漏洞研究公司，过去两年，TIM RTR实验室发现了60多个零日漏洞，其中4个漏洞CSSV 得分为
9.8。自2001年以来向供应商报告的漏洞清单中，被列入美国国家漏洞数据库的数量有10个，TIM报道了其中2个。

![](https://image.3001.net/images/20211027/1635333385_617935094be098ad9ac45.png!small)

 **以下是TIM RTR项目官网发布的2个漏洞信息：**

 **CVE-2021-32569**

在 18B 及更早版本的 OSS-RC 系统中，在ALEX 下浏览库会受到跨站脚本的约束，在爱立信网络管理器（OSS-RC客户升级到的新一代OSS系统）等系统中使用新的爱立信库浏览工具 ELEX可以规避掉这一问题。

漏洞描述: Improper Neutralization of Input During Web Page Generation (‘Reflected
Cross-site Scripting’). – CWE-79 Software Version: <=18B NIST:
https://nvd.nist.gov/vuln/detail/CVE-2021-32569 CVSv3: 6.1 Severity: Medium
Credits: Alessandro Bosco, Mohamed Amine Ouad, Massimiliano Brolli

 **CVE-2021-32571**

在 18B 及更早版本的 OSS-RC 系统，包含用户名及密码的文件并未随着数据迁移得到清理，而是被遗留在仅限顶级特权账户访问的文件夹中。

漏洞描述: Incomplete Cleanup. – CWE-459 Software Version: <=18B NIST:
https://nvd.nist.gov/vuln/detail/CVE-2021-32571 CVSv3: 4.9 Severity: Medium
Credits: Alessandro Bosco, Mohamed Amine Ouad, Massimiliano Brolli

在这一历史时期，对漏洞挖掘者进行道德规范显得特别重要。例如要求正义黑客一旦发现没有记录的漏洞，必须立即报告给供应商，以免对公共信息系统造成威胁。

参考来源：https://securityaffairs.co/wordpress/123764/security/ericsson-oss-rc-flaws.html

