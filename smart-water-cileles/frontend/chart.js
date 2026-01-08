document.addEventListener("DOMContentLoaded", () => {

    if (!DATA_AIR || DATA_AIR.length === 0) return;

    new Chart(document.getElementById("chartPH"), {
        type: "bar",
        data: {
            labels: DATA_AIR.map(d => d.rumah),
            datasets: [{
                label: "Nilai pH",
                data: DATA_AIR.map(d => d.pH),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    min: 0,
                    max: 14,
                    title: {
                        display: true,
                        text: "Skala pH"
                    }
                }
            }
        }
    });

});
