**COVID-19使许多公司员工利用RDP远程桌面办公，员工可以远程访问公司内部资源，远程与系统进行通信。为了维持业务连续性，许多组织对安全的要求降低，使攻击者有机可乘。**

RDP是运行在3389端口上的Microsoft协议，用户可远程访问内部系统。多数情况下，RDP运行在Windows服务器上，并承载部分服务，例如Web服务、文件服务等，它也可以连接到工业控制系统。RDP端口通常暴露于Internet，非法访问可使攻击者访问整个网络，并用作传播恶意软件的入口。

## RDP统计

暴露在Internet的RDP端口数量迅速增长，从2020年1月的大约300万到3月已超过450万。 在Shodan上搜索RDP端口数量结果如下图：

![image.png](https://image.3001.net/images/20200509/1589000103_5eb637a72769b.png!small)![image.png](https://image.3001.net/images/20200509/1589000123_5eb637bb325c2.png!small)

中国和美国暴露在互联网的RDP数量远超其他国家地区。大多数受感染系统都运行Windows Server，也有部分是其他操作系统，例如Windows 7。

![image.png](https://image.3001.net/images/20200509/1589000238_5eb6382e1c3bd.png!small)

对于攻击者而言，访问远程系统可以进行许多恶意操作，例如：

> 1、传播垃圾邮件：使用合法系统发送垃圾邮件非常方便。  
>
>
> 2、传播恶意软件：利用被攻陷的系统可以轻松传播恶意软件，渗透到内部网络。
>
> 3、单独使用受感染的机器：网络犯罪分子使用受感染的系统隐藏自身踪迹，例如在受感染计算机上编译工具。
>
> 4、还可以用于其他诈骗行为，例如身份盗用或个人信息收集。

近期针对RDP端口的攻击数量以及暗网在售的RDP凭证数量均在增加。

![批注 2020-05-09
130252.png](https://image.3001.net/images/20200509/1589000690_5eb639f288a5e.png!small)![批注
2020-05-09
130252.png](https://image.3001.net/images/20200509/1589000747_5eb63a2b8bdbb.png!small)中国（占总数的37％）和美国（占总数的37％）的系统数量最多，美国（占4％）的RDP凭证被盗数比其他国家要低得多。  

![image.png](https://image.3001.net/images/20200509/1589000875_5eb63aab779b5.png!small)

## 攻击者如何攻击远程系统？

弱密码仍然是常见的切入点之一，攻击者可以使用暴力攻击获得访问权限。 下图可看到RDP中20个最常用的密码。

![image.png](https://image.3001.net/images/20200509/1589001045_5eb63b557bbbf.png!small)下图显示了前10位常见密码的数量，大量易受攻击的RDP没有密码。  

![image.png](https://image.3001.net/images/20200509/1589001119_5eb63b9fed091.png!small)

RDP协议还存在一些需要修补的漏洞，去年详细说明了BlueKeep漏洞的工作原理，该漏洞允许攻击者远程执行代码。

> <https://www.mcafee.com/blogs/other-blogs/mcafee-labs/rdp-stands-for-really-> do-patch-understanding-the-wormable-rdp-vulnerability-cve-2019-0708/>  
>

一月初，还修复了远程桌面有关的其他漏洞：  

> <https://portal.msrc.microsoft.com/zh-CN/security-> guidance/advisory/CVE-2020-0609>  
>
>
> <https://portal.msrc.microsoft.com/zh-CN/security-> guidance/advisory/CVE-2020-0610>

这两个漏洞类似于BlueKeep漏洞，攻击者可发送特制的请求远程执行代码。

为了RDP协议的安全，需要进行以下操作：

> 1、不允许通过公开Internet进行RDP连接  
>
>
> 2、使用复杂密码以及多因素身份验证
>
> 3、锁定用户，阻止登录失败次数过多的IP
>
> 4、使用RDP网关
>
> 5、限制域管理员帐户访问权限
>
> 6、减少本地管理员的数量
>
> 7、使用防火墙限制访问
>
> 8、启用限制管理员模式
>
> 9、启用网络级别身份验证（NLA）
>
> 10、确保本地管理员帐户唯一，限制可以使用RDP登录的用户
>
> 11、不使用含有组织信息的帐户  
>

## 总结

网络犯罪分子正在瞄准RDP，它仍然是入侵组织的最常用的媒介之一。
对于攻击者来说，RDP入口可以快速有效的开展恶意活动，例如传播恶意软件，垃圾邮件或进行其他类型的犯罪。  

目前，暗网上有整套围绕RDP开展的业务，为了使自身不受到攻击，必须遵循安全原则，例如使用强密码、修补漏洞等。

 ***参考来源：[mcafee](https://www.mcafee.com/blogs/other-blogs/mcafee-labs/cybercriminals-actively-exploiting-rdp-to-target-remote-organizations/)，由Kriston编译，转载请注明来自FreeBuf.COM**  

