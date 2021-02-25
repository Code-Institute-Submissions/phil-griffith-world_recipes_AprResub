 $(document).ready(function(){
    let $submitBtn = $("#form input[type='submit']");
    let $passwordBox = $("#password");
    let $confirmBox = $("#confirm_password");
    let $errorMsg =  $('<span id="error_msg">Passwords do not match.</span>');
    let ingredient = 2;
    let step = 2;
    
    $(".sidenav").sidenav();
    $(".dropdown-trigger").dropdown();
    $('select').formSelect();
   

    // ************************* Register ****************************

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

        // ************************* Add Recipe ****************************

        $('#textarea1').val('New Text');
        M.textareaAutoResize($('#textarea1'));

        // button to add 1 ingredient at a time
        $('#add_ingredient').click(function() {
            console.log("HELLO");
            $('#ingredients').append(`<div class="row" id="ingredient_${ingredient}"><div class="input-field col s8">\
            <i class="material-icons prefix">account_circle</i>\
            <input id="ingredient${ingredient}" name="ingredient${ingredient}" type="text" class="validate" required>\
            <label for="ingredient${ingredient}">Ingredient ${ingredient}</label>\
            </div><div class="input-field col s4">\
            <input id="quantity${ingredient}" name="quantity${ingredient}" type="text" class="validate" required>\
            <label for="quantity${ingredient}">Quantity</label></div></div)`);
            if (ingredient == 2){
                console.log("ERROR");
                $('#ingredient_buttons').append(`<button type="button" id="remove_ingredient">Remove Ingredient</button>`);
            }
            ingredient++;
        })

        $('#ingredient_buttons').on('click', '#remove_ingredient', function() {
            console.log("Removing");
            $(`#ingredient_${ingredient-1}`).remove();
            ingredient--;
            if (ingredient == 2) {
                $('#remove_ingredient').remove();
            }            
        })

        // button to add 1 method step at a time
        $('#add_step').click(function() {
            console.log("HELLO");
            $('#method').append(`<div class="row" id="step_${step}"><div class="input-field col s12">\
            <i class="material-icons prefix">account_circle</i>\
            <input id="step${step}" name="step${step}" type="text" class="validate" required>\
            <label for="step${step}">Step ${step}</label>\
            </div></div)`);
            if (step == 2){
                console.log("ERROR");
                $('#method_buttons').append(`<button type="button" id="remove_step">Remove Step</button>`);
            }
            step++;
        })

        $('#method_buttons').on('click', '#remove_step', function() {
            console.log("Removing");
            $(`#step_${step-1}`).remove();
            step--;
            if (step == 2) {
                $('#remove_step').remove();
            }            
        })

    validateMaterializeSelect();
    function validateMaterializeSelect() {
        let classValid = { "border-bottom": "1px solid #4caf50", "box-shadow": "0 1px 0 0 #4caf50" };
        let classInvalid = { "border-bottom": "1px solid #f44336", "box-shadow": "0 1px 0 0 #f44336" };
        if ($("select.validate").prop("required")) {
            $("select.validate").css({ "display": "block", "height": "0", "padding": "0", "width": "0", "position": "absolute" });
        }
        $(".select-wrapper input.select-dropdown").on("focusin", function () {
            $(this).parent(".select-wrapper").on("change", function () {
                if ($(this).children("ul").children("li.selected:not(.disabled)").on("click", function () { })) {
                    $(this).children("input").css(classValid);
                }
            });
        }).on("click", function () {
            if ($(this).parent(".select-wrapper").children("ul").children("li.selected:not(.disabled)").css("background-color") === "rgba(0, 0, 0, 0.03)") {
                $(this).parent(".select-wrapper").children("input").css(classValid);
            } else {
                $(".select-wrapper input.select-dropdown").on("focusout", function () {
                    if ($(this).parent(".select-wrapper").children("select").prop("required")) {
                        if ($(this).css("border-bottom") != "1px solid rgb(76, 175, 80)") {
                            $(this).parent(".select-wrapper").children("input").css(classInvalid);
                        }
                    }
                });
            }
        });
    }
 });

