***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **几个月前，作者曾写过一篇关于攻击ADIDNS的[文章](https://blog.netspi.com/exploiting-adidns/)。这篇文章中主要讨论ADIDNS攻击端和防御端的额外技术。**  

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152808_5c83f8e8822d7.png!small)

## WPAD是什么？

Web代理自动发现（WPAD）是[LLMNR和NBNS欺骗](https://github.com/Kevin-Robertson/Inveigh)过程中的常见目标。WPAD乍看之下跟ADIDNS中的其他记录没什么太大区别，如果ADIDNS默认没有这条记录的话，认证用户可以直接添加这个记录。

如果你添加了一条WPAD记录，你将会发现它[没有任何的作用](https://room362.com/post/2016/05-22-wpad-persistence/)。这是由于GQBL（全局查询屏蔽列表）所导致的，默认情况下该列表中包含了WPAD和ISATAP。

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152819_5c83f8f3d8ce9.png!small)

现代Windows DNS服务器通常不会响应来自GQBL列表中主机的域名查询请求。为什么我这里用了“通常”这个词呢？这是因为GQBL并不是永远有效的。

## 绕过GQBL

我在尝试使用通配符记录时，我发现Windows
DNS服务器忽略了GQBL并使用通配符响应了对WPAD请求。目前为止，我还没有开始使用LDAP，我只能通过动态更新来添加记录。由于'*'字符不适用于动态更新，因此我打算找到能够与动态更新配合使用的GQBL绕过方法。

我发现的第一个方法是利用DNAME记录。如果DNS域中存在“WPAD”的DNAME记录，那么Windows DNS服务器就可以解析WPAD了。

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152832_5c83f9007d69f.png!small)

一般来说，DNAME记录不会解析与实际记录相匹配的请求，DNS服务器只会响应映射域中主机的请求，例如“host.wpad.inveigh.net”。此时，'wpad.inveigh.net'的root记录可以正常解析。

奇怪的是，我发现Windows
DNS服务器在满足某些条件时会响应DNAME记录的root请求。这种记录需要匹配GQBL中的主机且GQBL要处于启用的状态。对于WPAD来说，默认开启GQBL可能会更加危险。但是，我无法使用DNAME记录来处理动态更新。所以我得寻找另一种绕过的方法。随后，我发现了一种为WPAD子域名添加NS记录的方法。

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152841_5c83f909815e1.png!small)

这种方法比较复杂，因为需要设置NS记录指向一台可控制的DNS服务器。不过使用Kali自带的DNSchef是一种设置DNS服务器来提供应答接收的请求的简单方法。

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152851_5c83f91311211.png!small)

但此时我仍然无法使用动态更新完成绕过，不过在选择使用LDAP后，一切都变得明朗了。

## CVE-2018-8320

我在发现了这个问题之后，便立刻将研究成果提交给了微软，微软方面也为该漏洞分配了CVE编号（CVE-2018-8320），并发布了漏洞修复补丁。下面是我在修复漏洞后的系统上测试的结果。

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152865_5c83f92122375.png!small)

通配符记录已不再解析GQBL列表中主机的请求了：

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152873_5c83f9298a90d.png!small)

DNAME记录已不再解析GQBL列表中主机的请求了：

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152895_5c83f93f2727e.png!small)

但是正如你所看到的那样，NS记录仍然可以绕过GQBL。

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152911_5c83f94f708c4.jpg!small)

## 域名后缀搜索顺序

此前我曾建议使用管理员控制的通配符记录来预防ADIDNS通配符攻击和LLMNR /
NBNS欺骗攻击。但也有研究人员指出，当通过组策略将多个域名后缀分配给搜索列表时，通配符记录可能会存在问题。

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152925_5c83f95db0c08.png!small)

测试之后，我也验证了他们的说法。当我把通配符设置在较高级别域名后缀的DNS区域中，如果匹配到了有效记录，系统将阻止有效请求降级解析到任何较低级别的域名后缀。

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152941_5c83f96dd1382.png!small)

而这种情况就导致了一种新型攻击技术的诞生。这样一来，我们就可以定位对现有记录的请求，而不是在DNS区域中定位不存在的记录。如果可以将记录添加到域名后缀的DNS区域，我们就可以在任何低优先级的域名后缀中定位有效主机了。对目标主机的非完全有效请求将全部由你所添加的记录来响应。

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152952_5c83f9782e21f.png!small)

需要注意的是，在执行通配符攻击时应考虑到DNS后缀。如果你发现具有多个DNS后缀的搜索列表，那么在注入除了列表中最后一个DNS区域之外的任何记录时，通配符攻击将有可能发生中断。

## 通过钓鱼实现ADIDNS攻击

在实现LLMNR/NBNS欺骗时，欺骗攻击工具必须持续运行。但是，ADIDNS攻击只需要一些初始化操作就可以完成。因此，我认为通过网络钓鱼更容易实现ADIDNS攻击。此时，只需要一个连接至钓鱼目标的AD即可执行Payload，目的是为了添加可以向远程攻击者控制的系统发送流量的记录，你可以将这些记录用于C2服务器或进行其他的网络钓鱼攻击。

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152967_5c83f9878f9b1.png!small)

上图是我自己开发的PowerShell工具，我添加了一条指向公共IP的记录，实际攻击场景我们还可以使用更多的Payload。

这是另一个NS记录用于攻击的例子。一旦设置了NS记录，可以通过自己的DNS服务器来增加额外的记录到受控的子域名中。

## 浅谈ADIDNS防御

如上所述，如果你使用了具有多个DNS后缀的搜索列表，那么管理员控制的通配符A记录可能会存在安全问题。当然了，你也可以使用不会解析域名请求的记录类型（如TXT记录）来创建通配符。

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152978_5c83f99208214.png!small)

由于所有记录类型都存在dnsNode对象中，因此添加任何形式的通配符记录都会阻止非特权用户添加自己的名为“*”的dnsNode对象。不幸的是，不起解析作用的通配符记录不具有防御LLMNR和NBNS欺骗攻击的能力。

![利用ADIDNS绕过GQBL限制并解析WPAD域名](https://image.3001.net/images/20190310/1552152989_5c83f99d65f3e.png!small)

锁定DNS域权限是缓解认证用户ADIDNS攻击的最彻底的方法。根据设置，用户可能可以利用DHCP中的特定DNS动态更新账户。但是这可能需要你完全删除“已验证用户”下面的“创建所有子对象”权限。

许多域名解析攻击都是通过非完全有效的域名请求进行的。这类用户生成的请求很难消除。

 *** 参考来源：[netspi](https://blog.netspi.com/adidns-revisited/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

