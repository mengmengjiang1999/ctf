作者：SeaFood@知道创宇404实验室

#### 0x00 背景

近日，WordPress爆出了一个[SQLi漏洞](https://www.seebug.org/vuldb/ssvid-96376)，漏洞发生在WP的后台上传图片的位置，通过修改图片在数据库中的参数，以及利用php的`sprintf`函数的特性，在删除图片时，导致`'`单引号的逃逸。漏洞利用较为困难，但思路非常值得学习。

  

#### 0x01 漏洞分析

漏洞发生在 **wp-admin/upload.php** 的157行，进入删除功能，

![](https://images.seebug.org/content/images/2017/09/4611db6a-c357-4919-9141-4f670d2cced6.png-w331s)

之后进入函数`wp_delete_attachment( $post_id_del )`， **$post_id_del** 可控，而且没有做
**(int)** 格式转化处理。

**wp_delete_attachment** 位于`wp-includes\post.php`的 4863 行。其中

![](https://images.seebug.org/content/images/2017/09/2d70a62b-38ba-4a11-82e6-175abfcf3391.png-w331s)

图片的post_id被带入查询， **$wpdb- >prepare**中使用了 **sprintf** ，会做自动的类型转化，可以输入`22
payload`，会被转化为`22`，因而可以绕过。

之后进入4898行的`delete_metadata( 'post', null, '_thumbnail_id', $post_id, true
);`函数。

**delete_metadata** 函数位于`wp-includes\meta.php`的307行，

![](https://images.seebug.org/content/images/2017/09/72e360ee-34b9-4d24-95db-2a43646ab9f3.png-w331s)

在这里代码拼接出了如下sql语句， **meta_value** 为传入的 **media** 参数

    
    
    SELECT meta_id FROM wp_postmeta WHERE meta_key = '_thumbnail_id' AND meta_value = 'payload'

之后这条语句会进入查询，结果为真代码才能继续，所以要修改 **_thumbnail_id** 对应的 **meta_value**
的值为payload，保证有查询结果。

因此，我们需要上传一张图片，并在`写文章`中设置为 **特色图片** 。

在数据库的`wp_postmeta`表中可以看到，`_thumbnail_id`即是特色图片设定的值，对应的 **meta_value** 即图片的
**post_id** 。

![](https://images.seebug.org/content/images/2017/09/f0f60b44-45c7-4b42-8ab5-e05bd9bfab7e.png-w331s)

原文通过一个 WP<4.7.5 版本的xmlrpc漏洞修改`_thumbnail_id`对应 **meta_value**
的值，或通过插件`importer`修改。这里直接在数据库里修改，修改为我们的payload。

之后在365行，此处便是漏洞的核心，问题在于代码使用了两次`sprintf`拼接语句，导致可控的payload进入了第二次的`sprintf`。输入payload为`22
%1$%s hello`

![](https://images.seebug.org/content/images/2017/09/40115b6f-ad79-4a7e-8226-af242537e8a0.png-w331s)

代码会拼接出sql语句，带入 **$wpdb- >prepare**

    
    
    SELECT post_id FROM wp_postmeta WHERE meta_key = '%s'  AND meta_value = '22 %1$%s hello'

进入 **$wpdb- >prepare**后，代码会将所有`%s`转化为`'%s'`，即`meta_value = '22 %1$'%s' hello'`

![](https://images.seebug.org/content/images/2017/09/3322f77e-9138-4ad7-a076-24dbc32d89b2.png-w331s)

因为 **sprintf** 的问题 (vsprintf与sprintf类似)
，`'%s'`的前一个`'`会被吃掉，`%1$'%s`被格式化为_thumbnail_id ，最后格式化字符串出来的语句会变成

![](https://images.seebug.org/content/images/2017/09/c13416cb-8cd2-4ce0-8d33-9bd4ddc39a7e.png-w331s)

单引号成功逃逸！

最后payload为

    
    
    http://localhost/wp-admin/upload.php?action=delete&media[]=22%20%251%24%25s%20hello&_wpnonce=bbba5b9cd3

这个SQL注入不会报错，只能使用延时注入，而且需要后台的上传权限，所以利用起来比较困难。

  

#### 0x02 漏洞原理

上述WordPress的SQLi的核心问题在于在`sprintf`中，`'%s'`的前一个`'`被吃掉了，这里利用了`sprintf`的`padding`功能

![](https://images.seebug.org/content/images/2017/09/38f647be-ff4a-445d-a3ea-44e57b67256b.png-w331s)

单引号后的一个字符会作为padding填充字符串。

此外，`sprintf`函数可以使用下面这种写法

![](https://images.seebug.org/content/images/2017/09/e37fa61a-2bb3-4a56-adbd-c4b0c67669f2.png-w331s)

**%** 后的数字代表第几个参数， **$** 后代表类型。

所以，payload`%1$'%s'`中的`'%`被视为使用`%`进行 padding，导致了`'`的逃逸。

  

#### 0x03 php格式化字符串

但在测试过程中，还发现其他问题。php的`sprintf`或`vsprintf`函数对格式化的字符类型没做检查。

如下代码是可以执行的，显然php格式化字符串中并不存在`%y`类型，但php不会报错，也不会输出`%y`，而是输出为空

    
    
    <?php
    $query = "%y";
    $args = 'b';
    echo sprintf( $query, $args ) ;
    ?>

通过fuzz得知，在php的格式化字符串中，%后的一个字符(除了`'%'`)会被当作字符类型，而被吃掉，单引号`'`，斜杠`\`也不例外。

如果能提前将`%' and 1=1#`拼接入sql语句，若存在SQLi过滤，单引号会被转义成`\'`

    
    
    select * from user where username = '%\' and 1=1#';

然后这句sql语句如果继续进入格式化字符串，`\`会被`%`吃掉，`'`成功逃逸

    
    
    <?php
    $sql = "select * from user where username = '%\' and 1=1#';";
    $args = "admin";
    echo sprintf( $sql, $args ) ;
    //result: select * from user where username = '' and 1=1#'
    ?>

不过这样容易遇到`PHP Warning: sprintf(): Too few arguments`的报错。

还可以使用`%1$`吃掉后面的斜杠，而不引起报错。

    
    
    <?php
    $sql = "select * from user where username = '%1$\' and 1=1#' and password='%s';";
    $args = "admin";
    echo sprintf( $sql, $args) ;
    //result: select * from user where username = '' and 1=1#' and password='admin';
    ?>

通过翻阅php的[源码](https://github.com/php/php-src/blob/master/ext/standard/formatted_print.c)，在`ext/standard/formatted_print.c`的642行

![](https://images.seebug.org/content/images/2017/09/27b6c5a1-14ac-45f4-b8b0-7365fc317b1e.png-w331s)

可以发现php的`sprintf`是使用switch..case..实现，对于未知的类型`default`，php未做任何处理，直接跳过，所以导致了这个问题。

在[高级php代码审核技术](https://github.com/80vul/pasc2at)中的5.3.5中，提及过使用`$order_sn=substr($_GET["order_sn"],
1)`截断吃掉`\`或`"`。

之前也有过利用[iconv](https://www.leavesongs.com/PENETRATION/mutibyte-sql-inject.html)转化字符编码，`iconv('utf-8', 'gbk',
$_GET['word'])`因为utf-8和gbk的长度不同而吃掉`\`。

几者的问题同样出现在字符串的处理，可以导致`'`的转义失败或其他问题，可以想到其他字符串处理函数可能存在类似的问题，值得去继续发掘。

  

#### 0x04 利用条件

  1. 执行语句使用`sprintf`或`vsrptinf`进行拼接

  2. 执行语句进行了两次拼接，第一次拼接的参数内容可控，类似如下代码

    
    
    <?php
    
    $input = addslashes("%1$' and 1=1#");
    $b = sprintf("AND b='%s'", $input);
    ...
    $sql = sprintf("SELECT * FROM t WHERE a='%s' $b", 'admin');
    echo $sql;
    //result: SELECT * FROM t WHERE a='admin' AND b=' ' and 1=1#'

  

#### 0x05 总结

此次漏洞的核心还是`sprintf`的问题，同一语句的两次拼接，意味着可控的内容被带进了格式化字符串，又因为`sprintf`函数的处理问题，最终导致漏洞的发生。

此问题可能仍会出现在WordPress的插件，原文的评论中也有人提到曾在Joomla中发现过类似的问题。而其他使用`sprintf`进行字符串拼接的cms，同样可能因此导致SQL注入和代码执行等漏洞。

  

#### 0x06 参考链接

<https://medium.com/websec/wordpress-sqli-bbb2afcc8e94>

<https://medium.com/websec/wordpress-sqli-poc-f1827c20bf8e>

<http://php.net/manual/zh/function.sprintf.php>

<https://github.com/php/php-src/blob/c8aa6f3a9a3d2c114d0c5e0c9fdd0a465dbb54a5/ext/standard/formatted_print.c>

<https://www.seebug.org/vuldb/ssvid-96376>

  

**\------------------------------------2017.11.01
更新------------------------------------**

  

#### 0x07 WordPress 4.8.2补丁问题

国外安全研究人员[Anthony Ferrara](https://blog.ircmaxell.com/2017/10/disclosure-wordpress-wpdb-sql-injection-technical.html)给出了另一种此漏洞的利用方式，并指出了WordPress
4.8.2补丁存在的问题。

如下代码

    
    
    <?php
    
    $input1 = '%1$c) OR 1 = 1 /*';
    $input2 = 39;
    $sql = "SELECT * FROM foo WHERE bar IN ('$input1') AND baz = %s";
    $sql = sprintf($sql, $input2);
    echo $sql;
    //result: SELECT * FROM foo WHERE bar IN ('') OR 1 = 1 /*') AND baz = 39

`%c`起到了类似`chr()`的效果，将数字39转化为`'`，从而导致了sql注入。

对此，WordPress 4.8.2补丁在`WPDB::prepare()`中加入

    
    
    $query = preg_replace( '/%(?:%|$|([^dsF]))/', '%%\\1', $query );

从而，禁用了除`%d`，`%s`，`%F`之外的格式，这种方法导致了三个问题。

1.大量开发者在开发过程中使用了例如`%1$s`的格式，此次补丁导致代码出错。

2.在例如以下代码中

    
    
       $db->prepare("SELECT * FROM foo WHERE name= '%4s' AND user_id = %d", $_GET['name'], get_current_user_id());

`%4s`会被替换成`%%4s`
，`%%`在sprintf中代表字符`%`，没有格式化功能。所以，`$_GET['name']`会被写到`%d`处，攻击者可以控制user
id，可能导致越权问题的出现。

3.补丁可以被绕过

在`meta.php`的漏洞处

    
    
       if ( $delete_all ) {
         $value_clause = '';
         if ( '' !== $meta_value && null !== $meta_value && false !== $meta_value ) {
           $value_clause = $wpdb->prepare( " AND meta_value = %s", $meta_value );
         }
         $object_ids = $wpdb->get_col( $wpdb->prepare( "SELECT $type_column FROM $table WHERE meta_key = %s $value_clause", $meta_key ) );
       }

如果输入

    
    
       $meta_value = ' %s ';
       $meta_key = ['dump', ' OR 1=1 /*'];

之后两次进入`prepare()`，因为

    
    
       $query = preg_replace( '|(?<!%)%s|', "'%s'", $query ); 

使得`%s`变为`''%s''`

最后结果

    
    
       SELECT type FROM table WHERE meta_key = 'dump' AND meta_value = '' OR 1=1 /*''

WordPress也承认这是一个[错误的修复](https://core.trac.wordpress.org/ticket/41925)。

  

在WordPress
4.8.3的补丁中，一是修改了`meta.php`中两次使用`prepare()`的问题，二是使用随机生成的[占位符](https://make.wordpress.org/core/2017/10/31/changed-behaviour-of-esc_sql-in-wordpress-4-8-3/)替换`%`，在进入数据库前再替换回来。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/386/>

