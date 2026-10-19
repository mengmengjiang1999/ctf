作者：xd_xd  
作者博客：<http://xdxd.love/>

#### solveme.peng.kr winter sleep

solveme是一个CTF的练习平台，其中winter sleep题目是这样的。

    
    
    <?php
       error_reporting(0);
       require __DIR__.'/lib.php';
       if(isset($_GET['time'])){
           if(!is_numeric($_GET['time'])){
               echo 'The time must be number.';
           }else if($_GET['time'] < 60 * 60 * 24 * 30 * 2){
               echo 'This time is too short.';
           }else if($_GET['time'] > 60 * 60 * 24 * 30 * 3){
               echo 'This time is too long.';
           }else{
               sleep((int)$_GET['time']);
               echo $flag;
           }
           echo '<hr>';
       }
       highlight_file(__FILE__);

输入一个字符串，通过is_numric的判断，要大于5184000小于777600，最后通过sleep函数，就可以输出flag。显然，如果输入一个较大的数，会sleep很长时间。需要一个数大于5184000，然后int之后又要是一个很小的数。

解决的方案是这样的：

    
    
    <?php
    echo 60 * 60 * 24 * 30 * 2;
    echo "\n";
    echo 6e6;
    echo "\n";
    echo (int)'6e6';
    echo "\n";
    echo 60 * 60 * 24 * 30 * 3;

可以看以上脚本输出内容:

    
    
    5184000
    6000000
    6
    7776000

使用科学计数法。

看了一些writeup，只是给出了解决的办法，但是并没有详细的说明，为什么会这样。有的地方提到说是弱类型，虽然这几次比较存在类型的自动转换，但是跟我理解的弱类型的自动转换存在差异。所以想要探究一番。

#### 黑盒测试

![](https://images.seebug.org/content/images/2018/04/d7f92fe4-ae9d-4a12-a040-173c1431a2bd.png-w331s)

可以看到当接收到科学计数法表示的字符串跟一个整型变量运算(‘6e6’-0)，6e6自动并不是自动转换成了int型，而是转换成了float，所以最终的数字是float型的6000000。最后两行代码可以直接的说明了问题。使用int强制转换一个科学计数法表示的字符串，转换过程中并不能识别科学计数法，只是把e当做普通字符了。效果跟6a6是一样的。而用float转成浮点数，则可以成功识别科学计数法。

![](https://images.seebug.org/content/images/2018/04/caed1c1a-9236-4343-873f-5ff20b2d7dc2.png-w331s)

#### feature or bug

我的感觉是这应该是php的一个bug。同一个字符串，转换成int型和float型有着两种解释。正常的逻辑应该是(int)’6e6’ =
(int)(float)’6e6’。这样才比较符合正常的一个理解逻辑。

找了几个php的版本，分别做了下测试：

测试脚本如下：

    
    
    import docker
    client = docker.from_env()
    
    
    php_versions = ['5.3','5.4','5.5','5.6', '7.0','7.1','7.2']
    for version in(php_versions):
    php = "php:"+version + "-cli"
    
    print(php)
    print("echo((int)'6e6')")
    print(client.containers.run("php:"+version+"-cli", '''php -r "echo((int)'6e6');"'''))
    print("echo((float)'6e6')")
    print(client.containers.run("php:"+version+"-cli", '''php -r "echo((float)'6e6');"''’))

结果如下：

    
    
    ➜  dockerpy python phptest.py
    php:5.3-cli
    echo((int)'6e6')
    6
    echo((float)'6e6')
    6000000
    php:5.4-cli
    echo((int)'6e6')
    6
    echo((float)'6e6')
    6000000
    php:5.5-cli
    echo((int)'6e6')
    6
    echo((float)'6e6')
    6000000
    php:5.6-cli
    echo((int)'6e6')
    6
    echo((float)'6e6')
    6000000
    php:7.0-cli
    echo((int)'6e6')
    6
    echo((float)'6e6')
    6000000
    php:7.1-cli
    echo((int)'6e6')
    6000000
    echo((float)'6e6')
    6000000
    php:7.2-cli
    echo((int)'6e6')
    6000000
    echo((float)'6e6')
    6000000

在php7.0以前的版本中(int)’6e6’结果是6，但是在7.1以后的版本中，(int)’6e6’已经是6000000，符合(int)’6e6’ =
(int)(float)’6e6’这个逻辑了。

#### php内核分析

以下内容引用自《php7内核剖析》：

PHP是弱类型语言，不需要明确的定义变量的类型，变量的类型根据使用时的上下文所决定，也就是变量会根据不同表达式所需要的类型自动转换，比如求和，PHP会将两个相加的值转为long、double再进行加和。每种类型转为另外一种类型都有固定的规则，当某个操作发现类型不符时就会按照这个规则进行转换，这个规则正是弱类型实现的基础。
除了自动类型转换，PHP还提供了一种强制的转换方式:

  * (int)/(integer)：转换为整形 integer
  * (bool)/(boolean)：转换为布尔类型 boolean
  * (float)/(double)/(real)：转换为浮点型 float
  * (string)：转换为字符串 string
  * (array)：转换为数组 array
  * (object)：转换为对象 object
  * (unset)：转换为 NULL

无论是自动类型转换还是强制类型转换，不是每种类型都可以转为任意其他类型。

4.1.3 转换为整型

其它类型转为整形的转换规则：

  * NULL：转为0
  * 布尔型：false转为0，true转为1
  * 浮点型：向下取整，比如：(int)2.8 => 2
  * 字符串：就是C语言strtoll()的规则，如果字符串以合法的数值开始，则使用该数值，否则其值为 0（零），合法数值由可选的正负号，后面跟着一个或多个数字（可能有小数点），再跟着可选的指数部分
  * 数组：很多操作不支持将一个数组自动整形处理，比如：array() + 2，将报error错误，但可以强制把数组转为整形，非空数组转为1，空数组转为0，没有其他值
  * 对象：与数组类似，很多操作也不支持将对象自动转为整形，但有些操作只会抛一个warning警告，还是会把对象转为1操作的，这个需要看不同操作的处理情况
  * 资源：转为分配给这个资源的唯一编号

具体处理：

ZEND_API zend_long ZEND_FASTCALL _zval_get_long_func(zval *op) { try_again:

    
    
    switch (Z_TYPE_P(op)) {
        case IS_NULL:
        case IS_FALSE:
            return 0;
        case IS_TRUE:
            return 1;
        case IS_RESOURCE:
            //资源将转为zend_resource->handler
            return Z_RES_HANDLE_P(op);
        case IS_LONG:
            return Z_LVAL_P(op);
        case IS_DOUBLE:
            return zend_dval_to_lval(Z_DVAL_P(op));
        case IS_STRING:
            //字符串的转换调用C语言的strtoll()处理
            return ZEND_STRTOL(Z_STRVAL_P(op), NULL, 10);
        case IS_ARRAY:
            //根据数组是否为空转为0,1
            return zend_hash_num_elements(Z_ARRVAL_P(op)) ? 1 : 0;
        case IS_OBJECT:
            {  
                zval dst;
                convert_object_to_type(op, &dst, IS_LONG, convert_to_long);
                if (Z_TYPE(dst) == IS_LONG) {
                    return Z_LVAL(dst);
                } else {
                    //默认情况就是1
                    return 1;
                }
            }
        case IS_REFERENCE:
            op = Z_REFVAL_P(op);
            goto try_again;
            EMPTY_SWITCH_DEFAULT_CASE()
    }
    return 0;
    }

4.1.4 转换为浮点型

除字符串类型外，其它类型转换规则与整形基本一致，就是整形转换结果加了一位小数，字符串转为浮点数由zend_strtod()完成，这个函数非常长，定义在zend_strtod.c中，这里不作说明。

书中提到，字符串转换为整型，是C语言strtol()的规则，由ZEND_STRTOL函数完成的，字符串转换成浮点数，是用zend_strtod函数完成的。

对比一下C语言的strtol和strtod

![](https://images.seebug.org/content/images/2018/04/98e1819d-e445-4b99-a79c-a58d2319e76b.png-w331s)
![](https://images.seebug.org/content/images/2018/04/d3f428a0-43b5-4db2-997a-0076865f6a95.png-w331s)

strtol不能识别科学计数法，字符串6e6转成整型是6，而strtod可以识别科学计数法，6e6转成浮点数是6000000。

#### 动态调试php内核

#### 编译debug版php。

    
    
    git clone http://git.php.net/repository/php-src.git
    cd php-src
    git checkout PHP-7.0
    ./buildconf
    ./configure --disable-all --enable-debug --prefix=$HOME/myphp
    make
    make install

#### gdb调试

    
    
    gdb --args php -r "echo((int)'6e6');”

在类型转换函数上下断点：

    
    
    b _zval_get_long_func

![](https://images.seebug.org/content/images/2018/04/0b39e82c-1d67-4593-ac98-7333be7103d4.png-w331s)

可以看到使用zend_strtol函数进行转换。

![](https://images.seebug.org/content/images/2018/04/7cc8034d-bcf1-4798-89f9-5ddf97ddc180.png-w331s)

zent_strtol 直接是使用strtoll。

调试一下7.1版本php

![](https://images.seebug.org/content/images/2018/04/96507009-d407-41ae-bd80-e3baed3d87b4.png-w331s)

可以看到7.1版中使用了新的函数is_numeric_string替代strtoll。注释中说明使用新函数是为了避免strtoll的溢出问题，自己实现了is_number_string函数来替代strtoll。然而并没有提到科学计数法表示的字符串的问题。但是实际实现上跟strtoll有不同。妥善的处理科学计数法表示的数字。

![](https://images.seebug.org/content/images/2018/04/55c9813a-3c76-4b0b-97e2-0fb62b0f89b9.png-w331s)

最终的字符串转整型的逻辑如下：

![](https://images.seebug.org/content/images/2018/04/6e5c723e-a21a-47cc-b8e5-710ff772640d.png-w331s)

最终的处理逻辑是如果发现了小数点或者数字e，就采用zend_strtod来处理，这样就跟字符串转浮点数是一模一样的处理逻辑了。所以最终的结果也就符合了(int)’6e6’
= (int)(float)’6e6’这个逻辑。

#### 思考

那么这到底是个bug还是feature呢。最终的结果来看，php7.0及以前的版本使用strtoll转字符串到整型，7.1以后的版本使用了strtod来转换。所以strtoll不能识别科学计数法表示的数字是不是一个bug。

#### 参考资料

  * solveme.peng.kr的中文writeup:<http://www.freebuf.com/articles/web/165537.html>
  * php源码调试的文章:<https://gywbd.github.io/posts/2016/2/debug-php-source-code.html>
  * php7内核分析：<https://github.com/pangudashu/php7-internal>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/566/>

