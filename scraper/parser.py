import json
from curl_cffi import requests
from lxml import html


def fetch_otodom_listing(url: str) -> dict | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    try:
        response = requests.get(
            url, 
            headers = headers, 
            impersonate = "chrome120", 
            timeout = 15
        )

        if response.status_code != 200:
            print(f"Fetch error: HTTP {response.status_code}")
            return None

        # Extract __NEXT_DATA__ JSON script directly via XPath
        tree = html.fromstring(response.text)
        script_nodes = tree.xpath("//script[@id='__NEXT_DATA__']/text()")
        json_string = next(iter(script_nodes), None)

        if not json_string:
            print("Could not find __NEXT_DATA__ script tag via XPath.")
            return None

        data = json.loads(json_string)
        
        page_props = data.get("props", {}).get("pageProps", {})
        ad_data = page_props.get("ad")

        if not ad_data:
            print("Missing 'ad' object in parsed JSON.")
            return None

        target = ad_data.get("target", {})
        attributes = ad_data.get("attributes", {})
        location = ad_data.get("location", {})
        
        images_list = ad_data.get("images") or []
        first_image = next(iter(images_list), {})
        image_url = first_image.get("large") or first_image.get("medium")

        district = target.get("Subregion") or target.get("District")
        if not district:
            locations = location.get("reverseGeocoding", {}).get("locations", [])
            district_obj = next((loc for loc in locations if loc.get("locationLevel") == "district"), {})
            district = district_obj.get("name")

        rooms_raw = target.get("Rooms_num") or attributes.get("rooms_num")
        rooms_val = next(iter(rooms_raw), None) if isinstance(rooms_raw, list) else rooms_raw
        rooms = int(rooms_val) if rooms_val else None

        return {
            "otodom_id": str(ad_data.get("id") or target.get("Id")),
            "title": ad_data.get("title") or target.get("Title", "Brak tytułu"),
            "url": url,
            "city": target.get("City") or location.get("address", {}).get("city"),
            "district": district,
            "total_price": target.get("Price") or attributes.get("price"),
            "price_per_sqm": target.get("Price_per_m") or attributes.get("price_per_m"),
            "area_sqm": target.get("Area") or attributes.get("m"),
            "rooms": rooms,
            "image_url": image_url,
        }

    except Exception as e:
        print(f"Parsing error: {e}")
        return None