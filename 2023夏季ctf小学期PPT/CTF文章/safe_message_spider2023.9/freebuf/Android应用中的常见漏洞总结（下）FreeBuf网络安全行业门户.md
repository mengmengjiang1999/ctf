Android应用中的常见漏洞总结下期来啦，和小编一起看看吧~

##  **Zip包下载**

###  **UnZip解压文件漏洞**

 **描述：**

Zip
slip漏洞其实也是目录遍历的一种，通过应用程序解压恶意的压缩文件进行攻击。恶意攻击者通过构造一个压缩文件条目中带有../的压缩文件，上传后交给应用程序进行解压。由于程序解压时没有对文件名进行合法性的校验，而是直接将文件名拼接在待解压目录后面，导致可以将文件解压到正常解压缩路径之外并覆盖可执行文件，从而等待系统或用户调用他们实现代码执行（也可能是覆盖配置文件或其他敏感文件）。

 **背景知识：**

在Linux/Unix系统中“../”代表的是向上级目录跳转，有些程序在当前工作目录中处理到诸如用“../../../../../../../../../../../etc/hosts”表示的文件，会跳转出当前工作目录，跳转到到其他目录中。

Java代码在解压ZIP文件时，会使用到ZipEntry类的getName()方法，如果ZIP文件中包含“../”的字符串，该方法返回值里面原样返回，如果没有过滤掉getName()返回值中的“../”字符串，继续解压缩操作，就会在其他目录中创建解压的文件。

 **产生原理 ：**

因为ZIP压缩包文件中允许存在"../"的字符串，攻击者可以利用多个“../”在解压时改变ZIP包中某个文件6存放位置，覆盖掉应用原有的文件。如果被覆盖掉的文件是动态链接so、dex或者odex文件，轻则产生本地拒绝服务漏洞，影响应用的可用性，重则可能造成任意代码执行漏洞，危害用户的设备安全和信息安全.。

##  **Android签名类**

 **描述：**

Android具有签名机制。正常情况下，开发者发布了一个应用，该应用一定需要开发者使用他的私钥对其进行签名。恶意攻击者如果尝试修改了这个应用中的任何一个文件（包括代码和资源等），那么他就必须对APK进行重新签名，否则修改过的应用是无法安装到任何Android设备上的。但如果恶意攻击者用另一把私钥对APK签了名，并将这个修改过的APK对用户手机里的已有应用升级时，就会出现签名不一致的情况。因此，在正常情况下，Android的签名机制起到了防篡改的作用。但如果恶意攻击者利用漏洞，那么恶意攻击者就可以任意地修改一个APK中的代码（包括系统的内置应用），同时却不需要对APK进行重新签名。换句话说，用这种方式修改过的APK，Android系统会认为它的签名和官方的签名是一致的，但在这个APK运行时，执行的却是恶意攻击者的代码。恶意攻击者利用这个修改过的APK，就可以用来覆盖安装原官方应用（包括系统的内置应用）。

###  **“MasterKey”漏洞**

 **背景知识：**

Android签名的Signature Version V1 Android7.0之前的签名方式，使用jar
Signature方式对APK进行签名打包，jar Signature来自JDK。APK进行签名时会生成一个META-INF文件夹，里面有三个文件：MANIFEST.MF，CERT.RSA，CERT.SF，是用来记录签名信息的。

 **MANIFEST.MF：**

逐一遍历所有条目，如果是目录就跳过，如果是一个文件，就用SHA1（或者SHA256）消息摘要算法提取出该文件的摘要然后进行BASE64编码后，作为“SHA1-Digest”属性的值写入到MANIFEST.MF文件中的一个块中。该块有一个“Name”属性，其值就是该文件在apk包中的路径。

 **CERT.SF：**

1.计算这个MANIFEST.MF文件的整体SHA1值，再经过BASE64编码后，记录在CERT.SF主属性块（在文件头上）的“SHA1-Digest-Manifest”属性值值下。

2.逐条计算MANIFEST.MF文件中每块的SHA1，并经过BASE64编码后，记录在CERT.SF中的同名块中，属性的名字是“SHA1-Digest”。

CERT.RSA是一个满足PKCS7格式的文件：它会把之前生成的 CERT.SF文件，用私钥计算出签名,
然后将签名以及包含公钥信息的数字证书一同写入CERT.RSA中保存。

 **漏洞利用：**

1.向原始的App APK的前部添加一个攻击的classes.dex文件（A)；

2.安卓系统在校验时计算了A文件的hash值，并以”classes.dex”字符串做为key保存；

3.然后安卓计算原始的classes.dex文件（B），并再次以”classes.dex”字符串做为key保存，这次保存会覆盖掉A文件的hash值，导致Android系统认为APK没有被修改，完成安装；

4.APK程序运行时，系统优先以先找到的A文件执行，忽略了B，导致漏洞的产生。

###  **“9695860”漏洞**

 **背景知识：**

在每个Zip文件中都有一个Central directory，Central directory中的每一项是一个File header。这个File
header的结构对应到Android代码的类就是ZipEntry。File header结构中有一个偏移量指向local file
header，local file header后面就紧跟着file data。

    
    
    local file header signature     4 bytes  
    version needed to extract      2 bytes
    general purpose bit flag         2 bytes
    compression method              2 bytes
    last mod file time                    2 bytes
    last mod file date                    2 bytes
    crc-32                                     4 bytes
    compressed size                     4 bytes
    uncompressed size                 4 bytes
    file name length                      2 bytes
    extra field length                     2 bytes
    file name (variable size)
    extra field (variable size)
    
    //android 进行apk校验
    RAFStream rafstrm = new RAFStream(raf, entry.mLocalHeaderRelOffset + 28);
    DataInputStream is = new DataInputStream(rafstrm);
    int localExtraLenOrWhatever = Short.reverseBytes(is.readShort());
    is.close();
    
    // Skip the name and this "extra" data or whatever it is:
    rafstrm.skip(entry.nameLength + localExtraLenOrWhatever);
    rafstrm.mLength = rafstrm.mOffset + entry.compressedSize;
    if (entry.compressionMethod == ZipEntry.DEFLATED) {
    int bufSize = Math.max(1024, (int)Math.min(entry.getSize(), 65535L));
    return new ZipInflaterInputStream(rafstrm, new Inflater(true), bufSize, entry);
    } else {
    return rafstrm;
    }

 **漏洞原理：**

Java代码在读取“Central directory file header”结构的“Extra field
length”字段（java代码视为有符号short，C代码视为无符号short）时，如果大小超过0x7FFF则认为是负数，代码逻辑将负数一律按零处理。

> 1\. 向原有的APK中的classes.dex文件B替换为攻击文件A，并添加一个大小为0xFFFD的extrafield；
>
> 2\. 将原始dex文件B去除头3个字节写入extrafield；
>
> 3\. Android系统在校验签名时使用的是Java代码的short，将0xFFFD以16位带符号整形的方式解析得到-3,
> 并解析出原始的文件B，Android认为程序APK没有修改，正常安装；
>
> 4\. 系统在执行时使用C代码的uint16，将0xFFFD以16位无符号整形方式，得到攻击文件B。

按照正常逻辑，android读取local file header的file name length 和 extra field
length,跳转到file data
对classws.dex校验，hack后按照以下模型，java校验读原来的，没什么问题，但c读取classes.dex是读去我们的fake dex。

![](https://image.3001.net/images/20210518/1621327496_60a37e88dc7bacef6a837.png!small)

###  **“9950697”漏洞**

Signature Version V1的第3个洞，适用于android4.4以下的版本

 **漏洞原理：**

Android在校验签名时，解析Apk包用的是java代码（ZipFile.java和ZipEntry.java），而在安装apk时，包括解压、dexopt等，用的是c代码（ZipArchive.cpp），这两份代码在解析ZipEntry时的步骤都是先从索引段读取ZipEntry的信息，然后定位到数据段。

数据段中的ZipEntry的Data[]字段是用来存放真正的压缩数据的。Java和c定位到Data[]字段的方法都是根据Data[]字段之前的字段的长度计算偏移：

Data[]的偏移 = ZipEntry的偏移 + 固定header的长度 + extraFieldLength + fileNameLength

Java使用的fileNameLength是从索引段的ZipEntry获得的，而C则是从数据段的ZipEntry获得的，所以就这里造成了不一致性，导致java和c定位到的data[]不一致。因此可以在数据段的ZipEntry中构造一个不一样的fileNameLength，进而让java校验签名时读取的是合法的文件，而c在安装是读取的是恶意的文件，绕过签名验证。

###  **“janus”漏洞（CVE-2017-13156）**

 **背景知识：**

Android在4.4引入ART虚拟机，相比较于Dalvik虚拟机仅能运行包装于apk中的dex文件，ART还允许直接运行优化后的dex文件。具体操作是通过读取文件头部的magic字段进行判断，区别执行apk或者dex。

ZIP文件的读取方式是读取文件末尾定位的central directory, 然后通过里面的索引定位到各个zip
entry，每个entry解压之后都对应一个文件。ParseZipArchive()函数在进行以上处理时候并没有判断文件头部的magic字段是否为504B0304，即Zip。

 **漏洞原理：**

攻击者可以通过将恶意dex文件置于apk文件的头部(如下图所示)。在系统安装apk文件时，系统安装器解压zip时并没有先判断apk文件的头部magic字段，默认是apk(zip)文件，从而直接从文件尾部进行读取解压，此时签名没有任何变化，因此可欺骗系统，从而进行安装。

攻击关键点是当用户点击运行apk时，系统ART虚拟机会去判断文件头部的magic字段，从而使用不同的策略执行文件，由于该apk文件头部被修改为恶意dex，因此art虚拟机直接执行恶意dex文件。

 **攻击模型：**

![](https://image.3001.net/images/20210518/1621327509_60a37e95732d76934f7e5.png!small)
参考链接：[https://blog.checkpoint.com/2018/08/12/man-in-the-disk-a-new-attack-surface-for-android-apps/﻿](https://blog.checkpoint.com/2018/08/12/man-in-the-disk-a-new-attack-surface-for-android-apps/)

