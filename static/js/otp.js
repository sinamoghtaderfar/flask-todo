
const otpBtn = document.getElementById("sendOtpBtn");
const otpMsg = document.getElementById("otp-messages");
const changeForm = document.getElementById("changePasswordForm");

// ارسال OTP با AJAX

otpBtn.addEventListener("click", () => {
    const url = otpBtn.dataset.url;
    fetch(url, { method: "POST", headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(res => res.json())
        .then(data => {
            document.getElementById("otp-messages").innerHTML =
                `<div class="alert alert-info">${data.message}</div>`;
        });
});

// تغییر پسورد با AJAX
changeForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const formData = new FormData(changeForm);

    fetch("{{ url_for('change_password') }}", {
        method: "POST",
        body: formData,
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
    .then(res => res.json())
    .then(data => {
        if(data.success){
            otpMsg.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
            changeForm.reset();
        } else {
            otpMsg.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
        }
    });
});
