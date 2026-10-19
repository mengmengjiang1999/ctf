## 前言

本章主要是对php代码进行代码审计，针对DVWA靶场的Command Injection 进行high、impossible难度进行分析。

## high

##### 查看代码

![image.png](https://image.3001.net/images/20230708/1688783382_64a8ca1618155dd52e1df.png!small)

### 函数解析

  1. *isset — 检测变量是否已声明并且其值不为 null
  2. stristr — strstr() 函数的忽略大小写版本。将前后两个字符串进行对比，若在操作系统名称中找到了'Windows NT',那么函数返回匹配的字符串所在位置的后面的字符串，不匹配则返回false。详情：https://vimsky.com/examples/usage/php-stristr-function.html
  3. php_uname()，该函数返回当前服务器的操作系统名称和版本号。

  * ‘a’ or ‘s’: 返回全部系统信息（包括操作系统名称和版本号、主机名、内核版本等）
  * ‘n’: 返回主机名
  * ‘r’: 返回内核版本号
  * ‘s’: 返回操作系统名称
  * ‘v’: 返回操作系统版本号

  4. str_replace是一个PHP函数，用于将字符串中的指定字符或字符串替换为另一个字符或字符串。它接受三个参数：需要替换的字符或字符串、替换为的字符或字符串、以及源字符串。
  5. 当一个变量指着一个数组时，这个变量输出的值为数组的value值，不输出key值（key只是索引，真正的值为value）  
array_keys() 返回数组中每个元素的索引或键。  
trim（）函数移除字符串两侧的空白字符或其他预定义字符。

### 代码分析

    
    
    <?php
    //判断POST传参是否传值
    if( isset( $_POST[ 'Submit' ]  ) ) {
        //POST传参已传值，用trim函数定义输入的ip值，再将其赋值给变量$target
        $target = trim($_REQUEST[ 'ip' ]);
    
        // 定义一个array数组
        $substitutions = array(
            '&'  => '',
            ';'  => '',
            '| ' => '',
            '-'  => '',
            '$'  => '',
            '('  => '',
            ')'  => '',
            '`'  => '',
            '||' => '',
        );
    
        // 替换变量target中的值，将含有array数组中索引的字符串替换成array数组中的value值。此时也就是过滤特殊字符，并将他们为空
        $target = str_replace( array_keys( $substitutions ), $substitutions, $target );
    
        // php_uname()返回当前系统名版本，stristr匹配字符串，意思就是将当前系统版本和windows NT进行字符串对比，若相同即若为windows版本则输出。
        if( stristr( php_uname( 's' ), 'Windows NT' ) ) {
            // shell_exec()只输出命令执行结果。输出ping ip 的结果；
            // windows 默认有ping的次数，所以直接ping就行
            // 小数点为字符串拼接符
            // 将输出的结果赋值给变量$cmd
            $cmd = shell_exec( 'ping  ' . $target );
        }
        else {
            // 若为linux系统，若不配置 -c 4，则一直ping，则需要设置-c 4
            $cmd = shell_exec( 'ping  -c 4 ' . $target );
        }
    
        // 输出执行的结果
        echo "<pre>{$cmd}</pre>";
    }
    

## impossible

### 查看代码

![image.png](https://image.3001.net/images/20230708/1688800550_64a90d2618f7cff753165.png!small)

### 函数解析

  1. checkToken() 不是 PHP 内置函数，它是一个自定义函数。通常情况下，checkToken() 函数用于验证表单提交或 URL 请求中的 CSRF（跨站请求伪造）令牌，以确保请求是合法的。CSRF 攻击是一种常见的 Web 安全威胁，攻击者通过在受害者浏览器中注入恶意代码，来模拟用户的请求，从而执行未经授权的操作。
  2. stripslashes() 函数用于删除由 addslashes() 函数添加的反斜杠。在 PHP 中，如果我们要将某些数据存储到数据库中，需要对特殊字符进行转义，以防止 SQL 注入攻击。addslashes() 函数就是用来对字符串中的特殊字符进行转义，并在每个特殊字符前添加一个反斜杠。而 stripslashes() 函数则是用来删除这些反斜杠的，使得字符串恢复成原来的形式。通常情况下，在从数据库中读取数据并在页面上显示之前，需要使用 stripslashes() 函数将数据中的反斜杠删除，以便正常显示。
  3. generateSessionToken() 是一个自定义函数，用于生成一个随机的会话令牌。在 web 应用程序中，会话令牌是一种用于识别用户身份和验证用户请求的机制。当用户登录后，服务器会为其创建一个唯一的会话 ID，并将其存储在一个称为 session cookie 的小文件中，发送给用户的浏览器。每次用户发起请求时，浏览器都会将 session cookie 发送回服务器，以便服务器可以识别用户并验证其请求。为了防止会话劫持攻击，会话 ID 必须是随机的、不可预测的和唯一的。  
因此，generateSessionToken()
函数就是用来生成这样的会话令牌的。它通常使用随机数生成算法来生成一个字符串，该字符串包含字母、数字和特殊字符，长度一般为 32
个字符或更长。在生成会话令牌时，需要确保其足够随机、安全且不易被猜测。

  4. explode(): 使用一个字符串分割另一个字符串。
  5. is_numeric( ): 检测变量是否为数字或数字字符串
  6. sizeof（）:count()的别名，统计数组、Countable对象中所有元素的数量

### 代码分析

    
    
    <?php
    
        //判断POST传参是否传值
    if( isset( $_POST[ 'Submit' ]  ) ) {
       //验证表单提交的 CSRF（跨站请求伪造）令牌，确保请求合法。
        checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );
    
       //POST传参已传值，用trim函数定义输入的ip值，再将其赋值给变量$target
        $target = $_REQUEST[ 'ip' ];
        //将变量target中的反斜杠删除，以便正常显示，配合addslashes() 函数使用，可以理解为转义特殊字符。
        $target = stripslashes( $target );
    
        //将变量$target 拆分为4个八位字节
        $octet = explode( ".", $target );
    
       //用is_numeric函数检查每个八位字节是否为数字，且拆分后的target变量是否由4个八位字节组成
        if( ( is_numeric( $octet[0] ) ) && ( is_numeric( $octet[1] ) ) && ( is_numeric( $octet[2] ) ) && ( is_numeric( $octet[3] ) ) && ( sizeof( $octet ) == 4 ) ) {
    
           // 将拆分后的4个八位字节拼接为IP。
            $target = $octet[0] . '.' . $octet[1] . '.' . $octet[2] . '.' . $octet[3];
    
            // Determine OS and execute the ping command.
            if( stristr( php_uname( 's' ), 'Windows NT' ) ) {
                // php_uname()返回当前系统名版本，stristr匹配字符串，意思就是将当前系统版本和windows NT进行字符串对比，若相同即若为windows版本则输出。
                $cmd = shell_exec( 'ping  ' . $target );
            }
            else {
                // linux系统
                $cmd = shell_exec( 'ping  -c 4 ' . $target );
            }
    
              // 输出执行的结果
            echo "<pre>{$cmd}</pre>";
        }
        else {
              //  如果分割出来的任意八位字符部位非数字，则输出错误信息
            echo '<pre>ERROR: You have entered an invalid IP.</pre>';
        }
    }
    
    // 生成会话令牌
    generateSessionToken();
    
    ?>
    

