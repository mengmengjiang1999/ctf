*****本文原创作者：scu-igroup，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

##  **前言**  

**分析网络流量总是绕不开HTTPS，因其广泛使用甚至是强制使用逐渐被大众熟知，在保证其安全的同时也提高了对流量进行研究的难度。目前解析HTTPS协议的文章很多，有很多不错的文章可以带着入门，老实说，HTTPS协议还是挺复杂的，尤其是握手交换密钥的过程；虽然大部分的文章只是对协议握手的过程做了详细的解析，却很少涉及HTTPS网络数据包解密的部分，因此，本文即是从数据包层面，在知道私钥的情况下，来一步一步看如何对HTTPS的内容进行解密。**  

##  **正文**  

要对HTTPS网络数据包进行解密，其实是有一些工具是可以使用的，比如wireshark和ssldump，现在，先让我们来看看这两款工具如何使用，在手动对HTTPS的数据包进行解密。

### 1.wireshark解密HTTPS数据包

首先是wireshark，在wireshark界面上方，依次点击 编辑->首选项。

**![image.png](https://image.3001.net/images/20181219/1545187441_5c19b071cb856.png!small)**

再点击Protocols 找到SSL，并进行必要配置：

![image.png](https://image.3001.net/images/20181219/1545187477_5c19b09565d6a.png!small)

先是对RSA keys list进行编辑，点击Edit完成配置，如下所示：

![image.png](https://image.3001.net/images/20181219/1545187497_5c19b0a9b39b5.png!small)点击加号，依次配置（服务器IP、目的端口、应用层协议、私钥路径）。然后对SSL
debugfile进行配置，在这里面，wireshark会打印出解密过程中的调试信息，非常有用，后文在进行手动解密的时候即是通过它发现的错误，按照前文配置到一个路径下，配置完成点击ok后，可在wireshark主界面解密出通信内容。  
![image.png](https://image.3001.net/images/20181219/1545187515_5c19b0bbc6c04.png!small)

如图所示，顺利解出了HTTP的内容，在大呼神奇的同时，我们对它的解密过程却一无所知，这其实是不利于学习的，所以本文即是来扫除这些盲点。下面我们再来看看ssldump工具的使用。

ssldump是一款Linux下的小工具，可直接用apt包管理工具安装，目前最新版本是ssldump0.9b3（13年后就停止更新了，可以下载源码）。在shell中运行：

    
    
    ssldump -Ad -k./private.pem -r ./ssl.pcap  
    

该条命令会打印出部分的解密过程，如下图所示：

**![image.png](https://image.3001.net/images/20181219/1545187553_5c19b0e16cc86.png!small)**

从该图中可以看到client/server产生的随机数（random），加密的预主密码（EncryptedPremaster
secret），以及用到的加密套件，为：

    
    
    TLS_RSA_WITH_AES_256_CBC_SHA  
    

表示采用RSA进行身份认证和对称密钥交换，采用AES
256位对称加密算法，加密模式为CBC，采用SHA进行消息认证。虽然工具已经解出了HTTP的请求内容，但是打印信息中未打印出解密后的主密码和对称密钥，因此，打印信息没有完整反映解密过程，这款工具在centos下还会出现core
dumped错误，感觉不是太好用。

### 2.HTTPS协议简介

虽然已经有不少的帖子非常详细地介绍了HTTPS协议，但是本文依然选择简单介绍一下HTTPS协议，主要侧重于对解密中要用到的参数进行说明。如下图所示，为HTTPS完整握手的流程图。

**![image.png](https://image.3001.net/images/20181219/1545187666_5c19b152eba53.png!small)**

图中完整地反映了HTTPS的握手过程，在此过程中，Client会同Server交互若干参数来协商对称密钥，用来对应用数据进行加解密。这里笔者以TLS_RSA_WITH_AES_256_CBC_SHA这个密码套件为例，讲述整个解密过程。那么，解密过程需用到的参数如下：

1.clientrandom 客户端随机数；

2.serverrandom 服务器随机数；

3.EncryptedPreMaster 加密的预备主密码。

![image.png](https://image.3001.net/images/20181219/1545191290_5c19bf7ae9a22.png!small)

如上图所示，解密的过程大致为：先用私钥对Encrypted PreMaster Secret进行解密，得到decrypted PreMaster
Secret；再用client random、server random、decrypted PreMaster 得到Master
Secret；再用MasterSecret计算出消息认证密钥（key of
MAC）、数据加密对称密钥和CSC模式用到的初始化向量值(iv)，得到密钥后即可对通信内容进行解密了。看似过程很简单，实际上只有实验一把才会更好理解整个过程。

### 3.HTTPS网络数据包手动解密

在解密之前，需要说明的是，并不需要自己写解密代码来完成数据的解密，有很多好用的工具可以完成这件事，我们需要做的是，把整个流程串起来即可。本文中所使用的解密工具为openssl，很强大的工具，用它完成非对称加解密和对称加解密是相当方便的。

实验准备：本文的流量样本采用的TLS1.0版本，虽然目前主流是用TLS1.2，但是这两个版本基本框架一致，弄懂了前者，后者也是很好理解的，流程稍作改动同样能完成解密；以学习为目的，从1.0开始是一个不错的选择。本文流量的加密套件采用RSA非对称加密交换对称密钥参数，采用AES256对通信流量进行加密。所有的实验材料已上传到[github](https://github.com/scu-igroup/https_packets_decrypt)中。

那就正式开始吧，首先是在数据包中将client random，server random和Encrypted
PreMaster的二进制数据提取出来。如下图所示，在wireshark中分别找到clienthello、serverhello、clientkey
exchange数据包，选择要导出的字段，点击鼠标右键，选择导出分组字节流，存成bin文件，分别为client_random.bin、server_random.bin、premaster-encrypted.bin。

![image.png](https://image.3001.net/images/20181219/1545187748_5c19b1a42f08a.png!small)在Ubuntu中查看结果，这三个二进制文件的内容分别为：  

![image.png](https://image.3001.net/images/20181219/1545187763_5c19b1b38e0db.png!small)

首先，是对premaster-encrypted.bin进行解密。利用已获得的私钥private.pem进行解密，解密命令为：

    
    
    openssl pkeyutl -decrypt -in ./premaster-encrypted.bin -inkey ./private.pem -out premaster-decrypted.bin

如未报错，代表执行成功，将解密的数据存入到premaster-decrypted.bin文件中，用hexdump可查看。

![image.png](https://image.3001.net/images/20181219/1545187808_5c19b1e01e1d1.png!small)

就得到解密后的预备主密码，对于密码专家来说，得到预备主密码跟最后一步解密内容是等价的。但对于我们来说，还有几步要折腾。

下一步，即是利用预备主密码计算主密码，在此过程中，还需利用clientrandom和serverrandom，用命令将client_random.bin，server_random.bin两个文件合并起来。

    
    
    cat client_random.bin server_random.bin > random_cs.bin  
    

用hexdump查看有如下结果：

![image.png](https://image.3001.net/images/20181219/1545187831_5c19b1f7a91d0.png!small)

然后用伪随机函数计算（PRF）计算主密码，伪随机函数计算程序需在windows下运行，命令如下。

    
    
    .\PRF.exe--label "master secret" --length 48 --secret.\premaster-decrypted.bin --data .\random_cs.bin  --output master-secret.bin  
    

PRF.exe为网上分享的计算程序，源程序[见这里](https://github.com/lowleveldesign/diagnostics-tools/tree/master/PRF)，本文的github中已作分享。利用这款程序就可得到主密码文件master-secret.bin，用hexdump查看为：

![image.png](https://image.3001.net/images/20181219/1545187857_5c19b2112ea40.png!small)

这种计算主密钥的方法存在漏洞，在TLS1.2版本中已做调整。接下来，就可以利用主密码计算加密传输数据的对称密钥和其他参数了。在解密之前，需要用先生成random_sc.bin，如下：

    
    
    cat server_random.bin client_random.bin > random_sc.bin  
    

与上一个文件不同的是client random和server
random的顺序不一样，得到random_sc.bin。然后，同样在windows下运行，命令如下：

    
    
    .\PRF.exe--secret .\master-secret.bin --label "key expansion" --data.\random_sc.bin -n 136 -o key-expansion.bin  
    

得到key-expansion.bin文件，用hexdump查看为：

![image.png](https://image.3001.net/images/20181219/1545188573_5c19b4dd02e76.png!small)

这样利用主密码生成了6种信息，分别是：

> 20字节的消息认证码密钥（客户端→服务器）
>
> 20字节的消息认证码的密钥（服务器→客户端）
>
> 32字节的对称密码密钥（客户端→服务器）
>
> 32字节的对称密码的密钥（服务器→客户端）
>
> 16字节的对称密码的CBC模式所使用的初始化向量（客户端→服务器）
>
> 16字节的对称密码的CBC模式所使用的初始化向量（服务器→客户端）

字节数加起来刚好同key-expansion.bin文件的字节数吻合，在此，就得到了对称加密时所使用的密钥。客户端到服务器的对称密钥为：

    
    
    a86b855b66c5dc18566879eb98e8a86b7c90c5564438f3af80b317dcb5a25747  
    

现在我们就可以用它来解密客户端到服务器的应用数据内容。在正式解密前，我们先按照上述方法将客户端到服务端的应用层数据提取成二进制文件，为client-request.bin，然后用如下命令进行解密：

    
    
    openssl enc-aes-256-cbc -d -K $cs_key -iv $iv_value -in .\client-request.bin -out.\client-request-decrypted.bin  
    

其中，$cs_key为客户端到服务器传送消息的密钥，iv为上一个消息内容中最后一个分组的值，iv的值仅凭这句话，不太好找，我也是试出来的。确定iv值的方法如下所示：

![image.png](https://image.3001.net/images/20181219/1545188601_5c19b4f99ea8a.png!small)图中第24个数据包为要解密的内容，上一个消息指的是客户端到服务器方向的上一个消息，也即是第20个包，最后一个分组的值为该数据包最后16个字节，如下图所示：  

![image.png](https://image.3001.net/images/20181219/1545188619_5c19b50b260b8.png!small)第20个数据包的最后一个分组，即iv就是:
ed605d761378241c7add3c921022b268。需要说明的是，iv值的计算方法在TLS1.0版本存在漏洞，在TLS1.2版本中已做更改。得到iv就可执行解密命令，并将解密内容存在client-request-decrypted.bin文件中，用hexdump和cat查看：  

![image.png](https://image.3001.net/images/20181219/1545188696_5c19b558ed25d.png!small)

如上图所示，顺利解出HTTP协议的请求内容，最后有一段乱码，那是HMAC的值，做消息认证用，感兴趣的朋友可以自己去看消息认证相关内容，这里只需解出明文数据就行了。对于服务器到客户端的消息，采用同样的方法，也可以解出来，但用到的是服务器到客户端的密钥。

大家照着这个流程可以很快地复现出来，但笔者在此过程中踩过很多坑，有时也不知道哪一步计算错了，由于只要任何一部出错，后面的都不对，挺折腾的。不过，要解决调试问题，wireshark的debug文件很有用，里面把每一步需要计算的参数都打印出来了，部分结果如下图所示：

![image.png](https://image.3001.net/images/20181219/1545188720_5c19b57010b8f.png!small)

client write
key就是客户端到服务器的对称加密密钥，同我们计算的一样。因此，可对照着debug文件的结果，查看哪一步算错了，这可以帮助开发人员快速定位到问题。

既然手动能解出来，那下一步就是自动化实现了，这也不难，openssl提供有C和Python开发库，复杂的密码算法不用我们来实现，调用API解密函数即可。在以后的系列篇中，即是完成自动解密程序，以及加上对TLS1.2的支持。

## 总结

HTTPS协议是比较复杂的一个协议，要想学习它，光看它的技术原理是不得要领的，本文也是笔者在对它学习的过程中产生。尝试通过手动解密HTTPS数据包的过程是很有趣的，也能加强对HTTPS协议的理解。其中关于数字证书验证和消息认证本文没有涉及，由读者自己去研究了。对HTTPS协议的研究，大家如有其它的点，欢迎一起讨论。  

***本文原创作者：scu-igroup，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

