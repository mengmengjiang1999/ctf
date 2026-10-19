关于dvwa下的文件上传的一些新手学习过程，大佬们不喜勿喷，如有不足之处还请指出！

## 文件上传漏洞原理：

由于开发者对用户文件上传部分的控制不足，对于用户上传的文件格式和内容没有做严谨的判断，使得用户可以上传恶意的脚本文件，执行服务器命令。  

## Low级别

`<?php  
if( isset( $_POST[ 'Upload' ] ) ) {  
// Where are we going to be writing to?  
$target_path = DVWA_WEB_PAGE_TO_ROOT . "hackable/uploads/";  
$target_path .= basename( $_FILES[ 'uploaded' ][ 'name' ] );  
// Can we move the file to the upload folder?  
if( !move_uploaded_file( $_FILES[ 'uploaded' ][ 'tmp_name' ], $target_path ) )
{  
// No  
echo '<pre>Your image was not uploaded.</pre>';  
}  
else {  
// Yes!  
echo "<pre>{$target_path} succesfully uploaded!</pre>";  
}  
}  
?> `  
  
---  
  
根据源代码分析可知此时并没有任何的防御措施，所以可以直接编写上传一句话木马上去：

![1610853633_6003ad017ebeceed2c7f5.png!small?1610853633348](https://image.3001.net/images/20210117/1610853633_6003ad017ebeceed2c7f5.png!small?1610853633348)

![1610853721_6003ad595a3d06ff37020.png!small?1610853721236](https://image.3001.net/images/20210117/1610853721_6003ad595a3d06ff37020.png!small?1610853721236)

根据相对路径和url中的路径可知上传的绝对路径为

127.0.0.1/DVWA-master/hackable/uploads/shell.php

然后通过蚁剑连接：

![1610853775_6003ad8f0abad288ea361.png!small?1610853774877](https://image.3001.net/images/20210117/1610853775_6003ad8f0abad288ea361.png!small?1610853774877)

![1610853789_6003ad9d14e14e827de64.png!small?1610853788873](https://image.3001.net/images/20210117/1610853789_6003ad9d14e14e827de64.png!small?1610853788873)

## Medium级别

`<?php  
  
if( isset( $_POST[ 'Upload' ] ) ) {  
// Where are we going to be writing to?  
$target_path = DVWA_WEB_PAGE_TO_ROOT . "hackable/uploads/";  
$target_path .= basename( $_FILES[ 'uploaded' ][ 'name' ] );  
  
// File information  
$uploaded_name = $_FILES[ 'uploaded' ][ 'name' ];  
$uploaded_type = $_FILES[ 'uploaded' ][ 'type' ];  
$uploaded_size = $_FILES[ 'uploaded' ][ 'size' ];  
  
// Is it an image?  
if( ( $uploaded_type == "image/jpeg" || $uploaded_type == "image/png" ) &&  
( $uploaded_size < 100000 ) ) {  
  
// Can we move the file to the upload folder?  
if( !move_uploaded_file( $_FILES[ 'uploaded' ][ 'tmp_name' ], $target_path ) )
{  
// No  
echo '<pre>Your image was not uploaded.</pre>';  
}  
else {  
// Yes!  
echo "<pre>{$target_path} succesfully uploaded!</pre>";  
}  
}  
else {  
// Invalid file  
echo '<pre>Your image was not uploaded. We can only accept JPEG or PNG
images.</pre>';  
}  
}  
  
?> `

根据源代码可知只允许上传jpeg和png格式文件并对上传文件大小有了限制（100000B）

### 方法1

通过bp抓包可知存在mime类型检测

![1610854194_6003af328f8176c9decc9.png!small?1610854194436](https://image.3001.net/images/20210117/1610854194_6003af328f8176c9decc9.png!small?1610854194436)

修改content-type字段为 image/jpeg并转发

![1610854245_6003af65af34d3a60b692.png!small?1610854245593](https://image.3001.net/images/20210117/1610854245_6003af65af34d3a60b692.png!small?1610854245593)

上传成功

![1610854287_6003af8fba03d6cc7d9d9.png!small?1610854287542](https://image.3001.net/images/20210117/1610854287_6003af8fba03d6cc7d9d9.png!small?1610854287542)

然后通过蚁剑连接

![1610854299_6003af9ba7a50da145bc6.png!small?1610854299735](https://image.3001.net/images/20210117/1610854299_6003af9ba7a50da145bc6.png!small?1610854299735)

### 方法2

修改上传文件格式为png，然后抓包

![1610854453_6003b0356a9ed31774c48.png!small?1610854453291](https://image.3001.net/images/20210117/1610854453_6003b0356a9ed31774c48.png!small?1610854453291)

![1610854479_6003b04f6f3c232809f4e.png!small?1610854479265](https://image.3001.net/images/20210117/1610854479_6003b04f6f3c232809f4e.png!small?1610854479265)

只需要在filename中修改格式为php即可上传成功

![1610854526_6003b07e36453cd359b48.png!small?1610854526003](https://image.3001.net/images/20210117/1610854526_6003b07e36453cd359b48.png!small?1610854526003)

### 方法3

0x00截断（需要php版本低于5.3.4）：程序读取文件名时，遇到0x00，就认为文件名结束了，因为0x00就是字符0，也就相当于false和空。

首先上传shell.php.jpeg文件并抓包，然后到hex看十六进制，找到上传的文件名中的0x2e（.），并把第二个2e改为00（因为文件是test.php.jpg有两个点）

![1610854783_6003b17f32a6f3504116b.png!small?1610854783012](https://image.3001.net/images/20210117/1610854783_6003b17f32a6f3504116b.png!small?1610854783012)

  

![1610854811_6003b19bab7277b56a40a.png!small?1610854811590](https://image.3001.net/images/20210117/1610854811_6003b19bab7277b56a40a.png!small?1610854811590)

  

转发，上传成功

![1610855589_6003b4a5b206ca5c5702e.png!small?1610855589541](https://image.3001.net/images/20210117/1610855589_6003b4a5b206ca5c5702e.png!small?1610855589541)

用蚁剑连接

![1610855714_6003b522d8eb16a822ac5.png!small?1610855714751](https://image.3001.net/images/20210117/1610855714_6003b522d8eb16a822ac5.png!small?1610855714751)

## High

`<?php  
  
if( isset( $_POST[ 'Upload' ] ) ) {  
// Where are we going to be writing to?  
$target_path = DVWA_WEB_PAGE_TO_ROOT . "hackable/uploads/";  
$target_path .= basename( $_FILES[ 'uploaded' ][ 'name' ] );  
  
// File information  
$uploaded_name = $_FILES[ 'uploaded' ][ 'name' ];  
$uploaded_ext = substr( $uploaded_name, strrpos( $uploaded_name, '.' ) + 1);  
$uploaded_size = $_FILES[ 'uploaded' ][ 'size' ];  
$uploaded_tmp = $_FILES[ 'uploaded' ][ 'tmp_name' ];  
  
// Is it an image?  
if( ( strtolower( $uploaded_ext ) == "jpg" || strtolower( $uploaded_ext ) ==
"jpeg" || strtolower( $uploaded_ext ) == "png" ) &&  
( $uploaded_size < 100000 ) &&  
getimagesize( $uploaded_tmp ) ) {  
  
// Can we move the file to the upload folder?  
if( !move_uploaded_file( $uploaded_tmp, $target_path ) ) {  
// No  
echo '<pre>Your image was not uploaded.</pre>';  
}  
else {  
// Yes!  
echo "<pre>{$target_path} succesfully uploaded!</pre>";  
}  
}  
else {  
// Invalid file  
echo '<pre>Your image was not uploaded. We can only accept JPEG or PNG
images.</pre>';  
}  
}  
?>`  
  
---  
  
根据源代码可知，high级别做出了更多的限制：

getimagesize()函数限制了上传文件内容的文件头必须为图像类型；

（$uploaded_ext = substr( $uploaded_name, strrpos( $uploaded_name, ‘.’) +
1）只验证文件名的最后一个“.”后面的格式，防御了iis6.0解析漏洞

我们可以通过生成图片马的方式上传文件

在命令行下用copy命令将图片1.png和之前的一句话木马shell.php合并在一起

![1610860562_6003c8127cfc418095bdb.png!small?1610860562292](https://image.3001.net/images/20210117/1610860562_6003c8127cfc418095bdb.png!small?1610860562292)

![1610860590_6003c82ebd0d3c96213dc.png!small?1610860590647](https://image.3001.net/images/20210117/1610860590_6003c82ebd0d3c96213dc.png!small?1610860590647)

然后通过查看生成的png文件可知一句话木马已经写入到了最后部分

![1610860634_6003c85acbbd7b1ce17eb.png!small?1610860634754](https://image.3001.net/images/20210117/1610860634_6003c85acbbd7b1ce17eb.png!small?1610860634754)

并且可以成功上传新生成的png文件

![1610860698_6003c89a646830eb16a3f.png!small?1610860698207](https://image.3001.net/images/20210117/1610860698_6003c89a646830eb16a3f.png!small?1610860698207)

此时由于图片马中的php代码并没有被解析，所以不能直接使用蚁剑进行连接，这里可以通过命令执行漏洞将文件名改为php

在 command injection的命令输入框中输入以下命令

127.0.0.1|move ../../hackable/uploads/3.png ../../hackable/uploads/shell.php

![1610861224_6003caa8a4949cb2b0b84.png!small?1610861224477](https://image.3001.net/images/20210117/1610861224_6003caa8a4949cb2b0b84.png!small?1610861224477)

  

![1610861153_6003ca61bb0991ff485d6.png!small?1610861153589](https://image.3001.net/images/20210117/1610861153_6003ca61bb0991ff485d6.png!small?1610861153589)

然后用蚁剑连接

![1610861291_6003caeb452a98e4d1e85.png!small?1610861291097](https://image.3001.net/images/20210117/1610861291_6003caeb452a98e4d1e85.png!small?1610861291097)

另外我在这里也试了试用文件包含的方法，试了几次执行都会报错，可能是我dvwa的问题。

