## 下载靶机

<https://www.vulnhub.com/entry/jangow-101,754/>  

## 打开靶机

最好使用VirtualBox，如果使用VMware可能获取不到IP，解决参考：https://blog.csdn.net/qq_41918771/article/details/103636890

## 打靶

### IP发现

nmap扫描网段发现靶机IP：192.168.2.129![1637906047_61a0767f16ea27806d1ad.png!small?1637906047833](https://image.3001.net/images/20211126/1637906047_61a0767f16ea27806d1ad.png!small?1637906047833)

###
端口发现![1637906213_61a07725467b1125a693b.png!small?1637906214020](https://image.3001.net/images/20211126/1637906213_61a07725467b1125a693b.png!small?1637906214020)

### 访问网站

![1637909442_61a083c27eaec7c476045.png!small?1637909444193](https://image.3001.net/images/20211126/1637909442_61a083c27eaec7c476045.png!small?1637909444193)

### 扫描网站目录

使用dirb扫描网站目录，发现wordpress地址，但未发现后台登录地址，无果，返回首页查找线索。

![1637909524_61a0841487656456d8464.png!small?1637909525378](https://image.3001.net/images/20211126/1637909524_61a0841487656456d8464.png!small?1637909525378)

![1637909591_61a084579e4030bbf9861.png!small?1637909592407](https://image.3001.net/images/20211126/1637909591_61a084579e4030bbf9861.png!small?1637909592407)

### 首页发现可疑接口

![1637909674_61a084aa3e1be5414ebea.png!small?1637909674931](https://image.3001.net/images/20211126/1637909674_61a084aa3e1be5414ebea.png!small?1637909674931)

发现接口可执行系统命令，直接写入哥斯拉后门

![1637909714_61a084d234efa1713bcbe.png!small?1637909714927](https://image.3001.net/images/20211126/1637909714_61a084d234efa1713bcbe.png!small?1637909714927)

> echo '<?phpeval($_POST["pass"]);' > 1.php

![1637909825_61a085414a4dd6603fe5f.png!small?1637909825994](https://image.3001.net/images/20211126/1637909825_61a085414a4dd6603fe5f.png!small?1637909825994)

### 哥斯拉链接后门

![1637917418_61a0a2ea8ae62f9d4fa40.png!small?1637917419178](https://image.3001.net/images/20211126/1637917418_61a0a2ea8ae62f9d4fa40.png!small?1637917419178)

### 反弹shell  

哥斯拉webshell不理想，尝试反弹shell

尝试各种反弹shell命令，始终无法反弹，经大佬指点，靶机有防火墙，使用nc反弹shell，但靶机nc不支持-e参数，所以自己上传nc使用，最后，使用443端口，成功反弹shell  

![1637919399_61a0aaa71b5a6c723d6ba.png!small?1637919399694](https://image.3001.net/images/20211126/1637919399_61a0aaa71b5a6c723d6ba.png!small?1637919399694)

### 调用交互式shell  

靶机安装有python3，使用python调用交互式shell  

> python3 -c 'import pty;pty.spawn("/bin/bash")'

![1637919508_61a0ab14c87a48f01533a.png!small?1637919509352](https://image.3001.net/images/20211126/1637919508_61a0ab14c87a48f01533a.png!small?1637919509352)

### 提权  

查看用户文件发现md5字符串，解密发现为空密码，并不知道怎么用。  

![1637920830_61a0b03ec355787e4773b.png!small?1637920831339](https://image.3001.net/images/20211126/1637920830_61a0b03ec355787e4773b.png!small?1637920831339)

![1637920911_61a0b08fec5c417eff6d6.png!small?1637920912466](https://image.3001.net/images/20211126/1637920911_61a0b08fec5c417eff6d6.png!small?1637920912466)

查看配置文件，发现mysql数据库用户名/密码，但无法连接数据库。  

![1637920961_61a0b0c1dfa1b3a6c5b3a.png!small?1637920962503](https://image.3001.net/images/20211126/1637920961_61a0b0c1dfa1b3a6c5b3a.png!small?1637920962503)

使用脚本 linux-exploit-suggester-2.pl 查看系统可能存在的漏洞。  

![1637921049_61a0b119440308534bb24.png!small?1637921049856](https://image.3001.net/images/20211126/1637921049_61a0b119440308534bb24.png!small?1637921049856)

使用CVE-2017-16695漏洞顺利提权。  

![1637921155_61a0b183b7ace02bd8a2c.png!small?1637921156359](https://image.3001.net/images/20211126/1637921155_61a0b183b7ace02bd8a2c.png!small?1637921156359)

  

  

  

  

