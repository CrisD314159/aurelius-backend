"""Init"""
import multiprocessing


if __name__ == "__main__":
    multiprocessing.freeze_support()

    import uvicorn
    from app.main import app

    if multiprocessing.get_start_method(allow_none=True) != 'spawn':
        multiprocessing.set_start_method('spawn', force=True)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8223,
        reload=False,
        workers=1,
        log_level="info"
    )
