**天翼云安全研究团队** 近日得到CVE-2022-1329的漏洞资讯，由于该漏洞危害巨大，于是对其进行了研究与复现工作。  
在此分享给广大安全研究人员。

# 漏洞信息

![2022-04-20-16-01-12.png](https://image.3001.net/images/20220420/1650444628_625fc9548f0b553f4ed8b.png!small)  
[WordPress](https://wordpress.com/)是著名的博客框架，基于PHP语言开发，使用MySQL作为其数据库。而[Elementor](https://elementor.com/)是WP中流行的一个页面构建插件，据官网介绍全球有超过1千万个网站在使用Elementor。
**CVE-2022-1329** 这个漏洞针对的就是WP中的Elementor插件，所以影响范围是极大的。该漏洞可以让WP中的 **普通用户**
在WP站点中上传自己的PHP代码并运行，也就是说可以上传后门，因此造成极大的危害。  
受影响的漏洞范围是 **Elementor 3.6.0至3.6.2** 。在3.6.3中已经对该漏洞进行了修复。

# 漏洞原理

漏洞主要源于Elementor于3.6.0引入的一个新函数`function
upload_and_install_pro()`，该函数可以用于安装Elementor的pro版本，主要会执行以下步骤：

  1. 从POST请求中获取上传的pro版本zip文件

  2. 安装该zip（具体细节不重要，大概就是解压、校验）

  3. 开启该pro插件，这里会调用pro插件的主php文件  
整个函数的大致代码逻辑如下，进行了一些缩减：

    
    
    /**
     * Upload and Install Elementor Pro
     * @since 3.6.0
     * @return array
     */
    private function upload_and_install_pro() {
        $result = [];
        $error_message = __( 'There was a problem uploading your file', 'elementor' );
        // 获取上传的pro.zip
        if ( empty( $_FILES['fileToUpload'] ) ) {
            return $error_message;
        }
    
        // 此时一段不知道干嘛的代码路过，直接省略了
    
        // 安装插件，具体细节不重要
        $upload_result   = $upgrader->install( $_FILES['fileToUpload']['tmp_name'], [ 'overwrite_package' => false ] );
        if ( ! $upload_result || is_wp_error( $upload_result ) ) {
            return $error_message;
        } else {
            // 安装成功，激活pro插件
            $activated = activate_plugin( WP_PLUGIN_DIR . '/elementor-pro/elementor-pro.php', false, false, true );
    
            if ( ! is_wp_error( $activated ) ) {
                return $error_message
            }
        }
        return $result;
    }
    

这个函数最大的问题在于 **没有对权限进行检查** ，意味着普通用户也可以上传pro版本的安装包进行安装并激活，从而完成恶意代码或后门的植入。  
因此在3.6.3版本中Elementor对该函数添加了权限的判断，要求用户同时拥有 **安装插件** 和 **激活插件** 的权限才能继续：

    
    
    private function upload_and_install_pro() {
        if ( ! current_user_can( 'install_plugins' ) || ! current_user_can( 'activate_plugins' ) ) {
            return $this->get_permission_error_response();
        }
        ...
    }
    

# 漏洞复现

## 环境搭建

下载[漏洞相关数据仓库](https://github.com/Grazee/CVE-2022-1329-WordPress-Elementor-RCE)，然后可以使用 **docker** 一键开启WordPress+MySQL环境：

    
    
    docker-compose up -d
    

之后通过浏览器访问 **http://localhost:8000** 以进行WP，首次进入会需要 **创建Admin** 帐号。  
通过Admin账户进入WP管理后台，可以安装带漏洞的Elementor插件，比如3.6.1版本，[仓库](https://github.com/Grazee/CVE-2022-1329-WordPress-Elementor-RCE)里有提供zip安装包，也可以去[官方下载](https://downloads.wordpress.org/plugin/elementor.3.6.4.zip)。  
![2022-04-20-15-22-01.png](https://image.3001.net/images/20220420/1650444670_625fc97e8bafc02218419.png!small)  
然后创建一个普通权限的用户，假装自己是弱小可怜又没有权限的攻击者。  
![2022-04-20-15-23-16.png](https://image.3001.net/images/20220420/1650444677_625fc9856f9f2803ae32c.png!small)

## 漏洞利用

POC则参考了[AkuCyberSec](https://github.com/AkuCyberSec/CVE-2022-1329-WordPress-Elementor-3.6.0-3.6.1-3.6.2-Remote-Code-Execution-Exploit)发布的版本，主要步骤如下：

  1. 使用普通权限用户登录，获取Session和用户随机数nonce

  2. 通过`wp-admin/admin-ajax.php`接口提交请求，调用Elementor提供的`elementor_upload_and_install_pro`动作，并同时上传恶意的pro安装包  
![2022-04-20-15-46-55.png](https://image.3001.net/images/20220420/1650444691_625fc9937436e4d6b3d78.png!small)  
使用之前创建的普通权限用户信息，修改`poc.py`脚本中的用户名密码，然后一键发起漏洞利用：

    
    
    python3 poc.py
    

**脚本可能返回`Error - Upload
failed`，但是其实已经执行成功了。**刷新浏览器就可以看到pro安装包中的恶意代码`phpinfo();`已经会被WP执行了。  
![2022-04-20-15-49-40.png](https://image.3001.net/images/20220420/1650444708_625fc9a44cfec59940bed.png!small)  
当然也可以解压`elementor-pro.zip`，然后修改文件`elementor-pro.php`中的恶意代码，比如写入一句话木马，然后再重新打包发起攻击。

# 漏洞防御建议

目前有2种方法进行该漏洞防御：

  1. 对于使用Elementor的WP站点，将Elementor升级到3.6.3及以上版本。

  2. 没事不要开启WP的注册功能。

