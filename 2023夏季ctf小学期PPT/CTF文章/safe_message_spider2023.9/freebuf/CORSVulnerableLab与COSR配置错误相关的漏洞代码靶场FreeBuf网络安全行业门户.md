**此存储库包含与CORS配置错误相关的易受攻击代码。你可以在本地机器上配置易受攻击的代码，以实际利用与CORS相关的错误配置问题。**

在此，我想首先感谢@albinowax，AKReddy，Vivek Sir，Andrew Sir和@vanderaj对该项目的支持以及对我的鼓励！

![lab_login.png](https://image.3001.net/images/20190728/1564278605_5d3cff4db701e.png!small)

## 实验环境设置

以下是在本地/远程机器上配置易受攻击代码的必要条件：

> Apache web server
>
> PHP 5/7
>
> MySQL Database

### 配置步骤：

1.下载并解压缩Web服务器的“htdocs”或webroot目录中的代码。

2.打开PHPMyAdmin并创建名为“ica_lab”的新数据库。

3.如果你想使用MySQL“root”用户帐户，请跳过以下步骤直接到第5步。

4.通过执行以下SQL命令，创建一个名为“billu”的新用户：

    
    
    grant all on ica_lab.* to billu@localhost IDENTIFIED BY 'b0x_billu';

5.在文本编辑器中打开“c0nnection.php”，并在PHP中进行如下更改：

    
    
    change 
    $conn = mysqli_connect("127.0.0.1","billu","b0x_billu","ica_lab");
      to
    $conn = mysqli_connect("127.0.0.1","root","","ica_lab");

6.在PHPMyAdmin中，选择“database”，然后单击数据库名称“ica_lab”。

7.单击“Import”按钮，然后在本地计算机上浏览找到SQL转储文件“ica_lab.sql”。该文件位于存储库目录“database”中。

8.找到SQL数据库文件后，单击“Go”按钮。现在，数据库已准备就绪。

9.访问“CORS Vulnerable Lab”应用。

10.登录凭证已在输入字段中指定，只需单击“Let Me In”按钮即可。

## 靶场中的可用挑战

该实验环境中共模拟了3种错误配置。

![lab.png](https://image.3001.net/images/20190728/1564278623_5d3cff5f50f87.png!small)

### 应用程序信任任意来源

应用程序接受来自任意Origin的CORS请求。代码将“Origin”值放置在HTTP响应头“Access-Control-Allow-Origin”中。现在，此配置将允许来自任意“Origin”的任意脚本向应用发出CORS请求。Web浏览器将执行标准的CORS请求检查，而来自恶意域的脚本将能够窃取数据。

### 应用程序错误的“正则表达式”实现检查可信来源

应用程序已实施CORS策略，并对列入白名单的域/子域执行“正则表达式”检查。在这种情况下，应用程序在代码中实现了一个弱正则表达式，该代码仅检查在HTTP请求“Origin”头中的任意位置是否存在“b0x.com”域。如果HTTP头“Origin”的值为“inb0x.com”或b0x.comlab.com，则正则表达式会将其标记为pass。这种错误配置将导致跨域共享数据。

### 应用程序信任 Origin 头中指定 null 值

在此场景中，应用程序HTTP响应头“Access-Control-Allow-Origin”始终设置为“null”。当用户指定除null值以外的任意值时，应用程序将不会处理它，并在HTTP响应中保持“null”。很少有技巧允许攻击者执行攻击，并且可以使用CORS请求过滤受害者的数据。

##  **示例**

### 应用程序信任任意来源

应用程序接受“Origin”头中指定的任意值。

![1.png](https://image.3001.net/images/20190728/1564278647_5d3cff77805c7.png!small)

### 应用程序错误的“正则表达式”实现检查可信来源

应用程序信任白名单列表中的Origin。

![2.png](https://image.3001.net/images/20190728/1564278658_5d3cff82142a4.png!small)

应用程序不允许任何任意Origin。

![3.png](https://image.3001.net/images/20190728/1564278668_5d3cff8cdfdba.png!small)

在域名启动时应用弱正则表达式允许具有白名单域名字符串的Origin。

![4.png](https://image.3001.net/images/20190728/1564278679_5d3cff97d5501.png!small)

在域名末尾应用弱正则表达式允许具有白名单域名字符串的Origin。

![5.png](https://image.3001.net/images/20190728/1564278691_5d3cffa348422.png!small)

### 应用程序信任 Origin 头中指定 null 值

应用程序接受“Origin”头中指定的“null”值。

![6.png](https://image.3001.net/images/20190728/1564278702_5d3cffae75e38.png!small)

应用程序不接受除“null”“Origin”之外的任意值。

**![7.png](https://image.3001.net/images/20190728/1564278709_5d3cffb50593b.png!small)**

 ***参考来源：[GitHub](https://github.com/incredibleindishell/CORS-vulnerable-Lab)，FB小编secist编译，转载请注明来自FreeBuf.COM**

