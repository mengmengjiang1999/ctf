Guildma是Tétrade银行木马家族中的一员，它活动频繁并处于持续开发状态。最近，他们的新恶意软件Ghimob
banking已经开始感染移动设备，其目标主要是巴西、巴拉圭、秘鲁、葡萄牙、德国、安哥拉和莫桑比克的银行、FinTech、交易所和加密货币等应用程序。

Ghimob感染完成后，黑客可以远程访问被感染设备，用受害者手机完成交易。如果用户设置了屏幕锁定，Ghimob可以录制屏幕并回放解锁。当攻击者进行交易时，木马会利用WebView覆盖主屏幕或全屏打开某个网站，在用户查看屏幕时，攻击者会在后台使用金融应用程序执行交易。

## 多平台金融攻击

在监视Guildma Windows恶意软件活动时，发现用于传播恶意软件的ZIP文件和APK文件的链接，所有文件下载链接都指向同一个URL。
如果点击恶意链接的用户使用的是Android的浏览器，则下载的是Ghimob APK。APK托管在Guildma注册的多个恶意域中，
安装完成后该应用程序将使用“辅助功能模式”来持久控制目标。

![1605659604_5fb46bd4f38fea9e73cf2.png!small?1605659605119](https://image.3001.net/images/20201118/1605659604_5fb46bd4f38fea9e73cf2.png!small?1605659605119)

受感染的国家/地区分布：

![1605659637_5fb46bf53c0bf73695469.png!small?1605659637474](https://image.3001.net/images/20201118/1605659637_5fb46bf53c0bf73695469.png!small?1605659637474)

为了诱使受害者安装恶意文件，电子邮件中提供了查看详细信息的链接，收件人可以通过链接查看更多内容，应用程序本身则伪装为Google
Defender，Google Docs，WhatsApp Updater等。恶意软件启动后会检查是否存在调试器， 如果存在则该自行终止。

![1605662190_5fb475ee34e08e20e4ded.png!small?1605662190443](https://image.3001.net/images/20201118/1605662190_5fb475ee34e08e20e4ded.png!small?1605662190443)

感染完成后，恶意软件向服务器发送消息，内容包括手机型号，是否有屏幕锁和已安装的应用程序列表。
Ghimob会监视153种应用程序，这些应用程序主要来自银行，金融科技，加密货币和交易所。

## 远程控制

安装完成后Ghimob会隐藏应用程序图标，解密硬编码的C2列表，并访问所有C2来接收真实的C2地址。

在分析的样本中，C2提供程序都是相同的，但真实的C2在不同样本之间有所不同，所有的通信都是通过HTTP / HTTPS协议完成。

![1605661393_5fb472d14a0232aae1e0b.png!small?1605661393488](https://image.3001.net/images/20201118/1605661393_5fb472d14a0232aae1e0b.png!small?1605661393488)

受害人列表

在[Financial Threat Intel
Portal](https://opentip.kaspersky.com/)报告中描述了RAT使用的所有命令。

    
    
    Client:[TARGETED APP]
    ID: xDROID_smg930a7.1.125_7206eee5b3775586310270_3.1 
    Data:Sep 24
    2020 3:23:28 PM 
    Ref:unknown SAMSUNG-SM-G930A 7.1.1 25
    KeySec:trueKeyLock:falseDevSec:trueDevLock:false 
    com.sysdroidxx.addons - v:3.1 
    Ativar Google Docs 
    =======================================
    Link Conexao:hxxp://www.realcc.com
    Senha de 8 digitos:12345678
    Senha de 6 digitos:123456
    
    =======================================
    ============== LOG GERAL ==============
    =======================================
    22{< x >}[com.android.launcher3]--[TEXTO:null]--[ID:com.android.launcher3:id/apps_list_view]--[DESCRICAO:null]--[CLASSE:android.support.v7.widget.RecyclerView]
    22{< x >}[com.android.launcher3]--[TEXTO:null]--[ID:com.android.launcher3:id/apps_list_view]--[DESCRICAO:null]--[CLASSE:android.support.v7.widget.RecyclerView]
    22{< x >}[com.android.launcher3]--[TEXTO:null]--[ID:com.android.launcher3:id/apps_list_view]--[DESCRICAO:null]--[CLASSE:android.support.v7.widget.RecyclerView]
    16{< x >}[targeted app]--[TEXTO:]--[ID:null]--[DESCRICAO:Senha de 8 digitos]--[CLASSE:android.widget.EditText]
    0{< >}[targeted app]--[TEXTO:null]--[ID:null]--[DESCRICAO:null]--[CLASSE:android.widget.FrameLayout]
    1{< >}[targeted app]--[TEXTO:null]--[ID:null]--[DESCRICAO:null]--[CLASSE:android.widget.LinearLayout]
    2{< >}[targeted app]--[TEXTO:null]--[ID:android:id/content]--[DESCRICAO:null]--[CLASSE:android.widget.FrameLayout]
    3{< >}[targeted app]--[TEXTO:null]--[ID:null]--[DESCRICAO:null]--[CLASSE:android.widget.FrameLayout]
    
    
    =======================================
    ================ SALDOS ===============
    =======================================
    [DESCRICAO: Rolando Lero Agencia: 111. Digito 6. Conta-corrente: 22222. Digito .7]--    [TEXTO:Account Rolando Lero]
    [DESCRICAO:Agencia: 111. Digito 6. Conta-corrente: 22222. Digito .7]--[TEXTO:111-6 22222-7]
    [DESCRICAO:Saldo disponivel
    R$ 7000,00]--    [DESCRICAO:7000,00]--[TEXTO:R$ 7000,00]
    [TEXTO:Saldo disponivel]
    [DESCRICAO:Agendado ate 04/Out
    R$ 6000,00 ]--    [DESCRICAO:6000,00 ]--[TEXTO:R$ 6000,00 ]
    [TEXTO:Agendado ate 04/Out]

Ghimob不会实时监控屏幕，而是读取目标应用程序中的文本信息进行有选择性的攻击。它会监视葡萄牙语中的以下单词：saldo（余额），investimento（投资），empréstimo（借出），extrato（声明）。

## IOC

> 17d405af61ecc5d68b1328ba8d220e24
>
> 2b2752bfe7b22db70eb0e8d9ca64b415
>
> 3031f0424549a127c80a9ef4b2773f65
>
> 321432b9429ddf4edcf9040cf7acd0d8
>
> 3a7b89868bcf07f785e782b8f59d22f9
>
> 3aa0cb27d4cbada2effb525f2ee0e61e
>
> 3e6c5e42c0e06e6eaa03d3d890651619
>
> 4a7e75a8196622b340bedcfeefb34fff
>
> 4b3743373a10dad3c14ef107f80487c0
>
> 4f2cebc432ec0c4cf2f7c63357ef5a16

## 原文链接

[securelist](https://securelist.com/ghimob-tetrade-threat-mobile-devices/99228/)

