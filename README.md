# TMF620 MCP Server

This is a Model Context Protocol (MCP) server that allows AI agents to interact with a remote TMF620 Product Catalog Management API.

## Features

- Connect AI agents to a remote TMF620 Product Catalog Management API
- List, retrieve, and create catalogs, product offerings, and product specifications
- Configurable connection to any TMF620-compliant API

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Configure the connection to your remote TMF620 server:

Edit the `config.py` file and update the following settings:

- `TMF620_API_URL`: The base URL of your remote TMF620 server
- `AUTH_CONFIG`: Authentication details for your remote server (if required)
- Other settings as needed

## Running the Server

1. Start the mock TMF620 API server (for testing):

```bash
python mock_tmf620_api.py
```

This will start the mock server on http://localhost:8000.

2. Start the MCP server:

```bash
python mcp_server.py
```

The server will be available at http://localhost:7001 by default.

## Using with Cursor

To use this MCP server with Cursor:

1. Make sure the MCP server is running at http://localhost:7001.

2. In Cursor, go to Settings > Connections.

3. Add a new MCP connection with the URL:
   ```
   http://localhost:7001
   ```

4. Name your connection (e.g., "TMF620 API").

5. Save the connection.

You should then see the MCP tools appear in Cursor when you click on the tools icon.

### Troubleshooting Cursor Connection

If Cursor can't find any tools in your MCP server:

1. Verify the server is running correctly by checking the log messages in your terminal.

2. Ensure both servers are running:
   - The mock TMF620 API server on port 8000
   - The MCP server on port 7001

3. Try these alternative connection URLs in Cursor:
   - `http://127.0.0.1:7001`
   - `http://localhost:7001/`

4. Check for network issues:
   - Make sure your firewall allows connections to port 7001
   - Try disabling any network security software temporarily

5. Restart Cursor after making changes to the server.

6. Try visiting http://localhost:7001/ in your browser - you should receive a response even if it's a 404.

## Using with Claude Desktop

To use this MCP server with Claude Desktop, add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "tmf620": {
      "command": "python",
      "args": ["path/to/mcp_server.py"]
    }
  }
}
```

## Available Tools

The MCP server exposes the following tools to AI agents:

### Catalog Management
- `get_catalog`: Get a specific catalog by ID
- `list_catalogs`: List all available product catalogs

### Product Offering Management
- `list_product_offerings`: List all product offerings with optional filtering by catalog ID
- `get_product_offering`: Get a specific product offering by ID
- `create_product_offering`: Create a new product offering

### Product Specification Management
- `list_product_specifications`: List all product specifications
- `get_product_specification`: Get a specific product specification by ID
- `create_product_specification`: Create a new product specification

### System Tools
- `health_check`: Check the health of the server and API connection

## Example Usage

Here's an example of how an AI agent might use these tools:

```
To list all catalogs:
/tool list_catalogs

To get a specific catalog:
/tool get_catalog catalog_id=123456

To check health:
/tool health_check

To list product offerings:
/tool list_product_offerings catalog_id=cat-001

To get a specific product offering:
/tool get_product_offering offering_id=po-001

To create a new product offering:
/tool create_product_offering name="Premium Service" description="High-quality service" catalog_id="cat-001"
```

## Extending

To add more tools for other TMF620 endpoints, edit the `mcp_server.py` file and add new tool definitions following the existing pattern.

## License

This project is licensed under the MIT License. 