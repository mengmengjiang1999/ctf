安卓逆向第九篇-某里系代码伪装so案例sgmain

[ 萌木盖](https://www.jianshu.com/u/0e56159ab5a7)关注赞赏支持

# 安卓逆向第九篇-某里系代码伪装so案例sgmain

# 发现

首先是观察注解里的`main` 和so名字相近。并且没壳没接口实现类。怀疑在so中。  

image.png

# 打开so

打不开。有了些莫名其妙的东西。发现是个zip。不是so。

  

image.png

# 打开dex

将解压后的dex打开后，果然发现了实现类。但是最终调用的是libsgmainso-6.5.49.so

  

image.png

# 再次打开so

崩了，但打不开。表头被修改了。

  

image.png

# 修改表头

使用010editor修改`e_shoff`、`e_shnum`为0 地址分别为：0x20-0x23 , 0x30-0x31，这里0x31本来就是0
所以我没改。  

image.png

# 重新打开ida

正常打开

  

image.png

# 参考

根据网上教程学着简单分析一款so----修改section头表 <https://www.jianshu.com/p/6b65ee2b4325>  
详细分析一款移动端浏览器安全性
[https://www.anquanke.com/post/id/179080](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.anquanke.com%2Fpost%2Fid%2F179080)  
利用NanoHTTPD反射调用Android APP加密函数
[https://curz0n.github.io/2018/05/31/nanohttpd_encrypt/](https://links.jianshu.com/go?to=https%3A%2F%2Fcurz0n.github.io%2F2018%2F05%2F31%2Fnanohttpd_encrypt%2F)  
ida无法打开某大厂so文件 无法分析对应函数
[https://bbs.pediy.com/thread-259146.htm](https://links.jianshu.com/go?to=https%3A%2F%2Fbbs.pediy.com%2Fthread-259146.htm)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [逆向小白成长录](https://www.jianshu.com/p/e273049a4c20)

逆向小白成长录 前言 作为一个曾经从事过C、C++、C#、Java开发的野生程序员，在经过几年软件开发工作后，准备...

[安全fun](https://www.jianshu.com/u/f1cb9bb3cc18)阅读 112评论 0赞 0

  * [安卓逆向环境搭建](https://www.jianshu.com/p/808ba82b8da1)

篇幅有限 完整内容及源码关注公众号：ReverseCode，发送冲 刷机 https://developers.g...

[布丁和尚](https://www.jianshu.com/u/b2a63c970be4)阅读 891评论 0赞 0

  * [【kernel exploit】CVE-2021-22555 2字节堆溢出写0漏洞提权分析](https://www.jianshu.com/p/71edad1a3d9c)

文章首发于安全客：CVE-2021-22555 2字节堆溢出写0漏洞提权分析[https://www.anquan...

[bsauce](https://www.jianshu.com/u/a12c5b882be2)阅读 1,603评论 0赞 2

  * [android 加固、脱壳技术资料整理](https://www.jianshu.com/p/a75f3c88c089)

so 加固分析 通过一款早期代码抽取壳入门学习 so 层分析-0x指纹大神[https://bbs.pediy.c...

[牵手生活](https://www.jianshu.com/u/e09dc5872735)阅读 796评论 0赞 5

  * [2021-02-24-模糊测试（WinAFL）](https://www.jianshu.com/p/2ef0026ede57)

模糊测试 [https://lyj789.github.io/2021/02/24/CTF%E5%9F%BA%E7...

[L1E6N0A2](https://www.jianshu.com/u/6574db71f7b2)阅读 1,609评论 0赞 0

 