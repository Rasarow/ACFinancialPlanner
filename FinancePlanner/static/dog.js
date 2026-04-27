
console.log("DOG JS LOADED");
document.addEventListener("DOMContentLoaded", () => {

    console.log("DOG JS LOADED");

    const eyes = document.querySelectorAll(".eye");
    if (!eyes.length) {
        console.log("NO EYES FOUND");
        return;
    }

    document.addEventListener("mousemove", (e) => {

        eyes.forEach(eye => {
            const pupil = eye.querySelector(".pupil");
            if (!pupil) return;

            const rect = eye.getBoundingClientRect();

            const cx = rect.left + rect.width / 2;
            const cy = rect.top + rect.height / 2;

            const dx = e.clientX - cx;
            const dy = e.clientY - cy;

            const angle = Math.atan2(dy, dx);

            const max = 3;

            const x = Math.cos(angle) * max;
            const y = Math.sin(angle) * max;

            pupil.style.transform =
                `translate(-50%, -50%) translate(${x}px, ${y}px)`;
        });

    });

});