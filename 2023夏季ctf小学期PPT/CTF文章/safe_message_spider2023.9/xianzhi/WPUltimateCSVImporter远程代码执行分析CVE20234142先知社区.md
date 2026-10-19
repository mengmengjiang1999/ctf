**1.前言**  
WordPress的WP Ultimate CSV Importer插件易受远程代码执行的攻击  
**2.影响版本**  
<=7.9.8（所有用户）  
其他版本（管理员  
**3.漏洞信息**  
此漏洞发生在ImportHelpers.php中的get_header_values函数。

![](./img/3505406407816088607.png)  
trim_content数组为漏洞触发位置  
$header_trim 的作用是用来存储 $map 数组中经过处理后的键名。  
在函数中，通过循环遍历 $map 数组，对于每个键名，如果它包含了 ->static，->math，或者 ->cus1 这些字符串，那么就将它从 $map
数组中删除。否则，就使用 strtr() 函数将 $trim_content 数组中的键值对应替换掉键名中的字符串，得到 $header_trim，并将
$map 数组中的该键名和它对应的值存储到 $map 数组中。这样，就可以在后面的处理中使用 $header_trim 代替原始的键名

    
    
    $trim_content = array(
                '->static' => '', 
                '->math' => '', 
                '->cus1' => ''
            );
    

此函数为解析csv的关键功能，作者没有详细讨论近一步具体的触发利用  
**4.环境搭建**  
使用apache搭建wordpress  
这里需要注意的是php+mysql8会出错  
在mysql8时，出现了一种新的验证方式caching_sha2_password，这个方式成为了新的验证机制，默认在配置密码的时候也是用的这种方式进行处理的，原有的mysql_native_password被替换掉了。这就是为什么php连不上的原因。  
解决方式：

    
    
    update user set plugin=‘mysql_native_password’ where User=‘root’;
    flush PRIVILEGES;
    

![](./img/1525980353452716425.png)  
安装WP Ultimate CSV Importer插件，且赋予作者权限

![](./img/7273320495259452464.png)

**5.漏洞复现**  
制作一个恶意csv模板文件

![](./img/6848775966726286681.png)

注意：由于->字符在csv中会报错，后期上传时需要自己抓包修改

![](./img/4798746903587274771.png)  
成功触发

![](./img/317318672480824902.png)

6.技术细节

这里我找到两处触发条件，  
1.FIFUPOSTS  
2.FIFUPAGE  
通过set_fifu_values函数传递我们的csv文件的列值

![](./img/3925140526474954801.png)

我们来看set_fifu_values函数，set_fifu_values函数调用了我们的csv解析函数  
![](./img/7186082320302819138.png)  
当插件在检测到->static，->math，和 ->cus1时，会替换我们的csv文件，这个时候就会加载我们的恶意csv文件，触发payload  
在高级模式Create WP Custom Fields处抓包  
![](./img/2789638874938035342.png)

![](./img/3089155627563310922.png)  
这里用的是CORECUSTFIELD，CORECUSTFIELD也是位于set_fifu_values函数下的一个条件，我就把这个给替换成FIFUPOSTS，具体哪里调用FIFUPOSTS师傅们自己可以去找一下。  
**7.官方修复**  
官方在最新版本中只是禁用了作者的权限，而管理员仍然是可以上传解析的，所以此漏洞并未完美修复。

