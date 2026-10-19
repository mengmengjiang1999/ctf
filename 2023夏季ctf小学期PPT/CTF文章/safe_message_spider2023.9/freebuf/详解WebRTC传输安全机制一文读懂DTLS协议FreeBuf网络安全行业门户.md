作者｜进学

审校｜泰一

DTLS (Datagram Transport Layer Security) 基于 UDP 场景下数据包可能丢失或重新排序的现实情况下，为 UDP
定制和改进的 TLS 协议。在 WebRTC 中使用 DTLS 的地方包括两部分：协商和管理 SRTP 密钥和为 DataChannel 提供加密通道。

![](https://image.3001.net/images/20210915/1631699308_6141c16c81ca5367b0164.png!small)

本文结合实际数据包分析 WebRTC 使用 DTLS 进行 SRTP 密钥协商的流程。并对在实际项目中使用 DTLS 遇到的问题进行总结。

## DTLS 协议简介

在分析 DTLS 在 WebRTC 中的应用之前，先介绍下 DTLS 协议的基本原理。DTLS 协议由两层组成: Record 协议 和 Handshake
协议

  1. Record 协议：使用对称密钥对传输数据进行加密，并使用 HMAC 对数据进行完整性校验，实现了数据的安全传输。

  2. Handshake 协议：使用非对称加密算法，完成 Record 协议使用的对称密钥的协商。

### HandShake

TLS 握手协议流程如下，参考
[RFC5246](https://tools.ietf.org/html/rfc5246?spm=a2c6h.12873639.0.0.4c9a21a8kxR03N#section-7.3)

![](https://image.3001.net/images/20210915/1631699899_6141c3bb752e295534ba1.png!small)

DTLS 握手协议流程如下，参考
[RFC6347](https://tools.ietf.org/html/rfc6347?spm=a2c6h.12873639.0.0.4c9a21a8kxR03N#section-4.2.4)

![](https://image.3001.net/images/20210915/1631699900_6141c3bcb971bc54e287b.png!small)

TLS 和 DTLS 的握手过程基本上是一致的，差别以及特别说明如下：

  * DTLS 中 [HelloVerifyRequest](https://tools.ietf.org/html/rfc6347)是为防止 DoS 攻击增加的消息。

  * TLS 没有发送 [CertificateRequest](https://tools.ietf.org/html/rfc5246#section-7.4.4)，这个也不是必须的，是反向验证即服务器验证客户端。

  * DTLS 的 RecordLayer 新增了 SequenceNumber 和 Epoch，以及 ClientHello 中新增了 Cookie，以及 Handshake 中新增了 Fragment 信息（防止超过 UDP 的 MTU），都是为了适应 UDP 的丢包以及容易被攻击做的改进。参考 [RFC 6347](https://tools.ietf.org/html/rfc6347#section-4.2.2)

  * DTLS 最后的 Alert 是将客户端的 Encrypted Alert 消息，解密之后直接响应给客户端的，实际上 Server 应该回应加密的消息，这里我们的服务器回应明文是为了解析客户端加密的那个 Alert 包是什么。

RecordLayer 协议是和 DTLS 传输相关的协议，UDP 之上是 RecordLayer，RecordLayer 之上是 Handshake 或
ChangeCipherSpec 或 ApplicationData。RecordLayer 协议定义参考
[RFC4347](https://tools.ietf.org/html/rfc4347)，实际上有三种 RecordLayer 的包:

  * `DTLSPlaintext`，DTLS 明文的 RecordLayer。

  * `DTLSCompressed`，压缩的数据，一般不用。

  * `DTLSCiphertext`，加密的数据，在 ChangeCipherSpec 之后就是这种了。

没有明确的字段说明是哪种消息，不过可以根据上下文以及内容判断。比如 ChangeCipherSpec 是可以通过类型，它肯定是一个 Plaintext。除了
Finished 的其他握手，一般都是 Plaintext。

## SRTP 密钥协商

### 角色协商

在 DTLS 协议，通信的双方有`Client`和`Server`之分。在 WebRTC 中 DTLS 协商的身份是在`SDP`中描述的。描述如下，参考
[SDP-Anatomy](https://webrtchacks.com/sdp-anatomy/)中 DTLS 参数

    
    
    a=setup:active
    

`setup`属性在 [RFC4145](https://tools.ietf.org/html/rfc4145#section-4.1)，

setup:active，作为 client，主动发起协商

setup:passive, 作为 sever，等待发起协商

setup:actpass, 作为 client，主动发起协商。作为 server，等待发起协商。

### 算法协商 - Hello 消息

ClienHello 和 ServerHello 协商 DTLS 的 Version、CipherSuites、Random、以及 Extensions。  
![](https://image.3001.net/images/20210915/1631699902_6141c3be10c8aefca935d.png!small)  
![](https://image.3001.net/images/20210915/1631699905_6141c3c1064e676b252f4.png!small)

  * `Version`：Client 给出自己能支持的、或者要使用的最高版本，比如 DTLS1.2。Server 收到这个信息后，根据自己能支持的、或者要使用的版本回应，比如 DTLS1.0。最终以协商的版本也就是 DTLS1.0 为准。

  * `CipherSuites`：Client 给出自己能支持的加密套件 CipherSuites，Server 收到后选择自己能支持的回应一个，比如 TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA (0xc014)，加密套件确定了证书的类型、密钥生成算法、摘要算法等。

  * `Random`：双方的随机数，参与到生成 MasterSecret。MasterSecret 会用来生成主密钥，导出 SRTP 密钥。详见 [导出 SRTP 密钥]

  * `Extensions`：Client 给出自己要使用的扩展协议，Server 可以回应自己支持的。比如 Client 虽然设置了 SessionTicket TLS 这个扩展，但是 Server 没有回应，所以最终并不会使用这个扩展。

#### Cipher Suite

![](https://image.3001.net/images/20210915/1631699908_6141c3c47a38b805bdb98.png!small)

在 Hello 消息中加密套接字使用`IANA`中的注册的名字。IANA 名字由 Protocol，Key Exchange
Algorithm，Authentication Algorithm，Encryption Algorithm ，Hash Algorithm
的描述组成。例如，TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 的含义如下：

  * `Protocol`: Transport Layer Security (TLS)

  * `Key Exchange`: Elliptic Curve Diffie-Hellman Ephemeral (ECDHE)

  * `Authentication`: Rivest Shamir Adleman algorithm (RSA)

  * `Encryption`: Advanced Encryption Standard with 128bit key in Galois/Counter mode (AES 128 GCM)

  * `Hash`: Secure Hash Algorithm 256 (SHA256)

> 加密套接字在 [ciphersuite.info](https://ciphersuite.info/cs/)可以查到。在查到 IANA
> 名字的同时，也可以查到在 OpenSSL 中的名字。TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 在 OpenSSL
> 中的名字为 ECDHE-RSA-AES128-GCM-SHA256  
> Note: 关于 Authentication (认证)、KeyExchange (密钥交换)、Encryption (加密)、MAC (Message
> Authentication Code) 消息摘要等，可以参考 [RSA
> 密钥协商](https://www.zhihu.com/question/25116415)。

#### Extension

DTLS 的扩展协议，是在 ClientHello 和 ServerHello 的 Extensions 信息中指定的，所有的 TLS 扩展参考 [TLS
Extensions](https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml)。下面列出几个 WebRTC 用到的扩展：

  * `use_srtp`: DTLS 握手完成后 (Finished)，使用 SRTP 传输数据，DTLS 生成 SRTP 的密钥。 [RFC5764](https://tools.ietf.org/html/rfc5764)。ClientHello 中的扩展信息定义了 [RFC5764 4.1.2. SRTP Protection Profiles](https://tools.ietf.org/html/rfc5764#page-8)和 [srtp_mki](https://tools.ietf.org/html/rfc5764#section-4.1.3)。  
![](https://image.3001.net/images/20210915/1631699910_6141c3c6abe58b22e9965.png!small)

  * `supported_groups`，原来的名字为 elliptic_curves，描述支持的 ECC 加密算法，参考 [RFC8422 5.1.1.Supported Elliptic Curves Extension](https://tools.ietf.org/html/rfc8422#section-5.1.1)，一般用的是 secp256r1。  
![](https://image.3001.net/images/20210915/1631699912_6141c3c84a75cc90bfc28.png!small)

  * `signature_algorithms`，DTLS1.2 的扩展，指定使用的 Hash 和 Signature 算法，参考 [RFC5246 7.4.1.4.1. Signature Algorithms](https://tools.ietf.org/html/rfc5246#section-7.4.1.4.1)。DTLS1.0，RSA 用的是 md5sha1 摘要算法，DSA 用的是 sha1 摘要算法。  
![](https://image.3001.net/images/20210915/1631699914_6141c3caa21a4a0aec75c.png!small)

  * `extended_master_secret`，扩展 MasterSecret 的生成方式，参考 [RFC7627](https://tools.ietf.org/html/rfc7627)。在 KeyExchange 中，会加入一些常量来生成 MasterSecret。TLS 定义了扩展方式，如果用这个扩展，DTLS 的方式和 TLS 会有些不同。

  * `renegotiation_info`, 参考 [RFC5746](https://tools.ietf.org/html/rfc5746#section-3.2)

除了这些扩展协议，和 SRTP 密钥导出相关的还有：

> RFC5705: Keying Material Exporters for Transport Layer Security (TLS)，DTLS
> 如何从 MasterSecret 导出 Key，比如 SRTP 的 Key。  
> RFC5764: DTLS Extension to Establish Keys for the SRTP，DTLS 的 use_srtp
> 扩展的详细规范，包括 ClientHello 扩展定义、Profile 定义、Key 的计算。

### 身份验证 - Certificate

![](https://image.3001.net/images/20210915/1631699916_6141c3cca301e5b859fe6.png!small)  
数字证书是由一些公认可信的证书颁发机构签发的，不易伪造。数字证书可以用于接收者验证对端的身份，接收者收到某个对端的证书时，会对签名颁发机构的数字签名进行检查，一般来说，接收者事先就会预先安装很多常用的签名颁发机构的证书（含有公开密钥），利用预先的公开密钥可以对签名进行验证。

Server 端通过 Hello 消息，协商交换密钥的方法后，将 Server 证书发送给 Client，用于 Client 对 Server
的身份进行校验。Server 发送的证书必须适用于协商的 KeyExchange 使用的加密套接字，以及 Hello 消息扩展中描述的
Hash/Signature 算法对。

在 WebRTC 中，通信的双方通常将无法获得由知名根证书颁发机构 (CA)
签名的身份验证证书，自签名证书通常是唯一的选择。[RFC4572](https://tools.ietf.org/html/rfc4572)定义一种机制，通过在`SDP`中增加自签名证书的安全哈希，称为
"证书指纹"，在保证 SDP 安全传输的前提下，如果提供的证书的指纹与`SDP`中的指纹匹配，则可以信任自签名证书。在实际的应用场景中，SDP
在安全的信令通道 (https) 完成交换的，SDP 的安全完整是可以做到的。这样在 DTLS
协商过程中，可以使用证书的指纹，完成通信双方的身份校验。证书指纹在 SDP 中的描述如下，参考 [SDP-Anatomy](https://webrtchacks.com/sdp-anatomy/)中 DTLS 参数

    
    
    a=fingerprint:sha-256 49:66:12:17:0D:1C:91:AE:57:4C:C6:36:DD:D5:97:D2:7D:62:C9:9A:7F:B9:A3:F4:70:03:E7:43:91:73:23:5E
    

### 密钥交换 - KeyExchange

ServerKeyExchange 用来将 Server 端使用的公钥，发送给 Client 端。分为两种情况：

  1. `RSA`算法：如果服务端使用的是 RSA 算法，可以不发送这个消息，因为 RSA 算法使用的公钥已经在 Certificate 中描述。

  2. `DH`算法，是根据对方的公钥和自己私钥计算共享密钥。因为 Client 和 Server 都只知道自己的私钥，和对方的公钥；而他们的私钥都不同，根据特殊的数学特性，他们能计算出同样的共享密钥。关于 DH 算法如何计算出共享密钥，参考 [DH 算法](http://www.voidcn.com/article/p-rgubrwfd-bpg.html)。

![](https://image.3001.net/images/20210915/1631699918_6141c3ced94e391ab0c2d.png!small)

ClientKeyExchange 用来将 Client 使用的公钥，发送给 Server 端。

  1. `RSA`算法：如果密钥协商使用的 RSA 算法，发送使用 server 端 RSA 公钥，对 premaster secret 加密发送给 server 端。

  2. `DH`算法：如果密钥协商使用的 DH 算法，并且在证书中没有描述，在将客户端使用的 DH 算法公钥发送给 Server 端，以便计算出共享密钥。  
KeyExchange 的结果是，Client 和 Server 获取到了 RSA Key， 或通过 DH 算法计算出共享密钥。详见 [导出 SRTP
密钥] 的过程

### 证书验证 - CertificateVerify

使用 ClientRequest 中描述的 Hash/Signature 算法，对收到和发送的 HandShake 消息签名发送个
Server。Server 端对签名进行校验。

![](https://image.3001.net/images/20210915/1631699920_6141c3d0565393decf88c.png!small)

### 加密验证 - Finished

当 Server 和 Client 完成对称密钥的交换后，通过`ChangeCipherSpec`通知对端进入加密阶段，epoch 加 1。

随后 Client 使用交换的密钥，对 "client finished" 加密，使用 Finished 消息，发送给服务端。Server
使用交换的密钥，对 "server finished" 进行加密发送给客户端。一旦验证了 finished 消息后，就可以正常通信了。  
![](https://image.3001.net/images/20210915/1631699921_6141c3d1f2d835223a7ac.png!small)

## 导出 SRTP 密钥

上面介绍了 DTLS 的过程，以下通过结合上面例子给出的实际数据，详细说明 SRTP 密钥的导出步骤。

### 协商后的加密算法

加密套件：TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (0xc02f)  
椭圆曲线算法为：secp256r1，椭圆曲线的点压缩算法为：uncompressed。  
椭圆曲线算法的基础知识的介绍在 [ECC 椭圆曲线加密算法 -ECDH,ECDHE,ECDSA](https://zhuanlan.zhihu.com/p/66794410)，由文档中我们可以知道，确定椭圆曲线加密算法有如下参数：

  * 素数 p，用于确定有限域的范围

  * 椭圆曲线方程中的 a，b 参数

  * 用于生成子群的的基点 G

  * 子群的阶 n

  * 子群的辅助因子 h  
定义为`六元组(p,a,b,G,n,h)`

通过在 [SECG-SEC2 2.4.2 Recommended Parameters
secp256r1](http://www.secg.org/sec2-v2.pdf)中可以查到 secp256r1 对应的参数如下：

    
    
    secp256r1使用的参数如下：
    使用的素数p:
    p=FFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
    =2224(232−1)+2192+296−1
    椭圆曲线E:y^2=x^3+ax+b的参数定义如下：
    a=FFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC
    b=5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
    基点G的非压缩格式：
    G=046B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C2964FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5
    有限域的阶n:
    n=FFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    辅助因子h:
    h=01
    

### 通过 KeyExchange 交换椭圆曲线算法公钥

ECDH Server Parameter

    
    
    Pubkey:04b0ce3c5f2c4a9fbe7c2257c1328438f3378f74e9f528b6e27a00b44eee4c19e5e6b2cb6cab09f796bcf8c05102b2a4bcdc753d91cc4f431f558c845a1ba6f1ce
    

记为`Spk`

ECDH Client Paramter

    
    
    PubKey: 0454e8fbef1503109d619c39be0ccaf89efa3c3962300476465cbc66b15152cd8a900c45d506420f0123e65d8fbb70cb60b497893f81c5c2a0ef2f4bc2da996d9e
    

记为`Cpk`

### 根据 ECDHE 算法计算共享密钥 S (pre-master-secret)

假设 Server 的使用的椭圆曲线私钥为 Ds, Client 使用的 Dc，计算共享密钥的如下，参考 [ECC 椭圆曲线加密算法 -ECDH,ECDHE,ECDSA](https://zhuanlan.zhihu.com/p/66794410)

S = Ds * Cpk = Dc * Spk

这个共享密钥`S`就是我们在 RFC 文档中看到的`pre-master-secret`

### 计算 master secret

计算`master secret`过程如下，可参考 [Computing the Master
Secret](https://tools.ietf.org/html/rfc5246#section-8.1)

    
    
    master_secret = PRF(pre_master_secret, "master secret", ClientHello.random + ServerHello.random)[0..47];
    

计算出来的`master_secret`为 48 Bytes，其中`ClientHello.random`和`ServerHello.random`在
Hello 消息中给出。`PRF`是伪随机数函数 (pseudorandom function)，在协商的加密套件中给出。

### 使用 master_secrete 导出 SRTP 加密参数字节序列

使用 [RFC5705 4. Exporter
Definition](https://tools.ietf.org/html/rfc5705#section-4)给出的计算方式，使用参数`master_secret`，`client_random`，`server_random`计算字节序列：

    
    
    key_block = PRF(master_secret, "EXTRACTOR-dtls_srtp", client_random + server_random)[length]
    

在 [DTLS-SRTP 4.2. Key
Derivation](https://tools.ietf.org/html/rfc5764#section-4.2)中描述了需要的字节序列长度。

    
    
    2 * (SRTPSecurityParams.master_key_len + SRTPSecurityParams.master_salt_len) bytes of data
    

master_key_len 和 master_salt_len 的值，在`user_srtp`描述的 profile 中定义。我们的实例中使用的
profile 为`SRTP_AES128_CM_HMAC_SHA1_80`，对应的 profile 配置为：

    
    
    SRTP_AES128_CM_HMAC_SHA1_80
            cipher: AES_128_CM
            cipher_key_length: 128
            cipher_salt_length: 112
            maximum_lifetime: 2^31
            auth_function: HMAC-SHA1
            auth_key_length: 160
            auth_tag_length: 80
    

也就是我们需要`(128/8+112/8)*2 = 60 bytes`字节序列。

### 导出 SRTP 密钥

计算出 SRTP 加密参数字节序列，在 [DTLS-SRTP 4.2. Key
Derivation](https://tools.ietf.org/html/rfc5764#section-4.2)描述了字节序列的含义：

    
    
    client_write_SRTP_master_key[SRTPSecurityParams.master_key_len]; // 128 bits
    server_write_SRTP_master_key[SRTPSecurityParams.master_key_len]; // 128 bits
    client_write_SRTP_master_salt[SRTPSecurityParams.master_salt_len]; // 112 bits
    server_write_SRTP_master_salt[SRTPSecurityParams.master_salt_len]; // 112 bits
    

至此我们得到了，Client 和 Server 使用的 SRTP 加密参数：master_key 和 master_salt.

## DTLS 超时重传

DTLS 是基于 UDP 的，不可避免会出现丢包，需要重传。如果处理不当，会导致整个通信双方无法建立会话，通话失败。[RFC6347
4.2.4](https://tools.ietf.org/html/rfc6347#section-4.2.4)给出了超时和重传机制。  
在处理重传时，以下几点需要注意：

  1. 在 DTLS 协议中，为了解决丢包和重传问题，新增了 [message_seq.](https://tools.ietf.org/html/rfc6347#section-4.2.2)在发送 DTLS 重传消息时，一定要更新其中的`message_seq`，这样对端将把包识别是一个重传包，响应正确消息。否则，会默默丢弃这些包，不进行响应。

  2. 当 server 端收到 client 的 FINISHED 消息，并发送 FINISHED 消息给 client，更新 server 状态为协商完成，开始发送 SRTP 数据。此时发送给 client 的 FINISHED 消息，出现丢包。client 收到 SRTP 数据后丢弃。同时，再次发送 FINISHED 消息到 server，server 要正确响应。否则，会导致 DTLS 协商完成的假象，通话失败。

  3. 使用 openssl 1.1.1 之前版本，无法设置 DTLS 超时重传时间，可以超时重传机制不可用，大家开始转向使用 boringssl。openssl 1.1.1 开始版本已经支持设置 DTLS 超时重传，达到和 boringssl 同样的效果。参考 [DTLS_set_timer_cb](https://www.openssl.org/docs/man1.1.1/man3/DTLS_set_timer_cb.html)

## OpenSSL 的 DTLS 功能

DTLS 是一个庞大的协议体系，其中包括了各种加密，签名，证书，压缩等多种算法。大多数项目是基于 OpenSSL 或 BoringSSL 实现的 DTLS
功能。在实际项目使用 OpenSSL 的 DTLS 功能，与协商有关的接口总结如下。

  1. [X509_digest](https://www.openssl.org/docs/man1.1.0/man3/X509_digest.html)，计算证书 fingerprint，用在 SDP 协商中的`fingerprint`属性。

  2. [SSL_CTX_set_cipher_list](https://www.openssl.org/docs/manmaster/man3/SSL_CTX_set_cipher_list.html)，设置使用的加密套件，通过设置算法的描述，影响 Hello 消息中的 cipher list。

  3. [SSL_CTX_set1_sigalgs_list](https://www.openssl.org/docs/man1.1.0/man3/SSL_CTX_set1_sigalgs_list.html)设置签名算法。通过设置签名算法的描述，影响 hello 消息中`signature_algorithms`扩展。`signature_algorithms`对 DTLS 的`Hello 消息`，`KeyExchange`，`CerficateVerify`消息。`signature_algorithms`设置不正确，会出现 internal error，不容易定位问题。

  4. [SSL_CTX_set_verify](https://www.openssl.org/docs/man1.0.2/man3/SSL_CTX_set_verify.html)设置是否校验对端的证书。由于在 RTC 中大多数据情况下使用自签证书，所以对证书的校验，已校验身份是需要的。

  5. [SSL_CTX_set_tlsext_use_srtp](https://www.openssl.org/docs/man1.1.1/man3/SSL_CTX_set_tlsext_use_srtp.html)设置`srtp`扩展。srtp 扩展中的 profile，影响 srtp 加密时使用密钥的协商和提取。

  6. [SSL_set_options](https://www.openssl.org/docs/man1.1.0/man3/SSL_set_options.html)使用`SSL_OP_NO_QUERY_MTU`和 [SSL_set_mtu] 设置 fragment 的大小。默认 OpenSSL 使用 fragment 较小。通过上面两个接口，设置适合网络情况的 fragment。

  7. [DTLS_set_timer_cb](https://www.openssl.org/docs/man1.1.1/man3/DTLS_set_timer_cb.html)，设置超时重传的 Callback，由 callback 设置更合理的超时重传时间。

在开源项目 [SRS](https://github.com/ossrs/srs)中已经支持了 WebRTC 的基础协议，对 DTLS
协议感兴趣的同学，可以基于 SRS 快速搭建本机环境，通过调试，进一步加深对 DTLS 的理解。

## 总结

本文通过 WebRTC 中 SRTP 密钥的协商过程，来说明 DTLS 在 WebRTC 中的应用。DTLS 协议设计的各个加密算法的知识较多，加上 TLS
消息的在各种应用场景中的扩展，难免有理解和认知不到的地方，还需要进一步深入探索。

## 参考文献

  1. [TLS 1.2](https://tools.ietf.org/html/rfc5246)

  2. [DTLS 1.2](https://tools.ietf.org/html/rfc6347)

  3. [TLS Session Hash Extension](https://tools.ietf.org/html/rfc7627)

  4. [TCP-Based Media Transport in the Session Description Protocol](https://tools.ietf.org/html/rfc4145)

  5. [TLS Extension](https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml)

  6. [SRTP Extension for DTLS](https://tools.ietf.org/html/rfc5764)

  7. [OpenSSL Man](https://www.openssl.org/docs/man1.1.1/man3)

  8. [ECC 椭圆曲线加密算法 - 介绍](https://zhuanlan.zhihu.com/p/36326221)

  9. [ECC 椭圆曲线加密算法 - 有限域和离散对数](https://zhuanlan.zhihu.com/p/44743146)

  10. [ECC 椭圆曲线加密算法 - ECDH、ECDHE 和 ECDSA](https://zhuanlan.zhihu.com/p/66794410)

>
> 「视频云技术」你最值得关注的音视频技术公众号，每周推送来自阿里云一线的实践技术文章，在这里与音视频领域一流工程师交流切磋。公众号后台回复【技术】可加入阿里云视频云技术交流群，和作者一起探讨音视频技术，获取更多行业最新信息。

