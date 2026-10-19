![72.jpg](https://image.3001.net/images/20200417/1587092144_5e991ab0ea69f.jpg!small)  

**台湾合勤和利凌物联网设备漏洞正被利用**

安全研究人员报告，台湾合勤（Zyxel）和利凌（LILIN）所生产 DVR 设备的高危漏洞正被攻击者利用去组建僵尸网络发动分布式拒绝服务攻击。奇虎 360
的[研究人员称](https://blog.netlab.360.com/multiple-botnets-are-spreading-using-lilin-dvr-0-day/)，从 2019 年 8 月 30 日起，多个攻击团伙使用 LILIN DVR 0-day 漏洞传播
Chalubo，FBot，Moobot 僵尸网络。LILIN 0-day 漏洞主要包括：硬编码登陆账号密码，命令注入漏洞和任意文件读取漏洞。奇虎在 2020
年 1 月 19 日联络了 LILIN，2 月 13 日 LILIN 释出了新版固件修复了漏洞。Palo Alto Networks
的研究人员[报告](https://unit42.paloaltonetworks.com/new-mirai-variant-mukashi/)合勤
NAS 设备预认证命令注入漏洞被利用安装 Mirai 变种 Mukashi。合勤的漏洞非常容易利用，其漏洞安全评分为 9.8/10。

详文阅读：

<https://www.solidot.org/story?sid=63903>

**加密漏洞允许黑客克隆丰田现代起亚的汽车遥控钥匙**

比利时鲁汶大学和英国伯明翰大学的研究人员在汽车防盗控制器使用的加密系统中[发现了漏洞](https://arstechnica.com/cars/2020/03/hackers-can-clone-millions-of-toyota-hyundai-and-kia-keys/)。确切的说，研究人员是在丰田、现代和起亚实现的德州仪器加密系统 DST80 中发现了漏洞。黑客利用廉价的 Proxmark RFID
发射机在使用 DST80 的遥控钥匙附近可以收集到足够的信息去推断其密值，克隆遥控钥匙，关闭防盗系统启动汽车引擎。受影响的汽车型号包括丰田凯美瑞、花冠和
RAV4；起亚远舰、秀尔和锐欧；以及现代 I10、I20 和 I40。特斯拉 Tesla S
汽车也受到影响，研究人员在报告之后特斯拉已经释出了固件更新修复了漏洞。

详文阅读：

<https://www.solidot.org/story?sid=63750>

**Mukashi** **：新Mirai变种攻击Zyxel NAS设备**

上个月CVE-2020-9054漏洞PoC公布后，就被滥用来感染有漏洞的Zyxel
NAS设备，被感染的设备成为Mirai变种Mukashi僵尸网络的一部分。

Mukashi 回实用不同的默认凭证在暴露破解登陆口令，成功登陆后会通知C2服务器。固件版本低于5.21的Zyxel
NAS设备都受到预认证命令注入漏洞的影响。该漏洞CVSS v3.1评分为9.8，因为攻击者很快就武器化该漏洞来攻击IoT设备。

 **漏洞分析**

可执行文件weblogin.cgi在认证过程中没有正确地处理用户名参数，攻击者用单引号‘来结束字符串和分号；来连接任意命令来实现命令注入。因为weblogin.cgi接收HTTP
GET和POST请求，攻击者可以在HTTP请求中嵌入恶意payload来获取代码执行。

详文阅读：

<https://www.4hou.com/posts/pX4N>

**史上最强大的僵尸网络Dark_nexus横空出世**

网络安全公司 Bitdefender表示发现了让其它僵尸网络如 Mirai 和 Qbot “相形见绌”的新型僵尸网络
“dark_nexus”。它具有的特征和能力是当前僵尸网络无法比拟的。

僵尸网络是由已受陷且被奴役至主控制器的机器、物联网产品和移动设备组成的网络。这些设备可被用于执行 DDoS 攻击、发动大规模的垃圾邮件活动等。

Dark_nexus 的命名源自其横幅上打印的字符串，它虽然同时具有Mirai 和 Qbot 的冷链接，但研究团队表示其主要功能是原创的。

研究人员指出，“虽然它和此前已知的物联网僵尸网络存在相似之处，但其某些模块助其更强大更健壮。”

Dark_nexus
已出现三个月，在此期间已发布三个版本。蜜罐显示至少有1372个僵尸连接到该僵尸网络，主要的僵尸位于中国、韩国、泰国和巴西。为了攻陷发现的机器，Dark_nexus
将使用凭证填充和 exploit。它使用了同步和异步两种模块，不过它们都尝试使用 Telnet
协议以及预定义的凭证列表获取访问权限。研究人员指出，“和其它广为传播的僵尸网络使用的扫描器非常相似，该扫描器被当作建模 Telnet
协议和随后感染步骤的有限状态机实现，在感染过程中，攻击者基于此前的命令输出发出适应性命令。”

详文阅读：

<https://www.secrss.com/articles/18506>

**CVE-2020-10882: TP-Link 命令注入漏洞通告**

监测发现 ZDI 于 04月07日公开了其在Pwn2Own Tokyo竞赛中使用的一枚 TP-Link
的命令注入漏洞的技术细节。该漏洞的漏洞编号为CVE-2020-10882。

TP-Link（中文全称：普联技术有限公司）是专注于路由器设备生产的一家公司。

建议广大用户及时更新TP-Link设备固件。做好资产 自查/自检/预防 工作，以免遭受攻击。

详文阅读：

<https://cert.360.cn/warning/detail?id=ea0df6b0ad71ae8540e9582ff74b7a60>

