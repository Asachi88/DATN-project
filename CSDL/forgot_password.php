<?php
// Include database connection
require_once 'config.php';

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
if (empty($data['email'])) {
    echo json_encode(['success' => false, 'message' => 'Vui lòng nhập email']);
    exit;
}

$email = $conn->real_escape_string(trim($data['email']));

// Check if email exists
$stmt = $conn->prepare("SELECT id FROM users WHERE email = ?");
$stmt->bind_param("s", $email);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    // For security reasons, we still return success even if email doesn't exist
    echo json_encode(['success' => true, 'message' => 'Nếu email tồn tại, hướng dẫn đặt lại mật khẩu sẽ được gửi']);
    $stmt->close();
    exit;
}

// Generate token
$token = bin2hex(random_bytes(32));
$expiry = date('Y-m-d H:i:s', strtotime('+1 hour'));

// Update user with reset token
$stmt = $conn->prepare("UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE email = ?");
$stmt->bind_param("sss", $token, $expiry, $email);
$stmt->execute();

// In a real application, you would send an email with a reset link
// $reset_link = "https://yourwebsite.com/reset-password.php?token=$token";
// mail($email, "Đặt lại mật khẩu", "Nhấp vào liên kết để đặt lại mật khẩu: $reset_link", "From: no-reply@yourwebsite.com");

// For demonstration, we'll just return success
echo json_encode([
    'success' => true, 
    'message' => 'Hướng dẫn đặt lại mật khẩu đã được gửi đến email của bạn!'
]);

$stmt->close();
$conn->close();
?>