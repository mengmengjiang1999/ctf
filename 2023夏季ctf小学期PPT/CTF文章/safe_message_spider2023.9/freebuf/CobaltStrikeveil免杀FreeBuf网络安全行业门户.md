***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

生成Payload，把勾选的X64去掉(就算目标机是X64的，也不勾选)

![1621579964_60a758bcb997d75073549.png!small](https://image.3001.net/images/20210521/1621579964_60a758bcb997d75073549.png!small)

Payload内容

![1621580212_60a759b4cebf0dcc66dd6.png!small](https://image.3001.net/images/20210521/1621580212_60a759b4cebf0dcc66dd6.png!small)

在kali上安装veil，需要先更新源(apt-get update apt-get upgrade)

    
    
    apt-get install veil

![1621580229_60a759c5b0185f3e707eb.png!small](https://image.3001.net/images/20210521/1621580229_60a759c5b0185f3e707eb.png!small)

如果报以下错

![1621580255_60a759dfa3357819a6d1c.png!small](https://image.3001.net/images/20210521/1621580255_60a759dfa3357819a6d1c.png!small)

执行以下命令，修复

![1621580263_60a759e7271a4a1106e23.png!small](https://image.3001.net/images/20210521/1621580263_60a759e7271a4a1106e23.png!small)

use 1

![1621580281_60a759f9a53614cb86a28.png!small](https://image.3001.net/images/20210521/1621580281_60a759f9a53614cb86a28.png!small)

list查看Payload，有各种语言的Payload

![1621580291_60a75a03569d9a42b8ff4.png!small](https://image.3001.net/images/20210521/1621580291_60a75a03569d9a42b8ff4.png!small)

![1621580300_60a75a0cb075e9721ed0c.png!small](https://image.3001.net/images/20210521/1621580300_60a75a0cb075e9721ed0c.png!small)

这里使用GO语言下的Payload，因为没有使用MSF，所以使用GO语言的shellcode Payload

![1621580314_60a75a1a2753bbc1810c8.png!small](https://image.3001.net/images/20210521/1621580314_60a75a1a2753bbc1810c8.png!small)

输入use 17，选择Payload

![1621580323_60a75a23a1c3055663539.png!small](https://image.3001.net/images/20210521/1621580323_60a75a23a1c3055663539.png!small)

所有选项默认，不用管

![1621580327_60a75a27889b5004ddc28.png!small](https://image.3001.net/images/20210521/1621580327_60a75a27889b5004ddc28.png!small)

选择第三个generate

![1621580338_60a75a327876b34c645c4.png!small](https://image.3001.net/images/20210521/1621580338_60a75a327876b34c645c4.png!small)

设置shellcode，选择自定义shellcode，这里选择3

![1621580344_60a75a38995f5c37db7fc.png!small](https://image.3001.net/images/20210521/1621580344_60a75a38995f5c37db7fc.png!small)

把在CS生成的Payload.txt文件里面的内容复制到下面

![1621580359_60a75a475c09951540ca0.png!small](https://image.3001.net/images/20210521/1621580359_60a75a475c09951540ca0.png!small)

输入名称，可随便

![1621580364_60a75a4c27c831fc0c58a.png!small](https://image.3001.net/images/20210521/1621580364_60a75a4c27c831fc0c58a.png!small)

生成的exe文件就保存在了以下位置

![1621580368_60a75a50a7a05f1483833.png!small](https://image.3001.net/images/20210521/1621580368_60a75a50a7a05f1483833.png!small)

把以下exe文件上传到目标机执行即可

![1621580378_60a75a5ab610aef4f1e07.png!small](https://image.3001.net/images/20210521/1621580378_60a75a5ab610aef4f1e07.png!small)

## 总结

> 1.经测试，在生成Payload时，勾选X64，CS并不能上线，所以不勾选
>
> 2.经测试火绒报毒，360并没有报，所以可根据目标机的防护软件来进行免杀

