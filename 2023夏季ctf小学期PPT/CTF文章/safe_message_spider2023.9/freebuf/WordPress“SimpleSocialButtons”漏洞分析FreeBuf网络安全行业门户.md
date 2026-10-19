***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 0×01 前言

 **WordPress “Simple Social
Buttons”插件是一个流行的免费和付费插件，可以在侧边栏，内嵌，帖子内容的上方和下方等位置添加社交媒体共享按钮，像下图这样，根据插件供应商[WPBrigade](https://wpbrigade.com/wordpress/plugins/simple-social-buttons/)所述，该插件在WordPress插件库有超过500,000次下载，有超过40,000多个活动安装[。](https://wpbrigade.com/wordpress/plugins/simple-social-buttons/)该插件在2月11号曝出严重漏洞，影响广泛。**

![share.png](https://image.3001.net/images/20190213/1550071803_5c6437fb6e263.png!small)

## 0×02 影响范围及利用条件

影响范围：该漏洞影响Simple Social Buttons v2.0.4到v2.0.22之间的所有版本。  

利用条件：wordpress网站普通用户权限。

## 0×03 漏洞描述

该插件由于缺少权限检查，导致WordPress允许非管理员用户执行管理员操作，比如以订阅者用户身份修改wp_options
表数据，熟悉wordpress的人应该都知道wp_options表包含了许多应用配置信息，比如admin_email、siteurl、home等。

## 0×04 详细利用方式

根据以上漏洞描述，以普通用户权限可以修改wp_options表中的admin_email字段。以下是在本地环境下的复现过程：

1.首先搭建好wordpress环境，建立两个账户，其中一个为管理员账户admin，一个为普通用户A。

2.然后以admin用户登录，安装Simple Social
Buttons插件，wordpress官方插件库已经发布安全更新，这里通过下载安装，使用2.0.18版本，[Simple Social Buttons
v2.0.18下载地址](https://downloads.wordpress.org/plugin/simple-social-buttons.2.0.18.zip)，在wordpress\wp-content\plugins\目录下解压即可：

![install.png](https://image.3001.net/images/20190214/1550074267_5c64419b636a7.png!small)

3.刷新wordpress后台页面，即可看到Simple Social Buttons v2.0.18已经安装好：

![installsuc.png](https://image.3001.net/images/20190214/1550074412_5c64422c83680.png!small)4.然后访问Simple
Social
Buttons插件配置页面，这里主要是用来设置分享按钮的样式、位置等。该插件提供了直接import/export配置的功能，可以直接导入一段json进行配置，漏洞就发生在import功能处：

![import.png](https://image.3001.net/images/20190214/1550074828_5c6443ccc0f8c.png!small)

5.这里因为不知道json配置文件的具体格式一直报invalid，我们可以先export再import，导入我们的ssb-export-2019-2-13.json文件：

![importjson.png](https://image.3001.net/images/20190214/1550075048_5c6444a87bffa.png!small)然后通过抓包，我们可以拿到这个import请求，如下：

![request.png](https://image.3001.net/images/20190214/1550075211_5c64454bd3e4c.png!small)该请求包含了import的json数据，使用admin的cookie。

6.这里的漏洞利用就是基于这个请求，替换cookie为普通用户A的cookie，更改要import的json数据为{"admin_email":
"evil@evil.com"}，得到poc如下：

![poc.png](https://image.3001.net/images/20190214/1550076174_5c64490ea562c.png!small)

7.发送请求，便成功地以用户A的身份更改wp_options表中的admin_email字段：

![suc.png](https://image.3001.net/images/20190214/1550076241_5c6449512f48d.png!small)

## 0×05 总结&修复

该漏洞利用POST /wordpress/wordpress/wp-admin/admin-ajax.php请求，以任意普通用户身份即可执行管理员操作，危害较大。

修复方式：更新Simple Social Buttons插件至v2.0.22即可，官方当晚就发布了安全更新。

 ***本文作者：帕克飞走了，转载请注明来自FreeBuf.COM**

