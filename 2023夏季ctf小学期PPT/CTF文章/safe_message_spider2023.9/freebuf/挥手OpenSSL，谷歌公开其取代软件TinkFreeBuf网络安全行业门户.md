  

![1.jpg](https://image.3001.net/images/20180914/1536921239_5b9b8e9785c34.jpg!small)  
  

要说一个软件对IT和互联网业界影响力，恐怕OpenSS要算上一个。一个主要版本还不到V1.2的软件（V1.1.1为刚刚发布的LTS长期支持版本），占据了整改互联网底层安全核心。SSH、HTTPS,还有其他很多软件的安全加密算法都是离不开OpenSSL。

但是这么一个非常重要的基础软件，却在管理上和经费上曾爆出问题，以至于当2014年爆发心脏出血时候，整个业界，整个互联网、技术圈内的，甚至非技术圈内的也都震动了，其余波到现在还有影响。  

  
![2.jpg](https://image.3001.net/images/20180914/1536921250_5b9b8ea23f2b5.jpg!small)  

为了克服OpenSSL带来的问题，OpenBSD
Fork了一个新的软件LibreSSL，以确保SSL的库不会再出问题，基于OpenBSD的二十年积累下来的安全口碑，虫虫认为这是一个非常好的替代。同时各大公司也推出自己的SSL安全库，比如亚马逊的s2n。

本文介绍的则是，继继谷歌自己的BoringSSL和OpenBSD的LibreSSL之后，谷歌新发布的软件Tink。它是一个多语言，跨平台的安全加密类库。Tink是开源的，专注于创建简单的API，确保基础架构更具可移植性。

# AWS s2n

s2n(signal to
noise),是对TLS/SSL协议的C99（c语言标准）实现，基于开发一个简单，小巧，快速，并且优先考虑安全性的理念来设计。s2n使用Apache
License
2.0发布和许可，重点用于改进TLS（传输层安全性）和使用更轻量级的方法。s2n仅使用了6,000行代码，定义了更专注，更精简的库。当然可能会随着新版本的迭代而代码增加，因为目前还只是一个基本的实现。

![3.jpg](https://image.3001.net/images/20180914/1536922072_5b9b91d850265.jpg!small)  

s2n是完全开源的，托管在GitHub中（github：awslabs/s2n
），允许任何人review和fork代码，你可以Fork然后添加核心版本不支持的新功能。

亚马逊对安全问题比较认真，能及时反应社区发现的漏洞。还开展了与研究人员和学者合作的机制来解决新的问题。

![4.jpg](https://image.3001.net/images/20180914/1536922082_5b9b91e25eb44.jpg!small)  
  

# 认识Tink

Tink是谷歌基于BoringSSL发布的SSL安全库软件，当前版本版本为1.2.0（已经超过了OpenSSL积累了几十年的版本）。目前Tink已经在谷歌自己的应用中得到了大量应用，比如已经集成到了AdMob，Google
Pay，Google智能助理和Firebase。

Tink集成了 **AEAD方法**
（经过身份验证的加密AE和经过身份验证的加密以及相关数据）。集成了加密密钥，散列函数和消息验证代码（MAC）。Tink中AEAD的最低标准包括[RFC5116]：

明文和相关数据可以具有任何长度（从0到2³²字节）。

支持80位身份验证。

CCA2安全性（自适应选择密文攻击）。

谷歌分析了许多加密技术的弱点，在Tink中对他们做了专门修复。

  
![5.jpg](https://image.3001.net/images/20180914/1536922054_5b9b91c6ab114.jpg!small)  

# 实例演示  

官方仓库附带了详细的文档说明和许多实例，本文中简单举个例子。Tink就是用于简化加密处理并尽可能使用安全、最佳加密方法。在下面我们使用"qwerty123"键加密一个字符串（"napier"），注意示例代码用了java，官方目前支持C++，OC和JAVA原生库。

package com.helloworld;

import com.google.crypto.tink.aead.AeadConfig;

import java.security.GeneralSecurityException;

import com.google.crypto.tink.Aead;

import com.google.crypto.tink.KeysetHandle;

import com.google.crypto.tink.aead.AeadFactory;

import com.google.crypto.tink.aead.AeadKeyTemplates;

public final class HelloWorld {

public static void main(String[] args) throws Exception {

AeadConfig.register();

try {

KeysetHandle keysetHandle =
KeysetHandle.generateNew(AeadKeyTemplates.AES128_GCM);

Aead aead = AeadFactory.getPrimitive(keysetHandle);

String plaintext="napier";

String aad="qwerty123";

System.out.println("Text:"+plaintext);

byte[] ciphertext = aead.encrypt(plaintext.getBytes(), aad.getBytes());

System.out.println("Cipher:"+ciphertext.toString());

byte[] decrypted = aead.decrypt(ciphertext, aad.getBytes());

String s = new String(decrypted);

System.out.println("Text:"+s);

} catch (GeneralSecurityException e) {

System.out.println(e);

System.exit(1);

}

}

}

范例运行过程如下：

Text: hello123

Password: qwerty

Type: 1

Enc type: 128-bit AES GCM

Cipher: AQbLoE0ino8ofgrvuSSLOKTaYjdPc/ovwWznuMeYfjP+TO1fc6cn7DE=

Cipher:
4151624C6F4530696E6F386F666772767553534C4F4B5461596A6450632F6F7677577A6E754D6559666A502B544F31666336636E3744453D

Decrypted: hello123

在本例中，我们使用了带GCM的128位AES。我们的AEAD对象创建语句为：

KeysetHandle keysetHandle =
KeysetHandle.generateNew(AeadKeyTemplates.AES128_GCM);

然后使用encrypt()和decrypt()方法创建加密流，并其进行解密。

好今天文章就介绍到这里，在撰写本文的时候，我们得知golang和.net版本的Tink也已经起步（github：elucidsoftllc/tink.net）。

  

