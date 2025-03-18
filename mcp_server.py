import requests
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import config
import asyncio
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tmf620-mcp")

# Create FastAPI app
app = FastAPI(
    title=config.MCP_SERVER_NAME,
    version=config.MCP_SERVER_VERSION,
    description="TMF620 Catalog Interface"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to make API requests
def api_request(method, endpoint, params=None, json=None):
    if not endpoint.startswith("/"):
        raise ValueError("Endpoint must start with '/'")
    
    valid_methods = ["GET", "POST", "PUT", "DELETE"]
    if method.upper() not in valid_methods:
        raise ValueError(f"Invalid method {method}. Must be one of {valid_methods}")
    
    url = f"{config.TMF620_API_URL}{endpoint}"
    
    # Set up headers with authentication if provided
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Add authentication headers if configured
    if hasattr(config, 'AUTH_CONFIG'):
        if 'api_key' in config.AUTH_CONFIG:
            headers["Authorization"] = f"Bearer {config.AUTH_CONFIG['api_key']}"
        elif 'oauth_token' in config.AUTH_CONFIG:
            headers["Authorization"] = f"Bearer {config.AUTH_CONFIG['oauth_token']}"
        elif 'username' in config.AUTH_CONFIG and 'password' in config.AUTH_CONFIG:
            import base64
            auth_str = f"{config.AUTH_CONFIG['username']}:{config.AUTH_CONFIG['password']}"
            encoded = base64.b64encode(auth_str.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
    
    logger.info(f"Making {method} request to {url}")
    try:
        response = requests.request(method, url, params=params, json=json, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        # Try to get error details from response
        error_detail = "Unknown error"
        try:
            error_detail = response.json()
        except:
            error_detail = response.text
        
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error to {url}")
        raise HTTPException(status_code=503, detail=f"Could not connect to TMF620 API at {config.TMF620_API_URL}")
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout to {url}")
        raise HTTPException(status_code=504, detail="TMF620 API request timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=500, detail=f"Error making request to TMF620 API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint that returns available tools"""
    return {
        "name": config.MCP_SERVER_NAME,
        "version": config.MCP_SERVER_VERSION,
        "description": "TMF620 Catalog Interface",
        "tools": [
            {
                "name": "get_catalog",
                "description": "Get a specific catalog by its ID",
                "parameters": {"catalog_id": "string"}
            },
            {
                "name": "health_check",
                "description": "Check server and API connection health",
                "parameters": {}
            },
            {
                "name": "list_catalogs",
                "description": "List all available product catalogs",
                "parameters": {}
            },
            {
                "name": "create_product_offering",
                "description": "Create a new product offering in a catalog",
                "parameters": {
                    "name": "string",
                    "description": "string",
                    "catalog_id": "string"
                }
            },
            {
                "name": "list_product_offerings",
                "description": "List all product offerings in a catalog",
                "parameters": {"catalog_id": "string (optional)"}
            },
            {
                "name": "get_product_offering",
                "description": "Get details of a specific product offering",
                "parameters": {"offering_id": "string"}
            },
            {
                "name": "list_product_specifications",
                "description": "List all product specifications",
                "parameters": {}
            },
            {
                "name": "get_product_specification",
                "description": "Get details of a specific product specification",
                "parameters": {"specification_id": "string"}
            },
            {
                "name": "create_product_specification",
                "description": "Create a new product specification",
                "parameters": {
                    "name": "string",
                    "description": "string",
                    "version": "string (optional)"
                }
            }
        ]
    }

@app.get("/tools/get_catalog")
async def get_catalog(catalog_id: str):
    """Get specific catalog by ID"""
    try:
        endpoint = config.ENDPOINTS["catalog_detail"].format(id=catalog_id)
        return await asyncio.to_thread(api_request, "GET", endpoint)
    except Exception as e:
        logger.error(f"Error getting catalog: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/health_check")
async def health_check():
    """Check server and API connection health"""
    try:
        api_request("GET", config.ENDPOINTS["catalog_list"])
        return {"status": "healthy", "connection": "successful"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/tools/list_catalogs")
async def list_catalogs():
    """List all product catalogs"""
    return await asyncio.to_thread(api_request, "GET", config.ENDPOINTS["catalog_list"])

@app.post("/tools/create_product_offering")
async def create_product_offering(name: str, description: str, catalog_id: str):
    """Create a new product offering"""
    payload = {
        "name": name,
        "description": description,
        "catalogId": catalog_id,
        "lifecycleStatus": "Active",
        "isBundle": False,
        "isSellable": True
    }
    endpoint = config.ENDPOINTS["product_offering_create"]
    return await asyncio.to_thread(api_request, "POST", endpoint, json=payload)

@app.get("/tools/list_product_offerings")
async def list_product_offerings(catalog_id: str = None):
    """List all product offerings in a catalog"""
    try:
        params = {}
        if catalog_id and catalog_id.lower() != "null" and catalog_id != "":
            params["catalog.id"] = catalog_id
        endpoint = config.ENDPOINTS["product_offering_list"]
        return await asyncio.to_thread(api_request, "GET", endpoint, params=params)
    except Exception as e:
        logger.error(f"Error listing product offerings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/get_product_offering")
async def get_product_offering(offering_id: str):
    """Get details of a specific product offering"""
    try:
        endpoint = config.ENDPOINTS["product_offering_detail"].format(id=offering_id)
        return await asyncio.to_thread(api_request, "GET", endpoint)
    except Exception as e:
        logger.error(f"Error getting product offering: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/list_product_specifications")
async def list_product_specifications():
    """List all product specifications"""
    try:
        endpoint = config.ENDPOINTS["product_specification_list"]
        return await asyncio.to_thread(api_request, "GET", endpoint)
    except Exception as e:
        logger.error(f"Error listing product specifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/get_product_specification")
async def get_product_specification(specification_id: str):
    """Get details of a specific product specification"""
    try:
        endpoint = config.ENDPOINTS["product_specification_detail"].format(id=specification_id)
        return await asyncio.to_thread(api_request, "GET", endpoint)
    except Exception as e:
        logger.error(f"Error getting product specification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/create_product_specification")
async def create_product_specification(name: str, description: str, version: str = "1.0"):
    """Create a new product specification"""
    try:
        payload = {
            "name": name,
            "description": description,
            "version": version,
            "lifecycleStatus": "Active"
        }
        endpoint = config.ENDPOINTS["product_specification_list"]
        return await asyncio.to_thread(api_request, "POST", endpoint, json=payload)
    except Exception as e:
        logger.error(f"Error creating product specification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting MCP server for remote TMF620 API at {config.TMF620_API_URL}")
    logger.info(f"MCP server will be available at http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}")
    logger.info(f"Server configuration: name={config.MCP_SERVER_NAME}, version={config.MCP_SERVER_VERSION}")
    
    # Run the server
    uvicorn.run(
        app,
        host=config.MCP_SERVER_HOST,
        port=config.MCP_SERVER_PORT
    )