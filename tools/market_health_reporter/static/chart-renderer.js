// 🌰🌰🌰 Dynamic chart renderer for Market Health Reporter
// This script creates interactive charts using Chart.js

document.addEventListener('DOMContentLoaded', function() {
    // Find all canvas elements for charts
    const canvases = document.querySelectorAll('canvas[id^="chart-"]');
    
    canvases.forEach(canvas => {
        const metricId = canvas.id.replace('chart-', '');
        const metricElement = canvas.closest('.metric');
        
        // Extract data from the DOM elements
        const currentValue = parseFloat(metricElement.querySelector('p:nth-of-type(1) strong').nextSibling.textContent.trim());
        const change = parseFloat(metricElement.querySelector('p:nth-of-type(2) strong').nextSibling.textContent.trim());
        const changePercent = parseFloat(metricElement.querySelector('p:nth-of-type(2)').textContent.match(/-?\d+\.?\d*%/)[0].replace('%', ''));
        
        // Generate sample historical data (in real implementation, this would come from API)
        const labels = [];
        const data = [];
        const today = new Date();
        
        // Generate 30 days of historical data
        for (let i = 29; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            
            // Simulate realistic price movement based on current value and change
            const baseValue = currentValue / (1 + (changePercent / 100));
            const randomVariation = (Math.random() - 0.5) * baseValue * 0.02;
            const trendFactor = (changePercent / 100) * (i / 29);
            data.push(baseValue * (1 + trendFactor) + randomVariation);
        }
        
        // Create the chart
        const ctx = canvas.getContext('2d');
        const chartTitle = metricElement.querySelector('h2').textContent;
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: chartTitle,
                    data: data,
                    borderColor: changePercent >= 0 ? '#10b981' : '#ef4444',
                    backgroundColor: changePercent >= 0 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    pointBackgroundColor: changePercent >= 0 ? '#10b981' : '#ef4444',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${chartTitle} - 30 Day Trend`,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `${chartTitle}: ${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Value'
                        },
                        beginAtZero: false
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    });
});