11月5日，云安全公司Zscaler观察到，DanaBot恶意软件通过两次较大型的供应链攻击重出江湖，还通过DDoS攻击了一个俄语论坛。

2018年5月，SaaS公司Proofpoint首次在恶意软件即服务平台（malware-as-a-service）affiliates上发现了DanaBot。攻击者负责提供 C&C 面板、维护 C&C
基础设施并且提供客户服务支持，其他攻击者可以购买恶意软件和平台的访问权限。已购买的攻击者可以自由分发和使用该恶意软件，
**主要是为了窃取凭据进行银行欺诈** 。

一直以来，DanaBot都是一个活跃的银行木马。尽管DanaBot在2020年年底进行了重大升级更新，但总体来说一直保持相对低调。

## 2021年10月22日供应链攻击

美国网络安全和基础设施安全局（CISA）发出警告，NPM上
**名为UAParser.js的JavaScript包在2021年10月22日被污染，用于分发挖矿程序和DanaBot** 。

UAParser.js是一个用于检测浏览器、渲染引擎、操作系统、CPU和设备类型的JavaScript库。根据NPM的统计数据，
**每周有超过700万次下载** 。

本次攻击通过https://citationsherbe.at/sdd.dll下载DanaBot。

  * Loader的哈希为[2a3acdcd76575762b18c18c644a745125f55ce121f742d2aad962521bc7f25fd](https://www.virustotal.com/gui/file/2a3acdcd76575762b18c18c644a745125f55ce121f742d2aad962521bc7f25fd)
  * Loader下载的组件哈希为[77ff83cc49d6c1b71c474a17eeaefad0f0a71df0a938190bf9a9a7e22531c292](https://www.virustotal.com/gui/file/77ff83cc49d6c1b71c474a17eeaefad0f0a71df0a938190bf9a9a7e22531c292)

组件的主要配置如下所示：

![](https://image.3001.net/images/20211110/1636522830_618b5b4e64c97571a318e.png!small)

该恶意软件还配置了TOR节点（bjij7tqwaipwbeig5ubq4xjb6fy7s3lknhkjojo4vdngmqm6namdczad.onion）作为备用的C&C服务器。

该样本的affiliate ID为40，这是DanaBot的新成员。进行供应链攻击时，攻击者仅将恶意软件的凭据窃取组件启用，而其他组件尚未激活。

 **尽管攻击者的意图目前并不清楚，但有可能是想在获取访问凭据后出售给勒索软件的团伙** 。

## 2021年11月4日供应链攻击

就在前几天，又发现了另一个 **名为COA的NPM软件包被污染并用来传播DanaBot** ，该软件包用于解析命令行参数。根据NPM的统计数据，
**每周有接近900万次下载** 。

该攻击发生于2021年11月4日，与对UAParser.js的污染攻击相同，都是由affiliate ID为40的DanaBot的新成员发起的。

本次攻击通过https://pastorcryptograph.at/3/sdd.dll下载DanaBot。

> Loader的哈希为
>
>
> [26451f7f6fe297adf6738295b1dcc70f7678434ef21d8b6aad5ec00beb8a72cf](https://www.virustotal.com/gui/file/26451f7f6fe297adf6738295b1dcc70f7678434ef21d8b6aad5ec00beb8a72cf/details)
>
>
> Loader下载的组件哈希为[e7c9951f26973c3915ffadced059e629390c2bb55b247e2a1a95effbd7d29204](https://www.virustotal.com/gui/file/e7c9951f26973c3915ffadced059e629390c2bb55b247e2a1a95effbd7d29204/details)

与10月的攻击行动类似，攻击者也只启用了凭据窃取组件。

## DDoS攻击俄语论坛

affiliate
ID为40的DanaBot的新成员已经有一段时间没有变更过组件配置了。2021年10月20日，该攻击者向受害者下发了新的组件：（[8b64b8bfd9e36cc40c273deccd4301a6c2ab44df03b976530c1bc517d7220bce](https://www.virustotal.com/gui/file/8b64b8bfd9e36cc40c273deccd4301a6c2ab44df03b976530c1bc517d7220bce/detection)）

新的组件由Delphi编写，可以对硬编码的地址发起基于HTTP的DDoS攻击，如下所示：

![](https://image.3001.net/images/20211110/1636522964_618b5bd49dcbe30211e80.png!small)

攻击对象是俄语电子产品交流论坛，从User-Agent和单一的功能来看， **有可能是为了解决个人恩怨，而非攻击者的技战术的重大变更** 。

## 结论

尽管DanaBot的活跃度有所下降，但近期的这两次供应链攻击表明业界仍然不能忽视这个威胁。

## IOC

> 185.158.250.216:443  
> 194.76.225.46:443  
> 45.11.180.153:443  
> 194.76.225.61:443  
> 185.117.90.36:443  
> 193.42.36.59:443  
> 193.56.146.53:443  
> 185.106.123.228:443  
> 192.119.110.73:443  
> 192.236.147.159:443  
> 192.210.222.88:443  
> https://citationsherbe.at/sdd.dll  
> https://pastorcryptograph.at/3/sdd.dll  
> bjij7tqwaipwbeig5ubq4xjb6fy7s3lknhkjojo4vdngmqm6namdczad.onion  
> gcwr4vcf72vpcrgevcziwb7axooa3n47l57dsiwxvzvcdlt7exsvk5yd.onion  
> 2a3acdcd76575762b18c18c644a745125f55ce121f742d2aad962521bc7f25fd  
> 77ff83cc49d6c1b71c474a17eeaefad0f0a71df0a938190bf9a9a7e22531c292  
> 26451f7f6fe297adf6738295b1dcc70f7678434ef21d8b6aad5ec00beb8a72cf  
> e7c9951f26973c3915ffadced059e629390c2bb55b247e2a1a95effbd7d29204  
> f4d12a885f3f53e63ac1a34cc563db0efb6d2d1d570317f7c63f0e6b5bf260b2  
> ad0ccba36cef1de383182f866478abcd8b91f8e060d03e170987431974dc861e

## 参考来源

> [Zscaler](https://www.zscaler.com/blogs/security-research/spike-danabot-> malware-activity)

