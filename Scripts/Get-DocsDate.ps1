<#
.SYNOPSIS
    输出当前本机日期，供 Docs 文档元数据（最后更新、修订记录）使用。

.DESCRIPTION
    无参数时输出 yyyy-MM-dd 格式的当前日期。
    带 -Full 参数时输出完整的日期时间戳，用于修订记录等需精确到时间的场景。

.EXAMPLE
    powershell -NoProfile -File Scripts/Get-DocsDate.ps1
    # 2026-07-19

.EXAMPLE
    powershell -NoProfile -File Scripts/Get-DocsDate.ps1 -Full
    # 2026-07-19 21:10:05 +08:00

.NOTES
    参见 Docs 规则 docs-update-date.mdc。
#>

param (
    [switch]$Full
)

if ($Full) {
    Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
}
else {
    Get-Date -Format "yyyy-MM-dd"
}
