![1623051153_60bdcb917e7af8ff8854a.png!small?1623051153786](https://image.3001.net/images/20210607/1623051153_60bdcb917e7af8ff8854a.png!small?1623051153786)

## 0x00 Node.js安全检查引擎

Node.js作为常见的Web开发语言之一，Xcheck也针对该语言打造了对应的扫描引擎： **JsCheck** 。

同样基于污点传播模型，支持以下常见漏洞类型：

> 命令注入
>
> SQL注入
>
> URL跳转
>
> SSRF
>
> 路径穿越
>
> XXE
>
> 反序列化
>
> 模板注入
>
> XPath注入

目前JsCheck支持以下2个框架： **Koa、Express，** 其他框架有需要可以方便添加。

![1623051186_60bdcbb2cdd930a572fad.png!small?1623051187200](https://image.3001.net/images/20210607/1623051186_60bdcbb2cdd930a572fad.png!small?1623051187200)

## 0x01 Node.js一些有意思的特性

JsCheck为了能够精准的做污点传播，对Node.js的特性进行了精确的适配，比如： **this关键字，变量声明提升等。**

### this关键字

Node.js里的this根据所处的位置不同（普通函数，箭头函数），调用方式不同（直接调用，赋值给一个对象的属性再调用，当做构造函数调用），有着不同的指向含义。  
1）当在文件的最上层的时候，this指向的当前文件的`exports`对象：

![1623051209_60bdcbc937f6369bc41a8.png!small?1623051209543](https://image.3001.net/images/20210607/1623051209_60bdcbc937f6369bc41a8.png!small?1623051209543)

输出：

![1623051233_60bdcbe124dcfb43fc7e4.png!small?1623051233426](https://image.3001.net/images/20210607/1623051233_60bdcbe124dcfb43fc7e4.png!small?1623051233426)

2）当this在一个普通函数里，this指向的是`global`对象：

![1623051256_60bdcbf84b197558a4f94.png!small?1623051256748](https://image.3001.net/images/20210607/1623051256_60bdcbf84b197558a4f94.png!small?1623051256748)

输出：

![1623051293_60bdcc1d094c279ba4c58.png!small?1623051293268](https://image.3001.net/images/20210607/1623051293_60bdcc1d094c279ba4c58.png!small?1623051293268)

3）当this在一个构造函数里，this指向的是该构造函数生成的对象：

![1623051317_60bdcc35137ba69c5165b.png!small?1623051317345](https://image.3001.net/images/20210607/1623051317_60bdcc35137ba69c5165b.png!small?1623051317345)

输出：

![1623051338_60bdcc4a7f9790edd6b4c.png!small?1623051338821](https://image.3001.net/images/20210607/1623051338_60bdcc4a7f9790edd6b4c.png!small?1623051338821)

4）当this在箭头函数里，this指向的对象就会根据this定义时所处的为上下文而定：

![1623051361_60bdcc618bb457e9e3318.png!small?1623051361870](https://image.3001.net/images/20210607/1623051361_60bdcc618bb457e9e3318.png!small?1623051361870)

输出：

![1623051381_60bdcc75b6025d0102544.png!small?1623051382244](https://image.3001.net/images/20210607/1623051381_60bdcc75b6025d0102544.png!small?1623051382244)

### 变量声明提升

在Node.js里，如果一个变量不使用`var，const，let`修饰，那么默认它是一个全局变量：

![1623051400_60bdcc887cea38495129f.png!small?1623051401536](https://image.3001.net/images/20210607/1623051400_60bdcc887cea38495129f.png!small?1623051401536)

输出：

![1623051421_60bdcc9d4cabec48e23c6.png!small?1623051421544](https://image.3001.net/images/20210607/1623051421_60bdcc9d4cabec48e23c6.png!small?1623051421544)

如果使用了var声明变量，则会出现变量声明提升：

![1623051444_60bdccb40e28af79827a1.png!small?1623051444943](https://image.3001.net/images/20210607/1623051444_60bdccb40e28af79827a1.png!small?1623051444943)

输出：

![1623051464_60bdccc8df2c2f35fcb12.png!small?1623051465142](https://image.3001.net/images/20210607/1623051464_60bdccc8df2c2f35fcb12.png!small?1623051465142)

不但变量的声明会提升，函数的声明也会提升：

![1623051485_60bdccdd6b31ad0ada61b.png!small?1623051485826](https://image.3001.net/images/20210607/1623051485_60bdccdd6b31ad0ada61b.png!small?1623051485826)

等价于：

![1623051508_60bdccf4b587cce8bc3f3.png!small?1623051509045](https://image.3001.net/images/20210607/1623051508_60bdccf4b587cce8bc3f3.png!small?1623051509045)

## 0x02 误报消除的尝试

在处理误报的时候，最不好处理的就是用户自定义的过滤逻辑。因为，这里的写法形式很多，难以提取出固定的模式，其中有两个关键点：

 **1.识别出一段代码是过滤逻辑  
** **2.判定此段过滤逻辑是完备的**

针对这两个点，目前从业界来看，都没有完美的解决办法，Xcheck在这里做了一些尝试，对一些情况能够做出准确的判定。  
比如，通过字符串直接比对的情况：

![1623051532_60bdcd0c6daab2a2b7b7c.png!small?1623051532816](https://image.3001.net/images/20210607/1623051532_60bdcd0c6daab2a2b7b7c.png!small?1623051532816)

检测不满足条件后抛出异常的情况：

![1623051552_60bdcd204e48e97a6cdba.png!small?1623051552644](https://image.3001.net/images/20210607/1623051552_60bdcd204e48e97a6cdba.png!small?1623051552644)

对污点数据进行常量化替换（清洗）：

![1623051578_60bdcd3a22809d0722eab.png!small?1623051578428](https://image.3001.net/images/20210607/1623051578_60bdcd3a22809d0722eab.png!small?1623051578428)

过滤逻辑叠加污点对象传播时：

![1623051602_60bdcd520844a9ae3f767.png!small?1623051602316](https://image.3001.net/images/20210607/1623051602_60bdcd520844a9ae3f767.png!small?1623051602316)

判定对象和风险函数执行的对象不是同一个的情况：

![1623051621_60bdcd651131b33aecf61.png!small?1623051621336](https://image.3001.net/images/20210607/1623051621_60bdcd651131b33aecf61.png!small?1623051621336)

常见目录穿越漏洞的过滤逻辑：

![1623051642_60bdcd7a86a040b8776ea.png!small?1623051643098](https://image.3001.net/images/20210607/1623051642_60bdcd7a86a040b8776ea.png!small?1623051643098)

从实测效果来看，JsCheck的误报已经明显降低，但是后续还有优化提升空间。

## 0x03 扫描样例

目前，使用github上CodeQL的Node.js测试集来扫描，未做专门适配的情况下发现漏洞243个。

![1623051665_60bdcd917d036b9ca8ecc.png!small?1623051665908](https://image.3001.net/images/20210607/1623051665_60bdcd917d036b9ca8ecc.png!small?1623051665908)

查看详细的扫描报告，针对每个漏洞，各个污点传播节点有详细的展示：

![1623051690_60bdcdaa853892b94d1dd.png!small?1623051690938](https://image.3001.net/images/20210607/1623051690_60bdcdaa853892b94d1dd.png!small?1623051690938)

  

