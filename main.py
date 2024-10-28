import uvicorn
import asyncio
from server.init import create_app

async def main():
    app = await create_app()
    config = uvicorn.Config(app, host="0.0.0.0", port=5002)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())