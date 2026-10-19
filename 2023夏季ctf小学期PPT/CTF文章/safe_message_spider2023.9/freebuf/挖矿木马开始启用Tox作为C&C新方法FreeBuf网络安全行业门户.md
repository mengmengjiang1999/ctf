Tox 是一个 P2P 型的无中心服务器消息传递系统，使用 NaCl 进行加解密。由于没有中心服务器，类似 BitTorrent，会使用 UDP 与 DHT
来查找在线端点。这表明该方法能够保持很好的匿名性，每个用户都有一个表明自己身份的 ID。

此前也发现过 Tox 被攻击者用于进行通信，本次是 Uptycs 威胁研究团队发现了使用 Tox 协议的 ELF 样本文件。

## 技术概览

在野发现的二进制文件尽管是 stripped 的，但仍然可以顺利地进行反编译。文件是使用 C 语言进行编写的，只静态链接了
[c-toxcore](https://github.com/TokTok/c-toxcore)库。

下图为样本反编译的 main 函数：

![image.png-278.2kB](https://image.3001.net/images/20220824/1661349122_63062d0219f3cd71bcc48.png!small)main
函数

shell_script 变量是很可疑的，攻击者使用其终止已知会进行挖矿的进程，会清除经常用于持久化的一些定时任务。

如下所示，名为 start_routine1 的函数会在 /var/tmp/ 中创建一个具有随机文件名的文件，并将 shell_script
的内容写入并执行。

![image.png-202.3kB](https://image.3001.net/images/20220824/1661349123_63062d03340e5a260a1db.png!small)start_routine1
函数

Shell 脚本中包含终止挖矿进程的命令。

![image.png-221.7kB](https://image.3001.net/images/20220824/1661349124_63062d0426378c2a994f8.png!small)脚本文件

start_routine2 函数通过 main 函数中的 pthread_create 进行调用，通过 UDP 协议将每个命令的输出发送给 Tox
接收者。

![image.png-135.8kB](https://image.3001.net/images/20220824/1661349125_63062d0561d5c62fb882d.png!small)start_routine2
函数

其中有很多 bash 命令十分可疑，例如执行 dig 使用 resolver4.opendns.com 作为 DNS 服务器请求查询
myip.opendns.com。

执行 `curl -s -m 20 ifconfig.me`获取机器的 IP 地址并保存到名为 `name_var`的变量中。执行 `cat
/var/lib/dbus/machine-id`获取机器的硬件 ID，也存入相同变量中，并且在 tox_self_set_name
中进一步设置用户名称。相继执行 `nproc`、`uname -a`和 `whoami`命令，将结果存储在 `status_var`中，在
tox_self_set_status_message 中用于设置用户的状态信息。

![image.png-270.8kB](https://image.3001.net/images/20220824/1661349126_63062d06406bbbbcc0021.png!small)一些命令

main 函数中还有与 Tox 相关的函数 tox_new、tox_self_set_name 与
tox_self_set_status_message，这都与 Tox 设置有关。

![image.png-286.4kB](https://image.3001.net/images/20220824/1661349127_63062d072a0acf62147a7.png!small)main
函数的其余部分

上图中，调用了 tox_callback_friend_message。以上三个命令都是回调函数的一部分，作为参数传递给
tox_callback_friend_message，如下所示。

![image.png-210.5kB](https://image.3001.net/images/20220824/1661349128_63062d081bc826da3c52f.png!small)

回调函数

updatekilllist 会更新 start_routine1
中执行的脚本，`execscript`会按需运行脚本，`getinfo`会打印信息，`exit`会退出 Tox 连接。

## 结论

该样本尽管没有任何明显的恶意行为，但分析人员认为其是挖矿团伙的一个样本。过去曾经发现攻击者利用 Tox 作为通信方式，例如 HelloXD
勒索软件混合使用了 Tox 与 Tor。本次发现的样本则使用 Tox 协议运行脚本，对网络通信的监控仍然是非常重要的。

## IOC

> 333a6b3cf226c55d4438c056e6c302fec3ec5dcf0520fc9b0ccee75785a0c8c5

## 参考来源

> [Uptycs](https://www.uptycs.com/blog/is-tox-the-new-cc-method-for-> coinminers)

