import sys
sys.path.append('src')

print("Testing API Manager...")
print("-" * 40)

try:
    from api.api_manager import APIManager
    print("1. API Manager imported OK")
    
    manager = APIManager()
    print("2. API Manager created OK")
    
    status = manager.get_api_status()
    print("3. Got status OK")
    
    print("\nStatus details:")
    print(f"Claude status: {status['claude']['status']}")
    print(f"Claude error: {status['claude'].get('error', 'None')}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()