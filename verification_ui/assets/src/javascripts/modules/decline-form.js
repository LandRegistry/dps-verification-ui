if (document.getElementById("template_button")) {
    var templatesButton = document.getElementById("template_button");

    templatesButton.addEventListener("click", function(event) {
        event.preventDefault();
        var templatesDropDown = document.getElementById("decline_template");
        var selectedTemplate = templatesDropDown.options[templatesDropDown.selectedIndex].text;
        var declineTemplates = JSON.parse(document.getElementById("decline_templates").dataset.declineTemplates);

        var declineTemplate = declineTemplates.filter(function(template) {
            return template.decline_reason === selectedTemplate;
        }).shift();

        document.getElementById("decline_reason").value = declineTemplate.decline_text;
        document.getElementById("decline_advice").value = declineTemplate.decline_advice;
    });
}
