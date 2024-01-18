var apiUrlBase = 'http://127.0.0.1:8000/'
var sessionIDName = "sessionID";


function checkLoginStatus() {
    var sessionID = sessionStorage.getItem(sessionIDName);
    if (sessionID == null) {
        window.location.href = "login.html";
    }
}

function getUserPassData() {
    // Retrieve user input
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    // Validate user input
    // username must be at least 3 characters long and less than 36 characters long
    if (username.length < 3 || username.length > 36) {
        var msg = "Username must be at least 3 characters long and less than 36 characters long"
        alert(msg);
        throw Error(msg);
    }
    // password must be at least 6 characters long
    if (password.length < 6) {
        var msg = "Password must be at least 6 characters long"
        alert(msg);
        throw Error(msg);
    }

    // base64 password
    password = btoa(password);

    // return the data
    return {
        username: username,
        password: password
    };
}

let selectedLogo = null;
function toggleSelection(imgElement) {
    if (selectedLogo) {
        // Deselect the previously selected logo
        selectedLogo.classList.remove('selected');
    }

    // Select the new logo
    selectedLogo = imgElement;
    selectedLogo.classList.add('selected');
}
function cancelSelection() {
    closeModal();
    // Additional logic for canceling selection
    if (selectedLogo) {
        selectedLogo.classList.remove('selected');
        selectedLogo = null;
    }
}

function confirmSelection() {
    if (!selectedLogo) {
        alert('Please select a logo');
        return;
    }
    updateLogo(selectedLogo.src);
    // Additional logic for confirming selection
    console.log('Selected Logos:', selectedLogoPaths);

    closeModal();
}

function openModal() {
    const modal = document.getElementById('myModal');
    modal.style.display = 'block';
    // Query and render images in the modal
    queryAndRenderImages();
}

function closeModal() {
    const modal = document.getElementById('myModal');
    modal.style.display = 'none';
}

function queryAndRenderImages() {
    // get logo urls
    fetch(apiUrlBase + "logo", {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': sessionStorage.getItem(sessionIDName)
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data["msg"]) {
                alert(data["msg"]);
                return;
            } else {
                const modalImagesContainer = document.getElementById('modalImagesContainer');

                // Clear previous images
                modalImagesContainer.innerHTML = '';

                // Render images in the modal
                data.forEach(url_obj => {
                    const img = document.createElement('img');
                    img.src = apiUrlBase + url_obj["logo_url"];
                    img.className = 'modal-logo';
                    img.onclick = () => toggleSelection(img)
                    modalImagesContainer.appendChild(img);
                })
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        })

}

function handleFileSelect(event) {
    const fileInput = event.target;
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const userLogo = document.getElementById('user-logo');
            userLogo.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    uploadLogo();
}

function uploadLogo() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];

    if (file) {
        const formData = new FormData();

        formData.append('logo', file);
        formData.append('logo_name', file.name)

        fetch(apiUrlBase + 'upload-logo', {
            method: 'POST',
            headers: {
                'Authorization': sessionStorage.getItem(sessionIDName)
            },
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                if (data["msg"]) {
                    alert(data["msg"]);
                    return;
                } else {
                    console.log('Logo uploaded successfully:', data);
                    alert("Logo uploaded successfully!");
                    // Optionally update UI or perform other actions on success
                }
            })
            .catch(error => {
                alert(error);
                // Handle errors or display error messages
            });
    } else {
        console.error('No file selected');
        // Optionally display a message to the user about selecting a file
    }
}

function updateLogo(src) {
    src = src.replace(apiUrlBase, "");
    fetch(apiUrlBase + 'update-logo', {
        method: 'POST',
        headers: {
            'Authorization': sessionStorage.getItem(sessionIDName),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ logo_url: src }),
    })
        .then(response => response.json())
        .then(data => {
            if (data["msg"]) {
                alert(data["msg"]);
                return;
            } else {
                console.log('Logo updated successfully:', data);
                alert("Logo updated successfully!");
                // Optionally update UI or perform other actions on success
            }
        })
        .catch(error => {
            alert(error);
            // Handle errors or display error messages
        });
}

function handleSignup() {
    var userData = getUserPassData();
    // Send a POST request to the backend
    fetch(apiUrlBase + 'signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
        .then(response => response.json())
        .then(data => {
            if (data["msg"]) {
                alert(data["msg"]);
                return;
            } else {
                alert("User created successfully! Please go to login page to login.")
                window.location.href = "login.html";
            }
        })
        .catch((error) => {
            alert(error);
        });
}

function handleLogin() {
    var userData = getUserPassData();
    fetch(apiUrlBase + 'login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
        .then(response => response.json())
        .then(data => {
            if (data["msg"]) {
                alert(data["msg"]);
                return;
            } else {
                // Save the session ID in the local storage
                console.log(data);
                sessionStorage.setItem(sessionIDName, data["session_id"]);
                window.location.href = "user.html";
            }
        })
        .catch((error) => {
            alert(error);
        });

}

function handleLogout() {
    sessionStorage.clear();
    window.location.href = "login.html";
}

function handleUserData() {
    var sessionID = sessionStorage.getItem(sessionIDName);
    fetch(apiUrlBase + 'user', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': sessionID
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data["msg"]) {
                alert(data["msg"]);
                return;
            } else {
                document.getElementById("username").innerHTML = data["username"];
                // render logo
                logoImgUrl = apiUrlBase + data["logo_url"]
                document.getElementById("user-logo").setAttribute("src", logoImgUrl);

                // render product img
                if (data["systhesis_url"]) {
                    productImgUrl = apiUrlBase + data["systhesis_url"]
                }
                else {
                    productImgUrl = apiUrlBase + data["product_url"]
                }
                document.getElementById("product-img").setAttribute("src", productImgUrl);
            }

        })
        .catch((error) => {
            alert(error);
        });
}