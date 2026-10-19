![](https://image.3001.net/images/20220909/1662713804_631affcc07889c5fedc34.jpg!small)

## 关于pretender

pretender是一款功能强大的红队MitM安全测试工具，该工具专为红队研究人员设计，该工具不仅能够进行MitM和中继攻击，而且还支持执行DHCPv6
DNS接管以及mDNS、LLMNR和NetBIOS-NS欺骗攻击。在该工具的帮助下，广大研究人员可以针对目标网络执行更加全面的网络安全分析和渗透测试了。

pretender主要针对的是Windows主机，旨在执行中继攻击，但该工具也可以部署在Linux、Windows和其他支持Go程序的平台。除此之外，该工具支持使用任意IP应答名称解析查询。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/RedTeamPentesting/pretender.git

## 工具使用

为了获取到本地网络的详细情况，可以通过--dry模式来启动pretender，此时工具只会记录传入的查询，而不会应答任何查询请求：

    
    
    pretender -i eth0 --dry
    
    pretender -i eth0 --dry --no-ra # without router advertisements

如需通过mDNS、LLMNR和NetBIOS-NS执行本地域名解析欺骗，以及DNCPv6 DNS接管，可以直接运行下列命令：

    
    
    pretender -i eth0

我们可以使用--no-dhcp-dns、--no-lnr、--no-mdns、--no-llmnr、--no-netbios和--no-ra选项禁用特定的攻击。

如果ntlmrelayx.py运行在不同的主机三，比如说10.0.0.10/fe80::5，那么我们就可以通过下列形式运行pretender：

    
    
    pretender -i eth0 -4 10.0.0.10 -6 fe80::5

pretender可以设置为只响应指定域（或除特定域之外的所有域）的查询，并且它可以仅对特定主机（或除某些主机之外的所有主机）执行欺骗攻击：

    
    
    pretender -i eth0 --spoof example.com --dont-spoof-for 10.0.0.3,host1.corp,fe80::f --ignore-nofqdn

如需获取更多信息，可以运行下列信息查看工具帮助信息：

    
    
    pretender --help

## 工具构建

我们可以使用下列方式来构建pretender源码：

    
    
    go build

pretender还支持使用预配置设置来编译代码，此时需要按照下列形式修改ldflags：

    
    
    -ldflags '-X main.vendorInterface=eth1'

比如说，我们可以使用指定的默认接口来为Windows主机编译pretender，并配置中继IPv4地址（无颜色高亮输出）：

    
    
    GOOS=windows go build -trimpath -ldflags '-X "main.vendorInterface=Ethernet 2" -X main.vendorNoColor=true -X main.vendorRelayIPv4=10.0.0.10'

下面给出的是所有的vendor选项（可以通过defaults.go文件或pretender --help命令查看详细信息）：

    
    
    vendorInterface
    
    vendorRelayIPv4
    
    vendorRelayIPv6
    
    vendorSOAHostname
    
    vendorNoDHCPv6DNSTakeover
    
    vendorNoDHCPv6
    
    vendorNoDNS
    
    vendorNoMDNS
    
    vendorNoNetBIOS
    
    vendorNoLLMNR
    
    vendorNoLocalNameResolution
    
    vendorNoRA
    
    vendorNoIPv6LNR
    
    vendorSpoof
    
    vendorDontSpoof
    
    vendorSpoofFor
    
    vendorDontSpoofFor
    
    vendorSpoofTypes
    
    vendorIgnoreDHCPv6NoFQDN
    
    vendorDryMode
    
    vendorTTL
    
    vendorLeaseLifetime
    
    vendorRARouterLifetime
    
    vendorRAPeriod
    
    vendorStopAfter
    
    vendorVerbose
    
    vendorNoColor
    
    vendorNoTimestamps
    
    vendorLogFileName
    
    vendorNoHostInfo
    
    vendorHideIgnored
    
    vendorRedirectStderr
    
    vendorListInterfaces

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/RedTeamPentesting/pretender/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **pretender** ：【[
_GitHub传送门_](https://github.com/RedTeamPentesting/pretender)】

## 参考资料

> [
> _https://github.com/SecureAuthCorp/impacket_](https://github.com/SecureAuthCorp/impacket)
>
> [
> _https://github.com/dirkjanm/krbrelayx_](https://github.com/dirkjanm/krbrelayx)
>
> [ _https://blog.redteam-pentesting.de/2022/introducing-> pretender/_](https://blog.redteam-pentesting.de/2022/introducing-pretender/)

