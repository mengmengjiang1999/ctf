从0到1学习网络安全 【利用linux内核漏洞实现Docker逃逸】

[ _07](https://www.jianshu.com/u/044de43a8ffc)关注赞赏支持

# 从0到1学习网络安全 【利用linux内核漏洞实现Docker逃逸】

##### 利用linux内核漏洞实现Docker逃逸

    
    
    漏洞编号：CVE-2016-5195
    漏洞影响范围： 
    根据Linux内核官方评估自2007年来发行的 >=2.6.22的内核版本全部受影响
    
    由于此漏洞是在本地测试，漏洞环境没放到靶场。
    环境下载地址： https://pan.baidu.com/s/1FDDyErlmsfYkAzeYnp0DBQ 提取码: myck 
    

* * *

## 逃逸过程：

https://www.bug1024.cn

## 逃逸过程复现：

###### Step1:将下载的镜像安装后，登录目标主机开启存在漏洞的Docker环境

    
    
    #用户名：ibug
    #密码：root
    sudo docker ps -a #查看docker环境
    sudo docker start id #开启环境
    

开启Docker环境

  * 攻击机访问漏洞地址再次确认环境已开启

  

Docker环境已开启

###### Step2:此Docker环境为s2-052靶机环境，直接利用EXP拿到权限

获得Docker虚拟机权限

###### Step3:下载在自己服务器放好的linux内核漏洞EXP至docker环境中，解压并赋予可执行权限

image.png

###### Step4:执行EXP成功获取目标主机权限

id

ifconfig

## 修复建议：

  * 升级内核版本

**注意：**

  * 因为涉及到操作系统内核的升级，我们强烈建议您正确关闭正在运行的服务，并做好业务数据备份工作。同时创建服务器磁盘快照，避免修复失败造成不可逆的影响。

  * 如果您的服务器安装了第三方的防护软件（例如云锁、安全狗），则有可能导致内核升级不成功，建议您先卸载这些软件，等到升级内核成功后再重新安装启用。

参考链接：  
[https://help.aliyun.com/knowledge_detail/44786.html](https://links.jianshu.com/go?to=https%3A%2F%2Fhelp.aliyun.com%2Fknowledge_detail%2F44786.html)  
[https://bbs.aliyun.com/read/297492.html](https://links.jianshu.com/go?to=https%3A%2F%2Fbbs.aliyun.com%2Fread%2F297492.html)

* * *

> 由于小编也在学习中，写的不好各位勿喷。  
>  [从0到1学习网络安全 【目录】](https://www.jianshu.com/p/d62992b1ff2a)

实战靶场环境迁移：

[https://mp.weixin.qq.com/s/5Nat58sq85CmnW-
kWXAOsw](https://links.jianshu.com/go?to=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2F5Nat58sq85CmnW-
kWXAOsw)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [【linux内核漏洞利用】StringIPC—从任意读写到权限提升三种方法](https://www.jianshu.com/p/07994f8b2bb0)

参考：https://xz.aliyun.com/t/3204 题目：CSAW-2015-CTF的stringip...

[bsauce](https://www.jianshu.com/u/a12c5b882be2)阅读 2,368评论 2赞 2

  * [初识Docker逃逸漏洞](https://www.jianshu.com/p/89b329626621)

本文仅作学习记录，如有侵权，请联系删除！ 前言： 很早之前看过相关的文章介绍过，但是把，这知识不过脑啊，虽然还没有...

[book4yi](https://www.jianshu.com/u/d60a4e568a69)阅读 3,999评论 0赞 6

  * [Linux本地内核提权漏洞复现(CVE-2019-13272)](https://www.jianshu.com/p/c044be6f9d93)

0x00简介 在5.1.17之前的Linux内核中，kernel / ptrace.c中的ptrace_link错...

[5f4120c4213b](https://www.jianshu.com/u/5f4120c4213b)阅读 317评论 0赞 0

  * [【linux内核漏洞利用】call_usermodehelper提权路径变量总结](https://www.jianshu.com/p/a2259cd3e79e)

本文通过分析STARCTF 2019 hackme 题目，来总结一下提权时可修改的变量。不需要劫持函数虚表，不需要...

[bsauce](https://www.jianshu.com/u/a12c5b882be2)阅读 2,342评论 0赞 2

  * [【Linux内核漏洞利用】绕过内核SMEP姿势总结与实践](https://www.jianshu.com/p/3d707fac499a)

一、通过VDSO绕过PXN 1.简介 最近一年，一种利用VDSO( Virtual Dynamic Shared ...

[bsauce](https://www.jianshu.com/u/a12c5b882be2)阅读 2,937评论 0赞 5

 