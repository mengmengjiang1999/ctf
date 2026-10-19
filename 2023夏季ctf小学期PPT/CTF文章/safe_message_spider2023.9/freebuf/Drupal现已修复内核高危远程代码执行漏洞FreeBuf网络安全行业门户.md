***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![drupal_logo.png](https://image.3001.net/images/20180329/15223025484499.png!small)  

**Drupal CMS团队修复了一个重要安全漏洞，黑客可以通过访问URL接管网站。**

Drupal站长们应该立即更新到Drupal 7.58或Drupal 8.5.1。

Drupal团队上周早些时候预告了今天的补丁，当时它表示“在今天披露后黑客可能会在数小时或数天内开发出exp”。

安全漏洞确实非常严重，Drupal团队将严重程度分数设置为21（区间从1到25分）。

## 未经身份验证远程执行

漏洞编号为CVE-2018-7600，能让攻击者运行CMS核心组件的任何代码，从而接管站点。

攻击者无需在目标站点上进行注册或验证，只需要访问URL。

Drupal社区在2014年爆出过Drupalgeddon安全漏洞（CVE-2014-3704，SQL注入，严重性25/25）现在的漏洞被称为Drupalgeddon2。

![dd.png](https://image.3001.net/images/20180329/15223025125630.png!small)  

## 没有公开的PoC

目前没有公开的PoC或exp代码，但研究人员已经开始通过Drupal补丁进行寻找相关漏洞。

Drupal开发人员称，Drupal安全审计公司Druid的员工Jasper Mattsson发现了这个漏洞。

研究人员反复强调补丁的重要性，即便是Drupal主页今天也下线半小时用于修复补丁。

## EOLed Drupal 6也受到影响

除了修复Drupal的两个主要分支7.x和8.x之外，Drupal团队还公布了2016年2月中止更新的6.x分支的补丁。

根据BuiltWith.com的统计，Drupal目前拥有超过100万个网站，并在1万个最受欢迎的网站中拥有9％的市场份额。

## 骂战指引

如果你是WordPress站长，想嘲笑Drupal千疮百孔的网站，可以在Twitter上搜索标签#Drupalgeddon2加入骂战。

 ***
参考来源：[BleepingComputer](https://www.bleepingcomputer.com/news/security/drupal-fixes-drupalgeddon2-security-flaw-that-allows-hackers-to-take-over-sites/)，作者Sphinx，转载注明来自Freebuf.COM**  

