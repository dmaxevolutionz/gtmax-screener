/**
 * Komponen untuk merender balok Power Bar / Shell
 */
function createPowerBarElement(powerBarData) {
    const pb = powerBarData;
    let boxesHtml = '';

    for (let i = 1; i <= pb.total_boxes; i++) {
        const isActive = i <= pb.active_boxes;
        const color = isActive ? pb.bar_color : '#374151'; // Warna aktif vs warna redup/abu-abu
        const animClass = (isActive && pb.is_animated) ? 'animate-signal-blink' : '';

        boxesHtml += `
            <div class="power-box ${animClass}" 
                 style="background-color: ${color}; height: 10px; flex: 1; margin: 0 1px; border-radius: 2px;">
            </div>
        `;
    }

    return `
        <div class="power-bar-wrapper mt-3">
            <div class="flex justify-between text-xs text-gray-400 mb-1">
                <span>Signal Power: ${pb.power_percentage}%</span>
                <span>(${pb.active_boxes}/${pb.total_boxes})</span>
            </div>
            <div class="flex w-full bg-gray-800 p-1 rounded border border-gray-700/50">
                ${boxesHtml}
            </div>
        </div>
    `;
}