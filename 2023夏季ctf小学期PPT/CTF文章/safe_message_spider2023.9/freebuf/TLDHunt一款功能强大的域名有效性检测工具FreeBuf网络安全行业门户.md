![](https://image.3001.net/images/20230606/1686039119_647eea4f7729cb1710ca9.png!small)  

## 关于TLDHunt

TLDHunt是一款功能强大的域名有效性检测工具，TLDHunt本质上是一个命令行工具，可以帮助广大研究人员在其线上项目或其他业务进行过程中快速识别可用的域名。通过提供关键字和TLD（顶级域名）扩展列表，TLDHunt能够帮助检查符合给定条件域名的可用性。对于那些想要快速找到尚未使用的域名而不必在域名注册商网站上进行手动搜索的开发人员或安全研究人员来说，该工具特别有用。

如果你是红队或蓝队研究人员的话，该工具则可以帮助我们查找与原始域名相关的具有不同域名后缀的相似域名。

## 工具运行机制

为了检测目标域名是否有效或是否已经被注册，我们可以在WHOIS命令的输出结果中搜索单词“Name
Server”、“nsever”、“nameservers”或“status：active”，因为这些都是已注册域名的签名标记。

## 工具依赖组件

该工具使用Bash开发，唯一需要的依赖组件为whois库。因此，我们需要确保已经在本地设备上安装并配置好了whois。在Debian操作系统中，我们可以使用下列命令来安装whois：

    
    
    sudo apt install whois -y

## 域名扩展列表

工具提供的默认顶级域名列表（tlds.txt）的数据来源于https://data.iana.org/，我们也可以使用自己的自定义列表文件，但你需要确保文件内容格式如下：

    
    
    .aero
    
    .asia
    
    .biz
    
    .cat
    
    .com
    
    .coop
    
    .info
    
    .int
    
    .jobs
    
    .mobi

## 工具使用

    
    
    ➜  TLDHunt ./tldhunt.sh
    
     _____ _    ___  _  _          _   
    
    |_   _| |  |   \| || |_  _ _ _| |_
    
      | | | |__| |) | __ | || | ' \  _|
    
      |_| |____|___/|_||_|\_,_|_||_\__|
    
            Domain Availability Checker
    
     
    
    Keyword is required.
    
    Usage: ./tldhunt.sh -k <keyword> [-e <tld> | -E <exts>] [-x]
    
    Example: ./tldhunt.sh -k linuxsec -E tlds.txt

## 工具使用样例

使用默认的顶级域名列表：

    
    
    ./tldhunt.sh -k linuxsec

使用自定义顶级域名列表：

    
    
    ./tldhunt.sh -k linuxsec -E custom-tld.txt

添加-x选项仅输出未注册的域名：

    
    
    ./tldhunt.sh -k linuxsec -x

## 工具运行截图

![](https://image.3001.net/images/20230606/1686039224_647eeab8577fe399c5724.png!small)

## 项目地址

 **TLDHunt** ：【[ _GitHub传送门_](https://github.com/yuyudhn/TLDHunt)】

## 参考资料

> [ _https://github.com/Alex-Matveenko_](https://github.com/Alex-Matveenko)
>
> [ _https://data.iana.org/_](https://data.iana.org/)

