**2020年初以来受COVID-2019的影响，人们的生活完全转移到了网上，世界各地的人们在网上工作、学习、购物和娱乐。近期DDoS攻击的目标也反映了这一点，第一季度针对性最强的目标是医疗组织、支付服务以及游戏和教育平台。**

## 事件总结

3月中旬，攻击者试图攻击瘫痪[美国卫生与公共服务部（HHS）网站](https://www.theregister.co.uk/2020/03/16/hhs_reports_cyberattack/)。攻击的目的是剥夺公民获取有关流行病以及应对措施的官方数据。同时利用社交网络、短信和电子邮件传播错误信息，但最终攻击失败，HHS网站仍继续运行。另一个DDoS受害者是巴黎的大型医院[AssistancePublique-Hôpitauxde Paris](https://www.tellerreport.com/tech/2020-03-23---hospital-systems-paris-inaccessible-for-hours-on-end-due-to-ddos-attack-.ByG627LILL.html)，攻击者试图破坏医疗机构的基础设施，导致医院工作人员一段时间内无法使用程序和电子邮件服务，但是攻击者未能使整个组织瘫痪。

送餐服务Lieferando（德国）和Thuisbezorgd（荷兰）两家公司也遭受DDoS攻击，他们可以接受订单但无法处理订单，网络犯罪分子要求2
BTC才能停止DDoS。德国远程学习平台Mebis在远程开学的第一天就遭到袭击，服务中断了几个小时。3月下旬，澳大利亚当局报告MyGov服务门户网站遭到DDoS攻击。

本季度还出现基于政治目的攻击。在一月下旬，攻击者曾两次试图关闭希腊政府机构和紧急服务网站。暂时离线的包括总理，部委，消防局和警察局的网站。土耳其组织[Anka
Neferler Tim](https://www.thenationalherald.com/282159/hack-attacks-on-official-websites-rattles-greece/)声称对此负责。今年将举行美国总统大选，选举将伴随着DDoS攻击。2月初[选民注册和信息网站](https://securityboulevard.com/2020/02/fbi-outlines-technique-behind-ddos-attacks-on-us-voter-registration-website/)遭到攻击。攻击者使用PRSD（伪随机子域攻击）技术将大量请求发送到不存在子域。

金融机构也没有幸免。
2月，加密货币交易所[OKEx和Bitfinex](https://thenextweb.com/hardfork/2020/02/28/bitfinex-cryptocurrency-okex-ddos-hacker-denial-of-service-blockchain/)遭到了复杂的DDoS攻击。前者在不损害用户权益的情况下处理了该事件，后者则被迫离线一个小时。BitMEX加密货币交易所在本季度受到至少两次攻击，这与比特币的价格急剧下降有关，一些人认为交易所[有意下线防止大量抛售](https://bitcoinist.com/bitmex-refunds-traders-after-recent-ddos-attacks/)。2月下旬，澳大利亚金融机构收到了要求使用门罗币支付的[勒索邮件](https://www.zdnet.com/article/australian-banks-targeted-by-ddos-extortionists/)。如果拒不付款，攻击者将对其进行DDoS攻击。此前，新加坡，土耳其，南非和其他国家的公司也收到了类似的电子邮件。

3月中旬，一名网络犯罪分子因攻击俄罗斯Cherepovets公司的在线商店而被拘留。尽管他掩盖了DDoS攻击源，但网警还是追踪到了他。

## 趋势分析

本季度主要以新冠病毒为主，与上一份报告的预测相反，在2020年第一季度DDoS攻击的数量和质量均显著增加。与上一季度相比攻击次数增加了一倍，与2019年第一季度相比攻击次数增加了80％。攻击时长变得更长，平均持续时间和最大持续时间均明显增加。

![](https://image.3001.net/images/20200511/1589180608_5eb8f8c070221.png!small)

![](https://image.3001.net/images/20200511/1589180623_5eb8f8cf0399c.png!small)

在总体增长的背景下，智能攻击（smart attacks）的份额几乎保持不变，2019年和2020年第一季度处于相同水平，约为42％。

![](https://image.3001.net/images/20200511/1589180699_5eb8f91bcbfab.png!small)

对教育和行政网站的DDoS攻击数量与2019年同期相比增加了两倍。此类攻击在2020年第一季度占总数的19％，一年前仅为11％。

许多公司组织都在转向远程工作，攻击者的目标数量正在增加。大多数情况下的目标是公共资源，现在许多关键的基础设施（如公司VPN网关或非公共Web资源）可能也会受到威胁。

## 数据分析

2020年第一季度，大多数C＆C服务器仍在美国（39.93％），大多数僵尸主机在巴西。

> 1、本季度2月14日和15日的攻击次数超过了230次，1月25日的攻击次数为16次。
>
> 2、攻击在星期一最活跃，在星期三处于休息状态。
>
> 3、SYN泛滥是使用最多的攻击类型，ICMP攻击第二。
>
> 4、Windows僵尸网络持占比续走高，攻击份额增加了3个百分点至5.64％。

### 地理分布

攻击源IP地理分布：

![](https://image.3001.net/images/20200511/1589181140_5eb8fad4b9dcd.png!small)

僵尸网络服务器地理分布：

![](https://image.3001.net/images/20200511/1589181175_5eb8faf791abe.png!small)

### 攻击频次

每日攻击频次走势：

![](https://image.3001.net/images/20200511/1589181225_5eb8fb2954db1.png!small)

在过去的一个季度中，星期一的攻击次数显著增加：

![](https://image.3001.net/images/20200511/1589181301_5eb8fb7528af7.png!small)

### 攻击种类

ICMP泛洪增加了2个百分点，升至第二名（3.6％，上一报告期为1.6％）。排名最高还是SYN泛洪，其份额持续增长，达到92.6％的历史新高（超过了上个季度创下的历史记录84.6％）。

![](https://image.3001.net/images/20200511/1589181467_5eb8fc1b4e59e.png!small)

Windows僵尸网络份额持续增长：

![](https://image.3001.net/images/20200511/1589181534_5eb8fc5e0cb56.png!small)

## 总结

2020年第一季C＆C服务器数量排名前10位的国家/地区出现了克罗地亚和新加坡，Windows僵尸网络和ICMP泛洪攻击有所增加，但并没有影响整体情况。在情人节DDoS攻击数量增加，随后回落。

 ***参考来源：[securelist](https://securelist.com/ddos-attacks-in-q1-2020/96837/)，由Kriston编译，转载请注明来自FreeBuf.COM**

