## 1.首先要明白序列化和反序列化

序列化：主要是将变量进行转换，使其变为字符串，序列化一个对象将会保存对象的所有变量，但是不会保存对象的方法，只会保存类的名字。在程序执行结束时，内存数据便会立即销毁，变量所储存的数据便是内存数据，而文件、数据库是“持久数据”，因此PHP序列化就是将内存的变量数据“保存”到文件中的持久数据的过程。方便保存和传输，并且可以达到节省空间的目的

反序列化：主要是在特定的时候将序列化转换为字符串的内容再转换为原来的变量继续使用，简单来理解起来就是将序列化过存储到文件中的数据，恢复到程序代码的变量表示形式的过程，恢复到变量序列化之前的结果。

## 2.函数

PHP反序列化的相关函数主要是：serialize()和unserialize()

其中serialize()可以将变量转换为字符串，并且在转换的过程中保存当我变量的值

而unserialize()2可以将serialize()转换的字符串再转换为变量

## 3.内容

主要包括：类，变量，方法，对象（如下图）![1620810232_609b99f851d2471f1a240.png!small?1620810232950](https://image.3001.net/images/20210512/1620810232_609b99f851d2471f1a240.png!small?1620810232950)

## 4.PHP魔法函数

__construct 当一个对象创建时被调用，

__destruct 当一个对象销毁时被调用，

__toString 当一个对象被当作一个字符串被调用。

__wakeup() 使用unserialize时触发

__sleep() 使用serialize时触发

__destruct() 对象被销毁时触发

__call() 在对象上下文中调用不可访问的方法时触发

__callStatic() 在静态上下文中调用不可访问的方法时触发

__get() 用于从不可访问的属性读取数据

__set() 用于将数据写入不可访问的属性

__isset() 在不可访问的属性上调用isset()或empty()触发

__unset() 在不可访问的属性上使用unset()时触发

__toString() 把类当作字符串使用时触发,返回值需要为字符串

__invoke() 当脚本尝试将对象调用为函数时触发

### 示列：

#### 系列化

    
    
    <?php
    class User
    {
      public $age = 0;
      public $name = '';
     
      public function PrintData()
      {
        echo 'User '.$this->name.'is'.$this->age.'years old. <br />';
      }
    }
    //创建一个对象
    $user = new User();
    // 设置数据
    $user->age = 20;
    $user->name = 'daye';
     
    //输出数据
    $user->PrintData();
    //输出序列化之后的数据
    echo serialize($user);
     
    ?>
    

![1620810302_609b9a3e62b4f2b651123.png!small?1620810303232](https://image.3001.net/images/20210512/1620810302_609b9a3e62b4f2b651123.png!small?1620810303232)

O:4:"User":2:{s:3:"age";i:20;s:4:"name";s:4:"daye";}

对象类型:长度:"类名":类中变量的个数:{类型:长度:"值";类型:长度:"值";......}

反序列化

    
    
    <?php
    class User
    {
      public $age = 0;
      public $name = '';
    
      public function PrintData()
      {
        echo 'User '.$this->name.' is '.$this->age.' years old. <br />';
      }
    }
    //重建对象
    $user = unserialize('O:4:"User":2:{s:3:"age";i:20;s:4:"name";s:4:"daye";}');
    
    $user->PrintData();
    
    ?>
    

![1620810338_609b9a62ed82a2a2c64b0.png!small?1620810339480](https://image.3001.net/images/20210512/1620810338_609b9a62ed82a2a2c64b0.png!small?1620810339480)

#### 魔法函数自动调用

    
    
    <?php
    class test{
     public $varr1="abc";
     public $varr2="123";
     public function echoP(){
     echo $this->varr1."<br>";
     }
     public function __construct(){
     echo "__construct<br>";
     }
     public function __destruct(){
     echo "__destruct<br>";
     }
     public function __toString(){
     return "__toString<br>";
     }
     public function __sleep(){
     echo "__sleep<br>";
     return array('varr1','varr2');
     }
     public function __wakeup(){
     echo "__wakeup<br>";
     }
    }
     
    $obj = new test(); //实例化对象，调用__construct()方法，输出__construct
    $obj->echoP();  //调用echoP()方法，输出"abc"
    echo $obj;  //obj对象被当做字符串输出，调用__toString()方法，输出__toString
    $s =serialize($obj); //obj对象被序列化，调用__sleep()方法，输出__sleep
    echo unserialize($s); //$s首先会被反序列化，会调用__wake()方法，被反序列化出来的对象又被当做字符串，就会调用_toString()方法。
    // 脚本结束又会调用__destruct()方法，输出__destruct
    ?>
    

![1620810374_609b9a869ac9a474517c7.png!small?1620810375166](https://image.3001.net/images/20210512/1620810374_609b9a869ac9a474517c7.png!small?1620810375166)

## 总结

当出现PHP反序列化漏洞的时候，首先我们可以将想要输入的变量使用serialize()进行序列化，如：O:1:"S":1:{s:4:"test";s:28:"<img
src=x onerror=alert(1)>";}

其次，将序列化之后的字符串放到url中。在PHP代码中使用了unserialize()，则会自动执行特定的魔法函数，如果魔法函数中有其他的一些危险函数且是我们可控的，即可进行其他操作。

部分资料来源：<https://www.jb51.net/article/188446.htm>

靶场实战链接：<https://blog.csdn.net/qq_41954384/article/details/103831182>

