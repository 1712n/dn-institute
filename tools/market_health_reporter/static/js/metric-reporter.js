// 🌰 Chestnut: Dynamic chart functionality for Market Health Reporter
document.addEventListener('DOMContentLoaded', function() {
    const chartContainers = document.querySelectorAll('.chart-container');
    
    chartContainers.forEach(container => {
        const metricName = container.dataset.metricName;
        const chartData = JSON.parse(container.dataset.chartData);
        
        // Create canvas element for Chart.js
        const canvas = document.createElement('canvas');
        canvas.id = `chart-${metricName.replace(/\s+/g, '-').toLowerCase()}`;
        container.appendChild(canvas);
        
        // Prepare data for Chart.js
        const labels = chartData.map(item => item.date);
        const values = chartData.map(item => item.value);
        
        // Create gradient for chart background
        const ctx = canvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(54, 162, 235, 0.2)');
        gradient.addColorStop(1, 'rgba(54, 162, 235, 0)');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: metricName,
                    data: values,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    pointBackgroundColor: 'rgb(54, 162, 235)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    });
    
    console.log('🌰 Market Health Reporter: Dynamic charts initialized');
});