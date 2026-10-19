![](https://image.3001.net/images/20211028/1635413861_617a6f652ce474bd5d40d.jpg!small)

捷克网络安全软件公司 Avast 创建并发布了一个解密工具，以帮助 Babuk 勒索软件受害者免费恢复文件。

Avast Threat
Labs介绍，Babuk解密器是使用泄漏的源代码和解密密钥进行创建的，拥有扩展名为.babuk、.babyk、.doydo加密文件的 Babuk
受害者才可以免费使用。Babuk勒索软件的受害者可以从Avast的服务器上下载解密工具，并按照用户界面提示一次性解密整个分区。根据测试，该解密器可能只对Babuk源代码转储的部分密钥泄露受害者有效。

泄露的源代码和解密密钥源自一名自称是Babuk的组织成员，这名所谓的Babuk成员称因癌症晚期而不得不作出泄露源代码的决定。泄露的共享文档包含不同的Visual
Studio Babuk勒索软件项目，用于VMware
ESXi、NAS和Windows加密器，其中Windows文件夹包含Windows加密器、解密器的完整源代码，以及看起来像私钥和公钥生成器的内容。文件还包括勒索软件团伙为特定受害者编写的加密和解密程序。

![](https://image.3001.net/images/20211028/1635413530_617a6e1abedafc065aab6.jpg!small)

Babuk Windows 加密器源代码

泄漏事件发生后，Emsisoft 首席技术官兼勒索软件专家Fabian Wosar称该源代码是合法的，而且文档中可能还包含过去受害者的解密密钥。

## Babuk的动荡历史

Babuk
Locker，又名Babyk和Babuk，是一种勒索软件行动，在2021年初发起时便针对企业的数据进行窃取和加密双重勒索攻击。在袭击华盛顿特区的大都会警察局(MPD)
后，该组织被美国执法部门盯上，Babuk迫于压力停止了行动。

因该组织“管理员”想将窃取的MPD数据泄漏到网站进行公开，遭到其他成员的反对。此后Babuk成员分裂成两股势力，最初的“管理员”另立门户发起了Ramp网络犯罪网站，其他成员则以Babuk
V2的名义重新启动了勒索软件，从那时起继续瞄准和加密企业数据实施勒索攻击。

Ramp网络犯罪网站刚成立不久便遭到一系列DDoS攻击导致无法使用。“管理员”认为攻击的幕后黑手是他的前合作伙伴，但Babuk V2对此进行了否认。  
  
参考来源：https://www.bleepingcomputer.com/news/security/babuk-ransomware-decryptor-released-to-recover-files-for-free/

