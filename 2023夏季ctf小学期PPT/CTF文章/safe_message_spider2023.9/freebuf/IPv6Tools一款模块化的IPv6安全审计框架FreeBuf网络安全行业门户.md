![](https://image.3001.net/images/20200211/1581433167_5e42c14fd1273.jpg!small)

**IPv6Tools是一款功能健壮的IPv6功能审计框架，该框架以模块化架构实现，并且集成了大量功能模块和插件来帮助用户对启用了IPv6的网络进行安全审计。框架内置的模块支持枚举类似ICMPv6和组播监听器（MLD）之类的IPv6功能，除此之外，框架还支持枚举类似多播DNS（MDN）和本地链路多播名称解析（LLMNR）之类的上层协议（ULP）。广大研究人员可以根据自己的需求，通过使用Python语言创建插件和模块来扩展IPv6Tools的功能。**

##  工具要求

> python 2.7
>
> pip
>
> npm [仅开发者使用]

##  工具安装

###  标准用户安装

运行下列命令，在虚拟环境中安装源码：

    
    
    virtualenv venv && source venv/bin/activate
    
        git clone <http://github.com/apg-intel/ipv6tools.git>
    
        sudo pip install -r requirements.txt

###  开发者安装

    
    
    git clone <http://github.com/apg-intel/ipv6tools.git>
    
        git checkout dev
    
        npm run setup

##  工具使用

###  标准用户

运行下列命令启用框架脚本：

    
    
    sudo python app.py

打开Web浏览器，输入并访问下列地址：

    
    
    http://localhost:8080

###  开发者

运行下列命令启用服务：

    
    
    $ npm run serve

打开另一个终端窗口，然后运行下列命令：

    
    
    npm run dev

打开Web浏览器，输入并访问下列地址：

    
    
    http://localhost:8081

##  功能模块

IPv6Tools框架中的功能模块允许与单个节点或所有节点进行交互，用户可以直接在图形界面右键点击节点按钮来进行操作。

###  内置模块

该项目内置的的模块可以帮助研究人员验证目标网络，或测试自己的自定义模块。

poisonLLMNR：本地链路多播名称解析（LLMNR）继承了NBT-NS，它允许本地节点来解析域名或IP地址。启用该模块将会篡改本地链路中发送至所有节点的LLMNR查询。

CVE-2016-1879：该漏洞是SCTP中的一个漏洞，FreeBSD
v9.3、v10.1和v10.2都存在这个漏洞。启用该模块之后，将会发送特制的ICMPv6数据包，并可能导致单一节点出现DoS。

###  自定义模块

所有的模块都位于/modules目录中，并且在启动服务器时会进行自动加载。/modules目录中有一个名为template.py的文件，该文件中包含了所有模块都需要继承的类，以便在Web页面中正确显示并完成通信。

广大研究人员可以使用下列模块来自定义构建模块：

    
    
    from template import Template
    
        class IPv6Module(Template):
    
          def __init__(self, socketio, namespace):
    
            super(IPv6Module, self).__init__(socketio, namespace)
    
            self.modname = "CVE-2016-1879"
    
            self.menu_text = "FreeBSD IPv6 DoS"
    
            self.actions = [
    
              {
    
                "title": "FreeBSD IPv6 DoS", #name that's displayed on the buttons/menu
    
                "action": "action", #method name to call
    
                "target": True #set this to true to display it in the right-click menu
    
              }
    
            ]
    
          def action(self, target=None):
    
            # send a log msg
    
            self.socket_log('Running DoS on '+target['ip'])
    
            # do stuff, etc
    
            # merge results with main result set
    
            listOfDicts = [{ip: '::1', device_name: 'test'}]
    
            self.module_merge(listOfDicts)
    
    ###     libdnet安装
    
        git clone <https://github.com/dugsong/libdnet.git>
    
        cd libdnet
    
        ./configure && make
    
        sudo make install
    
        cd python
    
        python setup.py install

###  libpcap安装（Ubuntu）

    
    
    sudo apt install libpcap-dev

##  IPv6Tools扫描网络

![](https://image.3001.net/images/20200211/1581433259_5e42c1ab5b0a7.gif!small)

##  项目地址

> IPv6Tools：【[GitHub传送门](https://github.com/apg-intel/ipv6tools)】

##  参考资料

> 1、<https://secdevops.ai/theres-no-place-like-1-enumerating-local-> ipv6-networks-88a6247e3519>
>
> 2、<https://secdevops.ai/>

 ***参考来源：[apg-intel](https://github.com/apg-intel/ipv6tools)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

