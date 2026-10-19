![](https://image.3001.net/images/20211116/1637059489_61938ba13e1bb53796a4d.png!small)

## 关于ScaRCE框架

ScaRCE是一个专门针对漏洞CVE-2021-41773的漏洞挖掘框架，该工具可以帮助广大研究人员在漏洞扫描或渗透测试过程中，识别出公开站点中的CVE-2021-41773漏洞。

CVE-2021-41773漏洞主要影响的是Apahce 2
Web服务器，而ScaRCE通过扫描识别的方法找到目标Web服务器中的漏洞之后，将能够在目标Web服务器（需启用MOD_CGI）上执行远程命令注入。

该工具支持扫描单个目标，或从目标列表文件中读取目标信息并进行大规模识别扫描。

## 漏洞信息

根据Apache官方发布的安全公告，Apache HTTP Server中存在一个路径穿越漏洞，漏洞编号为CVE-2021-41773。Apache
HTTP Server（HTTPd）是Apache软件基金会的一个开放源代码的网页服务器，而Apache HTTP Server
2.4.49版本对路径规范化所做的更改中存在一个路径穿越漏洞，攻击者可利用该漏洞读取到Web目录外的其他文件，如系统配置文件、网站源码等，甚至在特定情况下，攻击者可构造恶意请求执行命令，控制服务器，且目前已存在在野利用。除此之外，攻击者还可利用该漏洞获得敏感信息甚至远程执行代码。

## 工具要求

  * curl
  * bash
  * git

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并执行ScaRCE框架脚本：

    
    
    - git clone https://github.com/HightechSec/scarce-apache2
    - cd scarce-apache2
    - bash scarce.sh

除此之外，你还可以使用下列方式在你的系统上安装并使用ScaRCE：

    
    
    - git clone https://github.com/HightechSec/scarce-apache2
    - cd scarce-apache2
    - sudo cp scarce.sh /usr/bin/scarce && sudo chmod +x /usr/bin/scarce
    - $ scarce

## 工具使用

### 菜单选项

> 菜单1：根据提供的文件扫描LFI漏洞，文件中包含目标主机URL列表或单个主机的URL地址。
>
> 菜单2：根据提供的文件扫描RCE（远程代码执行）漏洞，文件中包含目标主机URL列表或单个主机的URL地址。
>
> 菜单3：通过给定的目标URL地址在目标主机上实现远程代码执行，如果扫描结果存在假阳性，即目标并不受漏洞影响，则有可能报“500错误信息”。

### URL格式

>
> 使用http://（例如http://example.com）或https://（例如https://example.com）形式的URL地址来作为单个目标的地址参数。
>
> 对于通过列表文件提供的URL地址或IP地址，请不要使用如下所示的URL地址格式：
>
> [ _https://target.com_](https://target.com/)
>
> [ _http://hackerone.com_](http://hackerone.com/)
>
> [ _https://bugcrowd.com_](https://bugcrowd.com/)

## 工具使用演示

![](https://image.3001.net/images/20211116/1637059534_61938bce8bbded704601b.jpg!small)

![](https://image.3001.net/images/20211116/1637059540_61938bd4c53763ef8827c.jpg!small)

![](https://image.3001.net/images/20211116/1637059546_61938bda514adf1e1dbdd.jpg!small)

## 工具地址

 **ScaRCE：** 【[ _GitHub传送门_](https://github.com/HightechSec/scarce-apache2)】

