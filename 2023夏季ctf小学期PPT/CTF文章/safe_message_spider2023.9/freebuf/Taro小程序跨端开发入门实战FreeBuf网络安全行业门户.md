## 背景

很多企业一开始只做微信小程序，随着业务不断扩张和各大小程序平台的崛起，针对每个平台都去写一套代码是不现实的。而且原生的小程序开发模式有很多弊端。

为了让小程序开发更简单，更高效，我们采用 Taro 作为首选框架，我们将使用 Taro 的实践经验整理了出来，主要内容围绕着什么是 Taro，为什么用
Taro，以及 Taro 如何使用（正确使用的姿势），还有 Taro 背后的一些设计思想来进行展开，让大家能够对 Taro 有个完整的认识。

Taro 3.0 已经逐渐成熟，我们项目已经进行了Taro 3.0的升级，因此本文代码示例以 Taro 3.0 作为基础。

## 什么是 Taro

Taro 是一个多端统一的开发框架。使用 taro 它可以支持 React 的开发方式，编写一次可以运行多端的代码，就能够生成可以在各种小程序，H5 甚至
React Native 等多端应用。

Taro 官方介绍：  
Taro 是一个开放式跨端跨框架解决方案，支持使用 React/Vue/Nerv 等框架来开发 微信 / 京东 / 百度 / 支付宝 / 字节跳动 / QQ
小程序 / H5/ React Native 等应用。现如今市面上端的形态多种多样，Web、React
Native、微信小程序等各种端大行其道，当业务要求同时在不同的端都要求有所表现的时候，针对不同的端去编写多套代码的成本显然非常高，这时候只编写一套代码就能够适配到多端的能力就显得极为需要。

它的主要特点是：  
快：可以快速开发小程序： 解决小程序开发各种痛点；  
多：可以实现多终端适配：一套代码适配小程序、H5、RN 等多终端；

## 为什么用 Taro

随着应用变得庞大之后，复杂度越来越高，原生小程序开发的痛点逐渐暴露出来：  
•代码组织复杂：写一个页面的文件结构繁琐（四个之多）  
•规范不统一：组件、方法命名规范不统一、各种书写方式，语法结构不一致像 React 又像 Vue  
•孱弱的字符串模板：逻辑表现力不强，不支持 eslint  
•依赖管理混乱：缺少 npm 包依赖管理  
•不完全的 ES Next：仅支持部分 ES Next 语法，比较新的 ES2020, ES2021+ 都不支持  
•落后的开发方式：前端工程体系不完善，webpack 打包，css 预处理等缺失，对于前端来说比较落后的，对个人成长也不利

####  **可选技术方案可选技术方案**

对于以上微信小程序开发模式的痛点，业界也给出了一些可选方案：  
![](https://image.3001.net/images/20220808/1659945646_62f0c2ae256ec5ea104c9.jpg!small)

![](https://image.3001.net/images/20220808/1659945646_62f0c2aec4bff85d88437.png!small)

#### 对比分析

![](https://image.3001.net/images/20220808/1659945647_62f0c2af5bb784a04edaf.png!small)

> mpvue 是美团研发的框架，多端适配效果不好，很久问题都没人维护；
>
> WePY 是腾讯出的组件化框架，但是无法适配多端；
>
> Chameleon 在多端适配方面表现很突出，缺点是不支持京东小程序，无法转换原生小程序（想用只能重写项目）；
>
> Taro 优秀的特性，遵循 React/Vue 语法规范，引入的现代化的开发流程，让开发更专注核心代码，提供健全的代码检查方式。

#### 多端需求

![](https://image.3001.net/images/20220808/1659945648_62f0c2b00775bfc0c6fa3.png!small)  
Taro 支持平台最全面，独具转换能力，性能方面优于其它框架，总结特点如下：

> 可以实现微信小程序原生代码转换到微信平台，百度平台等；
>
> Taro 框架是唯一一款实现京东小程序适配的框架；
>
> 支持 React/Vue 语法，更好的支持组件化和 TypeScript；
>
> 行业影响力大，社区活跃，京东内部优秀团队研发的框架，支持有保障，研发团队靠谱非常支持我们的工作；
>
> 更加完善的UI组件库，支持多端同步调试能够适配更多终端；

 **一处编写，多端运行**  
![](https://image.3001.net/images/20220808/1659945649_62f0c2b10b6a0ba178996.jpg!small)

## 设计思想

#### 主要采用 React 开发方式

![](https://image.3001.net/images/20220808/1659945649_62f0c2b196a8246ab61db.jpg!small)

#### 用 React 写多端应用

![](https://image.3001.net/images/20220808/1659945650_62f0c2b22588678b4b696.png!small)

#### 核心思想

代码转换：使代码可以在不同平台上运行  
运行时适配：使代码在不同平台上有相同表现

#### 以微信小程序为例以微信小程序为例

![](https://image.3001.net/images/20220808/1659945651_62f0c2b328291352645a7.jpg!small)

JSX  
![](https://image.3001.net/images/20220808/1659945651_62f0c2b3eb9a95f5b0e68.jpg!small)

WXML  
![](https://image.3001.net/images/20220808/1659945652_62f0c2b46926991d6a5f3.jpg!small)

#### Taro 代码编译原理

![](https://image.3001.net/images/20220808/1659945652_62f0c2b4dd39ec19f2b01.jpg!small)  
Taro 的编译原理：就是对输入的源代码进行语法分析，语法树构建，随后对语法树进行转换操作再解析生成目标代码的过程。

首先是 Parse，将代码解析（Parse）成抽象语法树（Abstract Syntex Tree），然后对 AST
进行遍历（traverse）和替换(replace)（这对于前端来说其实并不陌生，可以类比 DOM 树的操作），最后是生成（generate），根据新的
AST 生成编译后的代码。

开发时遵循 React 语法标准，结合编译原理的思想，对代码文件进行一系列转换操作，最终获得可以在小程序运行的代码。而 React 最开始就是为了解决
Web 开发而生的，所以对代码稍加改动，也可以直接生成在 Web 端运行的代码，而同属 React 语法体系下的 React
Native，也能够很便捷地提供支持。同理其他平台，如快应用、百度小程序等，将源码进行编译转换操作，也能获得该平台下的对应语法代码。

![](https://image.3001.net/images/20220808/1659945653_62f0c2b57e91210518b11.jpg!small)

![](https://image.3001.net/images/20220808/1659945654_62f0c2b65ee0c3f78e1dd.jpg!small)

![](https://image.3001.net/images/20220808/1659945655_62f0c2b701d75ae23a628.jpg!small)

![](https://image.3001.net/images/20220808/1659945655_62f0c2b7a670f246a1e3f.jpg!small)

可以看出小程序和 Web 端上组件标准与 API
标准有很大差异，这些差异仅仅通过代码编译手段是无法抹平的，例如你不能直接在编译时将小程序的直接编译。因为他们虽然看上去有些类似，但是他们的组件属性有很大不同的，仅仅依靠代码编译，无法做到一致，同理，众多
API 也面临一样的情况。针对这样的情况，Taro 采用了定制一套运行时标准来抹平不同平台之间的差异。

这一套标准主要以三个部分组成，包括标准运行时框架、标准基础组件库、标准端能力 API，其中运行时框架和 API 对应
[@taro](https://github.com/taro "@taro")/taro，组件库对应
[@tarojs](https://github.com/tarojs
"@tarojs")/components，通过在不同端实现这些标准，从而达到去差异化的目的。

#### 多端适配基础标准

> 基础框架（生命周期、组件API）：以React的生命周期、组件api为基础，小程序的特性作为补充
>
> 标准组件库（View、Button）: 以微信小程序组件为标准，各端模拟实现
>
> 标准Api （request、setState）：扩展的小程序标准Api，各端模拟实现

多端适配基础架构图如下：  
![](https://image.3001.net/images/20220808/1659945656_62f0c2b8620577cc4973d.jpg!small)

![](https://image.3001.net/images/20220808/1659945656_62f0c2b8e772ee2eec52e.jpg!small)

## 快速上手

#### 初始化项目

环境准备：需要有个 node 环境，运行 npm 命令：

![](https://image.3001.net/images/20220808/1659945657_62f0c2b97bb74d51f3ded.png!small)

![](https://image.3001.net/images/20220808/1659945658_62f0c2ba00ca06ec67edd.png!small)

开始使用 Taro 编写页面：  
![](https://image.3001.net/images/20220808/1659945658_62f0c2ba70873e83b020d.png!small)

#### 运行项目

![](https://image.3001.net/images/20220808/1659945658_62f0c2baed41ed93df55f.png!small)

#### 多平台启动命令示例：

![](https://image.3001.net/images/20220808/1659945659_62f0c2bb7747b660ca86e.png!small)

如果同时看三端效果：分别运行以上命令即可；

#### 微信原生小程序转换 Taro 小程序

![](https://image.3001.net/images/20220808/1659945660_62f0c2bc23790f313eb88.png!small)

#### Taro 项目的组成

![](https://image.3001.net/images/20220808/1659945660_62f0c2bc9860ab19c25d1.png!small)

#### Taro项目目录结构

基本的目录结构：  
![](https://image.3001.net/images/20220808/1659945661_62f0c2bd4c966125bbb8b.png!small)

比较完整的多端项目结构：  
![](https://image.3001.net/images/20220808/1659945661_62f0c2bddfd6c386c1ca4.png!small)  
![](https://image.3001.net/images/20220808/1659945662_62f0c2be77fe7873e831d.png!small)

完整的文档请访问：<https://taro-docs.jd.com/>

## 多端适配

#### 多终端配置文件编写

•微信的配置文件 project.config.json，文件内容可以自定义微信小程序的选项，运行的目录和 appid 等；  
•百度小程序的配置文件 project.swan.json 内容和微信类似；  
•京东小程序的配置文件 project.jd.json 内容和微信类似；  
•其它平台的小程序都有独立的配置文件便于运行的调试；  
![](https://image.3001.net/images/20220808/1659945663_62f0c2bf204ab97e0b9b4.jpg!small)

#### 多终端入口文件

每个平台有不同的页面配置信息：  
•微信小程序页面是全量的，有微信登录页面（其它平台不需要）；  
•百度小程序有专门的登录页面有些页面百度不支持需隐藏比如：图片裁剪，达达同城，打印等；  
•京东小程序：不支持批量寄，不需要登录页面，不支持分包，都要写入主包中；

  

![](https://image.3001.net/images/20220808/1659945663_62f0c2bfbe23529ca84ad.jpg!small)

#### 差异化配置

> 不同平台加载对应的文件：
>
> 每个平台差异化配置信息：
>
> 地图类型；
>
> 渠道信息；
>
> 请求头信息；
>
> 。。。  
>

![](https://image.3001.net/images/20220808/1659945664_62f0c2c042926d9cf56f1.jpg!small)

#### 代码差异化处理

 **平台特定 js 代码块儿实现，在任意 js 代码中加入如下语法** ：  
![](https://image.3001.net/images/20220808/1659945664_62f0c2c0c37a0bd30cd2e.png!small)

 **平台特定 css 代码块儿实现, 在任意 css 代码中加入如下语法** ：  
![](https://image.3001.net/images/20220808/1659945665_62f0c2c16aec1c0013efe.png!small)  
提示：代码在打包时不会增加包体积，针对不同平台提取相应代码。

#### 多端适配案例

 **一些典型的多端通用解决方案：**

样式解析：

> 微信是 rpx，百度小程序 vw，京东小程序 px；
>
> Taro 统一使用 px 通过框架处理转换成对应平台的像素，因此 px 值不要使用单数；
>
> 1px(像素)的边框通常会转换成平台对应单位会导致无法显示， 可以使用大写的PX单位，例如： 1PX ；
>
> 百度小程序和京东小程序不支持 externalClasses，其它小程序也可能不支持避免使用；

模块导入和导出：

> 导入模块需要使用ES6 的 import， 不要使用 require 到 JS 文件（有些平台不支持）；
>
> 内联本地图片资源可以使用 require 动态导入；
>
> 导入外部资源的 url 必须使用 https，有些平台或机型不支持 http ;
>
> 小程序插件导入可以使用 require 但是要做多平台适配和兼容性处理；

组件开发细节：

> 组件 key 取值，不要使用 index ，对象的 id 属性要先解构出来；
>
> 组件渲染条件取 length 属性页面不更新；
>
> dataset 问题：百度和微信获取的不一样，都要用小写来保持代码一致： 这种驼峰的：data-goodsIndex={index} ，微信会转成全小写
> goodsindex， 百度会保留驼峰 ，正确地写法：data-goodsindex={index} ；

 **百度小程序开发注意事项：**

> 层次较深的状态不会更新时，需要解构变量；
>
> 转换成 vw 样式有偏差，确保样式的通用性；
>
> 个别组件 height: auto 有bug，不写没事；
>
> line-height 居中有偏差，用 flex 比较稳妥；
>
> fixed 布局居底要设置 left: 0, bottom: 0 ，不写默认会有问题（默认在中间渲染）；
>
> mask 组件层级较深时，可能不会更新状态，可以使用 tt-modal 代替；
>
> 图片裁剪，语音识别，打印功能等依赖原生 API 不支持；
>
> 状态更新从有到无需要显性设置 null ，例如将列表组件隐藏：this.setState({list: null}) {list && <组件实例>}；

 **京东小程序开发注意事项：**

> 不支持全局覆盖组件样式，如果想兼容需要单写加上拼接样式名；
>
> 不支持小程序分包，需要单独配置页面路由信息；
>
> showModal 弹窗不能定制 confirmColor 属性；
>
> storagesync 不支持存储 json 数据，读取需要自己手动JSON.parse；
>
> 不支持 canvas绘画API：微信自定义分享功能，图片裁剪，订单条形码等功能都做不了；
>
> 不支持同层渲染，原生组件上只能使用 Cover 组件；
>
> ios 内嵌H5，如果url带参数，需要手动做一下urlencode编码；
>
> H5页面使用小程序 webview 不具备全部京东 app webview 功能，有些功能不支持；
>
> 京东小程序分享 URL 和 其它小程序分享的 URL 不一样，要注意路径的差异区分：
>
> 例如：shareURL: 京东小程序： page/index/index 微信小程序：/pages/index/index

#### 多端同步调试

在 config/index.js 配置：outputRoot: dist/${process.env.TARO_ENV}  
![](https://image.3001.net/images/20220808/1659945665_62f0c2c1f09d6fb66a1dd.jpg!small)

## 生态与规划

#### 物流风格的 Taro UI组件库—Tarot(已适配Taro3.0)

![](https://image.3001.net/images/20220808/1659945666_62f0c2c2a6e2d50ad1dbd.png!small)

![](https://image.3001.net/images/20220808/1659945667_62f0c2c36658c59500cff.jpg!small)

#### 定制化 Taro 模板工程定制化 Taro 模板工程

模板工程主要特性：  
•自带按需引入的 Tarot 组件库及组件使用示例。  
•自带 pandora-tools 中的工具，如网关调用插件等。  
•登陆适配多端，小程序端自动引入京东无线登陆插件，h5端自动跳转无线统一登陆M页d等。  
•网关调用适配多端，自带 Demo 示例；  
•包含 TypeScript 和 Redux等更多高级API及用法示例；  
•其它功能持续更新……

#### 小程序 Mini Debug 工具

MiniDebug 是一款多端小程序调试工具，旨在提高小程序开发、测试效率的工具库  
功能介绍：  
主要功能包括环境切换、身份Mock、应用信息获取、位置模拟、缓存管理、扫一扫、H5跳转、更新版本等。工具部分页面如下图所示：  
目前已经在 GitHub 上开源（欢迎 issue）：<https://github.com/jdlfe/minidebug>

![](https://image.3001.net/images/20220808/1659945667_62f0c2c3ee21f8421bf03.jpg!small)

物流风格的小程序可视化拖拽平台（规划中）

京东商城已经实现了小程序可视化拖拽平台：<https://ling.jd.com/atom/cms/pc/06599>

![](https://image.3001.net/images/20220808/1659945668_62f0c2c48728362b4504f.png!small)

## 结语：

Taro V3.0.0 目前支持 React、Nerv、Vue 三类框架，在未来 Taro 将开放拓展能力，使得开发者可以通过 Taro
拓展更多的框架支持，（比如：适配 Flutter 将成为可能 ）。目前Taro框架完善社区活跃，即使没有多端需求，仅用 Taro 开发 H5
也是个不错的选择（未来可以 0 成本接入小程序平台），想了解更多 Taro 3.0 实践经验欢迎线下交流。

