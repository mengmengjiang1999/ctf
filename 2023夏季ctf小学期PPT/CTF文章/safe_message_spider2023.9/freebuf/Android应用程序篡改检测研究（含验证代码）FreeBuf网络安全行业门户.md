![](https://image.3001.net/images/20200303/1583231036_5e5e303ccb648.jpg!small)

**Android应用程序在上传至Play
Sotre之前，开发者需要先使用私钥来对其进行签名。每一个私钥都与一个公共证书进行绑定，而设备和服务都需要利用这个证书来验证应用程序来自一个可信的源。应用程序更新同样依赖于这个签名机制，因为更新程序的签名必须跟已安装App的签名相同，才能完成更新。**

然而，在Play Store中发布APK其实是非常简单的。广大开发人员可以通过在根设备中下载APK来获取到APK文件，或者通过网站爬虫的方法来从Play
Store中获取同一应用程序的所有不同版本的APK文件。当你拿到APK文件之后，我们就可以通过apktool和反编译器并使用自己的证书来修改这个应用程序，然后对其进行重新封装和打包。

从防御端的角度来看，应用程序开发人员会试图通过检查当前应用程序签名证书是否与目标App所使用的签名证书相同。这确实是一种有效的机制，但其缺点就是需要依赖系统API来获取应用程序签名密钥。在静态分析中，我们可以通过系统API来获取签名证书，并帮助我们定位到需要进行检测的地方，以便更好地实现安全防御。在动态分析中，我们有现成的钩子脚本可以快速绕过应用程序中的这种防御机制。比如说，RASP（运行时应用程序自我保护）就可以提供更好的安全机制来防止这种篡改操作，但在本文中我们对此不做赘述。

在这篇文章中，我们将围绕一种更加有效的检测方式来检查Android应用程序中的篡改行为，并且减少对系统API的依赖。

![](https://image.3001.net/images/20200303/1583231048_5e5e3048b8690.png!small)

###  下面给出的是我们在完成这个任务时所要满足的要求：

> 1、验证签名证书的哈希值，并将其并将其与C代码中预计算的哈希进行对比；
>
> 2、检测存储在源码文件只读区域中修复的源码以及预计算哈希；
>
> 3、检测本地代码中的动态篡改（钩子）；

##  验证C代码中签名证书的哈希

用来验证APK签名的签名证书存储在CERT.RSA或CERT.EC之中。在计算CERT.RSA的哈希值时，我们选择使用下面这个OpenSSL命令：

    
    
    openssl dgst -sha256 CERT.RSA

接下来，将上述命令的输出结果拷贝到[native-lib.c](https://github.com/darvincisec/DetectTamper/blob/master/app/src/main/c/core/native-lib.c)的APK_SIGNER_HASH变量值中。为了在程序运行时对APK进行解压并获取CERT.RSA，我这里选择使用开源代码库-libzip【[传送门](https://libzip.org/)】。接下来，我们需要使用mbedtls库来计算该证书的哈希，然后用它来跟嵌入在本地代码中的APK_SIGNER_HASH来进行对比。如果你不需要修改证书属性的话，你只需要做一次证书哈希对比即可。最好的方法，就是通过解析pkcs7证书来获取公钥，然后对其进行哈希计算。

##  检测本地代码中的静态和动态篡改

静态篡改指的是代码修复，动态篡改指的是在运行时挂钩本地库。

那么，攻击者如何才能绕过这种签名证书验证/检测机制呢？

> 1、使用他们自己的开发者证书哈希替换本地源码中的哈希；
>
> 2、修改用于新计算哈希和预计算哈希的比对代码，令其永远返回比对成功的结果；
>
> 3、在用于新计算哈希和预计算哈希的比对代码处设置钩子指令，令其永远返回比对成功的结果；

我的本地代码就只是一个C文件而已，它依赖于mbedtls来实现加密（HMAC,
SHA256），以及libzip静态库来对APK文件进行解压。除此之外，我还编写了一个marker文件来标记文本的起始和结尾处，以及rodata段：

    
    
    text_start.c
    
        const unsigned char rodata_hash[32] = {	dummy values };
    
        const unsigned char rodata_start[] = { 'm','a','r','k','e','r','s','t','a','r','t' };
    
        const void* text_start(){
    
            return (void *)text_start;
    
        }
    
        text_end.c
    
        const unsigned char rodata_end[] = { 'm','a','r','k','e','r','e','n','d' };
    
        const void* text_end(){
    
            return (void *)text_end;
    
        }

在代码中，计算本文段以及rodata段的HMAC，然后与预计算的值进行对比。那么，我们如何在代码构建之前获取到文本的HMAC和rodata段的数据呢？现在，HMAC密钥、HMAC文本和rodata
HMAC都会以const常量进行声明，而且并非静态const。接下来，在mbedtls、libzip、marker文件以及我自己的C文件的帮助下，我们就可以查看到各个数据段了：

![](https://image.3001.net/images/20200303/1583231120_5e5e3090c98bc.png!small)

在rodata段中，你可以看到rodata段之前看到rodata HMAC，因为计算出的HMAC不能在rodata段中。

![](https://image.3001.net/images/20200303/1583231124_5e5e309498294.png!small)

![](https://image.3001.net/images/20200303/1583231129_5e5e30992d8a5.png!small)

现在，我们的任务只完成了一半。接下来，我们还需要计算文本段和rodata段的HMAC。HMAC用来保证数据的完整性以及真实性。用于实现HMAC注入的代码我选择采用的是Go语言开发，主要是参考了BoringSSL
FIPS的实现方式。在injecthash这个Go文件中，会生成一个随机的HMAC密钥，有了这个密钥，我们就能计算文本段和rodata段的HMAC了。

然后，将HMAC密钥、文本段HMAC和rodata段HMAC注入到本地代码中，并移除rodata中的const符号。至此，我们就可以开始检测Android应用程序中的篡改行为了。

##  验证代码PoC

本文所介绍的机制我们已通过PoC代码实现，并上传到了GitHub上，感兴趣的用户可以自行下载获取。值得一提的是，相同的自完整性检查概念可以适用于具有相似二进制结构的任何应用程序。

> PoC验证代码：【[点我获取](https://github.com/darvincisec/DetectTamper)】

 *** 参考来源：[darvincitech](https://darvincitech.wordpress.com/2020/03/01/yet-another-tamper-detection-in-android/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

