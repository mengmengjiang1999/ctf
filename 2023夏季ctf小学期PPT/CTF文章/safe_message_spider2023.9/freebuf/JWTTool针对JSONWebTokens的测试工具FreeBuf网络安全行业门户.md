**众望所归，大家期待已久的JWT渗透测试工具终于出炉啦！没错，今天给大家介绍的这款名叫JWT Tool的工具，就可以针对JSON Web
Tokens进行渗透测试。**

![aaaaaaaaaaaaaaaaaaa.jpg](https://image.3001.net/images/20190703/1562142582_5d1c677682b3c.jpg!small)

## 什么是JWT？

JWT是JSON Web
Token的缩写，它是一串带有声明信息的字符串，由服务端使用加密算法对信息签名，以保证其完整性和不可伪造性。Token里可以包含所有必要的信息，这样服务端就无需保存任何关于用户或会话的信息了。JWT可用于身份认证，会话状态维持以及信息交换等任务。

JWT由三部分构成，分别称为header，payload和signature，各部分用“.”相连构成一个完整的Token，形如xxxxx.yyyyy.zzzzz。

### Header

使用一个JSON格式字符串声明令牌的类型和签名用的算法等，形如{"alg":"HS256", "typ":
"JWT"}。该字符串经过Base64Url编码后形成JWT的第一部分xxxxx。

Base64Url编码可以用这段代码直观理解：

    
    
    from base64 import *
    
    def base64URLen(s):
    
        t0=b64encode(s)
    
       t1=t0.strip('=').replace('+','-').replace('/','_')
    
        return t1
    
    ​
    
    def base64URLde(s):
    
        t0=s.replace('-','+').replace('_','/')
    
        t1=t0+'='*(4-len(t0)%4)%4
    
        return b64decode(t1)

### Payload

使用一个JSON格式字符串描述所要声明的信息，分为registered，public，状语从句：private三类，形如{"name": "John
Doe", "admin": true}，具体信息可参考RFC7519的JWT要求部分。

同样的，该字符串经过Base64Url编码形成JWT的第二部分yyyyy。

### Signature

将xxxxx.yyyyy使用alg指定的算法加密，然后再Base64Url编码得到JWT的第三部分zzzzz。所支持的算法类型取决于实现，但HS256和none是强制要求实现的。

## JWT Tool

简而言之，Jwt_tool.py这个工具及可以用来验证、伪造和破解JWT令牌。

其功能包括：

> 1、 检测令牌的有效性；
>
> 2、 测试RS/HS256公钥错误匹配漏洞；
>
> 3、 测试alg=None签名绕过漏洞；
>
> 4、 测试密钥/密钥文件的有效性；
>
> 5、 通过高速字典攻击识别弱密钥；
>
> 6、 伪造新的令牌Header和Payload值，并使用密钥创建新的签名；

### 适用范围

该工具专为渗透测试人员设计，可用于检测令牌的安全等级，并检测可能的攻击向量。当然了，广大研究人员也可以用它来对自己使用了JWT的项目进行安全测评以及稳定性测评。

### 工具要求

本工具采用原生Python 2.x开发，使用的都是常用Python库。大家可以在字典攻击选项中配置自定义字典文件。

## 工具安装

大家可以直接下载代码库中的jwt_tool.py文件，或使用下列命令将代码库克隆至本地：

    
    
    git clone https://github.com/ticarpi/jwt_tool.git

## 工具使用

    
    
    $python jwt_tool.py <JWT> (filename)

第一个参数就是JWT本身，后面需要跟一个文件名或文件路径。

 **样例：**

    
    
    $python jwt_tool.pyeyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpbiI6InRpY2FycGkifQ.aqNCvShlNT9jBFTPBpHDbt2gBB1MyHiisSDdp8SQvgw/usr/share/wordlists/rockyou.txt

本工具将会验证令牌的有效性，并输出Header和Payload的值。接下来，它会给用户提供可用的菜单选项。输入值可以为标准JWT格式或url-safe模式的JWT格式。

### 使用提示

大家还可以在Burp Search中使用正则表达式来寻找JWT（请确保开启了“大小写敏感“和“正则表达式”选项）：

    
    
    [=]ey[A-Za-z0-9_-]*\.[A-Za-z0-9._-]* - url-safe JWT version
    
    [=]ey[A-Za-z0-9_\/+-]*\.[A-Za-z0-9._\/+-]* - all JWT versions

## 项目地址

JWT Tool：【[GitHub传送门](https://github.com/ticarpi/jwt_tool)】

## 参考资料

> 1、 <https://jwt.io/introduction/>
>
> 2、 <https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-> libraries/>
>
> 3、 <https://www.ticarpi.com/introducing-jwt-tool/>
>
> 4、 <https://pentesterlab.com/exercises/jwt>
>
> 5、 <https://pentesterlab.com/exercises/jwt_ii>
>
> 6、 <https://pentesterlab.com/exercises/jwt_iii>

***
参考来源：[ticarpi](https://github.com/ticarpi/jwt_tool)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

