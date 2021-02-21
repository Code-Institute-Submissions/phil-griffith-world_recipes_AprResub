 $(document).ready(function(){
    let $submitBtn = $("#form input[type='submit']");
    let $passwordBox = $("#password");
    let $confirmBox = $("#confirm_password");
    let $errorMsg =  $('<span id="error_msg">Passwords do not match.</span>');
    
    $(".sidenav").sidenav();
    $(".dropdown-trigger").dropdown();
    $('select').formSelect();
    

    // confirm password code taken from the following site 
    // https://stackoverflow.com/questions/21727317/how-to-check-confirm-password-field-in-form-without-reloading-page

    function checkMatchingPasswords(){
        if($confirmBox.val() != "" && $passwordBox.val != ""){
            if( $confirmBox.val() != $passwordBox.val() ){
                $confirmBox.removeClass("valid");
                $confirmBox.addClass("invalid");
                $errorMsg.insertAfter($confirmBox);
                }
        }
    } 

    function resetPasswordError(){
        $submitBtn.removeAttr("disabled");
        var $errorCont = $("#error_msg");
        if($errorCont.length > 0){
            $errorCont.remove();
        }  
    }

    $("#confirm_password, #password").keydown(function(e){
        /* only check when the tab or enter keys are pressed
        * to prevent the method from being called needlessly  */
        console.log("Hello_confirm");
        if(e.keyCode == 13 || e.keyCode == 9) {
            checkMatchingPasswords();
        }
    })
        .blur(function(){                    
            // also check when the element looses focus (clicks somewhere else)
            checkMatchingPasswords();
        })
        .focus(function(){
            // reset the error message when they go to make a change
            resetPasswordError();
        })

        // on form submit check passwords match and disable submission if no match.
        // code taken from following site
        // https://api.jquery.com/submit/
        $( "form" ).submit(function( event ) {
            if ( $confirmBox.hasClass("invalid") ) {
                event.preventDefault();
            }
            return;
        });
    
 });

