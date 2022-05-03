from fastapi import FastAPI
from routers.auth import ruteador_auth
from routers.ordenes import ruteador_ordenes
from fastapi_jwt_auth import AuthJWT
from database.schemas import Settings
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
import re, inspect

app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title = "API de Entrega de Comida",
        version = "0.1",
        description = "Una API para un servicio de entrega de comida",
        routes = app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        }
    }

    # Get all routes where jwt_optional() or jwt_required
    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route,"endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            # access_token
            if (
                re.search("jwt_required", inspect.getsource(endpoint)) or
                re.search("fresh_jwt_required", inspect.getsource(endpoint)) or
                re.search("jwt_optional", inspect.getsource(endpoint))
            ):
                openapi_schema["paths"][path][method]["security"] = [
                    {
                        "Bearer Auth": []
                    }
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi



@AuthJWT.load_config
def get_config():
    return Settings()
    

app.include_router(ruteador_ordenes)
app.include_router(ruteador_auth)