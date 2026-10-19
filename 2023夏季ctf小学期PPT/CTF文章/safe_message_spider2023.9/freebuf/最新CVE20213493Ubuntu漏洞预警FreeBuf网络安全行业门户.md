**一. CVE-2021-3493简介**

 **OverlayFS漏洞允许Ubuntu下的本地用户获得root权限。**
Linux内核中overlayfs文件系统中的Ubuntu特定问题，在该问题中，它未正确验证关于用户名称空间的文件系统功能的应用程序。由于Ubuntu附带了一个允许非特权的overlayfs挂载的补丁，因此本地攻击者可以使用它来获得更高的特权。

目前漏洞细节已公开，请受影响的用户尽快采取措施进行防护。

 **二. 影响版本**

Ubuntu 20.10

Ubuntu 20.04 LTS

Ubuntu 18.04 LTS

Ubuntu 16.04 LTS

Ubuntu 14.04 ESM

 **三. 漏洞分析**

Linux支持存储在扩展文件属性中的文件功能，它们的工作方式类似于setuid-bit，但粒度更细。在伪代码中设置文件功能的简化过程如下:

![图片](https://image.3001.net/images/20210422/1619054846_6080d0fedb1882d47e704.jpg!small)

重要的调用是cap_convert_nscap，它检查与名称空间相关的权限。

如果我们从自己的名称空间和挂载上设置文件功能，就不会有问题，而且我们有权限这样做。但当OverlayFS将此操作转发给底层文件系统时，它只调用vfs_setxattr，并跳过cap_convert_nscap中的检查。

这允许在外部命名空间/mount中的文件上设置任意功能，并且在执行过程中应用。

在Linux 5.11中，对cap_convert_nscap的调用被移到了vfs_setxattr中，攻击很难实现。

 **四. 漏洞利用**

测试环境：Ubuntu 18.04 LTS

本地用户登录系统，运行POC。

 **五. 防御建议**

![图片](https://image.3001.net/images/20210422/1619054858_6080d10ac58934702e076.jpg!small)

更新系统软件包版本。详细版本信息请参考供应商的安全公告。

https://ubuntu.com/security/notices/USN-4915-1  
https://ubuntu.com/security/notices/USN-4916-1  
https://ubuntu.com/security/notices/USN-4917-1

 **六. 参考链接**

> https://ubuntu.com/security/CVE-2021-3493
>
> https://ssd-disclosure.com/ssd-advisory-overlayfs-pe/

![图片](https://image.3001.net/images/20210422/1619054866_6080d112915f373eb0d42.jpg!small)

