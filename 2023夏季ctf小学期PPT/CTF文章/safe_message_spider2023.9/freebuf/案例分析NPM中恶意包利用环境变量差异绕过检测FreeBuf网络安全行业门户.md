> OSCS
> (开源软件供应链安全社区)推出免费的漏洞、投毒情报订阅服务，社区用户可通过机器人订阅情报信息：https://www.oscs1024.com/?src=fb

## 事件简述

2022年7月14日，OSCS 监测发现NPM仓库中上传了 branch-node-core、epic-ue-loading
两个恶意组件包，出自相同的模板，通过多种方式绕过静态、动态检测机制。

由于发现这些恶意组件包在不同环境中的运行结果并不相同，我们对代码进行了分析，发现这些恶意组件包会检测用户运行环境的特征，根据特征判断是否进入恶意逻辑。

接下来我们以 branch-node-core
为例，分析其中尝试绕过代码静态分析和运行时动态检测的手法，希望能帮助安全研究人员和开发者关注此类风险，更加了解其中的绕过手法。

### 详细分析

如下图 package.json 所示，branch-node-core 只会在安装和构建时使用 **`node build-utils/update-library.js`** 调用恶意代码

![](https://image.3001.net/images/20220715/1657860146_62d0f032244ce4966bdae.png!small)（branch-node-core/package.json）

攻击者首先在 **`update-library.js`** 中定义了一个名为 **`filter`** 的列表， **filter**
列表中的元素使用`join`来生成字符串，例如将`["mirrors", "tencent", "com"]
转`为`mirrors.tencent.com`。

`join`是为了尝试绕过静态检测对代码中特殊字符串的分析，其中存放着攻击者用来判断是否开启投毒的环境信息元素。

![](https://image.3001.net/images/20220715/1657860146_62d0f032ea4bbfb5b8be6.png!small)

（filter 列表代码片段）

代码随后对环境信息进行了判断，在`data`中传入了环境变量，然后一共判断了 6
个条件，这些条件使用`||`连接，任一条件的返回值为`true`，将不会去调用`var req = http.request`，执行恶意代码。  
![](https://image.3001.net/images/20220715/1657860147_62d0f033af5bb23fdb2c4.jpeg!small)

（判断环境信息的表达式）

* * *

#### 1.判断环境变量内容

表达式的第一个条件：判断运行环境内的环境变量是否符合目标真实服务器的环境变量模板。

  * some() 方法用于检测数组中的元素是否满足指定条件（通过将元素传入匿名函数来判断条件），当匿名函数返回值为 true 则停止继续运行，直接返回 true。

  * every() 方法用于检测数组所有元素是否都符合指定条件（通过将元素传入匿名函数来判断条件），当匿名函数返回值为 false 则停止继续运行，直接返回 false。

攻击者通过结合 some 和 every 方法来将环境变量 data 与`filter`列表内的每一个元素进行比对，如果环境变量 data 完全包含
filter 的中的任一元素，则返回 true。

例如如果环境变量中包含`npm_config_registry=``registry.npmmirror.com ，`则表达式返回
true，不会执行恶意代码。

![](https://image.3001.net/images/20220715/1657860148_62d0f0345bc9a9c5bca69.png!small)

( 判断环境变量内容)

#### 2.判断环境变量数量

表达式的第二个条件：判断本机系统的环境变量的个数是否大于 10 个。

一般真实服务器的环境数量都大于 10，攻击者借此判断是否为沙箱环境，若本机环境变量的个数不满足 10
个，那么第二个条件就会返回`true`，不会执行恶意代码。

![](https://image.3001.net/images/20220715/1657860148_62d0f034f23857acfc771.png!small)

（判断环境变量数量）

#### 3.判断当前目录

表达式的第三个条件：判断当前路径是否为用户默认的 NPM 包存放路径

![](https://image.3001.net/images/20220715/1657860149_62d0f035a1674dd1c7ed9.png!small)

（判断当前目录）

#### 4.判断是否有流量分析

表达式的第四个条件：判断环境信息内是否存在`mitmproxy`代理劫持工具进行流量分析

![](https://image.3001.net/images/20220715/1657860150_62d0f036433ad22dd31a4.png!small)

（判断是否存在代理）

#### 5.判断 NPM 包名是否存在

表达式的第五和第六个条件：会去判断环境信息中是否存在`NPM`的包名与版本

![](https://image.3001.net/images/20220715/1657860150_62d0f036d2f8f42a8b23d.png!small)

（判断NPM包名是否存在)

当`if`判断的表达式均为`false`时，接下来会通过http方法试图请求 eo1ew7v449gkbah.m.pipedream.net
域名，将环境变量中的敏感数据发送给恶意域名

![](https://image.3001.net/images/20220715/1657860151_62d0f0377f25ab73ff446.png!small)

(传输敏感数据)

## 总结

目前 branch-node-core 和 epic-ue-loading 的下载数量分别为 532、318，OSCS 推测有用户可能已经安装了恶意组件。

![](https://image.3001.net/images/20220715/1657860152_62d0f0383d2d730d32393.png!small)![](https://image.3001.net/images/20220715/1657860152_62d0f038b4d8f7e9e6bb0.png!small)

通过分析 branch-node-core
我们可以发现其使用的多种绕过检测方式，类似这样的情况可能还有很多，对抗也会持续。对企业安全团队来说，需要持续提升风险检测防范能力；对于开发者而言，在引入项目依赖时需要注意甄别。

## 了解更多

 **1\. 免费使用 OSCS 的情报订阅服务**

OSCS
（开源软件供应链安全社区）会第一时间发布开源项目最新的安全风险动态，包括开源组件安全漏洞、投毒情报等信息，社区用户可通过企微、钉钉、飞书等方式进行订阅。

具体订阅方式详见：

> https://www.oscs1024.com/docs/vuln-warning/intro/?src=fb

