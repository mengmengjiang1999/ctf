实验吧CTF密码学Writeup-古典密码Writeup

[ syxvip](https://www.jianshu.com/u/380fd93bae2c)关注赞赏支持

# 实验吧CTF密码学Writeup-古典密码Writeup

### 古典密码分值：10

  * 来源： [北邮天枢战队](http://www.shiyanbar.com/user/studentcourse/A569313BDAD62C)
  * 难度：易
  * 参与人数：6803人
  * Get Flag：2507人
  * 答题人数：2791人
  * 解题通过率：90%

密文内容如下{79 67 85 123 67 70 84 69 76 88 79 85 89 68 69 67 84 78 71 65 72 79 72
82 78 70 73 69 78 77 125 73 79 84 65}

请对其进行解密

提示：1.加解密方法就在谜面中

    
    
         2.利用key值的固定结构
    

格式：CTF{ }

* * *

密文全是数字，ascll码转为字符串。

  

image.png

OCU{CFTELXOUYDECTNGAHOHRNFIENM}IOTA

既然是古典密码，并且利用key值的固定结构，上述共有 35 个 所以分为 5*7  
OCU{CFT  
ELXOUYD  
ECTNGAH  
OHRNFIE  
NM}IOTA

固定的格式为:格式：CTF{ }

所以，第一列为C 是2列或者第5列 ，第二列为T 第三列为F 第三列为F 最后列为 }

image.png

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [密码学](https://www.jianshu.com/p/a671ce609df1)

小case 嘿嘿，别看错，也别想错哦。要不然就XX了 解题链接 nick:1003:8EA9109FDA91D6B...

[Octantis](https://www.jianshu.com/u/168a113df9a4)阅读 3,385评论 0赞 3

  * [CTF密码学作业题笔记](https://www.jianshu.com/p/5e39a4d2d469)

1.奇怪的字符串 密文：89 51 82 109 89 50 86 122 97 71 107 61对应的asci...

[Beant](https://www.jianshu.com/u/5a41943caa83)阅读 4,140评论 0赞 4

  * [Sklearn randomforest与bagging算法使用](https://www.jianshu.com/p/e8ee294c7612)

bagging与randomforest是集成学习中的两个比较出名的算法， 特点是都可以并行。本文根据UCI 的g...

[marvinxu](https://www.jianshu.com/u/d821217bed45)阅读 3,613评论 2赞 4

  * [加密进阶（佩服写这篇文章的人）](https://www.jianshu.com/p/006a8e6e25e7)

CTF中那些脑洞大开的编码和加密 0x00 前言 正文开始之前先闲扯几句吧，玩CTF的小伙伴也许会遇到类似这样的问...

[查无此人asdasd](https://www.jianshu.com/u/6345e3b05eca)阅读 5,408评论 0赞 19

  * [行测大礼包—（数字推理题725道详解）](https://www.jianshu.com/p/bbf28250735f)

【1】7，9，-1，5，( ) A、4；B、2；C、-1；D、-3 分析:选D，7+9=16；9+（-1）=8；（...

[Alex_bingo](https://www.jianshu.com/u/d93f73567d7a)阅读 15,915评论 1赞 19

 