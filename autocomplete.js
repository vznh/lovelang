var languages = ["Spanish", "French", "Mandarin", "Korean"];
var input = document.getElementById('languages');
var list = document.getElementById('languageList');

input.oninput = function() {
    list.innerHTML = '';
    var value = this.value.toLowerCase();
    for (let i = 0; i < languages.length; i++) {
        if (languages[i].toLowerCase().includes(value)) {
            var option = document.createElement('option');
            option.value = languages[i];
            list.appendChild(option);
        }
    }
};