## 关于blaster

blaster是一款强大的弱密码隐患检测工具，用于网站登录弱密码检测。旨在解决登录测试中因为图片验证码、登陆处加密等无法直接进行弱密码检测的问题。他的主要特性有：

> 支持复选框勾选：主要场景为阅读平台使用须知、 隐私政策单选表单等。
>
> 支持复杂场景的事件操作：可根据不同场景，在登录前后自定义事件操作。
>
> 支持正则匹配反向过滤：应对不同响应类型、长度，提取关键信息进行反向过滤。
>
> 图片验证码识别：采用python第三方库进行ocr识别。
>
> 无视任何加密方式：它将用户名及密码字典填充至对应表单进行提交，无需逆向加密方式。
>
> 支持多次输入账号密码错误才出现验证码情况。
>
> 支持多并发。

## 系统要求

> 弱密码检测客户端：目前仅支持Windows运行
>
> 验证码识别服务端：无系统限制，操作系统中必须有Python3。

## 下载运行

### 下载地址

`https://github.com/jixing-lab/blaster/releases`

### 运行：

服务端（captcha_break_http_server）

`pip install -r requirements.txt``python cbhs.py -a user:pass -p 8999``-a
user:pass`

自定义账号密码

`-p 8999`

指定端口

客户端（先配置配置文件`conf.yaml`后在进行使用）

`.\blaster_win.exe -c conf.yaml -u user.txt -p pass.txt -o res.csv``-c`

指定config.yaml

`-u`

指定用户名字典

`-p`

指定密码字典

`-o`

测试数据输出文件位置

## 配置文件

### 概述

运行客户端之前，需要对目录内的`conf.yaml`进行配置，通过调整配置中的参数来满足我们在不同场景的需求。在修改配置时，请务必理解该项的含义后再修改，否则可能会导致非预期的情况。

### 登录目标设置

在配置文件中`target_url`设置登录目标网址  
•示例  
`target_url: 'http://www.example.com/login'`

### 浏览器路径配置

在配置文件中`browser_path`设置浏览器路径  
•示例  
`browser_path: 'C:\Program Files\Google\Chrome\Application\chrome.exe'`  
浏览器路径获取  
![浏览器路径配置](https://image.3001.net/images/20220507/1651914914_627638a2357a497d4cbdc.png!small)

### 运行浏览器状态

在配置文件中`headless`设置运行时浏览器是否显示运行  
•示例  
`headless: false`false：显示浏览器运行， true则反之。

### 服务端连接配置

在配置文件中`captchabreak_serverurl`配置与服务端的连接。  
•示例  
`captchabreak_serverurl:
'http://user:[pass@127.0.0](mailto:pass@127.0.0).1:8999/cb'`  
`user:pass`启动服务端时所设置的账号密码  
`127.0.0.1`服务端ip地址  
`8999`启动服务端时所设置的端口ip

### js path配置

配置文件中通过js path设置来定位用户名、密码、验证码、登录按钮位置，从而进行登录测试。

  1. `userinput_jspath: 'document.querySelector("#loginid")'# 用户名输入框js path`
  2. `passinput_jspath: 'document.querySelector("#security_in")'# 密码输入框js path`
  3. `captchainput_jspath: 'document.querySelector("#jcaptcha")'# 验证码输入框js path`
  4. `captchaimg_jspath: 'document.querySelector("#vcode")'# 验证码图片js path`
  5. `loginbutton_jspath: 'document.querySelector("#vcode")' # 登录按钮js path`

js path获取方式：  
![js
path获取方式](https://image.3001.net/images/20220507/1651914916_627638a4082e85d75fc3e.png!small)  
![](https://image.3001.net/images/20220507/1651914918_627638a6e394f233a76a3.png!small)

### js表达式设置

js表达式是为了在用户登录前或登录后，需要对确定协议等特殊情况。用户可以根据场景编辑不同的js表达式。

  1. `before_all_js_expr: '' # 在开始填写账号密码之前执行的js表达式`
  2. `before_login_js_expr: '' # 在点击登录之前执行的js表达式`

  * 示例场景：页面出现弹出层，需要关闭弹窗才能进行操作。
  * 示例解决弹出层：判断某按钮（弹出层关闭按钮X）是否存在，如果存在则点击；找出关闭按钮的js path按照格式编写代码即可。

  1. `null != jspath && jspath.click() // js代码格式`

  * 表达式不限于一个，如有其他场景或多个弹出层，可通过 && 或 || 进行叠加

###

登录请求的url特征码  
在配置文件中`loginreq_pattern`设置实际的登录数据包的url路径，前后加通配符`*`  
•示例  
`loginreq_pattern:'*sys/login*'`  
实际登录数据包url获取方式：  
![](https://image.3001.net/images/20220507/1651914919_627638a783c8907b2b9b6.png!small)

### 请求正则表达配置

  * 排除请求的正则，即只要命中其中任意一个正则的请求响应将被抛弃，即反向grep。
  * 示例场景：登录后的响应页面长度较大，返回格式为HTML，其中有（账号不存在、密码错误、验证码错误、登录成功）等不同情况，由于响应长度较大我们无法轻易区分测试数据的真实响应情况。
  * 示例解决响应长度较大问题：经过手工登录测试发现响应的HTML中出现这些关键信息（如账号不存在、密码错误、验证码错误），根据自己的需求，编写正则表达式，在发现响应中存在这些匹配内容时不输出到终端及结果文件中。
  * 这里需要具备一些正则表达式的技能，如果使用者技能有些欠缺，可以直接使用关键信息进行排除，或是在交流群内寻求帮助。

  1. `body_exclude_regex:`
  2. `- '账号不存在'`
  3. `- '验证码错误'`

  * 该参数不限于一个表达式，使用者根据自己的需求来增删表达式即可。

### 响应包限制

在配置文件中`maxbody_bytes_display`来设置登录请求响应包最大限制，当超过限制请求响应包具体内容不会显示，只会显示请求响应包的长度。

  * 示例

`maxbody_bytes_display: 512`  
通常请求响应包为html格式时会超出限制，用户可以根据自己的需求自行调整限制。

### 并发数设置

在配置文件中`concurrency`来设置并发数，利用多开浏览器同时工作。  
•示例  
`concurrency: 2`开启两个服务器同时进行登录测试。

### 操作超时设置

•示例  
`timeout_ms: 50000`浏览器中操作的超时时间(毫秒)

### 操作间隔设置

•示例  
`timeinterval_ms: 300`浏览器中操作登录过程中每个操作之间的时间间隔(毫秒)

### 代理设置

•示例  
`proxy: ''`# 代理

## 视频演示

<https://www.bilibili.com/video/BV1hi4y1m7jf?share_source=copy_web>

免责声明

该工具仅用于安全自查检测。由于传播、利用此工具所提供的信息而造成的任何直接或者间接的后果及损失，均由使用者本人负责，作者不为此承担任何责任。

作者拥有对此工具的修改和解释权。未经网络安全部门及相关部门允许，请勿善自使用本工具进行任何攻击活动，请勿以任何方式将其用于商业目的。

## 交流群加入

群满请扫描下方二维码邀请进入，备注blaster  
![](https://image.3001.net/images/20220507/1651914920_627638a81e8b24c30a352.png!small)

