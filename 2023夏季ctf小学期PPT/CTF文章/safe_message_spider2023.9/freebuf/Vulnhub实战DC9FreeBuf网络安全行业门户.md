## 前言

本次的实验靶场是Vulnhub上面的DC-9，其中的渗透测试过程比较多，最终的目的是要找到其中的flag。

## 一、信息收集

  1. 对目标网络进行扫描
    
        arp-scan -l

![1693641973_64f2ecf5e9dc8086438db.png!small?1693641973104](https://image.3001.net/images/20230902/1693641973_64f2ecf5e9dc8086438db.png!small?1693641973104)

  2. 对目标进行端口扫描
    
        nmap -sC -sV -oA dc-9 192.168.1.131

![1693643100_64f2f15cbf2aca289e64f.png!small?1693643099939](https://image.3001.net/images/20230902/1693643100_64f2f15cbf2aca289e64f.png!small?1693643099939)

  3. 扫描出目标开放了22和80两个端口，访问目标的80端口。

![1693642016_64f2ed20de8b49fee4326.png!small?1693642016204](https://image.3001.net/images/20230902/1693642016_64f2ed20de8b49fee4326.png!small?1693642016204)

  4. 对目标进行目录扫描与分析。
    
        nikto -host 192.168.1.134

![1693642036_64f2ed342faf4eee6394e.png!small?1693642035584](https://image.3001.net/images/20230902/1693642036_64f2ed342faf4eee6394e.png!small?1693642035584)

  5. 我访问了一下includes/目录，都是一些空文件，没什么特别的文件，但是我在search的菜单选项下的界面中试了一下SQL注入，发现其存在SQL注入，并且网页指向results.php的界面。

## 二、漏洞利用

### （1）SQL注入

  6. 既然在search选项下的界面存在SQL注入，那就进行SQL注入
    
        'or 1=1 #

![1693642055_64f2ed47c9f3747f3ca75.png!small?1693642054820](https://image.3001.net/images/20230902/1693642055_64f2ed47c9f3747f3ca75.png!small?1693642054820)

>     * 之前写成result.php了，难怪sqlmap无法扫描出来
>
>     * 如果是GET型SQL注入，那么直接在url中输入参数即可，而如果是POST提交，则需要指定--data "提交的数据"才行。

  7. 既然存在SQL注入，我们就是用sqlmap去扫描一下。
    
        sqlmap -u "http://192.168.1.134/result.php" --data "search=1" --dbs

![1693642073_64f2ed592ef5db1eecf95.png!small?1693642072479](https://image.3001.net/images/20230902/1693642073_64f2ed592ef5db1eecf95.png!small?1693642072479)

  8. 尝试对users这个库下手，因为要登陆一些网站后台需要用户名和密码，而这个库可能就有，先获取其中的所有表名。
    
        sqlmap -u "http://192.168.1.134/results.php" --data "search=1" -D users --tables

![1693642258_64f2ee12b12399a0b7c9f.png!small?1693642258038](https://image.3001.net/images/20230902/1693642258_64f2ee12b12399a0b7c9f.png!small?1693642258038)

  9. 有一张表，查看其具体的信息。
    
        sqlmap -u "http://192.168.1.134/results.php" --data "search=1" -D users -T UserDetails --dump

![1693642321_64f2ee514ca1e9f8de045.png!small?1693642320616](https://image.3001.net/images/20230902/1693642321_64f2ee514ca1e9f8de045.png!small?1693642320616)

> 可以将username和password做成两个字典，我分别做成了user-dict和pass-dict两个字典。

  10. 使用wfuzz工具测试一下，其中大多数的行数都相同，我于是过滤了一下，没有发现特殊的Payload参数。
    
        wfuzz -z file,user-dict -z file,pass-dict --hw 87 "http://192.168.1.134/manage.php?username=FUZZ&password=FUZZ" 

![1693642339_64f2ee6315a2d15cbfe4d.png!small?1693642338324](https://image.3001.net/images/20230902/1693642339_64f2ee6315a2d15cbfe4d.png!small?1693642338324)

  11. 只能试一下其他的数据库了，之前使用sqlmap扫描到目标还有一个Staff的数据库，扫描一下看其中还有哪些表。
    
        sqlmap -u "http://192.168.1.134/results.php" --data "search=1" -D Staff --table

![1693642358_64f2ee76138bcc70de618.png!small?1693642357288](https://image.3001.net/images/20230902/1693642358_64f2ee76138bcc70de618.png!small?1693642357288)

  12. 扫出来两张表，第一张表和我在目标网页的Display All Recodes菜单选项下的界面的内容差不多，没什么特别的，而第二张Users表有些东西，使用sqlmap扫描之后，里面有一个可以解密的哈希值。

> 之前的users是 **一个数据库** ，这里的Users是 **一张表** 。
    
        sqlmap -u "http://192.168.1.134/results.php" --data "search=1" -D Staff -T Users --dump

![1693642378_64f2ee8a559a25b969aa7.png!small?1693642377507](https://image.3001.net/images/20230902/1693642378_64f2ee8a559a25b969aa7.png!small?1693642377507)

  13. 我使用了第一个默认的字典去破解，结果破解出一个用户名Admin，密码是transorbital1。

![1693642403_64f2eea3ad8a69b877c8b.png!small?1693642403157](https://image.3001.net/images/20230902/1693642403_64f2eea3ad8a69b877c8b.png!small?1693642403157)

  14. 尝试使用获得的用户名和密码去manage选项的页面进行登录，结果成功登录，页面提示我已登录成功，并且多了一个Log Out的选项，之前没有，还有一条“File does not exist”的提示语，可能存在文件包含漏洞。

![1693642418_64f2eeb2aff6674eca6a5.png!small?1693642417708](https://image.3001.net/images/20230902/1693642418_64f2eeb2aff6674eca6a5.png!small?1693642417708)

### （2）文件包含漏洞

  15. 目标可能存在文件包含漏洞，但是我不知道传递文件的参数，于是我仍然使用wfuzz工具去试一下。
    
        wfuzz -b "PHPSESSID=k4vtn0fuo7d4bauibn1iqpp6gf" -w /usr/share/wfuzz/wordlist/general/common.txt http://192.168.1.134/manage.php?FUZZ=index.php

![1693642475_64f2eeeb6170350675182.png!small?1693642474648](https://image.3001.net/images/20230902/1693642475_64f2eeeb6170350675182.png!small?1693642474648)

>     * 我将参数-w中的字母写成了大写，导致后面报错。
>
>     * 遇到Kali无法连接阿里云的源，修改了DNS之后重启网络就好了，在/etc/apt/sources.list文件里面进行修改。

  16. 扫描出一个与众不同的参数——file，传入file=index.php的参数值发现没什么用，我于是尝试了一下../../../../../etc/passwd。

![1693642517_64f2ef15c734771aa3fc2.png!small?1693642516905](https://image.3001.net/images/20230902/1693642517_64f2ef15c734771aa3fc2.png!small?1693642516905)

> 我把--hw写成了-hw，少了一个“-”，导致出错。

  

### （3）爆破SSH密码

  17. 既然我已经获取了目标操作系统下的/etc/passwd文件，其中有些和users中的重复，我决定使用hydra对SSH账号密码进行暴力破解，结果显示不允许连接，试了多次也不行，目标可能做了一些限制。
    
        hydra -L user-dict -P pass-dict 192.168.1.134 ssh

![1693642549_64f2ef35bfa491a37b770.png!small?1693642548844](https://image.3001.net/images/20230902/1693642549_64f2ef35bfa491a37b770.png!small?1693642548844)

  18. 后来得知有一些方法可以用来保护ssh的22端口，例如开启knockd服务，这要求我们必须先访问一些其他的端口，然后才能访问22端口，这个文件是/etc目录下的knockd.conf文件中，当我去访问这个文件时，果然如此，必须依次访问7489、8475和9842三个端口才能开放22端口，之前扫描出来的22端口是处于被保护状态的，无法直接访问。

![1693642567_64f2ef474f6b7e96b47a0.png!small?1693642566322](https://image.3001.net/images/20230902/1693642567_64f2ef474f6b7e96b47a0.png!small?1693642566322)

  19. 使用nmap依次对三个端口进行访问。

![1693642583_64f2ef576aa9259dd630a.png!small?1693642582621](https://image.3001.net/images/20230902/1693642583_64f2ef576aa9259dd630a.png!small?1693642582621)

  20. 访问按以上三个端口之后，再访问22端口，成功访问。

![1693642603_64f2ef6b156ac9264d521.png!small?1693642602091](https://image.3001.net/images/20230902/1693642603_64f2ef6b156ac9264d521.png!small?1693642602091)

> 如果访问了也打不开，可以试一下如下命令：
>  
>     >     for x in 7489 8475 9842 22 ;do nc 192.168.1.134 $x;done

  21. 之后继续使用hydra进行暴力破解，爆破出来两个用户名和密码
    
        hydra -L user-dict -P pass-dict 192.168.1.134 ssh

![1693642617_64f2ef790d9e23c5b739c.png!small?1693642616322](https://image.3001.net/images/20230902/1693642617_64f2ef790d9e23c5b739c.png!small?1693642616322)

之后我又试了多次，又爆破出来一个用户名和密码。

![1693642634_64f2ef8a7dcb06e97270a.png!small?1693642633629](https://image.3001.net/images/20230902/1693642634_64f2ef8a7dcb06e97270a.png!small?1693642633629)

USERNAME| PASSWROD  
---|---  
chandlerb| UrAG0D!  
joeyt| Passw0rd  
janitor| Ilovepeepee  
  
> 我之前一直扫不出来，就使用nmap把7469、8475、9842、22这四个端口 _ **逆着访问了一遍**_ ，再用hydra爆破，还是不行，后来又
> _ **顺着访问了一遍**_ ，就可以了。

  22. 接下来要去验证这些用户名和密码是否能够登录，结果全部登录成功。

![1693642659_64f2efa325c433d5dc27f.png!small?1693642658219](https://image.3001.net/images/20230902/1693642659_64f2efa325c433d5dc27f.png!small?1693642658219)

![1693642673_64f2efb18449140c8b0fa.png!small?1693642672560](https://image.3001.net/images/20230902/1693642673_64f2efb18449140c8b0fa.png!small?1693642672560)

![1693642686_64f2efbe7f65558e0c18f.png!small?1693642685565](https://image.3001.net/images/20230902/1693642686_64f2efbe7f65558e0c18f.png!small?1693642685565)

  23. 既然我已经登陆了目标系统，就要去查看系统中的内容了。

  24. 我是用ls -a查找敏感文件时，只有janitor用户下有一个其他两个用户没有的东西，不确定是目录还是文件，使用file命令查看了一下，发现是一个目录，里面还有一个passwords-found-on-post-it-notes.txt的文件。

![1693642727_64f2efe731e261dec412d.png!small?1693642726190](https://image.3001.net/images/20230902/1693642727_64f2efe731e261dec412d.png!small?1693642726190)![1693642742_64f2eff621be7e3fef83f.png!small?1693642741198](https://image.3001.net/images/20230902/1693642742_64f2eff621be7e3fef83f.png!small?1693642741198)

  25. 这时出现了三个新密码，前面的三个在数据库中看到过。

![1693642759_64f2f0078a50c11fddeac.png!small?1693642758691](https://image.3001.net/images/20230902/1693642759_64f2f0078a50c11fddeac.png!small?1693642758691)

  26. 将这三个新密码加入到之前我做的密码字典pass-dict中，我将其改名为pass-dict1，原来的文件备份了，再次进行爆破，爆破出来一个新用户，试了一下密码，可以登录成功。

![1693642776_64f2f018cd22e20236094.png!small?1693642775855](https://image.3001.net/images/20230902/1693642776_64f2f018cd22e20236094.png!small?1693642775855)

![1693642793_64f2f029a9d0a36a91f4e.png!small?1693642792790](https://image.3001.net/images/20230902/1693642793_64f2f029a9d0a36a91f4e.png!small?1693642792790)

USERNAME| PASSWROD  
---|---  
chandlerb| UrAG0D!  
joeyt| Passw0rd  
janitor| Ilovepeepee  
fredf| B4-Tru3-001  

## 三、权限提升

  27. 已经拿到一些用户名和密码并且已经成功登陆了，接下来是提权的时候了。

> 提权的思路：
>
>   1. 找敏感文件：使用ls -a 或者find / *之类的命令
>
>   2. 查看可以用root权限去执行的程序：使用命令sudo -l：
>
>   3. 历史命令：使用history命令查看一些历史命令
>
>   4. 内核漏洞：使用uname -a去查看内核信息，然后再去查询其是否存在过历史漏洞，以方便我们提权
>
>

  28. 在所有已经登录的用户下输入`ls -a`，没有什么特别的，除了上面的janitor用户，接下来试一下`sudo -l`命令，结果在fredf这个用户中发现了一些特殊的信息，有一个具有root执行权限的程序test。

![1693642822_64f2f04651b84d8d3dd34.png!small?1693642821620](https://image.3001.net/images/20230902/1693642822_64f2f04651b84d8d3dd34.png!small?1693642821620)

  29. 无法直接访问，跳转到其路径之后才可以访问，发现是一个Python文件。

![1693643780_64f2f404abf48d79c7c21.png!small?1693643779983](https://image.3001.net/images/20230902/1693643780_64f2f404abf48d79c7c21.png!small?1693643779983)

  30. 直接执行是没用的，有一个提示，是关于这个Python文件读取和追加的，我于是去找了一下这个test.py文件所在的目录。

![1693642851_64f2f063c2698dd9a960c.png!small?1693642850773](https://image.3001.net/images/20230902/1693642851_64f2f063c2698dd9a960c.png!small?1693642850773)

  31. 分别查看一下。

![1693642879_64f2f07fc342e93bd6764.png!small?1693642879022](https://image.3001.net/images/20230902/1693642879_64f2f07fc342e93bd6764.png!small?1693642879022)

![1693642890_64f2f08a6cc9962e78a4c.png!small?1693642889652](https://image.3001.net/images/20230902/1693642890_64f2f08a6cc9962e78a4c.png!small?1693642889652)

  32. 既然可以读取追加，哪么就可以尝试添加一个设计好的用户，使其具有root权限，然后试着将其追加到一些特殊文件中，首先使用openssl生成一个用户名和密码。
    
        openssl passwd -1 -salt admin 123456

![1693642904_64f2f098ca84b91be6d92.png!small?1693642904081](https://image.3001.net/images/20230902/1693642904_64f2f098ca84b91be6d92.png!small?1693642904081)

  33. 追加到其他文件可能没有权限，只好追加到/tmp目录中，在/tmp/passwd中。
    
        echo 'admin03:$1$admin$LClYcRe.ee8dQwgrFc5nz.:0:0::/root:/bin/bash' >> /tmp/passwd

![1693642924_64f2f0ac69f73445c428f.png!small?1693642923512](https://image.3001.net/images/20230902/1693642924_64f2f0ac69f73445c428f.png!small?1693642923512)

  34. 成功了，这时可以使用test.py读取/tmp/passwd并且将其追加到/etc/passwd中。
    
        sudo ./test /tmp/passwd /etc/passwd

![1693642938_64f2f0ba80730f41f666e.png!small?1693642938303](https://image.3001.net/images/20230902/1693642938_64f2f0ba80730f41f666e.png!small?1693642938303)

之前的第一个admin用户的shell程序设置出错了，少了一个/，第二个admin和第一个用户名重复了，这时我将添加了一个admin03的用户，其权限为root权限。

  35. 追加成功，切换至具有root权限的admin03用户。

![1693642954_64f2f0caab27c0e02b6fc.png!small?1693642953817](https://image.3001.net/images/20230902/1693642954_64f2f0caab27c0e02b6fc.png!small?1693642953817)

  36. 转到root目录下，查看有没有关于flag的文件，通常情况下，这些文件都在root目录下。查看了一下，果然在这里。

![1693642969_64f2f0d9d75f7cbfc5dcd.png!small?1693642968939](https://image.3001.net/images/20230902/1693642969_64f2f0d9d75f7cbfc5dcd.png!small?1693642968939)

  37. 使用cat命令查看一下，果然如此，拿到了flag，完结散花。

![1693642981_64f2f0e58cfee15a8221f.png!small?1693642981032](https://image.3001.net/images/20230902/1693642981_64f2f0e58cfee15a8221f.png!small?1693642981032)

