# 前言

之前面试时遇到了C2相关的问题，这里在github上找了一个比较简单的C2，对其进行分析，算是迈入自己写C2的第一步

# 文件目录

-agent：nim编写的客户端  
-builder：elf、exe等程序生成器，加壳等操作  
-server：控制端  
-config.jsonc：配置文件  
-Nimbo-C2.py：主文件，调用该文件启动nimbo-c2

# 文件分析

## config.jsonc

文件作用：存储配置信息，主要包括协议、侦听端口、通信加密（aes）相关、日志文件等

### listener

    
    
    scheme：通信时使用的协议，目前该C2只支持http协议
    listen_on_address/port：listener侦听的地址和端口
    address/port：实际侦听的端口？不太理解，需要看看后续源码
        目前理解是listen_on的端口和agent建立连接，流量转发给port的端口
    

### agent

    
    
    call_home_timeframe/jitter_percent以及sleep_on_execution：用于隐蔽通信，没有任务时、初始化后的休眠时间
        感觉设计比较巧妙的点在于call_home_jitter_percent
    exe/dll/elf：有些局限，exe和elf似乎只能指定路径才能够识别，没有那么智能，痕迹挺明显
    

### communication

    
    
    aes加密用的key和iv，应该是数据传输用的
    

### c2

    
    
    logging：日志信息
    save_agents_data：保存agents相关的内容，目前理解为保存agents的回包吧，后续运行后分析
    prompt：没什么用的配置项，可以使界面变得亮晶晶（bushi）
    general：全局配置信息，是否开启listener、是否收集agents信息
    

### builder

    
    
    upx路径，该工具用的upx壳子，似乎还有一个nimprotect，后面看了一下只是简单的加解密
    

## Nimbo-C2.py

文件作用：主控端，运行后启动Nimbo-C2  
banner信息：一个痞老板？  
700多行，banner和help信息偏多，这里按照顺序梳理一下程序逻辑，按照函数进行分析  
初始化操作主要两步  
1、解析配置文件  
2、创建更好看的控制界面  
exit_nimbo：退出后的一些操作，主要根据配置文件确定是否保存日志等信息  
print_main_help：输出一些帮助信息，主控端的  
print_agent_help：输出远控可以实现的功能  
print_agents：输出目前上线的agents相关信息  
agent_screen_windows/linux：agent_help中一些功能的实现，封装为command_dict  
send_build_command：调用build创建一个落地文件  
main_screen：主控端的功能实现，main_help中的功能，死循环  
main函数：根据配置信息确定是否开启listener  
调主控功能main_screen  
总结看，功能比较全面，如果是一个人维护的整个项目，可以算是大佬了

## builder文件夹

### build.py

    
    
    首先定义了一些编译选项（nim不太了解，后续补充相关知识）
    之后解析配置文件，设置好配置项
    pack_upx：运行upx加壳，中间有对节重命名，一般upx加壳好像自动重命名，以upx开头
    build_exe/dll/elf：运行nim编译，生成exe/dll/elf
    main：解析build命令的参数
    

### config2agent.py

    
    
    首先读取配置文件（config.jsonc）
    设置了nimprotect相关的配置，该部分为一个单独的项目，后续对该部分分析
    create_config：将之前的配置写入到config.nim中
    

总结看，builder主要实现了生成exe、dll、elf文件，加入了upx加壳和nimprotect保护（可能是，后续分析）

## server文件夹

### utils.py：一些辅助函数

    
    
    log_message：以格式化的方式输出内容到日志
    clear_screen：清屏
    sanitize_data：数据清晰，替换\x00和转义单引号（可能数据传输时有坏字符吧，后续抓包分析）
    encrypt_cbc：aes的cbc加密，这里提一个todo，尝试抓流量做MITM
    decrypt_cbc：aes_cbc解密
    encode/decode_base_64：base64编解码
    is_valid_file：判断是否为有效文件
    read_file：读取文件
    write_file：写文件
    文件最后进行了一些设置，还是解析config.jsonc文件
    

### listener.py：核心功能，重新封装了一份http（看到这里其实比较好奇客户端怎么做的了）

    
    
    C2类：实现C2功能
        send_default_headers_and_status_code：发送了200和content-type
        update_last_checkin：ua头中有agent相关内容，保存最后一次交互的时间
        valid_request：判断请求类型是否有效，仍旧根据ua头
        parse_agent_data：执行一些具体操作了，核心功能都在这个地方，重点看agent_data从哪里来
        do_POST：处理post请求，这里可以看到agent_data从post请求体来，post有加密
        do_GET：处理get请求，建立连接和发送指令用
    listener_start：开启listener
    listener_status：查看状态
    listener_stop：关闭
    main函数：根据keep_listen状态判断是否处理请求还是关闭
    文件尾读取配置，开启一个c2（httpserver）和侦听用的线程
    

### ps_modules.py：powershell功能

    
    
    read_ps_module：读取两个powershell文件
    看了一下pstree功能为列进程，software为读取当前安装的软件（可能有误）
    

总结看，感觉很有新意，作者思路比较清晰，post和get处理数据的模式分得比较开（其实有种看大马的感觉）  
数据执行时有一个类似心跳的机制，并不是一直连着的

## agent

全部都是nim语言写的，主要功能为client端的操作

### common.nim

    
    
    一些辅助函数，包括加密、编码、执行命令、写文件等（和listener交互）
    post_data：发送post数据，和listener部分以post方式进行交互，包括数据类型和实际数据
    run_command_shell：命令执行功能，输出给到listener
    exfil_file：以base64方式读取文件并传输
    write_file：写文件功能
    change_sleep_time：更改sleep时间
    kill_agent：退出agent
    en/decrypt_cbc：cbc加解密
    en/decode_base64：base64编解码
    calc_sleep_time：返回sleep的时间
    

从这里可以看到，读写文件被base64编码，其他post的数据以cbc加密

### config.nim

    
    
    一些配置信息，根据之前build进行更改，这里不详细分析字段
    

### dll.nim

    
    
    生成dll使用的nim，主要调NimMain和nimbo_main两个函数
    NimMain可以理解为dllmain函数（可能有误）
    

elf/exe.nim：均调用了nimbo_main

### main.nim

    
    
    主函数实现，有对nimbo_main函数的实现
    这里对主函数功能分析
    1、请求一次c2
    2、解码返回信息
    3、解析回包并执行
    

### windows文件夹：核心功能在这里

    
    
    core
        collect_data：信息收集，执行了一次powershell，从命名上看，收集到的有hostname、系统版本、进程信息、用户及权限、ip信息等
            execute_encoded_powershell这个函数比较有意思，后面具体分析
        wrap_execute_encoded_powershell：对execute_encoded_powershell做了一个wrapper，支持执行及回传数据
        checksec：获取安装的杀软信息
        wrap_get_clipboard：获取剪切板内容
        wrap_get_screenshot：获取截屏内容
        wrap_record_audio：获取音频内容，有落地文件r.w
        dump_lsass：读取lsass内存，有落地文件l.d
        dump_sam：获取sam、system、security文件，均有落地文件，分别为s.am\s.ec\s.ys
        wrap_inject_shellc：向进程中注入shellcode
        wrap_execute_assembly：看命名，应该是执行汇编代码
        wrap_unhook_ntdll：解掉对ntdll的hook
        wrap_patch_func：看命名，应该是对函数进行patch，类似inline hook的操作吧
        set_run_key：设置自启动注册表项
        set_spe：设置spe
        uac_bypass：uac绕过，这里用了两种方式
        msgbox：弹一个messagebox
        speak：似乎是语音输出功能
        change_sleep_time：修改sleep的时间
        get_windows_agent_id：利用powershell拿uuid和guid
        is_elevated：判断是否高权限
        windows_start：启动一个agent进程
        windows_parse_command：解析传过来的命令并进行执行，在main.nim中有对函数的调用
    

### utils文件夹

    
    
    该文件夹保存具体功能的实现，这里只分析几个比较感兴趣的功能，其他的可以自行分析
        misc：对lsass内存dump
            首先获取lsass的pid，之后利用MiniDumpWriteDump API保存至l.d文件中
        priv：权限提升操作，主要调用一些windows的API
        clr：命令执行操作
            利用system.management.automation来执行命令
        memops：内存操作，包括unhook和patch
            unhook_ntdll：对ntdll解挂
                调用了一些nim支持的api接口
                操作比较粗暴，直接把原始文件盖过去了
            patch_func：这里对ntdll做了inline hook，主要hook了两个函数
                反病毒和日志记录
            inject_shellcode：向进程内注入shellcode
                远程线程注入，流程比较常规
    总结整个windows下的远控功能，感觉没有想象中的那么强大，比如hook部分、注入部分比较单薄
    也有一些比较有新意的点，感觉可以在实战中借鉴一下
    痕迹还是比较明显的
    

### linux文件夹

    
    
    linux下agent的核心功能
    core：和windows下基本一致
        collect_data：收集信息用，主要读取/etc
        wrap_load_memfd：暂时不清楚该函数的功能
        get_linux_agent_id：读取machine id
        linux_start：开启linux下的agent进程
        linux_parse_command：解析命令并进行执行
    utils文件夹：这里只有一个memfd.nim，为核心文件
        load_memfd：两种模式，一种为等待子进程结束，一种直接返回
            实现了无文件elf运行，操作也比较常规
    

总结整个agent端，windows下的操作似乎比linux更多，但linux本身也不需要额外操作（如截屏等），只要能执行命令即可  
其中的一些trick比较有意思，可以学习一下

# 总结

整体来看，Nimbo-C2实现的功能比较全面，如果是一个人完成，那算得上大佬了  
实战价值应该不高，尤其一些内存、注册表的敏感操作，比较简单粗暴，后续实际部署后抓包对流量、痕迹、免杀效果进行分析  
提一个todo，将agent端修改为C实现，并扩充功能  
再次吐槽freebuf的md模式，我不知道这篇发出来会是什么样子的，反正在vs里排版挺正常的（甩锅~）

