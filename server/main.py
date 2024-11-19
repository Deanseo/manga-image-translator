import io

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse, JSONResponse

from server.instance import ExecutorInstance, executor_instances
from server.request_extraction import get_ctx, while_streaming
from server.to_json import to_json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
async def register_instance(instance: ExecutorInstance, request: Request):
    instance.ip = request.client.host
    executor_instances.register(instance)
    return {"code": 0}

def transform_to_image(ctx):
    img_byte_arr = io.BytesIO()
    ctx.result.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()

@app.post("/json")
async def json(req: Request):
    ctx = await get_ctx(req)
    json = to_json(ctx)
    return JSONResponse(content=json)

@app.post("/bytes")
async def bytes(req: Request):
    ctx = await get_ctx(req)

@app.post("/image")
async def image(req: Request):
    ctx = await get_ctx(req)
    img_byte_arr = io.BytesIO()
    ctx.result.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type="image/png")

@app.post("/stream_json")
async def stream_json(req: Request):
    return while_streaming(req, transform_to_image)

@app.post("/stream_bytes")
async def stream_bytes(req: Request):
    return while_streaming(req, transform_to_image)

@app.post("/stream_image")
async def stream_image(req: Request):
    return while_streaming(req, transform_to_image)

if __name__ == '__main__':
    import uvicorn
    from args import parse_arguments

    args = parse_arguments()
    uvicorn.run(app, host=args.host, port=args.port)
