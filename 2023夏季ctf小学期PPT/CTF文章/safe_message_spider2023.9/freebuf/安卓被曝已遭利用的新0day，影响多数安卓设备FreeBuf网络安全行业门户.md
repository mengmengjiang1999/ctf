**谷歌发现一个未修复的安卓0day已遭利用。该0day存在于安卓操作系统的内核代码中，可被攻击者用于获取设备的根权限。颇具讽刺意味的是，这个0day曾在2017年12月于安卓内核版本3.18、4.14、4.4和4.9中被修复，但新版本被指易受攻击。**

![android-0-day.png](https://image.3001.net/images/20191005/15702612627720.png!small)

##  **受影响设备**

谷歌研究人员认为该漏洞影响如下运行安卓8.x及后续版本的安卓手机型号。

> 安卓9和安卓10预览版 Pixel 2
>
> 华为P20
>
> 小米红米5A
>
> 小米红米Note 5
>
> 小米A1
>
> Oppo A3
>
> 摩托罗拉Z3
>
> Oreo LG系列手机
>
> 三星S7、S8、S9

研究人员表示，“利用需要很少或不需要每台设备自定义”，意味着它可适用于大量手机型号，尽管他们仅在上述受影响手机型号上通过手动审计验证了这一点。

##  **详情及PoC**

该漏洞的编号是CVE-2019-2215。它存在于android-msm-wahoo-4.4-pie分支中（也有可能存在于其它地方）。它是/drivers/android/binder.c的binder驱动中的binder_线程结构的wait
member函数释放后使用漏洞。

binder_poll()传递可休眠的线程->wait等待队列。当使用epoll的现成使用BINDER_THREAD_EXIT明确退出时，该等待队列被释放，但并未从相应的epoll数据结构中删除。当该进程随后退出时，epoll清理代码尝试访问等待列表，从容导致释放后使用后果。

如下PoC展示的是KASAN内核构建中的UAF崩溃。

    
    
    #include <fcntl.h>            
    #include <sys/epoll.h>            
    #include <sys/ioctl.h>            
    #include <unistd.h>            
    #define BINDER_THREAD_EXIT 0x40046208ul            
    int main()    
    {                    
    int fd, epfd;                    
    struct epoll_event event = { .events = EPOLLIN };                    
    fd = open("/dev/binder0", O_RDONLY);                    
    epfd = epoll_create(1000);                    
    epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &event);                   
    ioctl(fd, BINDER_THREAD_EXIT, NULL);            
    }
    

## **被指和NSO组织有关**

该漏洞是由谷歌Project
Zero团队发现的，随后由谷歌威胁分析团队(TAG)证实。这两个团队曾在上个月发现了影响iOS用户的14个0day漏洞。不过这个安卓0day和这14个iOS
0day之间似乎并不相关。前者的详情目前是有限的。

谷歌TAG团队认为这个安卓0day是以色列利用和监控工具的卖家NSO集团的手笔。该公司长久以来被指责向专制政权出售黑客工具，不过最近由于遭受的批评增多，该公司承诺会和滥用黑客工具监控无辜人员或反对党派人士的客户作斗争。

该公司否认了这个安卓0day出自他们之手。该公司的一名发言人表示，“NSO过去未出售今后也不会出售利用或漏洞。这个利用和NSO没有关系，我们主要开发旨在帮助受许可限制的情报和执法部门开发用于挽救生命的产品。”

##  **危险系数没那么高**

好在这个0day并不像之前的0day那样危险。它并非远程代码执行漏洞，也就并非无需用户交互就能遭利用的0day。攻击者利用这个漏洞前必须具备某些条件。研究员表示，“这个漏洞是一个本地提权漏洞，允许完全攻陷一台易受攻击的设备。如果该利用是通过Web传递的，需要和渲染器漏洞配对，因为该漏洞可通过沙箱访问。”

安卓开源项目的一名发言人表示，“这个问题被评为高危漏洞，但要利用需要安装一个恶意应用程序。任何其它向量如通过web浏览器要求和其它利用组成利用链。”

安卓团队表示，“我们已将问题告知安卓合作伙伴，补丁已存在于安卓通用内核(Common Kernel)中。Pixel 3和3a设备并不受影响，Pixel
1和2设备将在十月更新中收到更新。”

谷歌Project
Zero团队通常会给软件开发人员90天的期限来修复该漏洞，之后再发布详情和PoC利用代码，但鉴于该漏洞已遭在野利用，因此在收到漏洞报告7天后就将其公开。

 ***参考来源：[ZDNet](https://www.zdnet.com/article/google-finds-android-zero-day-impacting-pixel-samsung-huawei-xiaomi-devices/)，奇安信代码卫士编译，转载请注明来自FreeBuf.COM**

