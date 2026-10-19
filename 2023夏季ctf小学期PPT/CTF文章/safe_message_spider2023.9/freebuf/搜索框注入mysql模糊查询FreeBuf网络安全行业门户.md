## mysql模糊查询和搜索框注入

### 1、mysql模糊查询的四种方式

%，匹配任意长度或类型的字符

_，匹配单个任意字符

[]，匹配括号中给定的一个字符或者一个范围

[^]，与上面一个相反，匹配不再括号内的

### 2、一般的模糊查询语句

select 字段 from 表名 where 字段 like 条件

### 3、搜索框注入

一般的网页为了用户着想都会提供搜索框查询相关信息，自然搜索框也成为了与数据库交互的一个重要接口。

对于搜索框而言最简单的实现方式就是模糊查询，例如要搜索某个姓王的用户，会在查询中执行如下SQL语句

    
    
    select username from users where username like '王%'
    

如果我们没有在搜索框处对用户输入做任何限制，那么用户输入恶意的字符就会造成SQL注入

### 4、靶场演示--以pikachu靶场的搜索框为例

输入一个%会出现什么结果呢？  
![图片.png](https://image.3001.net/images/20210815/1629029242_6119037adbdb79bf713c4.png!small)

如图所示它会将该字段所有值的结果抛出，它实际执行的SQL语句大概是这样的

    
    
    select uid,username,email from users where username like '%$var%'
    

$var作为变量接收用户输入

推断出它执行的SQL语句后就可以构造恶意的SQL语句，来判断它显示的字段数了  
如果用户输入如下：`$var = ' order by 1 -- -`，则执行SQL语句如下：

    
    
    select uid,username,email from users where username like '%' order by 1 -- -%'
    

正常情况下，只要order by语句字段数正确，同样会将该字段所有值抛出  
![图片.png](https://image.3001.net/images/20210815/1629029276_6119039cb39beb8e59d88.png!small)

通过几次尝试显示字段数为3，然后就可以使用union语句查询数据库名、表名、字段名和数据了。

如下，查询数据库名和数据库版本  
![图片.png](https://image.3001.net/images/20210815/1629029292_611903acf17efe58f2b90.png!small)

剩下查询表名、字段的方式就与一般的数字型、字符型注入的方式一样了

## 总结

造成搜索框注入的原因还是程序没有对用户输入进行过滤，导致用户可以对字符进行闭合和注释，构造恶意的SQL语句，获取数据库信息。

