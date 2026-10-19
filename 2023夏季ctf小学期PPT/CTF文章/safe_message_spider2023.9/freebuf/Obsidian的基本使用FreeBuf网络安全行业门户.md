> When you begin to touch your heart or let your heart be touched, you begin
> to discover that it's bottomless.  
> — Pema Chödrön

* * *

# 下载地址：

https://obsidian.md/download

[Obsidian.0.14.15下载地址](https://github.com/obsidianmd/obsidian-releases/releases/download/v0.14.15/Obsidian.0.14.15.exe)

`ris:CalendarCheck`

#`ris:Home2`

# 1、基本使用篇

## 标题

    
    
    # 一级标题
    ## 二级标题
    ## 三级标题
    ...
    ###### 六级标题
    注意：＃和文字间有一个空格
    

## 列表

### 有序列表

    
    
    1. 一级列表
    	1. 二级列表
    		1. 三级列表
    
    注意：格式是1.[空格]文字，中间的空格不能省略，然后若是按回车将就会自动取消一级列表
    按tab键可以生成二级列表，想要回到一级列表就按回车键
    

效果展示：  
![](https://image.3001.net/images/20220908/1662615796_631980f4cc41fc85156e3.png!small)

### 无序列表

    
    
    - 一级列表
    	- 二级列表
    		- 三级列表
    注意：格式是-[空格]文字，中间的空格不能省略，然后列表嵌套的规则和有序列表一样
    

## 表格

    
    
    | 姓名 | 年龄 |
    |--------|--------|
    | 萧瑟 | 20 |
    格式如上所示
    

## 插入图片

    
    
    ![可以选择是否输入](图片地址)
    例如下面的图片：![test|475](https://image.3001.net/images/20200701/1593550745.png!small)
    

![test](https://image.3001.net/images/20200701/1593550745.png!small)

## 插入链接

    
    
    [百度](http://www.baidu.com/)
    注意：中括号里一定要写东西，不然就不知道链接是什么了
    

[百度](http://www.baidu.com/)

## 插入本地文件或者标题

    
    
    格式：[[文件名#标题名]]
    注意：单输入文件名就可以定位到文件，若是想要定位到标题，加一个#就可以了
    

## 插入任务表

    
    
    - [ ] 刷牙
    - [ ] 洗脸
    作用：每天完成的任务可以打勾
    注意：中括号里的空格不能省略，按回车会自动生成下一个，再按回车即可取消
    

## 插入注释

    
    
    推荐使用三个反单引号，在2个三个反单引号之间可以写一些会被转义的内容，或者是编程语言等等
    注意：可以在第一个三个反单引号后面加一个语言类型即指定插入的语言类型
    例如：
    	```java
    	
    
    	```
    使用一个反单引号也能注释比较短的内容
    

## 标签

    
    
    格式：#名字
    注意：与标题的区别在于没有空格
    作用：可以快速定位或者引用你做过的标签
    
    

## 分隔符

`<hr>或者---`  
效果如下:

* * *

* * *

## 强制换行

`<br>`

## 强制空格

`&ampnbsp`

## 键盘文字

`<kbd>键盘文本</kbd>`  
效果如下:  
`键盘文本`

## 指定文字颜色

用法: `<font color=yellow>这是一段黄色文本</font>`  
效果: 这是一段黄色文本

## 数学公式

### LaTex的语法

先说下怎么换行  
$$  
\begin{aligned}a=b+c\b=c-a\c=a+b \end{aligned}  
$$  
$$  
\begin{matrix}已知y=\sqrt{x+3}&&(x>=0)\求y的最大值是多少 \end{matrix}  
$$  
$$  
\begin{bmatrix}已知y=\sqrt{x+3}&&(x>=0)\求y的最大值是多少 \end{bmatrix}  
$$

$$  
\begin{Bmatrix}已知y=\sqrt{x+3}&&(x>=0)\求y的最大值是多少 \end{Bmatrix}  
$$

$$  
\begin{vmatrix}  
0&1&2\  
3&4&5\  
6&7&8\  
\end{vmatrix}  
$$

$$  
\begin{Vmatrix}  
0&1&2\  
3&4&5\  
6&7&8\  
\end{Vmatrix}  
$$

  * 希腊字母

$\alpha$、$\beta$、$\chi$、$\Delta$、$\Gamma$、$\Theta$之类的

![](https://image.3001.net/images/20220908/1662615798_631980f60403b98b3333d.jpg!small)

  * 一些数学结构

![](https://image.3001.net/images/20220908/1662615798_631980f69fd42b751349a.jpg!small)

  * 效果如下：  
$\frac{123}{999}$、$\sqrt[n]{abc}$、$\frac{\sqrt{234}}{\sqrt[n]{abc}}$、$\underrightarrow{abc}$、$\overrightarrow{abc}$

  * 插入定界符

![](https://image.3001.net/images/20220908/1662615799_631980f788db7ded40a4c.png!small)

  * 效果如下

$|$、$|$、$\Uparrow$、${}$

  * 插入一些可变大小的符号

![](https://image.3001.net/images/20220908/1662615800_631980f845fd176a5cfa8.png!small)

效果如下：

$\sum$、$\int$、$\oint$、$\iint$、$\bigcap\bigcup\bigoplus\bigotimes$

  * 插入一些函数名称

![](https://image.3001.net/images/20220908/1662615800_631980f8e858c91ce7e3e.jpg!small)

效果如下：

$\sin$、$\cos$、$\tan$、$\log$、 $\tan(at-n\pi)$

  * 关系运算符和二进制运算符

![](https://image.3001.net/images/20220908/1662615801_631980f9a387aa54fab45.jpg!small)

效果如下：  
$\times$、$\ast$、$\div$、$\pm$、$\leq$、$\geq$、$\neq$、$\thickapprox$、$\sqsupset$、$\subset$、$\supseteq$、$\sqsupset$、$\sqsupseteq$、$\in$

  * 插入箭头符号

![](https://image.3001.net/images/20220908/1662615802_631980fa544258b3bb9ec.jpg!small)

效果如下：

$\leftarrow$、$\Leftarrow$、$\nLeftarrow$、$\rightleftarrows$

  * 其他符号

![](https://image.3001.net/images/20220908/1662615803_631980fb478c48c144c24.jpg!small)

  * 效果如下  
$\infty$、$\angle$、$\int$、$\triangle$、$\square$

  * 插入上下标

用`^`表示上标，用`_`表示下标记

效果如下：

$$  
\sin^2(\theta) + \cos^2(\theta) = 1  
$$  
$$  
\sum_{n=1}^\infty k  
$$  
$$  
\int_a^bf(x),dx  
$$  
$$  
\lim\limits_{x\to\infty}\exp(-x) = 0  
$$

  * 注意：`\,`在积分里的作用是为了增加些许间距，`\!`会减少一些间距。

  * 输出分段函数  
用`\begin{cases}`和`\end{cases}`来构造分段函数，中间则用`\\`来分段

$$  
f(x) =  
\begin{cases}  
2x,,,x>0\  
3x,,,x\le0\  
\end{cases}  
$$

  * 一些常见的数学公式

    
    
    title:一些常见的数学公式
    ```text
     $$
     f'(x) = x^2 + x
     $$
    ```
     $$
     f'(x) = x^2 + x
     $$
    ```text
    $$
     \lim_{x\to0}\frac{9x^5+7x^3}{x^2+6x^8}
    $$
    ```
    $$
     \lim_{x\to0}\frac{9x^5+7x^3}{x^2+6x^8}
    $$
    
    ```text
    $$
     \int_a^b f(x)\,dx
     $$
    ```
    $$
     \int_a^b f(x)\,dx
    $$
    
    ```text
    $$
     \int_0^{+\infty}f(x)\,dx
    $$
    ```
    $$
     \int_0^{+\infty}f(x)\,dx
    $$
    
    ```text
    $$
     \int_{x^2+y^2\leq R^2} \,f(x,y)\,dx\,dy = \int_{\theta=0}^{2\pi}\int_{r=0}^R \,f(r\cos\theta,r\sin\theta)\,r\,dr\,d\theta
     $$
    ```
    $$
     \int_{x^2+y^2\leq R^2} \,f(x,y)\,dx\,dy = \int_{\theta=0}^{2\pi}\int_{r=0}^R \,f(r\cos\theta,r\sin\theta)\,r\,dr\,d\theta
     $$
    
    ```text
    $$
     \int\!\!\!\int_D f(x,y)dxdy
     $$
    ```
    $$
     \int\!\!\!\int_D f(x,y)dxdy
     $$
    
    

## 常用的快捷键

ctrl + ,：打开设置  
ctrl + p：打开命令面板  
然后很多快捷键可以自己定义，在设置中

## 设置背景图片

首先下载一个插件：Style Setting  
打开设置 -> 选择第三方插件 -> 关闭安全模式 -> 浏览 -> 搜索Style Setting插件并且下载  
![](https://image.3001.net/images/20220908/1662615804_631980fc4d1a7ae11f3c1.png!small)

插件下载好会出现在设置的最下面  
![](https://image.3001.net/images/20220908/1662615805_631980fd526025a610556.png!small)

左侧的最下面就是我下载的插件

选择Style Setting -> 选择主题 -> 选择背景设置 -> 工作页面背景

选择开启背景,然后Theme ligth(主题明亮模式)和Theme Dark(主题黑暗)都选择Custom(自定义)

在路径那栏填写本地图片的路径就可以了，这样明亮模式和黑暗模式都是自定义的背景图片了

==注意==：记得移除笔记背景，不然可能会覆盖工作页面背景

![](https://image.3001.net/images/20220908/1662615806_631980fe557905f5b6858.png!small)

效果如下：  
![](https://image.3001.net/images/20220908/1662615807_631980ff7c6311cb23084.png!small)

Style Setting的功能远不止如此，可以自行摸索，设置个性化的Obsidian

    
    
    title:结语
    因为是初学者，懂得还不多，写错的地方还请各位大佬原谅，欢迎留言交流
    

# 图床设置

详细请查看如下：  
https://www.freebuf.com/articles/others-articles/340573.html

# 常用的插件使用

## 1、Style Setting

作用：可以设置背景（参考[[#设置背景图片]]）和其他的一些样式设计

## 2、Admotion

## 3、QuickAdd

作用：  
快速从模板新建文件  
功能很多，配合template超好用，后面有时间介绍

## 4、advanced table

作用：快速新建表格

用法：`|`+文本，然后按tab会自动生成表格

## 5、obsidian markmind

作用：  
添加pdf注释，写思维导图，并且打开为表格  
可以配合下面的table extended插件使用来合并单元格

用法：  
输入如下命令  
`--- mindmap-plugin: basic ---`  
注意：有两种模式，一种是basic，另一种是rich  
然后点击更多，选择打开为思维导图模式  
然后再选择打开为表格模式，就可以进行表格编辑了

==注意：==编辑好了以后，直接选择更多里面的复制为markdown，然后将内容复制到想要的地方，在最前面加一个-tx-，然后到阅读模式里就可以看到效果了

## 6、table extended

作用：  
合并单元格

使用：  
在表格上面加上：`-tx-`

可以配合其他插件使用，如：obsidian markmind

## 7、Markdown Table Editor

作用：  
可以随意的创建表格，指定几行几列等等  
可以直接选中表格然后打开命令面板，搜索table，选择open editor就可以进行编辑

## 8、Hover Editor

作用：  
可以将指定的面板浮动

使用：  
在控制面板中搜索hover，或者在更多中选择在hover中打开

## 9、cMenu

作用：  
快捷的工具栏  
使用：  
在控制面板中搜索cmenu，点击hide/show，就可以显示隐藏工具栏  
这里我设置了快捷键ctrl+4  
一开始他只出现在第一页，可以在插件选项中设置它出现在每一页，也可以自定义命令类型

## 10、 Cycle through Panes

作用：  
循环转到打开的文件，配合Sliding Panes效果更好  
用法：  
按ctrl+tab即可向右  
按ctrl+shift+tab即可向左

## 11、Collapse All Obsidian

作用：  
快速的吧折叠、打开文件夹下的所有文件  
用法：  
在左侧栏上有一个向上的两个大于号就是折叠所有文件夹  
也可以直接右键文件夹

## 12、PDF to MarkDown

作用：  
将pdf文件转为md文件  
用法：  
在最左侧的工具栏有一个选项，打开pdf文件后点击就可以了

下载地址：  
https://github.com/akaalias/obsidian-extract-pdf  
将这个文件夹下载下来，然后将文件夹整个移动到插件的文件夹，然后重启obsidian就可以使用了

## 14、增强编辑

提供了一些方便写作的功能，为很多操作设置了快捷键

我的Obsidian的插件如下：

![3R\)\[O6PKJ\[TNDP_%L4EV\]UW.jpg](https://image.3001.net/images/20220908/1662615318_63197f16c74a5b0461550.jpg!small)

我的Obsidian的界面现在如下

![T\[@CVVJVC%1W1MO~I%H@Y5M.jpg](https://image.3001.net/images/20220908/1662615552_6319800060cf02da6ee75.jpg!small)

我现在的库是使用了orange示例库，然后自己配置了一下插件

最后欢迎各位Obsidian的同好交流分享

