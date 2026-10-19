**今天给大家介绍一款名叫Pure Blood的渗透测试框架，该框架专为白帽子、渗透测试人员和Bug猎人设计，可实现多种渗透测试及信息收集功能。**

![a.png](https://image.3001.net/images/20180810/1533890402_5b6d4f62640b1.png!small)

## Pure Blood v2

### Web渗透/信息收集功能：

> 获取Banner；
>
> Whois查询；
>
> 路径跟踪；
>
> DNS记录；
>
> 反向DNS查询；
>
> DNS域传送查询；
>
> 端口扫描；
>
> 管理员接口扫描；
>
> 子域名扫描；
>
> CMS识别；
>
> 反向IP查询；
>
> 子网查询；
>
> 提取页面链接；
>
> 目录Fuzz（新功能）；
>
> 文件Fuzz（新功能）；
>
> Shodan搜索（新功能）；
>
> Shodan主机查询（新功能）。

### Web应用攻击（新功能）：

1.Wordpress：

> WPScan
>
> WPScan爆破攻击
>
> WordPress插件漏洞检测
>
> WordPress Woocommerce（目录欺骗攻击）
>
> WordPress Booking Calender 3.0.0（SQL注入/跨站脚本攻击）
>
> WordPress WP whit Spritz 1.0（远程文件包含攻击）
>
> WordPress Events Calendar（‘event_id‘ SQL注入攻击）

2.自动化SQL注入：

> 基于Union
>
> (Error Output = False)检测
>
> 功能已在超过100个站点上进行过测试

### 生成器：

1.修改目标页面；

2.密码生成器（新功能）；

3.哈希生成（新功能）。

## 工具安装

注：该工具支持任意Python版本。

你可以使用下列命令安装Pure Blood及其依赖组件：

    
    
    $ git clone <https://github.com/cr4shcod3/pureblood>
    
    $ cd pureblood
    
    $ pipinstall -r requirements.txt

## 视频演示

Web渗透：<https://asciinema.org/a/193579>

Web应用攻击：<https://asciinema.org/a/193578>

### Pure Blood还整合了以下项目资源：

> 1.[Colorama](https://pypi.org/project/colorama)
>
> 2.[Requests](https://github.com/requests/requests)
>
> 3.[Python-whois](https://pypi.org/project/python-whois)
>
> 4.[Dnspython](http://www.dnspython.org/)
>
> 5.[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup)
>
> 6.[Shodan](https://shodan.readthedocs.io/en/latest/)

### 许可证协议：

> 本项目遵循[MIT许可证协议](https://choosealicense.com/licenses/mit)。

## 其他

该项目目前仍在开发阶段，并且每天都会增加新的功能，但是在新版本发布之前开发者（[Cr4sHCoD3](https://www.facebook.com/cr4shcod3.py)）还需要进行完整测试，因此版本并不会每天都更新。该工具任何人都可以免费获取和使用，如果你在使用Pure
Blood的过程中发现了bug或者有更好的实施建议，可以到本项目的【[GitHub主页](https://github.com/cr4shcod3/pureblood)】上留言。

* 参考来源：[pureblood](https://github.com/cr4shcod3/pureblood)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM

