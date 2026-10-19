## 前言

Phobos勒索病毒最早于2019年被首次发现并开始流行起来，该勒索病毒的勒索提示信息特征与CrySiS(Dharma)勒索病毒非常相似，但是两款勒索病毒的代码特征却是完全不一样，近日笔者在逛某开源恶意软件沙箱的时候发现了一款Phobos勒索病毒捆绑某数控软件目录下的AdobeIPCBroker组件模块加载执行，这种通过正常软件捆绑勒索病毒的加载方式，此前也被应用于一些主流的勒索病毒攻击活动，出与好奇，笔者对这款Phobos勒索病毒进行了深度的分析与研究。

对这款勒索病毒与CrySiS勒索病毒相关的信息，可以去参考笔者之前的一篇文章，里面有详细的介绍。

[《2019年出现的这款新型的勒索病毒，你见过吗？》](http://mp.weixin.qq.com/s?__biz=MzA4ODEyODA3MQ==&mid=2247484508&idx=1&sn=cd77e02d63e488e92596c34da853bd74&chksm=902fab74a758226207ca5ea17727d6c0249005778044ba769d8746616407fffdeca2951b885f&scene=21#wechat_redirect)

## 深度分析

从开源沙箱平台下载到该勒索病毒样本，运行之后，启动AdobeIPCBroker组件程序，如下所示：

![](https://image.3001.net/images/20220403/1648993858_6249a642c57719c56422f.png!small)

该组件程序目录下，包含的文件，如下所示：

![](https://image.3001.net/images/20220403/1648993881_6249a6595e847c72d1394.png!small)加载执行的AdobeIPCBroker组件为正常软件，如下所示：

![](https://image.3001.net/images/20220403/1648993901_6249a66dbeda41d339996.png!small)通过初步分析，发现该目录文件夹里面有几个可疑文件，这几个可疑的文件分别为：TmEvent.dll、libcui40.dll、ground，至于我是如何能快速定位发现这几个可疑模块的，可能是我个人经验与直觉吧，这里也教大家一个比较笨的方法，就是查看这个组件程序加载了哪些模块，然后再一个一个去人工逆向分析排查，这个时候也不能依靠VT，因为大多数情况下VT上是没有这些样本文件的，除非样本已经被人传到了VT上，有时候就算VT上有了这些样本，也可能显示为正常的，因为黑客在攻击的时候已经做了相应的免杀处理，所以针对一些高端的黑客组织定向攻击行动，任何工具以及平台都只是起到辅助分析的作用，最后还是需要人工分析才能确认，安全永远是人与人的对抗，这款软件加载的相关DLL，如下所示：

![](https://image.3001.net/images/20220403/1648993922_6249a6823502352acfcd3.png!small)该组件通过加载TmEvent.dll恶意模块，动态加载libcui40.dll模块的导出函数RenderObject，如下所示：

![](https://image.3001.net/images/20220403/1648993940_6249a694f1b6617f4bb6e.png!small)libcui40.dll模块，加载ground恶意代码到内存并解密执行，如下所示：

![](https://image.3001.net/images/20220403/1648993958_6249a6a6b0801b54bd8e7.png!small)然后执行到解密的shellcode代码处，如下所示：

![](https://image.3001.net/images/20220403/1648993976_6249a6b85aa8f4c369178.png!small)解密出第二阶段的shellcode代码并跳转执行，如下所示：

![](https://image.3001.net/images/20220403/1648993994_6249a6cabff0ca13fe2a2.png!small)第二阶段shellcode再次分配内存空间，如下所示：

![](https://image.3001.net/images/20220403/1648994015_6249a6df22a9d7e88d3a9.png!small)在内存解密出勒索病毒核心代码，如下所示：

![](https://image.3001.net/images/20220403/1648994038_6249a6f6db9e8ff2bf2e5.png!small)通过对比之前phobos的Devos变种样本，内存解密出来的勒索病毒核心代码与此前勒索病毒核心代码高度相似，可以判定该勒索病毒为Phobos勒索病毒Devos的变种家族，如下所示：

![](https://image.3001.net/images/20220403/1648994056_6249a708cf13f93bdaddd.png!small)该勒索病毒加密后的文件，如下所示：

![](https://image.3001.net/images/20220403/1648994073_6249a719e0dfdcb396f3a.png!small)弹出的勒索提示信息，如下所示：

![](https://image.3001.net/images/20220403/1648994090_6249a72ab2314c99ddb6e.png!small)

黑客留下的相关联系方式，如下：

邮箱地址：

martin1993douglas@pressmail.ch

bryan1984jackson@tutanota.com

  

Telegram联系方式：

@devos_support

  

Jabber联系方式：

cris_nickson@xmpp.jp

  

## 威胁情报

HASH

A43453DC3F04860653FF23DB54F91F0D

5766B7A2FD2431D5FD95E7DFE53E9059

996C12AC07C7955FE018B68AC29FF8FB

72AD5CEBF69DE22B971997BB261EF519

  

PDB

D:\WinStandalone\qt\Users\pdb\pdb\Unicode Release\git\Bing\RE.pdb

  

## 总结

从上面的分析可以猜测这可能是一次定向勒索攻击行动，该攻击行动主要针对使用某数控机床仿真软件的行业公司进行定向攻击，免杀方面也做的很好，初期几个恶意模块在VT上基本都是显示为正常的，黑客通过二次打包捆绑某数控机床仿真软件程序，欺骗受害者安装恶意程序，加载目录下的勒索病毒恶意模块文件。

通过一些常用的软件捆绑勒索病毒的方式，也是勒索病毒攻击的主要方式之一，大家在下载一些软件的时候，一定要到正规的官方网站进行下载，同时要检测安装包软件的数字签名等信息是否完整有效，目前主流的勒索病毒都是无法解密的，同时勒索病毒的攻击也会越来越向定向化攻击发展为主，“APT式”的勒索病毒攻击未来会成为勒索病毒攻击的主要方式，可以预见，未来几年“APT式”的勒索攻击活动将是全球网络安全最大的威胁之一，同时数据窃取类的高级威胁攻击活动也将会越来越向定向化攻击活动发展。

最后还是那句话，做安全，不忘初心，坚持去做就可以了。

