# **概述** ****

近日，奇安信病毒响应中心发现Nemty勒索家族新变种开始肆虐，目前已经监测到国内有用户陆续中招，由于新变种暂无解密工具，我们提醒政企用户多加防范。

Nemty勒索在国内主要通过弱口令爆破的方式进行传播，本次捕获到的新变种为2.2版本，添加的文件名后缀.
NEMTY_<random{7}>。相较于之前版本，除了代码结构的改变，新变种同时提供了Tor浏览器和Web浏览器两种沟通模式，而且限定了交易时间，如果三个月内不支付赎金，网站将会停止支付赎金服务可能导致数据永久损失。

# 简要分析

Nemty自从被发现以来一直被修改，代码完成度不高，与流行的勒索家族相比成熟度较低，导致了其受到了地下分发商以及高级会员的怀疑，所以Nemty至今并没有大规模扩散的现象。但是自从十一月以来，根据奇安信多维度大数据关联分析，我们发现Nemty开始与Phorpiex僵尸网络进行合作。Phorpiex主要以分发色情邮件而闻名，在最近的更新中新增了SMB爆破模块，执行过程中会根据%appdata%目录下是否存在winsvcs.txt文件来判断Nemty是否已经下载。

![图片.png](https://image.3001.net/images/20191205/1575510690_5de862a2eabc1.png!small)

使用的SMB弱口令整理如下

![图片.png](https://image.3001.net/images/20191205/1575510698_5de862aa05da9.png!small)

如果爆破成功则会将Nemty传播到远程计算机，并重复检查Nemty进程

![图片.png](https://image.3001.net/images/20191205/1575510704_5de862b0c2ee8.png!small)

样本执行过程中会创建“just_a_little_game”互斥量

![图片.png](https://image.3001.net/images/20191205/1575510713_5de862b939ddd.png!small)

调用CMD删除卷影

![图片.png](https://image.3001.net/images/20191205/1575510719_5de862bf1f2b2.png!small)

获取本机相关信息

![图片.png](https://image.3001.net/images/20191205/1575510725_5de862c5230ec.png!small)

区域豁免

![图片.png](https://image.3001.net/images/20191205/1575510738_5de862d251c0b.png!small)

生成RSA密钥对

![图片.png](https://image.3001.net/images/20191205/1575510743_5de862d7bf8e7.png!small)

结束指定进程和服务

![图片.png](https://image.3001.net/images/20191205/1575510750_5de862dec102e.png!small)

创建注册表项写入相关信息

![图片.png](https://image.3001.net/images/20191205/1575510760_5de862e8283b0.png!small)

在每个目录下生成勒索信，内容如下

![图片.png](https://image.3001.net/images/20191205/1575510766_5de862ee20185.png!small)

之后开始加密文件，排除特定目录及文件

![图片.png](https://image.3001.net/images/20191205/1575510771_5de862f38c6a3.png!small)

完成之后向远程服务器发送信息

![图片.png](https://image.3001.net/images/20191205/1575510776_5de862f89deaf.png!small)

勒索网站页面如下

![图片.png](https://image.3001.net/images/20191205/1575510781_5de862fda4d9a.png!small)

# 小结

 **** 随着Nemty的代码越来越成熟，可以预见未来会有越来越多的地下分发商与之合作，奇安信病毒响应中心会持续对该勒索家族进行追踪。

目前奇安信集团全线产品，包括天擎、天眼、NGSOC、态势感知、威胁情报平台支持对涉及相关攻击活动的检测和相关勒索病毒的查杀。

# 安全建议

我们建议政企用户参考以下建议加强防范

1、 对重要数据和文件按时进行备份

2、 及时给电脑打补丁，修复漏洞

3、 不要点击来源不明的邮件，不要从不明网站下载软件（使用奇安信企业软件管家）

4、 关闭不必要的文件共享以及相关端口，如445，135，139等，如果业务没有需要的话尽量关闭3389端口或者给3389端口设置白名单配置。

5、 采用高强度的密码，不要使用弱口令，保证每台服务器的密码都不相同，每隔一段时间更换密码

# IOC

文件MD5：

fed493a6653bbe8f6ad456e2e0d1d5d3

钱包地址：

38rz9y1dZPTqM4s27PENRgmbyYeM7vhTii

域名：

nemty.top

nemty10.hk

