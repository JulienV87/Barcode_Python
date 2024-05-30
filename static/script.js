var app = {
    init: function() {
        app.initUploadBarcodeForm();
        app.initSocketIO();
    },
    initUploadBarcodeForm: function() {
        const form = document.getElementById('upload-form');
        form.addEventListener('submit', app.uploadBarcodeAction);
    },
    uploadBarcodeAction: function(e) {
        e.preventDefault();
        const form = e.target;
        const fileInput = document.getElementById('file-input');
        const resultDiv = document.getElementById('result');
        const formData = new FormData();
        formData.append('image', fileInput.files[0]);

        fetch('/scan', {
            method: 'POST',
            body: formData
        })
        .then((response) => {
            if (response.ok) {
                return response.json();
            }
            throw response;
        })
        .then((data) => {
            if (data.length === 0) {
                resultDiv.innerHTML = "<div style= color:red>Code-barres non détecté.<br>Veuillez réessayer avec une photo plus nette du code-barres.</div>";
            } else {
                resultDiv.innerText = data.join(', ');
            }
        })
        .catch((errorResponse) => {
            console.log(errorResponse);
            return errorResponse.json();
        })
        .then((errorData) => {
            if (errorData) {
                resultDiv.innerText = "Une erreur s'est produite lors de la numérisation du code-barres.";
            }
        });
    },
    initSocketIO: function() {
        const resultDiv = document.getElementById('result');
        const socket = io();

        socket.on('barcode', (data) => {
            resultDiv.innerText = `${data.data} (${data.type})`;
        });
    }
};

document.addEventListener('DOMContentLoaded', (event) => {
    app.init();
});