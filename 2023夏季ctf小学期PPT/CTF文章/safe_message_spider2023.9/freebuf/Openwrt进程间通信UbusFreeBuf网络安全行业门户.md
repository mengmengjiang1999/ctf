**目 录**

  1. 一. 介绍

1.1 模型架构

  1. 二. 交互方式

2.1 Ubus Cli

2.2 HTTP访问

  1. 三. 会话管理
  2. 四. 挖掘潜在漏洞

4.1 文件目录泄露

4.2 任意文件读取

  1. 五. 参考

  

# 一. 介绍

Ubus是Openwrt中的进程间通信机制，它让进程间通信的实现变得非常简单。ubus实现的基础就是UNIX
Socket，即本地Socket，相对于传统的网络通信Socket变得更加的高效、可靠。

## 1.1 模型架构

UNIX Socket采用C/S模型架构，分为服务端和客户端:

  1. server端建立socket，绑定到一个本地socket文件，负责监听客户端的连接
  2. client端建立一个或多个socket连接到服务端
  3. client端和server端互相发送消息
  4. client端和server端收到对方消息后，对收到消息进行对应处理

Ubus同样遵循上述流程，Ubusd实现server端，其它进程(如procd、netifd、ubus)实现client端，client之间通信需要通过服务端进行相应转发。

# 二. 交互方式

## 2.1 Ubus Cli

命令行Ubus工具与Ubusd交互(与所有当前注册)，对于使用参数调用过程返回响应，使用较为友好的JSON格式。

查看当前运行服务(如图1-1 当前运行服务)

$ ubus  
  
---  
  
![1658369325_62d8b52defe20d5485610.png!small?1658369326552](https://image.3001.net/images/20220721/1658369325_62d8b52defe20d5485610.png!small?1658369326552)

图1-1 当前运行服务

查找特定服务参数及方法(如图1-2 查找特定服务)

$ ubus -v list system  
  
---  
  
![1658369339_62d8b53baeba6d27615a9.png!small?1658369340508](https://image.3001.net/images/20220721/1658369339_62d8b53baeba6d27615a9.png!small?1658369340508)

图1-2 查找特定服务

查看特定服务特定参数(如图1-3 查看特定参数)

$ ubus call network.interface.lan status  
  
---  
  
![1658369358_62d8b54e310e43773a5c3.png!small?1658369358703](https://image.3001.net/images/20220721/1658369358_62d8b54e310e43773a5c3.png!small?1658369358703)

图1-3 查看服务特定参数

服务参数传递(图1-4 服务参数传递)

$ ubus call network.interface.lan status ‘{“name”:”eth0”}’  
  
---  
  
![1658369677_62d8b68d68c9a7b2883a2.png!small?1658369678001](https://image.3001.net/images/20220721/1658369677_62d8b68d68c9a7b2883a2.png!small?1658369678001)

图1-4 服务参数传递

## 2.2 HTTP访问

Openwrt uhttpd内置了一个uhttpd-mod-ubus插件运行http协议调用ubus功能，uhttpd中访问/ubus,首先会判断访问者是否有权限。Openwrt中ACl的实现主要通过rpcd，需要在/usr/share/rpcd/acl中配置acl文件。

以下是ACL定义示例，该示例仅允许访问某些特定的ubus模块，而不是无限制访问所有内容

luci-mod-system.json

{

"luci-mod-system-config": {

"description": "Grant access to system configuration",

"read": {

"ubus": {

"luci": [ "getInitList", "getLEDs", "getTimezones", "getUSBDevices" ],

"system": [ "info" ]

},

"uci": [ "luci", "system" ]

},

"write": {

"ubus": {

"luci": [ "setInitAction", "setLocaltime", "setPassword" ]

},

"uci": [ "luci", "system" ]

}

},

"luci-mod-system-ssh": {

"description": "Grant access to SSH configuration",

"read": {

"file": {

"/etc/dropbear/authorized_keys": [ "read" ]

},

"ubus": {

"file": [ "read" ]

},

"uci": [ "dropbear" ]

},

"write": {

"file": {

"/etc/dropbear/authorized_keys": [ "write" ]

},

"ubus": {

"file": [ "write" ],

"luci": [ "setInitAction", "setLocaltime" ]

},

"uci": [ "dropbear" ]

}

},

.............

"luci-mod-system-reboot": {

"description": "Allow rebooting the device",

"write": {

"file": {

"/sbin/reboot": [ "exec" ]

},

"ubus": {

"file": [ "exec" ],

"system": [ "reboot" ]

}

}

}

}  
  
---  
  
注意:

rpcd处理接口请求同时也需要预验证，配置登录文件为/etc/config/rpcd

config rpcd

option socket /var/run/ubus/ubus.sock

option timeout 30

config login

option username 'root'

option password '$p$root'

list read '*'

list write '  
  
---  
  
登录请求(获取rpc_session)

$ curl -d '{"jsonrpc": "2.0", "id": 1, "method": "call", "params": [
"00000000000000000000000000000000", "session", "login", {"username": "root",
"password": "secret" }]}' http://your.server.ip/ubus

{

"jsonrpc":"2.0",

"id":1,"result":

[0,

{

"ubus_rpc_session":"c1ed6c7b025d0caca723a816fa61b668",

"timeout":300,

"expires":299,

"acls":

{

"access-group":

{

"superuser":["read","write"],

"unauthenticated":["read"]

},

"ubus":

{

"*":["*"],

"session":["access","login"]},

"uci":{"*":["read","write"]}

},

"data":{"username":"root"}}]}  
  
---  
  
# 三. 会话管理

获取ubus_rpc_session就可以调用函数(图2-1 获取rpc session)

![1658369695_62d8b69f2672581784d38.png!small?1658369695716](https://image.3001.net/images/20220721/1658369695_62d8b69f2672581784d38.png!small?1658369695716)

图2-1 获取rpc session

请求头包格式

{ "jsonrpc": "2.0",

"id": <unique-id-to-identify-request>,

"method": "call",

"params": [

<ubus_rpc_session>,

<ubus_object>,//system

<ubus_method>, //board

{ <ubus_arguments> }

]

}  
  
---  
  
数据包响应错误码

enum ubus_msg_status {

UBUS_STATUS_OK,/* 0 */

UBUS_STATUS_INVALID_COMMAND,/* 1 */

UBUS_STATUS_INVALID_ARGUMENT,/* 2 */

UBUS_STATUS_METHOD_NOT_FOUND,/* 3 */

UBUS_STATUS_NOT_FOUND,/* 4 */

UBUS_STATUS_NO_DATA,/* 5 */

UBUS_STATUS_PERMISSION_DENIED,/* 6 */

UBUS_STATUS_TIMEOUT,/* 7 */

UBUS_STATUS_NOT_SUPPORTED,/* 8 */

UBUS_STATUS_UNKNOWN_ERROR,/* 9 */

UBUS_STATUS_CONNECTION_FAILED,/* 10 */

__UBUS_STATUS_LAST

};

{“jsonrpc”:“2.0”,”id“:1,”result“:[6]}`

That is a valid jsonrpc response, 6 is the ubus code for
UBUS_STATUS_PERMISSION_DENIED  
  
---  
  
# 四. 挖掘潜在漏洞

请求方式

File

  1. read
  2. list
  3. write

UCI

  1. set
  2. get
  3. show

## 4.1 文件目录泄露

![1658369710_62d8b6ae0f0092489f666.png!small?1658369710667](https://image.3001.net/images/20220721/1658369710_62d8b6ae0f0092489f666.png!small?1658369710667)

## 4.2 任意文件读取

![1658369719_62d8b6b7c5bfe497ee706.png!small?1658369720392](https://image.3001.net/images/20220721/1658369719_62d8b6b7c5bfe497ee706.png!small?1658369720392)

设置权限的原因导致任意文件读取失败

# 五. 参考

https://openwrt.org/zh/docs/techref/ubus

