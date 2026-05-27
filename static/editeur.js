document.addEventListener('DOMContentLoaded', function() {
    const content = document.getElementById('content');
    const code_place = document.getElementById('code_place');
    const code_add = document.getElementById('code_add');
    const normal_text_area = document.getElementById('normal_text_area');

    function add_code_place() {
        const new_code_place = document.createElement('div');
        new_code_place.classList.add('code_place');
        new_code_place.innerHTML = `<div class="code_place">
    <div class="code_body">
        <textarea class="code_input" placeholder="Entrez votre code ici..."></textarea>
    </div>
</div>`;
        content.appendChild(new_code_place);
    }

    code_add.addEventListener('click', add_code_place);

    function add_text_area() {
        const new_text_area = document.createElement('div');
        new_text_area.classList.add('normal_text_area');
        new_text_area.innerHTML = `<div class="normal_text_area">
        <div class="text_body">
            <textarea class="text_input" placeholder="Entrez votre texte ici..."></textarea>
        </div>
    </div>`;
        content.appendChild(new_text_area);
    }

    normal_text_area.addEventListener('click', add_text_area);
});