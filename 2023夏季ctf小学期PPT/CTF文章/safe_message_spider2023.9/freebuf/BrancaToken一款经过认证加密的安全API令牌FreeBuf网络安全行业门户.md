**今天给大家介绍的是一款名叫Branca的加密令牌，Branca使用了现代密码学算法来对API令牌进行认证和加密，并可用于多种在线服务之中。**

![Branca
Token：一款经过认证加密的安全API令牌](https://image.3001.net/images/20180319/15214634149343.png!small)  

## 工具介绍

Branca是一种易于使用的令牌格式，并且它的易于使用并不是以牺牲安全性换取来的。它使用了IETF XChaCha20-Poly1305
AEAD对称加密算法来生成防篡改的加密令牌，Payload本身是任意字节序列，你可以使用JSON对象、明文字符串或任意序列化二进制数据。

### 设计目标

> 1\. 安全第一；
>
> 2\. 易于实现和使用；
>
> 3\. 更小的令牌体积；

## 令牌格式

Branca令牌由header、密文（Cyphertext）和一个认证标识（Tag）组成，其中header由版本信息（Version）、时间戳（Timestamp）和随机数（Nonce）组成。将这些信息组合在一起之后，我们得到了下列数据结构：

    
    
    Version(1B) || Timestamp (4B) || Nonce (24B) || Ciphertext (*B) || Tag (16B)

代表上述二进制令牌的字符串必须使用base62编码，可选的字符集如下：

    
    
    0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy

### 版本信息（Version）

版本信息长度为8位，当前的版本信息为0xBA，你可以用它来识别已有的令牌，版本信息可以用来确定令牌格式和加密算法。

### 时间戳（Timestamp）

时间戳为32位，它是无符号的大端4字节UNIX时间戳。时间戳可以帮助验证方判断令牌的生成时间以确定其当前是否仍然有效。除此之外，以无符号整形存储时间戳可以帮助我们避免2038年问题，因为研究人员预测到2106年才会出现无符号整形溢出的问题。

### 随机数（Nonce）

随机数长度为192位，随机数必须是经过安全加密的随机字节，并且不会在令牌间重复使用。

### 密文（Cyphertext）

Payload使用[IETFXChaCha20-Poly1305](https://download.libsodium.org/doc/secret-key_cryptography/xchacha20-poly1305_construction.html)来进行加密和认证，但header中的数据（版本信息（Version）、时间戳（Timestamp）和随机数（Nonce））并没有进行加密（只需要认证），因为在某些人眼里，header只能被查看到，却不能被篡改…

### 认证标识（Tag）

认证Tag为128位，它是一种[Poly1305](https://en.wikipedia.org/wiki/Poly1305)消息认证码，可以用来确保Payload以及其他未加密Header不被篡改。

## 令牌使用

我们假设你的密码库支持组合模式，在组合模式下，认证标识Tag以及加密消息需要存储在一起。如果你的密码库不支持组合模式，tag就是ciphertext|tag组合的最后16字节数据。

### 生成令牌

一个256位的密钥key加上任意Payload，我们就可以按照下列步骤生成令牌：

> 1\. 生成安全加密随机数。
>
> 2\. 如果用户没有提供时间戳，则使用当前的unixtime。
>
> 3\. 通过组合version、timestamp和nonce来构造header。
>
> 4\. 使用IETF XChaCha20-Poly1305 AEAD以及用户提供的密钥来对Payload进行加密。
>
> 5\. 使用Base62对整个令牌进行编码。

### 验证令牌

用户可以按照下列步骤恢复原始的未加密Payload：

> 1\. 使用Base62对令牌进行解码。
>
> 2\. 确保解码后的令牌第一个字节为0xBA。
>
> 3\. 提取header。
>
> 4\. 提取nonce。
>
> 5\. 提取timestamp。
>
> 6\. 提取ciphertext|tag组合。
>
> 7\. 使用IETF XChaCha20-Poly1305 AEAD解密并验证ciphertext|tag组合。

## 代码库

当前已实现Branca令牌的项目如下：

**编程语言** **** |  **许可证协议** **** |  **使用的加密代码库** ****  
---|---|---  
[Elixir](https://github.com/tuupola/branca-elixir) |  MIT |
[ArteMisc/libsalty](https://github.com/ArteMisc/libsalty)  
[Go](https://github.com/hako/branca) |  MIT |  [GoKillers/libsodium-go](https://github.com/GoKillers/libsodium-go)  
[JavaScript](https://github.com/tuupola/branca-js) |  MIT |
[jedisct1/libsodium.js](https://github.com/jedisct1/libsodium.js)  
[PHP](https://github.com/tuupola/branca-php) |  MIT |
[paragonie/sodium_compat](https://github.com/paragonie/sodium_compat)  
[Python](https://github.com/tuupola/branca-python) |  MIT |
[jedisct1/libsodium](https://github.com/jedisct1/libsodium)  
  
### 许可证协议

本项目遵循MIT许可证协议。【[许可证文件](https://github.com/tuupola/branca-spec/blob/master/LICENSE.md)】

 *** 参考来源：[branca](https://github.com/tuupola/branca-spec/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

