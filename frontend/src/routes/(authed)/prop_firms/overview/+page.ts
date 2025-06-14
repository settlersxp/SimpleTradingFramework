import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
    // Fetch all prop firms
    const propFirmsResponse = await fetch('/api/prop_firms');
    if (!propFirmsResponse.ok) {
        throw new Error('Failed to load prop firms');
    }
    const propFirms = await propFirmsResponse.json();

    // For each prop firm, fetch their trades
    const propFirmsWithTrades = await Promise.all(
        propFirms.map(async (firm: any) => {
            // Fetch trades for the current prop firm
            const tradesResponse = await fetch(`/api/prop_firms/${firm.id}/trades`);
            const tradesJson = tradesResponse.ok ? await tradesResponse.json() : { trades: [] };
            const trades = Array.isArray(tradesJson.trades) ? tradesJson.trades : [];

            // Fetch trade pairs for each firm
            const tradePairsResponse = await fetch(`/api/prop_firms/${firm.id}/trade_pairs`);
            const tradePairs = tradePairsResponse.ok ? await tradePairsResponse.json() : [];

            return {
                ...firm,
                trades,
                tradePairs: tradePairs.trade_pairs
            };
        })
    );

    // console.log("Prop firms with trades:", propFirmsWithTrades[0].trades);
    return {
        propFirms: propFirmsWithTrades
    };
}; 