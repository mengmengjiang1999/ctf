# CVE-2020-7454：Libalias库中的越界访问漏洞

阅读量 **249939**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-07-02 15:30:24

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Lucas Leong，文章来源：thezdi.com

原文地址：<https://www.thezdi.com/blog/2020/6/29/cve-2020-7454-killing-two-systems-with-one-bug-in-libalias>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01e84fb49ac0cefd14.jpg)

## 0x00 绪论

2020年2月初，ZDI收到一份报告，报告中描述了Oracle
VirtualBox所使用的libalias数据包别名库中的越界访问漏洞。报告人是研究者Vishnu Dev
TJ，修复后分配的编号是[CVE-2020-7454](https://www.freebsd.org/security/advisories/FreeBSD-SA-20:12.libalias.asc)。分析报告时，我发现漏洞也存在于FreeBSD，本文将讨论VirtualBox和FreeBSD中的CVE-2020-7454漏洞，展示维护第三方库以及共享代码之难。

对于不熟悉libalias库的人，这里简要介绍一下。libalias是用于IP数据包[别名与解别名](https://www.kernel.org/doc/html/latest/networking/alias.html)（aliasing
and de-aliasing）的一个库，此外还用于地址伪装和NAT。既然有地址伪装和NAT的功能，就不难理解为何VirtualBox要使用这个库。不过，libalias源自FreeBSD，VirtualBox方面则维护着自己的libalias分支。不幸的是，本漏洞在两个版本上都有。它会导致FreeBSD内核模式和用户模式的越界访问。漏洞在VirtualBox
6.1.6和FreeBSD-SA-20:12中修复。

## 0x01 考察Oracle VirtualBox

以下分析基于VirtualBox 6.1.4。漏洞的根源在`AliasHandleUdpNbtNS()`函数中，该函数负责解析UDP
137端口上的NetBIOS名字服务数据包。以下是简化的相关代码：

    
    
    AliasHandleUdpNbtNS(...) 
        { 
            /* ... 略 ... */
    
            /* 计算UDP包数据长度 */ 
            uh = (struct udphdr *)ip_next(pip); 
            nsh = (NbtNSHeader *)udp_next(uh); 
            p = (u_char *) (nsh + 1); 
            pmax = (char *)uh + ntohs(uh->uh_ulen); /* <--- (1) */  
    
            /* ... 略 ... */
            if (ntohs(nsh->ancount) != 0) { 
                p = AliasHandleResource( 
                    ntohs(nsh->ancount), 
                    (NBTNsResource *) p, 
                    pmax, 
                    &nbtarg 
                    ); 
            } 
            /* ... 略 ... */
        } 
    AliasHandleResource(..., char *pmax, ...) 
        { 
            /* ... 略 ... */
                switch (ntohs(q->type)) { 
                case RR_TYPE_NB: 
                    q = (NBTNsResource *) AliasHandleResourceNB( 
                        q, 
                        pmax, 
                        nbtarg 
                        ); 
                    break; 
            /* ... 略 ... */ 
        }
    

在上面代码的(1)处，`uh_ulen`是UDP首部长度字段，是从不可信的客户机发来的，其最大值为0xFFFF。如果把uh_ulen的值设得很大，攻击者就可以产生过大的`pmax`值。而后，如果UDP包中含有应答资源记录（Answer
Resource Records），且类型为NetBIOS通用服务（NetBIOS General
Service），则执行会进入`theAliasHandleResourceNB()`函数：

    
    
    AliasHandleResourceNB(..., char *pmax, ...) 
    { 
        /* ... 略 ... */
        while (nb != NULL && bcount != 0) { 
            if ((char *)(nb + 1) > pmax) { /* <--- (2) */
                nb = NULL; 
                break; 
            } 
            if (!bcmp(&nbtarg->oldaddr, &nb->addr, sizeof(struct in_addr))) { /* <--- (3)  /
                /* ... 略 ... */ 
                nb->addr = nbtarg->newaddr; /* <--- (4) */
            } 
            /* ... 略 ... */
            nb = (NBTNsRNB *) ((u_char *) nb + SizeOfNsRNB); 
        } 
    }
    

在上面代码的(2)处，`while`循环试图寻找包中的旧地址，将其替换为新地址，直到`pmax`为止。因为`pmax`的值过大，所以(3)处发生了越界读。如果旧地址找到的话，在(4)处甚至可能越界写。

客户机上的攻击者可以构造不合理的UDP首部长度，以在主机上触发越界访问。UDP端口137在VirtualBox的默认配置下是打开的。为解决此问题，Oracle在上面第一份代码的(1)处[加入了](https://www.virtualbox.org/changeset/83597/vbox)UDP首部长度验证。

## 0x02 考察FreeBSD 12.1

如上所述，libalias库源自FreeBSD。分析Oracle
VirtualBox中的此漏洞时，我发现在使用`ipfw`做NAT时，此漏洞还影响到FreeBSD。`ipfw`包过滤器包含两种NAT方法：一种在内核，一种在用户空间。两种实现用的都是libalias提供的同一个函数。这就表示漏洞可在内核或者用户空间程序（`natd`）中触发，具体在哪取决于[NAT配置](https://www.freebsd.org/doc/handbook/firewalls-ipfw.html)。

以下是触发内核中的漏洞所需的FreeBSD 12.1相关配置：

    
    
    /boot/loader.conf 
     alias_nbt_load="YES" 
    /etc/rc.conf 
     gateway_enable="YES" 
     firewall_enable="YES" 
     firewall_nat_enable="YES" 
     firewall_nat_interface="em0" 
     firewall_type="OPEN"
    

越界访问发生在`alias_nbt.ko`中，这是已加载进内核的模块。

如果NAT配置是在用户空间的话，越界访问发生在`natd`进程的`libalias_nbt.so`中。这两种情况都可以远程触发，无需身份认证。

分析中我还发现一个惊喜。FreeBSD中的libalias包含这个漏洞的另一个变体，位于对[CuSeeMe](https://en.wikipedia.org/wiki/CU-SeeMe)协议的处理过程中，这个协议默认监听UDP端口7648。

    
    
    AliasHandleCUSeeMeIn(...) 
    { 
        /* ... snip ... */
        end = (char *)ud + ntohs(ud->uh_ulen); /* <--- untrusted UDP header length */
        if ((char *)oc <= end) { 
            /* ... snip ... */
            if (ntohs(cu->data_type) == 101) 
            /* Find and change our address */ 
            for (i = 0; (char *)(ci + 1) <= end && i < oc->client_count; i++, ci++) 
            if (ci->address == (u_int32_t) alias_addr.s_addr) { /* <--- OOBR */
                ci->address = (u_int32_t) original_addr.s_addr; /* <--- OOBW */
                break; 
            } 
        } 
    }
    

然而，这个漏洞不存在于VirtualBox中，所以对FreeBSD的[补丁](https://www.freebsd.org/security/advisories/FreeBSD-SA-20:12.libalias.asc)和VirtualBox的补丁会有所不同。在`UdpAliasIn()`和`UdpAliasOut()`中都加入了验证，这里是处理UDP包的合适的层次，这样就把任何包含这种漏洞的协议都修补了。

## 0x03 总结

这次案例分析展示了维护第三方库以及共享代码何其之难。即使源代码打了补丁或者更新了，这些改动还必须反映到上游产品之中。就算你和第三方的代码同步了，共享代码里的一个漏洞反而会有双倍的影响，因为使用共享代码的双方都受到影响。Oracle
VirtualBox在用户和安全研究者中越来越受欢迎。再次感谢Vishnu Dev
TJ报告此漏洞和其他VirtualBox漏洞。我们期望在未来收到他的更多报告。

本文翻译自thezdi.com
[原文链接](https://www.thezdi.com/blog/2020/6/29/cve-2020-7454-killing-two-systems-with-one-bug-in-libalias)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **hx1997** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/209537](/post/id/209537)

安全客 - 有思想的安全新媒体

本文转载自:
[thezdi.com](https://www.thezdi.com/blog/2020/6/29/cve-2020-7454-killing-two-systems-with-one-bug-in-libalias)

如若转载,请注明出处： <https://www.thezdi.com/blog/2020/6/29/cve-2020-7454-killing-two-systems-with-one-bug-in-libalias>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [CVE-2020-7454](/tag/CVE-2020-7454)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t01c4d2c10c5886a436.png) hx1997

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

