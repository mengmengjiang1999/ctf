> ### 高端的漏洞，往往只需要最朴素的挖洞方式，忙碌了两个小时的陈师傅，终于找到了 “晏皮”。

### 涉及到漏洞的保密，具体url和信息不提供嗷

![1606787557_5fc5a1e5ec61ece0ea05b.png!small](https://image.3001.net/images/20201201/1606787557_5fc5a1e5ec61ece0ea05b.png!small)

> 这次的目标相当的不简单，先整点有用的信息

![1606789103_5fc5a7efaeb3770de7711.png!small?1606789104441](https://image.3001.net/images/20201201/1606789103_5fc5a7efaeb3770de7711.png!small?1606789104441)

![1606789121_5fc5a801aabbffded64bd.png!small?1606789123397](https://image.3001.net/images/20201201/1606789121_5fc5a801aabbffded64bd.png!small?1606789123397)

> 开始觉得还挺正常的，而且没检测到waf，不知道会不会有sql注入的机会

![1606789180_5fc5a83c768534b2d6ce4.png!small?1606789181423](https://image.3001.net/images/20201201/1606789180_5fc5a83c768534b2d6ce4.png!small?1606789181423)

![1606789301_5fc5a8b5d1ffc1e24d139.png!small?1606789302648](https://image.3001.net/images/20201201/1606789301_5fc5a8b5d1ffc1e24d139.png!small?1606789302648)

c段信息就先不看了，太多了。。。

> 打开网站先看看有无注入点 //要挂个代理，开始 and 1=1，1=2；

网站大意了，但是有闪，闪了两下，没有回应我，我裂开。

> 我恼羞成怒给了他一个 "御剑"打击，顺手整个admin.php

![1606828585_5fc64229182f03d737e10.png!small?1606828585121](https://image.3001.net/images/20201201/1606828585_5fc64229182f03d737e10.png!small?1606828585121)

> 然后发现一个破绽，。。。叶师傅直接切他中路。。/admin 会直接爆目录

![1606828719_5fc642af416aafa5c9f21.png!small?1606828720295](https://image.3001.net/images/20201201/1606828719_5fc642af416aafa5c9f21.png!small?1606828720295)

> 看来“乱拳打倒老师傅”

![1606828940_5fc6438c7f04254a6ff4a.png!small?1606828940605](https://image.3001.net/images/20201201/1606828940_5fc6438c7f04254a6ff4a.png!small?1606828940605)

> 弱口令尝试失败 //其实我试了好几次
>
> 随身带的万能密码试试“锁”

![1606828847_5fc6432fb1b4977f9afc4.png!small?1606828847888](https://image.3001.net/images/20201201/1606828847_5fc6432fb1b4977f9afc4.png!small?1606828847888)

> 起飞--
![1606829039_5fc643efb7cff687207f9.png!small?1606829039766](https://image.3001.net/images/20201201/1606829039_5fc643efb7cff687207f9.png!small?1606829039766)

![1606829135_5fc6444f9c445f38de608.png!small?1606829135830](https://image.3001.net/images/20201201/1606829135_5fc6444f9c445f38de608.png!small?1606829135830)

> 到这里基本可以尝试拿shell了，开冲！
>
> 找了下文件上传地方，三好青年不能乱搞网站，悄悄的搞，打qiang的不要！

![1606829261_5fc644cda73235f0fc117.png!small?1606829261742](https://image.3001.net/images/20201201/1606829261_5fc644cda73235f0fc117.png!small?1606829261742)

> 抓包上传一句话木马成功，直接修改图片后缀即可（这里后台会修改上传的代码，用C32插入一句话）

![1606829622_5fc64636c2a8032e635ff.png!small?1606829624672](https://image.3001.net/images/20201201/1606829622_5fc64636c2a8032e635ff.png!small?1606829624672)

![1606829622_5fc646363ab36cebef2f0.png!small?1606829624673](https://image.3001.net/images/20201201/1606829622_5fc646363ab36cebef2f0.png!small?1606829624673)

> 上菜刀，可能有的人觉得已经成功了，hh （图片记得要下载查看下插入的一句话有没有被删）

![1606829656_5fc6465824a4d1c91e88f.png!small?1606829656229](https://image.3001.net/images/20201201/1606829656_5fc6465824a4d1c91e88f.png!small?1606829656229)

![1606829739_5fc646ab931325f087f39.png!small?1606829739763](https://image.3001.net/images/20201201/1606829739_5fc646ab931325f087f39.png!small?1606829739763)

> 失败了，可能是不允许外部，新手的第一次拿服务器失败了，喝瓶康帅傅直接裂开
>
> 那就看看下路有没有机会吧

![1606830359_5fc64917151a531cc85d1.png!small?1606830359305](https://image.3001.net/images/20201201/1606830359_5fc64917151a531cc85d1.png!small?1606830359305)

> 兄弟们该结婚了嗷~，不过我还是单身狗，看一看，顺便送个祝福

![1606830522_5fc649baf22ab1bb66df9.png!small?1606830525036](https://image.3001.net/images/20201201/1606830522_5fc649baf22ab1bb66df9.png!small?1606830525036)

> 恭喜的同时发现了注入点，奥里给！
>
>  
>

![1606830717_5fc64a7d797a54506e844.png!small?1606830717578](https://image.3001.net/images/20201201/1606830717_5fc64a7d797a54506e844.png!small?1606830717578)

![1606830793_5fc64ac9c5effc8fb54ec.png!small?1606830794862](https://image.3001.net/images/20201201/1606830793_5fc64ac9c5effc8fb54ec.png!small?1606830794862)

> 想绕过的往后放一放，这是正则匹配，但是bool注入看看能不能行

![1606831039_5fc64bbf0745148e48f61.png!small?1606831039232](https://image.3001.net/images/20201201/1606831039_5fc64bbf0745148e48f61.png!small?1606831039232)

> ascii() ,substr()等函数都没有报错，兄弟们冲, and ascii(substr(database(),1,1))=113 --+
> 测出来字母q

![1606832077_5fc64fcddec675df71590.png!small?1606832079547](https://image.3001.net/images/20201201/1606832077_5fc64fcddec675df71590.png!small?1606832079547)

> bool注入太慢了，sqlmap一跑vpn就要被封掉，我裂开, 数据库测出来是qywdnr

但是当我继续往下进行的时候发现 information这个单词被过滤了，， from也是

> 待我尝试了/**/，/*!*/,+,url,base64编码，unicode编码后我直接选择自闭。双重伤害。

好吧，xss漏洞

![1606834281_5fc658698c42f9fba61bc.png!small?1606834282663](https://image.3001.net/images/20201201/1606834281_5fc658698c42f9fba61bc.png!small?1606834282663)

> 这算是个低危漏洞了，提交一个构造的html，可以触发xss
>
>
> ![1606834588_5fc6599ca15cfb0cd770d.png!small?1606834588589](https://image.3001.net/images/20201201/1606834588_5fc6599ca15cfb0cd770d.png!small?1606834588589)

![1606834514_5fc65952b282d899de85c.png!small?1606834514694](https://image.3001.net/images/20201201/1606834514_5fc65952b282d899de85c.png!small?1606834514694)

> 完结，感觉裂开，网站看似漏洞百出，可是我这个菜鸡竟然没有达到预期的目标，还要继续努力成为一个牛批的白帽子。一起加油，兄弟们。

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

