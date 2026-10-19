# 移动应用安全基础篇——解密iOS加密数据

阅读量 **509430**

|评论 **6**

发布时间 : 2019-05-27 11:06:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01be02123191863645.jpg)

## 介绍

如今，在做APP安全测试的时候，越来越多的APP数据使用加密传输，一般的做法都需要去逆向APP并寻找到加解密算法。今天主要介绍一下iOS的一些逆向基础知识，教大家碰到加密数据的APP后该如何去解密。

今天主要是针对两款有不同加密方式的iOS应用，难度由低到高。

## 案例一：

首先解决挂代理抓不到包的问题

使用objection ios sslpinning disable绕过证书绑定

![](https://p1.ssl.qhimg.com/t013377a3578e78b930.jpg)

在登录处抓包发现，request包和response包都为加密传输：

![](https://p0.ssl.qhimg.com/dm/1024_246_/t011e8def40ce847b62.jpg)

appmon提供的scripts

hack.lu提供的scripts

通过参考github上的js脚本，改写了个较为全面的hook.js脚本:

    
    
    // Intercept the CCCrypt call.
    Interceptor.attach(Module.findExportByName('libcommonCrypto.dylib', 'CCCrypt'), {
        onEnter: function (args) {
            // Save the arguments
            this.operation   = args[0]
            this.CCAlgorithm = args[1]
            this.CCOptions   = args[2]
            this.keyBytes    = args[3]
            this.keyLength   = args[4]
            this.ivBuffer    = args[5]
            this.inBuffer    = args[6]
            this.inLength    = args[7]
            this.outBuffer   = args[8]
            this.outLength   = args[9]
            this.outCountPtr = args[10]
    
            console.log('CCCrypt(' + 
                'operation: '   + this.operation    +', ' +
                'CCAlgorithm: ' + this.CCAlgorithm  +', ' +
                'CCOptions: '   + this.CCOptions    +', ' +
                'keyBytes: '    + this.keyBytes     +', ' +
                'keyLength: '   + this.keyLength    +', ' +
                'ivBuffer: '    + this.ivBuffer     +', ' +
                'inBuffer: '    + this.inBuffer     +', ' +
                'inLength: '    + this.inLength     +', ' +
                'outBuffer: '   + this.outBuffer    +', ' +
                'outLength: '   + this.outLength    +', ' +
                'outCountPtr: ' + this.outCountPtr  +')')
    
            if (this.operation == 0) {
                // Show the buffers here if this an encryption operation
                console.log("In buffer:")
                console.log(hexdump(ptr(this.inBuffer), {
                    length: this.inLength.toInt32(),
                    header: true,
                    ansi: true
                }))
                console.log("Key: ")
                console.log(hexdump(ptr(this.keyBytes), {
                    length: this.keyLength.toInt32(),
                    header: true,
                    ansi: true
                }))
                console.log("IV: ")
                console.log(hexdump(ptr(this.ivBuffer), {
                    length: this.keyLength.toInt32(),
                    header: true,
                    ansi: true
                }))
            }
        },
        onLeave: function (retVal) {
            if (this.operation == 1) {
                // Show the buffers here if this a decryption operation
                console.log("Out buffer:")
                console.log(hexdump(ptr(this.outBuffer), {
                    length: Memory.readUInt(this.outCountPtr),
                    header: true,
                    ansi: true
                }))
                console.log("Key: ")
                console.log(hexdump(ptr(this.keyBytes), {
                    length: this.keyLength.toInt32(),
                    header: true,
                    ansi: true
                }))
                console.log("IV: ")
                console.log(hexdump(ptr(this.ivBuffer), {
                    length: this.keyLength.toInt32(),
                    header: true,
                    ansi: true
                }))
            }
        }
    })
    

使用frida hook CCCrypt函数

![](https://p4.ssl.qhimg.com/dm/919_1024_/t01b41a60c58227763c.jpg)

operation: 0x0代表加密，0x1代表解密，CCAlgorithm: 0x0指加密方式是kCCAlgorithmAES128，CCOptions:
0x1指模式是cbc，key=DATA_KEY20150116和iv=20150116

参阅CommonCryptor.h各参数意义

## 案例二：

在登录处抓包发现，request包和response包都为加密传输：

![](https://p3.ssl.qhimg.com/dm/1024_309_/t0135b74098ebc1f9ce.jpg)

使用hook.js脚本发现hook不到

![](https://p3.ssl.qhimg.com/dm/823_1024_/t01e8a882d4838a5984.jpg)

老方法，首先使用frida-ios-dump对该APP进行一键dump

frida-ios-dump，该工具基于frida提供的强大功能通过注入js实现内存dump  
然后通过python自动拷贝到电脑生成ipa文件，通过配置完成之后真的就是一条命令砸壳。

![](https://p4.ssl.qhimg.com/dm/864_1024_/t0147df98c4e27aee00.jpg)

砸壳完成后会生成ipa文件，我们解压缩然后使用IDA加载完二进制文件

然后在String窗口搜索loginbypassword（这个是登录时的信息），搜索后进入对应的类，接下来我们进入这个类看它用了哪些方法

![](https://p5.ssl.qhimg.com/dm/1024_347_/t01e7be3c692bec084b.jpg)

![](https://p4.ssl.qhimg.com/dm/1024_645_/t015448bfa51ba429cf.jpg)

找到这个字符串引用的代码位置

![](https://p2.ssl.qhimg.com/dm/1024_681_/t01e3c885b2b4289133.jpg)

之后双击callWebAPI:data:method:ssl:completionHandler:

找到[WebService callWebAPI:data:method:ssl:completionHandler:]

然后F5一下

![](https://p2.ssl.qhimg.com/dm/1024_759_/t0126290a5c19e406a3.jpg)

浏览该类发现可以看到data等关键加密信息，接着我们尝试搜索data前面的setValue:forKey

![](https://p1.ssl.qhimg.com/dm/1024_282_/t01a0a0e306fc567b4b.jpg)

[_priv_NBSSafeMutableDictionary setValue:forKey:]查看该类发现无结果，返回上一步重新查看加密所在的类

v87由v86 = -WebService returnDictionaryWithDataPath:返回

查看returnDictionaryWithDataPath:

![](https://p5.ssl.qhimg.com/dm/1024_312_/t012dd59f340351b106.jpg)

v8 = +RSA encryptString:privateKey:;  
v4由convertToJsonData:返回（明文）v6由AppPrivate返回（密钥）

查看密钥返回函数AppPrivate和encryptString:privateKey函数

![](https://p5.ssl.qhimg.com/dm/1024_444_/t012709a00417631abc.jpg)

然后使用frida进行hook

![](https://p2.ssl.qhimg.com/dm/1024_454_/t0147936da12b1a5a29.jpg)

## 使用objection

    
    
    ios hooking watch method “+[RSA encryptString:privateKey:]” –dump-args
    ios hooking watch method “+[RSA encryptString:privateKey:]” –dump-return
    

![](https://p1.ssl.qhimg.com/dm/1024_541_/t01a417a75f64773064.jpg)

直接使用objection的这两句命令可以达到同样的效果

附JS：

    
    
    if (ObjC.available){
        try{
            var className = "RSA";
            var funcName = "+ encryptString:privateKey:";
            var hook = eval('ObjC.classes.' + className + '["' + funcName + '"]');
            console.log("[*] Class Name: " + className);
            console.log("[*] Method Name: " + funcName);
            Interceptor.attach(hook.implementation, {
              onEnter: function(args) {
                var param1 = new ObjC.Object(args[2]);
                console.log("args[2] -> " + param1);
    
                var param2 = new ObjC.Object(args[3]);
                console.log("args[3] -> " + param2);
              },
              onLeave: function(retval) {
                var retur = new ObjC.Object(retval);
                console.log("retval -> " + retur);     
              }
            });
        }
        catch(err){
            console.log("[!] Exception2: " + err.message);
        }
    }
    else{
        console.log("Objective-C Runtime is not available!");
    }
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Tide安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/179261](/post/id/179261)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [移动安全](/tag/移动安全)

 **+1** __10赞

 __收藏

![](https://p5.ssl.qhimg.com/t013dca47abc465f8d2.png) Tide安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

