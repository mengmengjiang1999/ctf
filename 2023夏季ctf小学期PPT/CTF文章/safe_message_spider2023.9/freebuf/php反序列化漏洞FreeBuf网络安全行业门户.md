## php反序列化漏洞常识

### 什么是PHP的反序列化漏洞

序列化与反序列化一开始的初衷是，便于数据完整的传输，但是由于在php的反序列化中，对象会自动调用的魔法函数，而这些魔法函数本身又调用了其他方法，最终呈现一种链式调用，则会引起危险代码的执行。

### 反序列化函数

serialize(); 将对象序列化成字符串  
unserialize(); 将字符串反序列化回对象

### 反序列化漏洞

以 __ 开头的函数，是PHP 中的魔术方法。  
类中的魔术方法，在特定情况下会自动调用。即使魔术方法在类中没有被定义，也是真实存在的。  
两个下划线  
__construct() 在创建对象时自动调用  
__destruct() 在销毁对象时自动调用  
__wakeup() unserialize()时会自动调用这个函数  
__sleep() serialize()时会自动调用这个函数

## 魔法函数调用范例

### 自动调用construct()函数

在下方创建$shop1 对象时，自动调用函数

    
    
    <?php
    
    class Shop{
    	public $name;
    	public $prince;
    	public $detail;
    	public function __construct(){  //调用对象时
    		
    		echo "fanxuliehua";
    		
    	}
    }
    $shop1 = new Shop();//创建对象
    $shop1->name="dress";
    $shop1->prince=12;
    $shop1->detail="haokan";
    ?>
    

结果图：  
![image.png](https://image.3001.net/images/20230726/1690359941_64c0d88560bd7ae7b5e25.png!small)

### 自动调用destruct()函数

在销毁对象时自动调用，将对象置为空即为销毁对象。

    
    
    <?php
    class Shop{
    	public $name;
    	public $prince;
    	public $detail;
    
    	public function __destruct(){  //销毁对象时
    		
    		echo "xiaohuile";
    	
    	}
    }
    $shop1 = new Shop();//创建对象
    $shop1->name="dress";
    $shop1->prince=12;
    $shop1->detail="haokan";
    $shop1 = null;  //销毁对象
    
    ?>
    

结果图：  
![image.png](https://image.3001.net/images/20230726/1690360095_64c0d91fcdd82571ceb89.png!small)

### 自动调用sleep()函数

serialize()时会自动调用这个函数

    
    
    <?php
    
    class Shop{
    	public $name;
    	public $prince;
    	public $detail;
    	public function __sleep(){  //序列化时
    		
    		echo "xuliehua";
    	
    	}
    }
    $shop1 = new Shop();//创建对象
    $shop1->name="dress";
    $shop1->prince=12;
    $shop1->detail="haokan";
    
    serialize($shop1);   //序列化
    
    ?>
    

结果图：  
![image.png](https://image.3001.net/images/20230726/1690360376_64c0da3893db87abd117d.png!small)

### 自动调用wakeup()函数

unserialize()时会自动调用这个函数

    
    
    <?php
    
    class Shop{
    	public $name;
    	public $prince;
    	public $detail;
    	public function __wakeup(){  //反序列化时
    		
    		echo "fanxuliehua";
    	
    	}
    
    }
    $shop1 = new Shop();//创建对象
    $shop1->name="dress";
    $shop1->prince=12;
    $shop1->detail="haokan";
    serialize($shop1);   //序列化
    
    unserialize(serialize($shop1));   //反序列化
    ?>
    

结果图：  
![image.png](https://image.3001.net/images/20230726/1690360254_64c0d9be95a2d1f886ca9.png!small)

感谢观看，欢迎提问。

