Microsoft Exchange Online存在一个远程代码执行（RCE）漏洞，研究人员接连两次绕过了该漏洞的补丁，目前，该漏洞仍未得到修复。

该0-day漏洞影响多个软件即服务（SaaS）提供商，以及Exchange Server的本地安装。

Exchange Online是Microsoft Office 365套件的组成部分。安全研究人员Steven Seeley
1月12日发表了一篇博客文章，指出Exchange Online中的该漏洞可被用于访问无数的企业邮件账户。

随着对云部署的需求越来越普遍，Office 365的用户群也在迅速增长，到2019年底，活跃用户已达到2亿。

Seeley称，考虑到Microsoft Exchange
Server在过去两年中出现了六个RCE漏洞，尤其是CVE-2020-0688和CVE-2019-1373，激发他探查环境，寻找RCE漏洞。CVE-2019-1373促使他专注于powershell远程处理接口。

Seeley表示，这些漏洞都需要身份验证，但这并没有降低严重程度，“因为攻击者可以轻松创建恶意租户，并应用必要的权限。”——这是基于云计算的环境与本地环境之间的一个“基本”但常常被“忽略”的区别。

Microsoft将初始漏洞（CVE-2020-16875）评为高危漏洞（CVSS 8.4），但将其攻击复杂度标记为低。

根据Microsoft的安全公告，该漏洞存在于New-DlpPolicy cmdlet中，源于在创建DLP策略时，对用户提交的模板数据验证不当。

Seeley通过ecp和powershell接口两次触发了该漏洞。

令他吃惊的是，攻击outlook.office365.com和outlook.office.com服务器证明，他可以“在Microsoft的云上以系统权限执行命令，并通过http窃取敏感数据而不被捕获”。

要绕过Microsoft的第一个补丁有两种方法，Microsoft对该补丁绕过分配了编号CVE-2020-17132（CVSS 9.1）。

Seeley，使用‘&’符号调用powershell
cmdlet，借助powershell调用运算符，绕过了该补丁。该补丁修复了DlpPolicyTemplateMetaData.ValidateCmdletParameters中的漏洞。

另一组研究人员Leonard Rapp、Markus Vervier和Yasar
Klawohn独立发现，该补丁无法阻止在powershell控制台中执行内联代码。

“在循环通过cmdlet列表之后”，Seeley随后使用调用运算符绕过了第二个补丁，该运算符绕过了RestrictedLanguage模式的runspace，并完成了通过调用CmdletValidator.ValidateCmdlet执行的用来阻止攻击的六个检查。

Microsoft对Seeley在其在线服务奖励计划下的发现给予了“丰厚”的奖励，该计划为严重的RCE漏洞支付最高2万美元赏金。

该研究人员在2020年5月22日向Microsoft发送了他的初始报告，后者在9月8日发布了一则安全公告。

Seeley在12月9日向Microsoft报告再次绕过漏洞补丁，Microsoft在此前一天发布了月度补丁更新。Seeley警告称，由于最终的补丁尚未落地，该攻击仍无缓解措施。

该研究人员认为，依赖具有单点故障系统的云提供商不是正确的方法。

明智的做法是重新评估威胁形势。使用相对较新的技术，攻击者可能拥有比最初想象的更多的访问权限。

Seeley表示，.net中所有的代码执行漏洞并非都与反序列化相关。研究人员很容易受困于视野狭小，他建议研究人员不要‘随大流’。

作者：Adam Bannister  
来源：Port Swigger

