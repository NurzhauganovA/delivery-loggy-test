import uvicorn


try:
    import conf
except ImportError:
    from api import conf


def main() -> None:
    uvicorn.run(
        'api:app',
        host=conf.api.host,
        port=conf.api.port,
        reload=conf.api.reload,
        reload_delay=0.1,
        log_level=conf.api.log_level,
        ws_ping_interval=600.0,
        ws_ping_timeout=600.0,
        use_colors=True,
        access_log=True
    )


if __name__ == '__main__':
    main()
