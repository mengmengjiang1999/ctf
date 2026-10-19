来源：[先知安全技术社区](https://xianzhi.aliyun.com/forum/read/1973.html)  
作者：phpoop

#### 0x00 框架运行环境

ThinkPHP 是一个免费开源的，快速、简单的面向对象的轻量级 PHP 开发框架，是为了敏捷 WEB 应用开发和简化企业应用开发而诞生的。ThinkPHP
从诞生以来一直秉承简洁实用的设计原则，在保持出色的性能和至简的代码的同时，也注重易用性。

Thinkphp 在使用缓存的时候是将数据 序列化 然后存进一个 php 文件中这就导致我们了我们在一些情况下可以直接 getshell

#### 0x01 漏洞利用

该漏洞形成最关键的一点是，需要使用框架时，有使用缓存，才能利用这个漏洞

![](https://images.seebug.org/content/images/2017/08/1-4.png-w331s)

我们这里使用缓存查看官网对这个缓存类的说明以及利用方法

![](https://images.seebug.org/content/images/2017/08/2-7.png-w331s)
![](https://images.seebug.org/content/images/2017/08/3-6.png-w331s)

本地按照官方给的文档安装成功后，根据官网给的缓存使用方法，新建一个方法，我们都清楚缓存一般是为了减少数据库的开销为设置的，所以缓存的数据一般也是从数据库获取到的为了模拟线上，我们这里先查数据库数据在写入缓存。

![](https://images.seebug.org/content/images/2017/08/4-5.png-w331s)

这里我们写了一个add添加数据的方法

![](https://images.seebug.org/content/images/2017/08/5-5.png-w331s)
![](https://images.seebug.org/content/images/2017/08/6-5.png-w331s)
![](https://images.seebug.org/content/images/2017/08/7-4.png-w331s)

%2F%2F%0D%0A = //+回车

![](https://images.seebug.org/content/images/2017/08/8-4.png-w331s)
![](https://images.seebug.org/content/images/2017/08/9-4.png-w331s)

执行完以后查看方法缓存目录

![](https://images.seebug.org/content/images/2017/08/10-3.png-w331s)
![](https://images.seebug.org/content/images/2017/08/11-3.png-w331s)

这里需要特别说的一点是 TP的缓存名字是不变的，所以我们在审计的时候不用怕缓存文件名猜不到的情况。

![](https://images.seebug.org/content/images/2017/08/12-3.png-w331s)

#### 0x02 漏洞分析

上面我们展示了漏洞利用方法，这里我们对这个漏洞进行分析

![](https://images.seebug.org/content/images/2017/08/13-3.png-w331s)
![](https://images.seebug.org/content/images/2017/08/14-3.png-w331s)
![](https://images.seebug.org/content/images/2017/08/15-3.png-w331s)
![](https://images.seebug.org/content/images/2017/08/16-2.png-w331s)

为了证明我们的逻辑是对的我们这里打印一下返回的数据

![](https://images.seebug.org/content/images/2017/08/17-1.png-w331s)
![](https://images.seebug.org/content/images/2017/08/18-1.png-w331s)

通过这个我们就可以知道了下面这个截图的意思

![](https://images.seebug.org/content/images/2017/08/19-1.png-w331s)

实例化 \thinkp\cache\driver\ 文件里面的File类 并且调用set方法

![](https://images.seebug.org/content/images/2017/08/20-1.png-w331s)
![](https://images.seebug.org/content/images/2017/08/21-1.png-w331s)

缓存文件名称的获取方法

![](https://images.seebug.org/content/images/2017/08/22-1.png-w331s)
![](https://images.seebug.org/content/images/2017/08/23-1.png-w331s)
![](https://images.seebug.org/content/images/2017/08/24-1.png-w331s)
![](https://images.seebug.org/content/images/2017/08/25-1.png-w331s)
![](https://images.seebug.org/content/images/2017/08/26-1.png-w331s)

#### Thinkphp3.2 缓存函数设计缺陷

这个感觉没什么可以说的，和上面的原理是一样的，我们只演示攻击的方法

![](https://images.seebug.org/content/images/2017/08/27-1.png-w331s)
![](https://images.seebug.org/content/images/2017/08/28.png-w331s)
![](https://images.seebug.org/content/images/2017/08/29.png-w331s)
![](https://images.seebug.org/content/images/2017/08/30.png-w331s)
![](https://images.seebug.org/content/images/2017/08/31.png-w331s)
![](https://images.seebug.org/content/images/2017/08/32.png-w331s)
![](https://images.seebug.org/content/images/2017/08/33.png-w331s)
![](https://images.seebug.org/content/images/2017/08/34.png-w331s)

#### 修复方案

通过上面的过程与分析我们可以清楚了解造成这个漏洞的主要原因就是换行与回车导致绕过了注释。那么我们修复的方法就很简单了只要删除这些即可

修复方法：

  1. 打开文件：thinkphp\library\think\cache\driver\File.php
  2. 找到：`public function set($name, $value, $expire = null)` 方法
  3. 添加：`$data = str_replace(PHP_EOL, '', $data);` 如下图

![](https://images.seebug.org/content/images/2017/08/35.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/374/>

