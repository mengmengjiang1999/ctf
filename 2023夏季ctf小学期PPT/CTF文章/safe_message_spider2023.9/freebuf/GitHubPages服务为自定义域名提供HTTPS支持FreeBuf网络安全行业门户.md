![2018-05-01-github-pages-custom-domains-lock.png](https://image.3001.net/images/20180510/15259181079086.png!small)

GitHub Pages是为您和您的项目发布精美网站的最好方式。仅是通过编辑，推送，而您的改变都是大家可以看到的。GitHub
Pages自2009年起支持自定义域名，而在`*.github.io`域名上的网站，自2016年开始支持HTTPS。今天，GitHub
Pages上的自定义域名也开始获得来自HTTPS的支持。这意味着超过一百万个GitHub Pages网站会通过HTTPS提供服务。

HTTPS可加密GitHub服务器和浏览器之间的流量，从而让您确信您请求的页面就是您正在浏览的页面，而其它人不能在您浏览网站时探听或修改页面内容。

在这个项目上，我们与证书认证机构[Let’s Encrypt](https://letsencrypt.org/)合作，Let’s
Encrypt致力于让网络对每个人都更加安全的，作为它的这一使命支持者，我们已经正式成为这一倡议的白银赞助商。

##  **配置域**

您可能需要采取措施以保护您的自定义域名。

如果你正在使用`CNAME`或者`ALIAS`记录你的自定义域名，那么您的所有设备都是可用的，而且您的网站应该可以通过HTTPS进行访问。如果事实如此，而且您的网站确实可以通过HTTPS正确加载,您就可以选择在您的资源库设置中‘强制执行HTTPS’。通过HTTP访问您的网站的用户会被升级到HTTPS。

![2.png](https://image.3001.net/images/20180510/15259174783775.png!small)

如果您正在使用A记录，您必须用新的IP地址更新您网站的DNS记录。请参考我们的[指南](https://help.github.com/articles/setting-up-an-apex-domain/)，以利用Pages设置您的自定义域名并更新任意您可能设置过的A记录。

一旦您更新的DNS记录得到传播，而且您已确定您的网站通过HTTPS正确加载，您就可以在您的库的设置中为您的域名选择“强制执行HTTPS”。确保通过HTTP对您的网站发送请求的用户都可以升级到了HTTPS。

## 更快的站点加载时间

这些新的IP地址，并不仅仅是允许我们通过HTTPS服务于您的站点，还会把您的站点放在CDN后面，这样我们就可以快速的为您的站点提供来自世界各地的数据中心的服务，并提供对抗DDoS攻击的其它保护。尽管之前的IP地址在过渡期仍然有用，我们还是建议您迁移到新的IP地址，从而获取这些好处。

HTTPS将会很快应用于所有的GitHub
Pages网站。从我们的功能文档中获取更多内容。出现问题，请参照此[链接](http://www.example.com)。

*参考来源：[Custom domains on GitHub Pages gain support for HTTPS](https://blog.github.com/2018-05-01-github-pages-custom-domains-https/)，文章内容以原文为准，本文由丁牛网安实验室小编EVA编辑整理，如需转载请标明出处。

