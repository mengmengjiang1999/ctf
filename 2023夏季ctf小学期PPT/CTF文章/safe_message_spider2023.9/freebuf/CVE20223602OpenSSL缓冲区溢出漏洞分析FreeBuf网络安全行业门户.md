## 0x1 背景介绍

OpenSSL官方在2022年11月1号发布了漏洞编号为CVE-2022-3602的缓冲区溢出漏洞，起初该漏洞的评级被设定为 **严重**
，但由于一些堆栈保护措施的存在，目前并无证据能表明该漏洞能触发远程命令执行，因此OpenSSL官方随后将该漏洞的级别调整为 **高** 。

## 0x2 基础知识

### 国际化域名

英语：Internationalized Domain Name，缩写：IDN）又称 **特殊字符域名**
是指部分或完全使用特殊的文字或非拉丁字母组成的互联网域名，包括中文、俄语、韩语等使用非拉丁字母的语言，这些文字经Unicode编译而成。在域名系统中，国际化域名使用Punycode转写并以ANSII字符串储存。

### Punycode

 **国际化域名编码** （Punycode）：是一种表示Unicode码和ASCII码的有限的字符集。例如中文“上海”会被编码为“fhqz97e”。

Punycode的目的是在于国际化域名标签（IDNA）的框架中，使这些（多语言）的域名可以编码为ASCII(一句话概括就是将Unicode编码转换为ASCII编码)。编码语法在文档
[RFC 3492](https://tools.ietf.org/html/rfc3492)中规定。

### 认证方式

SSL有两种认证方式：单项认证和双向认证

#### 单向认证

只需要验证SSL服务器身份(客户端校验服务端证书)，不需要验证SSL客户端身份。

![image.png](https://image.3001.net/images/20221108/1667900496_636a2450effa683d85195.png!small)  
图片参考：https://www.cnblogs.com/Anker/p/6018032.html

#### 双向认证

双向认证：要求服务器和客户端双方都有证书，客户端需要校验服务端证书，服务端也需要校验客户端证书。

![image.png](https://image.3001.net/images/20221108/1667900488_636a244839e01b1e51cb1.png!small)  
图片参考：https://www.cnblogs.com/Anker/p/6018032.html

 **由于证书有两种认证方式，那么触发漏洞的证书既可以存在服务端也可以存在客户端**

### 名称约束

在根证书中进行定义，在校验证书时根证书会根据 **nameConstraints**
字段中的限制，去校验待校验证书是否符合要求。参考http://www.pkiglobe.org/name_constraints.html

### Openssl 3.0.6版本下载

    
    
    https://github.com/openssl/openssl/releases/tag/openssl-3.0.6
    

## 0x3 漏洞产生原因

查看 **ossl_punycode_decode** 函数的调用链，可以得到其调用链如下所示：

    
    
    NAME_CONSTRAINTS_check->nc_match->nc_match_single->nc_email_eai->ossl_a2ulabel->ossl_punycode_decode
    

#### 触发条件一：

从 **nc_match_single** 函数注释中可以看出要求 **subjectAltName** 指定 **otherName** 一个
**SmtpUTF8** 电子邮件地址。

![image.png](https://image.3001.net/images/20221108/1667900524_636a246ceffecdf2efd6b.png!small)

#### 触发条件二：

从 **ossl_a2ulabel** 函数可以获得第二个条件 ：必须有 **punycode** 编码的域名，另外值得关注的是
**ossl_a2ulabel** 函数中创建了数组 **buf** ，并设置其长度为 **512*4 byte**

![image.png](https://image.3001.net/images/20221108/1667900536_636a24787530758fbd651.png!small)

对漏洞触发函数 **ossl_punycode_decode** 进行简化，假设写入长度为513
但是buffer长度为512，当written_out为512时(从零开始增长)实际已经在buffer中写入了513个字符，因此触发了缓冲区溢出，又因为unsigned
int占据4 byte ，所以最多可以溢出 **4 byte** 数据

    
    
    int ossl_punycode_decode(const char *pEncoded, const size_t enc_len,
                             unsigned int *pDecoded, unsigned int *pout_length)
    {
    			......
        unsigned int max_out = *pout_length;  //max_out初始值为存放解码后的buffer大小
    
    			......
    
            if (written_out > max_out)   //漏洞存在点
                return 0;
    			......
    
        *pout_length = written_out;
        return 1;
    }
    

在实际的分析过程中发现由于溢出的数据过于小且默认编译出的openssl添加了很多保护措施，再加上生成Payload的过程中需要一个合法CA的配合，因此想要造成RCE目前来看是一件不太可能的事情。在默认编译下，Windows可以触发openssl崩溃但是Linux则未触发，后续将对此现象进行探究。

### Windows拒绝服务攻击原理分析：

由于Windows上默认添加了GS的保护，且溢出时的值覆盖了cookie，所以后续的cookie检查不通过，导致程序退出，进而造成拒绝服务攻击。

写入cookie的地址为0x000000B4B52FF600，写入的cookie值为: 0x0000CCA0F214C542

![image.png](https://image.3001.net/images/20221108/1667900554_636a248a37146498d7de1.png!small)

当溢出发生时，溢出值对cookie进行了覆盖，造成了后续的cookie校验不通过，程序退出。

![image.png](https://image.3001.net/images/20221108/1667900562_636a2492cb55bbd43f0d1.png!small)

![image.png](https://image.3001.net/images/20221108/1667900569_636a24991688be2311d95.png!small)

![image.png](https://image.3001.net/images/20221108/1667900577_636a24a13d2e7a417d822.png!small)

### Linux未造成拒绝服务攻击原理分析

在 **ossl_a2ulabel** 函数的反汇编中可以明显地看到为了存储 **ossl_a2ulabel**
函数的局部变量，堆栈升高了0x838，而cookie被存储在了rsp+0x828的地址处(cookie存放的地址:0x7fffffffd4c8)

![image.png](https://image.3001.net/images/20221108/1667900583_636a24a7c50ae53cab8ec.png!small)

![image.png](https://image.3001.net/images/20221108/1667900593_636a24b146097def668bb.png!small)

在缓冲区溢出时，可以看到溢出位置并没有溢出到0x7fffffffd4c8，也就未对cookie进行修改。

![image.png](https://image.3001.net/images/20221108/1667900603_636a24bb45c8b249edabb.png!small)

由于cookie并未发生改变，所以在后续的检查中并未触发程序崩溃。继续向下探寻，既然程序发生了溢出且并没有覆盖cookie，那么必然覆盖了
**ossl_a2ulabel** 函数中的局部变量，使用`info locals`命令查看当前函数的局部变量。

![image.png](https://image.3001.net/images/20221108/1667900612_636a24c449392af2c6274.png!small)

从上图中可以看到当前gdb识别的局部变量并未被进行覆盖，查看源码后可以看到当前函数中只有seed变量还未创建。

![image.png](https://image.3001.net/images/20221108/1667900619_636a24cb7c8770526e156.png!small)

继续向下执行发现栈溢出覆盖的变量确实为seed，而seed在 **ossl_punycode_decode**
函数执行完成后才会进行初始化，因此ossl_punycode_decode函数造成的栈溢出不影响后续程序的正常运行，也就未触发openssl崩溃。

![image.png](https://image.3001.net/images/20221108/1667900626_636a24d297ee062b63fb9.png!small)

![image.png](https://image.3001.net/images/20221108/1667900632_636a24d898777921fd9cf.png!small)

## 0x4 修补建议

将OpenSSL版本在 3.0.0 到 3.0.6 的升级为 3.0.7版本。

## 0x5 参考

https://www.openssl.org/news/secadv/20221101.txt  
https://securitylabs.datadoghq.com/articles/openssl-november-1-vulnerabilities/#exploitation-technical-details  
https://github.com/colmmacc/CVE-2022-3602/tree/e632801ebf64e080aa175041946a1fbcc05415f5  
https://www.cnblogs.com/Anker/p/6018032.html  
http://www.pkiglobe.org/name_constraints.html

