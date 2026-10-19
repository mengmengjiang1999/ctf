##

  

原创：h0x合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

![v2-b6ac4acb391e97c8ef3bf1f3f5fe9a62_hd.w](https://pic1.zhimg.com/80/v2-b6ac4acb391e97c8ef3bf1f3f5fe9a62_hd.webp)

前言

本文为实战过程中遇到的问题思考及记录，旨在与大家进行交流与分享。如观后有灵感一闪，请勿随意对互联网站点进行非法测试。

PS：截至投稿前，已将漏洞提交厂商并验证其已完成修复。

![v2-10e6c58b4c92b5f2d2a2997f12a5aa98_hd.w](https://pic4.zhimg.com/80/v2-10e6c58b4c92b5f2d2a2997f12a5aa98_hd.webp)

![v2-a17f39b0263ccd7b5082f9456ca34bcd_hd.w](https://pic4.zhimg.com/80/v2-a17f39b0263ccd7b5082f9456ca34bcd_hd.webp)

## 前期测试  

前期通过测试发现网站存在源码备份文件，可以直接下载网站源码。

链接：<http://www.abc.com/web.rar>

![v2-0d63de55e3902c92a1e47a286c9e8cf1_hd.w](https://pic1.zhimg.com/80/v2-0d63de55e3902c92a1e47a286c9e8cf1_hd.webp)

按照常规思路下载了源码后，查看里面的数据库即可知道管理员的密码，此处进行尝试。将asp后缀的数据库文件修改为mdb后缀打开

![v2-2cdf32cb3cd4f890ae0e8204d7ccc4e3_hd.w](https://pic4.zhimg.com/80/v2-2cdf32cb3cd4f890ae0e8204d7ccc4e3_hd.webp)

![v2-830eedb4e92aa6ecec0b2783fa5c1951_hd.w](https://pic4.zhimg.com/80/v2-830eedb4e92aa6ecec0b2783fa5c1951_hd.webp)

此时发现数据库的Admin_Pass的内容是18位长度类似MD5字符串，直接拿去CMD5解密是解密不了的。因为不是常规的16或32位密文。

![v2-2d034cadd362195eb35d5924a287a4e4_hd.w](https://pic2.zhimg.com/80/v2-2d034cadd362195eb35d5924a287a4e4_hd.webp)

通过查看源码，发现其验证方式如下：

![v2-4e186847f810853cdf02e2a31a5709b7_hd.w](https://pic1.zhimg.com/80/v2-4e186847f810853cdf02e2a31a5709b7_hd.webp)

通过Mid函数取32位MD5中第4位开始的18位字符串。

![v2-bf4dd73df11d94303ce4193bd4b64177_hd.w](https://pic3.zhimg.com/80/v2-bf4dd73df11d94303ce4193bd4b64177_hd.webp)

## 密码穷举  

由上述已经得到了密码的加密方法，通过编写个小脚本即可进行弱密码的穷举。如下：

![v2-694238c081158567462e657f90dfe967_hd.w](https://pic3.zhimg.com/80/v2-694238c081158567462e657f90dfe967_hd.webp)

使用上述穷举的弱口令用户登录后台管理，后台地址为admin。

![v2-336ae38979148abd7622af4a9a2ff6a8_hd.w](https://pic4.zhimg.com/80/v2-336ae38979148abd7622af4a9a2ff6a8_hd.webp)

![v2-f96429d6d7f893474b3566179c1ee5d5_hd.w](https://pic3.zhimg.com/80/v2-f96429d6d7f893474b3566179c1ee5d5_hd.webp)

登录后发现当前为受限管理员，很多功能无权限使用，抓包查看该功能请求。

![v2-76414b963e539cc834a8754982d59c38_hd.w](https://pic3.zhimg.com/80/v2-76414b963e539cc834a8754982d59c38_hd.webp)

发现cookie信息里有：

Angel_aspAdmin=UserName=zhanch&UserPass=adc3949ba59abbe56e&UserID=10

其中我们可以从数据库中获取到admin的UserPass及UserID，于是尝试替换是否能有权限访问该页面？于是进行测试：

![v2-9a2a17ec4257ff7ea832e6b69683453e_hd.w](https://pic2.zhimg.com/80/v2-9a2a17ec4257ff7ea832e6b69683453e_hd.webp)

替换后访问发现并没有成功，而是返回登录页面。

![v2-8eca10306f15d37895c9e4a1e29a2feb_hd.w](https://pic4.zhimg.com/80/v2-8eca10306f15d37895c9e4a1e29a2feb_hd.webp)

## 登录分析  

由于上述替换后并没有访问成功，于是结合源码进行登录分析。

![v2-6c565bfe558fb89ac49e7d356e05fbac_hd.w](https://pic2.zhimg.com/80/v2-6c565bfe558fb89ac49e7d356e05fbac_hd.webp)

通过上述代码，发现程序在判断是否已登录的操作，除了校验Cookie中的UserID、UserName、UserPass外，还会验证IP，这就是上述修改为admin的Cookie后返回登录页面的原因。

此IP的值是在每次登录的时候，在校验了账号密码正确后，会把登录客户端的IP更新同步到数据库中，代码如下：

![v2-c2602f41b1f88cd23f3705c03ea8a302_hd.w](https://pic3.zhimg.com/80/v2-c2602f41b1f88cd23f3705c03ea8a302_hd.webp)

![v2-03228edeccfa4c05aec2175e209f455f_hd.p](https://pic4.zhimg.com/80/v2-03228edeccfa4c05aec2175e209f455f_hd.png)

找到获取客户端IP的代码如下：

![v2-4de6dbacc4fd3cce85d12e6e4b5193d8_hd.w](https://pic3.zhimg.com/80/v2-4de6dbacc4fd3cce85d12e6e4b5193d8_hd.webp)

发现此处可以通过X-Forwarded-For的方式进行IP伪造。此处伪造IP为数据库里admin记录的IP。

![v2-e5822b50a7c100dea0daf4cabf2f3f9d_hd.w](https://pic4.zhimg.com/80/v2-e5822b50a7c100dea0daf4cabf2f3f9d_hd.webp)

成功返回了页面，说明admin管理员上次备份了网站后没有再登录过，或者admin登录的IP地址较固定。

此时开启X-Forwarded-For，并修改Cookie为：

Angel_aspAdmin=UserName=admin&UserPass=18cca7781212ba1922&UserID=1

即可以Admin管理员的权限管理网站。

![v2-13805815d637943dd538a148c48ac710_hd.w](https://pic1.zhimg.com/80/v2-13805815d637943dd538a148c48ac710_hd.webp)

如上，即使管理员密码破解不出来，若运气好，数据库记录的IP是管理员常登录的IP的情况下，用此方法也有几率登录管理后台。

![v2-bf6d294526f12eab48e6dc3b64acae96_hd.w](https://pic1.zhimg.com/80/v2-bf6d294526f12eab48e6dc3b64acae96_hd.webp)

## 后台GetShell  

登录管理后台后，数据库备份拿Shell是计算机基本操作，但此处也有坑点。正常来说上传图片马，通过数据库备份成asp后缀，即可拿Shell。但实际如下：

首先上传图片马

![v2-095fdd72c672de5812e993fe72f8d0bd_hd.w](https://pic2.zhimg.com/80/v2-095fdd72c672de5812e993fe72f8d0bd_hd.webp)

然后通过数据库备份成asp脚本

![v2-c921c4b0f11bee3e91d00d5b21c41d75_hd.w](https://pic4.zhimg.com/80/v2-c921c4b0f11bee3e91d00d5b21c41d75_hd.webp)

![v2-e042639d2f95a85c1f73e428debc8ddf_hd.w](https://pic2.zhimg.com/80/v2-e042639d2f95a85c1f73e428debc8ddf_hd.webp)

提示备份成功，但实际访问却是：

![v2-7c65fac13773ec67fb6a494f68af03ae_hd.w](https://pic2.zhimg.com/80/v2-7c65fac13773ec67fb6a494f68af03ae_hd.webp)

查看源代码后发现，当前数据库路径是写死的，所以再怎么改成图片文件路径也没有用，备份的还是原来数据库的文件。

![v2-4b8ce07e0ccb6f619c05d089b88fc768_hd.w](https://pic2.zhimg.com/80/v2-4b8ce07e0ccb6f619c05d089b88fc768_hd.webp)

![v2-d5e224b3ac9a275162eefd5519f1aa1c_hd.w](https://pic2.zhimg.com/80/v2-d5e224b3ac9a275162eefd5519f1aa1c_hd.webp)

去看备份的文件

![v2-2d1f93eb96412668b839e08713e71359_hd.w](https://pic3.zhimg.com/80/v2-2d1f93eb96412668b839e08713e71359_hd.webp)

看文件大小也就知道，这绝不是我们的图片马shell。

此处需用到恢复的功能进行GetShell，如下：

![v2-449f446f57547055d39b3587f3edc079_hd.w](https://pic4.zhimg.com/80/v2-449f446f57547055d39b3587f3edc079_hd.webp)

![v2-df6730f323ac03a1f91c838fb3e5ca63_hd.w](https://pic2.zhimg.com/80/v2-df6730f323ac03a1f91c838fb3e5ca63_hd.webp)

![v2-4822b4217d396c80c6b78f690109de6d_hd.w](https://pic4.zhimg.com/80/v2-4822b4217d396c80c6b78f690109de6d_hd.webp)

如上成功GetShell

![v2-a79f3ccfcdcddcfccf8d8e039e539803_hd.w](https://pic3.zhimg.com/80/v2-a79f3ccfcdcddcfccf8d8e039e539803_hd.webp)

后记

后来和小伙伴一起交流，问他思路，他说直接管理后台暴力破解登录后台。

![v2-ca6b91590904bcb24eeb1c894f617eb1_hd.w](https://pic3.zhimg.com/80/v2-ca6b91590904bcb24eeb1c894f617eb1_hd.webp)

后来回想了一下，当时第一次穷举并没有使用Top1000的弱口令，而是使用Top200的弱口令，导致我没有穷举到admin的密码。

其次当我看到后台有验证码时，就并未去验证其验证码是否会失效。

所以说，渗透测试是一门艺术，一千个观众眼中就有一千个哈姆雷特。有时候思路也是很重要的，得多思考多尝试，但总言之，不管黑猫白猫,能抓住老鼠就是好猫。

本文完。

声明：作者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关。

![v2-a8ab9696f562e16261e9d0cd503f046b_hd.w](https://pic1.zhimg.com/80/v2-a8ab9696f562e16261e9d0cd503f046b_hd.webp)

操作练习

暴力破解在渗透测试中的应用：只要你的字典足够强大，没有破解不了的密码！说的就是暴力破解攻击，暴力破解是一个经久不衰的攻击手段，是暴力美学黑客的最爱。

点击“[实验:公开课第八期|暴力破解在渗透测试中的应用(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECIDcee9-2e23-4a12-83b7-b2957dca9783)”，可预览学习（PC端操作最佳哟）

![v2-4263c8a24ab1b486dd0ca9cad88effce_hd.w](https://pic3.zhimg.com/80/v2-4263c8a24ab1b486dd0ca9cad88effce_hd.webp)

