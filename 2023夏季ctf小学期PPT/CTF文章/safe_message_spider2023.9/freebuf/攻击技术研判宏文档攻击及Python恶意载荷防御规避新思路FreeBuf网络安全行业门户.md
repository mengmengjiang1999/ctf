## **情报背景**  

近期卡巴斯基的研究人员发布了针对DeathStalker的追加分析报告，攻击者对攻击链的隐蔽性进行了较大的改进，在宏文档攻击日渐式微的今天带来一些新鲜的检测对抗思路。本文将对攻击者在宏文档攻击及Python恶意载荷中一些值得关注的防御规避技术进行分析研判。

 **组织名称**

|

DeathStalker  
  
---|---  
  
 **战术标签**

|

初始访问、防御规避  
  
 **技术标签**

|

VBA、py2exe、Python字节码  
  
 **情报来源**

|

https://securelist.com/vilerat-deathstalkers-continuous-strike/107075/  
  
##  **01** 攻击技术分析

![1663227705_6322d739de034c6b39ddd.png!small?1663227706994](https://image.3001.net/images/20220915/1663227705_6322d739de034c6b39ddd.png!small?1663227706994)

攻击链：远程DOTM模板加载执行VBA代码，释放执行自定义RAT

 **亮点1 VBA Stomping技术**

Office文档中的宏通常存储于三个位置：

  * VBA宏源码，用户宏编辑器中查看的版本

  * P-code，预编译的宏代码，适用于某个特定Office版本

  * Execodes，P-code执行后产生的进一步的字节码

VBA Stomping技术（T1564.007 Defense Evasion.HideArtifacts）是指攻击者将恶意代码以P-code的形式插入文档中。由于它的优先级较之用户可见的明文VBA更高，存在用户查看不存在恶意行为的明文宏代码之后放行的可能性，更加具备迷惑性。插入P-code的方式存在局限性，执行环境的Office版本必须和样本制作版本保持一致，这使得VBA
Stomping更适合具备目标基本信息的定向钓鱼攻击。在实战场景中攻击者也考虑到Office版本不一致的情况，在明文宏代码中实现迷惑性质的弹窗。

![1663227721_6322d74926987160367fe.jpg!small?1663227722133](https://image.3001.net/images/20220915/1663227721_6322d74926987160367fe.jpg!small?1663227722133)

执行P-code失败后的伪装弹窗

 **亮点2 宏代码中利用图片插入API发送HTTP请求**

在宏代码执行过程中，攻击者巧妙利用支持图片插入API发送HTTP请求实现数据渗出，规避对宏文档中常见WEB请求API调用的静态检测。

Shapes.AddPicture方法原本用于将图片添加到文档画布中，该方法的首个参数FileName的含义为插入的图像文件的路径（本地或远程），支持URL形式请求指定远程图片。

    
    
    Shapes.AddPicture (FileName, LinkToFile, SaveWithDocument, Left, Top, Width, Height)

常规使用方式如下，向画布中插入本地图片文件：

    
    
    '向画布添加本地图片  
    shpCanvas.CanvasItems.AddPicture _   
    FileName:="C:\Program Files\Microsoft Office\" & _   
    "Office\Bitmaps\Styles\stone.bmp", _   
    LinkToFile:=False, SaveWithDocument:=True 

``

稍加修改，给首个参数传入URL，即可向指定的HTTP服务器发起GET请求，通过控制URL实现信息的渗出。

![1663227738_6322d75aab02ff1ade090.png!small?1663227739663](https://image.3001.net/images/20220915/1663227738_6322d75aab02ff1ade090.png!small?1663227739663)复现：利用AddPicture方法发送GET请求  

 **亮点3 Python字节码花指令对抗静态分析工具**

攻击者利用py2exe工具对RAT加载器进行封装，原始Python脚本被编译为pyc模块与精简的Python运行时打包后一起分发，通常利用uncompyle6等工具即可反编译获取原始脚本的伪代码。

攻击者通过在Python字节码层面插入花指令，有效对抗了常见工具的静态逆向分析：

  * 可执行但是不产生实际效果

  * 插入迷惑性分支与异常处理

  * 插入始终不会执行到的畸形代码以破坏反编译

![1663227784_6322d7882409d575f7b73.png!small?1663227785271](https://image.3001.net/images/20220915/1663227784_6322d7882409d575f7b73.png!small?1663227785271)

插入垃圾代码破坏Python字节码反编译，右侧去除了花指令

本次攻击中出现的一些Python字节码花指令示例：

    
    
    #读取常数到栈顶  
    LOAD_CONST xx  
    #移除栈顶元素  
    POP_TOP  
      
    #交换栈顶两个元素，执行两次无效化  
    ROT_TWO  
    ROT_TWO  
      
    #交换栈顶三个元素位置，执行三次无效化  
    ROT_THREE  
    ROT_THREE  
    ROT_THREE

##  **02** 总结

随着微软Office中安全机制的加码，宏文档攻击的适用范围进一步收缩（在高版本中被默认禁用）。但在对目标环境有充分信息收集的情况下，针对特定Office版本的定制宏文档攻击依然有用武之地。本次攻击中出现了一些宏文档攻击利用新思路，包括对宏代码的伪装以及使用替代API发起请求，在野攻击中的宏文档攻击仍有其生命力。在载荷隐匿方面，利用py2exe封装脚本与解包分析的流程都久已完善，内嵌字节码混淆技术虽然无法对抗手动分析，但对常见分析工具的对抗有效增加了分析成本，在对抗自动化分析等场景有实战价值。

