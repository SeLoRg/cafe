from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from orders_service.app.router import router as orders_service_router


app = FastAPI(
    title="Your API",
    description="API documentation for your project",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",  # Путь для Swagger UI
    redoc_url="/api/redoc",  # Путь для Redoc UI
)
app.include_router(orders_service_router, prefix="/api/orders")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
