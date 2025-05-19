document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Ngăn chặn reload trang

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorMessage = document.getElementById("errorMessage");

    // Tạo tài khoản mẫu
    const users = [
        { username: "admin", password: "123456" },
        { username: "user", password: "123456" }
    ];

    // Kiểm tra thông tin đăng nhập
    const user = users.find(u => u.username === username && u.password === password);

    if (user) {
        alert("Đăng nhập thành công!");
        window.location.href = "index install.html"; // Chuyển hướng sau khi đăng nhập
    } else {
        errorMessage.textContent = "Tên đăng nhập hoặc mật khẩu không đúng!";
    }
});
