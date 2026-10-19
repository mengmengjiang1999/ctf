渗透环境：如下图所示，web服务器、ms-SQL服务器、PC客户端在同一个网络中，彼此之间，没有路由器或防火墙的隔离，这是一种危险的网络结构，入侵ms-SQL服务器，非常容易。（实战中，web服务是一个中控考勤服务）

![](https://image.3001.net/images/20220807/1659873867_62efaa4bc972188529fe7.png!small)

渗透原理：在win7机（或是kali虚拟机）上，浏览内网web，会触发web服务器联系ms-SQL数据库服务器，获取数据；在kali虚机上，我们可以截流web发送给ms-SQL的数据包，修改其中的sql语句，再将它发给ms-SQL执行，达到操控ms-SQL的目的。比如，我们可以增加一个新用户，然后，以新用户登入数据库。这样，我们就完全控制了ms-SQL数据库。这种攻击法，叫做中间人攻击。

渗透步骤：攻击步骤并不复杂，需要编写简单的脚本。过程中，只有二进制格式的字符串制作，略微复杂一点。我们将虚拟机kali作为攻击机，所有的操作都在kali上进行。bettercap和wireshark是kali的内置软件，无需安装，需要注意的是，kali的网卡需采用桥接模式。  
一、使用bettercap，发动中间人攻击，使kali成为中间人。

1、 编辑 spoof.cap 脚本。可以使用各种编辑工具，可以使用vi，其命令是 vi spoof.cap。内容只有两行，#后面是注释。见下图：

![](https://image.3001.net/images/20220807/1659838631_62ef20a7da0546925f9b2.png!small)

2、将kali变成中间人。只有一行命令

bettercap --gateway-override 192.168.1.9 -caplet spoof.cap

# 将ms-SQL服务器视为网关，kali才能变成web和ms-SQL的中间人

3、检查kali是否成功变成中间人。在模拟环境中，可以到web服务器和ms-SQL服务器上，使用 arp -a（同时适用于win系统和linux系统），
查看ip地址和mac码，检验中间人攻击是否成功。但在真实环境中，因为你无法操作服务器，所以只能跳过此步骤。实战说明：在kali上分别ping一下两台服务器，有助于arp欺骗迅速生效。

二、用浏览器访问网页，用wireshark抓包，捕获的sql语句越长越好

![](https://image.3001.net/images/20220807/1659871163_62ef9fbbd214d46c97e9b.png!small)

1、启动wireshark并设定好捕获参数。图中左上第一个就是捕获按钮，第二个是停止捕获。

2、浏览器中，尝试浏览不同的网页。

3、在wireshark捕获的数据中，我们要寻找一个特定的数据包，该数据包中原始的sql语句越长越好，足够的长度才能为我们篡改sql语句，提供足够多的字符空间。tds.query可以过滤出所有的数据库相关包，我们可以查看sql语句，找到长度足够的sql语句。上图中，列出了很多sql语句包，384是最长的，所以，它就是我们要找的特定数据包

4、重复操作浏览器，确保特定数据包能够重复出现

5、从特定数据包中抽取其原生的sql语句，制作二进制格式的字符串，这个步骤难度最大，是成功与否的关键。上图中间区域，tabular data stream
--tds query packet下面，可以看到完整的sql语句，它的确够长。鼠标放到下面蓝色区域，右键选择 as Escaped
String，再粘贴到编辑器中，变成如下图所示，需要手工处理一下，对照上副图，下图中删除白底数据，保留蓝底数据，然后删除头尾的引号、斜杠等，使它变成一个标准的二进制格式的字符串，它就是我们抽取的原始sql字符串，然后，复制到后面sql_replace.js截图的第7行。

![](https://image.3001.net/images/20220808/1659927433_62f07b89c42f69a616c56.png!small)

6、退出bettercap和wireshark

到目前为止，我们可以截留、监控、转发数据包，但是，我们还不能篡改数据。我们需要让数据经过一个代理tcp.proxy，在代理服务里面，才能修改数据。

三、编写2个脚本，一个是bettercap自动运行的脚本spoof.cap；另一个是替换sql语句的脚本sql_replace.js。

1、修改spoof.cap脚本，其内容从2行变成7行。原来的脚本，是用于启动arp欺骗攻击，增加的脚本作用是启动tcp.proxy代理。见下图：

![](https://image.3001.net/images/20220807/1659838670_62ef20ce5a530546e751f.png!small)

2、编写篡改数据的脚本，文件名为 sql_replace.js，采用javascript语言 。tcp.proxy代理会调用它，篡改数据。

脚本中有两个函数：

第一个是onLoad()，bettercap运行成功后，会在屏幕上提示：tcp module loader ----------------；

第二个函数示onData(from,to,data)，其中，只有data参数有用，
data就是系统截留的数据包，截留后，传递给onData函数，让它分析和修改，data被修改后，会自动转发到ms-sql服务器，在其上执行。为了便于分析，原始的data要转换生成为strFromNet（图中第17行）；onData()函数有二个重要的变量：一是strTotarget，它是我们伪造的sql语句，直接键盘敲入（图中第6行）。我们用它替换特定数据包中的原始sql语句；二是strFromCap，它是步骤二中，wireshark捕获的特定数据包中，抽取的原始sql语句，我们需要将它粘贴到这里（见图中第7行，为了方便阅读，图中数据截去了尾部，实际要长很多）。onData函数原理很简单，我们要在所有的捕获的数据包中搜索原始sql语句（图中第18行），一旦搜索到，将其替换成伪造的sql语句（图中第20行-38行），如果伪造的sql语句长度超过原生sql语句的长度，替换就会失败。如果短于原句，则填充空格补全。

![](https://image.3001.net/images/20220807/1659830729_62ef01c9c9c591bd44c21.png!small)

四、重新运行bettercap，加载上述脚本，注意屏幕上应该有提示。

bettercap --gateway-override 192.168.1.9 -caplet spoof.cap

此时，onData()函数已经加载，随时都可能篡改数据了。

五、重复网页操作，完成对ms-SQL的渗透。

如果屏幕上提示： ------find it----表示找到了特定数据包。如果没有出现这个提示，可能因为没有成为中间人，或是没有进行正确的网页操作，最大的可能是，捕获的原生sql数据包二进制转换出错了，需要重新转换一次。

如果屏幕上提示： ------crack sucessed!:):):) 表示替换成功。

如果屏幕上提示： -----but,its too short to replace with long command!-----表示替换失败。

修改strTotarget的值，你可以执行任何sql语句，增加用户，删除用户，其他等都可以。

