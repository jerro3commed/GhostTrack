#!/usr/bin/env python3
"""
GhostTrack - Geolocation Helper Utilities
Provides helper functions for IP geolocation, coordinate parsing,
and map URL generation used across the tracking modules.
"""

import re
import requests
from typing import Optional, Dict, Any


# Default timeout for HTTP requests (seconds)
REQUEST_TIMEOUT = 10

# Free geolocation API endpoints (fallback chain)
GEO_APIS = [
    "http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query",
    "https://ipapi.co/{ip}/json/",
    "https://freegeoip.app/json/{ip}",
]


def get_ip_geolocation(ip: str) -> Optional[Dict[str, Any]]:
    """
    Fetch geolocation data for a given IP address.
    Tries multiple free APIs in sequence as fallback.

    Args:
        ip: The IP address string to look up.

    Returns:
        A dictionary with geolocation fields, or None on failure.
    """
    for api_url in GEO_APIS:
        try:
            url = api_url.format(ip=ip)
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                # ip-api returns a 'status' field; others just return data
                if data.get("status") == "fail":
                    continue
                return normalize_geo_data(data)
        except (requests.RequestException, ValueError):
            continue
    return None


def normalize_geo_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize geolocation data from different API response formats
    into a consistent schema.

    Args:
        raw: Raw JSON response dictionary from a geo API.

    Returns:
        Normalized dictionary with standard keys.
    """
    return {
        "ip":          raw.get("query") or raw.get("ip", "N/A"),
        "country":     raw.get("country") or raw.get("country_name", "N/A"),
        "country_code": raw.get("countryCode") or raw.get("country_code", "N/A"),
        "region":      raw.get("regionName") or raw.get("region", "N/A"),
        "city":        raw.get("city", "N/A"),
        "zip":         raw.get("zip") or raw.get("postal", "N/A"),
        "latitude":    raw.get("lat") or raw.get("latitude", 0.0),
        "longitude":   raw.get("lon") or raw.get("longitude", 0.0),
        "timezone":    raw.get("timezone", "N/A"),
        "isp":         raw.get("isp") or raw.get("org", "N/A"),
        "org":         raw.get("org", "N/A"),
        "as":          raw.get("as", "N/A"),
    }


def build_google_maps_url(lat: float, lon: float) -> str:
    """
    Generate a Google Maps URL for a given coordinate pair.

    Args:
        lat: Latitude as a float.
        lon: Longitude as a float.

    Returns:
        A Google Maps URL string.
    """
    return f"https://www.google.com/maps?q={lat},{lon}"


def build_osm_url(lat: float, lon: float, zoom: int = 13) -> str:
    """
    Generate an OpenStreetMap URL for a given coordinate pair.

    Args:
        lat:  Latitude as a float.
        lon:  Longitude as a float.
        zoom: Zoom level (default 13).

    Returns:
        An OpenStreetMap URL string.
    """
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map={zoom}/{lat}/{lon}"


def validate_ip(ip: str) -> bool:
    """
    Validate whether a string is a valid IPv4 or IPv6 address.

    Args:
        ip: The string to validate.

    Returns:
        True if valid IP, False otherwise.
    """
    ipv4_pattern = re.compile(
        r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
        r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$"
    )
    ipv6_pattern = re.compile(
        r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
    )
    return bool(ipv4_pattern.match(ip) or ipv6_pattern.match(ip))


def format_geo_output(data: Dict[str, Any]) -> str:
    """
    Format a normalized geolocation dictionary into a human-readable string
    suitable for terminal output.

    Args:
        data: Normalized geo data dictionary.

    Returns:
        Formatted multi-line string.
    """
    maps_url = build_google_maps_url(data["latitude"], data["longitude"])
    osm_url  = build_osm_url(data["latitude"], data["longitude"])

    lines = [
        f"  IP Address   : {data['ip']}",
        f"  Country      : {data['country']} ({data['country_code']})",
        f"  Region       : {data['region']}",
        f"  City         : {data['city']}",
        f"  ZIP / Postal : {data['zip']}",
        f"  Latitude     : {data['latitude']}",
        f"  Longitude    : {data['longitude']}",
        f"  Timezone     : {data['timezone']}",
        f"  ISP          : {data['isp']}",
        f"  Organization : {data['org']}",
        f"  AS           : {data['as']}",
        f"  Google Maps  : {maps_url}",
        f"  OpenStreetMap: {osm_url}",
    ]
    return "\n".join(lines)
