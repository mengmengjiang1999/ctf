## SQL注入常识

### sql注入原理：

sql注入是服务器对于url无条件的信任读取，导致mysql读取url中的危险sql语句，进而将数据库信息返回到页面上。

### sql注入类型：

数字类型、字符类型

### sql注入手法：

  * 报错注入
  * 布尔盲注
  * 延时注入
  * union联合查询语句

### sql注入想要获取webshell需要哪些条件：

  * 权限是否为root权限
  * 是否知道webshell存放的绝对路径
  * my.ini配置文件中是否有secure_file_priv=

### 如何防御sql注入：

  * 过滤特殊字符

  1. 利用str_replace()函数定义select和union特殊字符为黑名单，当检测到有这些特殊字符时，会将其替换成空格，或者小数点。（若替换空格，可能会有大小写，双写绕过；小数点的话，则会避免这些绕过）；
  2. 将特殊字符 ‘ ’‘ （单引号/双引号）利用preg_replace()函数替换为空，不使特殊字符打乱原sql语句

使用mysqli_real_escape_strin函数进行参数化查询，转义字符。

  * 采用参数查询

数据库服务器不会将参数的内容视为SQL指令的一部份来处理，而是在数据库完成 SQL
指令的编译后，才套用参数运行，因此就算参数中含有恶意的指令，由于已经编译完成，就不会被数据库所运行。

## 演示注入方法

### 尝试报错注入

updatexml()更新xml文档的函数

语法updatexml(目标xml文档，xml路径，更新的内容)

第二个参数 xml中的位置是可操作的地方,如果我们写入其他格式，就会报错，并且会返回我们写入的非法格式内容，而这个非法的内容就是我们想要查询的内容。

    
    
    ?id=3'  and updatexml(1,concat(0x7e,(select database()),0x7e),1) --+
    

![image-20230614175137165.png](https://image.3001.net/images/20230719/1689772933_64b7e385cd2cc5735124c.png!small)

### 演示布尔盲注

通过猜测数据库名字的长度，然后与语句来判断是否可以成功输出

下图就是，如果长度不等于7，则为错误，即在页面上错误输出，当猜到length=8时，显示正确，则页面上正常输出，则表示数据库名字长度等于8  
![image-20230614191757014.png](https://image.3001.net/images/20230719/1689772982_64b7e3b61f5132c4c4d77.png!small)

    
    
    ?id=1' and length(database())=8--+
    

![image-20230614191929986.png](https://image.3001.net/images/20230719/1689773044_64b7e3f477bf35dc018a4.png!small)  
substr():截取字符串的内容

ascii: ASCII码  
![image-20230614192123560.png](https://image.3001.net/images/20230719/1689773080_64b7e418a836550bd8952.png!small)  
下图，语句的意思为 截取从数据库名第一个字符开始的第一个字符，为115，对应着ASCII码就是s，就这样一个个猜数据。

    
    
    ?id=3' and if(length(database())=8,sleep(5),1)--+
    

![image-20230614192136573.png](https://image.3001.net/images/20230719/1689773117_64b7e43d28bacefd77905.png!small)

### 尝试延时注入

当一个页面，无论输入什么时，都不出现报错页面，这时就需要使用延时注入。延时注入的思想就是使得程序运行慢几秒，通过看页面是否加载来判断语句是否正确。

    
    
    ?id=3' and if(length(database())=8,sleep(5),1)--+
    

![image-20230614201928197.png](https://image.3001.net/images/20230719/1689773178_64b7e47a8a0029f94ab43.png!small)

## sqlmap工具详解

### 列出所有库名

![image-20230614222526429.png](https://image.3001.net/images/20230719/1689773340_64b7e51cc5a7fd7388748.png!small)  
![image-20230614222643470.png](https://image.3001.net/images/20230719/1689773358_64b7e52e14c7d483d2280.png!small)

### 列出security数据库下的表

![image-20230614222908878.png](https://image.3001.net/images/20230719/1689773395_64b7e553802c86b739cd7.png!small)  
![image-20230614222948020.png](https://image.3001.net/images/20230719/1689773406_64b7e55e8898e59b7fdde.png!small)

### 列出users表下的字段

![image-20230614223052860.png](https://image.3001.net/images/20230719/1689773439_64b7e57f8158f7e0a0937.png!small)  
![image-20230614223104405.png](https://image.3001.net/images/20230719/1689773448_64b7e5886bbf2d989f045.png!small)

### 列出指定字段的内容

![image-20230614223221783.png](https://image.3001.net/images/20230719/1689773471_64b7e59f9317a15d0dc7c.png!small)  
![image-20230614223233453.png](https://image.3001.net/images/20230719/1689773481_64b7e5a941dc934b76a2a.png!small)

### sqlmap挂代理

\--proxy 代理 利用代理地址进行访问，防止ip被封

    
    
    sqlmap -r 1.txt --dbs -level=3 -risk=3 --batch -p "id" --proxy http://127.0.0.1:8080
    

![image-20230614225210821.png](https://image.3001.net/images/20230719/1689773567_64b7e5ffcda16d89518bb.png!small)  
![image-20230614224808423.png](https://image.3001.net/images/20230719/1689773578_64b7e60ae8b53f968105d.png!small)  
![image-20230614224738710.png](https://image.3001.net/images/20230719/1689773588_64b7e6146b1af6094c86a.png!small)

