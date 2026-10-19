**今天给大家介绍的是一款名叫DNS-Shell的交互工具，在该工具的帮助下，研究人员可通过DNS信道来实现交互式Shell。**

![１.png](https://image.3001.net/images/20190319/1553009167_5c910a0f851f7.png!small)  

## DNS-Shell

DNS-Shell是一款通过DNS信道实现交互式Shell的强大工具，该工具的服务器端基于Python开发，可在任何一种安装了Python环境的操作系统平台上运行，工具所使用的Payload均已PowerShell命令进行编码，保证了在不同平台间运行的稳定性和兼容性。

## DNS-Shell运行机制

该工具所使用的Payload会在服务器端脚本被调用时自动生成，Payload会使用nslookpu来向服务器端查询和请求新的操作命令，接下来服务器端会监听端口53并等待传入的连接。当Payload在目标设备上成功执行后，服务器端将会生成一个交互式Shell并提供给用户进行操作。

通信信道建立成功后，Payload会继续向服务器查询和请求新的操作指令，当攻击者在服务器端输入新的操作命令后，Payload将会收到命令并执行该命令，然后在命令执行成功后将执行结果返回给服务器端。

## 使用DNS-Shell

DNS-Shell的运行相对来说比较简单，DNS-Shell支持两种操作模式，即直接操作模式和递归模式：

### -使用git命令将工具从GitHub代码库克隆到本地：

    
    
    git clone https://github.com/sensepost/DNS-Shell.git

### -DNS-Shell直接模式：

    
    
    sudo python DNS-Shell.py -l -d [Server IP]

### -DNS-Shell递归模式：

    
    
    sudo python DNS-Shell.py -l -r [Domain]

## 项目地址

DNS-Shell：【[GitHub传送门](https://github.com/sensepost/DNS-Shell)】

 ***参考来源：[sensepost](https://github.com/sensepost/DNS-Shell)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

