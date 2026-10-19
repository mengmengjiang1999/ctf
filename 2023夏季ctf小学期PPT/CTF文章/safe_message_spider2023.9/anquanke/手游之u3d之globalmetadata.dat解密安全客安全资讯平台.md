# 手游之u3d之global-metadata.dat解密

阅读量 **487503**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-12-30 17:00:03

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01d593118c22070bdb.jpg)

所需工具：

010editor  
frida  
js脚本  
Il2CppDumper  
ida

一款国外的游戏，u3d引擎，没有mono，使用Il2CppDumper一番操作

![](https://p3.ssl.qhimg.com/t01e24edeae1d30233e.png)

Dump失败，好吧，  
ida打开libil2cpp.so,能正常打开，应该没加密  
010editor打开global-metadata.dat

![](https://p1.ssl.qhimg.com/t0130d77ac7036e8dee.png)

global-metadata.dat头部信息，正常是AF 1B B1 FA 18，  
应该就是加密了，  
使用模块跑一下  
下载地址：  
<https://www.sweetscape.com/010editor/repository/templates/>

![](https://p0.ssl.qhimg.com/t0183f1b6bad5932ff2.png)

导入后，跑一下

![](https://p3.ssl.qhimg.com/t01fca6c08baa3d764f.png)

出错，绝逼是加密了，如果没加密正常是能跑通的，找个没加密的跑一下，正常是这样的，如下图

![](https://p4.ssl.qhimg.com/t01a917dd6b151b1661.png)

这里说一下如何计算global-metadata.dat大小的，  
查看metadataHeader段

![](https://p1.ssl.qhimg.com/t0131b1f625fdc8d2d7.png)

有各种偏移和大小，计算整个文件大小就在这里面，  
直接查看最后一个

![](https://p3.ssl.qhimg.com/t01e32d7dd2e8e3bbcf.png)

大小和偏移加起来就是0x55c118 + 0xf0c = 0x55D024  
Ctrl+G,直接跳转到该偏移，刚好是文件末尾

![](https://p1.ssl.qhimg.com/t0180b6dfdf6dae2dfa.png)

看了很多文件，最后一个属性都是在0x108,0x10C，有个注意点就是如果最后一个属性的值比倒数第二个小的话，就取倒数第二个的属性值。  
基于以上两点，我们祭出frida，写下js脚本  
解释如下：

![](https://p1.ssl.qhimg.com/t012ee4a120c68de721.png)

代码如下：

    
    
     /*
    获取解密后的global-metadata.dat
    github:https://github.com/350030173/global-metadata_dump
    
    用法：
    frida -U -l global-metadata_dump.js packagename
    
    导出的文件在/data/data/yourPackageName/global-metadata.dat
    
    */
    
    
    
    //
    //get_self_process_name()获取当前运行进程包名
    //参考：https://github.com/lasting-yang/frida_dump/blob/master/dump_dex_class.js
    function get_self_process_name()
    {
    var openPtr = Module.getExportByName('libc.so', 'open');
    var open = new NativeFunction(openPtr, 'int', ['pointer', 'int']);
    
    var readPtr = Module.getExportByName("libc.so", "read");
    var read = new NativeFunction(readPtr, "int", ["int", "pointer", "int"]);
    
    var closePtr = Module.getExportByName('libc.so', 'close');
    var close = new NativeFunction(closePtr, 'int', ['int']);
    
    var path = Memory.allocUtf8String("/proc/self/cmdline");
    var fd = open(path, 0);
    if (fd != -1)
    {
        var buffer = Memory.alloc(0x1000);
    
        var result = read(fd, buffer, 0x1000);
        close(fd);
        result = ptr(buffer).readCString();
        return result;
    }
    
    return "-1";
    }
    
    function frida_Memory(pattern)
    {
    Java.perform(function ()
    {
        console.log("头部标识:" + pattern);
        var addrArray = Process.enumerateRanges("r--");
        for (var i = 0; i < addrArray.length; i++)
        {
            var addr = addrArray[i];
            Memory.scan(addr.base, addr.size, pattern,
            {
                onMatch: function (address, size)
                {
                    console.log('搜索到 ' + pattern + " 地址是:" + address.toString());
                    console.log(hexdump(address,
                        {
                            offset: 0,
                            length: 64,
                            header: true,
                            ansi: true
                        }
                        ));
                    //0x108，0x10C如果不行，换0x100，0x104
                    var DefinitionsOffset = parseInt(address, 16) + 0x108;
                    var DefinitionsOffset_size = Memory.readInt(ptr(DefinitionsOffset));
    
                    var DefinitionsCount = parseInt(address, 16) + 0x10C;
                    var DefinitionsCount_size = Memory.readInt(ptr(DefinitionsCount));
    
                    //根据两个偏移得出global-metadata大小
                    var global_metadata_size = DefinitionsOffset_size + DefinitionsCount_size
                        console.log("大小：", global_metadata_size);
                    var file = new File("/data/data/" + get_self_process_name() + "/global-metadata.dat", "wb");
                    file.write(Memory.readByteArray(address, global_metadata_size));
                    file.flush();
                    file.close();
                    console.log('导出完毕...');
                },
                onComplete: function ()
                {
                    //console.log("搜索完毕")
                }
            }
            );
        }
    }
    );
    }
    
    setImmediate(frida_Memory("AF 1B B1 FA 18")); //global-metadata.dat头部特征
    

安装游戏后，游戏启动，attach上

![](https://p3.ssl.qhimg.com/t01fc9d50127e8a3cdd.png)

导出的文件在你的游戏的私有目录下，/data/data/yourpackagename/global-metadata.dat  
之后导出放在电脑上，使用010查看

![](https://p2.ssl.qhimg.com/t01a724131e2e49bd12.png)

嗯，正常了，最后在使用Il2CppDumper导出dump.cs，  
那就可以愉快的分析了。。。

有兴趣的可以进群交流，QQ群:542863693，主要用于手游安全分析

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **灯-等灯等灯~** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/226685](/post/id/226685)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [游戏安全](/tag/游戏安全)

 **+1** __5赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) 灯-等灯等灯~

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

