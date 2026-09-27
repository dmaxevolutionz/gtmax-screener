/**
 * Komponen Kartu Saham
 */
function createStockCardElement(stock) {
    const plan = stock.trading_plan;
    const powerBarHtml = createPowerBarElement(stock.power_bar);

    return `
        <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-lg hover:border-gray-600 transition">
            <div class="flex justify-between items-center mb-2">
                <h2 class="text-xl font-bold text-yellow-400">${stock.ticker}</h2>
                <span class="text-xs font-bold px-2.5 py-1 rounded" style="background-color: ${stock.power_bar.bar_color}22; color: ${stock.power_bar.bar_color}; border: 1px solid ${stock.power_bar.bar_color}44;">
                    ${stock.signal}
                </span>
            </div>
            <div class="text-2xl font-black mb-3">
                Rp ${stock.close.toLocaleString('id-ID')}
            </div>
            <div class="grid grid-cols-3 gap-2 text-xs bg-gray-900 p-2 rounded mb-3 text-center border border-gray-700/40">
                <div><span class="text-gray-400">EMA20:</span><br><span class="font-medium">${stock.ema20}</span></div>
                <div><span class="text-gray-400">EMA50:</span><br><span class="font-medium">${stock.ema50}</span></div>
                <div><span class="text-gray-400">RSI:</span><br><span class="font-medium">${stock.rsi}</span></div>
            </div>
            <div class="text-xs space-y-1 bg-gray-900/60 p-2.5 rounded border border-gray-700/50">
                <div class="flex justify-between"><span class="text-red-400 font-semibold">Stop Loss (SL):</span> <span>Rp ${plan.stop_loss.toLocaleString('id-ID')}</span></div>
                <div class="flex justify-between"><span class="text-green-400 font-semibold">Take Profit 1:</span> <span>Rp ${plan.take_profit_1.toLocaleString('id-ID')}</span></div>
                <div class="flex justify-between"><span class="text-green-300 font-semibold">Take Profit 2:</span> <span>Rp ${plan.take_profit_2.toLocaleString('id-ID')}</span></div>
            </div>
            ${powerBarHtml}
        </div>
    `;
}