***本文作者：liang亮，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

 **数字签名，就是只有信息的发送者才能产生的别人无法伪造的一段数字串，这段数字串同时也是对信息的发送者发送信息真实性的一个有效证明。
不清楚的请自行科普[数字签名](https://baike.baidu.com/item/%E6%95%B0%E5%AD%97%E7%AD%BE%E5%90%8D)。本篇主要来讲签名值具体是怎么计算出来的~**

## 一、动手解密签名值

### 1、测试密钥

    
    
    //随机产生RSA私钥。因1024位的RSA密钥已不安全，本次测试使用2048长度的RSA密钥。
    > openssl genrsa  2048
    Generating RSA private key, 2048 bit long modulus
    .....................+++
    ............................................................................................................................+++
    e is 65537 (0x10001)
    -----BEGIN RSA PRIVATE KEY-----    MIIEowIBAAKCAQEAqmk7bbqdfdDWgQZ/srfpBurN40Rw8QqBjoE8cujbF8zHrNJc
    RlhHVRQ9HRwHAkG0xM5OzZjfzxHseJ+D3v84xEwHrd5l0t/iMVZxIOoyHk0gHDKv
    kFAaSk+Rlo61bqxgjcRTNkz9mpA8hmG55fYsl1ktJ05YA4rHSv33Dp5OsPGIlO+H
    RZRjdsu8iYfFUrPmfjoVZKPhiRHEeYtDxfyu3rUOlfdkLQyFmlrVJAMdatpM2paz
    eSY3ypqR0mClQ3+t4GpGrCjXqkFYOXP/02YpDKrO04zHtOxZNnZz7r3YedCgzG4Z
    uBvZGin3ig/X2fxZLJmmERhv9FizGvM541kA7wIDAQABAoIBACS/FGWQ/C0JP3gL
    IrYzGji3oTYEqCYSEeXc0GAm/jefnN8TbXptxtP9zT/dr1U5PfXCVxPWh0xrnQZV
    v2Xyuxb5Hh7L+kECrg/dh/+FANGv5+CsvVbtLv4fMlG47D61RQzM7PSknXsa5zJD
    GIcSEoOAY1A6gJgi8N6m7QNl96oH0TiTbs4xIo8wTgwPR2fkXFB/XySqweOZBeNW
    W6cGFb382lM2N51G72ElQe27+O214J/bHKDukoGgJ5GE2uI2r0xkIXYLsy+zeOdG
    gi1UEqjLng596wvH55hog+4b2aPQP2yxnzvtzQELb6XY/oApgQQd5HH5JpWa8ec3
    YJBmp0ECgYEA2Y9YyGp6zsRRTKFuqt1ISQltlFg6pxSAGJYbUPcLD2x67hXdfnhB
    s1fvNvG+hYh65e80/HZca8JKTB4ETU0oOPQfzoGRqa5pIxv37QIruskyu2Skevlo
    CMAT7EXO1CT5ewce1We1R3vUVIlBI3/JibsI89VyBlyDK2QnUKltBtkCgYEAyIVA
    PWnYt0EsA22LdFLcgOQ/W/LMYRssaxpbde9yXqp7MKhhAGFq33IWWYXaGhBVbslC
    Co5cLPrcPiNvB+lFPfFfmBTncU9FGnkDCiAGCufWuqHGSc2mmVnn/pdUdwqI+jSW
    tqCYQl5YO5R39sbjTPyilWWAuS0lUS9rLm3juQcCgYEAr6p8II9Bi/SeRIbQqew0
    sqyHK1G2QjReXfvOIKjo6FJKTDWhe720JxBome/GS2HxAfoMyZD0fRoLDbzq8lPL
    l3keuYqLR/wI7o1luZyYHKDacs8HtDfv1ajqLUwMfeVBACK2tc+gYxDMWFnfG7/R
    xoEb8G43PIW0b/PVft7eprkCgYAZK/kTfI0S/CBtUbwW3ywFFiIKBeG4MvQRgd6H
    YIan8ZjDU+/RX2lOIYFCvbXSXciLvsIGlzZlAxzQxBv1D0h87ScF7WHcbIoNN7G0
    /K4lglMHXLWKoEFQsOOZpx+YTf9CAYYF6QUUF8nVuN6SYQc5q+ExBevx0wQDPAOl
    cXAL0wKBgENcM4Gc0yAn8dRP803/I90s9zgHapKTjDCw6o3q331VNq90orWQj4hp
    bj2BovL6jH2OatpMEv3lLxHXT+pfG9VMGXV79h6AGo5VrLBAMPzAua1xr3nZTWiB
    EQd+4FF41ku94XsCbOwEdNgxtIw33m7OZmgYzajSPILvvI35DNnH
    -----END RSA PRIVATE KEY-----    
    // 通过生成的私钥，得到公钥
    > openssl  rsa -pubout
    -----BEGIN RSA PRIVATE KEY-----    MIIEowIBAAKCAQEAqmk7bbqdfdDWgQZ/srfpBurN40Rw8QqBjoE8cujbF8zHrNJc
    RlhHVRQ9HRwHAkG0xM5OzZjfzxHseJ+D3v84xEwHrd5l0t/iMVZxIOoyHk0gHDKv
    kFAaSk+Rlo61bqxgjcRTNkz9mpA8hmG55fYsl1ktJ05YA4rHSv33Dp5OsPGIlO+H
    RZRjdsu8iYfFUrPmfjoVZKPhiRHEeYtDxfyu3rUOlfdkLQyFmlrVJAMdatpM2paz
    eSY3ypqR0mClQ3+t4GpGrCjXqkFYOXP/02YpDKrO04zHtOxZNnZz7r3YedCgzG4Z
    uBvZGin3ig/X2fxZLJmmERhv9FizGvM541kA7wIDAQABAoIBACS/FGWQ/C0JP3gL
    IrYzGji3oTYEqCYSEeXc0GAm/jefnN8TbXptxtP9zT/dr1U5PfXCVxPWh0xrnQZV
    v2Xyuxb5Hh7L+kECrg/dh/+FANGv5+CsvVbtLv4fMlG47D61RQzM7PSknXsa5zJD
    GIcSEoOAY1A6gJgi8N6m7QNl96oH0TiTbs4xIo8wTgwPR2fkXFB/XySqweOZBeNW
    W6cGFb382lM2N51G72ElQe27+O214J/bHKDukoGgJ5GE2uI2r0xkIXYLsy+zeOdG
    gi1UEqjLng596wvH55hog+4b2aPQP2yxnzvtzQELb6XY/oApgQQd5HH5JpWa8ec3
    YJBmp0ECgYEA2Y9YyGp6zsRRTKFuqt1ISQltlFg6pxSAGJYbUPcLD2x67hXdfnhB
    s1fvNvG+hYh65e80/HZca8JKTB4ETU0oOPQfzoGRqa5pIxv37QIruskyu2Skevlo
    CMAT7EXO1CT5ewce1We1R3vUVIlBI3/JibsI89VyBlyDK2QnUKltBtkCgYEAyIVA
    PWnYt0EsA22LdFLcgOQ/W/LMYRssaxpbde9yXqp7MKhhAGFq33IWWYXaGhBVbslC
    Co5cLPrcPiNvB+lFPfFfmBTncU9FGnkDCiAGCufWuqHGSc2mmVnn/pdUdwqI+jSW
    tqCYQl5YO5R39sbjTPyilWWAuS0lUS9rLm3juQcCgYEAr6p8II9Bi/SeRIbQqew0
    sqyHK1G2QjReXfvOIKjo6FJKTDWhe720JxBome/GS2HxAfoMyZD0fRoLDbzq8lPL
    l3keuYqLR/wI7o1luZyYHKDacs8HtDfv1ajqLUwMfeVBACK2tc+gYxDMWFnfG7/R
    xoEb8G43PIW0b/PVft7eprkCgYAZK/kTfI0S/CBtUbwW3ywFFiIKBeG4MvQRgd6H
    YIan8ZjDU+/RX2lOIYFCvbXSXciLvsIGlzZlAxzQxBv1D0h87ScF7WHcbIoNN7G0
    /K4lglMHXLWKoEFQsOOZpx+YTf9CAYYF6QUUF8nVuN6SYQc5q+ExBevx0wQDPAOl
    cXAL0wKBgENcM4Gc0yAn8dRP803/I90s9zgHapKTjDCw6o3q331VNq90orWQj4hp
    bj2BovL6jH2OatpMEv3lLxHXT+pfG9VMGXV79h6AGo5VrLBAMPzAua1xr3nZTWiB
    EQd+4FF41ku94XsCbOwEdNgxtIw33m7OZmgYzajSPILvvI35DNnH
    -----END RSA PRIVATE KEY-----    writing RSA key
    -----BEGIN PUBLIC KEY-----    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqmk7bbqdfdDWgQZ/srfp
    BurN40Rw8QqBjoE8cujbF8zHrNJcRlhHVRQ9HRwHAkG0xM5OzZjfzxHseJ+D3v84
    xEwHrd5l0t/iMVZxIOoyHk0gHDKvkFAaSk+Rlo61bqxgjcRTNkz9mpA8hmG55fYs
    l1ktJ05YA4rHSv33Dp5OsPGIlO+HRZRjdsu8iYfFUrPmfjoVZKPhiRHEeYtDxfyu
    3rUOlfdkLQyFmlrVJAMdatpM2pazeSY3ypqR0mClQ3+t4GpGrCjXqkFYOXP/02Yp
    DKrO04zHtOxZNnZz7r3YedCgzG4ZuBvZGin3ig/X2fxZLJmmERhv9FizGvM541kA
    7wIDAQAB
    -----END PUBLIC KEY-----    

### 2、编写代码解密  

众所周知：

> RSA加密解密：私钥解密，公钥加密。

> RSA数字签名-俗称加签验签：私钥加签，公钥验签。

其实：

> 也是有私钥加密，公钥解密的。只是因为公钥是公开的，私钥加密后所有人都可以解密，没有意义，所以常用签名，而不是加密。

> 私钥加签的本质也是私钥加密数据的Hash值。

这里有个小技巧：我们用公钥对签名值解密，使用RSA_NO_PADDING，这样就能得到 签名时私钥加密的数据。

鉴于篇幅长度，代码只贴出关键部分。

代码之PHP：

    
    
    /**
         * 创建签名
         * @param string $data 数据
         * @return null|string
         */
        public function createSign($data = '')
        {
            if (!is_string($data)) {
                return null;
            }
            openssl_sign($data, $sign, self::getPrivateKey(),OPENSSL_ALGO_SHA256);
            return  $sign;
        }
    
        /**
         * 公钥解密数据
         * @param string $data 数据
         * @return null|string
         */
        public function decData($data = '')
        {
            if (!is_string($data)) {
                return null;
            }
            openssl_public_decrypt($data, $encData, self::getPublicKey(),OPENSSL_NO_PADDING);
            return  $encData;
        }
    
        /**
         * 公钥解密数据
         * @param string $data 数据
         * @return null|string
         */
        public function decDataPKCS1Padding($data = '')
        {
            if (!is_string($data)) {
                return null;
            }
            openssl_public_decrypt($data, $encData, self::getPublicKey(),OPENSSL_PKCS1_PADDING);
            return  $encData;
        }  
    

其他语言代码整理ing...

本次测试 java、js、C#、PHP。结果均一致，如下：

    
    
    使用示例私钥进行签名，得到如下结果
    签名值Base64： UjV/9zDoYcXTKKKDlWhFshQ08ikknKWqhCig8J7VhVrFCF+tFUQ85xnCUA0KR/t9CVFcf7SDA6ntr/T2xJ4T9TiAHEmNIhghZTlOsp+ieyvB5N4jQ6fuK6DjdtK/icklK5fmMozbKKiHwjr33lWY8NTfXydtKgd/5fPIVhUB26TyOKiO7JY3iAlylqfIpEy4g3fsxiiPGe022jIt400re1UCyZWbhXqdr2JUE7hAZEcMcbxvZff4Ilh6hHZ9rAkWBU1E2vsQUnnvdDK3BOQpZQvTtfIHbX+lhT5UcsFJrwOuONo0nG0s7MSjCsjQEf7iucEZpZeUYwOeMexVHsU9rw==
    签名值Hex： 52357ff730e861c5d328a283956845b21434f229249ca5aa8428a0f09ed5855ac5085fad15443ce719c2500d0a47fb7d09515c7fb48303a9edaff4f6c49e13f538801c498d22182165394eb29fa27b2bc1e4de2343a7ee2ba0e376d2bf89c9252b97e6328cdb28a887c23af7de5598f0d4df5f276d2a077fe5f3c8561501dba4f238a88eec963788097296a7c8a44cb88377ecc6288f19ed36da322de34d2b7b5502c9959b857a9daf625413b84064470c71bc6f65f7f822587a84767dac0916054d44dafb105279ef7432b704e429650bd3b5f2076d7fa5853e5472c149af03ae38da349c6d2cecc4a30ac8d011fee2b9c119a5979463039e31ec551ec53daf
    
    使用示例公钥进行NOPADDING解密，得到如下结果
    原数据Base64： AAH/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////ADAxMA0GCWCGSAFlAwQCAQUABCC5TSe5k00+CKUuUtfafav6xITv43pTgO6QiPes4u/N6Q==
    原数据Hex： 0001ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff003031300d060960864801650304020105000420b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
    
    使用示例公钥进行PKCS1_PADDING解密，得到如下结果
    原数据Base64： MDEwDQYJYIZIAWUDBAIBBQAEILlNJ7mTTT4IpS5S19p9q/rEhO/jelOA7pCI96zi783p
    原数据Hex： 3031300d060960864801650304020105000420b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
      
    

**简单分析**

1\. 字符串"hello world"进行sha256运算得到hash：
b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9

2\. 在Hash结果前数据填充：3031300d060960864801650304020105000420

3\. PKCS1 在上一步结果前填充：

    
    
    0001ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff00

## 二、结合资料分析RSA的补位

### 1、签名时，对Hash值的数据填充方式

对hash算法id和hash值进行ASN.1的DER编码。如下：

    
    
          DigestInfo ::= SEQUENCE {
    
              digestAlgorithm AlgorithmIdentifier,
    
              digest OCTET STRING
    
          }

为方便理解，我们使用ASN1dump对示例中的数据做解析：

    
    
    3031300d060960864801650304020105000420b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9

直接上图：

![数据解析](https://image.3001.net/images/20180927/1538032558_5bac83ae4d259.png!small)

可以看到sha256的算法id，2.16.840.1.101.3.4.2.1：

![看到算法ID](https://image.3001.net/images/20180927/1538032579_5bac83c36cca3.png!small)

数据也在其中，另附上部分算法id：

![分算法id](https://image.3001.net/images/20180927/1538032599_5bac83d7cde46.png!small)

另因为各个hash算法id是固定的，计算的结果也是固定的。所以不同的hash算法的填充也是固定的。如下：

    
    
    md2:"3020300c06082a864886f70d020205000410",
    md5:"3020300c06082a864886f70d020505000410",
    sha1:"3021300906052b0e03021a05000414",
    sha224:"302d300d06096086480165030402040500041c",
    sha256:"3031300d060960864801650304020105000420",
    sha384:"3041300d060960864801650304020205000430",
    sha512:"3051300d060960864801650304020305000440",
    ripemd160: "3021300906052b2403020105000414"  
    

### 2、pkcs1padding V1.5的填充模式
参考[rfc2312](https://tools.ietf.org/html/rfc2313#page-9)

以下描述均以十六进制字符串来描述。

pkcs1padding V1.5的填充模式方式如下：

    
    
    EB = 00+BT+PS +00 + D

即：加密块=00+块类型+填充字符+00+数据

1\. 开头00是为了确保块转换为整数的时候 小于模数

2\. BT（Block
Type）：当使用私钥操作，块类型为00或01，公钥操作，块类型为02。块类型为00，数据开头必须不能是00，因为填充的也是00，将无法解析。块类型为01或02，块可以被准确解析，因为不会是00来填充。

3\. PS（Padding String）：k-3-||D|| 个字节组组成，k表示密钥的字节长度, D表示明文数据D的字节长度
。当BT为01时，填充字节值为FF，BT为00时，填充字节值为00，BT为02时填充随机数（非00）。填充长度至少为8个字节

4\. 00,用于分开PS和D

5\. D，数据原文（HEX）

注意：2048位的RSA密钥，加密块长度也必须是2048位，也就是256个字节。所以示例中的加密块需要填充202个FF才够256个字节。

故签名的时候， 加密的块：`00+01+FF（202个） +00 +
">3031300d060960864801650304020105000420b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9`

## 三、测试题

最后抛了两个问题，看看大家有没有理解上面所介绍的内容。

1、RSA签名的时候 值是固定， 公钥加密的结果确实随机的，为什么？

2、分析如下代码，是否有问题？

![RSA解密异常代码](https://image.3001.net/images/20180927/1538032612_5bac83e457fff.png!small)

 ***本文作者：liang亮，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

