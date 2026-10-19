***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**最近一直在学习《[[红日安全]代码审计](https://www.freebuf.com/column/188018.html)》系列中关于php代码中存在的问题，从中受益匪浅。从中选取了一个DM企业建站的cms用作练习，在还原了练习中的漏洞后尝试对其进行代码审计，运用近期学习到的php审计知识点对该cms进行了审计，并很幸运的发现了一枚远程代码执行漏洞。接下来详细记录了漏洞发现的过程与大家交流学习。**

## 0x01 环境搭建

选用了XAMPP 与 DM企业建站v20190522
进行代码审计。XAMPP（Apache+MySQL+PHP+PERL）是一个功能强大的建站集成软件包，主界面如下：

![2.PNG](https://image.3001.net/images/20190626/1561521546_5d12ed8a9943e.png!small)

## 0x02 代码审计

CMS通常会包含install文件，方便用户网站一键搭建。但是该文件也是经常出现漏洞的位置，本次审计的CMS漏洞也是出现在安装部分，具体细节如下：

### [+] 漏洞位置 ：/install.php

    
    
      if($act=='doit'){
        echo ' <div class="wrap"> ';
        $local = htmlentitdm($_POST['local']);
        $data = htmlentitdm($_POST['data']);
        $user = htmlentitdm($_POST['user']);
        $ps = htmlentitdm($_POST['ps']);
        $mysql55 = htmlentitdm($_POST['mysql55']);
    
        if($mysql55=='y') $mysqlcont =  file_get_contents($filesqlnew);
        else  $mysqlcont =  file_get_contents($filesqlold);
    
        //echo $mysqlcont;
            file_put_contents($filesql,$mysqlcont);
    
        $content = '<?php  $mysql_server_name="'.$local.'"; $mysql_database="'.$data.'"; $mysql_username="'.$user.'";  $mysql_password="'.$ps.'"; ?>';  
        file_put_contents($file,$content);
            ...
    

可以看出程序接收参数后对参数进行了过滤，然后拼接成一个字符串写入到了文件之中，继续查看htmlentitdm函数。

    
    
    function htmlentitdm($v){
    	$v = str_replace("..'", "===-", $v); //filter something  
    	$v = str_replace(':','===-', $v);
    	$v = str_replace('\\','===-', $v);
       return htmlentities(trim($v),ENT_QUOTES,"utf-8");
    }//end func  
    

该函数中过滤了一部分非法字符串，但是过滤的并不完全，还有许多字符没有过滤。

在这里还要用到php语言的特性：[PHP可变变量](http://php.net/manual/zh/language.variables.variable.php)
。在PHP中双引号包裹的字符串中可以解析变量，而单引号则不行。
（[[红日安全]代码审计](https://www.freebuf.com/column/182130.html)）

在第一段代码中： _$content = ' <?php $mysql_server_name="'.$local.'";
$mysql_database="'.$data.'"; $mysql_username="'.$user.'";
$mysql_password="'.$ps.'"; ?>';_

可以发现拼接后的字符串把所有的变量都放到了单引号中，并且在字符串过滤时并没有过滤‘{}’，‘()’和‘$’等非法字符。这样一来漏洞利用方式就很清晰了，通过变量注入可执行代码，再去访问注入代码的php文件即可。

## 0x03 漏洞触发

在搞清楚漏洞利用法式后，下一步就是要寻找漏洞触发点，我们可以按照建站顺序一步一步寻找，因为漏洞点在install.php，其漏洞触发点也应该在安装部分。

![image.png](https://image.3001.net/images/20190626/1561533487_5d131c2fa23bc.png!small)在安装的过程中可以发现上图界面，主要是对数据库进行配置。传入的参数与漏洞点参数相同，所以在参数部分尝试进行注入‘${phpinfo()}’（任意字段注入效果相同）。接下来需要寻找代码插入的文件位置，最后在‘database.php’文件中发现了插入的代码，如下图：

![image.png](https://image.3001.net/images/20190626/1561533794_5d131d627e433.png!small)在php解析过程中，双引号内的字符串被当做变量执行，但是/component/dm-config/database.php文件无法直接访问。继续寻找可访问该文件的路径，最后发现在‘index.php’中包含了‘indexDM_load.php’。  

![image.png](https://image.3001.net/images/20190626/1561534167_5d131ed7975f8.png!small)  

在‘indexDM_load.php’中包含了我们所需要的‘database.php’。因此直接访问网站首页后可以远程执行代码，最终效果如下：

执行phpinfo()效果图：  

![image.png](https://image.3001.net/images/20190626/1561534287_5d131f4fdbf55.png!small)获取服务器进程列表：  

##
![image.png](https://image.3001.net/images/20190626/1561534306_5d131f62a756e.png!small)0x04
新的问题

在CMS建站结束后，install文件一般都会删除，防止攻击者重新访问后重建网站。在DM企业建站中，建站结束后'install.php'会被重命名为‘install+9位随机数.php’，一开始打算尝试爆破install的新生成的文件，但是9位随机数爆破空间为10的9次方，爆破空间太大没有什么可行性。之后在代码中找到了重命名部分的代码：

![image.png](https://image.3001.net/images/20190626/1561535242_5d13230a8fcb1.png!small)

  
可以看出install文件并不是完全的9位随机数命名，而是install + 四位随机（1111-9999） + ‘6’ +
四位随机数（1111-9999） +
‘.php’，这样以来爆破空间缩小了很多，通过爆破可以在很短的时间内找到install文件的新路径，爆破代码也很好实现。

## 0x05 最终流程

step1：暴力破解重命名后的install文件位置

step2：访问重命名后的install文件，并在参数中注入形如‘${phpinfo()}’的代码

step3：访问网站首页执行代码

在这里也可以尝试通过远程代码执行向网站中写入后门文件，再通过连接后门文件管理整个网站。

以上就为我发现漏洞及利用的整个流程，漏洞并不难，记录下来与大家共同学习交流。（已通知该cms开发修改漏洞）

 ***本文作者：Kriston，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

