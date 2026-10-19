## 1 简介

前端打包js代码时大部分会使用webpack,如果发布时没有删除掉生成的.map文件,就可以从map文件中直接获取到开发时的js源码．

使用这个burp-clj脚本可以自动检测访问的js链接是否包含map文件，并下载map文件，还原js源码．

## 2 安装方法

参考[之前](sectool/252034.html)文章burp-clj插件的安装方法,加载脚本<https://github.com/ntestoc3/burp-scripts>

![burp-clj-webpack-1.png](https://image.3001.net/images/20210302/1614695392_603e4be03abae50dbb629.png!small)

图1 加载脚本源，并启用webpack脚本．

建议git clone到本地，然后加载本地目录，否则每次启动burp都要从git同步代码，网络不好会造成速度很慢．

## 3 使用方法

设置webpack的保存目录:

![burp-clj-webpack-2.png](https://image.3001.net/images/20210302/1614695403_603e4beba7530e17eb42e.png!small)

图2 设置webpack保存目录

  

通过burp代理访问目标站点，如果webpack脚本发现存在js.map文件，就会自动下载，并解包js源码到设置的目录中．并添加相应的issue．

![burp-webpack.gif](https://image.3001.net/images/20210302/1614695667_603e4cf3a9730ba3eb75c.gif)

图3 使用方法

## 4 最后

本程序仅供于学习交流，请使用者遵守《中华人民共和国网络安全法》， 勿将此工具用于非授权的测试， 程序开发者不负任何连带法律责任。

