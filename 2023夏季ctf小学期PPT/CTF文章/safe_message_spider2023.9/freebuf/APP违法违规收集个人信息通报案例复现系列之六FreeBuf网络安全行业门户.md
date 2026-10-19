# 收集使用个人信息的目的、方式、范围发生变化时，未以适当方式通知用户，适当方式包括更新隐私政策等收集使用规则并提醒用户阅读等

 **【评估依据】**

 **《** 中华人民共和国网络安全法》

《中华人民共和国个人信息保护法》

《App违法违规收集使用个人信息行为认定方法》（国信办秘字〔2019〕191号）

《信息安全技术个人信息安全规范》(GB/T35273-2020)

《关于开展 APP 侵害用户权益专项整治工作的通知（工信部信管函〔2019〕337号）》

《关于开展纵深推进 APP 侵害用户权益专项整治行动的通知（工信部信管函〔2020〕164号）》

 **【评估方法】**

查看隐私政策中是否写明关于隐私政策更新时如何通知用户的情况，并验证是否属实。

 **【注意要点】**

一定要写明，在哪种情况下会更新隐私政策，这个在《App违法违规收集使用个人信息自评估指南》中第18点有写。一般提醒用户的方式有公告、邮箱、短信、弹窗、首页滚动屏等。

 **【评估难点】**

一般情况下第三方是比较难验证提示方式是否如隐私政策所写的，需要App运营者自查。

 **【违规案例来源】**

来源链接：

**[https://mp.weixin.qq.com/s?__biz=Mzg3OTU5NDQ3Ng==∣=2247489547&idx=1&sn=8782915e23659d310749cd7b9233244c&source=41#wechat_redirect](https://mp.weixin.qq.com/s?__biz=Mzg3OTU5NDQ3Ng==&mid=2247489547&idx=1&sn=8782915e23659d310749cd7b9233244c&source=41#wechat_redirect)**
****

![1654735565_62a142cd739ee0ac2a2c8.jpg!small](https://image.3001.net/images/20220609/1654735565_62a142cd739ee0ac2a2c8.jpg!small)

样本下载链接：

<https://www.anxz.com/down/21259.html>

![1654735744_62a143807733b95f0e96e.jpg!small](https://image.3001.net/images/20220609/1654735744_62a143807733b95f0e96e.jpg!small)

 **【复现过程】**

 **软件名称**

|

千聊  
  
---|---  
  
 **应用类型**

|

网络社区、儿童教育  
  
 **包名**

|

com.thinkwu.live  
  
 **软件大小**

|

24.22MB  
  
 **软件版本**

|

4.1.5  
  
 **MD5**

|

ab72a03aea31c46fbb25645b52ffe84e  
  
 **SHA-1**

|

b3636de5f6fe3a86eab409e9a60d581933fae82f  
  
 **SHA-256**

|

34eb73e05a3626f723c6f59e33120ad872d44958b1993fdea351017136c04210  
  
 **签名信息**

|

CN=nenglong, OU=nenglong, O=nenglong.com, L=gd-zs, ST=cn-gd, C=86  
  
 **SDKVersion**

|

targetSDKVersion：26

MinSDKVersion: 16  
  
隐私政策访问链接：

[https://m.qlchat.com//privacy_policy.html](https://m.qlchat.com/privacy_policy.html)

![1654735773_62a1439d143eaeae5c081.jpg!small](https://image.3001.net/images/20220609/1654735773_62a1439d143eaeae5c081.jpg!small)

更新后的隐私政策中已经有收集使用个人信息的目的、方式、范围发生变化时，将通过更新本政策、弹窗、页面提示等方式另行向用户说明对应信息的收集目的、范围及使用方式，并为用户提供自主选择同意的方式，且在征得用户明示同意后收集、使用的条款说明。

![1654735796_62a143b46b7cd8c80bdb6.jpg!small](https://image.3001.net/images/20220609/1654735796_62a143b46b7cd8c80bdb6.jpg!small)

隐私政策中也有相应的隐私政策更新说明。

![1654735822_62a143ceb23576e95c2ee.jpg!small](https://image.3001.net/images/20220609/1654735822_62a143ceb23576e95c2ee.jpg!small)

更新的隐私政策中已经有对通报中提及的课程记录信息收集有说明，但复现过程未测试其收集课程记录是否会向用户弹窗等明示。

根据官网提示需要关注公众号并绑定手机号才能使用手机号登录。

![1654735843_62a143e311489df6e20f9.jpg!small](https://image.3001.net/images/20220609/1654735843_62a143e311489df6e20f9.jpg!small)

使用注册手机号登录

![1654735865_62a143f97f7b7193a6faf.jpg!small](https://image.3001.net/images/20220609/1654735865_62a143f97f7b7193a6faf.jpg!small)

在“我的课程”中可以看到课程记录，但是通过抓包等动态行为监测未发现其上传或者提示收集用户课程记录。

![1654735891_62a14413008f59927c9a4.jpg!small](https://image.3001.net/images/20220609/1654735891_62a14413008f59927c9a4.jpg!small)

![1654735913_62a14429463f03f1c2095.jpg!small](https://image.3001.net/images/20220609/1654735913_62a14429463f03f1c2095.jpg!small)

 **【复现结论】**

该APP已根据通报内容进行了隐私政策内容的更新，测试时版本为2021年 08月
25日发布版本，通报中提及的新增的定制化课表能中会收集课程记录未以任何方式告之用户，本次复现中由于隐私政策内容更新等原因，未复现通报内容。

![1654735942_62a14446d28a8ae257c2f.jpg!small](https://image.3001.net/images/20220609/1654735942_62a14446d28a8ae257c2f.jpg!small)

 **【参考链接】**

https://www.freebuf.com/articles/neopoints/253807.html

<https://blog.csdn.net/wutianxu123/article/details/113730098>

