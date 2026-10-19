**![zBang
tool.png](https://image.3001.net/images/20190103/1546485172_5c2d7db48d813.png!small)**

**zBang是一个用于检测扫描网络中潜在特权帐户威胁的风险评估工具，组织或红队可利用zBang来识别潜在的攻击向量改善网络的安全状况，并可通过图形界面或查看原始输出文件来分析结果。**

关于zBang的更详细介绍，请参阅[@Hechtov](https://twitter.com/Hechtov)的博文：<https://www.cyberark.com/threat-research-blog/the-big-zbang-theory-a-new-open-source-tool/>

 **该工具由五个不同的扫描模块构建：**

>  **ACLight scan** \- 发现必须受保护的最高权限帐户，包括可疑的Shadow Admins。
>
>  **Skeleton Key scan** \- 发现可能被Skeleton Key恶意软件感染的域控制器。
>
>  **SID History scan** \- 使用secondary SID（SID历史记录属性）发现域帐户中的隐藏权限。
>
>  **RiskySPNs scan** \- 发现可能导致域管理员凭据窃取的SPN风险配置。
>
>  **Mystique scan** \- 发现网络中有风险的Kerberos委派配置。

## 执行要求

> 与域用户一起运行它。扫描不需要任何额外的权限；该工具对DC执行只读LDAP查询。
>
> 从已加入域的计算机（Windows计算机）运行该工具。
>
> PowerShell version 3或更高版本，以及.NET 4.5（默认情况下在Windows 8/2012及更高版本中提供）。

## 快速入门指南

1\. 从GitHub下载并运行最新版或使用你喜欢的编译器进行编译。

2\. 在打开的界面中，选择你要执行的扫描。在以下示例中，选中了所有五个扫描模块：

![opening
menu.png](https://image.3001.net/images/20190103/1546485199_5c2d7dcfa48c7.png!small)

3\. 要查看演示结果，请单击“Reload”。zBang工具带有内置的启动演示数据；你可以查看不同扫描的结果并使用图形界面进行播放。

4\. 要在网络中启动新扫描，请单击“Launch”。这将弹出一个新窗口，并显示不同扫描的状态。

![aclight.png](https://image.3001.net/images/20190103/1546485228_5c2d7dec137d0.png!small)

5\. 扫描完成后，将显示一条消息说明结果已导出到外部zip文件。

![zbang
finished.png](https://image.3001.net/images/20190103/1546485247_5c2d7dffebc7f.png!small)

6\. zip文件位于zBang的同一文件夹中，并且具有唯一的名称，其中包含扫描的时间和日期。你还可以将先前的结果导入zBang
GUI，而无需重新运行扫描。要导入先前的结果，请在zBang的打开界面中单击“Import”。

## zBang结果浏览

### A. ACLight scan

![aclight
result.png](https://image.3001.net/images/20190103/1546485287_5c2d7e27e53b5.png!small)

1\. 选择你扫描的域。

2\. 你将看到一个已发现的最高权限帐户的列表。

3\. 在左侧 - 查看“standard”标准权限帐户由于其组成员身份而获得的权限。

4\. 在右侧 - 查看“Shadow
Admins”这些帐户通过直接ACL权限分配获得其权限。这些帐户可能比标准的“域管理员”用户更隐蔽，因此它们并不安全并常常成为攻击者的首要目标。

5\. 在每个帐户上，你可以双击查看其权限拓扑图。

![aclight
tree.png](https://image.3001.net/images/20190103/1546485313_5c2d7e41d6985.png!small)

6\. 在一个帮助页面中描述了不同的可滥用ACL权限。点击右上角的“问号”查看：

![risky
ACLs.png](https://image.3001.net/images/20190103/1546485335_5c2d7e573015a.png!small)

7\. 更多有关Shadow Admins的内容，请参阅博文：<https://www.cyberark.com/threat-research-blog/shadow-admins-stealthy-accounts-fear/>

8\. 如要手动检查扫描结果，请解压缩已保存的zip文件并检查results文件夹：“[zip文件保存路径]\ACLight-master\Results”，包含摘要报告 -“特权帐户 - Layers Analysis.txt”。

9\. 在每个发现的特权帐户上：

> 识别特权帐户。
>
> 减少帐户的不必要权限。
>
> 确保帐户安全。验证这三个步骤后，你可以在小选择框中用“V”标记该帐户，并在界面上将其设置为绿色。

10\. 我们的目标是让所有的帐户都被标记为安全的绿色。

### B. Skeleton Key scan

1\. 在扫描页面中（单击上一部分中的相关书签），将显示所有已扫描的DC列表。

2\. 确保所有这些都被标为绿色。

3\. 如果扫描发现潜在的受感染DC，启动调查进程至关重要。

![skeleton
key.png](https://image.3001.net/images/20190103/1546485383_5c2d7e878cbdd.png!small)

4.有关Skeleton Key恶意软件的详细信息，请参阅@PyroTek3的博文：<https://adsecurity.org/?p=1255>

### C. SID History scan

1\. 在该扫描页面中，将有一个具有secondary SID（SID历史记录属性）的域帐户列表。  
2\. 每个帐户都有两个连接箭头，左边一个用于其主SID；另一个则用于其secondary SID（带有面具图标）。  
3\. 如果主SID具有特权，则它将为红色，如果SID历史记录具有特权，则将显示为红色面具。  
4\. 你应该搜索可能存在风险的情况，例如帐户具有非特权主SID，但同时具有特权secondary
SID。这就需要注意了，你应该检查该帐户并调查它具有特权secondary SID的原因，以确保网络中的潜在入侵者没有添加它。

![SIDhistory.png](https://image.3001.net/images/20190103/1546485410_5c2d7ea216a76.png!small)

*为了方便可视化，如果存在大量具有非特权SID历史记录的帐户（超过十个），它们将会被从显示中过滤掉，因为这些帐户并不那么敏感。

5\.
如要手动检查扫描结果，请解压缩已保存的zip文件并检查csv文件："[zip文件保存路径]\SIDHistory\Results\Report.csv"。

6\. 有关滥用SID History的更多信息，请参阅Ian
Farr的博文：<https://blogs.technet.microsoft.com/poshchap/2015/12/04/security-focus-sidhistory-sid-filtering-sanity-check-part-1-aka-post-100/>

### D. RiskySPNs scan

1\. 在扫描结果页面中，将显示所有使用用户帐户注册的SPN列表。

2\. 如果用户帐户是特权帐户，则该帐户将显示为红色。

3\.
拥有在特权帐户下注册的SPN是非常危险的。尝试更改/禁用这些SPN。为SPN使用计算机帐户或减少已向其注册了SPN的用户的不必要权限。另外，建议为这些用户分配强密码，并实现每个密码的自动轮换。

![riskySPNs.png](https://image.3001.net/images/20190103/1546485438_5c2d7ebe61d1e.png!small)

4\. 如要手动检查扫描结果，请解压缩已保存的zip文件并检查csv文件："[zip文件保存路径]\RiskySPN-master\Results\RiskySPNs-test.csv"。

5\. 有关SPN安全的更多信息，请参阅博文：<https://www.cyberark.com/blog/service-accounts-weakest-link-chain/>

### E. Mystique scan

1\. 扫描结果页面包含受委派权限信任的所有已发现帐户的列表。

2\. 有三种委派类型：无约束，约束和约束协议转换。帐户颜色对应于其委派权限类型。

3\.
禁用受委派权限信任的旧帐户和未使用帐户。特别是检查“无约束”和“约束协议转换”的风险委派类型。将“无约束”委派转换为“约束”委派，仅允许用于特定的所需服务。如果可能，必须重新验证和禁用“协议转换”类型的委派。

![mystique.png](https://image.3001.net/images/20190103/1546485457_5c2d7ed141387.png!small)

4\. 如要手动检查扫描结果，请解压缩已保存的zip文件并检查csv文件："[zip文件保存路径]\Mystique-master\Results\delegation_info.csv"。

5\. 有关风险委派配置的更多信息，请参阅博文：<https://www.cyberark.com/threat-research-blog/weakness-within-kerberos-delegation/>

***参考来源：[GitHub](https://github.com/cyberark/zBang)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

