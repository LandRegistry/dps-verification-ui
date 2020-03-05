var noRadio = document.querySelector('input[value="no"]');
var yesRadio = document.querySelector('input[value="yes"]');
var checkboxes = document.querySelectorAll('input[name="contact_preferences"]');

noRadio && noRadio.addEventListener('click', function(e) {
    toggleCheckboxes('setAttribute');
});
    
yesRadio && yesRadio.addEventListener('click', function(e) {
    toggleCheckboxes('removeAttribute');
});

function toggleCheckboxes(toggle) {
    [].forEach.call(checkboxes, function(x) {
        x[toggle]('disabled', '')
    });
}