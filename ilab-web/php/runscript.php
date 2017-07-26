<?php
    echo "about to execute";
    echo exec('whoami');
    echo exec('which python');
    system( '../scripts/ilabXls_copy.py 2>&1',$output);
    system('python ../sample.py 2>&1',$output2);
    print_r($output);
    print_r($output2);
    echo "executed";
?>
