import uvicorn

from src.core.settings import settings
from src.gunicorn_runner import GunicornApplication


def main() -> None:
    if settings.reload:
        uvicorn.run(
            "src.core.application:get_app",
            workers=settings.workers_count,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level="debug",
            factory=True,
        )
    else:
        GunicornApplication(
            "src.core.application:get_app",
            host=settings.host,
            port=settings.port,
            workers=settings.workers_count,
            factory=True,
            accesslog="-",
            loglevel="warning",
            access_log_format='%r "-" %s "-" %Tf',  # noqa: WPS323
        ).run()


if __name__ == "__main__":
    main()
