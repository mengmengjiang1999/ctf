**APT35又被成为‘Charming
Kitten’，是归属于伊朗的黑客组织。该组织自2014年活动以来，其目标为伊朗专家、人权活动人士和媒体人员。大多数受害者在中东、美国和英国。**

2019年10月4日微软宣布发现该组织正在尝试攻击email邮箱，其目标为美国总统竞选团队、美国现任和前任政府官员、全球政治记者、居住在伊朗境外的伊朗知名人士。这些钓鱼邮件全部由该组织在8月和9月制作。微软近期发现与Clearsky研究人员之前研究报告”APT35研究白皮书（一）“基本一致：

### 1、目标相同

在两起攻击活动中，目标都是对伊朗感兴趣的组织和个人，例如学术组织、人权组织、记者等。

### 2、时间线相同

在Clearsky最新的报告中已经提到发生在2019年7-8月的攻击，在微软发现的报告中同样提到攻击发生在8-9月30天内。

### 3、攻击面相同

在两次攻击中该组织使用的相似的攻击手段：

> 1）针对目标邮箱的登录凭证获取
>
> 2）利用微软、谷歌、雅虎服务的钓鱼邮件
>
> 3）通过短信的鱼叉钓鱼攻击，表明该组织正在收集目标雕花号码等信息。微软发现攻击者利用手机号和密码凭证恢复两种认证因素来获得邮箱账户的控制权。

本文将分析新发现的四种鱼叉式钓鱼方法，以及该组织的具体攻击方式。

## 攻击分析

‘Charming Kitten’一直尝试在用钓鱼的方式攻击目标，检测到的钓鱼数量一直增加，攻击可以分为三个方式：

> 1）利用社会工程学发送电子邮件
>
> 2）假冒社交平台传播恶意链接
>
> 3）向目标手机发送短信

通过对攻击活动的分析，确定了该组织四种攻击方式。

### 1、Google Drive链接下载

目标会受到攻击者发送的带有Google drive下载链接的邮件，目标下载后攻击者可利用恶意软件收集目标google凭证。

![](https://image.3001.net/images/20191012/1570863995_5da17b7b5dd63.png!small)

上面显示的链接指向一个使用google平台构建的站点，共享链接域名是gmail.com，但是实际应为google.com。

一个正确的google站点共享消息如下：

![](https://image.3001.net/images/20191012/1570864221_5da17c5deb1f9.png!small)

另一起钓鱼事件中，目标受到从未知用户发来的google drive共享消息，攻击者生成从目标账户收到大量垃圾邮件，并诱导目标点击链接。

![](https://image.3001.net/images/20191012/1570864372_5da17cf483435.png!small)

第三起事件中，目标收到从同事发来的邮件，攻击者假冒目标同事并诱导其点击链接。

![](https://image.3001.net/images/20191012/1570864483_5da17d63361ad.png!small)

链接会指向攻击者搭建的网站：

    
    
    hxxps://sites.google[.]com/view/cubqzpmuxra5bjxu7q2jxcxnhkldpa/drive/
    hxxps://sites.google[.]com/screenshot-sharing-service/drive/ 
    

![](https://image.3001.net/images/20191012/1570864618_5da17deac12b7.png!small)

点击下载链接后会被重定向到一个短网址域名，不会显示实际网址。

![](https://image.3001.net/images/20191012/1570864718_5da17e4e39aa2.png!small)

当特定攻击结束时，攻击者将从短网址服务中删除该站点，或将地址重定向到真正的邮件服务。例子如下：

![](https://image.3001.net/images/20191012/1570864817_5da17eb1d5f90.png!small)

![](https://image.3001.net/images/20191012/1570864832_5da17ec0050be.png!small)

如果被攻击者打开了上述链接，他们将被定向到恶意站点。在目前的攻击中，我们已经确定了一个“.site”TLD dominance。

![](https://image.3001.net/images/20191012/1570864921_5da17f19e67ad.png!small)

目标访问该网站时，攻击者会欺骗目标让他相信位于google服务中，并诱骗目标登录google账户下载文件。

![](https://image.3001.net/images/20191012/1570865114_5da17fda66a19.png!small)

### 2、SMS短信消息

在该方法总，攻击者将会以id为‘'Live
Recover’向目标发送信息，并警告目标有人正在攻击其电子邮件账户，诱骗目标点击链接验证。链接将利用短网址重定向恶意网站，下面的示例中目标收到的两条消息包含不同的链接：

![](https://image.3001.net/images/20191012/1570865329_5da180b1e2a0b.png!small)

### 3、登录警告信息

攻击者欺骗目标其邮箱正在朝鲜登录，并诱骗目标点击安全链接：

![](https://image.3001.net/images/20191012/1570865468_5da1813cddc14.png!small)

攻击者欺骗目标其邮箱密码被篡改，需要进行恢复设置，诱骗目标点击链接：

![](https://image.3001.net/images/20191012/1570865555_5da1819353df6.png!small)

但是在攻击者邮件中存在许多问题，首先发件人的地址为gmail邮箱，但是警告信息为雅虎邮箱；其次"Critical Security Alert"
题头信息出现了两次；前后两种界面中虽然设计形式发生了变化但是显示的时间日期和IP相同。点击链接后会跳转到钓鱼界面：hxxps://bitli[.]pro/B7ZI_f56f7c3f
，其中一些网站已经被封锁。

![](https://image.3001.net/images/20191012/1570865762_5da1826205730.png!small)

### 4、社交网络攻击

在之前的分析报告中，研究人员发现该组织假冒社交媒体获得目标的登录凭证。但是与之前不同，本次攻击中主要针对邮箱采取行动，在攻击活动中发现该组织不仅冒充Instagram，也有假冒的Facebook和Twitter网站。在w3-schools[.]org域名下发现了不同假冒网站的相关文件：

![](https://image.3001.net/images/20191012/1570866025_5da1836987876.png!small)

根据图片所示，该组织第一批上传的文件为Facebook和Twitter，google、National Iranian-American Council 和
Instagram为第二批上传文件。

每一个假冒站点中都会有一个ZIP文件:

![](https://image.3001.net/images/20191012/1570866198_5da184165a237.png!small)

![](https://image.3001.net/images/20191012/1570866206_5da1841eb1e80.png!small)

从压缩文件中可以看出攻击者使用WordPress和CrunchPress来搭建网站。

## 基础设施分析

已经发现8个新的和未知的域名：

    
    
    customers-recovery[.]site
    com-verifications[.]site
    com-session[.]site  
    

每一个域名都有各自的IP，在DNS查询后发现了他们的共同点：

![](https://image.3001.net/images/20191012/1570866684_5da185fc45e8e.png!small)

在最近的针对雅虎账户的活动中发现，该组织在2017年曾通过钓鱼获取雅虎账户的用户名和密码，但近年来已将重心转移到谷歌账户。在此次攻击活动中，该组织再次聚焦在雅虎账户并假冒雅虎服务。下面是该组织的一个钓鱼网站的url地址，该网站对yahoo服务（如ymail）进行了模仿。

    
    
    hxxps://mobiles.com-identifier[.]site/ymail/secureLogin/challenge/url?ucode=d105ad2b-2f7d-4193-a303-03eb32967133&service=mailservice&type=password 

在上一个报告中，发现恶意服务器将客户从仿冒网站重定向到原始网站。此次攻击中如果试图从非专用（即特别授权）入口访问网站，它也会将服务器设置为重定向到原始雅虎网站。

![](https://image.3001.net/images/20191012/1570867857_5da18a91250e0.png!small)

此次分析中在网站重定向前发现了其真实的地址及数字签名：

![](https://image.3001.net/images/20191012/1570868680_5da18dc85b1ad.png!small)

  

## IOCs

    
    
    my[.]en-gb[.]home-access[.]online
    notification-accountservice[.]com
    recovery-services[.]info
    recoverysuperuser[.]info
    see-us[.]info
    sessions-identifier-memberemailid[.]network
    smarttradingfast[.]com
    system-services[.]site
    telagram[.]net
    uploaddata[.]info
    verification-services[.]info
    40[.]112[.]253[.]185
    91[.]109[.]22[.]53
    136[.]243[.]195[.]229
    178[.]32[.]58[.]182
    185[.]177[.]59[.]240
    46[.]166[.]151[.]209
    51[.]68[.]200[.]126
    51[.]89[.]229[.]215
    51[.]255[.]157[.]110
    181[.]177[.]59[.]240
    bahaius[.]info
    bailment[.]org
    com-activities[.]site
    com-identifier[.]site
    com-session[.]site
    com-verifications[.]site
    customers-activities[.]site
    customers-recovery[.]site
    customers-reminder[.]info
    documentsfilesharing[.]cloud
    document-sharing[.]online
    gomyfiles[.]info
    identifier-activities[.]info
    identifier-activities[.]online
    identity-verification-service[.]info
    inbox-drive[.]info
    inbox-sharif[.]info
    magic-delivery[.]info
    microsoftinternetsafety[.]net
    mobilecontinue[.]network
    mobile-messengerplus[.]network  
    

 ***参考来源：[clearskysec](https://www.clearskysec.com/wp-content/uploads/2019/10/The-Kittens-Are-Back-in-Town-2.pdf)，由Kriston编译，转载请注明来自FreeBuf.COM**  

