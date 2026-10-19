# TLSv1.2网络安全协议学习

阅读量 **325256**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-11-30 15:30:52

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t019fba4e8d1d0df063.jpg)

## TLS协议概述

TLS前身为NetScape公司设计的SSL协议，之后由IETF形成了TLS标准，现在已发展到TLSv1.3版本。

TLS工作在传输层之上，应用层之下。接收应用层报文的数据提供保密性与完整性服务。

TLSv1.2版本包含5个子协议：Handshake、ChangeCipherSpec、Alert、Application

![](https://p1.ssl.qhimg.com/t016f7dcd4e577a30b9.png)

如今，TLS协议已经得到了广泛的使用，常用的HTTPS就是基于TLS协议提供的安全性服务。

## TLS描述语言

为了无二意地表述TL协议的各个子协议，需要先引入TLS的描述语言。语法与C语言非常类似

**基本原则** ：

  * 基本数据块大小为1字节（1 byte）
  * 注释由 / _开始_ / 结束
  * [[ ]] 表示可选的部件
  * 包含无具体含义的单字节实体，类型标识为opaque

**定长向量** ：表示为 `T Vector[n]`。Vector为向量名，T为向量数据类型，n为向量的 **字节数**

**变长向量** ：表示为 `T Vector<min..max>`。Vector为向量名，T为向量数据类型，min和max分别为向量最小和最大的
**字节数**

**枚举** ：用来表示某个变量可能的取值，表示为 `enum {e1(v1),e2(v2),···,en(vn)[[n]]}name`。其中

  * `name`是枚举变量的变量名
  * `ei`是枚举变量`name`可能的取值
  * `vi`是`ei`的具体指代数值
  * `n`表示可能取值的个数

**结构** ：用来表示一个特殊的变量，这个变量由不同类型的数据组成，表示为

    
    
    struct{
        T1 V1;
        T2 V2;
        ···
        Tn Vn;
    } [[name]]
    

其中

  * `Ti`表示变量类型
  * `Vi`表示变量名
  * `name`表示结构变量变量名

**变体** ：根据实际选择不同，成员变量可选择不同数据类型，表示为

    
    
    select(E){
        case e1: T1;
        case e2: T2;C
        ···
        case en: Tn;
    } [[fv]]
    

其中

  * `E`是要判定的变量
  * `ei`是`E`的取值
  * `Ti`是对应的数据类型
  * `fv`是变体变量变量名

## TLSv1.2 各个子协议

###  TLS Record协议

Record协议工作在其他子协议的更下层，简单而言，Record协议接收上层协议的内容，封装后交给传输层传输。

####  Record协议的功能

  * 消息传输：上层其他子协议将其数据提交给缓冲区，Record协议传输这些缓冲区中的数据。如果缓冲区超过长度限制，则需要进行分片；如果缓冲区过小，可以合并 **属于同一协议的** 小缓冲区内的内容
  * 完成加密和完整性验证：按照协商好的密码学套件和安全参数进行加密和完整性验证
  * 压缩： **设计上** 为了提高传输效率提供了压缩的功能。但是实践中，由于压缩功能存在安全性问题，所以一般没有实现。

####  Record协议封装过程图示

![](https://p1.ssl.qhimg.com/t0104dc602f4374730e.png)

####  Record Header

![](https://p3.ssl.qhimg.com/t0161f4fdaa91365cd4.png)

Record协议包含一个5字节的首部，其中包含三个字段`ContentType`、`ProtocolVersion`和`length`

  * `ContentType`表示上层子协议的类型，长为1 byte，描述如下： 
    
        enum{
        change_cipher_spec(20), /*ChangeCipherSpec协议*/
        alert(21),/*Alert协议*/
        handshake(22),/*Handshake协议*/C
        application_data(23),/*ApplicationData协议*/
        (255) /*总共255个可选值*/C
    }ContentType
    

  * `ProtocolVersion`表示协议版本号，包含一个大版本一个小版本，长为2 byte，描述如下： 
    
        struct{
        uint8 major;
        uint8 minor;C
    }ProtocolVersion
    

各个版本对应的取值如下：

![](https://p1.ssl.qhimg.com/t011d59559746bee9e4.png)

  * `length`表示数据的长度(不包括Record Header)，长为2 byte

Record协议封装后的报文分片描述如下（已加密）：

    
    
    struct{
        ContentType type;
        ProtocolVersion Version;
        uint16 length;
        select (SecurityParameters.cipher_type){
            case stream: GenericStreamCipher; /*流密码*/
            case block: GenericBlockCipher; /*分组密码*/
            case aead: GenericAEADCipher; /*AEAD模式*/
        }fragment /*数据分片*/
    }TLSCiphertext
    

###  TLS Handshake协议

####  Handshake功能

Handshake协议是TLS中最复杂的一个协议，在这个协议运行之后，需要完成如下事项：

  * 身份认证：确定客户端服务器的合法身份
  * 密码套件协商：商定相同的密码套件，否则无法通讯
  * 密钥协商：商定会话使用的密钥

####  Handshake对话过程

  * 先通俗地描述一下会话过程：客户端先与服务器取得联系。客户端随机告诉服务器，我可以使用RSA/AES和DSS/AES密码套件，需要选用哪一个密码套件进行会话。服务端告诉客户端选用RSA/AES密码套件通信，并且将证书发给客户端。客户端与服务器达成一致，切换密码套件，准备通信。
  * 形式化地描述：上述是一个简单的不太严谨的描述，下图是更加严谨的形式化的描述：

![](https://p4.ssl.qhimg.com/t01fce5737b13f0208f.png)

之后将会详细地阐释每个消息的含义

####  Handshake消息结构

用TLS描述语言描述如下

    
    
    enum {
        hello_request(0), client_hello(1), server_hello(2),  certificate(11), server_key_exchange (12),          certificate_request(13), server_hello_done(14),  certificate_verify(15),    
        client_key_exchange(16),  finished(20),
        (255)
    } HandshakeType; /*定义handshake消息类型*/
    struct{
        HandshakeType msg_type; /*Handshake消息类型*/
        uint24 length; /*消息长度*/
        select (HandshakeType){
            case hello_request: HelloRequest;
            case client_hello: ClientHello;
            case server_hello: ServerHello;
            case certificate: Certificate;
            case server_key_exchange: ServerKeyExchange;
            case certificate_request: CertificateRequest;
            case server_hello_done: ServerHelloDone;
            case certificate_verify: CertificateVerify;
            case client_key_exchange: ClientKeyExchange;
            case finished: Finished;C
        } body; /*消息体*/
    } Handshake;
    

####  Handshake：HelloRquest

**作用**
：用于和Client重新开始一次协商过程，Client应在之后发送一个ClientHello开始协商。如果此时Client正在进行一个协商，那么这条消息将被忽略。

**消息图示** ：

![](https://p4.ssl.qhimg.com/t01f17049170c0239ff.png)

####  Handshake：ClientHello

ClientHello是一次握手流程中的第一条消息，随着这条消息Client发送其 **支持的功能** 和 **首选项** 给服务器。

**发送ClientHello的情况** ：

  * 新建连接时
  * 重新协商时
  * 响应重建连接请求（HelloRequest）时

**消息图示** ：

![](https://p1.ssl.qhimg.com/t01bd3c867bedcfa7b4.png)

**ClientHello消息格式** ：

使用TLS描述性语言描述如下：

    
    
    struct {
        uint32 gmt_unix_time;  
        opaque random_bytes[28];
    } Random; /*Random类型包括时间和一个随机的字节数组*/
    opaque SessionID<0..32>;  uint8 CipherSuite[2]; /*密码学套件，两个字节的ID*/
    enum {null(0), (255)} CompressionMethod; /*压缩方法，不启用*/
    
    
    enum {
        signature_algorithms(13), (65535)
    } ExtensionType; /*定义扩展类型*/
    struct {
        ExtensionType extension_type;  
        opaque extension_data<0..2^16‐1>;
    } Extension; /*扩展类型*/
    
    struct {
        ProtocolVersion client_version; /*协议版本*/
        Random random; /*随机数*/ 
        SessionID session_id; /*会话ID，方便会话重用*/
        CipherSuite cipher_suites<2..2^16‐2>;  /*密码套件（多个），客户端首选的密码套件放在第一位
                                               注意：如果SessionID不为0，即要重用一个会话时，这个字段必须至少包括重用会                                           话使用的密码套件。*/
        CompressionMethod compression_methods<1..2^8‐1>;  /*压缩方法*/
        select (extensions_present) { /*扩展*/
            case false:    
                struct {};  
            case true:
                Extension extensions<0..2^16‐1>;
        };
    } ClientHello;
    

**抓包实例** ：

推荐一个TLS协议学习网站https://tls.ulfheim.net/，不仅包含TLSv1.2，也可以学习到TLSv1.3

抓取到的ClientHello如下：

![](https://p3.ssl.qhimg.com/t0136489ba8568b5708.png)

![](https://p3.ssl.qhimg.com/t018c41ab1e4044a608.png)

可以看到其中的各个字段值。

####  Handshake：ServerHello

当收到来自客户端的ClientHello的时候，如果在服务端能够找到对应的一套密码套件，那么服务器发送ServerHello消息响应客户端的ClientHello消息。如果不能找到匹配的算法，则返回一个警告。

**消息图示** ：

![](https://p5.ssl.qhimg.com/t0195bbc3c3373c415f.png)

**ServerHello消息格式** ：

用TLS描述语言描述如下：

    
    
    /*ServerHello与ClientHello基本一致，主要区别在于cipher_suite只包含最终确定使用的那一个*/
    struct {
        ProtocolVersion server_version;
        Random random;  
        SessionID session_id;
        CipherSuite cipher_suite;  /*只有一个确定使用的密码套件*/
        CompressionMethod compression_method;  
        select (extensions_present) {
            case false:
                struct {};  
            case true:
                Extension extensions<0..2^16‐1>;
        };
    } ServerHello;
    

**抓包实例** ：

![](https://p1.ssl.qhimg.com/t01204c848432821832.png)

可以见得，这一条报文中包含了多条消息，证实了TLSv1.2会将小的消息在不影响语义的情况下合并在一起进行发送。

![](https://p1.ssl.qhimg.com/t01f0a00430b7582d29.png)

可以看到ServerHello的报文中的密码套件只有一个，这就是之后需要使用的密码套件

####  Handshake：Certificate

服务器向客户端发送的证书，使得客户端能够认证服务器的身份。在匿名通讯时，服务器不需要发送证书。

**消息图示** ：

![](https://p0.ssl.qhimg.com/t0191b2c9e5970451d5.png)

**Certificate消息格式** ：

    
    
    opaque ASN.1Cert<1..2^24-1>;
    
    struct {
        ASN.1Cert certificate_list<0..2^24-1>;
    } Certificate;
    

ASN.1(抽象语法表示法1)，是支持复杂数据结构和对象的定义、传输、交换的一系列规则

**抓包实例** ：

![](https://p5.ssl.qhimg.com/t0124d1ed716e2951e8.png)

这里的证书是一条证书链，通过一级一级的证书认证Server证书的合法性。

####  Handshake：ServerKeyExchange

服务器发送了ServerCertificate消息之后立即发送ServerKeyExchange消息。同时，仅当之前发送的消息不足以让客户端交换premaster
secret(预主密钥)的时候，才会发送ServerKeyExchange消息。例如，通过非对称加密方式加密 premaster secret
时不需要发送ServerKeyExchange消息，因为客户端已经可以利用公钥传递 premaster secret 了。

**消息图示** ：

![](https://p5.ssl.qhimg.com/t0162bf122b8e44fac8.png)

**ServerKeyExchange消息格式** ：

    
    
    struct {
        uint8 Type;
        uint24 Length;
        obaque Parameters<0..2^24-1>;
    } ServerKeyExchange
    

**抓包实例** ：

![](https://p5.ssl.qhimg.com/t01fb4bbc91e86f1208.png)

这是抓到的ServerKeyExchange的消息，可见是通过ECDHE模式进行密钥交换的，同时使用RSA进行了签名，这与协商的结果一致。

####  Handshake：CertificateRequest

服务器发送CertificateRequest消息，要求客户端进行身份验证。消息中包含了服务器接受的 **证书类型列表** 以及可接受的 **CA列表**

**消息图示** ：

![](https://p5.ssl.qhimg.com/t01b12fcbf5c50e0513.png)

**CertificateRequest消息格式** ：

    
    
    struct {
        ClientCertificateType certificate_types<1..2^8‐1>;
        DistinguishedName certificate_authorities<0..2^16‐1>;
    } CertificateRequest;
    

####  Handshake：ServerHelloDone

服务器发送ServerHelloDone来完成密钥交换，服务器发送该消息后，便等待客户端相应。

**消息图示** ：

![](https://p4.ssl.qhimg.com/t019d573e84310722ce.png)

ServerHelloDone消息将不包含任何内容，只有type和length信息

**抓包实例** ：

![](https://p4.ssl.qhimg.com/t0116af0f2ed2335bb4.png)

发送了ServerKeyExchange消息后，Server完成了自己的协商部分的工作，于是发送ServerHelloDone给客户端

####  Handshake：ClientKeyExchange

在客户端收到ServerHelloDone之后马上发送ClientKeyExchange消息，如果需要发送Certificate消息，那么ClientKeyExchange消息需紧跟Certificate消息发送。如果密码套件中选用RSA等公钥加密算法，那么ClientKeyExchange发送加密后的premaster
secret；如果密码套件中选择Diffie-Hellman进行密钥交换，那么ClientKeyExchange发送DH中的公开值。

**消息图示** ：

![](https://p2.ssl.qhimg.com/t01c789d8c34f68e1e0.png)

**ClientKeyExchange消息格式** ：

    
    
    struct {
        select (KeyExchangeAlgorithm) {  
            case rsa: /*以RSA为例的公钥加密算法*/
                EncryptedPreMasterSecret;  
            case dhe_dss:
            case dhe_rsa:
            case dh_dss:
            case dh_rsa:
            case dh_anon:
                ClientDiffieHellmanPublic;
        } exchange_keys; /*区分公钥加密的密钥和利用DH交换的密钥*/
    } ClientKeyExchange;
    

**抓包实例** ：

![](https://p5.ssl.qhimg.com/t01920aa45c9366ce12.png)

![](https://p0.ssl.qhimg.com/t015bb7dc93776ed654.png)

####  Handshake：CertificateVerify

当服务器器向客户端发送了CertificateRequest消息时，客户端才需要发送CertificateVerify消息证明自身确实持有相应的证书和私钥

**消息图示** ：

![](https://p4.ssl.qhimg.com/t016ce540c1502e4029.png)

**CertificateVerify消息格式** ：

    
    
    struct {
        digitally‐signed struct {
            opaque handshake_messages[handshake_messages_length];
            /*handshake_messages指到这一步为止所有握手消息的拼接*/
            /*对handshake_messages进行签名进行验证*/
        } 
    } CertificateVerify;
    

####  Handshake：Finished

发送Finished消息表示握手结束，并且随消息发送一个密文，这个密文对应的明文是一个PRF（伪随机函数）的输出，该PRF的输入为master_secret（主密钥）、finished_label（分客户端和服务器）以及所有之前的握手消息组合的hash值。

**Finished消息的目的** ：

  * 确认收到的Finished消息是否正确
  * 确认握手协议是否正常结束
  * 确认密码套件切换是否正确

**消息图示** ：

![](https://p1.ssl.qhimg.com/t0133c78fccf9ae3474.png)

**Finished消息格式** ：

    
    
    struct {
        opaque verify_data[verify_data_length];
    } Finished;
    
    verify_data PRF(master_secret, finished_label,  Hash(handshake_messages))[0..verify_data_length‐1];
    /*finished_label分Client和Server版本*/
    

**抓包实例** ：

![](https://p2.ssl.qhimg.com/t0178eb7bec35dc9340.png)

在实际的抓包中，在ChangeCipherSpec消息之后会有一个Encrypted Handshake
Message消息，这个消息就是Finished消息。

**防止降级攻击** ：

所谓降级攻击，是一个作为中间人的攻击者通过篡改ClientHello中的密码套件列表，用弱密码套件替代用户设置的密码套件，从而达到降低会话安全性的目的。通过Finished消息，客户端和服务器都验证了握手消息的hash值，如果攻击者篡改了之前的消息，那么验证就会失败，从而达到防御降级攻击的目的。

###  TLS ChangeCipherSpec协议

ChangeCipherSpec协议比较简单，就是按照之前的约定切换密码套件

**消息图示** ：

![](https://p2.ssl.qhimg.com/t0134e57dcea53e156c.png)

**消息格式** ：

    
    
    struct {
        enum { change_cipher_spec(1), (255) } type;
    } ChangeCipherSpec;
    

**抓包实例** ：

![](https://p0.ssl.qhimg.com/t015d89f0910f7f7d2e.png)

###  TLS Alert协议

根据发生的不同状况，Alert协议报告异常或者直接中断连接

**消息图示** ：

![](https://p3.ssl.qhimg.com/t01726511729aed6006.png)

**消息格式** ：

    
    
    enum {
        warning(1), fatal(2), (255)
    } AlertLevel; /*定义告警的级别，现只有警告和致命两个级别*/
    
    struct {
        AlertLevel level;  
        AlertDescription description;
    } Alert;
    
    enum {
        close_notify(0),
        unexpected_message(10),  bad_record_mac(20),  decryption_failed_RESERVED(21), record_overflow(22),     
        decompression_failure(30),  handshake_failure(40),  no_certificate_RESERVED(41),bad_certificate(42), 
        unsupported_certificate(43),  certificate_revoked(44),  certificate_expired(45),      
        certificate_unknown(46),illegal_parameter(47),  unknown_ca(48),  access_denied(49),  
        decode_error(50), decrypt_error(51),  export_restriction_RESERVED(60),  protocol_version(70),  
        insufficient_security(71), internal_error(80),  user_canceled(90),  no_renegotiation(100),  
        unsupported_extension(110), (255)
    } AlertDescription; /*各种具体告警信息的定义*/
    

告警信息的定义如下：

![](https://p3.ssl.qhimg.com/t014249a50e6a7d4c8e.png)

**close_notify警报** ：

如果某方决定关闭连接时，需要发送自己的close_notify警报，而不是发送FIN关闭TCP连接，原因是为了防止截断攻击。

所谓 **截断攻击** ，即是指攻击者主动发送TCP
FIN包，意图结束通信，达到DoS的效果。而如果关闭连接需要发送close_notify警报的话，那么攻击者就没有权限使服务器中断一个连接，从而达到防御的效果。

###  TLS ApplicationData协议

这个协议就是承载加密后的应用层数据，并且计算一个消息认证码MAC以保证数据完整性

**消息图示** ：

![](https://p3.ssl.qhimg.com/t0112e11ea2aa57d701.png)

## TLSv1.2 密码套件

###  属性

TLSv1.2的密码套件包含如下属性：

  * 身份认证算法
  * 密钥交换算法
  * 加密算法（对称加密算法）
  * 加密密钥长度
  * 加密算法模式（可用时选填）
  * MAC算法（可用时选填）
  * 伪随机函数（PRF）
  * 用于Finished消息中的散列函数

###  格式

TLSv1.2中的密码套件表示遵循以下格式：

    
    
    TLS_[密钥交换算法]_[认证算法]_WITH_[[加密算法]_[密钥长度]_[算法模式]]_[MAC或PRF]
    

举个例子：

    
    
    TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
    

在这个例子中，可以从这个表示读出以下的信息

  * 身份认证算法——RSA
  * 密钥交换算法——ECDHE
  * 加密算法——AES
  * 加密密钥长度——128
  * 加密算法模式——GCM
  * 伪随机函数（PRF）——SHA-256

在表示时，每个密码套件都有一个对应的长为2字节的值用来标识，详情可以参见IANA的密码套件列表

###  特殊密码套件

在TLS握手的初始阶段中，需要使用到如下的空密码套件：

    
    
    TLS_NULL_WITH_NULL_NULL
    

标识的值为{0x00, 0x00}，这个密码套件不提供任何安全保护，并且不可进行协商

## TLSv1.2 密钥导出

TLSv1.2的密钥导出流程总体如下：

![](https://p3.ssl.qhimg.com/t0153649f90875cac58.png)

下面分别阐释每个部分的细节

###  预主密钥（pre_master_secret)

在`ClientKeyExchange`消息中便包含了一个经过处理之后的 **pre_master_secret** ，用TLS描述语言可描述如下

    
    
    struct{
        ProtocolVersion client_version;
        opaque random[46]; // 46字节的随机数
    }PreMasterSecret // 总计大小为48字节
    

在接收到预主密钥之后，接下来按如下的方法导出一个长为48字节的主密钥（可能输出长度超过48字节，截取适合长度即可）：

    
    
    master_secret = PRF(pre_master_secret, "master secret", ClientHello.random + ServerHello.random)[0..47];
    

  * `PRF()`：伪随机函数
  * `pre_master_secret`：预主密钥
  * `"master secret"`：一个字符串，作为label来表示生成的是什么密钥
  * `ClientHello.random和ServerHello.random`：客户端和服务器的随机数，合起来作为PRF函数的种子

其中，伪随机函数PRF的定义如下：

    
    
    PRF(secret, label, seed) = P_hash(secret, label+seed);
    P_hash(secret, seed) = HMAC_hash(secret, A(1) + seed) + // '+'在这里表示拼接字符串
                           HMAC_hash(secret, A(2) + seed) +
                           HMAC_hash(secret, A(3) + seed) + ···;
    // A()的定义
    A(0) = seed;
    A(i) = HMAC_hash(secret, A(i-1));
    

`P_hash`是一个数据扩展函数，使用选用的hash函数、密钥以及种子，可以扩展出任意长度的输出。例如使用hash函数为SHA-256，那么如果需要用`p_SHA256`生成长为48字节的密钥，那么只需迭代2次得到一个64字节的输出，截取前48字节作为密钥即可。

###  主密钥扩展

在双方得到相同的主密钥`master_secret`的时候，接下来就需要扩展出使用的密钥了。

    
    
    key_block = PRF(master_secret, "key expansion", server_random, client_random);
    

经过PRF函数的扩展，客户端与服务器只需要以相同的方法对这个key_block进行切割就可以得到相同的密钥

## 会话恢复

如此前提到的那样，TLSv1.2 协议可以利用SessionID恢复之前建立的会话

###  握手时的SessionID：

握手时用户和服务器发送的SessionID有两种情况：

  * 情况一：客户端发送的ClientHello消息中的SessionID为空（长度为0），表示这是一个新建立的会话。服务器对这条消息可能有如下回复： 
    * ServerHello消息的SessionID为空，那么服务器之后没有重用该会话的打算
    * ServerHello消息的SessionID为一个随机值，那么这个SessionID将标识当前的会话，客户端会保存该SessionID及相关的会话信息
  * 情况二：客户端发送的ClientHello消息中的SessionID不为空，表示想要重建SessionID标识的会话，服务器对这条消息可能有如下回复： 
    * ServerHello消息的SessionID为空，表示服务器因为某些原因不会重建会话，之后将进行完整的握手
    * ServerHello消息的SessionID与ClientHello消息的SessionID相同，那么说明服务器找到了SessionID对应的会话配置，并且将和ClientHello重建该会话

###  重建会话流程

![](https://p3.ssl.qhimg.com/t01a87b8e39080a891f.png)

###  SessionID的安全性

####  问题

  * 如果为每个会话维护一个SessionID，那么这将消耗服务器大量的存储空间
  * 对于有负载均衡的服务器集群，共享一个SessionID的缓存很困难

总而言之，SessionID重用会话的机制会给服务器带来过大的开销。

现阶段，为了解决SessionID带来的困难，通常采用的是 **Session Ticket** 机制

###  Session Ticket

####  Session Ticket的格式

    
    
    struct{
        opaque key_name[16];
        opaque iv[16];
        opaque encrypted_state<0..2^16-1>; 
        opaque mac[32];
    }ticket
    

  * key_name：用来标识一系列用来保护ticket的密钥
  * encrypted_state：加密的会话状态，加密由服务器进行，加密前的明文如下

    
    
    struct{
        ProtocolVersion protocol_version; // 协议版本
        CipherSuite ciphe_suite; // 密码套件
        CompressionMethod compression_method; // 压缩方法
        opaque master_secret[48]; // 主密钥
        ClientIdentity client_identity; // 客户端身份
        uint32 timestamp; // 一个时间戳
    }State
    

  * mac：对该ticket的消息认证码，输入key_name、IV、encrypted_state的长度以及encrypted_state本身

####  Session Ticket的使用

  * 客户端在创建会话时，在ClientHello消息中包含一个空的Session Ticket扩展，表示自己支持Session Ticket功能
  * 服务器接收到ClientHello之后，也发送一个空的Session Ticket扩展给客户端，表示自己支持该功能
  * 之后，服务器使用NewSessionTicket消息发送一个Session ticket给客户端
  * 客户端保存Session ticket，之后要使用时发送Session ticket给服务器即可

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **FFFcaptain328** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/222627](/post/id/222627)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [TLS](/tag/TLS)

 **+1** __9赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=vAHee0rrE6FYMEcr3bIzxA&s=40&t=1603034478)
FFFcaptain328

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

