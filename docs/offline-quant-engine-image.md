# quant-engine 离线镜像（tar）打包与部署

## 为什么不建议服务器端 `--build`
`quant-engine` 的 Dockerfile 在构建时需要：
- `apt-get` 安装系统依赖
- `pip` 下载/编译 Python 依赖

这两步都依赖外网（或内网 apt/pip 源）。因此“离线包”的正确用法是：在可联网的构建机上**预先构建镜像**，导出为 `.tar`，在服务器上 `docker load` 后直接 `docker compose up`（不要再 `--build`）。

如果你坚持在服务器上运行 `--build`，也可以做到“少拉取/不拉取基础镜像”，但 `apt/pip` 仍然需要可用的软件源（除非你进一步做依赖离线化/内网源）。

## 1) 在构建机（有网）打包 quant-engine 为 tar

### Windows（PowerShell）
在仓库根目录执行：

```powershell
# 仅构建&导出 quant-engine，输出到 dist/
./tools/package_images.ps1 -Registry quantbull -Tag 20260203 -Services quant-engine -SplitByService -SkipPull
```

输出示例：
- `dist/quant-engine_20260203.tar`

> 说明：`-SkipPull` 只是跳过 postgres/redis/tdengine 这些“运行时镜像”的 pull；因为你只打包 quant-engine。

### Linux/macOS（bash）

```bash
SERVICES=quant-engine REGISTRY=quantbull TAG=20260203 SKIP_PULL=1 ./tools/package_images.sh
# 输出：dist/quantbull_images_20260203.tar（仅包含 quant-engine）
```

如果你希望文件名更直观（单服务 tar），建议在 Linux 侧也用 `docker save -o dist/quant-engine_${TAG}.tar quantbull/quant-engine:${TAG}` 自己存一次。

## 2) 拷贝 tar 到服务器
用 scp/rsync/网盘均可，把 `.tar` 传到服务器任意目录，例如 `/opt/quantbull/offline/`。

## 3) 服务器侧加载镜像并启动（推荐）

```bash
docker load -i /opt/quantbull/offline/quant-engine_20260203.tar

# 让 compose 使用该 tag
export QUANT_ENGINE_IMAGE_TAG=20260203

# 离线环境建议禁止 compose 尝试 pull（否则会看到访问 registry-1.docker.io 失败的 warning）
export PULL_POLICY=never

# 启动（关键：不要 --build）
docker compose up -d
```

如果你不想设置 `QUANT_ENGINE_IMAGE_TAG`，也可以把已导入镜像打成 `latest`：

```bash
docker tag quantbull/quant-engine:20260203 quantbull/quant-engine:latest
```

如果你习惯总是带上 `--build`，可以改用：

```bash
docker compose up -d --no-build
```

## 4) 验证

```bash
docker images | grep 'quantbull/quant-engine'
docker compose ps quant-engine
```
