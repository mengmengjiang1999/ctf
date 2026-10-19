一款 x64dbg
自动化控制插件，通过Python控制x64dbg，实现远程动态调试，解决了逆向工作者分析漏洞，反病毒人员脱壳，寻找指令片段，原生脚本不够强大的问题，通过与Python相结合利用Python语法的灵活性以及丰富的第三方库，加速漏洞利用程序的开发，辅助漏洞挖掘以及恶意软件分析。

python包请安装与插件一致的版本，在cmd命令行下执行pip 命令即可安装。

  * 安装标准包：pip install LyScript32 或者 pip install LyScript64
  * 安装扩展包：pip install LyScriptTools32 或者 pip install LyScriptTools64

其次您需要手动下载对应x64dbg版本的驱动文件，并放入指定目录下。

  * 插件下载：[LyScript32 1.0.11 (32位插件)](https://github.com/lyshark/LyScript/raw/master/plugins/LyScript32-1.0.11.zip)或者 [LyScript64 1.0.11 (64位插件)](https://github.com/lyshark/LyScript/raw/master/plugins/LyScript64-1.0.11.zip)

插件下载好以后，请将该插件复制到x64dbg目录下的plugins目录下，程序运行后会自动加载插件文件。  
![901106_SA39Z7HZJ9XV4F2.jpg](https://image.3001.net/images/20220723/1658552243_62db7fb3b78a7e45ff2b6.jpg!small)

当插件加载成功后，会在日志位置看到具体的绑定信息以及输出调试，该插件并不会在插件栏显示。![image](https://image.3001.net/images/20220723/1658552244_62db7fb49bfbd313e7fd3.jpg!small)

如果需要远程调试，则只需要在初始化`MyDebug()`类是传入对端IP地址即可，如果不填写参数则默认使用`127.0.0.1`地址，请确保对端放行了`6589`端口，否则无法连接。  
![image](https://image.3001.net/images/20220723/1658552245_62db7fb58441f182e89dc.jpg!small)

运行x64dbg程序并手动载入需要分析的可执行文件，然后我们可以通过`connect()`方法连接到调试器，连接后会创建一个持久会话直到python脚本结束则连接会被强制断开，在此期间可调用`is_connect()`检查该链接是否还存在，具体代码如下所示。

    
    
    from LyScript32 import MyDebug
    
    if __name__ == "__main__":
        # 初始化
        dbg = MyDebug()
    
        # 连接到调试器
        connect_flag = dbg.connect()
        print("连接状态: {}".format(connect_flag))
    
        # 检测套接字是否还在
        ref = dbg.is_connect()
        print("是否在连接: ", ref)
    
        dbg.close()
    

GitHub 项目地址：<https://github.com/lyshark/LyScript>

