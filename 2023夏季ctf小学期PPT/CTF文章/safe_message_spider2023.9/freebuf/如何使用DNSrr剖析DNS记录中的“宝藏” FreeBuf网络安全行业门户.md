![](https://image.3001.net/images/20210825/1629872631_6125e1f78ce9f9797201e.jpg!small)

## 关于DNSrr

DNSrr采用Bash开发，可以帮助广大研究人员从DNS记录中枚举出所有有价值的内容，该工具使用了很多不同的技术，其中个包括：

> DNS转发爆破；
>
> DNS反向爆破；
>
> DNS缓存侦听；
>
> DNS区域转移；

上述技术，可以帮助我们从一台目标DNS服务器中尽可能多地收集到对我们有价值的信息。

 **我们将会在之后的版本中添加以下功能：**

> 添加新的技术，更好地从DNS记录中枚举出有效数据。
>
> 报告漏洞；
>
> 添加其他增强功能；

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/A3h1nt/Dnsrr

接下来，我们需要在命令行终端中切换到项目根目录，然后运行下列命令使用该工具：

    
    
    ./dnsrr.sh --help

## 工具使用

    
    
    ------------------- USAGE ------------------    
    -z    : Attempt Zone Transfer
    
            Syntax: ./dns.sh -z [Nameserver] [Domain Name]
    
    -fb   : Forward Lookup Bruteforce
    
            Syntax: ./dns.sh [Domain Name]
    
            Syntax: ./dns.sh [Domain Name] [Wordlist]
    
    -rb   : Reverse Lookup Bruteforce
    
            Syntax: ./dns.sh [Domain Name]
    
    -cs   : Perform DNS Cache Snooping
    
            Syntax: ./dns.sh [Name Server] [Wordlist]
    
    -x    : Explain A Particular Option
    
            Syntax: ./dns.sh -x [Option_Name]
    
    ------------------------------------------------
DNSrr支持五种不同的参数选项，如果你不知道每一个特定选项的实际作用，你可以直接使用“-x”选项来了解其背后的技术细节。

 **使用样例：**

    
    
    # To explain zone transfer
    
    ./dnsrr -x z

## 工具演示

### DNS区域转移

![](https://image.3001.net/images/20210825/1629872735_6125e25fdc5079d53baab.png!small)

### 转发查询爆破

![](https://image.3001.net/images/20210825/1629872744_6125e268ba215f62ca8d5.png!small)

## 项目地址

 **Dnsrr：** 【[ _GitHub传送门_](https://github.com/A3h1nt/Dnsrr)】

