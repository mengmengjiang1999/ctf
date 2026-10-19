## **一．背景**

 **近期接到客户反馈，其网络中有部分终端机器异常，拿到客户提供的样本分析后定性为是一起挖矿木马入侵事件，该挖矿木马复用了大量开源代码，用于对
BTV（“比特票”，一种基于比特币的分支币种）进行挖矿。** ****

## **二．样本详细分析**

通过分析客户提供的样本，发现样本实际上是不全的，但是并不影响对本次威胁的定性。其中最主要有三个样本文件：

样本名| 功能| SHA256  
---|---|---  
run.bat| 启动挖矿进程的bat脚本|
a02d5079ae3eeacb463aa855a1daec72587ff2bbf576cb95081ad9b56d614684  
Svchost.exe| 基于NSSM的保护进程|
29F0DBF2D07C4B68C3C9EE0D139D80BAD3E9058FBF9DBD574CB5B047CF742E74  
Systmss.exe| 挖矿进程|
24AE1FCD6080097248C1F2171218DA3DBD22E46CFEF854A0EC646AD80A503014  
  
客户提供的样本缺少的应该是一个安装程序，用于打包以上三个程序以及安装挖矿进程和启动保护进程。由于没有该起威胁的母体程序以及在受害计算机上取证，只在样本分析的角度并不好判断其是如何伪装感染用户计算机的。一般来说会通过程序打包软件对其打包，然后伪装成视频、压缩包等通过邮件或者挂马等方式来诱骗安全意识薄弱的用户点击。

###  **2.1 run.bat样本**

该文件内容是为:

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/1526981389683.png!small)

通过bat脚本传参调用程序开始挖矿。根据矿池地址知道其属于一种新的虚拟币种——比特票。比特票（BitVote）是2018年1月20日上线的一种新型比特币分叉币，采用CryptoNight算法，矿工可以使用自己的CPU挖矿并参与投票。

从<https://www.vvpool.com>可以看到其价格当前为0.49美元。

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269814194194.png!small)

其官网介绍：  

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269814442759.png!small)

截至两次分析时间，该挖矿样本对应的钱包信息如下：  

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269814759239.png!small)

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269815036342.png!small)![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269815207574.png!small)

最新支付记录：  

最早支付记录：  

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269816632884.png!small)  

从支付记录来看，该挖矿木马在2018年2月初活跃至今。

###  **2.2 svchost.exe样本**

该样本伪装成系统进程名svchost.exe用于迷惑受害者，该样本主要功能是用于保护挖矿程序被kill后可以重新启动。

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269816896951.png!small)

分析样本最后发现svchost.exe是基于NSSM编写的，样本中的主函数wmain位置代码：

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269817388647.png!small)

与github上NSSM（<https://github.com/kirillkovalenko/nssm>）的代码比较，代码逻辑完全是一致的：  

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269817815392.png!small)

其中NSSM是一个服务管理工具，它可以以NT服务开启应用，无论应用以何种方式失败均会尝试重启应用，参考其说明：  

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269818075180.png!small)

通过VT关联分析，该样本原始文件名是nssm.exe，设涉及大量的样本  

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269818315615.png!small)

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269818458586.png!small)

涉及的历史文件名：  

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269818715435.png!small)

VT链接：

_<https://www.virustotal.com/#/file/29f0dbf2d07c4b68c3c9ee0d139d80bad3e9058fbf9dbd574cb5b047cf742e74/relations>_

###  **2.3 systmss.exe样本**

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/1526981918705.png!small)

systmss.exe程序是负责挖矿的程序，从其代码中的信息分析，发现其是基于<https://github.com/lucasjones/cpuminer-multi>位置的项目编写的。

Systmss.exe中代码的片段：

对应到cpuminer-multi这个项目中的代码：  

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269819895398.png!small)

通过分析，Systmss.exe的代码完全是基于cpuminer-multi开源项目，cpuminer-multi是一个开源的多线程CPU挖矿程序，从其github页面可知，当前支持的算法较多，  

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269820166954.png!small)  

同时支持ARM、PowerPC、x86以及x86-64多种架构的CPU挖矿。

挖矿程序运行后会释放几个挖矿程序所依赖的DLL文件：

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/1526982052228.png!small)

通过VT关联分析，也发现了几个相关的事件：  

![一个针对“比特票”挖矿木马样本的分析](https://image.3001.net/images/20180522/15269820842422.png!small)  

VT链接：

_<https://www.virustotal.com/#/file/24ae1fcd6080097248c1f2171218da3dbd22e46cfef854a0ec646ad80a503014/relations>_

##  **三．总结**

该样本基于服用大量开源代码来编写，尤其基于NSSM来编写保护进程这种操作确实对于免杀程序有一定的效果。对于在2018年1月才发布的虚拟货币BTV便有一些针对其挖矿的木马进行传播，可见当前对于虚拟货币的挖矿依旧也是越演愈烈的状况，由于这一类恶意软件的制作门槛较低但是可以大量牟利，所以可以推测未来该类挖矿恶意软件的出现也会越来越多。

##  **四．IoCs**

### BTV挖矿信息：

> btv.vvpool.com:5700
>
> 13mUp3VADQGJF8k1GuSkhV4md5xCh6HwL4.586

### 样本HASH：

> a02d5079ae3eeacb463aa855a1daec72587ff2bbf576cb95081ad9b56d614684
>
> 29F0DBF2D07C4B68C3C9EE0D139D80BAD3E9058FBF9DBD574CB5B047CF742E74
>
> 24AE1FCD6080097248C1F2171218DA3DBD22E46CFEF854A0EC646AD80A503014

 ***本文作者：任子行，转载请注明来自 FreeBuf.COM**

