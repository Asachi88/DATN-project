<?php
// Include database connection
require_once 'config.php';

// Start session
session_start();

// Set headers
header('Content-Type: application/json');

// Check if request method is POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'message' => 'Phương thức không được phép']);
    exit;
}

// Get POST data
$data = json_decode(file_get_contents('php://input'), true);

// Validate form data
if (empty($data['username']) || empty($data['password'])) {
    echo json_encode(['success' => false, 'message' => 'Vui lòng nhập đầy đủ thông tin']);
    exit;
}

$username = $conn->real_escape_string(trim($data['username']));
$password = $data['password'];

// Get user from database
$stmt = $conn->prepare("SELECT id, username, password FROM users WHERE username = ?");
$stmt->bind_param("s", $username);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    echo json_encode(['success' => false, 'message' => 'Tên đăng nhập hoặc mật khẩu không chính xác']);
    $stmt->close();
    exit;
}

$user = $result->fetch_assoc();

// Verify password
if (password_verify($password, $user['password'])) {
    // Password is correct, create session
    $_SESSION['user_id'] = $user['id'];
    $_SESSION['username'] = $user['username'];
    
    echo json_encode([
        'success' => true, 
        'message' => 'Đăng nhập thành công!',
        'redirect' => 'dashboard.php' // Redirect to dashboard or home page
    ]);
} else {
    echo json_encode(['success' => false, 'message' => 'Tên đăng nhập hoặc mật khẩu không chính xác']);
}

$stmt->close();
$conn->close();
?>