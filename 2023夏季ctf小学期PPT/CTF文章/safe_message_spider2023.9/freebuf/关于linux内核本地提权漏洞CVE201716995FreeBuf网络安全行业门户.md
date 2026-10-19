# 漏洞概述

![2.jpg](https://image.3001.net/images/20180320/15215339517913.jpg!small)  

Jann Horn发现内核中Berkeley Packet Filter（BPF）实现中, Linux内核4.14.8版本开始kernel/bpf/
verifier.c源码中的check_alu_op函数启用了不正确地执行符号扩展,可导致内存任意读写漏洞。一般用户可利用这个漏洞，实现任意代码，获得本地提权操作。

![3.jpg](https://image.3001.net/images/20180320/15215339579707.jpg!small)  

  

日前， CVE-2017-16995的Linux内核漏洞攻击代码被发布：

![4.jpg](https://image.3001.net/images/20180320/15215339358432.jpg!small)  

# 影响版本

Linux Kernel Version 4.14~4.4 （主要是Debian和Ubuntu发行版）

# 内核版信息查看

cat /proc/version

# ubuntu版本影响情况

![5.jpg](https://image.3001.net/images/20180320/15215340498790.jpg!small)  

![5.jpg](https://image.3001.net/images/20180320/15215339868260.jpg!small)

更多信息请参考https://people.canonical.com/~ubuntu-security/cve/2017/CVE-2017-16995.html  

# redhat系列不受影响

笔者松了口气，看热闹就成了。

![7.jpg](https://image.3001.net/images/20180320/1521534072735.jpg!small)  

#  **修复建议：**  

目前暂未有明确的补丁升级方案。 建议用户在评估风险后，通过修改内核参数限制普通用户使用bpf(2)系统调用：

$ sudo sysctl kernel.unprivileged_bpf_disabled=1

$ echo kernel.unprivileged_bpf_disabled=1 | sudo tee
/etc/sysctl.d/90-CVE-2017-16995-CVE-2017-16996.conf

关于升级补丁，部分ubuntu版本已经提供了补丁见上一部分列出的链接，可以酌情安排升级。

 **参考链接**

1.https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-16995

2.http://openwall.com/lists/oss-security/2017/12/21/2

3.https://usn.ubuntu.com/usn/usn-3523-1

4.https://usn.ubuntu.com/usn/usn-3523-2

5.https://usn.ubuntu.com/usn/usn-3523-3

6.http://cyseclabs.com/exploits/upstream44.c

7.https://git.kernel.org/pub/scm/linux

/kernel/git/torvalds/linux.git/commit/?id=3db9128fcf02dcaafa3860a69a8a55d5529b6e30

  

  
  

