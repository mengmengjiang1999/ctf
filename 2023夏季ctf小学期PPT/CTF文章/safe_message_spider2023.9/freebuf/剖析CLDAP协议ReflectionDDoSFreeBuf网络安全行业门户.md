##  前言

**2018年上半年，得益于Memcache近5万的反射放大倍数，DDoS的峰值流量已经达到了一个前所未有的新高度—1.7Tbps，这也使得Memcache
ReDDoS成为目前DDoS的中坚力量。而与Memcache ReDDoS相比，2016年Akamai曝光的CLDAP
ReDDoS虽然没有前者极高的效率，但是其56~70倍的放大倍数在DDoS家族中也依然是一名佼佼者，因此也应引起关注。**

##  一、CLDAP协议缺陷

轻量目录访问协议（LDAP）被定义在[RFC2251](https://tools.ietf.org/html/rfc2251)（LDAPv3）中，由于LDAP是以TCP字节流的方式进行数据传输，其必要的绑定操作和频繁的数据搜索查询会在一定程度消耗较多的TCP连接资源，于是IETF在1995年发布了面向无连接的轻量目录访问协议（CLDAP），官方文档为[RFC1798](https://tools.ietf.org/html/rfc1798)（2003年
[RFC3352](https://tools.ietf.org/html/rfc3352)将CLDAP置为历史状态）。在CLDAP中只提供三种操作：searchRequest、searchResponse
（searchResEntry和searchResDone）、abandonRequest，在不提供身份验证功能的情况下，客户端可以使用UDP数据报对LDAP服务器389端口发起操作请求。由于客户端发起searchRequest后服务端将返回searchResEntry和searchResDone两条应答消息，一般情况下执行该操作将具有较小数据包反射出较大数据包的效果，这一缺陷随即被利用进行反射放大DDoS攻击。

![](https://image.3001.net/images/20180823/15350096891137.png!small)

##  二、CLDAP Reflection DDoS的现状

根据Akamai SIRT发布的[报告](https://www.akamai.com/cn/zh/multimedia/documents/state-of-the-internet/cldap-threat-advisory.pdf)，目前捕获到的CLDAP
ReDDoS最高峰值流量为24Gbps，最大反射倍数为70倍。由于CLDAP未被广泛运用，开源LDAP软件openLDAP早已不再支持UDP协议的请求。事实上，目前进行CLDAP
ReDDoS攻击被利用最多的服务是Windows服务器的活动目录服务Active
Directory（AD）。通常AD服务会在TCP端口389上监听来自客户端的LDAP操作请求，同时也会在UDP端口389上使用CLDAP协议来等待执行rootDSE的搜索操作（rootDSE条目在AD服务配置时创建，且允许未经身份验证的客户端对服务器的配置状态、功能和扩展属性进行查询，也被称作“AD
ping”）。一些Windows服务器的AD服务监听端口暴露在公网，进而被利用来执行rootDSE查询产生放大反射DDoS攻击，在Exploit-DB上已经有安全研究者公开了[Perl利用脚本](https://www.exploit-db.com/exploits/40703/)：。使用Nmap的ldap-rootdse脚本也可以对该缺陷进行扫描确认：

    
    
    nmap -Pn -sSU 389,636 --script ldap-rootdse <target_ip>

![](https://image.3001.net/images/20180823/15350096989864.png!small)

可见存在缺陷的服务器将会返回rootDSE的条目、条目属性等配置信息。

##  三、对公开Payload的改进和探索

针对Exploit-DB中rootDSE CLDAP ReDDoS的利用脚本，其Payload为：

![](https://image.3001.net/images/20180823/15350097034722.png!small)

由于LDAP和CLDAP在传输数据时是先将数据封装成为LDAPmessage消息体后使用ASN.1下的BER进行编码后再传输的，我们可以使用在线工具[ASN.1
Playground](http://asn1-playground.oss.com/)对此Payload进行还原（还原时需先编译加载RFC2251中对LDAPmessage的ASN.1结构体定义，也可以直接使用GitHub中相关研究者定义好的[asn文件](https://github.com/Kampbell/ISODE/blob/37f161e65f11348ef6fca2925d399d611df9f31b/isode%2B%2B/code/iso/itu/osi/asn1/asn/Lightweight-Directory-Access-Protocol-V3.asn)）：

![](https://image.3001.net/images/20180823/15350097084489.png!small)

可以看出此Payload是一次searchRequest操作的BER编码，其对top类的objectClass必选属性进行查询。通过测试捕获，该Payload平均能达到50倍左右的反射放大效率：

![](https://image.3001.net/images/20180823/15350097154991.png!small)

但是如果将解码出的LDAPmessage再重新编码回去，会发现BER编码位数减少，与公开的Payload相比缺失了一部分：

![](https://image.3001.net/images/20180823/15350097201606.png!small)

如果此编码可用，将会降低Payload长度（需要在末尾再补一个\x00作为LDAPmessage结尾）：

![](https://image.3001.net/images/20180823/1535009724756.png!small)

通过与原Payload相比较，可以发现原来Payload多出的部分（\x30\x84…）其实上是一段LDAPmessage响应消息，因此在编码时被认为不应当出现在请求报文中，所以完全可以去掉（暂不清楚脚本原作者这里的意图）。测试捕获后发现，改进后的这段40字节的Payload可用，且可以将反射放大效率提升至平均73倍左右，相比UScert公布的56~70倍数据提升了近18%，目前在公开渠道也暂未找到更为精简的Payload：

![](https://image.3001.net/images/20180823/15350097285714.png!small)

事实上，要得到最精简的Payload，还是要回到协议本身。从RFC2251中可以看出searchRequest操作共有8个字段，而接收自定义字符输入的字段只有baseObject、filter、attributes三个。在上述40字节Payload基础上，我们能继续做文章的依然是filter字段和attributes字段。

![](https://image.3001.net/images/20180823/15350097325629.png!small)

经过构造filter和attributes字段，我们得到了长度为31字节的更为精简的Payload。该Payload能达到均值约89倍的反射放大效率，相比UScert公布的数据又提升了41%，如果以Akamai捕获到的最高反射数据包大小3662字节计算，新的Payload能达到最高118倍的反射放大倍数，这也将刷新目前已知的CLDAP
ReDDoS理论放大倍数：

![](https://image.3001.net/images/20180823/15350097367294.png!small)

##  四、影响面分析

我们在ZoomEye中通过搜索比较发现，存在缺陷的Windows服务器具有特定的banner信息：

    
    
    0\x84\x00\x00\x00\x10\x02\x01\x01a\x84\x00\x00\x00\x07\n\x01\x00\x04\x00\x04\x00

结合编码中的每一个标志位来看，该banner信息与LDAP服务器bindResponse响应报文编码十分相似，因此推断出现该banner信息的原因，是由于ZoomEye扫描引擎在扫描到存在缺陷的LDAP服务器时服务器做出了一次绑定操作的响应，且告知客户端绑定成功，这也是在客户端searchRequest之前的必要操作：

![](https://image.3001.net/images/20180823/15350097417031.png!small)

使用此banner规则在ZoomEye中搜索共有214673条记录，约占所有LDAP服务器总数411527的52.2%：

![](https://image.3001.net/images/20180823/15350097483251.png!small)

考虑到不同服务器在不同时间节点上会出现配置上的变动，于是我们以2015、2016、2017这三年作为区分，使用爬虫分别采集前1000条数据对服务器缺陷进行有效性验证。结果如下表所示：

![](https://image.3001.net/images/20180823/15350097621021.png!small)

按照得出的占比，可以估算出目前互联网中存在缺陷的服务器总数：

![](https://image.3001.net/images/20180823/15350097667878.png!small)

因此我们认为，目前互联网中至少有2万台Windows服务器正处于被利用进行CLDAP
ReDDoS攻击的风险之中，当然这仍然依赖于ZoomEye所提供的数据，真实情况可能有更多。同时，我们获取了这3000条数据中153台缺陷服务器的反射数据包，其中最大的数据包长度为3208字节，最小的数据包长度为1918字节，153个数据包平均包长度为2665字节。根据这些捕获到的数据，现阶段CLDAP
ReDDoS的反射放大倍数应当处于62~103倍之间，平均反射放大倍数为86倍左右。

![](https://image.3001.net/images/20180823/15350097705067.png!small)

##  五、总结

本文对CLDAP协议的缺陷及其造成反射放大DDoS攻击的现状进行了介绍，同时对目前已公开的攻击载荷Payload进行了探讨，并进一步探索出更精简的Payload，将CLDAP
ReDDoS反射放大倍数从平均50倍提升至86倍，最后借助ZoomEye对互联网中受影响的Windows服务器进行了统计与分析。当前的CLDAP
ReDDoS攻击主要是由于Windows服务器活动目录服务缺陷所引起，在防范上首先也应做到对389端口和636端口的限制，即确保端口不外漏或客户端IP白名单机制，更多关于LDAP服务器的安全实践也可以参考
[Best Practices in LDAP
Security](https://people.apache.org/~elecharny/ldapcon/Andrew%20Findlay-paper.pdf)。

 ***本文作者：斗象能力中心TCC-S4kur4，转载请注明来自FreeBuf.COM**

