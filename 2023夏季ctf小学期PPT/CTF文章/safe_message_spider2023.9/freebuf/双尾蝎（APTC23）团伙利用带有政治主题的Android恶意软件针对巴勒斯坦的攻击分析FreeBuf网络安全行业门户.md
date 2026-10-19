## 背景介绍

**2017年3月15日奇安信红雨滴高级威胁分析团队已经对APT-C-23做了详细的揭露，APT-C-23组织的目标主要集中在中东地区，尤其活跃在巴勒斯坦的领土上。2016年5月起至今，双尾蝎组织（APT-C-23）对巴勒斯坦教育机构、军事机构等重要领域展开了有组织、有计划、有针对性的长时间不间断攻击。攻击平台主要包括Windows与Android。**

Android恶意程序主要伪装成两类应用程序：一类为聊天工具，另一类为软件升级工具。其传播方式主要有两种：第一种方法是通过短信，其中包含指向Google云端硬盘的网址或托管APK的C＆C域名，第二种方法是将他们的应用程序上传到第三方应用商店。其中Android版本当时已经更新了两个版本，类名对应的功能如下图。

![](https://ti.360.net/uploads/2019/05/08/1b35f4f419c7a1a1f1a44e6764b99b8f.png)

近期Check
Point发现了APT-C-23使用了带有政治主题的诱饵PDF文件，使用了新的C2[frowtisice[.]club](https://frowtisice.club/Margarita)
。

![](https://ti.360.net/uploads/2019/05/08/775c61391ba2a61e01747ea217b2c6c1.png)

经过我们分析，新样本在原有的基础上功能进行了增加，代码结构、控制指令等都进行了巨大的改变，程序运行后会显示带有政治主题的诱饵PDF文件，而随着巴以冲突的持续升温，APT-C-23再次更新其目的也显而易见。

![](https://ti.360.net/uploads/2019/05/08/ce295dee5e177950614ebc504588d0da.png)

下图为样本运行以后带有政治主题的PDF诱饵文件：

![](https://ti.360.net/uploads/2019/05/08/3a34131e99133661ed750f05a311893f.png)

## 样本分析

APT-C-23新样本通过仿冒Acrobat更新，并通过显示含有政治主题的诱饵PDF文件，诱骗用户安装使用；恶意软件主要目的为窃取用户手机信息，并对用户手机进行远程控制，新程序继承了APT-C-23下发控制指令的模式，实现了两种向应用推送消息的方式，FCM和SMS通信，从而可以更加稳定的接收到控制指令；程序运行以后会隐藏自身图标，从而保护自身不被卸载；程序会通过两种方式下发控制指令，两种方式下发的指令其功能类似，例如：开始对用户手机进行录音，上传用户手机短信，上传用户手机通讯录，上传用户手机文件等操作。

恶意程序运行界面：

![](https://ti.360.net/uploads/2019/05/08/d9dc31f1374acff0741c597dc7f266dd.png)

程序运行后隐藏自身图标：

![](https://ti.360.net/uploads/2019/05/08/79aaba9ee56c923f3480f170264260b9.png)

APT-C-23实现了两种向应用推送消息的方式，FCM和SMS通信，从而可以更加稳定的接收到控制指令。

### 通过SMS的控制指令下发

SMS控制指令：

![](https://ti.360.net/uploads/2019/05/08/9d3fff535cfbb03c62e9159b0f817ecf.png)

控制指令 | 指令含义 | 控制指令 | 指令含义  
---|---|---|---  
#.= | 开启录音，并上传录音 | 52115 | 启用更新通知  
#,, | 停止录音 | 52116 | 禁用更新通知  
52101 | 启动应用程序 | 52117 | 启用新的URL  
52102 | 关闭应用程序 | 52118 | 上传手机文件  
52103 | Enable Mobile Data | 52119 | 获取控制指令  
52104 | Disable Mobile Data | 52120 | 获取录制的内容  
52105 | 卸载应用程序 | 52121 | 未启用功能  
52106 | 删除录音文件 | 52122 | 获取短信通信记录  
52107 | 开启WiFi |  |  
52108 | 重启录音功能 |  |  
52109 | 取消更新 |  |  
52110 | 获取用户手机已安装程序信息 |  |  
52111 | 禁用第一次更新 |  |  
52112 | 启用第一次更新 |  |  
52113 | 获取所有短信内容 |  |  
52114 | 获取手机通讯录 |  |  
  
通过短信下发指令：

![](https://ti.360.net/uploads/2019/05/08/cfba0ff6b99a62e5a38dd4e542728e71.png)

指令：#.=

![](https://ti.360.net/uploads/2019/05/08/36e195ec1007e33fb75a883b7b6c6712.png)

指令：#,,

![](https://ti.360.net/uploads/2019/05/08/aabb4ffc81746c9cdd7bb2084a564945.png)

指令：52101

![](https://ti.360.net/uploads/2019/05/08/a50e571fcbd6c53b709173ee64baf42f.png)

指令：52102

![](https://ti.360.net/uploads/2019/05/08/c464182c7883c4e92718f671fb7056d6.png)

指令：52103

![](https://ti.360.net/uploads/2019/05/08/53cab29e58adca19af01ef066e4f8715.png)

指令：52104

![](https://ti.360.net/uploads/2019/05/08/c08ec1867bc7486e253be91504eb5ca3.png)

指令：52105

![](https://ti.360.net/uploads/2019/05/08/3918a076e99d235fa5471f7fd5ed0415.png)

指令：52106

![](https://ti.360.net/uploads/2019/05/08/9e795cea4c296a6be6b8c18186b492ef.png)

指令：52107

![](https://ti.360.net/uploads/2019/05/08/ab7d701923900df22ce3cd96afbef9e0.png)

指令：52108

![](https://ti.360.net/uploads/2019/05/08/24b82d509c2420c3a437adbcd0e4f497.png)

指令：52109

![](https://ti.360.net/uploads/2019/05/08/16c75ad9eae0bd34502c6c2d8ec1e1ae.png)

指令：52110

![](https://ti.360.net/uploads/2019/05/08/ca005a2eb2cba2607e5c3cd8c84c837f.png)

指令：52111

![](https://ti.360.net/uploads/2019/05/08/bf335ba709b42d82e4f8e9d3a765e1ff.png)

指令：52112

![](https://ti.360.net/uploads/2019/05/08/3e4928b1c73eea38d7ef080d9d96e3c9.png)

指令：52113

![](https://ti.360.net/uploads/2019/05/08/2890f49e8ffec8a65eda05a1bf1b07a0.png)

指令：52114

![](https://ti.360.net/uploads/2019/05/08/d5da36ecf7f4cac111ff6f4f0c5d251f.png)

指令：52115

![](https://ti.360.net/uploads/2019/05/08/1a96b2807165d35be08b0f0ce628e9ce.png)

指令：52116

![](https://ti.360.net/uploads/2019/05/08/d9f5a7d07142819bf90fffba65758410.png)

指令：52117

![](https://ti.360.net/uploads/2019/05/08/fc7e4723d2cb58346e96d092ee00f82c.png)

指令：52118

![](https://ti.360.net/uploads/2019/05/08/361390423939185eeb774f23563d7806.png)

指令：52119

![](https://ti.360.net/uploads/2019/05/08/891f2ea63a2f9935023c6d784c2dfdad.png)

指令：52120

![](https://ti.360.net/uploads/2019/05/08/a72ffb196f5c025279806fc72921779f.png)

指令：52121

![](https://ti.360.net/uploads/2019/05/08/319eaa66cca527e9852bcfe967d18014.png)

指令：52122

![](https://ti.360.net/uploads/2019/05/08/729b9ec4228bd1d5db6078d17a595a71.png)

### 重要代码截图

获取用户短信：

![](https://ti.360.net/uploads/2019/05/08/a88e1aa243d937383863c21d727e3ea6.png)

获取用户手机通讯录：

![](https://ti.360.net/uploads/2019/05/08/1e2e29fac02e5a664f20f9fb7cc24b1e.png)

上传URL：<https://frowtisice.club/Margarita>

![](https://ti.360.net/uploads/2019/05/08/a9a1e6feb888fec5d109c5103d6a4c57.png)

![](https://ti.360.net/uploads/2019/05/08/e649c6be1893930dc8f968d440e46da6.png)

### 通过FCM的控制指令下发

控制指令 | 指令含义  
---|---  
Eduardo | 检测更新  
JadisWalsh | 申请权限 统计短信、通讯录  
EzekielMonroe | 检测录音文件是否存在  
LizzieHenry | 开始录音并上传录音  
CarlRhee | 开启WiFi  
RositaPorter | 开启WiFi  
BethAaron | 对用户手机呼叫转移  
HershelJones | 无实际功能  
AndreaGrimes | 获取用户手机短信、获取用户通讯录  
Stookey | 上传手机文件  
SimonBlake | 停止录音并上传文件  
OliviaKal | 停止录音  
FrancineGary | 停止录音  
TanyaSubramanian | 仿冒Facebook、WhatsApp、GooglePlay、Messenger、Instagram更新  
update | 仿冒Facebook、WhatsApp、GooglePlay、Messenger、Instagram更新  
Michonne | 卸载程序  
TobinSpencer | 监控电量变化  
LoriHarrison | 上传手机固件信息  
MaggieChambler | 获取连接状态  
SashaGreene | 发送申请状态  
Barbara | 电话呼叫转移  
JessieMonroe | 电话呼叫转移  
LydiaAnderson | 手机回到主界面、可隐藏APP图标、设置隐藏时间等  
DeannaAnderson | 上传录音  
PatriciaKent | 上传手机各种文件  
DianneJared | 计算空间  
DeniseAnderson | 未启用功能  
TammyJed | 未启用功能  
MagnaRose | 未启用功能  
AmyLuke | 上传/android/main/recordHis下文件  
KarenOscar | 未启用功能  
AratBertie | 未启用功能  
TamielBrion | 未启用功能  
SophiaAxel | 卸载程序  
CyndieSamuels | 删除文件  
LauraPeletier | 设置响铃模式  
GoTesna | 未启用功能  
MariDuncan | 未启用功能  
  
指令：Eduardo

![](https://ti.360.net/uploads/2019/05/08/659ea898d81b57f19f9af04b75f80ea1.png)

指令：JadisWalsh

![](https://ti.360.net/uploads/2019/05/08/750fc3a36defef3760228ec6e1ce4d4b.png)

指令：EzekielMonroe

![](https://ti.360.net/uploads/2019/05/08/8514c7966bb17ceffcb8b1cd5ce206fa.png)

指令：LizzieHenry

![](https://ti.360.net/uploads/2019/05/08/a28f8e1d9d868d3b75c8fc521cae8888.png)

指令：CarlRhee

![](https://ti.360.net/uploads/2019/05/08/e63d4145aff1cabd641793803d3a8cc3.png)

指令：RositaPorter

![](https://ti.360.net/uploads/2019/05/08/65fac70512de661f4e05d1d6e816ef9c.png)

指令：BethAaron

![](https://ti.360.net/uploads/2019/05/08/bc351d36e28674169dd5d2355fa49fb2.png)

指令：HershelJones

![](https://ti.360.net/uploads/2019/05/08/0d1c6d95fac7b2dec76cf498a34cc742.png)

指令：AndreaGrimes

![](https://ti.360.net/uploads/2019/05/08/80483972e9b643b67dd5f1487541c9fd.png)

指令：Stookey

![](https://ti.360.net/uploads/2019/05/08/bafd2d635f8e1c6e2c4e187c06987a8f.png)

指令：SimonBlake

![](https://ti.360.net/uploads/2019/05/08/6955f41ffdb307d7eddd0baa142683ae.png)

指令：OliviaKal

![](https://ti.360.net/uploads/2019/05/08/8603f9ef20b523f1ecd9fef2c7832c26.png)

指令：FrancineGary

![](https://ti.360.net/uploads/2019/05/08/ca0d53a8aaceec50c1b86e52b036c3bb.png)

指令：TanyaSubramanian

![](https://ti.360.net/uploads/2019/05/08/28138d9f8c4c8b8aa94f7ce4313b2258.png)

指令：update

![](https://ti.360.net/uploads/2019/05/08/b3c1ce49746736efda1153e076e6f8c9.png)

![](https://ti.360.net/uploads/2019/05/08/7c2e8c9a78f93bb8a77e79601a779b85.png)

![](https://ti.360.net/uploads/2019/05/08/070eab70ff1dee56eabd27a04939c94d.png)

![](https://ti.360.net/uploads/2019/05/08/cca8e26d1be9e46e5b6600333002f23e.png)

指令：Michonne

![](https://ti.360.net/uploads/2019/05/08/80bd635cc8f8258dea3283a7897c32a0.png)

指令：TobinSpencer

![](https://ti.360.net/uploads/2019/05/08/cd29efbbec561ed3a2cb2c3238eaae5a.png)

指令：LoriHarrison

![](https://ti.360.net/uploads/2019/05/08/17b5d2092245f8acd36ebb4264474680.png)

指令：MaggieChambler

![](https://ti.360.net/uploads/2019/05/08/bd4b90dd263af8821875e47177b9fc1b.png)

指令：SashaGreene

![](https://ti.360.net/uploads/2019/05/08/4e464d91c179726b6ff46a67b90c3ec1.png)

指令：Barbara

![](https://ti.360.net/uploads/2019/05/08/23c35af7ecd46382ee5d44710a84d696.png)

指令：JessieMonroe

![](https://ti.360.net/uploads/2019/05/08/f72b283ea2add9ee8a1c38ed91826c54.png)

指令：LydiaAnderson

![](https://ti.360.net/uploads/2019/05/08/dbecf4cbd11ac09959fe0956030885ac.png)

指令：DeannaAnderson

![](https://ti.360.net/uploads/2019/05/08/a030d2ecf7d5666bd960c7513e3e9a1c.png)

指令：PatriciaKent

![](https://ti.360.net/uploads/2019/05/08/ccea6a88a39daf4f71373392dd94e320.png)

指令：DianneJared

![](https://ti.360.net/uploads/2019/05/08/d7ecb3d8de3c1bcf4586c9add5861df1.png)

指令："DeniseAnderson

![](https://ti.360.net/uploads/2019/05/08/9eb4843fe0df13fb4ee55a08fb5a8289.png)

指令：TammyJed

![](https://ti.360.net/uploads/2019/05/08/c29225ed4df4508de39f7667998a3f87.png)

指令：MagnaRose

![](https://ti.360.net/uploads/2019/05/08/dbfb59161b6cc3f5fdd2a33767bda124.png)

指令：AmyLuke

![](https://ti.360.net/uploads/2019/05/08/0422e9d51ea9b756cbb35da4a88aa23d.png)

指令：KarenOscar、AratBertie、TamielBrion

![](https://ti.360.net/uploads/2019/05/08/9f1ed15122d94b0dce9c6a5005cd02ee.png)

指令：SophiaAxel

![](https://ti.360.net/uploads/2019/05/08/e9bad074046a5be64a68e1a9c4aaccc1.png)

指令：CyndieSamuels

![](https://ti.360.net/uploads/2019/05/08/9a32a5356afab9004e0aecb903ee866e.png)

指令：LauraPeletier

![](https://ti.360.net/uploads/2019/05/08/4bca1983943654b91c37e7265772f496.png)

指令：GoTesna、MariDuncan

![](https://ti.360.net/uploads/2019/05/08/61a949831df7b7141de4aebd14ee3163.png)

### 重要代码截图

遍历手机文件：

![](https://ti.360.net/uploads/2019/05/08/dadc0e70b1cf4f55fa2b56c0a364c7ff.png)

删除临时文件，随机释放空间，为上传文件做准备：

![](https://ti.360.net/uploads/2019/05/08/84777a18fd314f8f0976763d61efcb69.png)

获取短信：

![](https://ti.360.net/uploads/2019/05/08/ab8161ab69b6507c118aeb368b00608c.png)

获取通讯录：

![](https://ti.360.net/uploads/2019/05/08/94ba72fe16f456915bca45bbece383a7.png)

## 总结

中东地区沟通了欧亚非，地理位置十分重要，而由于石油资源、宗教信仰、地缘政治、历史原因等问题又常年战乱不断。随着手机的普及与移动互联网的发展，移动平台已经成为了APT攻击的新战场。APT-C-23常年持续对巴勒斯坦多个重要领域进行攻击，而此次在巴以双方摩擦不断的情况下，APT-C-23移动端再次更新，并且使用了带有政治主题的PDF诱饵样本，诱骗用户安装使用。所以移动APT的更新速率以及实时性值得我们关注，我们也会时刻关注APT-C-23
Windows 与 Android最新变种的出现。

## IOC

样本Hash：  
---  
8B48CEC7CB30FF0F02B06C51AA15F24F  
9a8bb68564c8cd38e47a91c816776a84d78dfe5bd35cd014400e87cb76ca9440  
cf2d7545b1f5ec57142727f795e07e85b84cbfe9a8b9f75aa5219495c746d853  
e7d7f110369a67dd1129c5fbd38daeadcc01c2ab3ced98e2a3135283678e1914  
461e9c8fb2b0a049df3b5fccd9c453c65d30ee02699f715da09796a5bb236f7c  
0537cdd971843545ce569415226dfabd1053a149a2586f163b58f7cb46e80ac5  
16327e5fbb60bc8f57ba2bbfe02c0464ce0755312a10f566cd7123cf978160d3  
2240c56c98c90acc0cbc58ba0ea6f7d78bb2f80d97f5c23e2a6e0ba5e2db4960  
46976081c1bcec4daa9701fbe373010c0bcb17463359a91556f09339522b6a13  
1995f315d0431141b25dd2962a2b517bc27d0ba694fddf982d970f512f784945  
e0e1addc23a032b538a344498e862b808e767ce8bed9412dd8990d00b1d64b34  
79947899241dde6bb6c3b82d8a0841928fa25333909907ddafeddcc987d37fb9  
d6a7c537a3101c38d0bafdcde685ad97ebc15ecac6bfa6eacba80b933ae8a151  
fe074e77cf64227b6f79d08cae573dd8d48e32e72abf8482a1a4d7a6e42b4f2d  
56f13b40f115af5114445d6ea04e5c00b19302ec4425e1995e423f0cd4cc3cf0  
14b739028e1e85a95cd2efc4019fdae9a49622afe07d8ef542634b1908baedee  
51e2630f942578d81ed000aa8a7b5ff7e19608a53323092ba72bc3b686614e25  
adcc3186e92f9ffe6277443b918cef997f2debbd84f7ccba974ab89bedfe90a3  
76962d334b894349a512d8e533c8373b71389f1d20fd814cd8e7ecc89ed8530a  
7e4a5c61a6d7718381884ac7675f335282169641518379ea921731cf08c95b49  
4b5dafd98fdffe2736787281db233f8f1e904b05e70acbfa2358cb901269d039  
1702b7038a1a1dc514054d3070939b4c1fabf3b51a0192d64dcd4f934c27b3ca  
c38d2a739d9a4e7df51176c95abc43ba606928c5d88b3ebcd7202dbaa0499e35  
86e453b251707eb2b73a3f547d7ed34af2b850fd9d319143c22778dd73066901  
91cbeb6b02575423621e0a0871efca3b6d25004ce9c1700b97748e2d330b60fb  
2ff47bb5ce6baacba85047c43afe1f3a7f034f1dd547c385394055afa4ba64bc  
4ebb385b0bf460d8561c39af8b69144bfe8c7a4d8607b157784674de653b9a05  
6bdf6f1d5a8a4c94589ab9f1d40db7e7710bae82f143209f058b6e0b8f25884d  
6665a99e53b2d28497e4edba4c67b8e587b9291d524c737235c69379a00190ae  
183ec1960e40b0831fbc47bbd87de530a1f92de02b1a60eb91771ef5d7dd016b  
4842cff6fc7a7a413ceed132f735eee3121ffb03f98453dae966f900e341dd52  
cc40a67b3844116c594fd192055d62498f9907d46cc84afd6bfaefa3b6b665a9  
27d89d88db6fe1365e2c1ded2e8af805c353d741bfd45023e9f67e2cc8c4d28e  
1a9d5717622111e73cd11617bf29b9e8e9c50a83b90c85dee909faad24684585  
7752f5662d904a261eb57a948278d0804efef827c1bec6337e6b210a00635a27  
ddfe29e690f8ecd08c6efd304ac89283967b63e9e0ea508d8b69ab4a5365f038  
bdea751c2e106a4f83d8ba32b1f193a3aa65bf3aba4405e025887bb66cb7a0c3  
371f13e4dacb0a740752a2352f09804bae99887b833c6989feb211702b3679cb  
93a21428286602cfe02380a33411cb9d25004f627c685b4363e9ffb3baa5f201  
dd21373738175567c92de2031e9efce761ba8d1fe6c6e04e69648e7528eed309  
d16b235d931d4eecb38365af538be023bebdb547f8aadf69de4aadfabc65620a  
8d184f24277ace3dd55811c3ed5b810eaa34a1c9bff0de2a15eb996134e9e241  
1b3fddc07f524b22559a6c6688ff90fd0e7f035a5ac36237be5e28a10887e928  
C&C  
---  
frowtisice.club  
  
## 参考信息

<https://www.freebuf.com/articles/system/129223.html>

<https://www.jianshu.com/p/702ddf8dd51c>

<https://www.symantec.com/blogs/expert-perspectives/ongoing-android-malware-campaign-targets-palestinians-part-2>

 ***本文作者：奇安信威胁情报中信，转载请注明来自FreeBuf.COM**

