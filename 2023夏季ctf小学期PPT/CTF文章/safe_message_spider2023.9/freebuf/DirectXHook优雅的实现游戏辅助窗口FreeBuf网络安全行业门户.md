**作者：The_Itach1@知道创宇404实验室  
日期：2022年12月27日**

前言：最近看到了一个github的项目，分析过后觉得里面无论是代码还是界面都很好看，然后开始研究其代码。

这篇文章主要分析其如何实现的辅助窗口的实现，其用到的东西有minihook+DirectX11(9) Hook+imgui。

## Minihook

项目地址：[TsudaKageyu/minhook: The Minimalistic x86/x64 API Hooking Library for
Windows (github.com)](https://github.com/TsudaKageyu/minhook)

先来了解下Minihook，Minihook是适用于 Windows 的简约 x86/x64 API 挂钩库。

一般来说，我们Hook windwos API的步骤是

  * 编写DLL，确定Hook 的API函数。

  * 编写自己的函数。

  * 根据PE结构的知识点，遍历IAT函数表，根据函数名找到函数地址，进行修改，修改为我们的函数地址。

常见Hook IAT代码如下。

    
    
    // hook_iat
    BOOL hook_iat(LPCSTR szDllName, PROC pfnOrg, PROC pfnNew)
    {
    	HMODULE hMod;
    	LPCSTR szLibName;
    	PIMAGE_IMPORT_DESCRIPTOR pImportDesc; 
    	PIMAGE_THUNK_DATA pThunk;
    	DWORD dwOldProtect, dwRVA;
    	PBYTE pAddr;
    
        // hMod, pAddr = ImageBase of calc.exe
        //             = VA to MZ signature (IMAGE_DOS_HEADER)
    	hMod = GetModuleHandle(NULL);
    	pAddr = (PBYTE)hMod;
    
        // pAddr = VA to PE signature (IMAGE_NT_HEADERS)
    	pAddr += *((DWORD*)&pAddr[0x3C]);
    
        // dwRVA = RVA to IMAGE_IMPORT_DESCRIPTOR Table
    	dwRVA = *((DWORD*)&pAddr[0x80]);
    
        // pImportDesc = VA to IMAGE_IMPORT_DESCRIPTOR Table
    	pImportDesc = (PIMAGE_IMPORT_DESCRIPTOR)((DWORD)hMod+dwRVA);
    
    	for( ; pImportDesc->Name; pImportDesc++ )
    	{
            // szLibName = VA to IMAGE_IMPORT_DESCRIPTOR.Name
    		szLibName = (LPCSTR)((DWORD)hMod + pImportDesc->Name);
    		if( !_stricmp(szLibName, szDllName) )
    		{
                // pThunk = IMAGE_IMPORT_DESCRIPTOR.FirstThunk
                //        = VA to IAT(Import Address Table)
    			pThunk = (PIMAGE_THUNK_DATA)((DWORD)hMod + 
                                             pImportDesc->FirstThunk);
    
                // pThunk->u1.Function = VA to API
    			for( ; pThunk->u1.Function; pThunk++ )
    			{
    				if( pThunk->u1.Function == (DWORD)pfnOrg )
    				{
    					VirtualProtect((LPVOID)&pThunk->u1.Function, 
                                       4, 
                                       PAGE_EXECUTE_READWRITE, 
                                       &dwOldProtect);
    
                        pThunk->u1.Function = (DWORD)pfnNew;
    
                        VirtualProtect((LPVOID)&pThunk->u1.Function, 
                                       4, 
                                       dwOldProtect, 
                                       &dwOldProtect);						
    
    					return TRUE;
    				}
    			}
    		}
    	}
    
    	return FALSE;
    }
    

可以看到过程还是比较繁琐，Minihook就很好的帮我们简化这个过程。

写一个hook弹窗的样例吧，将minihook对应的lib导入到项目后，就可以直接使用了，很方便。

    
    
    #include <Windows.h>
    #include <iostream>
    #include "minhook/minhook.h"
    #pragma comment (lib, "minhook/minhook.lib")
    
    //typedef int (WINAPI* fMessageBoxA)(HWND, LPCSTR, LPCSTR, UINT);
    using fMessageBoxA = int(WINAPI*)(HWND , LPCSTR , LPCSTR , UINT );
    fMessageBoxA pMessageBoxA = NULL;
    
    PVOID pMessageBoxAAddress;
    
    int WINAPI MessageBoxAHooked(HWND hWnd, LPCSTR lpText, LPCSTR lpCaption, UINT uType)
    {
    	LPCSTR lpMyText = "Hacked by The_Itach1";
    	return pMessageBoxA(hWnd, lpMyText, lpCaption, uType);
    }
    
    void SetupMessageBoxAHook()
    {
    	pMessageBoxAAddress = (LPVOID)MessageBoxA;
    
    	if (MH_CreateHook(pMessageBoxAAddress, &MessageBoxAHooked, (PVOID*)&pMessageBoxA) != MH_OK)
    		return;
    
    	if (MH_EnableHook(pMessageBoxAAddress) != MH_OK)
    		return;
    
    	std::cout << "MessageBoxA Hook start!\n";
    }
    
    
    void initHook()
    {
    	if (MH_Initialize() != MH_OK)
    	{
    		MessageBoxA(NULL, "Error initialize minhook", "alternative hack", MB_OK | MB_ICONERROR);
    	}
    }
    
    void UnHook()
    {
    	MH_DisableHook((PVOID)MessageBoxA);
    	MH_RemoveHook((PVOID)MessageBoxA);
    	MH_Uninitialize();
    
    }
    
    int main()
    {
    	//minhook的初始化
    	initHook();
    
    	//MessageBoxAHook
    	SetupMessageBoxAHook();
    	//测试是否hook成功
    	MessageBoxA(NULL, "box1", "box1", MB_OK);
    
    	//卸载hook
    	UnHook();
    	MessageBoxA(NULL, "box2", "box2", MB_OK);
    
    	system("pause");
    }
    

效果如下，可以看出当hook时，弹窗的内容被修改了，不hook时，就是正常的弹窗了。

![image](https://image.3001.net/images/20221227/1672123550_63aa949e1bc717dbe7f24.png!small)

而且minihook相比于IAT hook，或者Detours，感觉操作上更加的简便。

## DirectX11

### DirectX 简介

DirectX 是 Windows 中的一组组件，允许软件（主要且尤其是游戏）直接与视频和音频硬件结合使用。 使用 DirectX
的游戏可以更有效地使用内置于硬件的多媒体加速器功能，从而改善你的整体多媒体体验。

### 为什么要挂钩DirectX

在为游戏创建作弊时，渲染额外的内容或修改模型在游戏中的渲染方式迟早可能需要。有多种技术可以实现这一点，但最常见的技术之一是挂钩 DirectX API 的
3D 图形组件。

比如说D3D
HOOK实现骨骼透视，实际上就是hookD3D绘制3D模型都需要调用的DrawIndexedPrimitive()函数，然后判断模型，修改其Z轴深度缓存，从而实现模型透视，还有就是这篇文章要讲到的，通过Hook
DirectX11中呈现渲染图像的函数，来达到在游戏窗口上多添加一个imgui的辅助窗口。

### Direct3D11初始化

[Direct3D11学习：（三）Direct3D11初始化 - 郭小雷 - 博客园
(cnblogs.com)](https://www.cnblogs.com/Ray1024/p/6084609.html)  
可以先看上面这篇文章，初步了解下Direct3D11初始化的过程，我们需要注意的是其中的创建一个渲染目标视图。

    
    
    ID3D11RenderTargetView* mRenderTargetView;
    ID3D11Texture2D* backBuffer;
    // 获取一个交换链的后台缓冲区指针
    mSwapChain->GetBuffer(0,__uuidof(ID3D11Texture2D), reinterpret_cast<void**>(&backBuffer));
    // 创建渲染目标视图
    md3dDevice->CreateRenderTargetView(backBuffer, 0, &mRenderTargetView);
    // 每调用一次GetBuffer方法，后台缓冲区的COM引用计数就会递增一次。我们需要在使用完之后释放它
    ReleaseCOM(backBuffer);
    

而什么是渲染呢  
在Direct3D中，一个设备对象至少包含两个显示缓存区：当前缓存区（Front Buffer）和后备缓存区（Back
Buffer），前者可以看成Direct3D窗口的映射。当我们渲染图形时，实际上并不是直接在窗口上输出，而是在后备缓存区上绘图。渲染完毕后，交换两个缓存区，使原来的后备缓存区变成当前缓存区，从而实现窗口刷新。快速重复此过程，就会在屏幕上形成连续的动画。

所以想要在游戏窗口，再加一个imgui的窗口，我们就需要在其执行绘制函数前，多创建一个渲染目标视图到其后备缓存区，这样后面绘制的时候，就也会绘制我们新添的imgui窗口。

### Imgui

[Dear Imgui](https://github.com/ocornut/imgui)是一个 **用于 C++ 的无膨胀图形用户界面库**
。它输出优化的顶点缓冲区，您可以在启用 3D 管道的应用程序中随时渲染这些缓冲区。它快速、可移植、与渲染器无关且自包含（无外部依赖项）。

Imgui的example很多，其中就有[example_win32_directx11](https://github.com/ocornut/imgui/tree/master/examples/example_win32_directx11)的例子，只不过是开发的角度，不像游戏是已经开发出来的exe，所以对于游戏，是需要对关键函数进行hook的。

下面来分析这个example_win32_directx11。

    
    
    // Dear ImGui: standalone example application for DirectX 11
    // If you are new to Dear ImGui, read documentation from the docs/ folder + read the top of imgui.cpp.
    // Read online: https://github.com/ocornut/imgui/tree/master/docs
    
    #include "imgui.h"
    #include "imgui_impl_win32.h"
    #include "imgui_impl_dx11.h"
    #include <d3d11.h>
    #include <tchar.h>
    
    // Data
    static ID3D11Device*            g_pd3dDevice = NULL;
    static ID3D11DeviceContext*     g_pd3dDeviceContext = NULL;
    static IDXGISwapChain*          g_pSwapChain = NULL;
    static ID3D11RenderTargetView*  g_mainRenderTargetView = NULL;
    
    // Forward declarations of helper functions
    bool CreateDeviceD3D(HWND hWnd);
    void CleanupDeviceD3D();
    void CreateRenderTarget();
    void CleanupRenderTarget();
    LRESULT WINAPI WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);
    
    // Main code
    int main(int, char**)
    {
        // Create application window
        //ImGui_ImplWin32_EnableDpiAwareness();
        WNDCLASSEXW wc = { sizeof(wc), CS_CLASSDC, WndProc, 0L, 0L, GetModuleHandle(NULL), NULL, NULL, NULL, NULL, L"ImGui Example", NULL };
        ::RegisterClassExW(&wc);
        HWND hwnd = ::CreateWindowW(wc.lpszClassName, L"Dear ImGui DirectX11 Example", WS_OVERLAPPEDWINDOW, 100, 100, 1280, 800, NULL, NULL, wc.hInstance, NULL);
    
        // Initialize Direct3D
        if (!CreateDeviceD3D(hwnd))
        {
            CleanupDeviceD3D();
            ::UnregisterClassW(wc.lpszClassName, wc.hInstance);
            return 1;
        }
    
        // Show the window
        ::ShowWindow(hwnd, SW_SHOWDEFAULT);
        ::UpdateWindow(hwnd);
    
        // Setup Dear ImGui context
        IMGUI_CHECKVERSION();
        ImGui::CreateContext();
        ImGuiIO& io = ImGui::GetIO(); (void)io;
        //io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;     // Enable Keyboard Controls
        //io.ConfigFlags |= ImGuiConfigFlags_NavEnableGamepad;      // Enable Gamepad Controls
    
        // Setup Dear ImGui style
        ImGui::StyleColorsDark();
        //ImGui::StyleColorsLight();
    
        // Setup Platform/Renderer backends
        ImGui_ImplWin32_Init(hwnd);
        ImGui_ImplDX11_Init(g_pd3dDevice, g_pd3dDeviceContext);
    
    
        // Our state
        bool show_demo_window = true;
        bool show_another_window = false;
        ImVec4 clear_color = ImVec4(0.45f, 0.55f, 0.60f, 1.00f);
    
        // Main loop
        bool done = false;
        while (!done)
        {
            // Poll and handle messages (inputs, window resize, etc.)
            // See the WndProc() function below for our to dispatch events to the Win32 backend.
            MSG msg;
            while (::PeekMessage(&msg, NULL, 0U, 0U, PM_REMOVE))
            {
                ::TranslateMessage(&msg);
                ::DispatchMessage(&msg);
                if (msg.message == WM_QUIT)
                    done = true;
            }
            if (done)
                break;
    
            // Start the Dear ImGui frame
            ImGui_ImplDX11_NewFrame();
            ImGui_ImplWin32_NewFrame();
            ImGui::NewFrame();
    
            // 1. Show the big demo window (Most of the sample code is in ImGui::ShowDemoWindow()! You can browse its code to learn more about Dear ImGui!).
            if (show_demo_window)
                ImGui::ShowDemoWindow(&show_demo_window);
    
            // Rendering
            ImGui::Render();
            const float clear_color_with_alpha[4] = { clear_color.x * clear_color.w, clear_color.y * clear_color.w, clear_color.z * clear_color.w, clear_color.w };
            g_pd3dDeviceContext->OMSetRenderTargets(1, &g_mainRenderTargetView, NULL);
            g_pd3dDeviceContext->ClearRenderTargetView(g_mainRenderTargetView, clear_color_with_alpha);
            ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());
    
            g_pSwapChain->Present(1, 0); // Present with vsync
            //g_pSwapChain->Present(0, 0); // Present without vsync
        }
    
        // Cleanup
        ImGui_ImplDX11_Shutdown();
        ImGui_ImplWin32_Shutdown();
        ImGui::DestroyContext();
    
        CleanupDeviceD3D();
        ::DestroyWindow(hwnd);
        ::UnregisterClassW(wc.lpszClassName, wc.hInstance);
    
        return 0;
    }
    
    // Helper functions
    
    bool CreateDeviceD3D(HWND hWnd)
    {
        // Setup swap chain
        DXGI_SWAP_CHAIN_DESC sd;
        ZeroMemory(&sd, sizeof(sd));
        sd.BufferCount = 2;
        sd.BufferDesc.Width = 0;
        sd.BufferDesc.Height = 0;
        sd.BufferDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
        sd.BufferDesc.RefreshRate.Numerator = 60;
        sd.BufferDesc.RefreshRate.Denominator = 1;
        sd.Flags = DXGI_SWAP_CHAIN_FLAG_ALLOW_MODE_SWITCH;
        sd.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
        sd.OutputWindow = hWnd;
        sd.SampleDesc.Count = 1;
        sd.SampleDesc.Quality = 0;
        sd.Windowed = TRUE;
        sd.SwapEffect = DXGI_SWAP_EFFECT_DISCARD;
    
        UINT createDeviceFlags = 0;
        //createDeviceFlags |= D3D11_CREATE_DEVICE_DEBUG;
        D3D_FEATURE_LEVEL featureLevel;
        const D3D_FEATURE_LEVEL featureLevelArray[2] = { D3D_FEATURE_LEVEL_11_0, D3D_FEATURE_LEVEL_10_0, };
        if (D3D11CreateDeviceAndSwapChain(NULL, D3D_DRIVER_TYPE_HARDWARE, NULL, createDeviceFlags, featureLevelArray, 2, D3D11_SDK_VERSION, &sd, &g_pSwapChain, &g_pd3dDevice, &featureLevel, &g_pd3dDeviceContext) != S_OK)
            return false;
    
        CreateRenderTarget();
        return true;
    }
    
    void CleanupDeviceD3D()
    {
        CleanupRenderTarget();
        if (g_pSwapChain) { g_pSwapChain->Release(); g_pSwapChain = NULL; }
        if (g_pd3dDeviceContext) { g_pd3dDeviceContext->Release(); g_pd3dDeviceContext = NULL; }
        if (g_pd3dDevice) { g_pd3dDevice->Release(); g_pd3dDevice = NULL; }
    }
    
    void CreateRenderTarget()
    {
        ID3D11Texture2D* pBackBuffer;
        g_pSwapChain->GetBuffer(0, IID_PPV_ARGS(&pBackBuffer));
        g_pd3dDevice->CreateRenderTargetView(pBackBuffer, NULL, &g_mainRenderTargetView);
        pBackBuffer->Release();
    }
    
    void CleanupRenderTarget()
    {
        if (g_mainRenderTargetView) { g_mainRenderTargetView->Release(); g_mainRenderTargetView = NULL; }
    }
    
    // Forward declare message handler from imgui_impl_win32.cpp
    extern IMGUI_IMPL_API LRESULT ImGui_ImplWin32_WndProcHandler(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);
    
    // Win32 message handler
    // You can read the io.WantCaptureMouse, io.WantCaptureKeyboard flags to tell if dear imgui wants to use your inputs.
    // - When io.WantCaptureMouse is true, do not dispatch mouse input data to your main application, or clear/overwrite your copy of the mouse data.
    // - When io.WantCaptureKeyboard is true, do not dispatch keyboard input data to your main application, or clear/overwrite your copy of the keyboard data.
    // Generally you may always pass all inputs to dear imgui, and hide them from your application based on those two flags.
    LRESULT WINAPI WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam)
    {
        if (ImGui_ImplWin32_WndProcHandler(hWnd, msg, wParam, lParam))
            return true;
    
        switch (msg)
        {
        case WM_SIZE:
            if (g_pd3dDevice != NULL && wParam != SIZE_MINIMIZED)
            {
                CleanupRenderTarget();
                g_pSwapChain->ResizeBuffers(0, (UINT)LOWORD(lParam), (UINT)HIWORD(lParam), DXGI_FORMAT_UNKNOWN, 0);
                CreateRenderTarget();
            }
            return 0;
        case WM_SYSCOMMAND:
            if ((wParam & 0xfff0) == SC_KEYMENU) // Disable ALT application menu
                return 0;
            break;
        case WM_DESTROY:
            ::PostQuitMessage(0);
            return 0;
        }
        return ::DefWindowProc(hWnd, msg, wParam, lParam);
    }
    
    

简单整理了下过程

    
    
    |--main()
    |		|--CreateWindowW() 创建一个windows窗口用于测试imgui
    |		|--CreateDeviceD3D()
    |		|			|--D3D11CreateDeviceAndSwapChain() 创建设备、设备上下文和交换链
    |		|			|--CreateRenderTarget() 创建渲染目标视图
    |		|--ImGui_Init ImGui初始化
    |		|--while(loop)
    |		|	|--PeekMessage，检测是否收到quit的消息
    |		|	|--ImGui 场景的设置
    |		|	|--g_pd3dDeviceContext->OMSetRenderTargets 将视图绑定到输出合并器阶段
    |		|	|--g_pd3dDeviceContext->ClearRenderTargetView 貌似和绘制背景有关
    |		|	|--g_pSwapChain->Present(1, 0);开始绘制
    |		|	|--后面就是一些结束清理过程了
    
    
    |--WndProc()
    |		|--ImGui_ImplWin32_WndProcHandler(hWnd, msg, wParam, lParam) 如果是Imgui的窗口，就交给Imgui的消息处理函数进行处理
    |		|--switch(msg)
    |		|		|--case WM_SIZE: 当窗口大小改变时产生这个消息
    |		|		|	|--CleanupRenderTarget();g_pSwapChain->ResizeBuffers;CreateRenderTarget();先清理渲染目标视图，然后在创建一个。
    |		|		|--case WM_DESTROY: 接收到WM_DESTROY时
    |		|		|	|--PostQuitMessage(0) 发送消息，结束main函数中的while循环。
    

### Hook的函数

imgui的example相当于就是实现了一个使用imgui窗口的D3D11的初始化过程，但是对于游戏，我们不是开发者，不能直接修改代码，所以就只有去hook其中的关键函数，在执行关键函数前，或者关键函数后，执行我们的代码。

所以我们需要明确对于DirectX11，需要hook哪些函数，通过Imgui提供的样例，我们可以知道在DirectX11需要Hook的有三个函数。

  * [IDXGISwapChain::Present](https://learn.microsoft.com/en-us/windows/win32/api/dxgi/nf-dxgi-idxgiswapchain-present)，绘制函数，我们需要在绘制函数前，自己创建一个渲染目标视图，然后是Imgui的初始化和窗口设置。

  * IDXGISwapChain::ResizeBuffers，窗口大小变换时会调用的函数，为了我们的imgui窗口也能够随窗口size变换而正常执行，我们需要hook这个函数，对原渲染目标视图进行release，然后重新创建。

  * WndProc，游戏窗口的消息处理函数，对于imgui窗口的消息，我们需要调用ImGui_ImplWin32_WndProcHandler()来进行处理。

和DirectX9有些不同的是，DirectX11的绘制函数和RESIZE函数是不一样的。

| DirectX9| DirectX11  
---|---|---  
向用户呈现渲染图像| [IDirect3DDevice9::EndScene](https://learn.microsoft.com/en-us/windows/win32/api/d3d9helper/nf-d3d9helper-idirect3ddevice9-endscene)|
[IDXGISwapChain::Present](https://learn.microsoft.com/en-us/windows/win32/api/dxgi/nf-dxgi-idxgiswapchain-present)  
改变窗口size调用的函数| [IDirect3DDevice9::Reset](https://learn.microsoft.com/en-us/windows/win32/api/d3d9helper/nf-d3d9helper-idirect3ddevice9-reset)|
[IDXGISwapChain::ResizeBuffers](https://learn.microsoft.com/en-us/windows/win32/api/dxgi/nf-dxgi-idxgiswapchain-resizebuffers)  
  
### 实战某游戏

主要还是将github上那个项目中DirectX11的部分分离了出来，然后我简化了其imgui的窗口。

dllmain.cpp，主要就是先创建一个用于输入调试信息的控制台，然后遍历了窗口，准确获取到bf1的窗口句柄，minihook的初始化。

    
    
    // dllmain.cpp : 定义 DLL 应用程序的入口点。
    #include "includes.h"
    
    namespace console
    {
    	FILE* output_stream = nullptr;
    
    	void attach(const char* name)
    	{
    		if (AllocConsole())
    		{
    			freopen_s(&output_stream, "conout$", "w", stdout);
    		}
    		SetConsoleTitle(name);
    	}
    
    	void detach()
    	{
    		if (output_stream)
    		{
    			fclose(output_stream);
    		}
    		FreeConsole();
    	}
    }
    
    
    #define RAISE_ERROR(check_var, error_message, success_message) \
    if (!check_var) \
    { \
    	MessageBoxA(NULL, error_message, "alternative hack", MB_OK | MB_ICONERROR); \
    	FreeLibraryAndExitThread(globals::hmModule, 1); \
    } \
    else \
    { \
    	std::cout << success_message << "0x" << std::hex << check_var << std::endl; \
    } \
    
    BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam)
    {
    	auto process_id_that_interests_us_very_much = GetCurrentProcessId();
    
    	HWND* cur_hwnd = (HWND*)lParam;
    
    	if ((!GetWindow(hwnd, GW_OWNER)) && IsWindow(hwnd))
    	{
    		DWORD process_id = NULL;
    		GetWindowThreadProcessId(hwnd, &process_id);
    
    		char* text_window = new char[255];
    
    		GetWindowText(hwnd, text_window, 255);
    
    		if (process_id_that_interests_us_very_much == process_id && strstr(text_window, "Battlefield") && !strstr(text_window, ".exe"))
    		{
    			std::cout << "Window: " << text_window << std::endl;
    			*cur_hwnd = hwnd;
    			return 0;
    		}
    	}
    
    	return 1;
    }
    
    void SetupHackThread(void)
    {
    	//开启一个控制台用来输出一些信息。
    	console::attach("bf1 console debug");
    
    	//获取Battlefield窗口的句柄
    	EnumWindows(&EnumWindowsProc, (LPARAM)&globals::hGame);
    
    	RAISE_ERROR(globals::hGame, "Error find window", "window handle: ");
    
    	//minhook的初始化
    	if (MH_Initialize() != MH_OK)
    	{
    		MessageBoxA(NULL, "Error initialize minhook", "alternative hack", MB_OK | MB_ICONERROR);
    	}
    	//DirectX11 Hook
    	m_pHook->SetupDX11Hook();
    
    	RAISE_ERROR(m_pHook->pPresentAddress, "Error hook DX11", "present: ");
    	RAISE_ERROR(m_pHook->pResizeBuffersAddress, "Error hook DX11", "resizebuffers: ");
    
    	//调用SetWindowLongPtr函数修改了游戏窗口的WndProc，也就是窗口的消息处理函数，具体的消息处理函数将在对应函数位置进行分析。
    	m_pHook->SetupWndProcHook();
    	RAISE_ERROR(m_pHook->pWndProc, "Error hook wndproc", "wndproc: ")
    
    	while (true)
    	{
    		Sleep(228);
    	}
    
    }
    
    BOOL APIENTRY DllMain( HMODULE hModule,
                           DWORD  ul_reason_for_call,
                           LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
            CreateThread(NULL, NULL, (LPTHREAD_START_ROUTINE)SetupHackThread, NULL, NULL, NULL);
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }
    
    
    

hook.h，hook类的定义，以及声明了几个变量，交换链、设备、设备上下文、渲染目标子资源。

    
    
    #pragma once
    class CHook
    {
    public:
    	PVOID pPresentAddress;
    	PVOID pResizeBuffersAddress;
    	WNDPROC pWndProc;
    	void SetupDX11Hook();
    	void SetupWndProcHook();
    };
    //智能指针类,相当于创建了一个指向CHook类的空指针。
    extern std::unique_ptr<CHook>m_pHook;
    extern IDXGISwapChain* swapchain;
    extern ID3D11Device* device;
    extern ID3D11DeviceContext* context;
    extern ID3D11RenderTargetView* render_view;
    

hook.cpp，主要就是之前提到三个函数的hook，然后代码流程和example_win32_directx11差不多。

    
    
    #include "../includes.h"
    
    std::unique_ptr<CHook>m_pHook = std::make_unique<CHook>();
    
    IDXGISwapChain* swapchain = nullptr;
    ID3D11Device* device = nullptr;
    ID3D11DeviceContext* context = nullptr;
    ID3D11RenderTargetView* render_view = nullptr;
    
    using fPresent = HRESULT(__fastcall*)(IDXGISwapChain*, UINT, UINT);
    fPresent pPresent = NULL;
    
    using fResizeBuffers = HRESULT(__fastcall*)(IDXGISwapChain*, UINT, UINT, UINT, DXGI_FORMAT, UINT);
    fResizeBuffers pResizeBuffers = NULL;
    
    static bool renderview_lost = true;
    
    
    
    namespace vars
    {
    	static bool bMenuOpen=true;
    }
    
    
    enum IDXGISwapChainvTable //for dx10 / dx11
    {
    	QUERY_INTERFACE,
    	ADD_REF,
    	RELEASE,
    	SET_PRIVATE_DATA,
    	SET_PRIVATE_DATA_INTERFACE,
    	GET_PRIVATE_DATA,
    	GET_PARENT,
    	GET_DEVICE,
    	PRESENT,
    	GET_BUFFER,
    	SET_FULLSCREEN_STATE,
    	GET_FULLSCREEN_STATE,
    	GET_DESC,
    	RESIZE_BUFFERS,
    	RESIZE_TARGET,
    	GET_CONTAINING_OUTPUT,
    	GET_FRAME_STATISTICS,
    	GET_LAST_PRESENT_COUNT
    };
    
    
    void InitImGui()
    {
    	IMGUI_CHECKVERSION();
    	ImGui::CreateContext();
    	ImGuiIO& io = ImGui::GetIO(); (void)io;
    	ImGui_ImplWin32_Init(globals::hGame);
    	ImGui_ImplDX11_Init(device, context);
    }
    
    
    void BeginScene()
    {
    	ImGui_ImplDX11_NewFrame();
    	ImGui_ImplWin32_NewFrame();
    	ImGui::NewFrame();
    	bool show_demo_window = true;
    	ImGui::ShowDemoWindow(&show_demo_window);
    	ImGui::Begin("Another Window", &show_demo_window);   // Pass a pointer to our bool variable (the window will have a closing button that will clear the bool when clicked)
    	ImGui::Text("Hello from another window!");
    	static int counter = 0;
    	if (ImGui::Button("Button"))                            // Buttons return true when clicked (most widgets return true when edited/activated)
    		counter++;
    	ImGui::Text("counter = %d", counter);
    	ImGui::End();
    	ImGui::Render();
    	ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());
    }
    
    HRESULT __fastcall Present_Hooked(IDXGISwapChain* pChain, UINT SyncInterval, UINT Flags)
    {
    	//第一次调用时，创建渲染目标视图
    	if (renderview_lost)
    	{
    		if (SUCCEEDED(pChain->GetDevice(__uuidof(ID3D11Device), (void**)&device)))
    		{
    			device->GetImmediateContext(&context);
    
    			ID3D11Texture2D* pBackBuffer;
    			pChain->GetBuffer(0, __uuidof(ID3D11Texture2D), (LPVOID*)&pBackBuffer);
    			device->CreateRenderTargetView(pBackBuffer, NULL, &render_view);
    			pBackBuffer->Release();
    
    			std::cout << __FUNCTION__ << " > renderview successfully received!" << std::endl;
    			renderview_lost = false;
    		}
    	}
    	//ImGui的初始化代码，套路代码
    	static auto once = [pChain, SyncInterval, Flags]()
    	{
    		InitImGui();
    		std::cout << __FUNCTION__ << " > first called!" << std::endl;
    		return true;
    	}();
    
    	//将视图绑定到输出合并器阶段
    	context->OMSetRenderTargets(1, &render_view, NULL);
    
    	//imgui窗口的绘制
    	BeginScene();
    
    	return pPresent(pChain, SyncInterval, Flags);
    }
    
    
    HRESULT __fastcall ResizeBuffers_hooked(IDXGISwapChain* pChain, UINT BufferCount, UINT Width, UINT Height, DXGI_FORMAT NewFormat, UINT Flags)
    {
    	static auto once = []()
    	{
    		std::cout << __FUNCTION__ << " > first called!" << std::endl;
    		return true;
    	}();
    
    	//释放掉渲染目标视图
    	render_view->Release();
    	render_view = nullptr;
    	//将标志改为true，这样下次Present_Hooked，又会创建一个渲染目标视图。
    	renderview_lost = true;
    
    	//这两个没看懂，imgui的example_win32_directx9有类似的代码，但是
    	ImGui_ImplDX11_CreateDeviceObjects();
    	ImGui_ImplDX11_InvalidateDeviceObjects();
    
    	return pResizeBuffers(pChain, BufferCount, Width, Height, NewFormat, Flags);
    }
    
    void CHook::SetupDX11Hook()
    {
    	//创建设备、设备上下文和交换链，只需要一个东西，就是目标窗口的hWnd
    	D3D_FEATURE_LEVEL feature_level = D3D_FEATURE_LEVEL_11_0;
    	DXGI_SWAP_CHAIN_DESC scd{};
    	ZeroMemory(&scd, sizeof(scd));
    	scd.BufferCount = 1;
    	scd.BufferDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
    	scd.BufferDesc.Scaling = DXGI_MODE_SCALING_UNSPECIFIED;
    	scd.BufferDesc.ScanlineOrdering = DXGI_MODE_SCANLINE_ORDER_UNSPECIFIED;
    	scd.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
    	scd.Flags = DXGI_SWAP_CHAIN_FLAG_ALLOW_MODE_SWITCH;
    	scd.OutputWindow = globals::hGame;
    	scd.SampleDesc.Count = 1;
    	scd.SwapEffect = DXGI_SWAP_EFFECT_DISCARD;
    	scd.Windowed = TRUE;
    	scd.BufferDesc.RefreshRate.Numerator = 60;
    	scd.BufferDesc.RefreshRate.Denominator = 1;
    
    	//https://learn.microsoft.com/en-us/windows/win32/api/d3d11/nf-d3d11-d3d11createdeviceandswapchain
    	if (FAILED(D3D11CreateDeviceAndSwapChain(NULL, D3D_DRIVER_TYPE_HARDWARE, NULL, NULL, &feature_level, 1, D3D11_SDK_VERSION, &scd, &swapchain, &device, NULL, &context)))
    	{
    		std::cout << "failed to create device\n";
    		return;
    	}
    
    	//*取一级指针的值，获取到IDXGISwapChain接口，https://learn.microsoft.com/en-us/windows/win32/api/dxgi/nn-dxgi-idxgiswapchain
    	void** pVTableSwapChain = *reinterpret_cast<void***>(swapchain);
    
    	//获取需要hook的两个函数的地址，就是IDXGISwapChain接口提供的两个函数。
    
    	//向用户呈现渲染图像。IDXGISwapChain::Present
    	this->pPresentAddress = reinterpret_cast<LPVOID>(pVTableSwapChain[IDXGISwapChainvTable::PRESENT]);
    	//更改交换链的后台缓冲区大小、格式和缓冲区数量。这应该在应用程序窗口大小调整时调用。IDXGISwapChain::ResizeBuffers
    	this->pResizeBuffersAddress = reinterpret_cast<LPVOID>(pVTableSwapChain[IDXGISwapChainvTable::RESIZE_BUFFERS]);
    
    	//开始hook，主要过程就是在执行原Present函数前，创建渲染目标视图，然后imgui初始化，绘制
    	if (MH_CreateHook(this->pPresentAddress, &Present_Hooked, (LPVOID*)&pPresent) != MH_OK
    		|| MH_EnableHook(this->pPresentAddress) != MH_OK)
    	{
    		std::cout << "failed create hook present\n";
    		return;
    	}
    
    	//这个函数就是当目标窗口的size改变时会调用的。
    	if (MH_CreateHook(pResizeBuffersAddress, &ResizeBuffers_hooked, (LPVOID*)&pResizeBuffers) != MH_OK
    		|| MH_EnableHook(pResizeBuffersAddress) != MH_OK)
    	{
    		std::cout << "failed create hook resizebuffers\n";
    		return;
    	}
    }
    
    LRESULT ImGui_ImplWin32_WndProcHandler(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam);
    
    LRESULT CALLBACK WndProc_Hooked(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
    {
    	static auto once = []()
    	{
    		std::cout << __FUNCTION__ << " first called!" << std::endl;
    
    		return true;
    	}();
    
    	//如果按下INS键，就打开或关闭外挂设置界面，如果之前是关闭的就打开，如果是打开的就关闭。
    	if (uMsg == WM_KEYDOWN && wParam == VK_INSERT)
    	{
    		vars::bMenuOpen = !vars::bMenuOpen;
    		return FALSE;
    	}
    
    	//如果外挂设置界面是打开状态，则调用ImGui的消息处理
    	if (vars::bMenuOpen && ImGui_ImplWin32_WndProcHandler(hwnd, uMsg, wParam, lParam))
    	{
    		return TRUE;
    	}
    
    	//调用原窗口处理消息的函数来处理其他消息，https://blog.csdn.net/wangpengk7788/article/details/55053053
    	return CallWindowProc(m_pHook->pWndProc, hwnd, uMsg, wParam, lParam);
    }
    
    void CHook::SetupWndProcHook()
    {
    	this->pWndProc = (WNDPROC)SetWindowLongPtr(globals::hGame, GWLP_WNDPROC, (LONG_PTR)WndProc_Hooked);
    }
    

最后效果如下。

![image](https://image.3001.net/images/20221227/1672123662_63aa950ea811a8bbbd799.png!small)

## DirectX9

前面已经提到DirectX11和DirectX9,是有些细微差别的，实际上其过程还相对于DirectX11减少了许多步骤，这里我同样编写了下DirectX9
Hook的代码，并找了一款游戏进行测验。

其代码过程也可参考imgui中的[example_win32_directx9](https://github.com/ocornut/imgui/tree/master/examples/example_win32_directx9)，同样我们需要hook一些函数。

### 实战某游戏

dllmain.cpp

    
    
    // dllmain.cpp : 定义 DLL 应用程序的入口点。
    #include "includes.h"
    
    namespace console
    {
    	FILE* output_stream = nullptr;
    
    	void attach(const char* name)
    	{
    		if (AllocConsole())
    		{
    			freopen_s(&output_stream, "conout$", "w", stdout);
    		}
    		SetConsoleTitle(name);
    	}
    
    	void detach()
    	{
    		if (output_stream)
    		{
    			fclose(output_stream);
    		}
    		FreeConsole();
    	}
    }
    
    #define RAISE_ERROR(check_var, error_message, success_message) \
    if (!check_var) \
    { \
    	MessageBoxA(NULL, error_message, "csgo hack", MB_OK | MB_ICONERROR); \
    	FreeLibraryAndExitThread(globals::hmModule, 1); \
    } \
    else \
    { \
    	std::cout << success_message << "0x" << std::hex << check_var << std::endl; \
    } \
    
    BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam)
    {
    	auto process_id_that_interests_us_very_much = GetCurrentProcessId();
    
    	HWND* cur_hwnd = (HWND*)lParam;
    
    	if ((!GetWindow(hwnd, GW_OWNER)) && IsWindow(hwnd))
    	{
    		DWORD process_id = NULL;
    		GetWindowThreadProcessId(hwnd, &process_id);
    
    		char* text_window = new char[255];
    
    		GetWindowText(hwnd, text_window, 255);
    
    		if (process_id_that_interests_us_very_much == process_id && strstr(text_window, "Counter-Strike") && !strstr(text_window, ".exe"))
    		{
    			std::cout << "Window: " << text_window << std::endl;
    			*cur_hwnd = hwnd;
    			return 0;
    		}
    	}
    
    	return 1;
    }
    
    void SetupHackThread(void)
    {
    	//开启一个控制台用来输出一些信息。
    	console::attach("csgo console debug");
    
    	//获取窗口的句柄
    	EnumWindows(&EnumWindowsProc, (LPARAM)&globals::hGame);
    
    	RAISE_ERROR(globals::hGame, "Error find window", "window handle: ");
    
    
    	//minhook的初始化
    	if (MH_Initialize() != MH_OK)
    	{
    		MessageBoxA(NULL, "Error initialize minhook", "csgo hack", MB_OK | MB_ICONERROR);
    	}
    	//DirectX9 Hook
    	m_pHook->SetupDX9Hook();
    
    	RAISE_ERROR(m_pHook->pEndSceneAddress, "Error hook DX9", "EndScene");
    	RAISE_ERROR(m_pHook->pResetAddress, "Error hook DX9", "Reset: ");
    
    	//调用SetWindowLongPtr函数修改了游戏窗口的WndProc，也就是窗口的消息处理函数，具体的消息处理函数将在对应函数位置进行分析。
    	m_pHook->SetupWndProcHook();
    	RAISE_ERROR(m_pHook->pWndProc, "Error hook wndproc", "wndproc: ")
    
    		while (true)
    		{
    			if (globals::unload_dll) break;
    			Sleep(228);
    		}
    
    
    	Sleep(30);
    
    	ImGui_ImplDX9_Shutdown();
    	ImGui_ImplWin32_Shutdown();
    	ImGui::DestroyContext();
    	Sleep(100);
    
    	MH_DisableHook(m_pHook->pEndSceneAddress);
    	MH_RemoveHook(m_pHook->pEndSceneAddress);
    	Sleep(100);
    
    	MH_DisableHook(m_pHook->pResetAddress);
    	MH_RemoveHook(m_pHook->pResetAddress);
    
    	MH_Uninitialize();
    	Sleep(100);
    
    	SetWindowLongPtr(globals::hGame, GWLP_WNDPROC, (LONG_PTR)m_pHook->pWndProc);
    
    	Sleep(100);
    
    	//free library
    	std::cout << "free library...\n\n";
    	FreeLibraryAndExitThread(globals::hmModule, 0);
    }
    
    BOOL APIENTRY DllMain( HMODULE hModule,
                           DWORD  ul_reason_for_call,
                           LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
    		globals::hmModule = hModule;
            CreateThread(NULL, NULL, (LPTHREAD_START_ROUTINE)SetupHackThread, NULL, NULL, NULL);
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }
    

hook.h

    
    
    #pragma once
    class CHook
    {
    public:
    	PVOID pEndSceneAddress;
    	PVOID pResetAddress;
    	PVOID pSetCursorPosAddress;
    	WNDPROC pWndProc;
    	void SetupDX9Hook();
    	void SetupWndProcHook();
    };
    //智能指针类,相当于创建了一个指向CHook类的空指针。
    extern std::unique_ptr<CHook>m_pHook;
    
    extern IDirect3D9* g_pD3D;
    extern IDirect3DDevice9* device;
    

hook.cpp

    
    
    #include "../includes.h"
    
    std::unique_ptr<CHook>m_pHook = std::make_unique<CHook>();
    
    using fEndscene = HRESULT(__stdcall*)(IDirect3DDevice9*);
    fEndscene pEndscene = NULL;
    using fReset = long(__stdcall*)(IDirect3DDevice9*, D3DPRESENT_PARAMETERS*);
    fReset pReset = NULL;
    
    IDirect3D9* g_pD3D= nullptr;
    IDirect3DDevice9* device = nullptr;
    ID3D11DeviceContext* context = nullptr;
    
    enum IDirect3DDevice9vTable //for dx9
    {
        RESET = 16,
        ENDSCENE=42
    };
    
    
    namespace vars
    {
        static bool bMenuOpen = true;
    }
    void InitImGui(IDirect3DDevice9* pd3dDevice)
    {
        IMGUI_CHECKVERSION();
        ImGui::CreateContext();
        ImGuiIO& io = ImGui::GetIO(); (void)io;
        ImGui_ImplWin32_Init(globals::hGame);
        ImGui_ImplDX9_Init(pd3dDevice);
    }
    
    void BeginScene()
    {
        // 界面开始绘制
        ImGui_ImplDX9_NewFrame();
        ImGui_ImplWin32_NewFrame();
    
        ImGui::NewFrame();
        bool show_demo_window = true;
        ImGui::ShowDemoWindow(&show_demo_window);
        ImGui::Begin("Another Window", &show_demo_window);   // Pass a pointer to our bool variable (the window will have a closing button that will clear the bool when clicked)
        ImGui::Text("Hello from another window!");
        static int counter = 0;
        if (ImGui::Button("Button"))                            // Buttons return true when clicked (most widgets return true when edited/activated)
            counter++;
        ImGui::Text("counter = %d", counter);
        ImGui::End();
        ImGui::Render();
        ImGui_ImplDX9_RenderDrawData(ImGui::GetDrawData());
    
    }
    
    HRESULT __stdcall EndScene_Hooked(IDirect3DDevice9* pd3dDevice)
    {
        static auto once = [pd3dDevice]()
        {
            std::cout << __FUNCTION__ << " > first called!" << std::endl;
        	InitImGui(pd3dDevice);
            return true;
        }();
        
        BeginScene();
    
        return pEndscene(pd3dDevice);
    }
    
    HRESULT __stdcall Reset_Hooked(IDirect3DDevice9* pd3dDevice, D3DPRESENT_PARAMETERS* pPresentationParameters)
    {
        static auto once = []()
        {
            std::cout << __FUNCTION__ << " > first called!" << std::endl;
            return true;
        }();
    
        ImGui_ImplDX9_InvalidateDeviceObjects();
        //HRESULT ret= pReset(pd3dDevice, pPresentationParameters);
        ImGui_ImplDX9_CreateDeviceObjects();
    
        return pReset(pd3dDevice, pPresentationParameters);
    }
    
    
    void CHook::SetupDX9Hook()
    {
    
    	g_pD3D =Direct3DCreate9(D3D_SDK_VERSION);
    
        D3DPRESENT_PARAMETERS g_d3dpp = {};
        ZeroMemory(&g_d3dpp, sizeof(g_d3dpp));
        g_d3dpp.Windowed = TRUE;
        g_d3dpp.SwapEffect = D3DSWAPEFFECT_DISCARD;
        g_d3dpp.BackBufferFormat = D3DFMT_UNKNOWN; 
        g_d3dpp.EnableAutoDepthStencil = TRUE;
        g_d3dpp.AutoDepthStencilFormat = D3DFMT_D16;
        //g_d3dpp.PresentationInterval = D3DPRESENT_INTERVAL_ONE;           // Present with vsync
        
        if (g_pD3D->CreateDevice(D3DADAPTER_DEFAULT, D3DDEVTYPE_HAL, globals::hGame, D3DCREATE_HARDWARE_VERTEXPROCESSING, &g_d3dpp, &device) < 0)
        {
            std::cout << "failed to create device\n";
            return;
        }
    
        void** pVTabledevice = *reinterpret_cast<void***>(device);
    
        
        this->pEndSceneAddress = reinterpret_cast<LPVOID>(pVTabledevice[IDirect3DDevice9vTable::ENDSCENE]);
        this->pResetAddress = reinterpret_cast<LPVOID>(pVTabledevice[IDirect3DDevice9vTable::RESET]);
    
        if (MH_CreateHook(this->pEndSceneAddress, &EndScene_Hooked, (LPVOID*)&pEndscene) != MH_OK
            || MH_EnableHook(this->pEndSceneAddress) != MH_OK)
        {
            std::cout << "failed create hook EndScene\n";
            return;
        }
    
        if (MH_CreateHook(this->pResetAddress, &Reset_Hooked, (LPVOID*)&pReset) != MH_OK
            || MH_EnableHook(this->pResetAddress) != MH_OK)
        {
            std::cout << "failed create hook Reset\n";
            return;
        }
    }
    
    
    
    LRESULT ImGui_ImplWin32_WndProcHandler(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam);
    
    LRESULT CALLBACK WndProc_Hooked(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
    {
        static auto once = []()
        {
            std::cout << __FUNCTION__ << " first called!" << std::endl;
    
            return true;
        }();
    
        //如果按下INS键，就打开或关闭外挂设置界面，如果之前是关闭的就打开，如果是打开的就关闭。
        if (uMsg == WM_KEYDOWN && wParam == VK_INSERT)
        {
            vars::bMenuOpen = !vars::bMenuOpen;
            return FALSE;
        }
    
        //如果设置界面是打开状态，则调用ImGui的消息处理
        if (vars::bMenuOpen && ImGui_ImplWin32_WndProcHandler(hwnd, uMsg, wParam, lParam))
        {
            return TRUE;
        }
    
        //调用原窗口处理消息的函数来处理其他消息，https://blog.csdn.net/wangpengk7788/article/details/55053053
        return CallWindowProc(m_pHook->pWndProc, hwnd, uMsg, wParam, lParam);
    }
    
    void CHook::SetupWndProcHook()
    {
        this->pWndProc = (WNDPROC)SetWindowLongPtr(globals::hGame, GWLP_WNDPROC, (LONG_PTR)WndProc_Hooked);
    }
    

最终效果如下。

![image](https://image.3001.net/images/20221227/1672123680_63aa952033eccfaa2b1c8.png!small)

## 结语

实际上关于DirectX
还有很多有意思的地方，比如说经典的WalkHack，通过钩取函数，实现获取人物模型编号，以及修改Z轴深度缓存来达到想要的目的。还有对于imgui，也是有很多可以学习的地方，对比古老的Mfc窗口，或者自定义窗口，imgui的窗口简单而美观，并且实现起来也很方便。

