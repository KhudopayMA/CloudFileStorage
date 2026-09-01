from collections.abc import Iterator

import pytest
from django.conf import settings
from django.core.management import call_command
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer

# mypy: ignore-errors

# @pytest.fixture(scope="session")
# def postgres_container() -> Iterator[PostgresContainer]:
#     with PostgresContainer("postgres:18.4") as postgres:
#         yield postgres
#
#
# @pytest.fixture(scope="session")
# def redis_container() -> Iterator[RedisContainer]:
#     with RedisContainer("redis:8.10.0") as redis:
#         yield redis
#
#
# @pytest.fixture(scope="session")
# def django_db_setup(  # type: ignore[no-untyped-def]
#     postgres_container: PostgresContainer,
#     redis_container: RedisContainer,
#     django_db_blocker,
# ) -> None:
#     settings.DATABASES["default"]["ENGINE"] = "django.db.backends.postgresql"
#     settings.DATABASES["default"]["NAME"] = postgres_container.dbname
#     settings.DATABASES["default"]["USER"] = postgres_container.username
#     settings.DATABASES["default"]["PASSWORD"] = postgres_container.password
#     settings.DATABASES["default"]["HOST"] = postgres_container.get_container_host_ip()
#     settings.DATABASES["default"]["PORT"] = postgres_container.get_exposed_port(5432)
#     settings.DATABASES["default"]["ATOMIC_REQUESTS"] = False
#
#     with django_db_blocker.unblock():
#         call_command("migrate")
#
#     redis_host = redis_container.get_container_host_ip()
#     redis_port = redis_container.get_exposed_port(6379)
#
#     settings.CACHES["default"] = {
#         "BACKEND": "django.core.cache.backends.redis.RedisCache",
#         "LOCATION": f"redis://{redis_host}:{redis_port}/0",
#     }
