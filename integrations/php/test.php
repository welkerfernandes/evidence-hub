<?php
declare(strict_types=1);
require __DIR__ . '/ingest.php';
function check(bool $condition): void { if (!$condition) throw new RuntimeException('Test failed'); }
$doc=validateDocument(['title'=>'Política','content'=>'Reembolso permitido.','extra'=>'ignored']);
check(count($doc)===2 && $doc['title']==='Política');
foreach ([[],['title'=>'','content'=>'x'],['title'=>'x','content'=>42]] as $bad) {
    try {validateDocument($bad);throw new RuntimeException('Expected validation error');}
    catch (InvalidArgumentException $expected) {}
}
foreach (['https://attacker.test','file:///etc/passwd','http://user:pass@localhost'] as $bad) {
    try {ingest($doc,$bad,'key');throw new RuntimeException('Expected URL error');}
    catch (InvalidArgumentException $expected) {}
}
echo "7 PHP validation checks passed\n";
