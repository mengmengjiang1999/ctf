***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**近期，360企业安全集团代码卫士团队安全研究人员发现友讯(D-LINK)公司旗下产品系列DIR-619、DIR-605系列路由器的两个高危安全漏洞(CVE-2018-20056和CVE-2018-20057)，并第一时间向友讯(D-LINK)公司汇报，协助其修复漏洞。**  

DIR-605及DIR-619系列是友讯公司旗下的家用路由器产品。北京时间2019年1月4日，友讯(DLINK)公司发布了安全更新公告(<https://securityadvisories.dlink.com/announcement/publication.aspx?name=SAP10100>)，公开致谢360企业安全集团代码卫士团队，并且发布相应的补丁修复漏洞。

![1.png](https://image.3001.net/images/20190129/1548749755_5c500bbb3186a.png!small)![2.png](https://image.3001.net/images/20190129/1548749771_5c500bcbed057.png!small)

图 致谢360代码卫士

本次友讯公司修复的漏洞中，CVE-2018-20056是一个缓冲区溢出漏洞，本文将针对该漏洞进行技术分析。

![3.png](https://image.3001.net/images/20190129/1548749789_5c500bdd43846.png!small)

## 漏洞概述

###  **CVE-2018-20056**

该漏洞是一个无需授权的栈缓冲区溢出漏洞，影响D-LINK DIR-605L 300M wireless cloud routing和DIR-619L
300M wireless cloud routing型号。漏洞出现在 web
服务器中的一个功能接口中，可被未经验证的用户通过`post`请求进行调用。请求的URL为：http://[target_ip]/goform/formLanguageChange，其中`POST`数据的`currtime`参数未进行长度校验通过危险的内存拷贝函数写入栈上，导致精心构造的`currtime`参数可以触发缓冲区溢出漏洞，甚至直接获得设备的
rootshell。

## 技术分析

通过binwalk解包固件后分析系统文件目录，发现系统中存在boa程序。Boa程序是一个轻量级的web服务器程序。常见于嵌入式系统中。通过逆向分析发现此程序在boa开源代码的基础上新增了很多功能接口以实现路由器上的不同功能。

其中大部分功能接口都需要经过身份验证后才可以使用，但仍旧存在少部分功能接口如登录注销等可以使用。通过逆向分析boa程序定位至`process_header_end`函数，可以找到未验证用户可使用的部分功能。其中部分关键代码如下，其判断流程可简单总结为,若`is_valid_user`函数判断请求来自于未验证用户后，
会再次通过`strstr`函数判断url请求是否为此用户可使用的功能接口。
通过分析及实验发现，除了login功能外，未验证用户还可以使用formlanguagechange功能接口来改变web前台界面显示的语言。

![4.png](https://image.3001.net/images/20190129/1548749851_5c500c1bc8139.png!small)![5.png](https://image.3001.net/images/20190129/1548749865_5c500c292a8c5.png!small)

接下来通过定位分析分发函数`websaspinit`寻找进入此函数的方式，关键代码如下：

![6.png](https://image.3001.net/images/20190129/1548749888_5c500c400aec1.png!small)

通过分析实验发现，在`post`请求访问http://[target_ip]/goform/formLanguageChange时会进入`formLanguageChange`函数流程，函数中通过`websgetvar`函数获取`post`请求中`config.i18n_language`，`currtime`，`nextpage`参数的值。

在`websgetvar`函数中，通过`strlen`、`malloc`、`memcpy`函数将参数值保存至申请出的一块内存空间中，但并未对参数长度进行判断和限制。这种参数获取的方式在遇到危险的内存拷贝函数时极易产生问题，是后面产生漏洞的根源所在。

![7.png](https://image.3001.net/images/20190129/1548749957_5c500c8570e78.png!small)

图 websgetvar函数

继续分析`formLanguageChange`函数，程序将获取到的`currtime`参数值直接通过危险函数`sprintf`写入栈上`0x110-0xf8`的位置导致了缓冲区溢出。

通过分析， 函数返回地址保存在`0x110-0x4`位置，即当参数长度大于`0xf4`时会直接覆盖函数返回地址，导致程序控制流被劫持。

![8.png](https://image.3001.net/images/20190129/1548749975_5c500c972bea3.png!small)

图 formLanguageChange函数

结合路由器环境本身防护机制的不足，在攻击者控制程序流程后，可通过rop技术实现任意代码执行。

Rop流程为：1.赋值`a0`参数。

2.调用`sleep`函数。

3.赋值某寄存器为栈上地址。

4.通过寄存器跳转的方式跳入栈中shellcode的位置完成利用。

![9.png](https://image.3001.net/images/20190129/1548749997_5c500cade0e4e.png!small)

图 利用结果

## 参考链接

<https://securityadv.isories.dlink.com/announcement/publication.aspx?name=SAP10100>

<https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-20056>

***本文作者：360代码卫士，转载请注明来自FreeBuf.COM**

