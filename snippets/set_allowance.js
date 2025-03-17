// SNIPPET 1 START
const setAllowance = async (chain, token, contract_name, amount) => {
  try {
    const response = await fetch(
      `https://api.compasslabs.ai/beta/v0/generic/allowance/set/${chain}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: {
          sender: "0x...", // public wallet address
          call_data: {
            token,
            contract_name,
            amount,
          },
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching allowance:", error);
    return null;
  }
};

const token = "USDT";
const contract_name = "UniswapV3Router";
const amount = "1";

await setAllowance(chain, token, contract_name, amount);
// SNIPPET 1 END
