近日，WordPress安全公司Wordfence的研究人员发现一项严重的漏洞，它可以作用于三种不同的WordPress插件，并已影响超过84000个网站。
该漏洞的执行代码被追踪为CVE-2022-0215，是一种跨站请求伪造(CSRF) 攻击，通用安全漏洞评分系统（CVSS）对其给予8.8的评分。
![](https://image.3001.net/images/20220118/1642498627_61e68a43da3023f037a29.jpg!small)

2021年 11 月 5 日，Wordfence 公司情报团队第一次在Login/Signup Popup插件中发现这个漏洞并启动披露程序
。几天后他们又在Cart Woocommerce (Ajax)插件与Waitlist Woocommerce (Back in stock
notifier)插件中发现了相同的漏洞。通过这个漏洞攻击者只要欺骗站点管理员执行一个动作就可以更新在受攻击网站上的任意站点选项。

攻击者通常会制作一个触发 AJAX
操作并执行该功能的请求。如果攻击者能够成功诱骗站点管理员执行诸如单击链接或浏览到某个网站之类的操作，而管理员已通过目标站点的身份验证，则该请求将成功发送并触发该操作，该操作将允许攻击者更新该网站上的任意选项。

攻击者可以利用该漏洞将网站上的“users_can_register”（即任何人都可以注册）选项更新为
确定，并将“default_role”设置（即在博客上注册的用户的默认角色）设置为管理员，那么他就可以在受攻击的网站上注册为管理员并完全接管它。

## Wordfence团队报告的影响 Xootix维护的三个插件：

> Login/Signup Popup插件（超过 20000 次安装）
>
> Side Cart Woocommerce(Ajax)插件 （超过 4000 次安装）
>
> Waitlist Woocommerce (Back in stock notifier)插件（超过 60000 次安装）

这三个XootiX插件设计的初衷旨在为 WooCommerce 网站提供增强功能。Login/Signup Popup
插件允许添加登录和注册弹出窗口到标准网站和运行WooCommerce插件的网站。Waitlist WooCommerce
插件允许添加产品等待列表和缺货项目通知。Side Cart Woocommerce 插件通过 AJAX 提供支持使网站上的任何地方使用都可以使用购物栏。

![](https://image.3001.net/images/20220118/1642498836_61e68b14d2d31693f7c77.png!small)

对于这项漏洞，Wordfence
团队特别提醒WordPress用户必须检查其网站上运行的版本是否已更新为这些插件可用的最新修补版本，即Login/Signup Popup插件 2.3
版，Waitlist Woocommerce插件2.5.2 版”，以及Side Cart Woocommerce 插件 2.1 版。

> 参考来源：
>
> <https://securityaffairs.co/wordpress/126821/hacking/wordpress-plugins-> flaws-2.html>

