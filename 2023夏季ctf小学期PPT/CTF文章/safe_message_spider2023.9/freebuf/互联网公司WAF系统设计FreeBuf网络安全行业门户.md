## 0x01 WAF简介

> WAF 全称是Web Application Firewall, 简单讲就是web防火墙，
> 是对web业务进行防护的一种安全防护手段。其实，现在很多的移动app，也是使用的http协议进行数据交换，也可以理解成web业务，可以对app
> server进行防护。

主要的web危害，一般指的是OWASP Top
10，比如SQL注入、XSS、CSRF等常见的web危害方法。当然可能不止这些方法，比如社工。轻则用你的服务器打个ddos，重则数据全部被盗，损失公司的信誉和money。

 **互联网公司的业务倾向于云平台，云WAF就应运而生，除去考虑硬件WAF的考虑，下面只讲基于互联网公司的需求，打造一款WAF联动系统。**

## 0x02 WAF基本组成

大部分互联网公司的业务，都会使用Nginx做各种各样的工作，负载均衡、A/B测试、Web网关等等的功能；另外，加上openresty（nginx +
lua)的开发效率和易用性，提高了程序猿开发nginx功能的效率。现在互联网公司招WAF开发的，一般都会加上nginx lua的要求，可见使用nginx +
lua开发WAF，实在是天时地利人和。

现在简单的说一下WAF系统的组成。WAF系统主要是由三部分组成的：执行前端、后端中心系统及数据库。

执行前端是WAF的执行引擎， 主要是根据规则进行过滤。根据规则匹配的结果，执行相应的动作。

后端中心系统主要是生成规则的逻辑，并与执行前端的nginx进行必要的数据交换。

数据库就是存放规则和一些配置及状态的地方，可以根据实际情况，选择关系型数据库或者Nosql。

![waf1.png](https://image.3001.net/images/20170302/14884463333545.png!small)

其中，可以看到后端中心系统相当于WAF的大脑，会根据不同的域名或者设备hostname的配置生成对应的逻辑。当执行前端拉取配置和规则时，
后端中心会把它对应的内容发给执行前端。这里做成集中式的管理模式，主要是方便统一管理，另外可以监控执行前端的状态，具体的状态数据，可以根据实际的情况进行协商，目前是建议json数据走http协议，方便易用。当然，数据传输的过程最好还是使用对称加密加base64
encode。

## 0x03 WAF细节考虑

一直比较关注cloudflare的云WAF，基本上WAF规则可以考虑为三类（不考虑长亭科技的sqlchop
<https://github.com/chaitin/sqlchop>，据说有类似的xss 要开源)：: 1️⃣通用的规则，比如sql、xss
规则，拦截恶意爬虫和扫描器等等的非常有效，这种基本上通用的。2️⃣cms规则，就是根据不同的cms，根据相应的漏洞定制的规则，比如php网站，不可能存在java语言的漏洞，具有专一性。3️⃣自定义规则，这就是根据自己的需求，自定义一些规则。根据入侵类型，再细分就会更多了，拦截shell、爬虫等等的，这里只是输了大概。

在github上面，最具参考的lua waf 就属 <https://github.com/p0pr0ck5/lua-resty-waf>她了，
其它的并不是说不好，然而只有这个最接近Modsecurity的逻辑， 最突出的有点就是规则的弹性化，最接近Modsecrity的规则。 不过，
<https://github.com/starjun/openstar>里面的很多防御方法，也是可以借鉴的。

* * *

###  **执行前端：  
**

基于p0pr0ck5
的WAF，二次修改一下，就可以做成上述的执行前端，但是它是有Bug的，生产环境下需要线下流量测试。主要在这个基础上，添加拉取配置和规则的timer就可以了，
有些人说用zookeeper什么的， 另外还有用的http 来进行配置更新通知，zookeeper不建议，当你reload的时候，就可以看见很多nginx
处于shutting down状态，就只zookeeper处于keepalive状态。
使用http访问加共享内存，京东的涛哥是这样做的，也是有些坑，不过timer最简单，每个worker单独维护一个配置，避免了锁的情况。

另外，收集日志最好不要用kafka， 打火焰图的时候，明显cpu时间有点长，用tcp或者http 发送最靠谱。执行前端大概就是这些内容，记得加上xpcall
能把一些小的问题catch到，避免影响请求。

所有的配置是用json传输的，然后转换成 lua的数据格式，使其能正确识别出WAF规则。WAF规则类似如下：

    
    
    {
        "vars": [
            {
                "parse": {
                    "values": 1
                }, 
                "type": "REQUEST_ARGS"
            }
        ], 
        "pattern": "select[^A-Za-z].*from\\W|union\\W.*select[^A-Za-z]", 
        "actions": {
            "disrupt": "SCORE", 
            "nondisrupt": [
                {
                    "action": "setvar", 
                    "data": {
                        "key": "anomaly_score", 
                        "col": "TX", 
                        "value": 8, 
                        "inc": 1
                    }
                }
            ]
        }, 
        "msg": "SQLInject", 
        "operator": "REGEX", 
        "id": 10001
    }

确保WAF能够识别出这些规则就可以了，严格按照它的格式来，毕竟lua脚本的优势在这里体现的一览无余。

* * *

###  **后端中心系统** :

后端中心系统同样是使用的Openresty(别的我也不会，开个玩笑），设计成类似api网关，还是那句话好管理。根据不同的域名和设备Hostname发送不同的配置。甚至，可以把所有WAF的逻辑放到这里，这是lua支持热加载的功能。这里是如何做你的WAF的关键，主要逻辑还是在这里。

这里是一些基本配置涵盖了：

>   1. WAF基本配置，包括了规则拉取服务配置、日志中心配置及更新组件等配置。  
> 这些基本配置决定了，WAF主要的逻辑处理。
>   2. IP列表， 包括了所有黑名单的ip，及对应host或者uri对应的ip，其中，支持配置生效时间。
>   3. 规则列表，主要是Web入侵规则配置，包括了default集合及对应host的waf配置。
>

基本配置主要是配置规则拉取服务配置、日志中心配置及更新组件等配置。这些配置也可以有由服务端动态生成。

    
    
    conifg =  {              
        ip_status = "off",
        waf_status = "off",
        srvhost="127.0.0.1",
        srvport=80,
        srvuir="/api/get_waf_data",
        loghost="127.0.0.1",
        logport=80,
        loguri="/api/post_waf_log",
        deny_code=201,
        delay = 10,
    }

IP列表， 其中有些是全局封禁，有些是针对某些接口，配置有过期时间的功能。

    
    
    ip_list =  {
                  global_ip={{"1.1.1.1", 0}, {"2.2.2.2", 123124}, { "3.3.3.3", 0}}
                  host = {{"1.1.1.1", 123124214}, { "2.2.2.2", 123412412}}
                  host1_uri1 ={{"1.1.1.1", 0}, { "2.2.2.2", 123412412}}
                  host2_uri2 = {{"1.1.1.1", 1231241}, {"2.2.2.2", 0}}
    },

规则的内容就是上面已经列出的内容了。 其中因为要适合配置的逻辑需要根据根据自己的需求进行修改。

* * *

###  **数据库和Web：**

数据库规则设计：

    
    
    CREATE TABLE `waf_rules_info` (
      `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
      `ruleid` int(10) NOT NULL COMMENT '规则id',
      `patterntype` varchar(32) DEFAULT 'REGEX',
      `specific` varchar(255) DEFAULT NULL,
      `vartype` varchar(255) DEFAULT NULL,
      `patternvalue` varchar(255) DEFAULT NULL COMMENT 'base64 封装',
      `action` varchar(32) DEFAULT NULL,
      `score` int(10) DEFAULT NULL,
      `description` varchar(512) DEFAULT NULL COMMENT 'decrption',
      `transforms` varchar(512) DEFAULT NULL COMMENT 'json 结构体',
      `negated` int(5) DEFAULT '0',
      `ruletype` varchar(32) DEFAULT NULL,
      `rulephase` varchar(32) DEFAULT NULL,
      PRIMARY KEY (`id`,`ruleid`),
      KEY `rule_id` (`ruleid`)
    ) ENGINE=MyISAM AUTO_INCREMENT=53 DEFAULT CHARSET=utf8;

这个是最主要的，有些属性暂时没有设置。

对于web而言，主要还是配合下发配置，规则方面，我是设置了三层结构：规则->规则组->host。它们只是逻辑上的关系，具体在后面逻辑实现时，会把散列的规则进行分组并根据数据库的逻辑进行组合，生成对唯一host的配置。同理，可以设置不同的分组，达到灰度测试的目的。

![屏幕快照 2017-03-02
下午7.04.06.png](https://image.3001.net/images/20170302/14884526733075.png!small)

这是具体规则的web设置，规则配置增删改规则，规则分组则是对规则分组的增删改操作，规则应用则是对不同host配置不同的规则分组。
这里说明一下，规则分组是按照XSS、SQLi 、灰度等功能分开的，对于host进行不同的配置。

目前，阿里云有自定义的规则，太单一，远远比不上cloudflare的设计，而且cloudflare更贴近互联网公司的需求，最主要的如何让自定义功能更有弹性，更大限度的支持规则的弹性。

简简单单，就说了个大概， 如果真的对WAF有研究的话，剩余的就比较轻松了，算是抛砖引玉了。

## 0x04 其它

记得有个作者提到，WAF位置卡位比较好，
现在很多CC和扫描器都是在七层防御的，WAF封禁某些ip和用户还是比较靠谱的，另外很多是cdn过来的请求，只能靠x-forward-for取出来的ip进行封禁，当然它可以伪造，就看数据分析的能力，把真实的ip抓出来。WAF规则p0pr0ck5
提供了一些Modsecurity转译的，可以参考它实现自己的规则。另外，WAF的性能也很重要，章亦春大神的很多讲座ppt有提到的，可以作为参考。章亦春大神已经创业了，它打造的商业openresty就有WAF的支持。

最后，就先写这些吧，有问题的可以私信我，后面会引入大数据分析和安全数据挖掘。第一次发文章，欢迎各位大神轻拍。

***本文作者：chengfangang，转载请注明来自Freebuf.COM**

