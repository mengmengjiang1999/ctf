<http://inject2.lab.aqlab.cn:81/Pass-01/index.php?id=1>  
存在index.php? 前几节课讲过？一般为get传参！  
当然界面上也说了

![](https://image.3001.net/images/20210928/1632814770_6152c6b24f4e8f49b55c7.png!small)————————————————开始尝试——————————————  
1.判断是否存在注入

![](https://image.3001.net/images/20210928/1632814771_6152c6b312b1235691108.png!small)当输入id=2时页面发生变化  
再继续  
<http://inject2.lab.aqlab.cn:81/Pass-01/index.php?id=2%20and%201=2>  
当加上条件and1=2时界面不显示（报错）基本确定存在注入  
————————————————判断字段数——————————————  
<http://inject2.lab.aqlab.cn:81/Pass-01/index.php?id=2%20order%20by%204>输入order
by 4 之后原本显示正常的界面显示不正常！  
判断当前表中字段数为3  
由于接下来要使用union select 联合查询（联合查询关键在于前后字段数需要相同 ）所以进行字段数判断！  
————————————————判断回显点——————————————

![](https://image.3001.net/images/20210928/1632814771_6152c6b3b795e7e1e8fd7.png!small)输入·联合查询发现回显为第二三字段![](https://image.3001.net/images/20210928/1632814772_6152c6b466c4b41ab9598.png!small)并且得出当前database（）=’error’

![](https://image.3001.net/images/20210928/1632814772_6152c6b4e062ea4b7a355.png!small)再次查看所使用MySQL
版本  
由于MySQL版本高于5.0 大概率有系统自带库information_schema/ tables/ columns 存在  
————————————————尝试查找——————————————![](https://image.3001.net/images/20210928/1632814773_6152c6b58a56c30251ffb.png!small)查询出一个table_name为user
那么我们再看看有没有其他的表  
在url尾输入 limit 0，1 /1，1 /2，1 /尝试一下

![](https://image.3001.net/images/20210928/1632814774_6152c6b6138bd9de12dbe.png!small)发现输出为error表中的内容  
原来是因为 id=1 and 1=1 并没有造成前面的数据异常，导致输出为  
id =1 and 1=1 limit 1,1 的内容

改正后输出尝试得到另一个表 error_flag  
![](https://image.3001.net/images/20210928/1632814774_6152c6b697baa6fdefdc4.png!small)————————————————尝试查找字段——————————————

![](https://image.3001.net/images/20210928/1632814775_6152c6b72767ce4927f4d.png!small)发现表error_flag
中有id 字段  
再次limit 尝试

![](https://image.3001.net/images/20210928/1632814775_6152c6b79feb128df68a7.png!small)得到想要内容
column_name 为Flag  
————————————————尝试查找内容——————————————  
![](https://image.3001.net/images/20210928/1632814776_6152c6b822d8d599b120f.png!small)得到flag  
提交发现错误  
再次limit  
得出更多![](https://image.3001.net/images/20210928/1632814776_6152c6b89ac7206e0e563.png!small)

![](https://image.3001.net/images/20210928/1632814777_6152c6b91f49a99f6626b.png!small)

![](https://image.3001.net/images/20210928/1632814777_6152c6b9a10090b834909.png!small)完成第一题4.1.1-SQL注入-显错注入Rank 1

印证（注入的本质是由于用户可控制输入的内容被当作数据库代码进行执行！）

### 第二题

————————————————分析url——————————————-  
<http://inject2.lab.aqlab.cn:81/Pass-02/index.php?id=1>  
输入id=1/2/3 返回界面会发生变化

但是输入id=3-1界面无变化

![](https://image.3001.net/images/20210928/1632814778_6152c6ba310ac4b65eff0.png!small)并且输入

![](https://image.3001.net/images/20210928/1632814778_6152c6bac1bed283de87b.png!small)显示界面正常  
and 1=2 永远不可能成立 为什么界面会正常

![](https://image.3001.net/images/20210928/1632814779_6152c6bbb079289341f1d.png!small)查看提示  
被闭合

![](https://image.3001.net/images/20210928/1632814780_6152c6bc3ee656072d8cb.png!small)说输入内容确实是被单引号所闭合当成一个整体字符串来  
并没有将1！=2这个执行  
于是想办法破坏’’由于单引号需要两个在一起才能发挥作用  
于是’ 我在次输入单引号并且破坏后面的单引号#(或者—%20+将其注释)’  
————————————————开始尝试——————————————

![](https://image.3001.net/images/20210928/1632814780_6152c6bcad5ceeaf6da06.png!small)

![](https://image.3001.net/images/20210928/1632814781_6152c6bd4ab3c7087d7be.png!small)发现界面错误了  
再次尝试  
将条件变为 and 1=1

![](https://image.3001.net/images/20210928/1632814781_6152c6bdb9223ba8cdf1f.png!small)他又行了  
说明注释单引号起作用了  
————————————————判断字段数——————————————  
order by 1/2/3/4  
当输入order by 4 时候界面出错  
大概率说明 字段数为 3  
————————————————判断回显点——————————————

![](https://image.3001.net/images/20210928/1632814782_6152c6be3f8f3ea4579ec.png!small)由此发现回显点为第二三字段  
并且得出 数据库的版本 以及 database（）=‘error’  
————————————————尝试查找——————————————

![](https://image.3001.net/images/20210928/1632814782_6152c6beb0059c8591dce.png!small)发现table
有user  
继续使用limit 得出

![](https://image.3001.net/images/20210928/1632814783_6152c6bf31096dbb6ed0d.png!small)得出想要的table
为error_flag

————————————————尝试查找字段——————————————

![](https://image.3001.net/images/20210928/1632814783_6152c6bfbc83ea4f4a819.png!small)得到字段为
flag

————————————————尝试查找内容——————————————

![](https://image.3001.net/images/20210928/1632814784_6152c6c04a2a589bd0c74.png!small)得出flag  
再次使用limit 查看是否有其他flag

![](https://image.3001.net/images/20210928/1632814784_6152c6c0c8db706e1781e.png!small)

![](https://image.3001.net/images/20210928/1632814785_6152c6c15b60bc70697c9.png!small)

![](https://image.3001.net/images/20210928/1632814785_6152c6c1d5131a11ed43a.png!small)得到所有flag  
完成第二题4.1.2-SQL注入-显错注入Rank 2  
验证（注入本质为用户输入的数据被数据库当作代码执行）

### 第三题

——————————————研究url——————————————

![](https://image.3001.net/images/20210928/1632814786_6152c6c25fb5ab247ddc3.png!small)

![](https://image.3001.net/images/20210928/1632814786_6152c6c2e6f690e00782b.png!small)输入不同id
参数 界面信息会发生变化

输入 and 1=2 尝试

![](https://image.3001.net/images/20210928/1632814787_6152c6c38bc4f3aceb0ed.png!small)发现界面无动于衷  
发现(‘2 and 1=2’)输入内容被’’和（）包围

同样是输入的内容被闭合

尝试 突破闭合

![](https://image.3001.net/images/20210928/1632814788_6152c6c40825643562185.png!small)发现’
突破闭合行不通

![](https://image.3001.net/images/20210928/1632814788_6152c6c47ba103a67b059.png!small)括号突破闭合同样行不通

再次尝试

![](https://image.3001.net/images/20210928/1632814788_6152c6c4eee9a0187a59a.png!small)更改and
条件

![](https://image.3001.net/images/20210928/1632814789_6152c6c56a807b961e08a.png!small)突围成功  
—————————————— 判断字段数————————————————

![](https://image.3001.net/images/20210928/1632814789_6152c6c5d809e081d1514.png!small)当oeder
by 为4 时候  
出现错误  
得出字段数为三  
—————————————— 判断回显点————————————————

![](https://image.3001.net/images/20210928/1632814790_6152c6c64ed706f54c0fe.png!small)回显为二三字段

—————————————— 尝试找出table_name————————————————

![](https://image.3001.net/images/20210928/1632814790_6152c6c6d182547b99eb1.png!small)得出user表  
limit  
得出error_flag 表  
![](https://image.3001.net/images/20210928/1632814791_6152c6c75eba441f77021.png!small)

—————————————— 尝试找出column_name————————————————

![](https://image.3001.net/images/20210928/1632814791_6152c6c7e70e7ae8026ae.png!small)得出字段flag

—————————————— 尝试找出内容————————————————

![](https://image.3001.net/images/20210928/1632814792_6152c6c89e7cfa8fb6af5.png!small)继续limit  
得出更多的flag

![](https://image.3001.net/images/20210928/1632814793_6152c6c91ab4c0796069d.png!small)

![](https://image.3001.net/images/20210928/1632814793_6152c6c9a79336e3ec634.png!small)

![](https://image.3001.net/images/20210928/1632814794_6152c6ca319a8861fa559.png!small)得到所有flag  
完成第三题4.1.3-SQL注入-显错注入Rank 3  
验证（注入本质为用户输入的数据被数据库当作代码执行）

### 第四题

————————————————分析url——————————————

![](https://image.3001.net/images/20210928/1632814794_6152c6cab3d45d17aad93.png!small)  
貌似没有什么异常  
但是  
输入and1=2 无反应

![](https://image.3001.net/images/20210928/1632814795_6152c6cb434801f1ea112.png!small)发现被双引号加括号包围了

尝试突破闭合包围  
基于前面经验直接”）突破闭合

![](https://image.3001.net/images/20210928/1632814795_6152c6cbb145b080341de.png!small)突破成功  
——————————————判断字段数————————————

![](https://image.3001.net/images/20210928/1632814796_6152c6cc335ed2500e573.png!small)字段数为三  
——————————————判断回显点————————————

![](https://image.3001.net/images/20210928/1632814796_6152c6cca9d3820e5259c.png!small)回显点在二三字段  
——————————————查找表————————————

![](https://image.3001.net/images/20210928/1632814797_6152c6cd3866319e01744.png!small)使用limit
得出其他表

![](https://image.3001.net/images/20210928/1632814797_6152c6cdca00fade76469.png!small)得到error_flag  
——————————————查找表中字段————————————

![](https://image.3001.net/images/20210928/1632814798_6152c6ce66ddc8407c083.png!small)得到flag
字段

——————————————查找表中内容————————————

![](https://image.3001.net/images/20210928/1632814798_6152c6ceed31e5aee627f.png!small)得到flag  
使用limit 得到其他的

![](https://image.3001.net/images/20210928/1632814799_6152c6cf750bad21e1d02.png!small)

![](https://image.3001.net/images/20210928/1632814799_6152c6cfe41a9905473bd.png!small)

![](https://image.3001.net/images/20210928/1632814800_6152c6d06cffd4d12cea1.png!small)完成第四题

结论：and 条件是需要加上的，从而使得想要的内容不受影响  
查找内容时候要细心，猜想时一次不行试多次  
不要一次不行就放弃  
细心特别是中英文差别！

