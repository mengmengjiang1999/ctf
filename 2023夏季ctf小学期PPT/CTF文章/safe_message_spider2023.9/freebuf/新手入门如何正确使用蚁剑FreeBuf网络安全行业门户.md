## 前言

蚁剑（antsword）是一款优秀的webshell管理工具，使用该工具的时候可能是很多人最幸福的时刻之一，因为使用该工具代表着我们经过千辛万苦获取到了一定的权限，但如果我们使用不当，这很可能是我们最悲伤的时候

很多人对于webshell管理工具的使用可能很粗糙，比如上传了一句话木马后，就直接使工具连接了。但现在的安全设备已经十分熟悉蚁剑这一类工具的指纹信息了，可能我们刚连上木马，下一秒权限就丢失了

所以本文将会从头讲解如何正确的使用蚁剑，正确享受美好的时刻

## 设置代理

使用代理主要目的是隐藏自身，注意使用代理可以连接内网shell的技巧不要忘了。另外可以设置代理地址为burp，自己抓包看看 antsword 的流量

![image.png](https://image.3001.net/images/20211219/1639911779_61bf11631aaeebfa95ae6.png!small)

## 请求头配置

antsword 最明显的流量特征就是 User-Agent，不过我下载的最新版竟然会自动生成 User-Agent。为了安全还是设置一下

![image.png](https://image.3001.net/images/20211219/1639911794_61bf1172505ba588380b2.png!small)

设置好后可以用 burp 抓包验证一下

![image.png](https://image.3001.net/images/20211219/1639911807_61bf117fb8096852620cc.png!small)

## 编码器

User-Agent 设置好后，但我们却发现注入的代码基本是明文传输，如果目标有防火墙之类的设备，我们会很难连接上shell

antsword 提供了几种编码器也可以尝试使用，如 chr 编码器，PHP
类型独有，通信时使用`chr`函数对传输的字符串进行处理拼接，可以看到请求中除了 eval 字样没有明显的特征信息

![image.png](https://image.3001.net/images/20211219/1639911820_61bf118c83ce5222b45c4.png!small)

hex 编码器，ASPX, CUSTOM 类独有，将通信数据字符转成16进制数据传输

另外我找到 antsword 在 github
上也提供了一些编码器：https://github.com/AntSwordProject/AwesomeEncoder

我这里以 **aes_128_ecb_zero_padding.js** 为例，演示一下怎么去设置使用这些编码器

复制代码先手动添加编码器和解码器

![image.png](https://image.3001.net/images/20211219/1639911836_61bf119ca0d5091a42124.png!small)

该编码器是需要特定的shell配合的，所以我们上传的shell需要单独定制，如该编码器需要的shell如下：

    
    
    <?php
    @session_start();
    $pwd='ant';
    $key=@substr(str_pad(session_id(),16,'a'),0,16);
    @eval(openssl_decrypt(base64_decode($_POST[$pwd]), 'AES-128-ECB', $key, OPENSSL_RAW_DATA|OPENSSL_ZERO_PADDING));
    ?>
    

链接shell时要选好对应的编码器和解码器

![image.png](https://image.3001.net/images/20211219/1639911851_61bf11ab136c07bd6b043.png!small)

可以抓包看下流量，基本上没有什么特征信息了

![image.png](https://image.3001.net/images/20211219/1639911862_61bf11b62c60b48fd3cea.png!small)

如果能做到webshell免杀和通信流量隐藏，我们就会拥有稳稳的幸福

参考：

蚁剑官方文档：https://www.yuque.com/antswordproject/antsword

