欢迎关注同名微信公众号！[狼蛛安全实验室](https://mp.weixin.qq.com/s/ccMQEhCoSwOaUV1RMFpFvg)！

## 正文

最近研究了一下部分压缩文件的文件头，发现在RAR中存在一个很有意思的字段“DOSTIME
FileTime”，在RAR4的压缩中不会将其转到UTC+0的时间，即在RAR4中压缩时，所使用的时间为本地时间，那么这个信息有什么意义呢？![](https://image.3001.net/images/20220812/1660273193_62f5c2291124370dc63df.png!small)

假设，在东京（UTC+9）有一个小黑客，在小黑客本机12点的时候，编译了一个木马，那么木马的修改时间为12点，小黑客将木马通过RAR4压缩，然后在小黑客时区的12点15分通过邮件的方式发送到中国（UTC+8）小李的电脑上，不幸的小李被邮件内容吸引，于是打开了压缩包中了马。

在以上场景中，从小李时区（UTC+8）的角度看，小李是在11点15分（UTC+8）收到的邮件，其中的木马却是在12点被生成，由此可以推测出攻击者时区大于小李的时区。

以上仅是一个利用的方法，实际上可玩性很高，作者也通过此方法辅助溯源到某攻击组织。

![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273204_62f5c23442dbc355ae30b.jpg!small)

以下篇幅主要讲解作者的一些分析流程，作者会尽量写的详细一点，方便大家学习。

首先，我们建立一个叫”FileName.txt”的文件，内容为：”Content”，（注意此处的文件时间：2021/5/19
12:23）![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273220_62f5c2441474e8c411183.jpg!small)

将其通过RAR4和RAR5压缩算法压缩为4.rar和5.rar

![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273234_62f5c25226cc42b2aa6c8.jpg!small)

通过16进制编辑器两个文件进行分析，此处推荐使用010 Editor，本文中所用到的解析模板放至文末。

RAR4的文件头为：52 61 72 21 1A 07 00

![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273242_62f5c25ad2ffa99b0b594.jpg!small)

RAR5的文件头为：52 61 72 21 1A 07 01 00

![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273255_62f5c26729b745afae090.jpg!small)

查看4.rar的字段”struct RarBlock block[0]”->”struct FileHeadBlock file”->”DOSDATE
FileDate”/”DOSTIME FileTime”

可以看到文件时间为”12:23″与文件创建时间相同，说明使用RAR4压缩时未对时间进行转换，仅通过压缩者电脑的时区保存。

![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273269_62f5c275407797c5b0101.jpg!small)

查看5.rar的字段”struct RarBlockV5 Block[1]”->”struct Records records”->”struct
Record record”->”FILETIME mtime”

可以看到文件时间为”04:23″与”12:23″的文件创建时间不相同，且刚好相差8个小时，说明使用RAR5压缩时会将时间转换为UTC+0的时区时间。

![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273281_62f5c2815523fd424a849.jpg!small)

PS：溯源需要尽可能的掌握更多的攻击者信息，上述的方法只是一个引子，希望可以帮大家扩展思路。

另外，在使用010 Editor时，如果发现没有RAR的解析模板，可以使用附件的代码，使用方式如下（附件获取方式见文末）：

![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273293_62f5c28de6e85cd7d015b.png!small)

新建模板后把附件的代码复制进去保存。

![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273302_62f5c2966998bdb6b7c18.png!small)![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273312_62f5c2a033852300f83af.png!small)

打开刚刚保存的.bt文档，运行起来即可。

![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273319_62f5c2a7dda2ffa8ac1df.png!small)![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273325_62f5c2add566be4f86f84.png!small)![640?wx_fmt=png](https://image.3001.net/images/20220812/1660273331_62f5c2b3d7f548d213046.png!small)

要是觉得有用的话，欢迎收藏转发此文章~

RAR模板解析代码：关注同名公众号”[狼蛛安全实验室](https://mp.weixin.qq.com/s/aPE-G38E7CZmp36JZG8cng)“，
**后台回复"RAR"获取下载链接！**

