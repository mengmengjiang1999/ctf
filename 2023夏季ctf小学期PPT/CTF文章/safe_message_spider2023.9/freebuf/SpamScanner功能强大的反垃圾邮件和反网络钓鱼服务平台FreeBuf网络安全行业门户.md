![](https://image.3001.net/images/20220107/1641525096_61d7af680f399e3961100.png!small)  

## 关于Spam Scanner

Spam Scanner是一款功能强大的[ _反垃圾邮件_](https://en.wikipedia.org/wiki/Anti-spam_techniques)、[ _电子邮件过滤_](https://en.wikipedia.org/wiki/Email_filtering)和[
_网络钓鱼防御_](https://en.wikipedia.org/wiki/Phishing)服务平台。Spam
Scanner也是SpamAssassin、rspamd、SpamTitan等产品的最佳替代选择。

我们的目标是建立和利用一个可扩展、性能好、简单、易于维护、功能强大的API，用于我们的转发电子邮件服务，以限制垃圾邮件，并提供其他措施来防止网络犯罪分子对我们的用户展开攻击。

最初我们尝试使用SpamAssassin，后来评估了rspamd，但最终我们发现所有现有的解决方案都非常复杂，缺少所需的功能或文档，配置起来也比较麻烦，技术壁垒较高，从其他角度来说也限制了平台的可扩展性。

对我们来说，我们重视隐私以及数据和用户的安全性——特别是我们对存储任何类型的日志或元数据都有“零容忍政策”。这些解决方案中没有一个符合这一隐私政策（没有删除基本的垃圾邮件检测功能），因此Spam
Scanner便应运而生。

## 功能介绍

Spam Scanner基于现代化技术构建，可以提供高性能服务，有助于减少垃圾邮件、网络钓鱼和其它类型的攻击。

> 1、朴素贝叶斯分类器
>
> 2、垃圾邮件内容检测
>
> 3、网络钓鱼内容检测
>
> 4、可执行文件链接和附件检测
>
> 5、病毒检测
>
> 6、NSFW（Not Safe For Work）图片检测

## 工具依赖组件

> [ _Node.js_](https://nodejs.org/)
>
> [ _Cloudflare_](https://cloudflare.com/)
>
> [ _ClamAV_](https://www.clamav.net/)

## ClamAV配置

### Ubuntu

 **1、安装ClamAV**

    
    
    sudo apt-get update
    
    sudo apt-get install build-essential clamav-daemon clamav-freshclam clamav-unofficial-sigs -qq
    
    sudo service clamav-daemon start

 **2、配置ClamAV**

    
    
    sudo vim /etc/clamav/clamd.conf
    
    
    -Example
    
    +#Example
    
     
    
    -#StreamMaxLength 10M
    
    +StreamMaxLength 50M
    
     
    
    +# this file path may be different on your OS (that's OK)
    
     
    
    \-#LocalSocket /tmp/clamd.socket
    
    \+LocalSocket /tmp/clamd.socket
    
    
    sudo vim /etc/clamav/freshclam.conf
    
    
    -Example
    
    +#Example

 **3、确保ClamAV在开机时自动启动**

    
    
    systemctl enable freshclamd
    
    systemctl enable clamd
    
    systemctl start freshclamd
    
    systemctl start clamd

### macOS

 **1、安装ClamAV**

    
    
    brew install clamav

 **2、配置ClamAV**

    
    
    # if you are on Intel macOS
    
    sudo mv /usr/local/etc/clamav/clamd.conf.sample /usr/local/etc/clamav/clamd.conf
    
     
    
    # if you are on M1 macOS (or newer brew which installs to `/opt/homebrew`)
    
    sudo mv /opt/homebrew/etc/clamav/clamd.conf.sample /opt/homebrew/etc/clamav/clamd.conf
    
    
    # if you are on Intel macOS
    
    sudo vim /usr/local/etc/clamav/clamd.conf
    
     
    
    # if you are on M1 macOS (or newer brew which installs to `/opt/homebrew`)
    
    sudo vim /opt/homebrew/etc/clamav/clamd.conf
    
    
    -Example
    
    +#Example
    
     
    
    -#StreamMaxLength 10M
    
    +StreamMaxLength 50M
    
     
    
    +# this file path may be different on your OS (that's OK)
    
     
    
    \-#LocalSocket /tmp/clamd.socket
    
    \+LocalSocket /tmp/clamd.socket
    
    
    # if you are on Intel macOS
    
    sudo mv /usr/local/etc/clamav/freshclam.conf.sample /usr/local/etc/clamav/freshclam.conf
    
     
    
    # if you are on M1 macOS (or newer brew which installs to `/opt/homebrew`)
    
    sudo mv /opt/homebrew/etc/clamav/freshclam.conf.sample /opt/homebrew/etc/clamav/freshclam.conf
    
    
    # if you are on Intel macOS
    
    sudo vim /usr/local/etc/clamav/freshclam.conf
    
     
    
    # if you are on M1 macOS (or newer brew which installs to `/opt/homebrew`)
    
    sudo vim /opt/homebrew/etc/clamav/freshclam.conf
    
    
    -Example
    
    +#Example
    
    
    freshclam

 **3、确保ClamAV在开机时自动启动**

    
    
    sudo vim /Library/LaunchDaemons/org.clamav.clamd.plist

## 工具安装-NPM安装

    
    
    npm install spamscanner

## 工具使用

    
    
    const fs = require('fs');
    
    const path = require('path');
    
     
    
    const SpamScanner = require('spamscanner');
    
     
    
    const scanner = new SpamScanner();
    
     
    
    //
    
    // NOTE: The `source` argument is the full raw email to be scanned
    
    // and you can pass it as String, Buffer, or valid file path
    
    //
    
    const source = fs.readFileSync(
    
      path.join(__dirname, 'test', 'fixtures', 'spam.eml')
    
    );
    
     
    
    // async/await usage
    
    (async () => {
    
      try {
    
        const scan = await scanner.scan(source);
    
        console.log('scan', scan);
    
      } catch (err) {
    
        console.error(err);
    
      }
    
    });
    
     
    
    // then/catch usage
    
    scanner
    
      .scan(source)
    
      .then(scan => console.log('scan', scan))
    
      .catch(console.error);
    
     
    
    // callback usage
    
    if (err) return console.error(err);
    
    scanner.scan(source, (err, scan) => {
    
      if (err) return console.error(err);
    
      console.log('scan', scan);
    
    });

## 许可证协议

本项目的开发与发布遵循BSL v1.1开源许可证协议。

## 项目地址

 **Spam Scanner：** 【[
_GitHub传送门_](https://github.com/spamscanner/spamscanner)】

## 参考资料

> [ _https://www.digitalocean.com/community/tutorials/how-to-setup-exim-> spamassassin-clamd-and-dovecot-on-an-arch-linux-> vps_](https://www.digitalocean.com/community/tutorials/how-to-setup-exim-> spamassassin-clamd-and-dovecot-on-an-arch-linux-vps)
>
> [ _https://medium.com/@wingsuitist/set-up-clamav-for-osx-1-the-open-source-> virus-scanner-82a927b60fa3_](https://medium.com/@wingsuitist/set-up-clamav-> for-osx-1-the-open-source-virus-scanner-82a927b60fa3)
>
> [ _http://redgreenrepeat.com/2019/08/09/setting-up-clamav-on-> macos/_](http://redgreenrepeat.com/2019/08/09/setting-up-clamav-on-macos/)
>
> [
> _https://paulrbts.github.io/blog/software/2017/08/18/clamav/_](https://paulrbts.github.io/blog/software/2017/08/18/clamav/)
>
> [
> _https://gist.github.com/zhurui1008/4fdc875e557014c3a34e_](https://gist.github.com/zhurui1008/4fdc875e557014c3a34e)

