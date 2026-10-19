随着越来越多的组织向微服务/DevOps转型，容器生态系统每年都会发生很大的变化。近期，Sysdig发布了《2019年度容器使用报告》，报告中大篇幅的介绍了2019年容器生态下的安全现状问题。

报告基于2,000,000个运行于生产环境中的容器收集的真实数据，从多个角度，分析了这一年来，容器生态系统所发生的变化，样本数量几乎是去年（90,000）的22倍多。

相比较2018年的报告，今年的这个报告有以下几个特点：

（1）从题目上看，2018年之前的报告都是Docker年度使用报告，今年将Docker改为了Container，这也体现了在生态系统中容器运行时的广度有所扩大；

（2）样本数较去年增加了22倍多，所有的统计数据来源于线上客户真实的业务数据，这样的数据增长，说明在容器环境中的安全需求与安全建设发生了飞速的发展；

（3）报告中首次增加容器环境安全相关的现状数据。

下面本文将着重解读2019年容器环境的安全现状。

**1.Docker+K8S** **仍然是主流技术路线选择**

rkt、lxc、mesos等容器运行时已经几乎很少见，docker和containerd基本成为容器运行时的主流实现。

![https://mmbiz.qpic.cn/mmbiz_png/hiayDdhDbxUbhytMsHicFLbZbXEvjicLrmjpCCnf3oRibKjGDmfSUkes1fwk9icia3peNPXLg2uNf8BCUbRWWdMO9VQg/640?wx_fmt=png](https://image.3001.net/images/20191125/1574651832_5ddb47b86f24c.png!small)

在编排工具上，毫无悬念的Kubernetes占据了榜首，加上OpenShift以及Rancher，其占有比例达到了89%，Swarm从2018年的11%降到了5%。

![https://mmbiz.qpic.cn/mmbiz_png/hiayDdhDbxUbhytMsHicFLbZbXEvjicLrmjrCLhZpCc7YdhBqsvUex8a5ibvvfqQIPDZje846TA3TWggQdz6px3xLw/640?wx_fmt=png](https://image.3001.net/images/20191125/1574651839_5ddb47bfea368.png!small)

**2.** **镜像安全问题仍然突出**

在用户的生产环境中，有40%的镜像来源于公开的镜像仓库。

![https://mmbiz.qpic.cn/mmbiz_png/hiayDdhDbxUbhytMsHicFLbZbXEvjicLrmjgOQ7Moh56kGIiaic77fKzCY6fDx6FAxbYsBcLvbUsSKPjEUZpUibHn5ibA/640?wx_fmt=png](https://image.3001.net/images/20191125/1574651852_5ddb47ccc2920.png!small)

镜像的漏洞问题依然十分突出，连续5天对应用到生产环境中的镜像进行漏洞扫描，通过率仅为48%。

![https://mmbiz.qpic.cn/mmbiz_png/hiayDdhDbxUbhytMsHicFLbZbXEvjicLrmjVOSB11lwuHsfsZQP96ibQ2SHiceiawt5L3q7NDIG5VXq7hhiaIbQ8hPRMQ/640?wx_fmt=png](https://image.3001.net/images/20191125/1574651860_5ddb47d44d4f2.png!small)

 **3.** **安全配置规范应用情况不理想**

CIS等安全配置规范，在生产环境中落实情况并不是很理想，主要体现在禁用了seccomp、没有设置SELinux、AppArmor、以root/特权模式运行等问题。

![https://mmbiz.qpic.cn/mmbiz_png/hiayDdhDbxUbhytMsHicFLbZbXEvjicLrmjeIicqfZdkdKonAFgAFGHdJycicUhOHZhm8kz6IKIoOdibiaVmAYscuRg2w/640?wx_fmt=png](https://image.3001.net/images/20191125/1574651865_5ddb47d944afe.jpg!small)

 **4.** **运行时安全**

通过Falco的监控，运行时安全威胁Top10主要体现在了写/etc目录、写/root目录、创建特权容器、更改线程命名空间、创建挂载敏感目录的容器、获取sudo权限、尝试在二进制目录下写文件、异常运行shell、系统程序处理网络行为、shell登入容器。

![https://mmbiz.qpic.cn/mmbiz_png/hiayDdhDbxUbhytMsHicFLbZbXEvjicLrmj9pS0v0VLnQiaT192ia2kVdXpmuran62myQMIjia2***Vicia1SWibialeWAhg/640?wx_fmt=png](https://image.3001.net/images/20191125/1574651876_5ddb47e48d72b.jpg!small)

Kubernetes的node ready、CPU利用率、Memory利用率等成为主要的运维告警项。

![https://mmbiz.qpic.cn/mmbiz_png/hiayDdhDbxUbhytMsHicFLbZbXEvjicLrmjd5jnpKhHpb8xB8KV0qIUJian7oNMN4ygnZe8Rj4ickRcjSfzHoBo80MA/640?wx_fmt=png](https://image.3001.net/images/20191125/1574651891_5ddb47f342d0a.png!small)

总体来说，报告从多个角度展示了容器生态，尤其是容器环境的安全现状。对比前两年的报告，一方面可以看出，容器在计算环境中扮演了越来越重要的角色，另一方面，容器生态的安全问题，也是越来越多的引起容器使用者的关注。扫描文末二维码，关注公众号，回复“2019”，即可下载报告原文。

****

****

****

****

****

****

********

