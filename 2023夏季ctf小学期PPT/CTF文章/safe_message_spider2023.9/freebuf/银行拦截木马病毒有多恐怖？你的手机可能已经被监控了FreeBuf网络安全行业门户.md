## 一．简述  

**“银行拦截木马”病毒是一种精准钓鱼，窃取用户银行账户的病毒木马，涉案金额过亿。犯罪分子通过社会工程学手段获取到受害者的银行卡帐号密码，病毒木马伪装成银行应用、系统应用、照片等方式诱导受害者进行安装，通过隐藏图标潜伏在用户手机，激活设备管理器导致无法卸载，最后通过监控手机的银行短信验证码，实现窃取用户银行卡里的金钱。根据腾讯安全反诈骗实验室大数据显示，“银行拦截木马”主要分布在东南亚国家中：缅甸，马来西亚，日本，俄罗斯，尼日利亚，印尼。**

##  二．海外支付类病毒隐私收集方式

> *
> C&C服务器上传方式：伪装正常应用，使用虚假通知或者钓鱼页面诱导用户点击链接，窃取用户银行卡账号，银行密码，并且拦截短信，窃取通讯录，照片，GPS位置信息发送到远程服务器
>
> * STMP邮箱发送方式：通过隐藏后台潜伏在用户手机，拦截用户资金短信，窃取通讯录，通话记录，照片等以邮件方式发送

## 三．海外支付类病毒技术特点

> * 涉及敏感权限包括：短信读写权限、通讯录读取权限、打电话权限；并且注册大量的广播事件，实时监控受害用户手机
>
> * 钓鱼页面技术：C&C服务器云端下发展示内容伪造银行系统或社交网络登录，窃取用户隐私信息
>
> * 监控应用：上传用户手机中的银行软件，防病毒软件，社交软件，加密货币应用
>
> * 植入多个功能模块：银行木码中植入置顶勒索病毒模块，当用户卸载时激活勒索模块
>
> * 反分析技术：加壳，反仿真，加密，混淆等其他规避技术增加检测难度

![1.png](https://image.3001.net/images/20180420/15242063865015.png!small)

## 四.“银行拦截木马”申请的敏感权限

申请敏感权限包括：短信读写权限、通讯录读取权限、打电话权限；并且注册大量的广播事件，实时监控受害用户手机

![2.png](https://image.3001.net/images/20180420/15242063996853.png!small)

## 五.“银行拦截木马”使用技术点

![3.png](https://image.3001.net/images/20180420/15242064103980.png!small)

  

## 六. BankBot家族版本变化衍生

随着时间变化，基于社会工程学诈骗BankBot家族功能越来越丰富对抗成不断增加

![4.png](https://image.3001.net/images/20180420/1524206423388.png!small)

## 七．“银行拦截木马”仿冒软件名Top 20榜单

通常会伪装成各种正常的软件例如:相册、社交软件、杀毒软件、相册等

![5.png](https://image.3001.net/images/20180420/1524206433480.png!small)  

## 八.“银行拦截木马”地域分布趋势

主要分布在东南亚国家中：缅甸，马来西亚，日本，俄罗斯，尼日利亚，印尼，其中东南亚国家是近几年国内电信网络诈骗作案人员藏身之地。

![6.png](https://image.3001.net/images/20180420/15242064436839.png!small)  

## 九．“银行拦截木马”技术点：

9.1 接受C＆C服务器指令：

当用户手机设备接受到C＆C服务器指令做指定操作上传信息（上传短信，通讯录，照片，GPS位置信息等）

![7.png](https://image.3001.net/images/20180420/15242064896919.png!small)

9.2 劫持或者覆盖窗口、虚假“钓鱼”窗口

弹出警告虚假通知（标题：“紧急消息！”；“确认您的帐户”）诱导用户点击链接，进入钓鱼页面

虚假通知被翻译出七种语言（俄语，英语，土耳其语，德语，意大利语，法语，乌克兰语）

![8.png](https://image.3001.net/images/20180420/1524206498406.png!small)  

9.3 拦截资金验证码短信

![9.png](https://image.3001.net/images/20180420/15242065115323.png!small)

9.4
植入置顶勒索病毒模块，当用户取消设备管理器时自动激活置顶勒索病毒模块，强制将自身界面置于设备屏幕上方，致使用户无法正常使用设备，并以支付解锁对用户进行勒索。

![10.png](https://image.3001.net/images/20180420/15242065265713.png!small)

![11.png](https://image.3001.net/images/20180420/15242065395686.png!small)  

9.5 流氓申请激活设备管理器权限，连续频繁弹出窗口，直至用户点击激活

![12.png](https://image.3001.net/images/20180420/15242065503523.png!small)

![13.png](https://image.3001.net/images/20180420/15242065668792.png!small)

9.6 检测用户移动设备上安装的银行软件，防病毒软件，社交软件，加密货币应用发送到远程服务器，为后续仿冒应用推出新型病毒

![14.png](https://image.3001.net/images/20180420/1524206577288.png!small)

## 十．设备管理器清理方案：

无ROOT权限清除方案：

> * 使用adb命令行 “am force-stop 包名”可以强制关闭应用
>
> *使用手机管家查杀后即可查杀卸载病毒

![15.png](https://image.3001.net/images/20180420/15242065896464.png!small)

## 十一．安全建议

(1) 谨慎下载安装各类破解以及盗版应用,如破解的游戏等

(2) 建议从官方网站或正规应用市场下载安装应用,可以最大限度的保证下载应用的安全性

(3) 安装使用腾讯手机管家等安全软件对手机进行安全检测,开启病毒库的自动更新服务(务必开启云查杀功能),第一时间拦截存在安全风险的应用安装

“银行拦截木马”攻击目标银行类和支付系统，加密货币软件，社交软件，防病毒软件以下是详细列表：

银行应用和支付系统

> *Sbe*******Online – ru.**********mobile;
>
> *Sbe*******iness Online – ru. **********_sbbol;
>
> *Al****Bank - ru.al**********.android;
>
> * A****Business– ru.al**********do.amc;
>
> *Visa*****Wallet - r****w;
>
> * R******mobilebank – ru.ra**********news;
>
> *Ti***ff – com.id**********.android;
>
> *Pa***al – com.pay**********mobile;
>
> *Web***** Keeper – com.**********.my;
>
> *RO****Online – ru.ro**********oid;
>
> * V****Online– ru.vtb24. **********.android;
>
> * M****Bank– ru.si**********d.ui;
>
> *Ya****Money: online payments – ru. **********money;
>
> *Sberbank******ERBANK - ua.com.cs**********droid.sbrf;
>
> *Pr****t24 – ua. **********.ap24;
>
> *Ru*********mobile bank – ru.si**********bbank;
>
> * U***NK- financial supermarket - com. *****ksu;
>
> *Id*****Bank – com.a**********bank;
>
> * I**O– pl.**********iko;
>
> *Ba***SMS – com**********ms;
>
> * O****Smart– ua.com.cs.**********android.otp;
>
> * V******(Ukraine)– ua.v**********droid;
>
> *Osc*****24/7 – ua.os**********line;
>
> *Pla******Bank – com.tr**********atinum;
>
> *Un******Mobile – hr.ass**********a.mUCI.ua;
>
> *Raiff******Online – ua.pent**********production;
>
> *Uk******bank – com.ukr**********CardM;
>
> *St****Mobile – com.cofor**********android;
>
> *Ch****Mobile – com. **********roid;
>
> *Bank******Mobile Banking – com. ********.bofa;
>
> *We*******Mobile – com.w**********mobile;
>
> *TD*******tional – com.ws**********.tddii;
>
> *TD*******Trading – com. **********t.trader;
>
> *Ak*****Direkt – com.ak**************_direkt;
>
> *Ya*******Mobil Bankacılık – com. *****.android;
>
> * Ç*******OR – com. *********iscek;
>
> *JS*****BANK – com. **********.iscep;
>
> * İ******ep –com. ********iscep;
>
> * İ******et –com. *********isbankasi.

加密货币应用

> *Bi****nex - bitf*********app;
>
> *Bi****nium - veke*********rtex
>
> *Bit*******Widget - brot*********dget;
>
> *Bitcoin/**********ticker - master*********action;
>
> *Fl*******idget - leowa**********oinsw;
>
> *Bit*******Price - ozgu************ice;
>
> *Cry*******Prices All-in-One - coinp**********ges;
>
> *Block*****in – Bitcoin & Ether Wallet - block******droid;
>
> *Block*******Merchant - block*********chant;
>
> *WU*******paid - hyper************repaid;
>
> * B*******com– Bitcoin Wallet - block********wallet;
>
> * B*******FARI– Free Bitcoin - claimy*************fari;
>
> *Bit*******IQ - hand*************riceiq;
>
> *Bit*******allet - schil*************let;
>
> *Block*******Bitcoin / Altcoin App - block***********folio;
>
> *Bit*******Freewallet - org. ***********app;
>
> *Bit*******Crane - bit************.money;
>
> *Bit*******MarketCap.com (unofficial) / Altcoin - coin************app;
>
> *coinpay**************sapp (CoinPayments)
>
> *Bit************Freewallet - org. ************.app;
>
> *Coin*******Capp – Blockchain Cryptocurrencies - cenc***********tcapp;
>
> *Cry*******Story – Cryptocurrency Portfolio - benzne*************story;
>
> *Dogecoin Wallet - lang************let.

社交应用

> Wh******App- com.********sapp;
>
> P******Store– com.**************ding;
>
> Me******ger– com.**********orca;
>
> F*******ok– com.**************katana;
>
> Y*****be– com.**************youtube;
>
> U***er– com**********cab;
>
> V*****er– com***********voip;
>
> Sn*******at– com************android;
>
> In*******am– com***********android;
>
> i**o– com**************imoim;
>
> Tw*****r– com.**********android.

防病毒应用

> *Anti*******Light – com *********web;
>
> * C**********AntiVirus– com.**********security;
>
> *Kas**********Security – com.**********.free;
>
> *ES**********Antivirus – com.*********.ems;
>
> *Avast**********Antivirus – com.**********security;
>
> *Clean**********Antivirus – com. **********.mguard;
>
> *36**********Antivirus – com. **********.security;
>
> *AV**********Android – com.********virus;
>
> *Anti**********Cleaner – com.**********tivirus;
>
> *Sup**********Antivirus – com.**********.master;
>
> *Andro**********Android 2017 – com.**********.free;
>
> *Trust**********Mobile Security – com.**********.security;
>
> *Sop**********Security – com.**********.smse.

 ***本文作者：腾讯手机管家，转载请注明来自FreeBuf.COM**  

