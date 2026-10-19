SQL报错注入就是利用数据库的某些机制，人为地制造错误条件，使得查询结果能够出现在错误信息中。这种手段在联合查询受限且能返回错误信息的情况下比较好用。

##  ** **01使用报错注入的前提****

页面上没有显示位但是有sql语句执行错误信息输出位。

使用mysql_error()函数，可以返回上一个Mysql操作产生的文本错误信息。

##  ** **02 MYSQL报错注入的分类****

（1）BIGINT等数据类型溢出

（2）xpath语法错误

（3）floor（）报错

（4）列名重复报错

（5）参数不规范报错

##  ** **03数据类型溢出****

1.最大整型数据运算溢出：

适用版本：mysql版本号大于5.5.5

（Mysql处理整型数据如下表：）

![](https://image.3001.net/images/20230725/1690273289_64bf8609bf1c3974747bd.png!small)

报错原理：

无标志位的最大整型数据是2^64-1也就是18446744073709551615，当超过这个数值时，会产生数据溢出错误，并返回错误信息

（BIGINT UNSIGNED value is out of range in ‘xxxxxxxxxx’）

![](https://image.3001.net/images/20230725/1690273345_64bf864177e53ddf7f28f.png!small)

当然，在尝试注入的时候，尤其是对长度做了限制的时候，不需要输入完整的数进去，可以使用按位取反运算即可：

![](https://image.3001.net/images/20230725/1690273442_64bf86a2e4d5a8fbf9806.png!small)

同时我们知道，当sql语句成功执行后会返回0值，这个值可以进行逻辑运算，也可以进行数学运算，也就是说我们可以利用这个值与最大整数做运算，由此可以绕过一些限制并实施sql注入。

![](https://image.3001.net/images/20230725/1690273490_64bf86d27be970d9d4766.png!small)![](https://image.3001.net/images/20230725/1690273522_64bf86f2794b1649452eb.png!small)

![](https://image.3001.net/images/20230725/1690273501_64bf86dd64884ae8be0e2.png!small)

注入尝试：

Payload如下：

![](https://image.3001.net/images/20230725/1690273591_64bf873764b3c2bdcc5d3.png!small)![](https://image.3001.net/images/20230725/1690273607_64bf8747372713be90279.png!small)

2.exp函数溢出错误：

适用版本：mysql5.5.44-5.5.47.

报错原理：

Exp函数中参数的取值最大为709，当取710时，运算的数据发生了溢出，返回错误信息（DOUBLE value is out of range in
‘xxxxxxx’）

![](https://image.3001.net/images/20230725/1690273753_64bf87d9b40fe99b98efc.png!small)![](https://image.3001.net/images/20230725/1690273762_64bf87e264e7420ddbb58.jpg!small)

注入尝试：

Payload如下

![](https://image.3001.net/images/20230725/1690273854_64bf883e09f6d1602ea3d.png!small)![](https://image.3001.net/images/20230725/1690273864_64bf88489f41403c80630.png!small)

当版本大于5.5.53时，不能返回查询结果

![](https://image.3001.net/images/20230725/1690273900_64bf886cb7479c00a32c8.png!small)

##  **04 XPATH语法错误**

适用版本：mysql版本号大于5.1.5

从mysql5.1.5开始提供两个XML查询和修改的函数，extractvalue（）和updatexml（）。

![](https://image.3001.net/images/20230725/1690273962_64bf88aa4f8e7557b4fa0.png!small)

Extractvalue（）负责在xml文档中按照xpath语法查询节点内容updatexml（）则负责修改查询到的内容

函数测试：

![](https://image.3001.net/images/20230725/1690274000_64bf88d00e4c0bf2e8f75.png!small)

报错原理：

这两个函数的第二个参数都要求是符合xpath语法的字符串，如果不满足要求就会报错，并且会把查询结果放在报错信息里。

注入测试：

![](https://image.3001.net/images/20230725/1690274265_64bf89d934094bde4a65e.png!small)![](https://image.3001.net/images/20230725/1690274278_64bf89e68066a150d4cb0.png!small)

但是这两个函数的限制要求是最长不能超过32位。

##  **05 Floor（）注入**

关键函数：

Rand() -----产生0~1的伪随机数

Floor() -----向下取整数

Concat() -----连接字符串

Count() -----计算总数

Payload如下：

Select count(*),concat(PAYLOAD,floor(rand(0)*2))x from 表名 group by x;

原理分析：

首先rand（0）的作用是产生0~1的随机数，但这个随机数列是伪随机数，也可以说是一组固定的值，当我们对这组随机数乘2后，得到的也是一组固定的值，如下：

![](https://image.3001.net/images/20230725/1690274351_64bf8a2fad0336d7fdaf0.png!small)![](https://image.3001.net/images/20230725/1690274386_64bf8a5235af10680e18b.png!small)

然后我们使用floor（）函数，向下取整，得到了一组十分重要的数列（011011011…….）无限重复，这个数列很重要！

![](https://image.3001.net/images/20230725/1690274432_64bf8a805aed3f216a786.png!small)

然后，我们来分析一下count（）和group by连用的情况

这是user表中数据

![](https://image.3001.net/images/20230725/1690275086_64bf8d0ede3543ada61dd.png!small)

对user表按照id查询每个id出现的总数

![](https://image.3001.net/images/20230725/1690275108_64bf8d246cf2404413c1b.png!small)

深入剖析一下原理，主要分以下几个步骤：

1.建立虚拟表，其中key是主键，不能重复

![](https://image.3001.net/images/20230725/1690275136_64bf8d409382a0401ec21.png!small)

2.开始从原始表中查询数据，取第一条查看虚拟表中是否存在该数据，不存在则插入新数据，存在则count（*）字段直接加1。

![](https://image.3001.net/images/20230725/1690275819_64bf8feb43c9b27e4be81.png!small)

3.重复步骤2，直至原始表中数据被全部取完。

![](https://image.3001.net/images/20230725/1690275849_64bf900904582d83841dc.png!small)

但是，当遇上我们刚刚构造的011011这个神奇的数列的时候，就会出现一个大问题。这种报错方法的本质是因为floor(rand(0)*2)的重复性，导致group
by语句出错，当我们使用这个数列的时候会造成主键重复，抛出错误。

我们来还原一下注入过程：

  1. 构造虚拟表

第一次运算group
by后面的floor(rand(0)*2)，得到0值，将该值与虚拟表中进行比对，发现没有此值，故做插入处理，但当插入时进行了第二次运算，取1值，并彻底插入虚拟表中，结果如下：![](https://image.3001.net/images/20230725/1690275900_64bf903cbf930dce1002c.png!small)

3.继续，取第二个值1（这时已经是第三次运算后的值了）在虚拟表中比对，发现有值，所以count加1![](https://image.3001.net/images/20230725/1690275938_64bf906255037a7bc7b94.png!small)

4.当取第三个值0（这里因为是第四次运算所以取0）时，并未在虚拟表中找到该值，所以做插入处理，当插入时进行了第五次运算，变成了1进行插入，又因为表中已经存在1的主键，故产生主键重复错误，抛出异常（主键1重复）。

![](https://image.3001.net/images/20230725/1690275966_64bf907e8ec0fb7064fc7.png!small)注入测试：![](https://image.3001.net/images/20230725/1690276092_64bf90fc33221b714ed72.png!small)

整个查询过程中，floor(rand(0)*2)被计算了5次，查询原始数据表3次，所以表中需要至少3条数据才能报错。

##  **06 列名重复报错**

适用版本：只适用于mysql低版本

关键函数：

NAME_CONST()

![](https://image.3001.net/images/20230725/1690276188_64bf915c3bbfe748e0bb0.png!small)

根据官方文档，name_const（）函数要求参数必须是常量，所以我们当连续使用两个name_const（）函数，并把其中参数作为要查询的函数，则会造成列名重复错误，并将查询结果返回在错误信息中。

![](https://image.3001.net/images/20230725/1690276209_64bf9171eb0f7b91b3d00.png!small)

利用列名重复报错的特性，加上join函数可以进一步获取列名

![](https://image.3001.net/images/20230725/1690276233_64bf91897000f548020ef.png!small)

##  **07 参数不规范报错**

适用版本：mysql版本号在5.5.44 - 5.7.17

mysql有些几何函数，例如geometrycollection()，multipoint()，polygon()，multipolygon()，linestring()，multilinestring()，这些函数对参数要求是形如(1
2,3 3,2 2 1)这样几何数据，如果不满足要求，则会报错。

注入测试：![](https://image.3001.net/images/20230725/1690276276_64bf91b42b283e898d64c.png!small)
**![](https://image.3001.net/images/20230725/1690276293_64bf91c5238dbd75b15cb.png!small)**

##  **08 Mysql报错注入的防御方法**

1\. 屏蔽能造成报错注入的各种函数，函数

2.对输入长度做限制，对用户输入做预处理

3.对各种报错注入的返回结果，统一返回至不包含任何错误提示信息的回显页面。

4.使用数据库防火墙，精准分析业务SQL和危险SQL，拦截SQL注入等危险语句。

