点击重启机器，在重启时不断的按键盘上的向上的方向键，调出启动菜单（可能要尝试很多次）

![](https://image.3001.net/images/20220902/1662123264_6311fd0015ccafa40e4b6.png!small)

按e进入内核加载的配置行

![](https://image.3001.net/images/20220902/1662123277_6311fd0d230c0ccf32461.png!small)

将其修改为单用户模式

修改前

![](https://image.3001.net/images/20220902/1662123289_6311fd196f86b6ef5a427.png!small)

修改后

rw single init=/bin/bash

![](https://image.3001.net/images/20220902/1662123301_6311fd259f0cfe68c44fe.png!small)

按住ctrl+x进入单用户模式

![](https://image.3001.net/images/20220902/1662123314_6311fd3239b55ce6e1e5b.png!small)

输入ip a，查看当前网卡信息

![](https://image.3001.net/images/20220902/1662123327_6311fd3f14843bf60cb6e.png!small)

    
    
    vi /etc/network/interfaces
    或者
    vi /etc/netplan/00-installer-config.yaml
    
    哪个文件存在就修改哪个配置文件,不同系统配置文件不同(存在的话可以输入一部分table键自动补全路径)

我这里是/etc/network/interfaces进入之后提示我ifipdown已经被netplan(5)代替了，让我去/etc/netplan下找配置文件

![](https://image.3001.net/images/20220902/1662123373_6311fd6d2497aaff2df21.png!small)![](https://image.3001.net/images/20220902/1662123383_6311fd77d34708e4b79b1.png!small)

vi 50-cloud-init.yaml

![](https://image.3001.net/images/20220902/1662123404_6311fd8c879bc8c1082ed.png!small)

发现网卡名称不正确，修改为正确的就行

![](https://image.3001.net/images/20220902/1662123418_6311fd9ad3b45e30b3a70.png!small)

重启计算机正常进入系统。

