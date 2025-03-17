"""Example of setting allowance."""
# mypy: ignore-errors
# SNIPPET 1 START
import requests


def set_allowance(chain, token, contract_name, amount):
    """Set allowance."""
    url = f"https://api.compasslabs.ai/beta/v0/generic/allowance/set/{chain}"
    payload = {
        "sender": "0x...",
        "call_data": {"token": token, "contract_name": contract_name, "amount": amount},
    }

    try:
        response = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching allowance:", e)
        return None


if __name__ == "__main__":
    chain, token, contract_name, amount = "ethereum", "USDT", "UniswapV3Router", "1"
    result = set_allowance(chain, token, contract_name, amount)
# SNIPPET 1 END
