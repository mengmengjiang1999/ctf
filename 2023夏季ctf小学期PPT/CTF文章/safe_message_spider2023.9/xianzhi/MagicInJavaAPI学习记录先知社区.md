## 前言

这篇文章主要是对[`yemoli`](yml-sec.top)和[`R1ckyZ`](r1ckyz.github.io)在KCON2023中的议题《Magic In Java API》的一次学习记录

对应的slide可以在<https://github.com/knownsec/KCon/tree/master/2023中获取>

## 概述

该议题的结构如下

  1. API的介绍
  2. 该API在各个框架或者组件能够的影响细节
  3. 在RASP中利用该API的小技巧
  4. 根据各个组件的修复方式总结了一些有效的防御措施

## API介绍

议题中API指代的就是`sun.print.UnixPrintServiceLookup`这个类

![](./img/4451348162914624816.png)

这是一个用于打印服务注册的功能的接口

一个用于查找可用的打印机服务

    
    
    public static void main(String[] args) throws IOException {
        // 获取 UnixPrintServiceLookup 实例
        PrintServiceLookup lookup = (PrintServiceLookup) PrintServiceLookup.lookupDefaultPrintService();
    
        // 使用 UnixPrintServiceLookup 查找所有可用的打印服务
        PrintService[] printServices = lookup.getPrintServices();
    
        if (printServices.length == 0) {
            System.out.println("No printers available.");
        } else {
            System.out.println("Available printers:");
            for (PrintService printer : printServices) {
                System.out.println(printer.getName());
            }
        }
    }
    

在windows中对应的功能是在`Win32PrintServiceLookup`中实现的

    
    
    public static void main(String[] args) {
        // 获取 PrintServiceLookup 实例
        // 获取所有可用的打印服务
        PrintService[] printServices = PrintServiceLookup.lookupPrintServices(null, null);
    
        if (printServices.length == 0) {
            System.out.println("No printers available.");
        } else {
            System.out.println("Available printers:");
            for (PrintService printer : printServices) {
                System.out.println(printer.getName());
            }
        }
    }
    

在`UnixPrintServiceLookup`初始化的时候

![](./img/3643366500491245430.png)

创建了一个`PrinterChangeListener`监听器，是一个线程类，不断的更新服务

![](./img/651186917617919902.png)

过程中存在有可能利用的点`getAllPrinterNamesBSD`方法中

![](./img/1329182305596563662.png)

![](./img/3311776135631057422.png)

存在有命令执行的位置，传入的参数是在`lpcAllCom`数组中的其中一个元素

如果我们能够控制传入的参数就能够达到RCE的目的

之后就是从修改类属性的”不同方法“的角度来阐明该API可能导入RCE的情况

  1. 想要更改类的属性值，我们常用的结合反序列化可以通过java中的反射机制进行类属性值的更改，这个想法在很多其他的常见反序列化利用中很常见，但是可惜的是，在`UnixPrintServiceLookup`类并没有实现`Serializable`接口

![](./img/9001103224344786876.png)

但是跟进过dubbo
rpc框架的CVE也能够知道，在类似hession这类远程调用协议，在序列化和反序列化的过程中可以反序列化没有实现`Serializable`接口的类

  1. 可能在恢复bean类的过程中会直接使用反射来恢复类属性值

## available protocols

在前面更改类属性值得其中第一个方法也就是通过反序列化过程中的反射机制来进行类属性值得更改

前面只提到了在dubbo使用hession的时候可以在没有实现`Serializable`接口得情况下进行属性值的更改

在原slide中作者总结了常见的序列化协议是否支持没有实现`Serializable`接口

![](./img/5586992553006406512.png)

也主要就是hession类和json处理类的几个协议

### Hession

在图中，可以利用的hession版本是在3.x才可以

#### Hession 3.x

我们简单跟进一下具体的能够进行利用的原理（即为什么可以支持没有实现`Serializable`接口的类的反序列化和是怎样通过反射来修改类属性

这里我们默认是对Java对象进行反序列化，因为在hessian的反序列化的过程中将会针对不同的类型选择不同的序列化器

![](./img/7253986175524739281.png)

针对Java对象，默认是使用`JavaDeserializer`这个反序列化器

  1. 首先是在`Hessian2Input#readObject`方法中

根据tag位的不同选择不同的处理方法

![](./img/6490282692096679235.png)

  1. 而在`Hessian2Input#readObjectDefinition`中主要是将反序列化的类中所有存在的类名给保存在了`_classDefs`属性中

![](./img/8856658359856180445.png)

  1. 之后又重新回到了`Hessian2Input#readObject`中进行类对象的实例化

![](./img/1152928267121573205.png)

  1. 这里并没有显示的指明反序列化的类，进而通过序列化工厂类的反序列化逻辑进行反序列化

![](./img/1978632304868631866.png)

![](./img/318961276064213782.png)

通过type确定使用默认的`JavaDeserializer`反序列化器

  1. 来到了`JavaDeserializer#readObject`中进行对象的实例化

![](./img/1948281973694496322.png)

  1. 在`JavaDeserializer#instantiate`中存在有调用构造方法的操作

![](./img/5564372609578154362.png)

  1. 在得到了反序列化类的实例之后，将其传入`JavaDeserializer#readObject`的一个同名方法中进行类属性的反序列化

![](./img/4692508503914644638.png)

对于不同的属性的类型，将会选择不同的反序列化器进行处理

![](./img/6055501162994677259.png)

这里我们象征性的看一下String类型的反序列过程

![](./img/7648700917261822029.png)

这里是通过反射进行恢复属性值

总结一下，上面也就是在hessian反序列化的过程中可能调用构造方法和反射恢复属性值的原理

至于hessian中的可以序列化和反序列化不实现`Serializable`接口的类，我们可以在`SerializerFactory#getDefaultSerializer`中找到出处

![](./img/7112408612348367951.png)

在抛出`IllegalStateException`异常需要满足条件`if
(!Serializable.class.isAssignableFrom(cl) &&
!this._isAllowNonSerializable)`如果没有实现`Serializable`接口，也可以选择将属性`_isAllowNonSerializable`设置为true

    
    
    hessianOutput.getSerializerFactory().setAllowNonSerializable(true);
    

#### Hessian 4.x

在4.x的版本中在前面的默认的反序列化器直接简单的设置为`JavaDeserializer`的基础上进行了一个限制

具体在`SerializerFactory#getDefaultSerializer`这个方法中，这个方法是用来返回一个没有被直接匹配的序列化器的一个默认的序列化器

![](./img/4470710267530726747.png)

这里的逻辑为：

  1. 如果`_defaultSerializer`不为null，就返回这个序列化器进行类对象的序列化操作，如果为null则执行 2 操作
  2. 如果没有实现`Serializable`接口的情况下同时没有开启`_isAllowNonSerializable`将会抛出异常，否则执行 3 操作
  3. 如果启动了不安全的序列化器，并且目标类中没有名为`writeReplace`的无参方法，就构造一个`UnsafeSerializer`返回
  4. 如果上面的都不满足就会返回3.x版本中的默认的JavaSerializer序列化器

而在API的触发点 -- 构造方法的入口的位置`instantiate`方法中

在3.x版本中将会在这里调用构造方法，结合之后的反射修改属性值控制参数能够达到RCE

而在这里4.x版本，使用的是`UnsafeDeserializer#instantiate`方法

![](./img/1520833044219640218.png)

使用了allocateInstance这个native方法实例化一个被序列化的对象，但是这里不会执行构造函数，也就不能够利用该API

在属性值的恢复也使用的是Unsafe类中的API

![](./img/6162207912531546063.png)

#### a case

构造一个简单的JavaBean，观察构造函数是否调用

    
    
    import java.io.Serializable;
    
    public class ObjectTest implements Serializable {
        private String cmd;
    
        public ObjectTest() {
            System.out.println("construct...");
        }
    
        public String getCmd() {
            return cmd;
        }
    
        public void setCmd(String cmd) {
            this.cmd = cmd;
        }
    }
    

分别使用3.x 4.x版本的hessian进行序列化和反序列化操作

### Hessian-lite

这个协议是在alibaba用在Dubbo这个RPC框架中的一个内置版本

维护了一些常见的黑名单

![](./img/8525123793983386187.png)

这也是导致CVE-2022-39198的sink点，我之前也分析过这个链子

<https://xz.aliyun.com/t/11961>

### sofa hessian

这个也和hessian-lite类似，都是在原始hessian的基础上的修改版本，也内置了一个黑名单

![](./img/2768929945229215370.png)

和原始的hessian类似，在4.x版本中同样使用了Unsafe的API，将不会进行构造方法的触发

## 总结

这里主要是针对hessian和其衍生的协议的角度详细学习了hessian中能够调用构造方法的原理，同时也对hessian协议有了更深的理解

