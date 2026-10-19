因为前端时间需要收集许多漏洞补丁信息做实验分析，所以需要一个完整的收集验证流程来提高效率。

# CVE对应commit、issue验证流程

1、CVE Search Result中搜索：

    
    
    type confusion in v8
    

https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=Type+confusion+in+V8

可得有关30+条CVE记录。

2、由对应CVE的参考链接即可访问https://crbug.com/(bug id)，即issue描述网站，由此得到Bug
id，以及一些commit，若是permission denied：

可尝试在Chromium Gerrit搜索例如：

    
    
    Bug: chromium:1216437
    

此处给出了对应bug id的工单信息，对应其change id即可验证commit和补丁。

需要注意的是：同一个CVE可能具有多个补丁，也就意味着多个工单信息，想要查找最原始的补丁只要找发布时间最早的即可

以搜索CVE-2021-30551为例：

1）此处可得到通往crbug.com的链接，以及这个CVE的bug id  
![image](https://image.3001.net/images/20220508/1651997135_627779cfe716edcf4d41d.png!small)

2）进入 https://crbug.com/1216437 ,可以看到对此bug的问题描述。  
![image](https://image.3001.net/images/20220508/1651997144_627779d87ad09cdc9b5c0.png!small)

3）往下滑即可看到如：点击链接即可前往查看补丁
https://chromium.googlesource.com/v8/v8/+/f9857fdf743eeb263aec3944259ad811f564291b

![image](https://image.3001.net/images/20220508/1651997151_627779dfd07bdc5d496d5.png!small)

4）此处即可查看补丁相关信息，此处点击Reviewed-on给出的链接即可通往gerrit查看其工单信息https://chromium-review.googlesource.com/c/v8/v8/+/2940889

![image](https://image.3001.net/images/20220508/1651997158_627779e6efe1b9e17e7b5.png!small)

5）工单信息，此处提供了diff，那么此时就已经能够对漏洞补丁信息进行较为完善的收集啦：

![image](https://image.3001.net/images/20220508/1651997166_627779eeda6404c330fb0.png!small)

第二个可行的方案：

在master分支搜索：

    
    
    git log --grep "(bug id)"  //chromuim仓库信息只能通过bug id、change id等方式搜索
    

若出现多个commit说明有多个补丁，下拉到最底层的第一个补丁即是 0-days In-the-Wild 中公布的补丁。

