打开靶机，使用nmap进行网段扫描：

![](https://image.3001.net/images/20230713/1689238896_64afbd70efb9af9884696.png!small)​

排除主机和kali IP，锁定靶机IP：192.168.38.141：

![](https://image.3001.net/images/20230713/1689238897_64afbd719c6868dcb5885.png!small)

接下来进行端口扫描：

![](https://image.3001.net/images/20230713/1689238898_64afbd7253c6011d923e2.png!small)

扫描服务详细信息：

![](https://image.3001.net/images/20230713/1689238898_64afbd72e5ece17c1c674.png!small)

这里扫到内容管理系统，网站也扫出来了：http-generator: Drupal 7 (http://drupal.org)

之后可以使用whatweb进行指纹识别，识别CMS等系统：

![](https://image.3001.net/images/20230713/1689238899_64afbd73be2c6475b0072.png!small)

接下来找找CMS（内容管理系统）系统漏洞：

![](https://image.3001.net/images/20230713/1689238900_64afbd748e24f699b0bd3.png!small)

使用第四个，进行设置：

![](https://image.3001.net/images/20230713/1689238901_64afbd7581195792b0242.png!small)

可以看到这里有个flag1，进行查看：

![](https://image.3001.net/images/20230713/1689238902_64afbd7697d23f47b283f.png!small)

这里有个提示：

![](https://image.3001.net/images/20230713/1689238903_64afbd7778ee4eb79b22b.png!small)

没一个CMS都需要一个配置文件，即Drypal7的配置文件：setting.php:

![](https://image.3001.net/images/20230713/1689238904_64afbd78376d6d9f679be.png!small)

/**  
*  
* flag2  
* Brute force and dictionary attacks aren't the  
* only ways to gain access (and you WILL need access).  
* What can you do with these credentials?  
*  
*/  
  
$databases = array (  
'default' =>  
array (  
'default' =>  
array (  
'database' => 'drupaldb',  
'username' => 'dbuser',  
'password' => 'R0ck3t',  
'host' => 'localhost',  
'port' => '',  
'driver' => 'mysql',  
'prefix' => '',  
),  
),  
);

比较重要的就是这俩个，根据信息登录数据库：

![](https://image.3001.net/images/20230713/1689238905_64afbd790cc6cb019851b.png!small)

查看数据库，根据之前看到的信息，选择：

![](https://image.3001.net/images/20230713/1689238905_64afbd79b4ec757fbbb89.png!small)

接下来查询users表：

![](https://image.3001.net/images/20230713/1689238906_64afbd7a67fb8c6364c20.png!small)

可以看到有俩个用户信息以及相应密码，但是密码是加密的，这里直接修改数据库密码，使用Drupal 7自带密码生成器生成一个简单密码进行修改：

![](https://image.3001.net/images/20230713/1689238907_64afbd7b2844054e58f3e.png!small)

password: 123 hash: $S$DORnycDcoVYQXFiFThiwtonFe22NAlC8nTZKbzbVwWep4bYBMUFY；

接下来就是修改数据库中的密码：

![](https://image.3001.net/images/20230713/1689238908_64afbd7c0ec53ec1746bd.png!small)

完事就可以登录了：

![](https://image.3001.net/images/20230713/1689238908_64afbd7cdf156f613c857.png!small)

![](https://image.3001.net/images/20230713/1689238909_64afbd7d9ba10a1a8ead2.png!small)

在这里找到了flag3：

![](https://image.3001.net/images/20230713/1689238910_64afbd7e7e82b2697b98b.png!small)

![](https://image.3001.net/images/20230713/1689238911_64afbd7f1dbd6529f80d3.png!small)

Special PERMS will help FIND the passwd - but you'll need to -exec that
command to work out how to get what's in the shadow.

特殊的PERMS将有助于查找密码，但您需要执行该命令才能找到阴影中的内容。

接下来根据提示提权，通过find，-exec进行提权：

![](https://image.3001.net/images/20230713/1689238911_64afbd7fb6f6c4305b8f9.png!small)

