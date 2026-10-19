**如何收集一个公司的员工信息，猎头、商业竞对都比较关心。方式上其实有几种，一个是通过招聘网站搜集简历，但国内网站如果要看简历的联系方式则需要收费，这个成本比较高，介绍几个简单方法：**

## 一，LinkedIn

通过LinkedIn可以拿到邮箱，拿到邮箱以后当然可以有其他玩法，比如钓鱼、撞库之类。工具直接可在<https://github.com/DisK0nn3cT/linkedin-gatherer>下载，可以针对某个特定域名，生成Excel，包括姓名，邮箱，职位，照片等信息。也可以只输入名字，定向搜索某人。

工具目前还不够智能，开发者的目标是只需要输入公司名，收集抓取自动进行，并且发个邮件出来，BUT，目前还没达到这个水平。开发者还准备用自然语言处理发现角色和部门类型，实现关系可视化，当然这也还没实现。不过就目前这能力，基本足够用了。

需要注册个linkedin账号并激活，这个账号能够关联三度关系，如果这个账户看不到相关人的话，建议和目标公司的一些关键人成为好友。另外需要一个Hunter.io
API密钥，可以<https://hunter.io>注册一个。

这个比较简单，现成的工具可用，就不多说了。

## 二，国内某互联网从业者常用APP

为了避免引起争议，就不说名字了。只看了IOS版本，注册需要手机号和验证码，然后可以搜索特定公司员工。用Burp观察了下，先搜索了饿了么，请求如下：

    
    
    GET /search/contacts?query=%E9%A5%BF%E4%BA%86%E4%B9%88&dist=3&searchTokens=%5B%22%E9%A5%BF%E4%BA%86%E4%B9%88%22%5D&me=1&highlight=true&frm=webview%23%2Fsearch%2Fcontacts&appid=4&vc=11.2.1&push_permit=1&version=4.18.8&channel=AppStore&net=wifi&jsononly=1&imei=<censor IMEI>&open=icon&density=2&u=<censor user ID>&device=iPhone10%2C4&access_token=<censor access token>&ts=<censor ts>HTTP/1.1
    Host: ****.cn
    Accept: */*
    Cookie: access_token=<censor access token>; channel=AppStore; u=<censor user ID>; version=4.18.8; session=<censor session cookie>; session.sig=<censor session signature>
    User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C153/{iPhone10,4} [iOS 11.2.1]/MaiMai 4.18.8(4.18.8.9)
    Accept-Language: en-GB;q=1, zh-Hant-GB;q=0.9, zh-Hans-GB;q=0.8
    Accept-Encoding: gzip, deflate
    Connection: close  
    

请求输出是JSON格式，不过超过25000条记录就会连接超时。  

POST请求如下所示：

    
    
    POST /xxxx/user/v3/login?account=<censored account phone number>&appid=4&vc=11.2.1&push_permit=1&version=4.18.8&channel=AppStore&net=wifi&imei=<censored IMEI>&open=icon&density=2&u=&device=iPhone10%2C4&access_token= HTTP/1.1
    Host: open.taou.com
    Content-Type: application/x-www-form-urlencoded
    Connection: close
    Accept: */*
    User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C153/{iPhone10,4} [iOS 11.2.1]/MaiMai 4.18.8(4.18.8.9)
    Accept-Language: en-GB;q=1, zh-Hant-GB;q=0.9, zh-Hans-GB;q=0.8
    Accept-Encoding: gzip, deflate
    Content-Length: 128
    account=<censored URL encoded phone number>&appid=4&cnt=1&dev_type=4&dname=<censored device name>&new_fr=1&password=<censored password>&stage=complete_uinfo

可以通过将参数移动到URL中将其更改为GET请求，例如在以下请求中：

    
    
    GET /xxxx/user/v3/login?account=<censored&account=<censored+URL+encoded+phone+number>&appid=4&cnt=1&dev_type=4&dname=<censored+device+name>&new_fr=1&password=<censored+password>&stage=complete_uinfo account
    Host: open.taou.com
    Connection: close
    Accept: */*
    User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C153/{iPhone10,4} [iOS 11.2.1]/xxxx 4.18.8(4.18.8.9)
    Accept-Language: en-GB;q=1, zh-Hant-GB;q=0.9, zh-Hans-GB;q=0.8
    Accept-Encoding: gzip, deflate

响应如下所示：

    
    
    HTTP/1.1 200 OK
    Server: nginx
    Date: Mon, 01 Jan 2018 09:38:33 GMT
    Content-Type: application/json; charset="utf-8"
    Connection: close
    Vary: Accept-Encoding
    Content-Length: 4223
    {"has_weibo": 0, "token": "<censored token>", "has_password": 1, "user": {"meeting_partake_count": 0, 
    <......>
    "education": [], "id": <censored ID>, "ht_city": null, "job_count": 0, "cshow_url": "[http](https://xxxx.cn/show?webuid=TsJ6oBCd&srcu=TsJ6oBCd&profession=0&src=app&ampregfr=cshow&abtype=0&turl=http%3A//taou.cn/d/7lnZp)
    <......>

然后就在github上搜到了一个工具是MaiInt，居然是外国人写的专门针对xx的，看来国外势力凯觎已久啊<https://github.com/vysec/MaiInt>，跑了下效果还不错。早知道先搜GitHub啊，白费功夫了都。

![图片
1.png](https://image.3001.net/images/20180712/15314089054209.png!small)![图片
2.png](https://image.3001.net/images/20180712/15314089143292.png!small)![图片
3.png](https://image.3001.net/images/20180712/1531408919381.png!small)

## 三、Hunter.io

不用那么费事啦，Hunter.io也收集了大量的邮件地址信息，输入ele.me会看到以下内容，还带有每个来源网页，不过有很多看起来都是HR小姐姐。

![图片 4.png](https://image.3001.net/images/20180712/15314089523883.png!small)  

