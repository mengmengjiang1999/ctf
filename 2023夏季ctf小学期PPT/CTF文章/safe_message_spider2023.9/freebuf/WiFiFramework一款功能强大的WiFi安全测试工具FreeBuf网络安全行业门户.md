![](https://image.3001.net/images/20220121/1642699100_61e9995cbd27b3029c7bc.jpeg!small)  

## 关于Wi-Fi Framework

Wi-Fi Framework是一款功能强大的WiFi安全测试工具，该工具本质上来说是一个安全框架，可以帮助广大研究人员更轻松地执行Wi-Fi安全测试。除此之外，我们还可以利用Wi-Fi
Framework来创建模糊测试工具，设计新的测试方案，创建PoC以验证漏洞，自动化渗透测试或开发其他的漏洞测试工具。

该框架的主要优点是，它允许我们重用Linux的Wi-Fi功能，以便更轻松地实施安全测试。比如说，该框架可以帮我们连接（受保护的）Wi-Fi网络，并在测试客户端时为我们广播信标。一般来说，Linux的任何Wi-Fi功能都可以重用，以更快地实施安全测试。

## Wi-Fi Framework架构

下图显示的是Wi-Fi Framework中Wi-Fi守护进程和框架组件架构：

![](https://image.3001.net/images/20220121/1642699214_61e999ce6fba0c2523f10.png!small)

## 工具安装

该框架可以在本地Linux系统或虚拟机环境中运行。

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/domienschepers/wifi-framework.git

接下来，使用下列命令安装工具所需的依赖组件：

    
    
    apt-get update
    
    apt-get install git make gcc python3-venv net-tools
    
    apt-get install libdbus-1-dev libnl-3-dev libnl-genl-3-dev libnl-route-3-dev libssl-dev

安装完成之后，使用下列命令安装框架：

    
    
    cd ../dependencies
    
    ./build.sh
    
    cd ../setup
    
    ./pysetup.sh

### Libwifi

libwifi库作为一个git只模块使用，需要手动安装：

    
    
    git submodule init
    
    git submodule update

## 工具使用

初始化并激活Python环境：

    
    
    source setup/venv/bin/activate

模拟Wi-Fi网络接口：

    
    
    ./setup-hwsim.sh 4

运行工具并创建测试用例：

    
    
    usage: run.py [-h] [--config CONFIG] [--binary BINARY] [--debug DEBUG] iface name

指定网络配置信息：

    
    
    cd setup
    
    ln -s supplicant-wpa3-personal.conf supplicant.conf

## 工具使用样例

假设我们现在需要测试客户端是否使用全零密钥去加密帧数据，而这种情况可能发生在密钥重新安装攻击期间。那么在Wi-Fi
Framework的帮助下，我们无需重新实现接入点的所有功能，只需编写以下测试用例即可：

    
    
    class ExampleKrackZerokey(Test):
    
    name = "example-krack-zero-key"
    
    kind = Test.Authenticator
    
     
    
    def __init__(self):
    
    super().__init__([
    
    # Replay 4-Way Handshake Message 3/4.
    
    Action( trigger=Trigger.Connected, action=Action.Function ),
    
    # Receive all frames and search for one encrypted with an all-zero key.
    
    Action( trigger=Trigger.NoTrigger, action=Action.Receive ),
    
    # When we receive such a frame, we can terminate the test.
    
    Action( trigger=Trigger.Received, action=Action.Terminate )
    
    ])
    
     
    
     
    
    def resend(self, station):
    
    # Resend 4-Way Handshake Message 3/4.
    
    station.wpaspy_command("RESEND_M3 " + station.clientmac )
    
     
    
     
    
    def receive(self, station, frame):
    
    if frame[Dot11].addr2 != station.clientmac or not frame.haslayer(Dot11CCMP):
    
    return False
    
     
    
    # Check if CCMP-encrypted frame can be decrypted using an all-zero key
    
    plaintext = decrypt_ccmp(frame.getlayer(Dot11), tk=b"\x00"*16)
    
    if plaintext is None: return False
    
     
    
    # We received a valid plaintext frame!
    
    log(STATUS,'Client encrypted a frame with an all-zero key!', color="green")
    
    return True

上面的测试用例将创建一个客户端能够连接的接入点。客户端连接后，它将向客户端发送4路握手消息。接下来，易受攻击的客户端将开始使用全零加密来密钥，随后测试用例将会自动检测到这一情况。

我们也可以使用模拟Wi-Fi来运行上述测试用例：

    
    
    ./setup/setup-hwsim.sh 4
    
    source setup/venv/bin/activate
    
    ./run.py wlan1 example-krack-zero-key

## 项目地址

 **Wi-Fi Framework：** 【[ _GitHub传送门_](https://github.com/domienschepers/wifi-framework)】

## 参考资料

> [
> _https://github.com/vanhoefm/libwifi_](https://github.com/vanhoefm/libwifi)
>
> [ _https://www.krackattacks.com/#demo_](https://www.krackattacks.com/#demo)
>
> [
> _https://dl.acm.org/doi/10.1145/3448300.3468261_](https://dl.acm.org/doi/10.1145/3448300.3468261)
>
> [
> _https://github.com/vanhoefm/fragattacks_](https://github.com/vanhoefm/fragattacks)
>
> [ _https://github.com/domienschepers/wifi-> framework/blob/master/docs/EXAMPLES.md_](https://github.com/domienschepers/wifi-> framework/blob/master/docs/EXAMPLES.md)

