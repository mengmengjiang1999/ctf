本文仅用于记录自身学习过程。

## 准备工具

1、夜神模拟器

2、node

## 源码位置

首先，存放各个小程序的源码位置，理论上只要你登录之后，挨个页面访问一遍，源码就会自动备份在一个目录下  
/data/data/com.tencent.mm/MicroMsg/…/appbrand/pkg/

/data/data/com.tencent.mm/MicroMsg/3cc9951254f0c03740f2b14e7444d34d/appbrand/pkg

![1645775792_62188bb012845fa6a4fdd.png!small?1645775792281](https://image.3001.net/images/20220225/1645775792_62188bb012845fa6a4fdd.png!small?1645775792281)

如何区分是自己想要的小程序

通过adb命令删除文件下所有内容。

![1645775808_62188bc079f665bba8b24.png!small?1645775808707](https://image.3001.net/images/20220225/1645775808_62188bc079f665bba8b24.png!small?1645775808707)

重新加载小程序

![1645775813_62188bc5e0139153d095b.png!small?1645775814022](https://image.3001.net/images/20220225/1645775813_62188bc5e0139153d095b.png!small?1645775814022)

  

提取文件到本地

adb pull
/data/data/com.tencent.mm/MicroMsg/3cc9951254f0c03740f2b14e7444d34d/appbrand/pkg.tar.gz
D:\xiaocx

![1645775825_62188bd14bd499f321230.png!small?1645775825458](https://image.3001.net/images/20220225/1645775825_62188bd14bd499f321230.png!small?1645775825458)

试坑：后来发现[adb](https://so.csdn.net/so/search?q=adb&spm=1001.2101.3001.7020)pull
是在adb shell的模式下进行的，需要先退出shell 再运行adb pull。

下载node最新版本，下载[反编译](https://so.csdn.net/so/search?q=%E5%8F%8D%E7%BC%96%E8%AF%91&spm=1001.2101.3001.7020)文件，安装依赖

[node下载地址： https://nodejs.org/zh-cn/download/](https://nodejs.org/zh-cn/download/)

node简 介： Node.js 是一个开源和跨平台的 JavaScript 运行时环境。简单的说 Node.js 就是运行在服务端的
JavaScript。

![1645775844_62188be4191585e8bc992.png!small?1645775844204](https://image.3001.net/images/20220225/1645775844_62188be4191585e8bc992.png!small?1645775844204)

下载好node后，需要去github安装反编译文件，这里使用的是

[项目地址：
https://github.com/xuedingmiaojun/wxappUnpacker/](https://github.com/xuedingmiaojun/wxappUnpacker)

试坑：将下载好的文件存放后，需要安装依赖，这里建议大家进入到当前文件夹进行依赖的安装，否则你会安装第二遍

npm install

npm install esprima

npm install css-tree

npm install cssbeautify

npm install vm2

npm install uglify-es

npm install js-beautify

安装好之后，会在项目文件里生成插件

![1645775856_62188bf034ad697328da9.png!small?1645775856399](https://image.3001.net/images/20220225/1645775856_62188bf034ad697328da9.png!small?1645775856399)

这个时候，将你的wxapkg文件放入至当前目录下，成功编译后，会在当前目录生成对应的源文件。

使用命令：node wuWxapkg.js filepath

![1645775863_62188bf700e86b8b0c524.png!small?1645775863144](https://image.3001.net/images/20220225/1645775863_62188bf700e86b8b0c524.png!small?1645775863144)

查看反编译成功后的文件夹。

![1645775868_62188bfc9fe28bbfd3448.png!small?1645775868806](https://image.3001.net/images/20220225/1645775868_62188bfc9fe28bbfd3448.png!small?1645775868806)

