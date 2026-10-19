***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

## 1\. 概述

一时冒出个想法，由于web安全范围广、知识分散、攻击技巧又多，准备搞个命令行小工具将web安全各种知识融合在一起，包括测试的功能点、测试方法思路技巧、使用工具等等，在web测试中起到提供思路的作用。说干就干，先搞了个小样。

## 2\. 实现思路

语言：Python

数据库：sqlite3

配色用到的库：colorama

https://github.com/dandh811/summer

    
    
    import sqlite3
    from colorama import Fore, Back, Style
    
    logo = """  
    ========================================
    |       Summer                         |
    |       author:dandh811                |
    |       email: dandh811@163.com        |
    |       version:0.0.2                  |
    ========================================                                                                                                        
    """
    
    print(logo)
    
    conn = sqlite3.connect('my.db')
    
    cursor = conn.cursor()
    
    
    q = False
    while not q:
        cursor.execute("select * from functions")
        functions_all = cursor.fetchall()
        res = ''
        for fun in functions_all:
            res = res + fun[0] + ' | '
        print(Fore.GREEN + "[功能模块] " + res)
        keyword = input(Fore.RED + "[!] 请输入测试功能关键字, 退出请按'q'：")
        if keyword == 'q':
            q = True
            break
        if not keyword:
            continue
        # keyword = 'login'
        cursor.execute("select * from functions where name like '%"+keyword+"%'")
        functions = cursor.fetchall()
        if functions:
            cursor.execute('select * from cases where function =?', (functions[0][0],))
            cases = cursor.fetchall()
            if cases:
                print(Fore.GREEN + '[+] "' + keyword + '"功能的测试用例如下:')
                print('-' * 80)
    
                res = {}
                i = 1
                for case in cases:
                    print('\t' + str(i) + '. ' + case[1])
                    res[i] = case[0]
                    i += 1
                print('-' * 80)
                cycle_flag = True
                while cycle_flag:
                    num = input(Fore.RED + "[!] 如果需要了解测试用例的详细信息，请输入用例序号, 按0返回上层: ")
                    if not num or not num.isdigit():
                        continue
                    if int(num) < 0 or int(num) >= i:
                        continue
                    print('-' * 80)
                    if int(num) == 0:
                        cycle_flag = False
                    else:
                        cursor.execute('select * from cases where id =?', (res[int(num)],))
                        case = cursor.fetchall()[0]
                        print(Fore.WHITE + "[用例名称] " + case[1])
                        if case[5]:
                            print(Fore.YELLOW + "[用例描述] " + case[5])
                        if case[7]:
                            print(Fore.GREEN + "[payload] " + case[7])
                        if case[3]:
                            print(Fore.MAGENTA + "[推荐工具] " + case[3])
                        if case[4]:
                            print(Fore.CYAN + "[参考资料] " + case[4])
                        if case[6]:
                            contributor = case[6]
                        else:
                            contributor = 'dandh811'
                        print(Fore.BLUE + "[贡献者] " + contributor)
                        print('-' * 80)
    
    
            else:
                print("[!] 该功能测试用例待完善")
            print('[!] 如果觉得太low或者有更好的需要补充，请输入"+"进行反馈。')
        else:
            print('[!] 未匹配到该搜索，系统还在完善中!')
    
    conn.close()
    
    

实现效果如下图：  
![微信截图_20210730073247.png](https://image.3001.net/images/20210730/1627602494_61033e3ee58df9843d143.png!small)

