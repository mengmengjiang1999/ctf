原创：冬青合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

![v2-b6ac4acb391e97c8ef3bf1f3f5fe9a62_hd.w](https://pic2.zhimg.com/80/v2-b6ac4acb391e97c8ef3bf1f3f5fe9a62_hd.webp)

NTLM hash

NTLMhash通常是指Windows系统下SecurityAccount Manager中保存的用户密码hash。

通常Mimikatz是通过读取lsass.exe进程来获得已登录用户的NTLMhash

## NTLMhash的产生  

将明文口令转换成十六进制，转换成Unicode格式，然后对Unicode字符串进行MD4加密，这个结果就是32位的十六进制NTLMhash

![v2-a17f39b0263ccd7b5082f9456ca34bcd_hd.w](https://pic1.zhimg.com/80/v2-a17f39b0263ccd7b5082f9456ca34bcd_hd.webp)

Net-NTLM hash

通常是指网络环境下NTLM认证中的hash，在挑战/响应中产生。Responder获取的也就是Net-NTLMhash。

## NTLM协议认证过程  

①客户端向服务器发送一个包含登录用户名的请求

②服务器接收到请求后，生成一个16位的随机数，这个随机数被称为Challenge,明文发送回客户端。使用登录用户名对应的NTLMHash加密Challenge，获得Challenge1，生成challeng1同时将challenge发送到客户端

③客户端接受到Challenge后，使用将要登录到账户对应的NTLMHash加密Challenge生成Response，然后将Response发送至服务器端。

PS：经过NTLMHash加密的Challenge称为NetNTLM Hash。

④服务器端收到客户端的Response后，比对Chanllenge1与Response是否相等，若相等，则认证通过。

更多资料参考如下

<https://www.secpulse.com/archives/94848.html>

![v2-bf4dd73df11d94303ce4193bd4b64177_hd.w](https://pic1.zhimg.com/80/v2-bf4dd73df11d94303ce4193bd4b64177_hd.webp)

利用responder获取Net-NTLMhash

命令：responder-I eth0 -wrf

![v2-a615de462b7958959a0cfa8ba0923322_hd.w](https://pic1.zhimg.com/80/v2-a615de462b7958959a0cfa8ba0923322_hd.webp)

当受害者使用了远程连接服务器的命令，responder便能捕获该hash

![v2-f533d9302ace5bf5abe942f61e39c1b9_hd.w](https://pic2.zhimg.com/80/v2-f533d9302ace5bf5abe942f61e39c1b9_hd.webp)

上图就是responder捕获到的Net-NTLMv2hash

![v2-8eca10306f15d37895c9e4a1e29a2feb_hd.w](https://pic3.zhimg.com/80/v2-8eca10306f15d37895c9e4a1e29a2feb_hd.webp)

利用hashcat破解该hash

Hashcat-m
5600costin::TEST:e62ca9c0128f9f75:1EE76BC14356C7C6AB25E9EC6CEA7908:0101000000000000B2425466A03BD501EB22E06A81D76659000000000200060053004D0042000100160053004D0042002D0054004F004F004C004B00490054000400120073006D0062002E006C006F00630061006C000300280073006500720076006500720032003000300033002E0073006D0062002E006C006F00630061006C000500120073006D0062002E006C006F00630061006C000800300030000000000000000000000000200000CD9794483DF117EF10B298CAD00E1102A255C9747EAFB278F152A3BBFE38CFB30A001000000000000000000000000000000000000900220048005400540050002F003100390032002E003100360038002E0031002E00310032000000000000000000/root/Desktop/1.txt
--force

-m：5600对应NetNTLMv2

\--force代表强制执行，因为系统不支持IntelOpenCL

![v2-e473b6a8b68e1e1187eb65d8cab0365a_hd.w](https://pic4.zhimg.com/80/v2-e473b6a8b68e1e1187eb65d8cab0365a_hd.webp)

可以看到，密码被成功破解，破解成功的密码是Net-NTLMhash，接下来，我们用这个密码来攻击这台机器

![v2-7fb3202cc174136567e57785c3756ddc_hd.w](https://pic4.zhimg.com/80/v2-7fb3202cc174136567e57785c3756ddc_hd.webp)

攻击失败，无法利用hash传递来进行攻击，如果攻击成功可以获取到NTLMhash来进行hash传递攻击，所以这里换个思路进行。

![v2-bf6d294526f12eab48e6dc3b64acae96_hd.w](https://pic4.zhimg.com/80/v2-bf6d294526f12eab48e6dc3b64acae96_hd.webp)

利用responder来进行中继攻击（MultiRelay）

该攻击不需要对responder获取到hash进行破解，可以直接利用该hash攻击其他机器，禁用Responder.conf文件中的http服务和smb服务

![v2-be707a5be93ae14fc59909996cfc7353_hd.w](https://pic1.zhimg.com/80/v2-be707a5be93ae14fc59909996cfc7353_hd.webp)

运行responder

命令：responder-I eth0 -v -F

同时运行该工具

./MultiRelay.py-t 192.168.1.110 -u ALL

需要注意的是，需要中继的机器必须要有域管理员权限或本地管理员权限，否则，是无法利用的

![v2-e466981786ee95534769a745d5d46ff1_hd.w](https://pic2.zhimg.com/80/v2-e466981786ee95534769a745d5d46ff1_hd.webp)

这里通过中继拿到了这台机器的shell

![v2-8b392d4626c7fd260c4b3c571a8964cf_hd.w](https://pic1.zhimg.com/80/v2-8b392d4626c7fd260c4b3c571a8964cf_hd.webp)

MultiRelay提供了自带的命令例如mimil命令来调用Mimikatz函数

![v2-ab47d0687f86455849be04b51783b580_hd.w](https://pic1.zhimg.com/80/v2-ab47d0687f86455849be04b51783b580_hd.webp)

这里我们通过该shell来加载一个meterpreter

使用exploit/multi/script/web_delivery并按下图进行设置

![v2-84794564a1dc1b1d0735d1a0658e5b8e_hd.w](https://pic4.zhimg.com/80/v2-84794564a1dc1b1d0735d1a0658e5b8e_hd.webp)

加载payloadwindows/x64/meterpreter/reverse_https并运行之后会生成一段powershell代码

![v2-f07c32347a40ec38e0ac4f6471ecb12a_hd.w](https://pic3.zhimg.com/80/v2-f07c32347a40ec38e0ac4f6471ecb12a_hd.webp)

将该powershell代码放在该主机的shell里运行

![v2-523830e8cd0fdd8ff9bd2fedd7aba5af_hd.w](https://pic2.zhimg.com/80/v2-523830e8cd0fdd8ff9bd2fedd7aba5af_hd.webp)

不久就会弹回一个meterpreter

![v2-d0fc8b13e7a6d39b7b8b62fad9b2f8f1_hd.w](https://pic1.zhimg.com/80/v2-d0fc8b13e7a6d39b7b8b62fad9b2f8f1_hd.webp)

总结：这是一个常规的方法来拿到一个域内的主机，要想拿到域控还得不断的进行信息收集以及利用。

参考资料：

<https://blog.csdn.net/nzjdsds/article/details/94314995>

<https://www.secpulse.com/archives/94848.html>

![v2-a79f3ccfcdcddcfccf8d8e039e539803_hd.w](https://pic4.zhimg.com/80/v2-a79f3ccfcdcddcfccf8d8e039e539803_hd.webp)

相关实操推荐

解密WindowsNTLMHash
：hashcat号称世界上最快的密码破解，世界上第一个和唯一的基于GPGPU规则引擎，免费多GPU（高达128个GPU），多哈希，多操作系统（Linux和Windows本地二进制文件），多平台（OpenCL和CUDA支持），多算法，资源利用率低，基于字典攻击，支持分布式破解等等。

点击“[实验:解密Windows NTLM
Hash(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID821e-a70f-4ae3-9aeb-01b0fd47656c)”，可预览学习（PC端操作最佳哟）

![v2-1a4fef2038de1c1e4832271e9a2b9d36_hd.w](https://pic1.zhimg.com/80/v2-1a4fef2038de1c1e4832271e9a2b9d36_hd.webp)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！

