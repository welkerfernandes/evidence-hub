<?php
declare(strict_types=1);

/** CLI ingestion boundary for legacy PHP systems. No arbitrary target URLs. */
function validateDocument(array $input): array {
    foreach (['title', 'content'] as $field) {
        if (!isset($input[$field]) || !is_string($input[$field]) || trim($input[$field]) === '') {
            throw new InvalidArgumentException('Missing or invalid ' . $field);
        }
    }
    if (mb_strlen($input['title']) > 200 || mb_strlen($input['content']) > 100000) {
        throw new InvalidArgumentException('Document exceeds API limits');
    }
    return ['title' => $input['title'], 'content' => $input['content']];
}

function ingest(array $input, string $baseUrl, string $key): array {
    $data = validateDocument($input);
    $parts = parse_url($baseUrl);
    if (!$parts || !in_array($parts['scheme'] ?? '', ['http', 'https'], true)
        || !in_array($parts['host'] ?? '', ['127.0.0.1', 'localhost', 'evidence-api'], true)
        || isset($parts['user']) || isset($parts['pass']) || isset($parts['query']) || isset($parts['fragment'])) {
        throw new InvalidArgumentException('Only configured internal Evidence Hub hosts are allowed');
    }
    if ($key === '' || preg_match('/[\r\n]/', $key)) throw new InvalidArgumentException('Invalid API key');
    $handle = curl_init(rtrim($baseUrl, '/') . '/documents');
    curl_setopt_array($handle, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 3, CURLOPT_TIMEOUT => 12, CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json', 'X-API-Key: ' . $key],
        CURLOPT_POSTFIELDS => json_encode($data, JSON_THROW_ON_ERROR)]);
    $body = curl_exec($handle);
    $status = (int)curl_getinfo($handle, CURLINFO_RESPONSE_CODE);
    curl_close($handle);
    if ($body === false || $status < 200 || $status >= 300) throw new RuntimeException('Ingestion failed, HTTP ' . $status);
    return json_decode($body, true, 512, JSON_THROW_ON_ERROR);
}

if (realpath($_SERVER['SCRIPT_FILENAME'] ?? '') === __FILE__) {
    try {
        $raw = stream_get_contents(STDIN, 500001);
        if (strlen($raw) > 500000) throw new InvalidArgumentException('Input too large');
        $input = json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
        if (!is_array($input)) throw new InvalidArgumentException('Expected JSON object');
        $result = ingest($input, getenv('EVIDENCE_URL') ?: 'http://127.0.0.1:8102', getenv('EVIDENCE_KEY') ?: '');
        echo json_encode($result, JSON_THROW_ON_ERROR) . PHP_EOL;
    } catch (Throwable $error) { fwrite(STDERR, $error->getMessage() . PHP_EOL); exit(1); }
}
