import pytest
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer
from django.conf import settings


@pytest.fixture
def db_container() -> PostgresContainer:
    with PostgresContainer("postgres:18.4") as postgres:
        yield postgres


@pytest.fixture
def redis_container() -> RedisContainer:
    with RedisContainer("redis:8.10.0") as redis:
        yield redis


@pytest.fixture
def django_db_setup(
    db_container: PostgresContainer,
    redis_container: RedisContainer
):

    settings.DATABASE["default"] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_container.dbname,
        'USER': db_container.username,
        'PASSWORD': db_container.password,
        'HOST': db_container.get_container_host_ip(),
        'PORT': db_container.port,
    }

    settings.CACHES["default"] = {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://{redis_container.get_container_host_ip()}:{redis_container.port}',
    }
