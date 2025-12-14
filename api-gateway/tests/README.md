# API Gateway 测试文档

## 测试覆盖

### 认证测试 (test_auth.py)
- ✅ 根路径测试
- ✅ 健康检查测试
- ✅ JSON 格式登录成功/失败
- ✅ OAuth2 格式登录成功/失败
- ✅ 获取当前用户信息（成功/无令牌/无效令牌）

### 网关测试 (test_gateway.py)
- ✅ 网关健康检查
- ✅ 所有微服务健康状态检查

### 服务层测试 (test_services.py)
- ✅ 认证服务测试
  - Token 创建
  - Token 验证（成功/失败）
  - 用户认证（成功/失败）
- ✅ 代理服务测试
  - 服务 URL 配置
  - 服务健康检查

## 运行测试

```bash
# 运行所有测试
pytest

# 运行指定测试文件
pytest tests/test_auth.py

# 运行指定测试用例
pytest tests/test_auth.py::test_login_json_success

# 显示详细输出
pytest -v

# 显示覆盖率（需要安装 pytest-cov）
pytest --cov=. --cov-report=html
```

## 测试统计

- **总测试数**: 18
- **通过**: 18
- **失败**: 0
- **覆盖率**: 待补充（需要安装 pytest-cov）

## 测试 Fixtures

- `client`: FastAPI TestClient 实例
- `auth_token`: 预认证的 JWT Token

## 注意事项

1. 测试使用 FastAPI 的 TestClient，不需要实际启动服务器
2. 认证测试使用示例用户（admin/admin123）
3. 代理服务测试会尝试连接实际的服务地址（如果服务未运行会返回 unhealthy）
