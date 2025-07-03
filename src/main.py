from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.agent.examples import supervisor  # 根据你的实际实现调整
from typing import Optional
from loguru import logger
from langchain_core.messages import AIMessage, HumanMessage, AIMessageChunk
import uuid

app = FastAPI()

# 允许跨域，方便本地前端调试
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: Optional[str] = None


class ChatResponse(BaseModel):
    response: str


@app.api_route("/chat", response_model=ChatResponse, methods=["POST", "GET"])
async def chat_endpoint(req: Request, chat_request: ChatRequest = None):
    if req.method == "POST":
        user_message = chat_request.message
    else:
        user_message = req.query_params.get("message")


    result = supervisor.invoke(
        {"messages": [{"role": "user", "content": user_message}]}
    )
    messages = result.get("messages", [])
    logger.info(f"result: {messages}")
    assistant_reply = next(
        (msg.content for msg in reversed(messages) if isinstance(msg, AIMessage)), None
    )
    return ChatResponse(response=assistant_reply)


@app.api_route("/chat/stream", methods=["POST", "GET"])
async def chat_sse(request: Request, chat_request: ChatRequest = None):
    async def event_generator():
        if request.method == "POST":
            user_message = chat_request.message
        else:
            user_message = request.query_params.get("message")
        logger.info(f"user_message: {user_message}")


        thread_id = str(uuid.uuid4())
        cfg = {"configurable": {"thread_id": thread_id}}
        async for output in supervisor.astream(
            {"messages": [("user", user_message)]}, config=cfg, stream_mode="messages"
        ):
            if await request.is_disconnected():
                break
            # logger.info(f"output: {output}")
            if isinstance(output[0], AIMessageChunk):
                yield f"data: {output[0].content}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/")
async def chat_endpoint():
    return {"message": "Hello, World!"}
