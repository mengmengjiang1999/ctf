## 1\. 背景

目前大多数IOT设备配置文件都采取加密方式，避免数据明文存储所带来的安全隐患。结合前段时间对不同设备配置文件加解密的分析，对现有不同厂商设备加密方式做一个归纳。

## 2\. 加密方式

厂商主流配置文件加密方式主要有以下几种:

> 异或加密
>
> AES加密
>
> 自定义算法加密

### 2.1 异或加密

某国外品牌路由器配置文件加密方式

![1662521830_631811e6db194214fb4fa.png!small?1662521831094](https://image.3001.net/images/20220907/1662521830_631811e6db194214fb4fa.png!small?1662521831094)

通过设置固定的key来对配置文件内容亦或加密

异或解密

    
    
    def xor(data, key):  
    key_len = len(key)  
    data_len = len(data)  
    key= data_len//key_len*key+key[:data_len%key_len]  
    return bytearray(a^b for a, b in zip(*map(bytearray, [data, key])))  
    ​  
    if __name__ == "__main__":  
    with open("cfg122.bin","rb")as f:  
    data = f.read()  
      
    key = b'\xAB\xCD\x88v'#key  
    res = xor(data,key)  
    ​  
    with open("cfg.txt",'wb')as f:  
    f.write(res)  
    ​

### 2.2 AES加密

某硕路由器配置文件加密方式

![1662521845_631811f51b8950b87fe36.png!small?1662521845963](https://image.3001.net/images/20220907/1662521845_631811f51b8950b87fe36.png!small?1662521845963)

![1662521854_631811fe7cb8c451608f5.png!small?1662521855100](https://image.3001.net/images/20220907/1662521854_631811fe7cb8c451608f5.png!small?1662521855100)

加密流程

> 获取加密密钥
>
> base64解码
>
> 利用获取到的key，aes解密

获取解密结果。

![1662521864_631812082f970b9c8f939.png!small?1662521873567](https://image.3001.net/images/20220907/1662521864_631812082f970b9c8f939.png!small?1662521873567)

### 2.3 自定义算法

某科设备配置文件加密方式。

![1662521875_631812133d917cffbd7f8.png!small?1662521875583](https://image.3001.net/images/20220907/1662521875_631812133d917cffbd7f8.png!small?1662521875583)

文件内容采用与、或运算最终达到配置文件加密。

获取解密结果。

![1662521890_6318122280ec917c61205.png!small?1662521891693](https://image.3001.net/images/20220907/1662521890_6318122280ec917c61205.png!small?1662521891693)

## 3\. 总结

不同厂商、不同设备采用的配置文件加密都是互不相同的。如果攻击者轻松获取到用户配置文件，那对于用户而言是非常危险的，攻击者可以轻松获取用户凭据获取设备权限。

