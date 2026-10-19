# angr符号执行

## 将符号向量保存在内存中

在一些题目中可能缺少输入，或者不能定位输入的位置，这时要求我们将符号向量保存在内存当中。

### 06_angr_symbolic_dynamic_memory

同样ida载入

![](./img/3080418523184066757.png)

我们发现将我们输入的64位字符串保存在了内存之中。

直接写出脚本

    
    
    import angr
    import claripy
    
    p = angr.Project('06_angr_symbolic_dynamic_memory')
    start_addr = 0x08048699
    init_state = p.factory.blank_state(addr=start_addr)#跳过程序的输入直接从计算开始
    
    
    fake_addr1 = 0x12345678
    fake_addr2 = 0x12345678 - 100#随意赋给符号向量两个空间（地址随便选一个）
    buffer1 = 0x0abcc8a4
    buffer2 = 0x0abcc8ac
    
    
    init_state.memory.store(buffer1, fake_addr1, endness=p.arch.memory_endness)
    init_state.memory.store(buffer2, fake_addr2, endness=p.arch.memory_endness)
    
    v1 = claripy.BVS('v1', 64)
    v2 = claripy.BVS('v2', 64)#生成符号向量
    
    
    init_state.memory.store(fake_addr1, v1)
    init_state.memory.store(fake_addr2, v2)
    
    
    simgr = p.factory.simgr(init_state)
    
    def is_good(state):
        return b"Good Job" in state.posix.dumps(1)
    
    def is_bad(state):
        return b"Try again" in state.posix.dumps(1)
    
    simgr.explore(find=is_good, avoid=is_bad)
    
    if simgr.found:
        solution_state = simgr.found[0]
        s1 = solution_state.solver.eval(v1, cast_to=bytes).decode()
        s2 = solution_state.solver.eval(v2, cast_to=bytes).decode()#将输出的字符串打印出来
        print(s1, s2)
    

需要注意的点：

    
    
    fake_addr1 = 0x12345678
    fake_addr2 = 0x12345678 - 100#随意赋给符号向量两个空间（地址随便选一个）
    buffer1 = 0x0abcc8a4
    buffer2 = 0x0abcc8ac
    

需要注意大小端。但符号向量则不需要。

![](./img/3075196810757784755.png)

可以跑出答案。

## 文件的符号向量化

当程序读取文件的时候我们需要将文件进行符号向量化当作我们的输入。我们需要创建一个SimFile对象，该对象是个模拟文件，然后将符号变量存放在模拟文件中并将模拟文件插入到state中，这样在模拟运行时，程序就会从我们模拟的文件中读取符号变量作为输入的参数进行后续的运行。

### 07_angr_symbolic_file

![](./img/2928691810021765568.png)

发现读取了文件我直接模拟这个文件。

    
    
    import angr
    import claripy
    
    def is_good(state):
        return b"Good Job" in state.posix.dumps(1)
    
    def is_bad(state):
        return b"Try again" in state.posix.dumps(1)
    
    p = angr.Project('07_angr_symbolic_file')
    start_addr = 0x080488e7
    init_state = p.factory.blank_state(addr=start_addr)#生产project
    
    v = claripy.BVS('v', 0x40*8)#设置文件大小
    filename = 'OJKSQYDP.txt'#设置文件名称
    simfile = angr.storage.SimFile(name=filename, content=v, size=0x40)#生成simfile
    init_state.fs.insert(filename, simfile)
    
    simgr = p.factory.simgr(init_state)
    simgr.explore(find=is_good, avoid=is_bad)
    
    if simgr.found:
        solution_state = simgr.found[0]
        s = solution_state.solver.eval(v, cast_to=bytes)
        print(s)
    
    
    
    v = claripy.BVS('v', 0x40*8)#设置文件大小
    filename = 'OJKSQYDP.txt'#设置文件名称
    simfile = angr.storage.SimFile(name=filename, content=v, size=0x40)#生成simfile
    init_state.fs.insert(filename, simfile)
    

此步设置了我们的txt文档，将其设计为符号向量。

我们需要输入包括文件大小文件名称等条件。

![](./img/7260137103781302478.png)

## 构建表达式防止路径爆炸

在程序中使用for进行比较字符串时很容易产生路径爆炸，这时候我们需要进行人为的构建表达式来进行防止

### 08_angr_constraints

![](./img/5055857169380632006.png)

    
    
    import angr
    import claripy
    import sys
    
    project = angr.Project("07_angr_symbolic_file")
    
    start_address = 0x8048625
    initial_state = project.factory.blank_state(addr=start_address)
    
    password = claripy.BVS('password', 128)#设定密码
    
    password_address = 0x804a050  #求解的入口
    initial_state.memory.store(password_address, password)
    
    sm = project.factory.simgr(initial_state)
    
    address_to_check_constraint = 0x08048565    #比较函数的地址
    sm.explore(find=address_to_check_constraint)
    
    if sm.found:
        solution_state = sm.found[0]
    
        constrained_parameter_address = 0x804a050     
        constrained_parameter_size_bytes = 0x10
        constrained_parameter_bitvector = solution_state.memory.load(constrained_parameter_address,constrained_parameter_size_bytes)
    
        constrained_parameter_desired_value = 'AUPDNNPROEZRJWKB' #比较的字符串
        constraint_expression = constrained_parameter_bitvector == constrained_parameter_desired_value
    
        solution_state.add_constraints(constrained_parameter_bitvector == constrained_parameter_desired_value)
    
        solution = solution_state.solver.eval(password,cast_to=bytes)
    
        print('solution is: ',solution.decode('utf-8'))
    
    
    
    onstrained_parameter_address = 0x804a050     
        constrained_parameter_size_bytes = 0x10
        constrained_parameter_bitvector = solution_state.memory.load(constrained_parameter_address,constrained_parameter_size_bytes)
    

此部分比较复杂，简单来说就是构建了 constrained_parameter_bitvector ==
constrained_parameter_desired_value相等的表达式，将其作为约束的条件传入约束器中，可以成功的防止路径爆炸。

成功

![](./img/4259290175312293608.png)

## 使用hook防止路径爆炸

我们可以使用hook来防止路径爆炸。

Hook可以译为挂钩或者钩子，是逆向工程中改变程序运行流程的技术，可以让自己的代码运行在其他程序当中。通常说Hook函数，则是接收被Hook函数的参数，然后使用这些参数执行自己的代码，并将返回值返回（也可以没有返回值），至于被Hook的函数，可以选择让它继续执行，或者不执行。

### 09_angr_hooks

ida载入。

![](./img/8821783124916579035.png)

![](./img/5777263910891477689.png)

这个比较函数会导致路径爆炸，我们使用hook来跳过这个函数，从而执行我们自己设置的函数。

    
    
    import angr
    import claripy
    import time
    
    
    def good(state):
        tag = b'Good' in state.posix.dumps(1)
        return True if tag else False
    
    
    def bad(state):
        tag = b'Try' in state.posix.dumps(1)
        return True if tag else False
    
    
    time_start = time.perf_counter()
    
    path_to_binary = './dist/08_angr_constraints'
    p = angr.Project(path_to_binary, auto_load_libs=False)
    start_addr = 0x08048625
    init_state = p.factory.blank_state(addr=start_addr)
    
    buffer = claripy.BVS('buffer', 16*8)
    buffer_addr = 0x0804a050
    init_state.memory.store(buffer_addr, buffer)
    
    simgr = p.factory.simgr(init_state)
    
    check_addr = 0x08048565
    simgr.explore(find=check_addr)
    
    if simgr.found:
        solution_state = simgr.found[0]
        buffer_current = solution_state.memory.load(buffer_addr, 16)
        key = 'AUPDNNPROEZRJWKB'
    
        solution_state.solver.add(buffer_current == key)
    #我们自己的比较。
        solution = solution_state.solver.eval(buffer, cast_to=bytes)
        print('[+]Success:', solution.decode())
    
    
    else:
        raise Exception("Could not find solution")
    
    print('program last: ', time.perf_counter() - time_start)
    

可以执行，发现跑出答案

