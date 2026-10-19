![](https://image.3001.net/images/20191101/1572611111_5dbc2427f0436.jpg!small)

## 写在前面的话

 **在这篇文章中，我们将告诉大家如何使用活动目录服务接口（ADSI）并结合C/C++来实现Cobalt
Strike的活动目录枚举。现在很多环境下都会对PowerShell和.NET程序进行非常严格的监视，而本文所介绍的技术也许可以帮你们躲避这些机制的检测。**

想象一下，你现在正在使用TIBER-EU、CBEST其他红队安全评估框架，最终成功渗透进了目标网络，并且使用Payload和C2信道成功绕过了目标网络的安全防护措施，那么接下来该怎么办呢？比如说，怎么确保我们的活动目录枚举工具不触发安全警报呢？

别着急，我们一起往下看！

## C/C++

如果使用传统的PowerShell/C#的话，就可能需要将写好的脚本放置到目标设备的磁盘中，而这样就有可能被安全产品检测到。这里，我们可以选择使用assembly.load等方法直接将工具加载到内存中，而C/C++正好可以帮我们实现类似的功能。这里，我们可以使用反射方法来将已编译好的C/C++恶意程序注入到目标设备的内存之中，下面给出的是目前几种比较热门的方法：

> 1、[ _DonutPE加载器_](https://github.com/TheWover/donut)（[
> _参考资料_](https://modexp.wordpress.com/2019/06/24/inmem-exec-dll/)）
>
> 2、反射型DLL注入（[
> _原始版本_](https://github.com/stephenfewer/ReflectiveDLLInjection)）（[
> _改进版本_](https://github.com/dismantl/ImprovedReflectiveDLLInjection)）
>
> 3、[ _Shellcode反射型DLL注入_](https://github.com/monoxgas/sRDI)

## 活动目录服务接口（ADSI）

好了，我们回到正题上，也就是如何实现活动目录的枚举。我们希望在枚举AD信息的时候不会触发AMSI或者是不留下明显的事件日志（可以通过伪造事件日志的内容来实现），要与活动目录进行对接并枚举其对象属性，我们需要使用到活动目录服务接口（ADSI）。

### 活动目录接口（ADSI）介绍

ADSI，即活动目录服务接口（ActiveDirectoryServicesInterface），是Microsoft新推出的一项技术，它统一了许多底层服务的编程接口，程序员可以使用一致的对象技术来访问这些底层服务。ADSI把这些服务的公共部分提取出来，同时隔离出相异的部分，程序员可以用统一的接口访问底层服务的公共部分，并延伸到底层服务的专有部分。ADSI提供了一组COM接口，可以用来访问来自不同网络提供商的目录服务功能，独立软件供应商和开发人员可以使用ADSI对其产品和应用程序进行目录启用。

非常好，那么我们的重点就要放在如何通过C/C++来构建自己的活动目录枚举工具了。在这里，我们其实不需要自己去重复造轮子了，因为微软的GitHub库已经给我们提供了一份非常优秀的参考样例-QueryUsers，我们可以使用这个样例来开发我们自己的客户端了。

## QueryUsers

> QueryUsers：【[ _GitHub传送门_](https://github.com/microsoft/Windows-classic-> samples/tree/master/Samples/Win7Samples/netds/adsi/activedir/QueryUsers/vc)】

QueryUsers可以在活动目录域这个实现分区查询，并且可以指定过滤器匹配的用户对象，该工具使用了IDirectorySearch来实现搜索功能的执行。

在QueryUsers的帮助下，我们可以搜索特定用户或所有用户，并返回所有标识用户的所有属性。QueryUsers的工作机制如下：

> 1、ADSI是基于COM构建的，因此我们需要使用CoInitialize()函数在程序内初始化COM；
>
> 2、我们需要使用ADsOpenObject()对[
> _LDAProotDSE_](https://ldapwiki.com/wiki/RootDSE)进行绑定，因此我们可以收集有关活动目录的信息，并使用返回的IADsCOM对象来获取[
> _defaultNamingContext_](https://docs.microsoft.com/en-> us/windows/win32/adsi/rootdse)信息；
>
> 3、获取到[ _defaultNamingContext_](https://docs.microsoft.com/en-> us/windows/win32/adsi/rootdse)之后，我们可以再次使用ADsOpenObject()来对Domain容器进行绑定，它将返回[
> _IDirectorySearch_](https://docs.microsoft.com/en-> us/windows/win32/api/iads/nn-iads-> idirectorysearch)COM接口，而该接口可以用来对活动目录进行查询和搜索；
>
>
> 4、在调用FindUsers()函数时，它将基于函数参数和以下字符串构造一个LDAP过滤器-“(&(objectClass=user)(objectCategory=person)%s)”。如果我们为改程序提供以下搜索过滤器参数“(sAMAccountName=Administrator)”，那么我们的LDAP过滤器实则为(&(objectClass=user)(objectCategory=person)
> (sAMAccountName=Administrator))”；
>
> 5、使用ADS_SEARCHPREF_INFO结构体作为搜索参数的首选项；
>
> 6、执行IDirectorySearch对象中的ExecuteSearch()方法，该方法将根据我们的 LDAP 过滤器返回所有结果；
>
> 7、最后，使用GetFirstRow()、GetNextColumnName()、GetColumn()和
> GetNextRow()方法遍历结果，并输出特定的用户属性；

## 集成到常用的C2框架&PoC

Cobalt Strike具有用于代码/DLL注入的多种功能选项，并且嵌入有功能非常强大的脚本语言支持，因此开发人员可以根据自己的需要来扩展Cobalt
Strike的功能。

为了验证该技术的可行性，我们开发了一种基于ADSI和反射型DLL的活动目录枚举工具，该工具可以直接在Cobalt
Strike中使用。我们的PoC工具名叫Recon-AD，该工具目前由其中反射型DLL以及对应的AggressorScript脚本构成。

其主要功能如下：

> 1、Recon-AD-Domain: 查询域信息（包括域名、GUID、站点名称、密码策略、域控列表等）；
>
> 2、Recon-AD-Users: 查询用户对象和相应的属性；
>
> 3、Recon-AD-Groups: 查询组对象和相应的属性；
>
> 4、Recon-AD-Computers: 查询计算机对象和相应的属性；
>
> 5、Recon-AD-SPNs: 查询配置了服务主体名称（SPN）的用户对象并显示有用的属性；
>
> 6、Recon-AD-AllLocalGroups: 在计算机是上查询所有本地组和组成员；
>
> 7、Recon-AD-LocalGroups: 在计算机上查询特定的本地组和组成员（默认 Administrators 组）；

广大研究人员可以自行从本项目的[ _GitHub库_](https://github.com/outflanknl/Recon-AD)中下载[
_Recon-AD_](https://github.com/outflanknl/Recon-AD)，并在Cobalt
Strike中加载相应的脚本来完成自己的任务。

## 工具运行截图

使用Recon-AD-Domain显示本地机器的域信息：

![](https://image.3001.net/images/20191101/1572611175_5dbc246741c09.png!small)

使用Recon-AD-Groups Domain Admins命令枚举域管理员组的属性信息：

![](https://image.3001.net/images/20191101/1572611179_5dbc246bae217.png!small)

使用Recon-AD-User username命令输出指定用户的属性信息：

![](https://image.3001.net/images/20191101/1572611185_5dbc24719d6fa.png!small)

## 总结

在这篇文章中，我们较少了关于活动目录服务接口（ADSI）的相关内容，并描述了如何将其与C/C++以及Cobalt Strike结合来实现活动目录的枚举。

 *** 参考来源：[ _outflank_](https://outflank.nl/blog/2019/10/20/red-team-tactics-active-directory-recon-using-adsi-and-reflective-dlls/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

