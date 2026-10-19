## 0x00 序  

**每年iOS系统大版本升级，对于安全研究人员都是一次新的挑战。在大版本中，除了修补一些未经公开的漏洞外，苹果还会增加新的缓解机制，大大提高了整个越狱的难度。这不仅要求安全研究人员能够挖掘出可以独立提权的漏洞，还要能够攻破签名绕过和根目录读写这两道关卡。在iOS
12中，业界公开的解决方案都已经被苹果封堵。**

## 0x01 签名绕过（CodeSign Bypass）

在iOS中有非常严格的签名校验机制，所有发布的App均需要通过苹果颁发的证书进行签名之后才能上架。由于存在TeamID机制，即第三方动态库与宿主进程使用同一个证书签名，纵使通过漏洞利用完成提权后，依然无法运行未签名的binary，也无法注入代码到其他进程，因此需要绕过苹果的签名校验。在iOS11中，业界有两种公开的解决方案：

### (1). 劫持签名校验进程amfid（hijack amfid @i41nbeer）

iOS系统中通过AMFI的Mach
Message调用用户态进程amfid进行签名校验，其中MISValidateSignatureAndCopyInfo函数返回签名校验结果和CDHash（Code
Dictionary Hash）到内核。

在iOS 10以前，MISValidateSignature可以通过简单地返回一个布尔值完成绕过。iOS
10以后，MISValidateSignature*函数的返回值为字典。Google Project Zero的安全研究人员Ian
Beer提出的解决方案是通过劫持amfid的exception
handler，并把MISValidateSignatureAndCopyInfo函数指向一个无效地址，从而使得每次进行签名校验时amfid都会发生exception，最终回调到劫持的exception
handler。从回调函数中获取到binary信息并正确返回CDHash，通过整个校验逻辑。如图1-1所示。

![劫持amfid绕过签名简易流程图.png](https://image.3001.net/images/20180918/1537252891_5ba09e1be84f9.png!small)

图1-1 劫持amfid绕过签名简易流程图

在iOS12中，内核增加了CMS（Cryptographic Message
Syntax）校验，而业界常用的自签名工具ldid以及jtool中CMS都是为空的，导致上述解决方案失效。同时内核增加了CoreTrust模块用于对抗hardcoded证书，因此要伪造签名并通过苹果校验的难度大大提高。

### (2). 伪造签名授信缓存（fake trust cache @Xerub）

内核中AMFI使用trust cache快速校验ad-hoc的binary，它是一个链表式的数据结构，并且存放的位置不受限于KPP/AMCC的保护，提权完成之后可以在内核中找到这个结构体，插入自签名binary的CDHash绕过签名校验。

在iOS12中，已经无法从AMFI中找到trust cache chain了，他被存放在内核的const
data段中，这意味着无法对他进行修改。系统通过调用pmap_lookup_in_static_trust_cache进行校验。

然而当我们仔细研究AMFI中的签名校验逻辑时发现，内核中有2个trust cache chain，校验时分别对这两个trust
cache进行检索匹配，只要通过其中一个校验即可，虽然上述static trust cache
chain无法修改，但是另外一个依然可以修改！并且binary通过trust
cache的校验后，无需再进行CMS校验！苹果虽然尝试封堵这种绕过方式，但依然存在漏洞，导致新增加的缓解机制被轻松绕过。

## 0x02 根目录读写（Root Filesystem Read / Write）

在iOS中为了保障手机文件安全，即使进程拥有Root权限，依然无法修改Root Filesystem的内容。iOS 11.3对Root
Filesystem有过加强，从而令重新挂载Root Filesystem后，修改Root Filesystem会触发内核panic。在iOS
11.3后根目录读写的解决方案有两种：

### (1). 伪造有效的mnt_data（Xiaolong Bai and Min (Spark) Zheng @ Alibaba Security
Lab）

在iOS 11.3中，即使把RDONLY的标志去掉使Root
Filesystem能被挂载为可读写，但由于挂载的是一个只读的snapshot，并且snapshot中的mnt_data
不包含有效的extent结构，因此修改Root Filesystem会触发内核panic。那解决的方案自然是将snapshot
remount的mnt_data替换为一个有效的mnt_data。苹果在iOS
12的APFS中进一步加强了对mnt_data合法性的校验，用上述方法直接替换会触发内核OOM Panic。

### (2). 删除/dev/disk0s1s1 snapshot （cererdlong and eakerqiu @ Alibaba Pandora
Lab）

对于snapshot的另一种解决方案是直接删除。通过删除/dev/disk0s1s1的snapshot，使得reboot时系统无法加载对应的snapshot，最终被迫系统使用真实的/dev/disk0s1s1进行mount。

虽然苹果在内核有对fs_snapshot_delete进行校验，无法将正在使用的snapshot直接删除，但却没有对fs_snapshot_rename进行校验。因此可以对正在使用的snapshot改名！通过这个漏洞将snapshot改名后，reboot时系统找不到原本注册的snapshot，被迫使用真实的/dev/disk0s1s1进行mount。重启完成后，不仅可以直接将改名的snapshot删除，而且可以通过简单修改mount的mnt_flag直接mount
update根目录为可读写。

苹果在iOS 12的APFS对这个漏洞也进行修补，使得正在使用的snapshot无法被rename。尽管如此，依然有新的思路和方法可以挂载根目录为可读写。

## 0x03 结论

苹果在iOS 12中修复了很多未公开的漏洞，增加了新的缓解机制，但在iOS 12正式版发布的数小时内，潘多拉实验室完成了iOS
12的完美越狱，如图3-1和3-2所示。从技术的角度来看，完美越狱和非完美越狱的主要区别在于重启过程中是否能自动执行越狱代码，在手机重启完成前完成越狱。

![技术稿-iOS12内核控制PC.PNG](https://image.3001.net/images/20180918/1537252935_5ba09e472765b.png!small)![技术稿-iOS12内核控制PC_.png](https://image.3001.net/images/20180918/1537253048_5ba09eb8d7571.png!small)

图3-1&3-2 iOS 12控制内核PC完成越狱并安装Cydia

## iOS 12完美越狱视频演示

## 0x04 参考文献

> 1\. MacOS and *OS Internals <http://newosxbook.com/>
>
> 2\. Mach portal <https://bugs.chromium.org/p/project-> zero/issues/detail?id=965>
>
> 3\. extra_recipe <https://github.com/xerub/extra_recipe>
>
> 4\. iOS jailbreak internals (1): Remount rootfs after iOS 11.3
> <https://media.weibo.cn/article?id=2309404245794218721506>

***本文作者：阿里安全技术，转载请注明来自FreeBuf.COM**

