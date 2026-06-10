document.addEventListener("DOMContentLoaded", () => {

    const editor = document.getElementById("editor");

    document
        .getElementById("add-text")
        .addEventListener("click", addTextBlock);

    document
        .getElementById("add-code")
        .addEventListener("click", addCodeBlock);

    addTextBlock();

    function addTextBlock() {

        const block = document.createElement("div");

        block.className = "block text-block";

        block.innerHTML = `
            <div class="block-header">
                <span>Texte</span>

                <button type="button" class="delete">
                    ✕
                </button>
            </div>

            <textarea name="codes[]" class="code-input"></textarea>

            <input type="hidden" name="block_types[]" value="code">`;

        attachDelete(block);

        editor.appendChild(block);
    }

    function addCodeBlock() {

        const block = document.createElement("div");

        block.className = "block code-block";

        block.innerHTML = `
            <div class="block-header">

                <select name="languages[]">

                    <option value="html">HTML</option>
                    <option value="css">CSS</option>
                    <option value="javascript">JavaScript</option>
                    <option value="python">Python</option>
                    <option value="c">C</option>
                    <option value="cpp">C++</option>

                </select>

                <button type="button" class="delete">
                    ✕
                </button>

            </div>

            <textarea
                name="codes[]"
                class="code-input"
                placeholder="Ton code..."
            ></textarea>
        `;

        attachDelete(block);

        editor.appendChild(block);
    }

    function attachDelete(block) {

        block
            .querySelector(".delete")
            .addEventListener("click", () => {

                block.remove();

            });

    }

});