***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ** ***本文原创作者：丶楼兰，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

 **萌新入坑PHP代码审计中╭(°A°`)╮**
**选了这个易上手CMS，费尽心思审计出了一个有趣的二阶注入，满意的睡了，第二天打算写文档的时候，竟然发现……**

## 0x00 漏洞代码

用户在发布资讯时,尽管对POST数据使用了addslashes函数，但是由于editor参数可控仍旧可以插入构造好的Payload

/user/zxsave.php 第51行：

![1.png](https://image.3001.net/images/20180906/1536234878_5b91157ea8cbb.png!small)

在查看用户发布的资讯时,会查询文章id所对应的相关信息。

/zx/show.php 第36行：

![2.png](https://image.3001.net/images/20180906/1536234885_5b911585f1b14.png!small)

会根据该资讯id，需要具备的查看信息的用户组级别（groupid）来进行判断,如果groupid不为0，并且查看资讯时需要花费积分时，那么便会调用Payif函数。

/zx/show.php 第155行：

![3.png](https://image.3001.net/images/20180906/1536234893_5b91158d2a05f.png!small)

如果用户积分多余查看资讯的积分时，那么便会：

  1. 减去查看者对应的积分（根据cookie里面的Username参数）；
  2. 增加发布者对应的积分（根据查看文章对应信息里面的editor字段）；
  3. ...

/zx/show.php 第92行：

![4.png](https://image.3001.net/images/20180906/1536234901_5b9115957a292.png!small)

例如：

1.正常模式下：editor=admin,$jifen=10时，那么第二条查询语句便是：

    
    
    update zzcms_user set totleRMB=totleRMB+10 where username = 'admin'

如果 editor=' and groupid=(select sleep(3)) -- - 时，那么第二条查询语句便是：

    
    
    update zzcms_user set totleRMB=totleRMB+10 where username = '' and groupid = (select sleep(3)) -- -'

此时我们便可根据页面所响应的时间，来判断查询语句是否成功了。

## 0x01 利用漏洞

可以看到普通用户的groupid是1。

![5.png](https://image.3001.net/images/20180906/1536234910_5b91159e6bdfc.png!small)

在发布资讯是可以选择vip用户才能查看或者高级会员查看，或者直接在BurpSuite中修改groupid为2，并设置查看积分为大于0的值：

![6.png](https://image.3001.net/images/20180906/1536234918_5b9115a6989e0.png!small)

在查看该信息时可以看到，添加了限制：

![7.png](https://image.3001.net/images/20180906/1536234926_5b9115aedb177.png!small)

此时将editor设置为咱们的Payload：

![8.png](https://image.3001.net/images/20180906/1536234936_5b9115b8a1e4b.png!small)

此时在查看资讯时便可以看到响应时间的异常：

![9.png](https://image.3001.net/images/20180906/1536234945_5b9115c16e731.png!small)

我们最后传入数据库的SQL语句如下，可以看到，这样的话我们每执行一次查询语句便加不了10积分，而查看资讯却需要10积分，这样说来，执行一次Payload需要十积分，经过测试，最少也是1分，这...也太豪了。

> update zzcms_user set totleRMB=totleRMB+10 where username = TEag1e'' and
> groupid = (select sleep(3)) -- -'

经过我思考后，我将and逻辑运算符替换为了or逻辑运算符，酱紫的话，便可以减10，加10了，一分钱不花了

 **然后说一下我遇到的坑/新GET到的细节：**

MySQL中在使用or逻辑运算符时，如果前面的条件已经将数据库中的结果全部筛选出来了，那么or后面的条件便不会在进行执行了。

例如：此时数据库中全是groupid为1的用户

![10.png](https://image.3001.net/images/20180906/1536234953_5b9115c96e082.png!small)

如果SQL语句是：

    
    
    update zzcms_user set totleRMB=totleRMB+10 where groupid = 1 or username = (select sleep(3))

那么username后面的自查询便不会执行，而如果使用的是and逻辑运算符的话，如果and前面的条件一条数据也查询不出来时，那么and后面的子查询语句便也不会执行了。

## 0x02 第二天醒来

第二天，我正要写文档的时候，发现咋就失败了呢，等我回到数据库中时，发现editor字段竟然设置了50个字符的限制，好惨...

![11.png](https://image.3001.net/images/20180906/1536234968_5b9115d892e72.png!small)

尽管有些失落，但是我并不气馁，毕竟漏洞被忽略的多了已经习惯了。。

## 0x03 一些小东西

上文笔者已经说过了，看积分文章时：

1.减去查看者对应的积分（根据cookie里面的Username参数）；

2.增加发布者对应的积分（根据查看文章对应信息里面的editor字段）。

经过测试发现此处存在逻辑漏洞，未校验cookie里面Username参数，那么发布资讯时，将editor设置为咱们自己的用户名，在查看咱们构造的需要花费积分的资讯时，将cookie里面的Username设置为其他用户的用户名。

那么：每看一次，受害者便减掉10积分，而我们则加10积分。

看一下初始时两个用户的积分：

![12.png](https://image.3001.net/images/20180906/1536234980_5b9115e4ec996.png!small)

此时我们设置好前置条件后，在查看该资讯时，将Username为test：

![13.png](https://image.3001.net/images/20180906/1536234994_5b9115f24bf4a.png!small)

可以看到咱们的积分加了10分，而test用户却减了10分：

##
![14.png](https://image.3001.net/images/20180906/1536235003_5b9115fb2d4f0.png!small)附录

zzcms v8.3 下载地址：

<https://pan.baidu.com/s/1vFT6pG31J7NMKtRsbt1fLQ>

 ***本文原创作者：丶楼兰，本文属FreeBuf原创奖励计划，未经许可禁止转载**

