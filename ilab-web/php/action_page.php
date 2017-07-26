<?php
/**
 * Created by PhpStorm.
 * User: rgangwar
 * Date: 5/23/17
 * Time: 5:00 PM
 */
$user = $_GET['uname'];
$password = $_GET['pwd'];
$ldap = ldap_connect("ldap://ldap.cisco.com:389/");
if($ldap)
    echo "successful";
ldap_set_option($ldap, LDAP_OPT_PROTOCOL_VERSION, 3);
ldap_set_option($ldap, LDAP_OPT_REFERRALS, 0);
echo "$ldap";
echo "$user";
echo "$password";

try{
    if ($bind = ldap_bind($ldap, "$user", "$password")) {

       print ("login successful!");
    } else {
        print "validation_error";
    }
}catch(Exception $ex){
    print "error";
}
?>

