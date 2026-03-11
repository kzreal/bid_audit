"""
HiAgent API 配置文件
"""

# 基础配置
class Config:
    # API 基础URL，格式：http://域名:端口/api/proxy/api/v1
    # 例如：http://33.234.30.131:32300/api/proxy/api/v1
    API_URL = "http://your-server:port/api/proxy/api/v1"

    # API 密钥，从智能体预览页获取
    API_KEY = "your_api_key_here"

    # 用户ID，1-20字符，仅支持字母和数字
    USER_ID = "250701283"

    # 最大重试次数
    MAX_RETRIES = 3

    # 异步查询的最大重试次数
    ASYNC_MAX_RETRIES = 10


# 测试环境配置
class TestConfig(Config):
    API_URL = "http://test-server:port/api/proxy/api/v1"
    API_KEY = "test_api_key"
    USER_ID = "test_user"


# 生产环境配置
class ProductionConfig(Config):
    pass


# 开发环境配置
class DevelopmentConfig(Config):
    API_URL = "http://dev-server:port/api/proxy/api/v1"
    API_KEY = "dev_api_key"
    USER_ID = "dev_user"


# 根据环境选择配置
environment = "production"  # 可选: "development", "test", "production"

if environment == "development":
    config = DevelopmentConfig()
elif environment == "test":
    config = TestConfig()
else:
    config = ProductionConfig()
