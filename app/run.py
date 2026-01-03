"""Init"""
import multiprocessing
import os
import sys


if __name__ == "__main__":
    multiprocessing.freeze_support()

    if not os.environ.get('MAIN_PROCESS'):
        os.environ['MAIN_PROCESS'] = '1'
    else:
        sys.exit(0)  # Exit if already initialized

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
