## 一、漏洞信息

### 漏洞描述

 **CVE** **编号：** CVE-2022-42889

Apache Commons Text：该组件是一款处理字符串和文本块的开源项目，简单来说，除了核心Java提供的功能外，Apache
Commons文本库还包含了许多有用的实用程序方法，用于处理字符串。通常在开发过程中用于占位符和动态获取属性的字符串编辑工具包，常用于数据库查询前的语句替换，或者页面输出时的替换。

Apache Commons
Text执行变量插值，允许动态评估和扩展属性。插值的标准格式是“$｛prefix:name｝”，其中“prefix”用于查找org.apache.commons.text.loookup的实例，执行插值的StringLookup
。从1.5版开始一直到1.9版，默认Lookup实例集包括插值器，这些插值器可能导致任意代码执行或与远程服务器通信。这些查找是：-“script”-使用JVM脚本执行引擎（javax.script）执行表达式-“dns”-解析dns记录-“url”-从url加载值，如果使用不受信任的配置值，则受影响版本中使用插值默认值的应用程序，可能容易受到远程代码执行或与远程服务器无意接触的影响。
**建议用户升级到** **Apache Commons Text 1.10.0** **，默认情况下会禁用有问题的插值器。**

### 影响范围

1.5 <= Apache Commons Text <= 1.9

### 修复建议

建议升级组件，获取官方版本地址如下：

https://commons.apache.org/proper/commons-text/download_text.cgi

### 安博通防护能力

 **对于该漏洞，安博通已经第一时间跟进，添加相应的** **IPS** **防护规则，为用户提供高效及时的安全防护。**

 **IPS** **版本：** 20221017.uips及以上版本

 **规则编号：** 995174

![](https://image.3001.net/images/20221130/1669776567_6386c4b7dc5d005c0fe91.jpg!small)防护效果

# 二、漏洞研究

### 漏洞复现

复现的代码如下：

    
    
    package com.seanwrightsec.poc;
    
    import org.apache.commons.text.StringSubstitutor;
    
    import java.util.Scanner;
    
    public class PoC {
        public final static String DEFAULT_POC_STRING = "${script:javascript:195 + 324}";
    
        public static void main(String[] args) {
            StringSubstitutor stringSubstitutor = StringSubstitutor.createInterpolator();
            System.out.println("Enter your exploit string (press Enter to use the default of '${script:javascript:195 + 324}'): ");
            Scanner in = new Scanner(System.in);
            String exploitString = in.nextLine();
            if (exploitString.equals("")) {
                exploitString = DEFAULT_POC_STRING;
            }
            String output = stringSubstitutor.replace(exploitString);
            System.out.println("=====");
            System.out.printf("Exploiting PoC with the exploit string '%s'%n", exploitString);
            System.out.println("=====");
            System.out.println("PoC Output:");
            System.out.println("-----");
            System.out.println(output);
            System.out.println("=====");
        }
    }

构造语句：${dns:address|www.google.com}，实现了对Google的dns地址查询命令并成功返回，可见远程代码执行漏洞确实存在。

###
![](https://image.3001.net/images/20221130/1669776720_6386c55017a1c6c143519.jpg!small)代码研究

下面从代码运行的视角来分析漏洞产生的原因。

先从StringSubstitutor.replace方法中跟入。

![](https://image.3001.net/images/20221130/1669776823_6386c5b767c721ccfd382.png!small)

调用substitute解析传入的字符串。

![](https://image.3001.net/images/20221130/1669776853_6386c5d55258eb6b89c84.png!small)

跟进resolveVariable 。

![](https://image.3001.net/images/20221130/1669776883_6386c5f3bb2d1e42a4de6.png!small)

这里获取的StringLookup，就是之前使用StringSubstitutor.createInterpolator()创建实例化对象的地方。

![](https://image.3001.net/images/20221130/1669776913_6386c6110514097ab5e2b.png!small)并在构造方法中调用了this.setVariableResolver(variableResolver)，设置VariableResolver为InterpolatorStringLookup类。

![](https://image.3001.net/images/20221130/1669776943_6386c62fd775f71cfc7c3.png!small)继续跟入InterpolatorStringLookup的lookup方法中。

![](https://image.3001.net/images/20221130/1669776981_6386c655ab54e2f725655.png!small)构造的JavaScript字符串被传入到lookup方法中。

![](https://image.3001.net/images/20221130/1669777023_6386c67f7159f71153892.png!small)而ScriptStringLookup类调用了lookup方法。

![](https://image.3001.net/images/20221130/1669777093_6386c6c53f0232d1afb3e.jpg!small)ScriptStringLookup类中的scriptEngine.eval函数获取到了传入的构造语句，直接执行。

![](https://image.3001.net/images/20221130/1669777125_6386c6e58ed10f3924132.png!small)关于这个引擎的介绍和使用可以参考这个链接：

https://www.qieseo.com/329754.html

Nashorn扩展可以使JVM在运行时动态调用JavaScript脚本，大大提升了开发时的灵活机动性，也正因此导致了Apache Commons
Text远程代码执行漏洞。

### 原因分析

该漏洞存在于StringSubstitutor插值器对象中。插值器由StringSubstitutor.createInterpolator()方法创建，并允许StringLookupFactory中定义的字符串查找。这可以通过传递字符串“${prefix:name}”来使用，其中前缀如下：

![](https://image.3001.net/images/20221130/1669777179_6386c71b003332f5a8fc0.jpg!small)使用“script”、“dns”或“url”查找，将允许字符串在传递给插值器对象时，执行任意脚本。

由于Commons Text是一个库，因此插值器的具体用法将决定此漏洞的影响程度。

虽然此特定代码片段不太可能存在于生产应用程序中，但令人担忧的是，在某些应用程序中，pocstring变量可能被攻击者控制。从这个意义上说，该漏洞与Log4Shell相呼应。但是，与Log4j中易受攻击的字符串替换相比，StringSubstitutor插值器的使用范围要小得多。并且这种插值器的性质意味着，将内容输入到易受攻击的对象中的可能性，比仅与Log4Shell中的此类字符串交互的可能性要小。

### PoC/Exp

 **POC :** https://github.com/SeanWrightSec/CVE-2022-42889-PoC

