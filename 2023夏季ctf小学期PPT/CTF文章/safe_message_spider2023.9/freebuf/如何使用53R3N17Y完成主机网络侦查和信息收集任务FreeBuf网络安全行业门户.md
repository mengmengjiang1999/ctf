![](https://image.3001.net/images/20230421/1682071459_64425fa330d6b03b3e023.jpg!small)

## 关于53R3N17Y

53R3N17Y是一款功能强大的信息收集工具，该工具基于Python开发，可以帮助广大研究人员快速收集与目标主机、IP地址或域名的相关信息。

该工具基于hackertarget.com来收集与目标相关的详细信息，因此针对单个IP地址，每天的API调用次数上限为100次。

## 支持的操作系统平台

> OSX El Capitan 10.11
>
> Ubuntu 16.04
>
> Backbox 5
>
> Kali Linux 2018.1

注意：当前版本的53R3N17Y已在Python 2.7.14环境中进行过完整测试。

## 工具安装

由于该工具基于Python 2开发，因此我们首先需要在本地设备上安装并配置好Python 2.7.14环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/abaykan/53R3N17Y.git serenity

然后切换到项目目录中，并使用pip命令和项目提供的requirements.txt文件安装该工具所需的其他依赖组件：

    
    
    cd serenity
    
    pip install -r requirements.txt

安装完成之后，我们就可以运行下列命令来启动53R3N17Y并查看工具帮助信息：

    
    
    serenity -h

## 工具帮助菜单

![](https://image.3001.net/images/20230421/1682071496_64425fc87908dcb102bcc.png!small)

## 工具参数解析

> -h, --help 显示工具帮助信息
>
> -1, --revht 通过HackTarget获取反向IP
>
> -2, --revygs 通过YouGetSignal 获取反向IP
>
> -3, --geo IP地理位置查询
>
> -4, --whois Whois 查询
>
> -5, --host 搜索目标主机
>
> -6, --dns DNS 查询
>
> -7, --sdns 寻找共享DNS
>
> -8, --http 显示HTTP Header
>
> -9, --links 页面链接爬取

## 工具输出样例

    
    
    ~/tools/53R3N17Y (master*) ▶ serenity -a google.com                                                                 
    
         _-----_
    
        |       |    .------------------------.
    
        |--(o)--|    |   Welcome to 53R3N17Y  |
    
       `---------´   |       abaykan.com      |
    
        ( _´U`_ )    '------------------------'
    
        /___A___
    
         |  ~  |
    
       __'.___.'__
    
     ´   `  |° ´ Y `
    
     
    
    2018-04-07 23:50:07
    
     
    
     
    
     
    
     
    
     
    
    Geo IP Lookup 'http://google.com'
    
    ------------------------------------    
     
    
    [#] IP Address: 216.58.217.46
    
    [#] Country: US
    
    [#] State: California
    
    [#] City: Mountain View
    
    [#] Latitude: 37.419201
    
    [#] Longitude: -122.057404
    
     
    
     
    
     
    
    Reversing IP 'http://google.com'
    
    -----------------------------------    
     
    
    [#] den03s10-in-f46.1e100.net
    
    [#] voidweaver.com
    
     
    
     
    
     
    
    Whois Lookup 'http://google.com'
    
    -----------------------------------    
     
    
    [#]    Domain Name: GOOGLE.COM
    
    [#]    Registry Domain ID: 2138514_DOMAIN_COM-VRSN
    
    [#]    Registrar WHOIS Server: whois.markmonitor.com
    
    [#]    Registrar URL: http://www.markmonitor.com
    
    [#]    Updated Date: 2018-02-21T18:36:40Z
    
    [#]    Creation Date: 1997-09-15T04:00:00Z
    
    [#]    Registry Expiry Date: 2020-09-14T04:00:00Z
    
    [#]    Registrar: MarkMonitor Inc.
    
    [#]    Registrar IANA ID: 292
    
    [#]    Registrar Abuse Contact Email: abusecomplaints@markmonitor.com
    
    [#]    Registrar Abuse Contact Phone: +1.2083895740
    
    [#]    Domain Status: clientDeleteProhibited https://icann.org/epp#clientDeleteProhibited
    
    [#]    Domain Status: clientTransferProhibited https://icann.org/epp#clientTransferProhibited
    
    [#]    Domain Status: clientUpdateProhibited https://icann.org/epp#clientUpdateProhibited
    
    [#]    Domain Status: serverDeleteProhibited https://icann.org/epp#serverDeleteProhibited
    
    [#]    Domain Status: serverTransferProhibited https://icann.org/epp#serverTransferProhibited
    
    [#]    Domain Status: serverUpdateProhibited https://icann.org/epp#serverUpdateProhibited
    
    [#]    Name Server: NS1.GOOGLE.COM
    
    [#]    Name Server: NS2.GOOGLE.COM
    
    [#]    Name Server: NS3.GOOGLE.COM
    
    [#]    Name Server: NS4.GOOGLE.COM
    
    [#]    DNSSEC: unsigned
    
    [#]    URL of the ICANN Whois Inaccuracy Complaint Form: https://www.icann.org/wicf/
    
    [#] >>> Last update of whois database: 2018-04-07T16:49:58Z <<<
    
    [#] For more information on Whois status codes, please visit https://icann.org/epp
    
    [#] NOTICE: The expiration date displayed in this record is the date the
    
    [#] registrar's sponsorship of the domain name registration in the registry is
    
    [#] currently set to expire. This date does not necessarily reflect the expiration
    
    [#] date of the domain name registrant's agreement with the sponsoring
    
    [#] registrar.  Users may consult the sponsoring registrar's Whois database to
    
    [#] view the registrar's reported date of expiration for this registration.
    
    [#] The Registry database contains ONLY .COM, .NET, .EDU domains and
    
    [#] Registrars.
    
     
    
     
    
     
    
    Searching Host 'http://google.com'
    
    -------------------------------------    
     
    
    [#] error check your search parameter
    
     
    
     
    
     
    
    DNS Lookup 'http://google.com'
    
    ---------------------------------    
     
    
    [#] ;; Truncated, retrying in TCP mode.
    
    [#] google.com. 93 IN A 172.217.8.110
    
    [#] google.com. 136 IN AAAA 2607:f8b0:4008:802::200e
    
    [#] google.com. 307379 IN NS ns2.google.com.
    
    [#] google.com. 307379 IN NS ns3.google.com.
    
    [#] google.com. 307379 IN NS ns1.google.com.
    
    [#] google.com. 307379 IN NS ns4.google.com.
    
     
    
     
    
     
    
    Find Shared DNS 'http://google.com'
    
    --------------------------------------    
     
    
    [#] ioide.org
    
    [#] jowettconsulting.co.nz
    
    [#] graceunconditional.com
    
    [#] growability.org.au
    
    [#] happylambert.xyz
    
    [#] meragav.online
    
    [#] abc-learning-center.org
    
    [#] activelyproactive.christmas
    
    [#] activelyproactive.club
    
    [#] activelyproactive.company
    
    [#] activelyproactive.guru
    
    [#] activelyproactive.london
    
    [#] activelyproactive.photography
    
    [#] activelyproactive.sale
    
    [#] activelyproactive.website
    
    [#] xn--80ab0aoqap9e.xn--p1ai
    
    [#] xn--86-jlcd4afobn6c.xn--p1ai
    
    [#] bookmovie.biz
    
    [#] cafejo.cl
    
    [#] castlerockdesignanddevelopment.com
    
    [#] chasel.top
    
    [#] rding-china.com
    
    [#] remholod86.ru
    
    [#] multiferreteria.com
    
    [#] alvinspeed.info
    
    [#] appleid-support.org
    
    [#] asmallcompany.net
    
    [#] trenchant.in
    
    [#] event-photography-berlin.com
    
    [#] sdrobo.space
    
    [#] shira-1.org
    
    [#] cspk.in
    
    [#] wushuguan.se
    
    [#] khoroshkov.ru
    
    [#] kkenterprises.org
    
    [#] klinika16.ru
    
    [#] laybal.ru
    
    [#] skylinemedia.ru
    
    [#] stayout.tech
    
    [#] free2meet4love-events.online
    
    [#] fropost.ru
    
    [#] iantestfeb28.xxx
    
     
    
     
    
     
    
    HTTP Header Host 'http://google.com'
    
    ---------------------------------------    
     
    
    [#] HTTP/1.1 301 Moved Permanently
    
    [#] Location: http://www.google.com/
    
    [#] Content-Type: text/html; charset=UTF-8
    
    [#] Date: Sat, 07 Apr 2018 16:50:13 GMT
    
    [#] Expires: Mon, 07 May 2018 16:50:13 GMT
    
    [#] Cache-Control: public, max-age=2592000
    
    [#] Server: gws
    
    [#] Content-Length: 219
    
    [#] X-XSS-Protection: 1; mode=block
    
    [#] X-Frame-Options: SAMEORIGIN

## 工具使用演示

 **演示视频** ：【[ _点我观看_](https://asciinema.org/a/176391)】

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/abaykan/53R3N17Y/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **53R3N17Y** ：【[ _GitHub传送门_](https://github.com/abaykan/53R3N17Y)】

## 参考资料

> [ _https://hackertarget.com/_](https://hackertarget.com/)
>
> [
> _http://hits.dwyl.io/abaykan/53R3N17Y_](http://hits.dwyl.io/abaykan/53R3N17Y)

