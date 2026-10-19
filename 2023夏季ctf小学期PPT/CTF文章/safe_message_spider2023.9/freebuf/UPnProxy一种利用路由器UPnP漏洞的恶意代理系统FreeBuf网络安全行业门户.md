## 前言

 **目前，全球大约有350多万台设备部署了UPnP，其中大概有28万台设备存在安全问题。Akamai的研究人员表示，现在已经有接近5万台设备受到了UpNp
NAT注入攻击活动的入侵，而这种注入攻击（针对的是SMB所使用的服务端口）会将目标路由器连接的设备暴露在互联网安全风险之中。**

![1.png](https://image.3001.net/images/20181202/1543757182_5c03dd7e37b80.png!small)

## 背景

今年年初，Akamai的研究人员发现有攻击者开始通过滥用通用即插即用（UPnP）来隐藏恶意流量，并创建恶意代理系统了，这种技术我们将其命名为UPnProxy。在UPnProxy的帮助下，攻击者可以随意控制恶意流量，这绝对是一种严重的安全风险，因为这样的安全漏洞可以应用到多种攻击技术中，包括垃圾邮件、网络钓鱼、点击欺诈和DDoS等等。

就目前的数据来看，UPnProxy目前仍在活动当中，全球潜在的受感染设备数量达到了350万台，已确定的易受攻击设备数量为28万台左右。虽然之前检测到的某些攻击活动已经消失了，但是我们又发现了其他新的攻击活动，所以受感染设备的数量一直在变化当中。

在Akamai之前发布的报告中，我们强调了攻击者利用UPnProxy来入侵目标路由器连接设备的可能性。不幸的是，这件事情真的发生了。

![2.png](https://image.3001.net/images/20181202/1543757195_5c03dd8b50c3b.png!small)

对于家庭用户来说，这种攻击可以导致一系列问题，比如说网络质量下降、恶意软件感染、勒索软件攻击和网络欺诈等等。但对于商业用户来说，这种安全威胁可以将那些本不应该暴露在互联网上的系统暴露在外，而且还是在管理员毫无意识的情况下发生的，这样就大大增加了企业系统的攻击面。更令人担忧的是，这种攻击主要针对的是Windows平台和Linux平台，而这两个平台是目前受木马蠕虫和勒索软件攻击最多的系统平台。

## “永恒的沉默”

在11月7日，研究人员又发现了一种属于UPnProxy家族的新型攻击活动，我们将其命名为Eternal
Silence，即“永恒的沉默”，而这个名字是从攻击者留下的端口映射描述中得来的。

在路由器上，路由器上的NewPortMappingDescription域一般是类似“Skype”这样的值，表示允许合法注入。在UPnProxy活动中，这个域可以被攻击者控制。在Akamai最新检测到的受攻击路由器中，这个域的值全部为西班牙文“galleta
silenciosa”或“silent cookie/cracker”。这种注入攻击会将目标路由器连接设备的TCP端口139和445暴露在外：

    
    
    {"NewProtocol":"TCP", "NewInternalPort": "445","NewInternalClient": "192.168.10.212",
    
    "NewPortMappingDescription":"galleta silenciosa", "NewExternalPort": "47669"}

综合所有分析结果考量，Akamai的研究人员认为攻击者很可能在利用EternalBlue和EternalRed漏洞在入侵其他设备。不幸的是，Akamai的研究人员无法得知注入攻击成功之后还会发生什么，因为目前我们只能观察到注入攻击的过程，而无法检测到最后完成直接攻击的Payload。研究人员认为，攻击成功之后网络犯罪分子能做的事情非常多，比如说实施勒索软件攻击，或在目标网络系统中植入后门并实现持续感染。

## 攻击分析

![3.png](https://image.3001.net/images/20181202/1543757217_5c03dda1379d2.png!small)

EternalBlue（CVE-2017-0144）：永恒之蓝，这已经是一个很有名的漏洞了，这个漏洞可以算是斯诺登当年从NSA那里“偷”来的。这个漏洞可以影响每一个Windows版本，即使你安装了补丁（MS17-010），近期也有网络犯罪分子仍在利用这个漏洞来发动[网络攻击](https://www.theguardian.com/technology/2017/dec/30/wannacry-petya-notpetya-ransomware)，比如说[WannaCry](https://en.wikipedia.org/wiki/WannaCry_ransomware_attack)和
[NotPetya](https://www.wired.com/story/notpetya-cyberattack-ukraine-russia-code-crashed-the-world/)。

EternalRed（CVE-2017-7494）：永恒之红，永恒之蓝的兄弟，它的目标是Samba，并开启了Eternal家族“进军”Linux系统的大门。它已经被用于多种恶意挖矿活动之中了，并且逐渐发展出了[SambaCry](https://www.pcworld.com/article/3199106/linux/the-sambacry-scare-gives-linux-users-a-taste-of-wannacry-petya-problems.html)。

我们发现，这一攻击活动其实并非具有针对性的攻击，而是利用现成的、经过现实考验过的真实开发成果来进行的大规模攻击，并通过“广撒网”的形式来填充网络犯罪分子的“目标设备池”。这种方式也很正常，因为很多没有接入外网的企业设备很可能没有安装针对永恒之蓝或永恒之红的补丁，但通过SMB端口转发技术，攻击者将能够入侵路由器背后的其他接入设备，此时那些没有安装补丁的设备将无一幸免。

下面给出的是我们在其中一台受感染路由器中发现的Eternal Silence注入样本：

    
    
    {"NewProtocol":"TCP", "NewInternalPort": "445","NewInternalClient": "192.168.10.165", 
    
    "NewPortMappingDescription":"galleta silenciosa", "NewExternalPort":"47622"}, 
    
    {"NewProtocol":"TCP", "NewInternalPort": "139","NewInternalClient": "192.168.10.166", 
    
    "NewPortMappingDescription":"galleta silenciosa", "NewExternalPort":"28823"}, 
    
    {"NewProtocol":"TCP", "NewInternalPort": "445","NewInternalClient": "192.168.10.166", 
    
    "NewPortMappingDescription":"galleta silenciosa", "NewExternalPort":"47623"}, 
    
    {"NewProtocol":"TCP", "NewInternalPort": "139","NewInternalClient": "192.168.10.183", 
    
    "NewPortMappingDescription":"galleta silenciosa", "NewExternalPort":"28840"}, 
    
    {"NewProtocol":"TCP", "NewInternalPort": "139","NewInternalClient": "192.168.10.194",
    
     "NewPortMappingDescription":"galleta silenciosa", "NewExternalPort":"28851"}, 
    
    {"NewProtocol":"TCP", "NewInternalPort": "139","NewInternalClient": "192.168.10.198", 
    
    "NewPortMappingDescription":"galleta silenciosa", "NewExternalPort":"28855"}, 
    
    {"NewProtocol":"TCP", "NewInternalPort": "139","NewInternalClient": "192.168.10.207",
    
     "NewPortMappingDescription":"galleta silenciosa", "NewExternalPort":"28864"}, 
    
    {"NewProtocol":"TCP", "NewInternalPort": "139","NewInternalClient": "192.168.10.209", 
    
    "NewPortMappingDescription":"galleta silenciosa", "NewExternalPort":"28866"}, 
    
    {"NewProtocol":"TCP", "NewInternalPort": "139","NewInternalClient": "192.168.10.212", 
    
    "NewPortMappingDescription":"galleta silenciosa", "NewExternalPort":"28869"}, 
    
    {"NewProtocol":"TCP", "NewInternalPort": "445","NewInternalClient": "192.168.10.212", 
    
    "NewPortMappingDescription":"galleta silenciosa", "NewExternalPort": "47669"}

## 缺乏可见度

一般来说，管理员很难在路由器上检测到恶意NAT注入行为。UPnP协议本身是用来让设备自动通过路由器的IGD来请求NAT/端口转发功能。在这种情况下，审计这些规则需要使用到UPnP工具集、设备扫描和手动规则审计。

下面这个Bash脚本可以导出UPnP NAT实体：

    
    
    #!/usr/bin/bashurl=$1 soap_head='<?xml version="1.0"encoding="utf-8"?>
    
    <s:Envelopes:encodingStyle="<http://schemas.xmlsoap.org/soap/encoding/>"xmlns:s="<http://schemas.xmlsoap.org/soap/envelope/>">
    
     
    
    <s:Body>
    
    <u:GetGenericPortMappingEntryxmlns:u="urn:upnp-org:serviceId:WANIPConnection.1#GetGenericPortMappingEntry">
    
    <NewPortMappingIndex>'
    
    soap_tail='</NewPortMappingIndex></u:GetGenericPortMappingEntry></s:Body></s:Envelope>'
    
     
    
    for iin `seq 1 10000`; do
    
        payload=$soap_head$i$soap_tail
    
        curl -H 'Content-Type:"text/xml;charset=UTF-8"' -H 'SOAPACTION: 
    
    "urn:schemas-upnp-org:service:WANIPConnection:1#GetGenericPortMappingEntry"'--data "$payload" "$url" echo "
    
    "done

下面是我们从一台受UPnProxy注入攻击的主机中导出的数据：

    
    
    $./brute_upnproxy.sh <http://192.168.1.1:2048/etc/linuxigd/gatedesc.xml>
    
    <?xmlversion="1.0"?>
    
    <s:Envelopexmlns:s="<http://schemas.xmlsoap.org/soap/envelope/>"s:encodingStyle="<http://schemas.xmlsoap.org/soap/encoding/>"><s:Body>
    
    <u:GetGenericPortMappingEntryResponsexmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
    
    <NewRemoteHost></NewRemoteHost><NewExternalPort>50694</NewExternalPort>
    
    <NewProtocol>TCP</NewProtocol><NewInternalPort>53</NewInternalPort><NewInternalClient>8.8.8.8</NewInternalClient>
    
    <NewEnabled>1</NewEnabled><NewPortMappingDescription>node:nat:upnp</NewPortMappingDescription><NewLeaseDuration>0</NewLeaseDuration>
    
    </u:GetGenericPortMappingEntryResponse></s:Body></s:Envelope>
    
     
    
    <?xmlversion="1.0"?>
    
    <s:Envelopexmlns:s="<http://schemas.xmlsoap.org/soap/envelope/>"s:encodingStyle="<http://schemas.xmlsoap.org/soap/encoding/>"><s:Body>
    
    <u:GetGenericPortMappingEntryResponsexmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1"><NewRemoteHost></NewRemoteHost>
    
    <NewExternalPort>30932</NewExternalPort><NewProtocol>TCP</NewProtocol><NewInternalPort>53</NewInternalPort>
    
    <NewInternalClient>8.8.8.8</NewInternalClient><NewEnabled>1</NewEnabled><NewPortMappingDescription>node:nat:upnp</NewPortMappingDescription>
    
    <NewLeaseDuration>0</NewLeaseDuration></u:GetGenericPortMappingEntryResponse></s:Body></s:Envelope>
    
    ...snip...

## 总结

毫无疑问，这些受攻击的设备将任由攻击者摆布。因为这些设备本不应该暴露在互联网上，而管理员也已经将这些设备进行了隔离，所以他们一般也不会去检查。此外，这些在内部网络系统中的设备很少会优先进行补丁安装或升级，因此它们的安全风险也会更高，而这种类型的攻击对这类设备的影响也会更大。

 ***参考来源：[akamai](https://blogs.akamai.com/sitr/2018/11/upnproxy-eternalsilence.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

