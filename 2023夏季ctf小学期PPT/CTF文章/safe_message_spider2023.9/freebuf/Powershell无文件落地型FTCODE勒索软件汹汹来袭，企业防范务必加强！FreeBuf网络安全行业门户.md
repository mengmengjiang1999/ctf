## **概述** ****

奇安信病毒响应中心在日常的样本运营中发现多个恶意Office
DOC格式的样本，其以宏的形式执行命令行参数，然后通过Powershell的方法执行勒索代码，加密文件实现勒索，
全程没有二进制的文件落地。这也就意味着，受害者将无法在被勒索设备上找到加密样本，从而无法通过样本分析对加密文件进行解密。

由于勒索软件加密后缀名为.FTCODE，因此奇安信病毒响应中心将其命名为FTCODE勒索软件。

##  **详细分析** ****

捕获的样本通过鱼叉邮件的形式投递，内容如下：

_"Tribunale di Milano.Avviso XXXXXXX"_ dove XXXXXXX sta per una serie casuale
di numeri. L'allegato presenta nomi del tipo _"AvvisoXXXXXXX.zip"_ dove
XXXXXXX sta per una serie casuale di numeri diversi da quelli contenuti
nell'oggetto email.

下列为翻译成中文：

_“您好，附在此电子邮件中，我们已将相关**的Pdf副本发送给您。根据633/72号总统令第21条，不含税值的文件。原始文件可在您提供的远程信息处理地址或您所在的地区获得税务局”。_

样本起初由压缩包打包，从文件名可见：

MD5| 95f35480848de94cdcc836302db996dc  
---|---  
文件名| IT755422261536411934527067.doc  
文件类型| Doc  
创建时间| 2019-09-26 00:02:00  
保存用户名| Administrator  
  
打开后是一个Office365的图片界面，里面有意大利语的描述来诱导用户点击”启用宏”按钮，除了上诉表格的样本外，其他捕获的样本也均针对意大利用户发起攻击。

![图片.png](https://image.3001.net/images/20190929/1569752682_5d90866ab7a4c.png!small)图2.1
法语描述的诱导用户点击宏按钮

从DOC文件中提取到宏代码，该代码中的内容做了简单的加密，单字节add 441后可以得到解密后的内容：

![图片.png](https://image.3001.net/images/20190929/1569751639_5d90825783739.png!small)图2.2
doc中提取到的宏代码

![图片.png](https://image.3001.net/images/20190929/1569751651_5d908263c8080.png!small)图2.3
解密出的待运行的命令行参数

执行起来的Powershell命令base64解码后得到的内容如下，会从http[:]//aweb.theshotboard[.]info/?page=xing&vid=dc1:load下载下一阶段的payload执行：

该URL每次请求的结果都是不一样，可能基于对抗病毒动态检测的考虑：

![图片.png](https://image.3001.net/images/20190929/1569751676_5d90827ce087a.png!small)图2.4
请求url的返回结果

Powershell脚本执行起来后，会先通过Get-UICulture判断操作系统的语言，如果是以下国家则后续会进行另一个分支操作：

CN| 中国  
---|---  
RO| 罗马尼亚  
RU| 俄罗斯  
UA| 乌克兰  
BY| 白俄罗斯  
  
之后判断是否在虚拟机中执行，检测的虚拟机种类包括VirtualBox、VMWare、KVM和HVM，接下来从[
_http://cofee.theshotboard.net/?need=uuid
&vid=dc1:loadjs&_](http://cofee.theshotboard.net/?need=uuid&vid=dc1:loadjs&)下载文件到$env:PUBLIC
+ "\Libraries\WindowsIndexingService.js，然后创建计划任务，指向该js文件实现持久化：

![图片.png](https://image.3001.net/images/20190929/1569751737_5d9082b96b241.png!small)图2.5
判断操作系统语言和虚拟机环境

随机生成一个密钥，用自带的公钥加密随机生成的密钥，进行base64编码后放到personal
KEY；令人奇怪的是攻击者把加密文件用的密钥经过base64编码后，通过HTTP Post的方式发送到自己的服务器。

![图片.png](https://image.3001.net/images/20190929/1569751748_5d9082c461699.png!small)图2.6
通过内置公钥加密随机生成的密钥

上报guid和随机生成的密钥，因此，如果被中招的勒索的用户设备存在天眼类的全流量监控设备，相应的key是可以捕获到并能用于解密被加密的文件：

![图片.png](https://image.3001.net/images/20190929/1569751757_5d9082cd060ec.png!small)图2.7
往攻击者的服务器上报数据

该勒索病毒加密的文件类型如下：

加密后的文件的后缀名为.FTCODE，然后在同目录下创建READ_ME_NOW.htm文件，展示被加密机器的加密密钥和机器码：

![图片.png](https://image.3001.net/images/20190929/1569751772_5d9082dcb2231.png!small)图2.8
该恶意代码的加密部分

然后删除磁盘卷影，防止数据恢复：

![图片.png](https://image.3001.net/images/20190929/1569751779_5d9082e3885df.png!small)图2.9
执行防止文件恢复的一些命令

访问攻击者的域名的时候，404的页面如下，可知攻击者是在crypt_c3440c138ba8013目录下搭建的网站后台：

![图片.png](https://image.3001.net/images/20190929/1569751789_5d9082ed166c1.png!small)图2.10
404页面内容

![图片.png](https://image.3001.net/images/20190929/1569751802_5d9082fa98b25.png!small)

图2.11 本地勒索页面内容

 ****

**下图所示，其称如果在3天内付款只需要0.** **2** **比特币，但是过后就要收1比特币。约合***** **11530.4。** ****

![图片.png](https://image.3001.net/images/20190929/1569751816_5d90830876261.png!small)

图2.12 洋葱勒索 付款页面

![图片.png](https://image.3001.net/images/20190929/1569751828_5d908314bd46b.png!small)

图 2.13 文件加密图

##  **总结** ****

如今，勒索软件种类频频出现，而这类全程以脚本的形式执行的勒索，更容易摆脱杀毒软件的查杀。因此人员安全培训将是重中之重，不要随意点击来源不明的文件，并且邮件入口也要做好响应的规则过滤等。

目前本文中样本仅针对 **意大利用户** ，但极有可能被修改用于针对中国的目标，因此务必对此类攻击进行检测，奇安信全线产品均可检测此类威胁，且若
**布置全流量抓包设备可以协助解密** 。

最后，国庆期间，奇安信病毒响应中心7*24小时值守，实时为用户解答与网络安全一切疑惑，拨打电话4008-136-360
或400-678-3600，[或者发送相关邮件至邮箱
ti_support@qianxin.com](mailto:%E6%88%96%E8%80%85%E5%8F%91%E9%80%81%E7%9B%B8%E5%85%B3%E9%82%AE%E4%BB%B6%E8%87%B3%E9%82%AE%E7%AE%B1%C2%A0ti_support@qianxin.com)即可。

## **IOC** ****

 **MD5** ****

95f35480848de94cdcc836302db996dc

6e158d8b4bbd66d8d81351aac74195f5

2ff80f44313702349f6b21d869abff1c

e347486275f4a968e68d3e1d29f56c24

f6fdc5f3c20358c4672d24d325a08cc7

**HOST** ****

aweb.theshotboard.info

[ _http://cofee.theshotboard.net/?need=uuid
&;amp;vid=dc1:loadjs&_](http://cofee.theshotboard.net/?need=uuid&;amp;vid=dc1:loadjs&)

FTCODE勒索软件在运行后，机器码会存放在此路径，因此可以作为排查条件。

C:\Users\Public\OracleKitw00log03.tmp

![图片.png](https://image.3001.net/images/20190929/1569751850_5d90832a96436.png!small)

**勒索软件相关信息** ****

加密后缀名为.FTCODE ，

本地勒索页面名称

READ_ME_NOW.htm

**付款链接** ****

<http://qvo5sd7p5yazwbrgioky7rdu4vslxrcaeruhjr7ztn3t2pihp56ewlqd.onion/?guid=>
c681463e-42a8-4f56-ba19-01c8abdf36bc

