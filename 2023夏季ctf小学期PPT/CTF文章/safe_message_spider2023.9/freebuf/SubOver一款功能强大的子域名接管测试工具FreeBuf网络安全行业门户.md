![](https://image.3001.net/images/20230508/1683539131_6458c4bb0639fc3083848.jpg!small)

## 关于SubOver

SubOver是一款功能强大的子域名接管测试工具，该工具原先采用Python语言开发，后续使用了Golang进行重写。自该工具重构开始，它一直以速度和运行效率为首要目标。到目前为止，当前版本的SubOver支持检测30多项服务，这一点也是该工具的强大之处。

当前版本的SubOver使用Golang的并发特性进行开发，因此速度非常快。在该工具的帮助下，广大研究人员可以轻松检测和报告潜在的子域名接管问题。

## 工具要求

> Golang

## 工具安装

由于该工具基于Golang开发，因此我们首先需要在本地设备上安装并配置好Golang环境，除此之外无需其他任何依赖组件。

### Go安装

    
    
    go get github.com/Ice3man543/SubOver

### 源码获取

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Ice3man543/SubOver.git

## 工具使用

    
    
    ./SubOver -l subdomains.txt

### 参数解析

> -l：指定子域名列表文件路径（每个子域名按行分隔）；
>
> -a：检测所有的主机，忽略CNAME；
>
> -t：设置并发线程数量；
>
> -v：显示Verbose输出（默认false）；
>
> -https：强制使用HTTPS连接（默认为HTTP）；
>
> -timeout：设置自定义超时时间（默认为10s）；
>
> -h：显示工具帮助信息；

## 支持检测的服务

> Github, Heroku, Unbounce, Tumblr, Shopify, Instapage, Desk, Tictail,
> Campaignmonitor, Cargocollective, Statuspage, Amazonaws, Cloudfront,
> Bitbucket, Smartling, Acquia, Fastly, Pantheon, Zendesk, Uservoice, Ghost,
> Freshdesk, Pingdom, Tilda, Wordpress, Teamwork, Helpjuice, Helpscout, Cargo,
> Feedpress, Surge, Surveygizmo, Mashery, Intercom, Webflow, Kajabi,
> Thinkific, Tave, Wishpond, Aftership, Aha, Brightcove, Bigcartel,
> Activecompaign, Compaignmonitor, Acquia, Proposify, Simplebooklet,
> Getresponse, Vend, Jetbrains, Azure

## 工具运行截图

![](https://image.3001.net/images/20230508/1683539226_6458c51a1618d9bec6d4c.png!small)

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-2-Clause_](https://github.com/Ice3man543/SubOver/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **SubOver** ：【[ _GitHub传送门_](https://github.com/Ice3man543/SubOver)】

## 参考资料

> [ _https://github.com/haccer/subjack_](https://github.com/haccer/subjack)
>
> [ _https://github.com/antichown/subdomain-> takeover_](https://github.com/antichown/subdomain-takeover)
>
> [ _https://github.com/anshumanbh/tko-> subs_](https://github.com/anshumanbh/tko-subs)
>
> [ _https://github.com/edoverflow/can-i-take-over-> xyz_](https://github.com/edoverflow/can-i-take-over-xyz)

