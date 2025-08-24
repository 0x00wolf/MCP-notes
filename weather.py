# From the modelcontextprotocol.io server demonstration

from typing import Any
import httpx
from mcp.server.fastmcp import fastmcp

# Initialize fast server
mcp = fastmcp("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """ Make a request to NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url=url, headers=headers, timeout=15.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """ Format an alert into a readable string."""
    props = feature["properties"]
    return f"""
    Events: {props.get('event', 'Unknown')}
    Area: {props.get('areaDesc', 'Unknown')}
    Severity: {props.get('severity', 'Unknown')}
    Description: {props.get('description', 'No description available')}
    Instruction: {props.get('instruction', 'No specific instructions available')}
    """


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather Alerts for a US state.

    Args:
        state: Two letter us State code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alert found"

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]  # Only show next 5 periods
        forecast = f"""
        {period['name']}:\n
        Temperature: {period["temperature"]}°{period["temperatureUnit"]}\n
        Wind: {period["windSpeed"]} {period["windDirection"]}\n
        Forecast: {period["detailedForecast"]}
        """
    forecasts.append(forecast)
    return "\n---\n".join(forecasts)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
