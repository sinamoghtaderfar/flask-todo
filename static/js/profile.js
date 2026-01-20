document.addEventListener("DOMContentLoaded", function () {
    const deleteBtn = document.getElementById("deleteProfileImage");
    const preview = document.getElementById("preview");

    if (!deleteBtn) return;

    deleteBtn.addEventListener("click", function () {
        if (!confirm("Are you sure you want to remove your profile image?")) return;

        fetch("/profile/delete-image", {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                preview.src = "/static/profile_img/default.png";
                deleteBtn.remove();
            }
        });
    });
});
