// ======= Auto logout =======
let timer;
const logoutTime = 3 * 60 * 1000;

function resetTimer() {
    clearTimeout(timer);
    timer = setTimeout(() => {
        alert("You have been inactive for 3 minutes. Logging out...");
        window.location.href = "/logout";
    }, logoutTime);
}


window.onload = resetTimer;
document.onmousemove = resetTimer;
document.onkeypress = resetTimer;
document.onclick = resetTimer;
document.onscroll = resetTimer;
