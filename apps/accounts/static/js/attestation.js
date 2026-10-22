const RANKS_ORDER = ['МС', 'КМС', '1', '2', '3'];

function checkNormal(results, normal) {
    const checks = [];
    for (const key of ['pullups', 'rope_climbing', 'pushups', 'squats', 'back_bends', 'hang']) {
        if (results[key] != null) checks.push(results[key] >= normal[key]);
    }
    for (const key of ['cross_10km', 'shuttle_run']) {
        if (results[key] != null) checks.push(results[key] <= normal[key]);
    }
    return checks.length === 8 && checks.every(Boolean);
}

function calculateRank(results) {
    for (const rank of RANKS_ORDER) {
        if (checkNormal(results, NORMALS[rank])) return rank;
    }
    return 'Не прошёл';
}

function renderNormals() {
    const tbody = document.getElementById('normals-body');
    for (const rank of RANKS_ORDER) {
        const n = NORMALS[rank];
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><b>${rank}</b></td>
            <td>${n.pullups}</td>
            <td>${n.rope_climbing}</td>
            <td>${n.pushups}</td>
            <td>${n.squats}</td>
            <td>${n.back_bends}</td>
            <td>${n.cross_10km}</td>
            <td>${n.shuttle_run}</td>
            <td>${n.hang}</td>
        `;
        tbody.appendChild(row);
    }
}

function updateRank() {
    const output = document.getElementById('rank-output');
    if (!RESULTS) {
        output.textContent = 'Нет данных';
        return;
    }
    const rank = calculateRank(RESULTS);
    output.textContent = rank;
    output.style.color = rank === 'Не прошёл' ? '#ff8b95' : '#75ef92';
}

document.addEventListener('DOMContentLoaded', () => {
    renderNormals();
    updateRank();
});