# 1.目前webshell检测的难点

在目前的技术条件下，精准Webshell检测还是一项非常复杂事情，主要的难度在于:

  1. 多语言：Webshell的种类非常多样化，根据web环境的不同，webshell的语言包括PHP、ASP、ASP.NET、JSP等等。

  2. 版本语法差异: 不同类型的语言在不同的版本下，具有不同的语法和语言特性，比如php5和php7、jdk8和jdk18的很多语法差别就很大。这样对webshell的引擎检测的语法解析兼容性就提出了很高的要求，同时需要对语言特性有较高的了解。

  3. 加密和混淆：攻击者可以使用各种加密和混淆技术来隐藏Webshell的代码，包括字符串加密、代码混淆、反射、压缩等等。这些技术使得Webshell的代码难以被检测出来，需要使用专门的技术进行解密和分析。

# 2.Kunwu

昆吾进行了深度优化，内置了模糊规则、污点分析模拟执行、机器学习三种高效的检测策略。

github地址：https://github.com/kunwu2023/kunwu

 **检测流程**

首先，模糊规则对待检测文件进行快速初步筛查，迅速判断文件是否为恶意文件。如果确定为恶意文件，则直接将其标记为恶意。反之，模糊规则会评估是否需要对文件进行深度检测。如果需要，文件将交由机器学习和污点分析模拟执行进行深度检测，确保检测速度的同时提高准确性。

 **策略优势**

 **1\. 模糊规则**

经过大量样本的积累和实验，模糊规则能够快速判断文件的可疑程度。根据可疑程度判断是否需要深度检测，既保证了检出率，又最大限度地节省了系统资源。

 **2\. 污点分析模拟执行**

以PHP为例，首先让我们了解一下PHP的解析过程：
![image.png](https://image.3001.net/images/20230517/1684317752_6464a63873b01b86f5af1.png!small)PHP编译过程包括词法分析、语法分析，在语法分析阶段生成AST(抽象语法树)。从AST中，我们可以洞察到PHP代码的结构特点。

    
    
    <?php 
    $func = new ReflectionFunction($_GET['m']); 
    echo $func->invokeArgs(array($_GET['c']));
    

![image.png](https://image.3001.net/images/20230517/1684317753_6464a6395a2b46e119ac1.png!small)

污点分析模拟执行通过遍历AST中的节点属性，对每个节点进行模拟执行。这种方法在Webshell检测中实现了高检出率和低误报率。

 **3\. 机器学习**

机器学习策略从多个角度对文件进行特征提取，可以在面对新出现的未知样本时保持较高的准确率。通过与其他检测策略相结合，机器学习策略能够在Webshell检测中实现高检出率和低误报率

# 3.检出率对比

样本仓库 https://github.com/BlackArch/webshells

### 某盾: 检测199

![image](https://image.3001.net/images/20230517/1684317383_6464a4c76b3f642e85526.png!small)

### 某马:检测196

![image](https://image.3001.net/images/20230517/1684317402_6464a4da8f8666c4381f6.png!small)

### 某狗:检测211

![image](https://image.3001.net/images/20230517/1684317427_6464a4f3c3e021281f384.png!small)

### Kunwu:207

![image](https://image.3001.net/images/20230517/1684317443_6464a5032f6c741665773.png!small)

## 4.误报率对比

样本来自于网络搜集的一些常用CMS，内容如下  
![image](https://image.3001.net/images/20230517/1684317463_6464a5178fc9bf01ecbda.png!small)

### D盾：3

![image](https://image.3001.net/images/20230517/1684317482_6464a52a9480b37b83d8d.png!small)

### 河马:8

![image](https://image.3001.net/images/20230517/1684317497_6464a5393dde5fcf4ef0d.png!small)

### 安全狗:0

![image](https://image.3001.net/images/20230517/1684317512_6464a548d70ff86b94482.png!small)

### Kunwu:0

![image](https://image.3001.net/images/20230517/1684317528_6464a558cad6769f398d0.png!small)

# 5.结果对比

/| 检出率| 误报率| Mac支持| Linux支持| windows支持| Cli支持  
---|---|---|---|---|---|---  
某盾| 87%| 0.0009%| ❌| ❌| ✅| ❌  
某马| 85%| 0.002%| ❌| ✅| ✅| ✅  
某狗| 92%| 0%| ❌| ❌| ✅| ❌  
Kunwu| 90%| 0%| ✅| ✅| ✅| ✅  
  
# 6.迭代路线图

  1. 增强加密webshell的检出效果，提高检出率

  2. 进一步优化检测速度，更快的为大家提供服务

