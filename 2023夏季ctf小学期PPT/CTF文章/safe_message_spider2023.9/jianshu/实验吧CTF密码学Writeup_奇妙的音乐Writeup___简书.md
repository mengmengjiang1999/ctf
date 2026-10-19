实验吧CTF密码学Writeup-奇妙的音乐Writeup

[ syxvip](https://www.jianshu.com/u/380fd93bae2c)关注赞赏支持

# 实验吧CTF密码学Writeup-奇妙的音乐Writeup

### 奇妙的音乐分值：10

  * 来源： [北邮天枢战队](http://www.shiyanbar.com/user/studentcourse/A569313BDAD62C)
  * 难度：易
  * 参与人数：5493人
  * Get Flag：1506人
  * 答题人数：1774人
  * 解题通过率：85%

据说flag就藏在这段音乐中，请仔细听。

格式：CTF{}

解题链接： <http://ctf5.shiyanbar.com/crypto/123.zip>

* * *

题目中给了一个压缩包，解压出来有一个压缩包（压缩包内有密码），然后还有一张图片，图片下面有盲文，首先对盲文进行解密

附上盲文密码表：

  

image.png

解密后的明文为：kmdonowg

用密码将压缩包解压出来以后。

  

image.png

一听 肯定是摩斯密码，上wave editor 便于观察

  

image.png

    
    
    -.-.  -  ..-.  .--   .--. .   ..  -----   ---..   --...   ...--   ..---  ..--..   ..---   ...--  -..  --..  
    
    

image.png

CTF{WPEI08732?23DZ}

然后提交以后密码错误。。呵呵哒，换下大小写

CTF{wpei08732?23dz}

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [CTF取证类题目指南](https://www.jianshu.com/p/022fb173677d)

文章简介：大致介绍了CTF比赛中Fornesics题目的常见类型和各类使用工具，此类题目在国内CTF中偶尔出现，但...

[看雪学院](https://www.jianshu.com/u/fc7a20500211)阅读 8,258评论 0赞 20

  * [实验吧CTF-隐写术Writeup](https://www.jianshu.com/p/500b96ce956c)

实验吧-隐写术-欢迎来到地狱Writeup 压缩包解压后图片损坏，那么修复，丢进 winhex修复（工具自行goo...

[syxvip](https://www.jianshu.com/u/380fd93bae2c)阅读 12,968评论 0赞 5

  * [《勇敢爱》](https://www.jianshu.com/p/009145ede019)

这篇小说是我在学校没意思写的！明天开始写你们帮我看看 写的好吗？谢谢！

[恩兮阿](https://www.jianshu.com/u/eda96c544cb2)阅读 202评论 1赞 1

 