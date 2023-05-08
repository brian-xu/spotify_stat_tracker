window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesSimple = document.getElementById('datatablesSimple');
    if (datatablesSimple) {
        new simpleDatatables.DataTable(datatablesSimple, {
            columns: [
                { select: [0, 5], sortable: false},
                {
                    select: 3,
                    sort: "desc",
                    type: 'string',
                    render: function(data, td, rowIndex, cellIndex) {
                        let totalSeconds = parseInt(data);
                        let hours = Math.floor(totalSeconds / 3600);
                        totalSeconds %= 3600;
                        let minutes = Math.floor(totalSeconds / 60);
                        let seconds = totalSeconds % 60;
                        minutes = String(minutes).padStart(2, "0");
                        hours = String(hours).padStart(2, "0");
                        seconds = String(seconds).padStart(2, "0");
                        return `${hours}:${minutes}:${seconds}`;
                    }
                }
            ]
        });
    }
});
