***本工具仅供技术分享、交流讨论，严禁用于非法用途**

**VulnX是一款自动化Shell注入工具，支持多种类型的内容管理系统，其中包括Wordpress、Joomla、Drupal和Prestashop等等，广大研究人员可以使用VulnX来检测这些CMS系统中的安全问题。**

![2.jpg](https://image.3001.net/images/20190617/1560733454_5d06e70ed5171.jpg!small)

VulnX本质上是一款智能化Bot，可实现Shell自动注入，并帮助研究人员检测CMS系统中的安全漏洞。它可以执行快速CMS安全检测、信息收集（包括子域名、ip地址、国家信息、组织信息和时区等等）和漏洞扫描。

## 功能介绍

> 1、 检测CMS漏洞，支持wordpress, joomla, prestashop, drupal, opencart, magento,
> lokomedia；
>
> 2、 目标信息收集；
>
> 3、 目标子域名收集；
>
> 4、 多线程扫描支持；
>
> 5、 检测安全漏洞
>
> 6、 自动Shell注入；
>
> 7、 利用Dork搜索引擎；
>
> 8、 高级端口扫描；
>
> 9、 DNS服务器导出；
>
> 10、同时扫描多个目标；
>
> 11、Dork枚举；

### DNS映射

用户课使用--dns或-d来对目标子域名执行DNS映射，并生成isetso.rnu.tn：

    
    
    vulnx-u isetso.rnu.tn --dns -d --output $PATH

其中的$PATH变量存储的是结果图的存储地址。

![3.png](https://image.3001.net/images/20190617/1560733468_5d06e71c103bb.png!small)

![4.png](https://image.3001.net/images/20190617/1560733471_5d06e71f80230.png!small)

## 漏洞利用

![6.gif](https://image.3001.net/images/20190617/1560733487_5d06e72f57b20.gif!small)

## 各CMS平台支持的扫描组件

### Joomla

> [Com Jce](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Com Jwallpapers](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Com Jdownloads](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)[Com
> Jdownloads2](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Com Weblinks](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Com Fabrik](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Com Fabrik](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Com Jdownloads Index](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)[Com
> Foxcontact](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Com Blog](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Com Users](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)[Com Ads
> Manager](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Com Sexycontactform](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Com Media](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)
>
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)[Mod_simplefileupload](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)[Com
> Facileforms](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Com Facileforms](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Com extplorer](https://github.com/anouarbensaad/vulnx/blob/master/)

### Wordpress

> [Simple Ads Manager](https://www.exploit-db.com/exploits/36614)
>
> [InBoundio
> Marketing](https://www.rapid7.com/db/modules/exploit/unix/webapp/wp_inboundio_marketing_file_upload)
>
> [WPshop
> eCommerce](https://www.rapid7.com/db/modules/exploit/unix/webapp/wp_wpshop_ecommerce_file_upload)
>
> [Synoptic](https://cxsecurity.com/issue/WLB-2017030099)
>
> [Showbiz Pro](https://www.exploit-db.com/exploits/35385)
>
> [Job Manager](https://www.exploit-db.com/exploits/45031)
>
> [Formcraft](https://www.exploit-db.com/exploits/30002)
>
> [PowerZoom](http://www.exploit4arab.org/exploits/399)
>
> [Download Manager](https://www.exploit-db.com/exploits/35533)
>
> [CherryFramework](https://www.exploit-db.com/exploits/45896)
>
> [Catpro](https://vulners.com/zdt/1337DAY-ID-20256)
>
> [Blaze SlideShow](https://0day.today/exploits/18500)
>
> [Wysija-Newsletters](https://www.exploit-db.com/exploits/33991)

### Drupal

> [Add Admin](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)[Drupal
> BruteForcer](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [Drupal Geddon2](https://github.com/anouarbensaad/vulnx/blob/master/)

### PrestaShop

> [attributewizardpro](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)
>
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)[columnadverts](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [soopamobile](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [pk_flexmenu](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [pk_vertflexmenu](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [nvn_export_orders](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [megamenu](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [tdpsthemeoptionpanel](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [psmodthemeoptionpanel](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [masseditproduct](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)
>
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)[blocktestimonial](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [soopabanners](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)
>
>
> [](https://github.com/anouarbensaad/vulnx/blob/master/)[Vtermslideshow](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [simpleslideshow](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [productpageadverts](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [homepageadvertise](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [homepageadvertise2](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [jro_homepageadvertise](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [advancedslider](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [cartabandonmentpro](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [cartabandonmentproOld](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [videostab](https://github.com/anouarbensaad/vulnx/blob/master/)
>
>
> [wg24themeadministration](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [fieldvmegamenu](https://github.com/anouarbensaad/vulnx/blob/master/)
>
> [wdoptionpanel](https://github.com/anouarbensaad/vulnx/blob/master/)

### Opencart

> [Opencart BruteForce](https://github.com/anouarbensaad/vulnx/blob/master/)

可用的命令行选项

    
    
    usage:vulnx [options]
    
      -u --url              目标URL地址
    
      -D --dorks            搜索Dock
    
      -o --output           指定输出目录
    
      -t --timeout          HTTP请求超时
    
      -c --cms-info         搜索CMS信息，包括主题、插件、用户和版本
    
      -e --exploit           扫描并利用安全漏洞
    
      -w --web-info        Web信息收集
    
      -d --domain-info     子域名信息收集
    
      -l, --dork-list         枚举Dork列表
    
      -n, --number-page   搜索引擎的页面数量(Google)
    
      -p, --ports           端口扫描
    
      -i, --input            从输入文件导入目标域名
    
      --threads            扫描线程数量
    
      --dns                DNS信息收集

## 工具安装

### Docker安装

    
    
    $ git clone <https://github.com/anouarbensaad/VulnX.git>
    
    $ cd VulnX
    
    $ docker build -t vulnx ./docker/
    
    $ docker run -it --name vulnx vulnx:latest -u <http://exemple.com>

[](http://exemple.com)

**查看日志文件：**

    
    
    $ docker run -it --name vulnx -v "$PWD/logs:/VulnX/logs" vulnx:latest-u http://exemple.com

### Ubuntu安装

    
    
    $ git clone <https://github.com/anouarbensaad/vulnx.git>
    
    $ cdVulnX
    
    $ chmod +x install.sh
    
    $ ./install.sh

### Termux安装

    
    
    $ pkg update
    
    $ pkg install -y git
    
    $ git clone <http://github.com/anouarbensaad/vulnx>
    
    $ cd vulnx
    
    $ chmod +x install.sh
    
    $ ./install.sh

## 工具常用命令

参考命令样本：settimeout=3 , cms-gathering = all , -d subdomains-gathering , run--exploits

    
    
    vulnx -u http://example.com --timeout 3 -c all -d -w –exploit

搜索Dork样本命令：-D or --dorks , -l --list-dorks

vulnx--list-dorks命令将会返回可利用漏洞表。

 **搜索单个目标网站**

选项：-u或--url

    
    
    vulnx -u http://example.com

 **扫描超时**

选项：--timeout（默认为3秒）

    
    
    vulnx-u http://example.com --timeout=4

 **运行漏洞利用模块**

选项：--exploit或-e

    
    
    vulnx-u http://example.com --exploit

 **CMS信息收集**

选项：--cms-info或-c

    
    
    vulnx-u http://example.com --cms-info all

 **子域名 &IP信息收集**

选项：--domain-info或-d

    
    
    vulnx-u http://example.com --domain-info

 **网站信息收集**

选项：--web-info或-w

    
    
    vulnx-u http://example.com --web-info

 **扫描开放端口**

选项：--ports或-p

    
    
    vulnx-u http://example.com --ports

 **DNS信息收集**

选项：--dns

    
    
    vulnx-u http://example.com --dns

## 项目地址

VulnX：【[GitHub传送门](https://github.com/anouarbensaad/vulnx)】

### 许可证协议

本项目遵循[GPL-v3.0](https://github.com/anouarbensaad/VulnX/blob/master/LICENSE)开源许可证协议。

 ***
参考来源：[anouarbensaad](https://github.com/anouarbensaad/vulnx)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

