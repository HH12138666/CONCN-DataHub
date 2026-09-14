# 现有回归测试

在仓库根目录执行：

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

- `backend/`：19 项实际 MySQL 集成测试、2 项边界预览测试、1 项发布完整性测试，覆盖名额、并发、审核、越权、下载及变更后的源文件拒绝处理。
- `clipping/`：5 项测试，覆盖编码、分级、命名、配置及裁切网格和南北方向的逐像元核对。

网站测试会清空并重建 **`concn_datahub_test`** 的测试记录，只能在专用、可丢弃的本地测试库执行。测试禁止使用其他数据库名；不要将真实数据放入该测试库。连接参数读取 `backend/.env`，测试只覆盖数据库名及测试选项。

这套回归测试使用合成流域和 ZIP，不会向正式目录插入演示流域。另已通过 `scripts/verify_local_download.py` 对本地真实数据执行 HTTP 下载验收，记录见 [本地真实下载验收](../docs/本地真实下载验收.md)。暂时没有完整浏览器端到端测试套件。
