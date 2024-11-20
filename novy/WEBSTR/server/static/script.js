function generateQR() {
    const name = document.getElementById("qr_name").value;
    if (!name) {
        alert("Prosím zadejte své jméno!");
        return;
    }

    const token = Math.random().toString(36).substr(2, 10); // Generování tokenu

    fetch(`/api/qr_code/${token}`)
        .then(response => response.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const img = document.getElementById("qr_code");
            img.src = url;
            document.getElementById("qr_code_container").style.display = 'block';
        })
        .catch(error => {
            console.error("Chyba:", error);
            alert('Nepodařilo se vygenerovat QR kód.');
        });
}
