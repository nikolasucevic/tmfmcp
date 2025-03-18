import requests
import json

def create_product_offering(name, description, catalog_id="cat-001"):
    url = "http://localhost:7001/tools/create_product_offering"
    params = {
        "name": name,
        "description": description,
        "catalog_id": catalog_id
    }
    
    response = requests.post(url, params=params)
    print(f"Creating product offering: {name}")
    print(f"Response status: {response.status_code}")
    try:
        print(f"Response body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response text: {response.text}")
    return response

# Example mock products
mock_products = [
    {
        "name": "Enterprise Cloud Storage",
        "description": "High-performance cloud storage solution for enterprises with 99.99% uptime SLA"
    },
    {
        "name": "5G Private Network",
        "description": "Dedicated 5G network infrastructure for industrial and enterprise use"
    },
    {
        "name": "IoT Platform Pro",
        "description": "Enterprise IoT platform with advanced analytics and device management"
    },
    {
        "name": "Managed Security Suite",
        "description": "Comprehensive security solution including SIEM, EDR, and 24/7 SOC"
    }
]

if __name__ == "__main__":
    print("Creating mock product offerings...")
    for product in mock_products:
        try:
            result = create_product_offering(**product)
            print("-" * 50)
        except Exception as e:
            print(f"Error creating product {product['name']}: {e}")
            print("-" * 50) 