<?php

$method = $_SERVER['REQUEST_METHOD'];

function adopt($text) {
    return '=?UTF-8?B?' . base64_encode($text) . '?=';
}

function sendEmailViaGmail($to, $subject, $message, $fromName, $fromEmail) {
    $smtpHost = getenv('SMTP_HOST') ?: 'smtp.gmail.com';
    $smtpPort = (int) (getenv('SMTP_PORT') ?: 587);
    $smtpUsername = getenv('SMTP_USERNAME') ?: '';
    $smtpPassword = getenv('SMTP_PASSWORD') ?: '';

    if ($smtpUsername === '' || $smtpPassword === '') {
        return false;
    }

    $socket = fsockopen($smtpHost, $smtpPort, $errno, $errstr, 20);
    if (!$socket) {
        return false;
    }

    $response = fgets($socket, 515);
    if (substr($response, 0, 3) !== '220') {
        fclose($socket);
        return false;
    }

    fputs($socket, "EHLO localhost\r\n");
    $response = fgets($socket, 515);
    if (substr($response, 0, 3) !== '250') {
        fclose($socket);
        return false;
    }

    while (true) {
        $line = fgets($socket, 515);
        if ($line === false || substr($line, 3, 1) !== '-') {
            break;
        }
    }

    fputs($socket, "STARTTLS\r\n");
    $response = fgets($socket, 515);
    if (substr($response, 0, 3) !== '220') {
        fclose($socket);
        return false;
    }

    if (!stream_socket_enable_crypto($socket, true, STREAM_CRYPTO_METHOD_TLS_CLIENT)) {
        fclose($socket);
        return false;
    }

    fputs($socket, "EHLO localhost\r\n");
    $response = fgets($socket, 515);
    if (substr($response, 0, 3) !== '250') {
        fclose($socket);
        return false;
    }

    while (true) {
        $line = fgets($socket, 515);
        if ($line === false || substr($line, 3, 1) !== '-') {
            break;
        }
    }

    fputs($socket, "AUTH LOGIN\r\n");
    $response = fgets($socket, 515);
    if (substr($response, 0, 3) !== '334') {
        fclose($socket);
        return false;
    }

    fputs($socket, base64_encode($smtpUsername) . "\r\n");
    $response = fgets($socket, 515);
    if (substr($response, 0, 3) !== '334') {
        fclose($socket);
        return false;
    }

    fputs($socket, base64_encode($smtpPassword) . "\r\n");
    $response = fgets($socket, 515);
    if (substr($response, 0, 3) !== '235') {
        fclose($socket);
        return false;
    }

    fputs($socket, "MAIL FROM:<{$fromEmail}>\r\n");
    $response = fgets($socket, 515);
    if (substr($response, 0, 3) !== '250') {
        fclose($socket);
        return false;
    }

    fputs($socket, "RCPT TO:<{$to}>\r\n");
    $response = fgets($socket, 515);
    if (substr($response, 0, 3) !== '250') {
        fclose($socket);
        return false;
    }

    fputs($socket, "DATA\r\n");
    $response = fgets($socket, 515);
    if (substr($response, 0, 3) !== '354') {
        fclose($socket);
        return false;
    }

    $emailData = "From: " . adopt($fromName) . " <{$fromEmail}>\r\n";
    $emailData .= "To: {$to}\r\n";
    $emailData .= "Subject: " . adopt($subject) . "\r\n";
    $emailData .= "MIME-Version: 1.0\r\n";
    $emailData .= "Content-Type: text/html; charset=UTF-8\r\n";
    $emailData .= "Reply-To: {$fromEmail}\r\n";
    $emailData .= "\r\n{$message}\r\n.\r\n";

    fputs($socket, $emailData);
    $response = fgets($socket, 515);
    if (substr($response, 0, 3) !== '250') {
        fclose($socket);
        return false;
    }

    fputs($socket, "QUIT\r\n");
    fclose($socket);

    return true;
}

$projectName = trim($_POST['project_name'] ?? '');
$adminEmail = trim($_POST['admin_email'] ?? '');
$formSubject = trim($_POST['form_subject'] ?? '');

$fromName = $projectName ?: 'Website Contact Form';
$fromEmail = $adminEmail ?: 'no-reply@example.com';
$messageBody = '';

if ($method === 'POST') {
    foreach ($_POST as $key => $value) {
        if ($value !== '' && $key !== 'project_name' && $key !== 'admin_email' && $key !== 'form_subject') {
            $messageBody .= "<tr><td style='padding:10px;border:1px solid #e9e9e9;'><b>" . htmlspecialchars($key, ENT_QUOTES, 'UTF-8') . "</b></td><td style='padding:10px;border:1px solid #e9e9e9;'>" . htmlspecialchars($value, ENT_QUOTES, 'UTF-8') . "</td></tr>";
        }
    }
} elseif ($method === 'GET') {
    foreach ($_GET as $key => $value) {
        if ($value !== '' && $key !== 'project_name' && $key !== 'admin_email' && $key !== 'form_subject') {
            $messageBody .= "<tr><td style='padding:10px;border:1px solid #e9e9e9;'><b>" . htmlspecialchars($key, ENT_QUOTES, 'UTF-8') . "</b></td><td style='padding:10px;border:1px solid #e9e9e9;'>" . htmlspecialchars($value, ENT_QUOTES, 'UTF-8') . "</td></tr>";
        }
    }
}

if ($messageBody !== '') {
    $messageBody = "<table style='width:100%; border-collapse:collapse;'>{$messageBody}</table>";
}

$sent = sendEmailViaGmail($adminEmail, $formSubject ?: 'Contact Form Message', $messageBody, $fromName, $fromEmail);

if ($sent) {
    http_response_code(200);
    echo 'OK';
} else {
    http_response_code(500);
    echo 'Mail sending failed. Configure SMTP_USERNAME and SMTP_PASSWORD on your server.';
}
