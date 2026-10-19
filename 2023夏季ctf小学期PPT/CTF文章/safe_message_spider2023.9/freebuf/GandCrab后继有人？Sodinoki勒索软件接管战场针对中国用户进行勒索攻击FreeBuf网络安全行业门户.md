**背景**

近日，奇安信威胁情报中心红雨滴安全研究团队(RedDrip)监测到了针对中国用户投递的且带有中文诱饵的压缩包样本，经分析后确认压缩包内为Sodinokibi勒索病毒。在进行关联分析之后，我们发现诱饵文件与上月初我们捕获到的投递GandCrab[1]的诱饵文件之间存在某些相似的地方，不排除这两起攻击活动由同一个团伙运营，或两者之间联系紧密，有一定程度的人员重合。

Sodinokibi最早在今年4月份被Talos发现[2]，当时攻击者通过WebLogic服务器零日漏洞CVE-2019-2725发起攻击并投放该恶意负载。他们在分析时发现攻击者在植入Sodinokibi数小时后又植入了GandCrab
v5.2勒索病毒，并猜测这一异常事件可能是因为新样本Sodinokibi在当时没有达到攻击效果，因此再次使用GandCrab来进行钱财勒索。Tesorion在后续的分析报告中，进一步指出了这两个家族在随机URL生成方面的相似性。在本文中我们将指出两者在诱饵文件方面的相似之处，尽管尚无法确认二者的关联，但相信随着更多新线索的出现，真相将逐渐显现出来。

几天前，GandCrab的作者在表示将停止运营该勒索病毒并退休[4]，然而Sodinokibi等新样本的出现表明这并不代表勒索类恶意样本的影响会因此而减少。GandCrab即便真的退出，其一年狂卷25亿美元的“辉煌”业绩并成功逃脱法律制裁，只会更多激励后来者沿着这个技术路线和勒索模式继续作恶，我们绝没有放松警惕的借口，与勒索的搏斗只会持续加强。

##  **诱饵分析** ****

MD5|  12befdd8032a552e603fabc5d37bda35  
---|---  
文件格式| Email  
  
通过邮件分析，红雨滴团队发现此次攻击疑似针对国内游戏测评公司任玩堂（[www.appgame.com](http://www.appgame.com)），邮件伪装成DHL货物交付延迟通知，获取受害者信任并诱使打开。

![](https://ti.qianxin.com/uploads/2019/06/04/ef6b3f24998f9dfd8dfd1c9c612ac919.png)

附件为压缩包，内含四个文件，可执行文件的属性设置为隐藏，因此正常用户在默认设置情况下是无法看到可执行程序的存在，只能看到两个快捷方式。在设置显示隐藏文件后能看到所有的相关文件：

**![](https://ti.qianxin.com/uploads/2019/06/04/57ab8e6b3079dabdff3c9824d328796b.png)  
**

##  **样本** **分析** ****

文件名|  重要信息.doc.exe/聯繫方式.doc.exe  
---|---  
MD5| e08d8c6d2914952c25df1cd0da66131b  
  
伪装成Office Word的病毒样本首先解密一段ShellCode，并跳转执行该ShellCode：

![](https://ti.qianxin.com/uploads/2019/06/04/00a24aa89e2c2c099f8b00d82852f2ca.png)
![](https://ti.qianxin.com/uploads/2019/06/04/7347d582af94b95d4cd98543447137ce.png)

ShellCode主要功能为解密核心PayLoad并跳转执行：

![](https://ti.qianxin.com/uploads/2019/06/04/d06c9882473a254aa7734642fd81938f.png)

核心PayLoad为sodinokibi勒索病毒，动态解密修正137处IAT：

![](https://ti.qianxin.com/uploads/2019/06/04/109de9429d92d1b8020bc8f9bf9419d5.png)

紧接着创建互斥，保证只有一个实例运行：

![](https://ti.qianxin.com/uploads/2019/06/04/930d75bba974c9df8e7c031c2aee4cb9.png)

之后解密配置信息，解密函数如下：

![](https://ti.qianxin.com/uploads/2019/06/04/0fa0b4c18989cf8e8b6f17a94983b3b7.png)

解密的配置信息包括公钥、白名单目录、白名单文件、白名单后缀、域名、要结束的进程等信息：

![](https://ti.qianxin.com/uploads/2019/06/04/b323aaa85e1d30b0f29abcb6a9c90153.png)

然后将公钥、加密后的后缀等信息保存到注册表HKEY_LOCAL_MACHINE\SOFTWARE\recfg：

![](https://ti.qianxin.com/uploads/2019/06/04/dbe8c1e72bee6d3dc8c531163e2df828.png)

并通过GetKeyboardLayoutList获取键盘布局信息，当遇到下列语言环境时则不进行文件加密：

![](https://ti.qianxin.com/uploads/2019/06/04/d77b7c791ece3ab6de5e780b861641da.png)

判断操作系统位数：

![](https://ti.qianxin.com/uploads/2019/06/04/30df260fea17feaa01d43581bf02160e.png)

![](https://ti.qianxin.com/uploads/2019/06/04/423d2c72b4535865afc3ef5d67d910a2.png)

判断当前进程是否存在配置文件中需要结束的进程，若有则结束该进程

![](https://ti.qianxin.com/uploads/2019/06/04/76dbacabf54e337b3b95d0e944c8f7fe.png)

并通过执行CMD命令删除卷影文件防止用户恢复被加密的文件：

![](https://ti.qianxin.com/uploads/2019/06/04/1a96e7d01da5b646133f2824cf8d1c90.png)

删除备份文件：

![](https://ti.qianxin.com/uploads/2019/06/04/fce42c9d19efa91dc95a6592b827135c.png)

并在每个目录下生成勒索相关信息：

![](https://ti.qianxin.com/uploads/2019/06/04/537cfbbd19e67568062e8c26fc49527a.png)

最终加密除白名单配置以外的所有文件，将加密后的文件设置为之前保存在注册表中的随机后缀：

![](https://ti.qianxin.com/uploads/2019/06/04/93689423a0adfe3802e8175a17b8d73f.png)

加密结束后，改变桌面背景，显示勒索信息：

![](https://ti.qianxin.com/uploads/2019/06/04/d35e86bc4ab2cb980bcf529d283fc5c5.png)

最后尝试连接配置文件中的域名，发送受害者计算机基本信息：

![](https://ti.qianxin.com/uploads/2019/06/04/38c2d9df14bec99f79c759881633ca96.png)

## **关联分析** ****

2019年5月，奇安信红雨滴安全团队发布了《卷土重来！中文诱饵Gandcrab勒索软件肆虐五月初》分析文章，有趣的是我们发现这两次的攻击的投递方式几乎一模一样：

![](https://ti.qianxin.com/uploads/2019/06/04/bd895bcc387733c756ee387ce7178a0e.png)

且其快捷方式都泄露了攻击者的电脑名，都为win-0ev5o0is9i7

![](https://ti.qianxin.com/uploads/2019/06/04/3e2714cfbfc800343160ffeb70465753.png)

通过该电脑名我们发现近期韩国ESTsecurity也披露了针对韩国境内传播Sodinoki勒索病毒攻击活动，其攻击手法与此次攻击活动一致，且快捷方式中泄露的电脑名也为win-0ev5o0is9i7

![](https://ti.qianxin.com/uploads/2019/06/04/abcd76902de05164893af2e873c1d287.png)

## **防护建议** ****

1\. 尽量关闭不必要的端口，如 445、135，139 等，对 3389、5900 等端口可进行白名单配置，只允许白名单内的 IP 连接登陆。

2\. 采用高强度的密码，避免使用弱口令密码，并定期更换密码。

3\. 安装奇安信天擎新一代终端安全管理系统。

4\. 及时更新软件，安装补丁。

##  **总结** ****

由于Sodinokibi会通过电子邮件传播，我们建议您不要打开任何未知来源的电子邮件，尤其是不要打开附件。即使附件来自常用联系人，我们也建议您在打开之前，使用奇安信天擎对其进行扫描，以确保它不包含任何恶意文档或文件。

奇安信威胁情报中心RedDrip安全研究团队最后再次提醒各企业用户，加强员工的安全意识培训是企业信息安全建设中最重要的一环，如有需要，企业用户可以建设态势感知，完善资产管理及持续监控能力，并积极引入威胁情报，以尽可能防御此类攻击。

目前，基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对Sodinokibi的检测。

##  **参考链接** ****

[1].[
_https://mp.weixin.qq.com/s/TKZN9Qvcf_qqikeurdHBpg_](https://mp.weixin.qq.com/s/TKZN9Qvcf_qqikeurdHBpg)

[2]. [_https://blog.talosintelligence.com/2019/04/sodinokibi-ransomware-exploits-weblogic.html_](https://blog.talosintelligence.com/2019/04/sodinokibi-ransomware-exploits-weblogic.html)

[3]. [_https://www.tesorion.nl/aconnection-between-the-sodinokibi-and-gandcrab-ransomware-families/_](https://www.tesorion.nl/aconnection-between-the-sodinokibi-and-gandcrab-ransomware-families/)

[4]. [_https://www.zdnet.com/article/gandcrab-ransomware-operation-says-its-shutting-down/_](https://www.zdnet.com/article/gandcrab-ransomware-operation-says-its-shutting-down/)

[5]. [_https://blog.alyac.co.kr/2344_](https://blog.alyac.co.kr/2344)

## **附录** ****

 **红雨滴高级威胁研究团队（RedDrip Team）** ****

奇安信旗下的高级威胁研究团队红雨滴（RedDrip
Team，@reddrip7），持续运营奇安信威胁情报中心至今，专注于APT攻击类高级威胁的研究，是国内首个发布并命名“海莲花”（APT-C-00，OceanLotus）APT攻击团伙的安全研究团队，也是当前奇安信威胁情报中心的主力威胁分析技术支持团队。

目前，红雨滴团队拥有数十人的专业分析师和相应的数据运营和平台开发人员，覆盖威胁情报运营的各个环节：公开情报收集、自有数据处理、恶意代码分析、网络流量解析、线索发现挖掘拓展、追踪溯源，实现安全事件分析的全流程运营。团队对外输出机读威胁情报数据支持奇安信自有和第三方的检测类安全产品，实现高效的威胁发现、损失评估及处置建议提供，同时也为公众和监管方输出事件和团伙层面的全面高级威胁分析报告。

依托全球领先的安全大数据能力、多维度多来源的安全数据和专业分析师的丰富经验，红雨滴团队自2015年持续发现多个包括海莲花在内的APT团伙在中国境内的长期活动，并发布国内首个团伙层面的APT事件揭露报告，开创了国内APT攻击类高级威胁体系化揭露的先河，使之成为国家级网络攻防的焦点。

![](https://ti.qianxin.com/uploads/2019/06/04/7ee5b718c388cf362c2bd0dda741c671.png)

  

