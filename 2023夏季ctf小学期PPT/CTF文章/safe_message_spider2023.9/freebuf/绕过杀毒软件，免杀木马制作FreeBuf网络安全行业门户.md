绕过杀毒软件，免杀木马制作（以杀毒软件AVG Anti-Spyware为例）

一、将Sever.exe打开，分块生成100个文件

![1661830618_630d85daa294c990fc9fc.png!small](https://image.3001.net/images/20220830/1661830618_630d85daa294c990fc9fc.png!small)

二、查杀生成的文件，再二次处理，重复这个过程，直到缩小到很小的范围，精确定位特征码于0009B9C3

![1661830623_630d85dff176d05b8280d.png!small](https://image.3001.net/images/20220830/1661830623_630d85dff176d05b8280d.png!small)

![1661830637_630d85edad120a00dcfc5.png!small](https://image.3001.net/images/20220830/1661830637_630d85edad120a00dcfc5.png!small)

![1661830644_630d85f48a683974a5396.png!small](https://image.3001.net/images/20220830/1661830644_630d85f48a683974a5396.png!small)

![1661830656_630d86005fa6dc02ea8ac.png!small](https://image.3001.net/images/20220830/1661830656_630d86005fa6dc02ea8ac.png!small)

![1661830660_630d8604002cef77930cf.png!small](https://image.3001.net/images/20220830/1661830660_630d8604002cef77930cf.png!small)

![1661830663_630d8607b15cab0f85f17.png!small](https://image.3001.net/images/20220830/1661830663_630d8607b15cab0f85f17.png!small)

![1661830666_630d860a90573d804170e.png!small](https://image.3001.net/images/20220830/1661830666_630d860a90573d804170e.png!small)

![1661830670_630d860edb61d3a139d12.png!small](https://image.3001.net/images/20220830/1661830670_630d860edb61d3a139d12.png!small)

![1661830675_630d86138e38737e63c17.png!small](https://image.3001.net/images/20220830/1661830675_630d86138e38737e63c17.png!small)

三、将文件偏移地址0009B9C3转换成内存地址0049C5C3

![1661830680_630d8618e5eafc8459c04.png!small](https://image.3001.net/images/20220830/1661830680_630d8618e5eafc8459c04.png!small)

四、在OllyDbg中跳转到0049C5C3，滑动滚轮看到0049C5C1特征码指令内容，将指令内容填至程序最下方00空白的004A21E4处，并将JMP
004A21E4汇编至0049C5C1处。全部复制保存即能实现木马的免杀。

![1661830692_630d862400adbf87ab294.png!small](https://image.3001.net/images/20220830/1661830692_630d862400adbf87ab294.png!small)

![1661830710_630d863683920106c59a7.png!small](https://image.3001.net/images/20220830/1661830710_630d863683920106c59a7.png!small)

![1661830713_630d8639c9816887ad8cf.png!small](https://image.3001.net/images/20220830/1661830713_630d8639c9816887ad8cf.png!small)

五、将免杀木马在XP肉鸡上运行，Win7主机控制端能看见XP肉鸡上线

![1661830720_630d8640457e91f3509a7.png!small](https://image.3001.net/images/20220830/1661830720_630d8640457e91f3509a7.png!small)

