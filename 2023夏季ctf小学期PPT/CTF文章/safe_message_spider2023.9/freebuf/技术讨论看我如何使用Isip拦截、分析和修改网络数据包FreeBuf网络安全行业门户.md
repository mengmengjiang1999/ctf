**今天给大家介绍的是一款名叫Isip的模拟工具，该工具套装可用于数据包修改、嗅探、模拟中间人攻击、模糊测试和模拟DoS攻击等等。**

![222222222222222.png](https://image.3001.net/images/20181107/1541583324_5be2b1dc18084.png!small)

## 工具演示视频

视频地址：<https://asciinema.org/a/11128>

### 工具安装

    
    
    git clone <https://github.com/halitalptekin/isip.git>
    
    cd isip
    
    pip install -r requirements.txt

## 工具使用

数据包模拟工具可以在packet命令循环中找到，输入命令之后，你将会进入到main命令循环中：

    
    
    isip:main>packet
    
    isip:packet>

大家可以使用new命令创建一个新的sip数据包，如果你没有给数据包命名的话，isip会默认以message-{id}的形式命名数据包。

    
    
    isip:packet>new
    
    isip:packet>new r1

使用list命令列举出所有新创建的sip[数据包](https://www.kitploit.com/search/label/Packets)：

    
    
    isip:packet>list

使用show命令查看数据包属性，你还可以配合ip、udp或sip选项跟show命令一起使用：

    
    
    isip:packet>show message-1
    
    isip:packet>show message-1 ip
    
    isip:packet>show message-1 udp
    
    isip:packet>show message-1 sip
    
    isip:packet>show message-1 ip src
    
    isip:packet>show message-1 udp sport
    
    isip:packet>show message-1 sip uri
    
    isip:packet>show message-1 sip headers.to

使用set命令设置数据包属性，你还可以配合ip、udp或sip命令来进行设置：

    
    
    isip>set message-1 ip src 12.12.12.12
    
    isip>set message-1 udp sport 4545
    
    isip>set message-1 sip method OPTIONS
    
    isip>set message-1 sip headers.from "blabla"

使用set命令设置数据包随机属性，你还可以配合random-headers-from, random-headers-to, random-headers-call-id,random-headers-max-forwards, random-headers-user-agent, random-headers-contact,random-headers-invite-cseq和 random-headers-register-cseq命令一起使用。

    
    
    isip:packet>set message-1 ip src random-ip
    
    isip:packet>set message-1 udp sport random-port
    
    isip:packet>set message-1 sip headers.from random-headers-from
    
    isip:packet>set message-1 sip headers.to random-headers-to
    
    isip:packet>set message-1 sip headers.contact random-headers-contact
    
    isip:packet>set message-1 sip body random-data 50

使用send命令发送数据包：

    
    
    isip:packet>send message-1 1
    
    isip:packet>send message-1 150

使用parse命令解析数据包中的文本信息：

    
    
    isip:packet>parse test/test1.txt r1

使用load命令从pcap文件中加载数据包，如果你没有对数据包命名，工具会自动以message-{id}的形式命名：

    
    
    isip:packet>load test.pcap r1
    
    isip:packet>load test.pcap

接下来，使用save命令保存数据包为pcap文件：

    
    
    isip:packet>save r1 test.pcap
    
    isip:packet>save r2 test.pcap # assume you have r2.0, r2.1, r2.2, r2.3 ...

使用wireshark命令，用[wireshark](https://www.kitploit.com/search/label/Wireshark)打开数据包：

    
    
    isip:packet>wireshark r1
    
    isip:packet>wireshark r2 # assume you have r2.0, r2.1, r2.2, r2.3 ...

使用hist命令查看操作记录：

    
    
    isip:packet>hist

使用shell或!命令执行Shell代码：

    
    
    isip:packet>shell ls -la
    
    isip:packet>! cat /etc/passwd

使用?或help命令查看帮助页面：

    
    
    isip>?
    
    isip>help
    
    isip:packet>?
    
    isip:packet>help
    
    isip:packet>help new
    
    isip:packet>help send
    
    isip:packet>help set
    
    isip:packet>help show

## 项目地址

GitHub主页：【[传送门](https://github.com/halit/isip)】

***参考来源：[isip](https://github.com/halit/isip)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

