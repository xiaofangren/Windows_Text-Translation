import subprocess
import time
import ctypes
import ctypes.wintypes

user32 = ctypes.windll.user32

hwnd = user32.GetForegroundWindow()
sb = ctypes.create_unicode_buffer(256)
user32.GetWindowTextW(hwnd, sb, 256)
print(f"当前窗口: {sb.value} (0x{hwnd:x})")
print("请在 8 秒内切换到浏览器并选中一些文字...")
time.sleep(8)

hwnd2 = user32.GetForegroundWindow()
sb2 = ctypes.create_unicode_buffer(256)
user32.GetWindowTextW(hwnd2, sb2, 256)
print(f"目标窗口: {sb2.value} (0x{hwnd2:x})")

ps_code = f'''
$hwnd = {hwnd2}

Add-Type -AssemblyName UIAutomationClient

function ScanElement($element, $depth) {{
    $indent = "  " * $depth
    try {{
        $name = $element.Current.Name
        $ctrl = $element.Current.ControlType.ProgrammaticName
        if ($name.Length -gt 100) {{ $name = $name.Substring(0,100) + "..." }}
        
        $hasText = $false
        $patterns = $element.GetSupportedPatterns()
        foreach ($p in $patterns) {{
            if ($p.ProgrammaticName -eq "TextPattern" -or $p.ProgrammaticName -eq "ValuePattern") {{
                $hasText = $true
            }}
        }}
        
        if ($hasText -or ($name -and $name.Trim() -ne "")) {{
            Write-Host "$indent$ctrl"
            if ($name.Trim()) {{ Write-Host "$indent  Name: '$name'" }}
            foreach ($p in $patterns) {{
                Write-Host "$indent  $($p.ProgrammaticName)"
            }}
        }}
        
        if ($depth -lt 12) {{
            try {{
                $children = $element.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
                if ($children.Count -gt 0) {{
                    foreach ($child in $children) {{
                        ScanElement $child ($depth+1)
                    }}
                }} elseif ($hasText -and $depth -gt 2) {{
                    try {{
                        $tp = $element.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
                        $selection = $tp.GetSelection()
                        if ($selection.Count -gt 0) {{
                            $t = $selection[0].GetText(-1)
                            if ($t) {{ Write-Host "SELECTED: '$t'" }}
                        }}
                    }} catch {{}}
                    try {{
                        $vp = $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                        $v = $vp.Current.Value
                        if ($v) {{ Write-Host "VALUE: '$v'" }}
                    }} catch {{}}
                }}
            }} catch {{ }}
        }} elseif ($depth -ge 12 -and $hasText) {{
            try {{
                $tp = $element.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
                $selection = $tp.GetSelection()
                if ($selection.Count -gt 0) {{
                    $t = $selection[0].GetText(-1)
                    if ($t) {{ Write-Host "DEEP SELECTED: '$t'" }}
                }}
            }} catch {{}}
        }}
    }} catch {{ }}
}}

try {{
    $element = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
    if (-not $element) {{ Write-Host "Element: null"; return }}
    ScanElement $element 0
}} catch {{
    Write-Host "ERROR: $_"
}}

Write-Host "`n=== 直接搜索 TextPattern ==="
try {{
    $root = [System.Windows.Automation.Automation]::RootElement
    $textPatternCond = [System.Windows.Automation.PropertyCondition]::new(
        [System.Windows.Automation.AutomationElement]::IsTextPatternAvailableProperty, $true)
    $textElements = $root.FindAll([System.Windows.Automation.TreeScope]::Subtree, $textPatternCond)
    Write-Host "全局 TextPattern 元素数: $($textElements.Count)"
    $foundSelected = $false
    foreach ($el in $textElements) {{
        try {{
            $tp = $el.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
            $sel = $tp.GetSelection()
            if ($sel.Count -gt 0) {{
                $t = $sel[0].GetText(-1)
                if ($t) {{
                    Write-Host "找到选中文本: '$t'"
                    $foundSelected = $true
                }}
            }}
        }} catch {{ }}
    }}
    if (-not $foundSelected) {{ Write-Host "未找到选中文本" }}
}} catch {{
    Write-Host "Global search error: $_"
}}
'''

print("\n深度扫描 UIA...\n")

try:
    result = subprocess.run(
        ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_code],
        capture_output=True, text=True, timeout=30
    )
    print(result.stdout)
    if result.stderr.strip():
        print("STDERR:", result.stderr[:500])
except Exception as e:
    print(f"Error: {e}")

input("\n按回车退出...")
