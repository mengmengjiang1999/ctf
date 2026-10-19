进入实验环境，打开题目地址，发现是个俄罗斯方块的游戏，尝试先玩了几局，但是并没有什么用，玩游戏就能获得flag？感觉不太靠谱，看看有没有别的思路。

![小游戏](https://image.3001.net/images/20210129/1611909753_6013ca79e6c7e3f467dd7.png!small)

我们先分析这个游戏服务，这是一个web的游戏，那么我们在浏览器的开发者工具中，对网络请求进行分析，发现我们对目标进行访问时，并没有实质性的后台请求：

所以基本可以断定，这是一个前台页面的游戏，游戏的运行、计分都是由js脚本来支持的，所以我们找到了请求中仅有的js页面代码：

![找到js代码](https://image.3001.net/images/20210129/1611909755_6013ca7b5febbda39da8e.png!small)

这个js混淆过，所以需要先美化，也就是js代码的格式化。经过分析，会发现，当游戏分数达到既定的条件时，js代码会在页面的头部中添加urlkey字段，值为“webqwer”[1]+“100.js”，即为“webqwer”的第2个字母与“100.js”拼接为“e100.js”。

![js代码](https://image.3001.net/images/20210129/1611909756_6013ca7c17502cf9b20ea.png!small)  
  

也是一个js文件，我们尝试直接访问，可以下图下图所示的内容，这是jsfuck编码：

![获得jsfuck编码](https://image.3001.net/images/20210129/1611909756_6013ca7cc3637fbef36da.png!small)

jsfuck编码是可以直接在控制台运行的，我们复制粘贴到控制台，但是我们直接可以用google浏览器，f12打开开发者工具，然后将编码粘贴到console中，内容过多，环境可能卡顿，耐心等待：

![将编码粘贴到console](https://image.3001.net/images/20210129/1611909757_6013ca7dc00a50d82587a.png!small)

粘贴完成之后，回车就可运行，页面就会弹出flag：

![弹出flag](https://image.3001.net/images/20210129/1611909759_6013ca7f7581cadf63392.png!small)  
  

最后填写一下答案，完成。

![填写答案](https://image.3001.net/images/20210129/1611909760_6013ca801aed627056759.png!small)

本次实验操作地址：[https://www.hetianlab.com/expc.do?w=exp_ass&ec=ECID9d6c0ca797abec2016092313364600001](https://www.hetianlab.com/specialized/20210126131003)

