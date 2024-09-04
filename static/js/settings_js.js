 const fileInput = document.getElementById('file-input');
    const profilePic = document.getElementById('profile-pic');
    const bgColorInput = document.getElementById('bg-color');
    const bgImageInput = document.getElementById('bg-image-input');
    const fontFamilySelect = document.getElementById('font-family');

    // Change profile picture
    fileInput.addEventListener('change', function() {
        const file = fileInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                profilePic.src = e.target.result;
            }
            reader.readAsDataURL(file);
        }
    });

    // Change background color
    bgColorInput.addEventListener('input', function() {
        document.body.style.backgroundColor = bgColorInput.value;
        document.body.style.backgroundImage = ''; // Remove background image if color is selected
    });

    // Change background image
    bgImageInput.addEventListener('change', function() {
        const file = bgImageInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.body.style.backgroundImage = `url(${e.target.result})`;
            }
            reader.readAsDataURL(file);
        }
    });

    // Change font family
    fontFamilySelect.addEventListener('change', function() {
        document.body.style.fontFamily = fontFamilySelect.value;
    });