import httpx

def get_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=10.0, follow_redirects=True)
