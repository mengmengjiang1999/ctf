最近一直在学习逻辑漏洞，偶然看到我家小孩学校组织的投票活动，得知老师组织这次投票活动，我专门向老师申请做一次 **逻辑漏洞测试**
，老师说非常欢迎，老师说对我这个玩电脑的家长早有耳闻，于是便有了以下的过程。  
此测试过程必须1、微信登陆下投票 2、token验证jwt加密，解密发现openid等参数

### 1、第一种方法突破微信登录投票

一个微信账号一天投3票之扣别人的票增加自己的余票实现刷票  
首先用微信识别老师发来的投票二维码如图：

![1635406484_617a529461cea978c2371.png!small?1635406486761](https://image.3001.net/images/20211028/1635406484_617a529461cea978c2371.png!small?1635406486761)

使用微信号登陆，不停的放包，直到这里

![1635406795_617a53cb181d96b95a939.png!small?1635406796417](https://image.3001.net/images/20211028/1635406795_617a53cb181d96b95a939.png!small?1635406796417)

修改playerIdwei为别人的，因为用自己的playerid，自己的票数为变为-负数，修改num数为负数，如-9999，因为num参数可控，这时候你的票数会多出9999票，别人会少9999票，打个比方如图：

  

![1635407042_617a54c2bae733cd08a69.png!small?1635407044485](https://image.3001.net/images/20211028/1635407042_617a54c2bae733cd08a69.png!small?1635407044485)

  

这时候你就在你的账号不停歇的点投票就行，直到超过第一名，如图：

  

![1635407269_617a55a5ecd295dac5700.png!small?1635407271385](https://image.3001.net/images/20211028/1635407269_617a55a5ecd295dac5700.png!small?1635407271385)

  

票数瞬间变为1002票，本来一个微信号一天只能投一个选手3票，这时候已经成功突破，秒变1002票。

以上是第一种方法刷票，扣别人的票，加自己的余票，然后再刷给自己… …

### 2、 第二种方法利用long长整型溢出刷票

同样到这个包，如下：

    
    
    POST /vote/api/wx/voteFree/add HTTP/1.1
    Host: 111.cn
    Content-Length: 73
    Accept: application/json, text/javascript, */*; q=0.01
    X-Requested-With: XMLHttpRequest
    User-Agent: Mozilla/5.0 (Linux; Android 10; TEL-AN00a Build/HONORTEL-AN00a; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/045811 Mobile Safari/537.36 MMWEBID/3773 MicroMessenger/8.0.15.2020(0x28000F3D) Process/tools WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64
    token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqd3QtaWQiOiJvWmZMLXZuandCeWY1MU01Zm1CRlpZV0Z0ZFI4Iiwid3hPcGVuSWQiOiJvWmZMLXZuandCeWY1MU01Zm1CRlpZV0Z0ZFI4Iiwibmlja25hbWUiOiJkaWdleHBsb2l0IiwiZXhwIjoxNjM1MzAwNTY2fQ.0VBEVOvfDLfduF9MPto2D8Ok1Y9C90roMBMQzTn9oL0
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    Origin: http://111.cn
    Referer: http://111.cn/welcome/detail.html?activityId=37bd3ad6-38c0-437c-870a-801dc6fed2a7&playerId=139969&skin=default
    Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7
    Cookie: SESSION=MWE3NDU3NWItM2MzMS00YWJmLTkxZTItNmU2MWQ0NzNhZDk5; token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqd3QtaWQiOiJvWmZMLXZuandCeWY1MU01Zm1CRlpZV0Z0ZFI4Iiwid3hPcGVuSWQiOiJvWmZMLXZuandCeWY1MU01Zm1CRlpZV0Z0ZFI4Iiwibmlja25hbWUiOiJkaWdleHBsb2l0IiwiZXhwIjoxNjM1MzAwNTY2fQ.0VBEVOvfDLfduF9MPto2D8Ok1Y9C90roMBMQzTn9oL0; appid=wx6656xxoocd3e6xxoo
    Connection: close
    
    voteActivityId=37bd3ad6-38c0-437c-870a-801dc6fed2a7&playerId=139969#=3

修改num=3333333{},如图：

![1635407556_617a56c4d614afedb6911.png!small?1635407558171](https://image.3001.net/images/20211028/1635407556_617a56c4d614afedb6911.png!small?1635407558171)

  

判断为long长整型，既然num=-333333可控，那我们就把num=-333333改为2的63次方，也就是num=-9223372036854775808，执行完以后，提示500错误，提示超出范围…
…然后微信打开投票二维码就卡半天了，恢复之前如图：

![1635407685_617a57458629774dcd4b2.png!small?1635407688971](https://image.3001.net/images/20211028/1635407685_617a57458629774dcd4b2.png!small?1635407688971)

  

这是之前测试的时候不小心搞成，所以才有了第二种方法。

也就是刷票数为负 -270多万，如上图。

等溢出恢复以后票数变成15W多，排名第一，如图：

![1635407814_617a57c610c847c896db4.png!small?1635407816169](https://image.3001.net/images/20211028/1635407814_617a57c610c847c896db4.png!small?1635407816169)

 **注：由于测试过程没有保存录像或图片，导致溢出以后的返回包没能贴图，不过没关系，正负数都试一遍，一般参**
**数可负数的话，直接负的最大溢出量就够了。**

