## escapeshellarg

 **escapeshellarg()** 将给字符串增加一个单引号，并且能引用或者转码任何已经存在的单引号

    
    
    escapeshellarg(string $arg): string
    

示例：

    
    
    echo escapeshellarg("hello 123");echo "\n";
    echo escapeshellarg("hello' 123");
    

输出：

    
    
    'hello 123'
    'hello'\'' 123'
    

## escapeshellcmd

 **escapeshellcmd()** 对字符串中可能会欺骗 shell
命令执行任意命令的字符进行转义，转义的字符包括：`&#;`|*?~<>^()[]{}$\`

和`\x0A`和`\xFF`。`'`和`"`仅在不配对儿的时候被转义

    
    
    escapeshellcmd(string $command): string
    

示例:

    
    
    echo escapeshellcmd("hello' 123");echo "\n";
    echo escapeshellcmd("hello'' 123");
    

输出：

    
    
    hello\' 123
    hello'' 123
    

## escapeshellarg和escapeshellcmd的分工

escapeshellarg 和 escapshellcmd 都是 php 提供用来防止注入命令的函数，二者分工不同，escapshellcmd
主要用来限制用户输入特殊符号执行其它命令，如下代码所示，只允许用户执行 find 的命令

    
    
    <?php
    system(escapeshellcmd('find '.$command));
    

escapeshellarg 会给字符包裹一对引号，是为了让用户的输入只能位于参数的位置，如下代码所示，限制用户只能输入 -name 选项的参数值

    
    
    <?php
    system('find ./ -name '.escapeshellarg($dir));
    

## escapeshellarg和escapeshellcmd混用

如果先用 escapeshellarg() 再用 escapeshellcmd() 过滤一段字符串：

    
    
    $a = "hello' 123";
    
    $b = escapeshellarg($a);
    echo $b;echo "\n";
    
    $c = escapeshellcmd($b);
    echo $c;
    

输出：

    
    
    'hello'\'' 123'
    'hello'\\'' 123\'
    

最后的字符串相当于是`'hello'`、`\\''`、`123\'`，这些在linux命令行中会拼接起来，最终的单引号也成功被闭合，后面可以随意注入新的语句了

但是如果是先用 **escapeshellcmd** 函数过滤,再用的 **escapeshellarg** 函数过滤,则没有这个问题

### 真实场景

虽然这种写法看着很傻，但总会有粗心的开发者有意无意的会用到这些写法。在 phpmailer 中就爆出过一个命令执行漏洞（
CVE-2016-10033），原因是 mail 函数的第 5 个参数可控时则可拼接 sendmail 命令造成任意文件写入rce

后面 phpmailer 在 5.2.18 做了一版修复代码如下，其中 $this->Sender 可控时会造成漏洞，官方想直接使用
escapeshellarg 命令过滤

    
    
    if (!empty($this->Sender) and $this->validateAddress($this->Sender)) {
        $params = sprintf('-f%s', escapeshellarg($this->Sender));
    }
    

可官方却忽略了 mail() 函数底层有一次 escapeshellcmd 过滤，从而造成了这次漏洞（CVE-2016-10045）

参考：

PHP escapeshellarg()+escapeshellcmd() 之殇：https://paper.seebug.org/164/

[谈谈escapeshellarg参数绕过和注入的问题](http://www.lmxspace.com/2018/07/16/%E8%B0%88%E8%B0%88escapeshellarg%E5%8F%82%E6%95%B0%E7%BB%95%E8%BF%87%E5%92%8C%E6%B3%A8%E5%85%A5%E7%9A%84%E9%97%AE%E9%A2%98/)

谈escapeshellarg绕过与参数注入漏洞：https://www.leavesongs.com/PENETRATION/escapeshellarg-and-parameter-injection.html

