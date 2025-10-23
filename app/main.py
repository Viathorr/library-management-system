from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes.user_route import router as user_router
from app.routes.book_route import router as book_router
from app.routes.order_route import router as order_router


app = FastAPI(title="Library Management System API",
              description="API for managing library resources, users, and orders.",
              version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api", tags=["users"])
app.include_router(book_router, prefix="/api", tags=["books"])
app.include_router(order_router, prefix="/api", tags=["orders"])

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
    
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Library Management System API!"}
