## 介绍

咱们计划使用PHP调用Python插件来实现插件扫描器，但是PHP在调用Python时候，一般人看来，若使用命令执行方式是非常粗糙的。于是有些大佬，开始思考如何请PHP轻松愉快的调用Python，这时出现一款组件，它解决了PHP调用Python的难题。它就是PHP-Python，能够通过 [Github PHP-Python](https://github.com/liuzhen153/php-python)
对它进行关注。值得一提的是此库是在年久失修的PPython基础上改写，作者为了表达尊敬故沿用原名。

## 令人惊喜Demo

PHP-Python的作者非常用心的使用ThinkPHP 5.0 为用户们展示借助PHP-Python调用Python。经过咱们测试PHP-Python对于Linux的支持是令人满意的。关于如何使用继续说明。

### 使用方法（以ThinkPHP5为例）

#### 类库端的操作

1.克隆代码放到example的extend目录下。

2.在python目录下新建文件目录和文件，例：test/test.py。

3.python文件的基本写法和以前没有区别，其实就是将对外部访问的部分封装成方法，最终要将结果返回一个字符串或数组。

4.在test.py中写入你要调用的方法，例：

    
    
    # 无参数
    def hello():
        return 'Hi , Tommy'
    
    # 传递参数
    def hello_name(name):
        return 'Hi , ' + name
    
    # 返回数组
    def return_arr():
        user = {}
        user['name'] = 'Tommy'
        user['age']     = 24
        return user
    
    # 由于PHP传过来的参数都会被处理成字符串类型，所以需要使用数字类型的地方请自行转换，如若是其他类型数据做类似处理，否则会报错。
    # 但是由Python传给PHP的结果的数据类型不受限制
    def dosum(num1 , num2):
        return int(num1) + int(num2)
    

4.使用终端用python3运行类库下的php_python.py文件

python3 php_python.py 看到以下输出，证明启动成功

    
    
    -------------------------------------------    - PPython Service
    - Time: 2017-08-04 13:24:13
    -------------------------------------------    Listen port: 21230
    charset: utf-8
    Server startup...
    

#### 在控制器中如何使用

  * 头部要引用该类库

    
    
    use ppython\Ppython;
    

  * 示例代码

    
    
    <?php
    namespace app\index\controller;
    use ppython\Ppython;
    
    class Index
    {
        // 不带参数
        public function py()
        {
            $python = new Ppython();
            $data = $python->py("sayhi.hi::hello");
            dump($data);
        }
    
        //带参数的方法
        public function py_with_something($name)
        {
            $python = new Ppython();
                // 更多参数依次往后添加
            $data = $python->py("sayhi.hi::hello_name",$name);
            dump($data);
        }
    
        // python返回的是数组
        public function py_arr()
        {
            $python = new Ppython();
            $data = $python->py("sayhi.hi::return_arr");
            dump($data);
        }
    
        // PHP传递数字类型变量，计算2+3的和
        public function py_num()
        {
            $python = new Ppython();
            $data = $python->py("sayhi.hi::dosum",2,3);
            dump($data);
        }
    }
    

#### 访问以查看效果

  * 开启服务器，将根目录指向example的public下。

  * 访问不带参数的方法 <http://localhost/index/index/py>

直接会得到结果 string(10) "Hi , Tommy"

  * 访问带参数的方法，可以依次将参数跟在方法后面 <http://localhost/index/index/py_with_something/name/Handsom_Tommy>

经过Python处理后得到结果（多参数的情况按照说明使用即可）

string(18) "Hi , Handsom_Tommy"

  * Python返回给PHP的结果不受限制，我们来测试下返回一个数组

<http://localhost/index/index/py_arr>

得到相应数组

    
          array(2) {
      ["name"] => string(5) "Tommy"
      ["age"] => int(24)
      }
    

  * 由于PHP传过来的参数都会被处理成字符串类型，所以需要使用数字类型的地方请自行转换，如若是其他类型数据做类似处理，否则会报错。

<http://localhost/index/index/py_num>

得到以下结果，Python返回给PHP的数据类型不受限制

int(5)

## 如何研发插件式扫描器

ThinkPHP的能力很强，足够轻松的将多层做的满意。插件方面可以通过PHP-Python，使用Python任务调度器进行对于Python插件的任务调度或PHP-Python直接调度Python插件。对于咱们研发插件式扫描器提供了眼前一亮的解决方案。关于架构方面，如果可以请参考 《轻量级插件式扫描器逻辑功能实现》
研究或讨论。

## 总结

PHP-Python的优势在于解决常年为人诟病的调用中颗粒度和效率问题。能够使用多种编程更好的发挥其优秀面解决实际的问题。用于插件式扫描器只是其中小部分应用方案，期待它还能有更多的作为。

