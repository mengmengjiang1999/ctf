**APT35又被成为“Charming
Kitten”，是归属于伊朗的黑客组织。该组织自2014年活动以来，其目标为伊朗专家、人权活动人士和媒体人员。大多数受害者在中东、美国和英国。**

## 活动时间线

其活动时间线如下：

> 2015年，Clearsky研究人员发现该组织网络钓鱼攻击行为，并发布名为“Thamar reservoir”的调查报告。
>
> 2017年，Clearsky检测并揭露该组织在2016年至2017年大规模的间谍活动，其主要攻击包括冒充假冒组织和个人进行鱼叉和水坑攻击。
>
> 2018年，该组织试图通过虚假网站攻击Clearsky研究组织，同年该组织利用虚假邮件以及网站发起针对中东的网络攻击。
>
>
> 2019年，该组织攻击活动量急剧增加，从中可知其发起了新的网络攻击活动，共分为两个阶段，针对两类不同的人：伊朗学术研究中来自美国、中东和法国的非伊朗研究员；在美国的持有不同政见者的伊朗人。

今年8月该组织活动持续进行，与7月不同的是，apt组织正在将目标范围拓展到全球具有影响力的人，并不是限定于学术研究人员和国家组织。此外，在2019年8月发现该组织已经在电子邮件中添加追踪器，可以跟踪转发至其他邮箱的电子邮件并获取地理位置。

## 攻击流程

> 1、第一阶段是利用社会工程学的方法发送电子邮件，黑客模仿一位知名的研究人员或记者，邀请收件人参加某主题活动。
>
> 2、第二个阶段是一个虚假网站，模拟各种谷歌服务，如gmail或google drive，受害者从钓鱼电子邮件重定向到这些服务。  
>
>
> 3、使用虚假社交网站，冒充Instagram官方网站，并试图提取非google服务的凭据。  
>

## 邮件分析

### 第一组邮件

攻击者冒充研究机构，试图私下联系受害者，鼓励他们查看简历。在电子邮件中的链接是一个虚假网站的url地址![1.PNG](https://image.3001.net/images/20191011/1570761895_5d9feca742a52.png!small)

此链接并不是恶意链接，它目的是为了赢得受害者的信任，该网站包含与原文完全相同的页面，只有发件人的地址发生了变化。

![1.PNG](https://image.3001.net/images/20191011/1570762066_5d9fed527af85.png!small)  

电子邮件是以十进制编码用javascript嵌入到网页内容中的，例如：来自isis online[.]org发送到假电子邮件地址isis
online[.]net，如下所示：

![1.PNG](https://image.3001.net/images/20191011/1570762189_5d9fedcde5289.png!small)其编码为：

###
![1.PNG](https://image.3001.net/images/20191011/1570762311_5d9fee4777699.png!small)第二组邮件

该组邮件中，攻击者冒充一名知名记者，与上一组邮件不同的是该邮件不包含任何指向虚假网站的链接。攻击者会让目标参与关于伊朗或其感兴趣的在线会议，若目标有兴趣参与则会要求提供以下信息：

> 1、其他参与者的名单
>
> 2、会议的日期和时间
>
> 3、有关付款的具体方式信息

![1.PNG](https://image.3001.net/images/20191011/1570762563_5d9fef43be0c8.png!small)对文章中出现的Deutcshe
Welle网站进行扫描后发现，该网站是一个德国的国际新闻门户网站，如下图所示。该网站仍然在用于攻击活动。

![1.PNG](https://image.3001.net/images/20191011/1570764767_5d9ff7df1648d.png!small)第二波攻击主要集中在8月份，攻击者在同一个晚上冒充CNN记者向多个目标发送电子邮件，以下为电子邮件内容：

![1.PNG](https://image.3001.net/images/20191011/1570764906_5d9ff86aea604.png!small)通过分析邮件头部信息可以发现攻击者在邮件中植入的追踪信息，其内容如下：

![1.PNG](https://image.3001.net/images/20191011/1570764986_5d9ff8ba44a8b.png!small)攻击者使用追踪器检查邮件是否转发给其他收件人，并获取受害者的地理位置和IP地址。数据通过安装在受害者计算机上的cookie按以下路径收集：  

    
    
    C:\Users\admin\AppData\Roaming\Microsoft\Windows\Cookies\Low\admin@gnldr[$].txt  
    

cookie内容如下：  

![1.PNG](https://image.3001.net/images/20191011/1570765093_5d9ff92542bde.png!small)为了进一步掩盖消息的恶意目的，攻击者附加了CNN标志：  

##
![1.PNG](https://image.3001.net/images/20191011/1570765229_5d9ff9ad537a8.png!small)基础设施分析

确定了超过六个服务器负责托管网站。其中，四个服务器为第一阶段的一部分，而另外两个主机服务器模拟google服务。我们估计这些可能被用于攻击第二阶段的数据窃取。  

![1.PNG](https://image.3001.net/images/20191011/1570765372_5d9ffa3c542b4.png!small)经过一个月的攻击活动，攻击者切换了用于存储电子邮件地址的服务器，其中包含数千个地址。  

这些域名只能通过上文提到过的链接进行访问，其他情况下服务器会将访问者重新定向到原始网站。下图为shodan查询的ip地址，185.141.63[.]160，会被重定向到虚假域名unirsd[.]com。

185.141.63[.]135是唯一一个指向两个域名的服务器：

> 1、leslettrespersanes[.]net，虚假的法国杂志“Les Lettres Persanes”
>
> 2、Inztaqram[.]ga，虚假的 Instagram 公司

![1.PNG](https://image.3001.net/images/20191011/1570766014_5d9ffcbe9c045.png!small)在对其他服务器进行搜索的过程中确定了一个重定向到google服务的服务器，该服务器同时承载两个伊朗域名，该服务器极有可能是此次攻击活动的一部分：

##
![1.PNG](https://image.3001.net/images/20191011/1570766265_5d9ffdb913a39.png!small)![1.PNG](https://image.3001.net/images/20191011/1570766299_5d9ffddb28d92.png!small)活动关联

利用三个主要因素来对该组织的攻击活动进行划分：

1、第一个因素为：在上述邮件中出现的两个主要网站：犹太期刊和德国杂志（Deutsche Welle）

在2019年3月通过域名jewishjournal[.]online分析确认该组织发起的另一起网络攻击活动，并利用DNS记录发现了另一个假冒Deutsche
Welle的域名：deutcshewelle[.]net

![1.PNG](https://image.3001.net/images/20191011/1570776948_5da02774a0504.png!small)通过dns记录可以发现，该组织利用自2019年7月就开始使用Jewish
Journal进行攻击活动。![1.PNG](https://image.3001.net/images/20191011/1570777031_5da027c731700.png!small)

2、第二个因素为：如上文提到的该组织的目标为美国、中东、法国中持有不同政见者的人，但是在邮件中都会重复出现拼写错误。

3、假冒NIAC的行为证明该组织属于伊朗。

除上述原因外，更多信息将该组织的活动与伊朗联系起来。其中一个是在exnovin[.]org网站上找到的原始服务器NetBlock的IP地址。

exnovin是一家伊朗货币兑换平台，该域名先前托管在德国托管公司hetzner上，这些因素很可能与该组织有关。![1.PNG](https://image.3001.net/images/20191011/1570777467_5da0297b3b54f.png!small)

## IOCs

    
    
    isis-online[.]net
    acconut-verify[.]com
    leslettrespersanes[.]net
    unrisd[.]com
    drive-accounts[.]com
    niaconucil[.]org
    skynevvs[.]com
    islamicemojimaker[.]com
    w3-schools[.]org
    seisolarpros[.]org
    exnovin[.]org
    185[.]141[.]63[.]161
    185[.]141[.]63[.]162
    185[.]141[.]63[.]135
    185[.]141[.]63[.]160
    185[.]141[.]63[.]156
    185[.]141[.]63[.]157
    185[.]141[.]63[.]8
    185[.]141[.]63[.]172  
    

 ***参考来源：[clearskysec](https://www.clearskysec.com/wp-content/uploads/2019/09/The-Kittens-Are-Back-in-Town-Charming-Kitten-Sep-2019.pdf)，由Kriston编译，转载请注明来自FreeBuf.COM**  

