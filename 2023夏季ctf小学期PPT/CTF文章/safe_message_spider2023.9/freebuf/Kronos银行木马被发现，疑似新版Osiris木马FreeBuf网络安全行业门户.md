![](https://image.3001.net/images/20180725/15325022896331.png!small)

**根据Proofpoint安全研究人员的说法，新版本的Kronos银行木马正蠢蠢欲动，研究人员证实，最近三次宣传这个旧木马的翻新版本在2014年经历了鼎盛时期。**

根据昨天晚上发布[报告](https://www.proofpoint.com/us/threat-insight/post/kronos-reborn)显示，今年4月，研究人员已经发现了这种新型Kronos变种的第一批样本。

最初的样本似乎是处于测试阶段，实际活动在6月下旬开始实施，当时研究人员开始检测malspam并利用套件向野外用户提供这个新版本。

## 活动针对德国，日本，波兰

Proofpoint报告发现了三个活动和一个测试运行，活动主要针对德国，日本和波兰银行的用户。  

![](https://image.3001.net/images/20180725/15325025602064.png!small)在此活动中使用该恶意软件不是原来的Kronos，而是在2014版本基础上更新了几个版本。  

Proofpoint报告了2018年和2014年版本之间广泛的代码重叠。相似之处包括2018版本使用相同的Windows
API散列技术和散列，相同的字符串加密技术，相同的C＆C加密机制，相同的C＆C协议和加密，相同的webinject格式（Zeus格式）以及类似的C＆C面板文件布局。

但这两个版本并不完全相同。主要区别在于2018版使用Tor托管的C＆C控制面板。

## Kronos 2018版可能是新版Osiris木马

研究人员说，与此同时，这种新的Kronos变种开始出现在他们的雷达上，一名恶意软件作者开始在黑客论坛上宣传一种新的银行木马，他称之为Osiris。  

Proofpoint的研究人员并未设法获得这种新Osiris恶意软件的样本，但他们表示该宣传广告很好地描述了Kronos 2018版本。  

最大的线索是这个新特洛伊木马的作者声称他的木马只有350 KB大小，接近于早期Kronos
2018版[样本](https://www.virustotal.com/en/file/e1347d1353775c4b18dc83fbf22f7ba248e1a27f255d7487782dc6f9fee0607d/analysis/)——研究人员4月份发现的（351
KB）大小。该样本被命名为os.exe，大概来自Osiris，巧合与否，目前没有得到证实。  

![](https://image.3001.net/images/20180725/15325026399281.png!small)

***参考来源：bleepingcomputer，由抗生素1209编译，转载请注明来自FreeBuf.COM**

