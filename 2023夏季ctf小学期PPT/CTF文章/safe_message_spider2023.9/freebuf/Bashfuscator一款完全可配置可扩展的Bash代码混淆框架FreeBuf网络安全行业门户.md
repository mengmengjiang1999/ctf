![](https://image.3001.net/images/20230824/1692880368_64e74df05eb45074efa79.png!small)

## 关于Bashfuscator

Bashfuscator是一款完全可配置可扩展的Bash代码混淆框架，该工具专为红队和蓝队研究人员设计，它通过将不同的混淆技术和方法组织到框架内的模块中来实现其功能，而这些技术和方法我们将其称之为“Mutator”。该工具基于Python
3开发，可以通过叠加不同的Mutator来创建和生成具备不同特性的Payload。

该工具的主要目标是为了帮助研究人员通过绕过Linux系统上的静态检测，来测试和提升Linux系统的安全性。除此之外，该工具也适用于想要研究代码模糊测试技术的用户。

该工具目前支持下列五种类型的Mutator：

> 1、命令混淆；
>
> 2、字符串混淆；
>
> 3、令牌混淆；
>
> 4、编码器；
>
> 5、压缩器；

## Payload支持

尽管Bashfuscator确实可以在UNIX系统上工作，但它生成的许多Payload却不一定可以。这是因为大多数UNIX系统使用BSD风格的实用程序，而Bashfuscator是为使用GNU风格的应用程序而构建的。未来可能会添加BSD
Payload的支持，但目前使用Bashfuscator生成的Payload应该可以在使用Bash 4.0或更新版本的GNU Linux系统上工作。

## 工具安装

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3.6+环境。

接下来，在基于Debian的发行版系统中，广大研究人员可以使用下列命令安装工具所需的依赖组件：

    
    
    sudo apt-get update && sudo apt-get install python3 python3-pip python3-argcomplete xclip

在基于RHEL的发行版系统中，我们可以使用下列命令安装工具所需的依赖组件：

    
    
    sudo dnf update && sudo dnf install python3 python3-pip python3-argcomplete xclip

接下来，我们可以运行下列命令将该项目源码克隆至本地，并完成工具的安装：

    
    
    git clone https://github.com/Bashfuscator/Bashfuscator
    
    cd Bashfuscator
    
    python3 setup.py install --user

需要注意的是，当前版本的Bashfuscator仅支持基于Debian和RHEL的发行版系统。

## 工具使用样例

我们可以直接将需要混淆的命令使用-c选项传递给工具，或使用-f命令将需要混淆的脚本传递给工具即可：

    
    
    $ bashfuscator -c "cat /etc/passwd"
    
    [+] Mutators used: Token/ForCode -> Command/Reverse
    
    [+] Payload:
    
     
    
       ${@/l+Jau/+<b=k } p''"r"i""n$'t\u0066'  %s  "$(      ${*%%Frf\[4?T2   }  ${*##0\!j.G }   "r"'e'v <<< '   "} ~@{$"   ")  }  j@C`\7=-k#*{$   "}   ,@{$"  ; }  ;   } ,,*{$  "}]  }   ,*{$  "}   f9deh`\>6/J-F{\,vy//@{$" niOrw$   } QhwV#@{$ [NMpHySZ{$"  s%  "f"'"'"'4700u\n9600u\r'"'"'$p  {   ;  }  ~*{$  "}  48T`\PJc}\#@{$"   1#31  "}  ,@{$"   }  D$y?U%%*{$ 0#84  *$   }   Lv:sjb/@{$   2#05   }   ~@{$   2#4   }*!{$  }   OGdx7=um/X@RA{\eA/*{$ 1001#2   }   Scnw:i/@{$  } ~~*{$  11#4   "} O#uG{\HB%@{$"   11#7 "} ^^@{$"  011#2   "}   ~~@{$" 11#3 }  L[\h3m/@{$  "}   ~@{$" 11#2 }  6u1N.b!\b%%*{$   }   YCMI##@{$   31#5 "} ,@{$" 01#7  }  (\}\;]\//*{$ }   %#6j/?pg%m/*{$   001#2  "}  6IW]\p*n%@{$"   }  ^^@{$ 21#7  } !\=jy#@{$  }   tz}\k{\v1/?o:Sn@V/*{$  11#5   ni   niOrw  rof ;   "}   ,,@{$"  } MD`\!\]\P%%*{$   )  }@{$   a   }  ogt=y%*{$ "@$" /\   }   {\nZ2^##*{$    \   *$  c  }@{$  }   h;|Yeen{\/.8oAl-RY//@{$   p  *$  "}@{$"  t   }  zB(\R//*{$  } mX=XAFz_/9QKu//*{$  e   *$  s  } ~~*{$  d   }  ,*{$   }  2tgh%X-/L=a_r#f{\//*{$   w }  {\L8h=@*##@{$   "}   W9Zw##@{$"  (=NMpHySZ    ($"  la'"'"''"'"'"v"'"'"''"'"''"'"'541\'"'"'$  } &;@0#*{$ '   "${@}" "${@%%Ij\[N   }"    ${@~~  }   )"  ${!*} |   $@  $'b\u0061'''sh   ${*//J7\{=.QH   }  
    
     
    
    [+] Payload size: 1232 characters

接下来，我们还可以使用--clip命令将混淆后的Payload拷贝到剪贴板，或使用-o命令将其输出到文件中。

我们还可以使用--chose-mutators选项来指定需要使用的混淆模块或Mutator：

    
    
    bashfuscator -c "cat /etc/passwd" --choose-mutators token/special_char_only compress/bzip2 string/file_glob -s 1
    
    [+] Payload:
    
     
    
    "${@#b }"  "e"$'\166'"a""${@}"l "$(  ${!@}m''$'k\144'''ir -p '/tmp/wW'${*~~} ;$'\x70'"${@/AZ }"rin""tf  %s  'MxJDa0zkXG4CsclDKLmg9KW6vgcLDaMiJNkavKPNMxU0SJqlJfz5uqG4rOSimWr2A7L5pyqLPp5kGQZRdUE3xZNxAD4EN7HHDb44XmRpN2rHjdwxjotov9teuE8dAGxUAL'>  '/tmp/wW/?
    
    ??';  prin${@#K. }tf %s  'wYg0iUjRoaGhoNMgYgAJNKSp+lMGkx6pgCGRhDDRGMNDTQA0ABoAAZDQIkhCkyPNIm1DTQeppjRDTTQ8D9oqA/1A9DjGhOu1W7/t4J4Tt4fE5+isX29eKzeMb8pJsPya93'  >  '/tmp/wW/???
    
    ' "${@,, }"  &&${*}pri''\n${*,}tf %s 'RELKWCoKqqFP5VElVS5qmdRJQelAziQTBBM99bliyhIQN8VyrjiIrkd2LFQIrwLY2E9ZmiSYqay6JNmzeWAklyhFuph1mXQry8maqHmtSAKnNr17wQlIXl/ioKq4hMlx76' >'/tmp/wW/??
    
     
    
    ';"${@,  }" $'\x70'rintf  %s 'clDkczJBNsB1gAOsW2tAFoIhpWtL3K/n68vYs4Pt+tD6+2X4FILnaFw4xaWlbbaJBKjbGLouOj30tcP4cQ6vVTp0H697aeleLe4ebnG95jynuNZvbd1qiTBDwAPVLTtCLx' >'/tmp/wW/?
    
     
    
    ?' ;  ${*/~} p""${@##vl  }ri""n''tf %s  '  pr'"'"'i'"'"'$'"'"'n\x74'"'"'f %s  "$( prin${*//N/H  }tf  '"'"'QlpoOTFBWSZTWVyUng4AA3R/gH7z/+Bd/4AfwAAAD8AAAA9QA/7rm7NzircbE1wlCTBEamT1PKekxqYIA9TNQ' >'/tmp/wW/????'  "${@%\`  }"  ;p''r""i$'\x6e'''$'\164'"f" %s 'puxuZjSK09iokSwsERuYmYxzhEOARc1UjcKZy3zsiCqG5AdYHeQACRPKqVPIqkxaQnt/RMmoLKqCiypS0FLaFtirJFqQtbJLUVFoB/qUmEWVKxVFBYjHZcIAYlVRbkgWjh'  >'/tmp/wW/?
    
     
    
     
    
    '  ${*};"p"rin''$'\x74f' %s  'Gs02t3sw+yFjnPjcXLJSI5XTnNzNMjJnSm0ChZQfSiFbxj6xzTfngZC4YbPvaCS3jMXvYinGLUWVfmuXtJXX3dpu379mvDn917Pg7PaoCJm2877OGzLn0y3FtndddpDohg'>'/tmp/wW/?
    
    ?
    
    ' && "${@^^ }"  pr""intf  %s  'Q+kXS+VgQ9OklAYb+q+GYQQzi4xQDlAGRJBCQbaTSi1cpkRmZlhSkDjcknJUADEBeXJAIFIyESJmDEwQExXjV4+vkDaHY/iGnNFBTYfo7kDJIucUES5mATqrAJ/KIyv1UV'> '/tmp/wW/
    
    ???'  ${*^}; ${!@}  "${@%%I  }"pri""n$'\x74f' %s '1w6xQDwURXSpvdUvYXckU4UJBclJ4OA'"'"'  |""b${*/t/\(  }a\se$'"'"'6\x34'"'"' -d| bu${*/\]%}nzi'"'"'p'"'"'${!@}2  -c)"  $@  |${@//Y^  } \ba\s"h"  ' >  '/tmp/wW/
    
    ??
    
    ' ${@%b  } ;  pr"i"\ntf  %s  'g8oZ91rJxesUWCIaWikkYQDim3Zw341vrli0kuGMuiZ2Q5IkkgyAAJFzgqiRWXergULhLMNTjchAQSXpRWQUgklCEQLxOyAMq71cGgKMzrWWKlrlllq1SXFNRqsRBZsKUE' >  '/tmp/wW/??
    
    ?'"${@//Y  }" ;$'c\141t' '/tmp/wW'/????  ${*/m};"${@,,  }"  $'\162'\m '/tmp/wW'/????  &&${@^ }rmd\ir  '/tmp/wW'; ${@^^  }   )"  "${@}"  
    
     
    
    [+] Payload size: 2062 characters

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/Bashfuscator/Bashfuscator/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Bashfuscator** ：【[
_GitHub传送门_](https://github.com/Bashfuscator/Bashfuscator)】

## 参考资料

> [
> _https://bashfuscator.readthedocs.io/en/latest/Usage.html_](https://bashfuscator.readthedocs.io/en/latest/Usage.html)
>
> [
> _https://www.youtube.com/watch?v=zef422NDmpo_](https://www.youtube.com/watch?v=zef422NDmpo)

