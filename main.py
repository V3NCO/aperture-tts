# Source - https://stackoverflow.com/a
# Posted by MatsLindh
# Retrieved 2025-11-10, License - CC BY-SA 4.0

from aperture.app import app

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('aperture.app:app', host='0.0.0.0', port=7272, reload=True)
