威胁行为者正在利用CVE-2020-14882超危漏洞攻击未修复的Oracle WebLogic Server，部署Cobalt
Strike信标，以此在遭受入侵的设备上获取持续性远程访问权限。

Cobalt
Strike是一款合法的渗透测试工具，但该工具同样可以被威胁行为者使用。他们在后漏洞利用任务中利用该工具部署可以让他们获取持续性远程访问权限的信标。

获得访问权限后，威胁行为者可以访问所入侵的服务器，窃取数据，以及部署第二阶段的恶意软件payloads。

Oracle在10月份的关键补丁更新中修复了CVE-2020-14882远程执行代码漏洞。该补丁发布一周后，攻击者已在扫描查找暴露在互联网上的WebLogic
Server。

11月1日，Oracle发布了一则紧急安全更新，修复另一个影响WebLogic
Server的远程执行代码漏洞CVE-2020-14750。未经身份验证的远程攻击者可利用该漏洞接管未修复的实例。

11月3日，美国SANS技术研究所表示，针对脆弱的WebLogic实例的最新系列攻击开始于上周末。

攻击者正在利用base64编码的Powershell脚本在未修复的Oracle WebLogic Server上下载和安装Cobalt Strike
payloads。

![1604988250_5faa2d5a2b08f5a2b4523.png!small](https://image.3001.net/images/20201110/1604988250_5faa2d5a2b08f5a2b4523.png!small)

Cobalt Strike部署

有分析报告指出，2020年第三季度66%的勒索软件攻击都涉及红队工具Cobalt Strike，这表明随着勒索软件行为者弃用商业木马后，越来越依赖该工具。

网络安全公司Spyse发现超过3300个受到CVE-2020-14882影响Oracle WebLogic Server暴露在线。

鉴于CVE-2020-14882和CVE-2020-14750的利用难度低，可被未经身份验证的攻击者用于接管脆弱的WebLogic
Server，厂商已建议用户立即应用安全更新，阻止攻击。

