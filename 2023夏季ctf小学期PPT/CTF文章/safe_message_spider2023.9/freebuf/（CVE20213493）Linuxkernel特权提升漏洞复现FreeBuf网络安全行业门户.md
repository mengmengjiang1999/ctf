***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、简介

Linux，全称GNU/Linux，是一种免费使用和自由传播的[类UNIX](https://baike.baidu.com/item/%E7%B1%BBUNIX/9032872)操作系统，其内核由[林纳斯·本纳第克特·托瓦兹](https://baike.baidu.com/item/%E6%9E%97%E7%BA%B3%E6%96%AF%C2%B7%E6%9C%AC%E7%BA%B3%E7%AC%AC%E5%85%8B%E7%89%B9%C2%B7%E6%89%98%E7%93%A6%E5%85%B9/1034429)于1991年10月5日首次发布，它主要受到[Minix](https://baike.baidu.com/item/Minix/7106045)和Unix思想的启发，是一个基于[POSIX](https://baike.baidu.com/item/POSIX)的多用户、[多任务](https://baike.baidu.com/item/%E5%A4%9A%E4%BB%BB%E5%8A%A1/1011764)、支持[多线程](https://baike.baidu.com/item/%E5%A4%9A%E7%BA%BF%E7%A8%8B/1190404)和多[CPU](https://baike.baidu.com/item/CPU)的操作系统。

## 二、漏洞描述

Linux内核中overlayfs文件系统中的Ubuntu特定问题，它未正确验证关于用户名称空间的文件系统功能的应用。由于Ubuntu附带了一个允许非特权的overlayfs挂载的补丁，因此本地攻击者可以使用它来获得更高的特权。

## 三、复现

Exp下载地址：<https://github.com/briskets/CVE-2021-3493>

查看内核版本

    
    
    Uname -a

![1620567290_6097e4fa575d6d586559d.png!small?1620567290132](https://image.3001.net/images/20210509/1620567290_6097e4fa575d6d586559d.png!small?1620567290132)

下载exp：git clone <https://github.com/briskets/CVE-2021-3493.git>

![1620567299_6097e503daac9a8a8799b.png!small?1620567299721](https://image.3001.net/images/20210509/1620567299_6097e503daac9a8a8799b.png!small?1620567299721)

低权限账号编译并赋予权限

![1620567306_6097e50a392931411f695.png!small](https://image.3001.net/images/20210509/1620567306_6097e50a392931411f695.png!small)

执行exp

![1620567314_6097e5122bc44f4855f7a.png!small?1620567313908](https://image.3001.net/images/20210509/1620567314_6097e5122bc44f4855f7a.png!small?1620567313908)

## 四、漏洞防御

1、更新系统软件包

2、更新linux内核

