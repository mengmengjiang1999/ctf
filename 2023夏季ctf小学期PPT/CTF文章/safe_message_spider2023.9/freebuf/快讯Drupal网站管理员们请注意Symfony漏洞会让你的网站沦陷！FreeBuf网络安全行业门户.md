***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **各位Drupal网站的管理员们请注意，请赶紧更新你们的Drupal版本。**

![a1.png](https://image.3001.net/images/20180810/1533878556_5b6d211cb8f4e.png!small)

**Drupal是一款开源的内容管理系统，Drupal项目组目前已经发布了一个更新补丁来修复其软件中的一个安全绕过漏洞，而这个漏洞将允许远程攻击者拿到目标站点的完整控制权。**

这个漏洞编号为CVE-2018-14773，该漏洞存在于Drupal框架的第三方组件代码库中，这个组件名叫Symfony
HttpFoundation，目前主要使用在Drupal Core之中，版本号在8.5.6之前的Drupal 8.x版本都会受到该漏洞的影响。

由于Symfony这款Web应用程序框架拥有多个PHP组件，它目前也应用到了很多开源项目之中，因此这个漏洞的出现也会导致很多其他的Web应用程序处于安全风险之中。

## Symfony组件漏洞

根据Symfony发布的安全公告，这个安全绕过漏洞之所以会存在，主要是因为Symfony的某些遗留功能以及不安全的HTTP头所导致的。Symfony组件支持ISS头，而这种功能将允许用户通过X-Original-URL或X-Rewrite-URL
HTTP请求头重写请求URL中的路径，并绕过Symfony的请求路径限制，从而访问到目标Web服务器中的缓存数据。

远程攻击者可以手动指定'X-Original-URL'或'X-Rewrite-URL'
HTTP头的值，并修改请求URL中的路径，从而绕过目标Web服务器的访问限制，并让目标系统呈现不同的URL地址。

目前为止，Symfony的2.7.49, 2.8.44, 3.3.18,
3.4.14,4.0.14和4.1.3版本都已经成功修复了该漏洞，而Drupal也已经在其最新版本8.5.6中修复了这个问题。

![a2.png](https://image.3001.net/images/20180810/1533878575_5b6d212f09680.png!small)

## Zend框架同样存在这个漏洞

除了Symfony之外，Drupal段对还在[Zend
Feed](https://framework.zend.com/security/advisory/ZF2018-01)和Diactoros代码库中发现了相同的安全漏洞，他们还将这个漏洞命名为了“URL重写漏洞”。

不过，虽然目前的Drupal Core并没有使用到存在安全漏洞的功能，但是他们仍建议广大用户尽快更新自己的Drupal版本，如果网站直接使用到了Zend
Feed或Diactoros模块，那就请不要犹豫，现在立刻马上更新Drupal！

## 后话

Drupal目前驱动着全球范围内的数百万个网站，但不幸的是，自从一个高危的远程代码执行漏洞（[Drupalgeddon2](https://thehackernews.com/2018/04/drupal-rce-exploit-code.html)）被发现之后，这些CMS网站一直都在经受着网络攻击者的[频繁攻击](https://thehackernews.com/2018/04/drupal-vulnerability-exploit.html)。因此，在攻击者开始利用这个新型漏洞来攻击你的Drupal网站之前，请尽快更新自己的站点。

 *** 参考来源：[thehackernews](https://thehackernews.com/2018/08/symfony-drupal-hack.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

