## Web Fuzzer 的海量发包优化

### 背景

Web Fuzzer 作为 Repeater 和 Intruder 的一个比较完美的集合，同时也是 “渗透测试” 同学非常高频使用的功能：我们尝试在 Web
Fuzzer 上做了非常大量的优化和调整

### 基础介绍

[Web Fuzzer: MORE than Repeater +
Intruder](https://www.freebuf.com/sectool/324384.html)

### 热加载 Fuzz 强化

[Yakit Web Fuzzer 终极能力强化：热加载
Fuzz](https://www.freebuf.com/sectool/332243.html)

随着大家的深入使用和大量用户反馈，我们可以挖掘出 Web Fuzzer 的一些明显局限：在字典量大和大量爆破场景的时候，我们前端数据量巨大导致 “筛选”
甚至 “渲染” 时的异常卡顿。

## 如何解决？

我们在新版本 (Yakit >= 1.0.14-sp13) 中支持了可以在 “高级设置” 中配置 “过滤器”，可以匹配 “用户感兴趣的内容”：

![1653292038_628b3c06e2eb6278991c0.jpg!small?1653292039137](https://image.3001.net/images/20220523/1653292038_628b3c06e2eb6278991c0.jpg!small?1653292039137)

我们可以配置 “状态码 / 关键字 / 正则” 过滤器，来匹配用户感兴趣的内容，丢弃掉不符合要求的数据包，以此来换取内容流畅并且适宜 “长时间” 开启
“大量” 工作。

### Quick View

我们把上述流程用朴素的时序图展示，其实非常简单：

  1. 用户设置要测试的包
  2. 设置排除选项
  3. 发送
  4. Yakit 根据响应中的 “是否匹配到用户设置条件” 字段来进行客户端丢弃数据

![1653293219_628b40a309370bdbb5e47.jpg!small?1653293219327](https://image.3001.net/images/20220523/1653293219_628b40a309370bdbb5e47.jpg!small?1653293219327)

  

## 案例：尝试对 250000 (25w) 个用户密码对进行爆破

我们首先指定一个非常非常常见的场景，我们针对一个 500 * 500 的爆破场景进行支持：

我们使用 Yak 语言构建一个比较简单的 “靶场”：当用户名和密码都为 “500” 的时候，我们返回登陆成功，否则返回登陆失败。

`httpserver.Serve("0.0.0.0", 8883, httpserver.handler(func(writer, req) { `

``

`url := str.ExtractURLFromHTTPRequest(req, false)[0] `

``

`username = re.FindSubmatch(url, `username=([^&]*)`)[1] `

``

`password = re.FindSubmatch(url, `password=(.*)`)[1] `

``

`if username == "500" && password == "500" { `

``

`writer.Write([]byte("登陆成功")) `

``

`return `

``

`} `

``

`writer.Write([]byte("登陆失败")) `

``

`})) `

``

  

![1653293230_628b40ae2ac55073391bd.jpg!small?1653293230611](https://image.3001.net/images/20220523/1653293230_628b40ae2ac55073391bd.jpg!small?1653293230611)

在我们配置了 “过滤器” 之后，轻松跑到上万请求并不会有任何卡顿的情况。情绪十分稳定

  

![1653293313_628b4101e4f761cb8edd6.jpg!small?1653293314175](https://image.3001.net/images/20220523/1653293313_628b4101e4f761cb8edd6.jpg!small?1653293314175)

  

# 甜品级功能：批量插件执行重构

在 yakit-v1.0.14-sp13 之前的版本中，我们的批量插件需要 “分类别”，手动
“多选”。给用户正常使用代理非常大的不便，同时，每一个任务都会保留过程和进度，让整个前端变得 “臃肿 / 卡顿 / 掉帧” 仅仅是一个 “勉强能用”
的程度。

对于执行日常合规任务 / 常规检查的用户，这有一点难以投入生产使用。

我们吸取了大量用户的建议，重构了这个功能，在保持原本 “目的” 的情况下，支持可以使用 Tag 作为依据扫描，同时仅保留关键结果和滚动日志，保证前端性能。

![1653291474_628b39d20c8d267c2c007.png!small?1653291478129](https://image.3001.net/images/20220523/1653291474_628b39d20c8d267c2c007.png!small?1653291478129)

![1653291565_628b3a2daf9df345c94fd.png!small?1653291571406](https://image.3001.net/images/20220523/1653291565_628b3a2daf9df345c94fd.png!small?1653291571406)

![1653291921_628b3b91b113c9cdcbad4.png!small?1653291926738](https://image.3001.net/images/20220523/1653291921_628b3b91b113c9cdcbad4.png!small?1653291926738)

# 用户交互优化：

  1. 对绝大多数允许 “多开” 的功能设置了 “通用二级 Tab 机制”，减少了 “Tab过多” 的糟糕用户体验
  2. HTTP History 新增 “无限滚动” 的功能
  3. MITM 新增 “Match && Replace” 这部分能力将在之后 “单独推文” 为大家介绍

# 引擎的例行更新：

### yak-1.0.15-sp2

  1. 优化 servicescan 指纹异常跳过的 BUG
  2. 优化 servicescan 扫描结果 HTTP Banner 不展示的不合理设计
  3. 优化 gRPC 端口扫描中 “上下文” 不独立导致的问题
  4. 优化部分插件以及配套表现
  5. 优化 risk.NewDNSLogDomain 的表现，屏蔽了代理对 gRPC 的影响
  6. 修复了导入插件无法覆盖之前 “is_general_module” 选项的 BUG

### yak-1.0.15-sp3

优化了 MITM 交互式劫持中对 deflate 的 zlib 和 flate 解码容错

### yak-1.0.15-sp4

  1. 修复 tomcat 爆破的问题
  2. 修复批量扫描流程中的过滤器的 BUG，优化了批量扫描调用远程插件的表现
  3. JSON 模块新增函数：Find / FindFirst 来支持 jsonpath，让 yak 提取 json 数据甚至不再需要 if else ，也减少了崩溃风险。

## END

如果你喜欢 Yakit，欢迎关注我们，或者加入小小的技术讨论组（进讨论组请添加微信Juzi19880818），关注我们的公众号（Yak
Project），立即获取最新的技术姿势。

官网教程：https://www.yaklang.io/products/intro

视频教程：https://space.bilibili.com/437503777

下载地址：https://github.com/yaklang/yakit

