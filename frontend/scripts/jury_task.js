const sliders = document.querySelectorAll('.score-slider');
const totalDisplay = document.getElementById('total-result');

function updateTotalScore() {
    let total = 0;
    sliders.forEach(s => {
        total += parseInt(s.value);
    });
    totalDisplay.textContent = total;
}

sliders.forEach(slider => {
    slider.addEventListener('input', function() {
        const valueDisplay = document.getElementById(`val-${this.id}`);
        const val = parseInt(this.value);
        if (val > 1 && val < 10) {
            valueDisplay.textContent = val;
        } else {
            valueDisplay.textContent = '';
        }
        const percent = ((val - this.min) / (this.max - this.min)) * 100;
        valueDisplay.style.left = `calc(${percent}% + (${8 - percent * 0.15}px))`;
        updateTotalScore();
    });
});